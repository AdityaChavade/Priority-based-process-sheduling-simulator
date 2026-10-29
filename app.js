(() => {
  const $ = id => document.getElementById(id);
  const samples = {
    io: `$AMJ00010020001005\nGD10PD10CR10BT10PD10H\n$DTA\nLOW_PRIORITY_DATA___\n$END\n$AMJ00020010001001\nGD20PD20H\n$DTA\nHIGH_PRIORITY_DATA__\n$END`,
    preempt: `$AMJ00010020001005\nLR00LR00LR00LR00LR00LR00LR00LR00H\n$DTA\nLOW PRIORITY JOB\n$END\n$AMJ00020010001001\nLR00LR00H\n$DTA\nHIGH PRIORITY JOB\n$END`,
    error: `$AMJ00030003000101\nLR00LR00LR00LR00H\n$DTA\nERROR SAMPLE\n$END`
  };
  let deckText='',jobs=[],events=[],history=[],results=[],selectedJob=null,activeFilter='all',activeJob=null,currentTick=0,timer=null,paused=true;
  const fileInput=$('file-input'),dropzone=$('dropzone');
  function setDeck(text,name){stop();deckText=text;$('file-name').textContent=name||'Sample job deck loaded';$('run-button').disabled=!text.trim();$('error-message').hidden=true;}
  fileInput.addEventListener('change',async e=>{const f=e.target.files[0];if(f)setDeck(await f.text(),f.name);});
  $('sample-button').addEventListener('click',()=>setDeck(samples.io,'Sample: I/O jobs · 2 jobs'));
  $('preempt-sample-button').addEventListener('click',()=>setDeck(samples.preempt,'Sample: priority preemption · 2 jobs'));
  $('error-sample-button').addEventListener('click',()=>setDeck(samples.error,'Sample: time limit error · 1 job'));
  for(const t of ['dragenter','dragover'])dropzone.addEventListener(t,e=>{e.preventDefault();dropzone.classList.add('dragover');});
  for(const t of ['dragleave','drop'])dropzone.addEventListener(t,e=>{e.preventDefault();dropzone.classList.remove('dragover');});
  dropzone.addEventListener('drop',async e=>{const f=e.dataTransfer.files[0];if(f)setDeck(await f.text(),f.name);});
  $('run-button').addEventListener('click',initialize);
  $('rerun-button').addEventListener('click',initialize);
  $('step-button').addEventListener('click',()=>{stop();step();});
  $('play-button').addEventListener('click',()=>{if(timer){stop();return;}if(!jobs.length)initialize();if(jobs.length&&!done()){paused=false;$('play-button').textContent='Ⅱ Pause';timer=setInterval(step,550);}});
  $('log-filters').addEventListener('click',e=>{const b=e.target.closest('button[data-filter]');if(!b)return;activeFilter=b.dataset.filter;document.querySelectorAll('.filter').forEach(x=>x.classList.toggle('active',x===b));renderLogs();});
  function parse(text){
    const lines=text.replace(/\r/g,'').split('\n'),out=[];let j=null,mode='';
    for(const raw of lines){const line=raw.trimEnd();if(line.startsWith('$AMJ')){if(j)out.push(j);const d=(line.slice(4).match(/\d/g)||[]).join('');if(d.length<12)throw Error('An $AMJ card needs at least 12 digits: ID, time limit and line limit.');j={id:d.slice(0,4),ttl:Number(d.slice(4,8)),tll:Number(d.slice(8,12)),priority:d.length>=14?Number(d.slice(12,14)):10,program:'',data:[],status:'FUTURE',ic:0,ttc:0,llc:0,register:'    ',compare:false,memory:{},history:[],arrivalTick:out.length*4,readBlock:'',pendingRead:'',termination:''};mode='program';}
      else if(!j)continue;else if(line.startsWith('$DTA'))mode='data';else if(line.startsWith('$END')){out.push(j);j=null;mode='';}else if(mode==='program')j.program+=line.replace(/\s/g,'');else if(mode==='data'&&line.length)j.data.push(line);}
    if(j)out.push(j);if(!out.length)throw Error('No jobs found. Add job cards using $AMJ, program instructions, $DTA and $END.');
    out.forEach(p=>{p.instructions=(p.program.match(/.{1,4}/g)||[]).map((op,i)=>({op:op.padEnd(4,' '),va:i}));p.instructions.forEach(x=>p.memory[x.va]=x.op);});return out;
  }
  function initialize(){stop();try{jobs=parse(deckText);}catch(e){$('error-message').textContent=e.message;$('error-message').hidden=false;return;}events=[];history=[];results=[];selectedJob=jobs[0].id;activeJob=null;currentTick=0;paused=true;jobs.forEach(j=>transition(j,'FUTURE',`Job ${j.id} queued for admission at tick ${j.arrivalTick}.`));$('workspace').hidden=false;$('play-button').textContent='▶ Run';render();$('workspace').scrollIntoView({behavior:'smooth',block:'start'});}
  function step(){if(done()){stop();render();return;}currentTick++;for(const j of jobs){if(j.status==='FUTURE'&&j.arrivalTick<=currentTick)transition(j,'READY',`Job ${j.id} admitted to the ready queue (priority ${j.priority}).`);if(j.status==='WAITING'&&j.waitUntil<=currentTick){j.readBlock=j.pendingRead||'';for(let i=0;i<10;i++)j.memory[j.readAddress+i]=(j.readBlock.slice(i*4,i*4+4)||'    ').padEnd(4,' ');transition(j,'READY',`Input completed; job ${j.id} returned to ready queue.`);add('io',j,`GD${String(j.readAddress).padStart(2,'0')} data block is available.`);}}
    const next=jobs.filter(j=>['READY','RUNNING'].includes(j.status)).sort((a,b)=>a.priority-b.priority||a.arrivalTick-b.arrivalTick)[0];
    if(!next){add('state',{id:'OS'},'CPU idle; jobs are arriving or waiting for I/O.');render();return;}
    if(activeJob&&activeJob!==next.id){const prev=jobs.find(j=>j.id===activeJob);if(prev&&prev.status==='RUNNING')transition(prev,'READY',`Job ${prev.id} preempted and returned to ready queue.`);add('state',next,`Context switch: selected job ${next.id} (priority ${next.priority}) over job ${activeJob}.`);}
    activeJob=next.id;if(next.status!=='RUNNING')transition(next,'RUNNING',`Job ${next.id} dispatched to CPU.`);
    const ins=next.instructions[next.ic];if(!ins){finish(next,'ALL GOOD');render();return;}const op=ins.op.slice(0,2),operand=Number(ins.op.slice(2).trim())||0;next.ttc++;next.ic++;add('cpu',next,`IC ${String(ins.va).padStart(2,'0')} · execute <code>${escapeHtml(ins.op)}</code>.`);
    if(next.ttc>next.ttl){finish(next,'TIME LIMIT EXCEEDED','ERROR');render();return;}
    if(op==='H '||op==='H'){finish(next,'ALL GOOD');render();return;}
    if(op==='LR'){next.register=word(next,operand);add('cpu',next,`R ← memory[${operand}] (${escapeHtml(next.register)}).`);}
    else if(op==='SR'){next.memory[operand]=next.register;add('cpu',next,`memory[${operand}] ← R (${escapeHtml(next.register)}).`);}
    else if(op==='CR'){next.compare=word(next,operand)===next.register;add('cpu',next,`Compare memory[${operand}] with R · ${next.compare?'equal':'not equal'}.`);}
    else if(op==='BT'){if(next.compare){next.ic=Math.min(operand,next.instructions.length);add('cpu',next,`Branch taken to instruction ${String(operand).padStart(2,'0')}.`);}else add('cpu',next,'Branch not taken; comparison flag is false.');}
    else if(op==='GD'){if(!next.data.length){finish(next,'OUT OF DATA ERROR','ERROR');render();return;}next.readAddress=operand;next.pendingRead=next.data.shift();next.waitUntil=currentTick+2;activeJob=null;transition(next,'WAITING',`Job ${next.id} waits for input on GD${String(operand).padStart(2,'0')}.`);add('io',next,'Input channel started (2 tick delay).');}
    else if(op==='PD'){if(next.llc>=next.tll){finish(next,'LINE LIMIT EXCEEDED','ERROR');render();return;}const line=Array.from({length:10},(_,i)=>word(next,operand+i)).join('').trimEnd();next.llc++;results.push({id:next.id,text:line,kind:'print',n:next.llc});add('io',next,`PD${String(operand).padStart(2,'0')} printed output line ${next.llc}.`);}
    else {finish(next,`OPCODE ERROR: ${ins.op.trim()}`,'ERROR');render();return;}
    render();if(done())stop();
  }
  function word(j,a){return (j.memory[a]||'    ').padEnd(4,' ').slice(0,4);}
  function transition(j,state,message){j.status=state;const h={tick:currentTick,id:j.id,state,message};j.history.push(h);history.push(h);add('state',j,message);}
  function finish(j,message,status='FINISHED'){j.termination=message;transition(j,status,`Job ${j.id} terminated · ${message}.`);results.push({id:j.id,text:message,kind:'termination'});activeJob=null;}
  function add(kind,j,text){events.push({tick:currentTick,kind,id:j.id,text});}
  function done(){return jobs.length>0&&jobs.every(j=>['FINISHED','ERROR'].includes(j.status));}
  function stop(){if(timer){clearInterval(timer);timer=null;}paused=true;const b=$('play-button');if(b)b.textContent='▶ Run';}
  function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  function render(){if(!jobs.length)return;$('job-count').textContent=jobs.length;$('run-summary').textContent=`TICK ${currentTick} · ${jobs.filter(j=>['FINISHED','ERROR'].includes(j.status)).length}/${jobs.length} COMPLETE`;
    $('job-list').innerHTML=jobs.map(j=>`<article class="job-card${selectedJob===j.id?' selected':''}" data-id="${j.id}"><div class="job-top"><span class="job-id">JOB ${j.id}</span><span class="status ${j.status.toLowerCase()}">${j.status}</span></div><div class="job-meta"><span>PRI <b>${j.priority}</b></span><span>TIME <b>${j.ttc}/${j.ttl}</b></span><span>LINES <b>${j.llc}/${j.tll}</b></span></div><div class="job-progress"><span style="width:${Math.min(100,j.ic/Math.max(1,j.instructions.length)*100)}%"></span></div></article>`).join('');document.querySelectorAll('.job-card').forEach(c=>c.addEventListener('click',()=>{selectedJob=selectedJob===c.dataset.id?null:c.dataset.id;render();}));
    const active=jobs.find(j=>j.id===activeJob)||jobs.find(j=>j.id===selectedJob);$('cpu-job').textContent=active?`JOB ${active.id}`:'IDLE';$('cpu-view').innerHTML=active?cpuHTML(active):'<div class="empty-state">CPU is idle between instructions or during I/O.</div>';
    const chosen=jobs.find(j=>j.id===selectedJob);$('memory-label').textContent=chosen?`JOB ${chosen.id}`:'SELECT A JOB';$('memory-view').innerHTML=chosen?memoryHTML(chosen):'<div class="empty-state">Select a job to inspect its instruction and data words.</div>';
    renderLogs();$('history-count').textContent=selectedJob?`JOB ${selectedJob}`:'ALL JOBS';const hs=history.filter(h=>!selectedJob||h.id===selectedJob);$('history-list').innerHTML=hs.length?hs.slice().reverse().map(h=>`<div class="history-row"><span class="log-time">T+${String(h.tick).padStart(3,'0')}</span><span class="status ${h.state.toLowerCase()}">${h.state}</span><span>${escapeHtml(h.message)}</span></div>`).join(''):'<div class="empty-state">State changes appear as the simulation advances.</div>';
    $('results-list').innerHTML=results.length?results.map(r=>`<div class="result-row"><div class="result-label"><span>JOB ${r.id} · ${r.kind==='print'?'PRINTED LINE '+r.n:'TERMINATION'}</span><span>${r.kind==='print'?'PD':'OS'}</span></div><div class="result-text ${r.kind==='termination'?'termination':''}">${escapeHtml(r.text)}</div></div>`).join(''):'<div class="empty-state">Printed lines and termination messages will appear here.</div>'; $('result-count').textContent=`${results.length} LINES`;
    $('step-button').disabled=done();$('play-button').disabled=done();if(done())$('play-button').textContent='✓ Complete';
  }
  function cpuHTML(j){const ins=j.instructions[Math.max(0,j.ic-1)];return `<div class="cpu-grid"><span>IC</span><b>${String(j.ic).padStart(2,'0')}</b><span>IR</span><b class="mono">${escapeHtml(ins?ins.op:'----')}</b><span>R</span><b class="mono">${escapeHtml(j.register)}</b><span>C</span><b>${j.compare?'TRUE':'FALSE'}</b><span>TTC</span><b>${j.ttc} / ${j.ttl}</b><span>STATE</span><b>${j.status}</b></div>`;}
  function memoryHTML(j){const entries=Object.entries(j.memory).map(([a,v])=>[+a,v]).sort((a,b)=>a[0]-b[0]);return `<div class="memory-grid"><div class="memory-head"><span>VA</span><span>WORD</span><span>TYPE</span></div>${entries.map(([a,v])=>`<div class="memory-row ${a===j.ic-1?'current-word':''}"><span>${String(a).padStart(2,'0')}</span><code>${escapeHtml(v)}</code><span>${a<j.instructions.length?'CODE':'DATA'}</span></div>`).join('')}</div>`;}
  function renderLogs(){const shown=events.filter(e=>(activeFilter==='all'||e.kind===activeFilter)&&(!selectedJob||e.id===selectedJob));$('log-count').textContent=`${shown.length} EVENTS`;$('log-list').innerHTML=shown.slice().reverse().map(e=>`<div class="log-entry"><span class="log-time">T+${String(e.tick).padStart(3,'0')}</span><span class="log-tag ${e.kind}">${e.kind}</span><span class="log-text"><strong>${e.id==='OS'?'SYSTEM':'JOB '+e.id}</strong> · ${e.text}</span></div>`).join('')||'<div class="empty-state">No events match this filter.</div>';}
})();
