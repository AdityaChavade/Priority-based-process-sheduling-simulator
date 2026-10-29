#include <iostream>
#include <cstring>
#include <fstream>
#include <time.h>
#include <bits/stdc++.h>
#include <list> 

#define N 40
#define SIZE 300
#define K 4

using namespace std;

enum TASK{ IS , OS , LD , RT , WT };
enum STATUS{ Loading , Loaded , Ready , Execute , Terminate , Read , Write };

class PCB{
    public:
    int ID;
    int TTL; 
    int TLL;  
    int TTC; 
    int LLC; 
    int priority; 
    char F;
    int  P_COUNT, D_COUNT;
    int  D , P , O, END;
    int flag = 0;
    int PTR ;
    short IC;
    string terminateMsg ;
    STATUS status;
    
    char R_save[K]; 
    bool C_save;    

    PCB(PCB* pcb) {
        ID = pcb->ID; TTL = pcb->TTL; TLL = pcb->TLL; TTC = pcb->TTC;
        LLC = pcb->LLC; priority = pcb->priority; F = pcb->F;
        D = pcb->D; P_COUNT= pcb->P_COUNT; D_COUNT= pcb->D_COUNT;
        P = pcb->P; END = pcb->END; O = pcb->O; status = pcb->status;
        PTR = pcb->PTR; IC = pcb->IC; terminateMsg = pcb->terminateMsg;
        
        for(int i=0; i<K; i++) R_save[i] = pcb->R_save[i];
        C_save = pcb->C_save;
    }
    
    PCB() {
        TTL = TLL = TTC = LLC = D = P_COUNT = D_COUNT = P = END = IC = O = ID = 0;
        priority = 10; 
        F = 'P'; 
        PTR = -1;
        terminateMsg = ' ';
        status = STATUS::Loading;
        
        for(int i=0; i<K; i++) R_save[i] = ' ';
        C_save = false;
    }
};

class CH{
    public:
    int flag, value, time, total_time;
    CH() { flag = 0; value = 0; time = 0; total_time=0; }
};

typedef struct buffer{
    int status; 
    char value[40];
    void initalize(){ 
        for(int i = 0; i<40; i++) value[i] = ' ';
    }
}Buffer;

class MOS{
    private:
    char MainMemory[SIZE][K],DrumMemory[SIZE+200][K], IR[K], R[K];
    int drum = 0, memory=0;
    short RA;
    bool C;
    int SI = 0, PI = 0, TI = 0, IOI = 0;
    CH* ch = new CH[3];
    int count = 0;
    ifstream fi;
    ofstream fo;
    bool mark[30];
    int eof = 0;
    TASK task = TASK::IS;
    int flag = 0;
    
    int active_job_id = -1; 
    bool was_idle = false; // Tracks if the CPU was already idle to prevent spam

    queue<Buffer*> emptyQ, inputfulBufferQ, outputfulBufferQ;
    queue<PCB*> loadQ, inputOutputQ, terminateQ, pendingQ;
    list<PCB*> readyQ; 

    int Allocate();
    bool check_operand(char , char);
    void Map(PCB*, int);
    int cardReader();
    void store_buffer_DrumMM(PCB*);
    void loadDrumMM(PCB*);
    void execute();
    void LR(); void SR(); void CR(); void BT(PCB*);
    void drum_to_OutputBuffer(PCB*);
    void IRI1(); void IRI2(); void IRI3();
    void masterMode();
    void store_bufferDrum(Buffer*);
    void terminate(int,int);
    void simulation();
    void startCH(int);
    void sortReadyQueue(); 

    public:
    MOS();
    void begin();
    void initialization();
    void close_all();
};

int main() {
    srand(time(0));
    MOS my_os;
    my_os.begin();
    my_os.close_all();
    return 0;
}

void MOS::sortReadyQueue() {
    readyQ.sort([](const PCB* a, const PCB* b) {
        return a->priority < b->priority; 
    });
}

void MOS::begin(){
    int tmr=0;
    cout<<"Priority RTOS KERNEL STARTED (With Context Switching) \n\n";
    initialization();
    IOI = 1; 
    do {
        execute();
        simulation();
        masterMode();
        tmr++;
    } while(eof!=1 || !inputfulBufferQ.empty() || !outputfulBufferQ.empty() || !loadQ.empty() || !readyQ.empty() || !inputOutputQ.empty() || !terminateQ.empty() );

    cout << "\n=========================================================\n";
    cout << "   OS Shutting Down. All Jobs Completed Successfully.    \n";
    cout << "=========================================================\n";
}

void MOS::initialization(){
    memory = 0;
    for(int i = 0 ; i<SIZE ; i++)
        for(int j = 0 ; j<K; j++) MainMemory[i][j] = ' ';
    
    for(int i = 0 ; i<30 ; i++) mark[i] = false; 
    for(int i = 0 ; i<K ; i++) R[i] = ' ';
    C = false;
    
    for(int i = 0 ; i<10;i++) {
        Buffer* temp = new Buffer;
        temp->initalize(); 
        temp->status = 0;
        emptyQ.push(temp);
    }
    
    for(int i = 0 ; i<50;i++)
        for(int j = 0 ; j<K;j++) DrumMemory[i][j] = ' ';
    
    ch[0].value = 1; ch[1].value = 2; ch[2].value = 4;
    ch[0].total_time = 5; ch[1].total_time = 5; ch[2].total_time = 2;
}

int MOS::Allocate() {
    int random = rand() % 30;
    while(mark[random]) random = rand() % 30;
    mark[random] = true;
    return random;
}

bool MOS::check_operand(char a , char b) {
    if(!( ( (a<='9'&&a>='0') || a==' ') && ( (b<='9'&&b>='0')|| b==' ') )){
        PI = 2; return false;
    }
    return true;
}

void MOS::Map(PCB* temp , int VA) {
    int pte_i;
    int pte = temp->PTR + (int)VA/10;
    string content;
    for(int i = 0; i<K; i++) content+=MainMemory[pte][i];
    
    if(content == "    ") {
        PI = 3; 
        return;
    }
    pte_i = stoi(content);
    RA = pte_i*10 + VA%10;
}

int MOS::cardReader(){
    char c;
    if(eof == 1 || emptyQ.empty()) return 1;
    
    Buffer* temp = emptyQ.front();
    emptyQ.pop();
    temp->status = 1; 
    if(inputfulBufferQ.size() == 10) return 1;
    
    if(fi.is_open()) {
        int count = 0;
        fi.get(c);
        if(c == '\n') return 0;
        temp->value[count++] = c;
        if(c =='H' && pendingQ.back()->F == 'P'){
            temp->value[count++] = ' '; temp->value[count++] = ' '; temp->value[count++] = ' ';
        }
        while(fi.good()){
            fi.get(c);
            if(count == 40 || c =='\n'){
                if(temp->value[0] == '$') {
                    if(temp->value[1] == 'A') {
                        PCB *temp_pcb = new PCB();
                        temp_pcb->ID = stoi(string(1,temp->value[4])+string(1,temp->value[5])+string(1,temp->value[6])+string(1,temp->value[7]));
                        temp_pcb->TTL = stoi(string(1,temp->value[8])+string(1,temp->value[9])+string(1,temp->value[10])+string(1,temp->value[11]));
                        temp_pcb->TLL = stoi(string(1,temp->value[12])+string(1,temp->value[13])+string(1,temp->value[14])+string(1,temp->value[15]));
                        
                        try { temp_pcb->priority = stoi(string(1,temp->value[16])+string(1,temp->value[17])); } 
                        catch(...) { temp_pcb->priority = 10; }

                        temp_pcb->F = 'P';
                        pendingQ.push(temp_pcb);
                    }
                    else if(temp->value[1] == 'D'){
                        pendingQ.back()->F = 'D';
                    }
                }
                else{
                    if(pendingQ.back()->F == 'P') pendingQ.back()->P_COUNT +=1;       
                    else if(pendingQ.back()->F == 'D') pendingQ.back()->D_COUNT +=1;
                }
                inputfulBufferQ.push(temp);
                if(!( (IOI >> 2) & 1)) IOI|=4;
                task = TASK::IS;
                return 0;
            }
            temp->value[count++] = c;
            if(c =='H' && pendingQ.back()->F == 'P'){
                temp->value[count++] = ' '; temp->value[count++] = ' '; temp->value[count++] = ' ';
            }
            if(fi.eof() && flag == 0) {
                inputfulBufferQ.push(temp);
                task = TASK::IS;
                flag = 1;
            }
        }
    }
    return 1;
}

void MOS::store_buffer_DrumMM(PCB* temp){
    int m = Allocate()*10;
    int itr = temp->PTR;
    while(MainMemory[itr][3] != ' ') itr++;
    MainMemory[itr][3] = '0'+ (m%100)/10;  
    MainMemory[itr][2] = '0'+ (m/100);
    MainMemory[itr][1] = '0';
    MainMemory[itr][0] = '0';

    for(int i = 0 ; i< 10 ; i++)
        for(int j = 0 ; j<K ; j++)
            MainMemory[m+i][j] = DrumMemory[temp->P+i][j];   
    temp->P+=10;
}

void MOS::loadDrumMM(PCB* temp){
    if(temp->PTR == -1) temp->PTR = Allocate()*10;
    store_buffer_DrumMM(temp);        
}

void MOS::execute(){
    if(readyQ.empty()) {
        if(active_job_id != -1) {
            cout<<"\n---------------------------------------------------"<<endl;
            cout<<"[CONTEXT SWITCH] Job ID: "<<active_job_id<<" is removed from CPU."<<endl;
            cout<<"[SAVE] Registers safely saved to PCB for Job ID: "<<active_job_id<<endl;
            cout<<"---------------------------------------------------\n"<<endl;
            active_job_id = -1;
        }
        if(!was_idle) { // Only print once when state changes to idle
            cout<<"CPU Idle..."<<endl;
            was_idle = true; 
        }
        return;
    }
    
    was_idle = false; // CPU is no longer idle
    sortReadyQueue(); 
    PCB* temp = readyQ.front();
    
    if(active_job_id != temp->ID) {
        cout<<"\n---------------------------------------------------"<<endl;
        if(active_job_id != -1) {
            cout<<"[CONTEXT SWITCH] Preempting/Yielding Job ID: "<<active_job_id<<endl;
            cout<<"[SAVE] Registers safely saved to PCB for Job ID: "<<active_job_id<<endl;
        }
        cout<<"[DISPATCH] Starting/Resuming Job ID: "<<temp->ID<<" (Priority: "<<temp->priority<<")"<<endl;
        cout<<"[RESTORE] Loading Registers (R and C) from PCB into CPU for Job ID: "<<temp->ID<<endl;
        cout<<"---------------------------------------------------\n"<<endl;
        active_job_id = temp->ID;
    }
    
    if(temp->status != STATUS::Execute) temp->status = STATUS::Execute;

    // Load state
    for(int i=0; i<K; i++) R[i] = temp->R_save[i];
    C = temp->C_save;

    temp->TTC++;
    Map(temp,temp->IC);
    
    if(!PI) { 
        for(int k = 0 ; k<K ; k++) IR[k] = MainMemory[RA][k];
        
        if(IR[0]=='H' && IR[1]==' ') {
            SI = 3; 
        } else if(temp->TTC > temp->TTL) {
            TI = 2; 
        } else {
            temp->IC++;
            if(check_operand(IR[2],IR[3])) {
                int operand = stoi(string(1,IR[2])+string(1,IR[3]));
                Map(temp,operand);
                
                if(!PI) {
                    string instruction =  string(1,IR[0])+string(1, IR[1]);
                    if(instruction == "LR") LR();               
                    else if(instruction == "SR") SR();            
                    else if(instruction == "CR") CR();          
                    else if(instruction == "BT") BT(temp);
                    else if(instruction == "GD") { SI = 1; task = TASK::RT; }
                    else if(instruction == "PD") { SI = 2; task = TASK::WT; } 
                    else if(instruction[0] == 'H') { SI = 3; task = TASK::OS; }
                    else { PI = 1; }
                }
            }
        }
    }
    
    // Save state
    for(int i=0; i<K; i++) temp->R_save[i] = R[i];
    temp->C_save = C;
}

void MOS::LR(){ for(int i=0; i<K; i++) R[i] = MainMemory[RA][i]; }
void MOS::SR(){ for(int i=0; i<K; i++) MainMemory[RA][i] = R[i]; }
void MOS::CR(){
    C = true;
    for(int i=0; i<K; i++) if (MainMemory[RA][i] != R[i]) C = false;
}
void MOS::BT(PCB* temp){ if(C) temp->IC = (IR[2]-'0')*10+(IR[3]-'0'); }

void MOS::drum_to_OutputBuffer(PCB* temp){
    if(emptyQ.empty() || temp->LLC < 0) return;
    Buffer* obq ;
    if(temp->LLC == 0) {
        terminateQ.pop();
        if(!emptyQ.empty()) {
            obq = emptyQ.front();
            obq->status = 2;
            for(int i = 0 ; i < 40; i++) {
                if(i < temp->terminateMsg.length()) obq->value[i] = temp->terminateMsg[i];
                else obq->value[i] = ' '; 
            }
            outputfulBufferQ.push(obq);
            emptyQ.pop();
        }
        return;
    }
    obq = emptyQ.front();
    emptyQ.pop();
    obq->status = 2;
    int k = 0;
    for(int i = 0; i<10; i++)
        for(int j = 0; j<K; j++) obq->value[k++] = DrumMemory[temp->O+i][j];
    outputfulBufferQ.push(obq);
    temp->O+=10;
    temp->LLC--;
}

void MOS::IRI1(){
    eof = cardReader();
    if(eof !=1 && !emptyQ.empty()) startCH(0);
}

void MOS::IRI2(){
    if(outputfulBufferQ.empty()) return;
    Buffer* temp = outputfulBufferQ.front();
    outputfulBufferQ.pop();
    
    temp->value[39] = '\0'; 
    fo << temp->value << "\n"; 
    
    temp->status = 0;
    temp->initalize();
    emptyQ.push(temp);
    startCH(1);
}

void MOS::IRI3(){
    switch (task) {
    case TASK::IS: {
        if(inputfulBufferQ.empty()) break;
        if(drum<=490) startCH(2);
        
        Buffer* temp = inputfulBufferQ.front();
        inputfulBufferQ.pop();
        
        if(temp->value[0] == '$') {
            if(temp->value[1] == 'A') {
                pendingQ.front()->F = 'P';
                pendingQ.front()->P = drum;
            }
            else if(temp->value[1] == 'D'){
                pendingQ.front()->F = 'D';
                pendingQ.front()->D = drum;
            }
            else {
                pendingQ.front()->O = drum;
                pendingQ.front()->END = drum - 10;
                pendingQ.front()->status = STATUS::Loaded;
                PCB* temp = new PCB(pendingQ.front());
                loadQ.push(temp);
                task = TASK::LD;
                drum += (pendingQ.front()->TLL)*10; 
                pendingQ.pop();
            }
        }
        else store_bufferDrum(temp);
        
        temp->status = 0;
        temp->initalize();
        emptyQ.push(temp);
        break;
    }
    case TASK::LD: {
        if(loadQ.empty()) break;
        PCB* temp = loadQ.front();
        loadDrumMM(temp);
        temp->P_COUNT--;
        startCH(2);
        if(temp->P_COUNT == 0) {
            temp->status = STATUS::Ready;
            readyQ.push_back(temp); 
            sortReadyQueue(); 
            loadQ.pop();
        }
        break;
    }
    case TASK::RT: {
        if(inputOutputQ.empty()) break;
        PCB* temp = inputOutputQ.front();
        if(temp->D_COUNT == 0) {
            terminateQ.push(temp);
            inputOutputQ.pop();
            terminate(1,-1);
            break;
        }
        startCH(2);
        for(int i = 0 ; i< 10 ; i++)
            for(int j = 0 ; j<K ; j++) MainMemory[RA+i][j] = DrumMemory[temp->D+i][j];
        
        temp->D+=10; temp->D_COUNT--;
        readyQ.push_back(temp); 
        sortReadyQueue(); 
        inputOutputQ.pop();
        break;
    }
    case TASK::WT: {
        if(inputOutputQ.empty()) break;
        PCB* temp = inputOutputQ.front();
        temp->LLC++;
        if(temp->LLC > temp->TLL) {
            temp->LLC--;
            terminateQ.push(temp);
            inputOutputQ.pop();
            terminate(2,-1);
            break;
        }
        startCH(2);
        for(int i = 0 ; i< 10 ; i++)
            for(int j = 0 ; j<K ; j++) DrumMemory[temp->END+10+i][j] = MainMemory[RA+i][j];
        
        temp->END+=10;
        if(temp->status == STATUS::Terminate) {
            terminateQ.push(temp);
            terminate(3,-1);   
        }
        else {
            readyQ.push_back(temp); 
            sortReadyQueue(); 
        }
        inputOutputQ.pop();
        break;   
    }
    case TASK::OS: {
        if(terminateQ.empty()) break;
        startCH(2);
        PCB* temp = terminateQ.front();
        drum_to_OutputBuffer(temp);
        if(!( (IOI >> 1) & 1)) IOI|=2; 
        break;   
    }
    default: break;
    }

    if(!terminateQ.empty()) task = TASK::OS;
    else if(!inputfulBufferQ.empty() && drum <=490) task = TASK::IS;
    else if(!loadQ.empty()) task = TASK::LD;
    else if(!inputOutputQ.empty()) {
        PCB* temp = inputOutputQ.front();
        if(temp->status == STATUS::Read) task = TASK::RT;
        else task = TASK::WT;
    }
}

void MOS::masterMode(){
    if(!readyQ.empty() &&( PI || SI || TI)) {
        PCB* temp = readyQ.front();
        if(TI == 0 || TI == 1) {
            if(PI == 1) { terminateQ.push(temp); readyQ.pop_front(); terminate(4,-1); }
            else if(PI == 2) { terminateQ.push(temp); readyQ.pop_front(); terminate(5,-1); }
            else if(PI == 3) {
                string instruction = string(1,IR[0])+string(1, IR[1]);
                if(instruction=="PD" || instruction=="LR" || instruction=="CR") {
                    terminateQ.push(temp); readyQ.pop_front(); terminate(6,-1);      
                } else {
                    int m = Allocate()*10;
                    int itr = temp->PTR+stoi(string(1,IR[2])+string(1, IR[3]))/10;
                    MainMemory[itr][3] = '0'+ (m%100)/10;  
                    MainMemory[itr][2] = '0'+ (m/100);
                    MainMemory[itr][1] = '0'; MainMemory[itr][0] = '0';  
                    temp->IC--; PI = 0;
                    return;        
                }            	    
            }
            else if(SI == 1) {
                temp->status = STATUS::Read; inputOutputQ.push(temp); readyQ.pop_front(); task = TASK::RT; SI = 0;
            }
            else if(SI == 2) {
                temp->status = STATUS::Write; inputOutputQ.push(temp); readyQ.pop_front(); task = TASK::WT; SI = 0;
            }
            else if(SI == 3) {
                terminateQ.push(temp); readyQ.pop_front(); terminate(0,-1); SI = 0;
            }   
        }
        else {
            if(PI == 1) { terminateQ.push(temp); readyQ.pop_front(); terminate(3,4); }
            else if(PI == 2) { terminateQ.push(temp); readyQ.pop_front(); terminate(3,5); }        
            else if(PI ==3) { terminateQ.push(temp); readyQ.pop_front(); terminate(3,-1); }        
            else if(SI == 1) { terminateQ.push(temp); readyQ.pop_front(); terminate(3,-1); }          
            else if(SI == 2) {
                readyQ.pop_front(); task = TASK::WT; temp->status = STATUS::Write;
                inputOutputQ.push(temp); temp->status = STATUS::Terminate;
            }
            else if(SI == 3) { terminateQ.push(temp); readyQ.pop_front(); terminate(0,-1); }
        }  
    }
        
    if( (IOI >> 2) & 1) IRI3();
    if( (IOI >> 1) & 1) IRI2();
    if( (IOI >> 0) & 1) IRI1();
}

void MOS::store_bufferDrum(Buffer* temp){
    int k= 0;
    for(int i = 0 ; i< 10 ; i++){
        for(int j = 0 ; j<K ; j++){
            if(temp->value[k]=='\0') break;
            DrumMemory[drum+i][j] = temp->value[k++];   
        }
    }
    drum+=10;
}

MOS::MOS(){
    fi.open("Correct1.txt",ios::in); 
    fo.open("output.txt",ios::out); 
    memset(DrumMemory,' ', sizeof(DrumMemory));
}

void MOS::close_all(){ fi.close(); fo.close(); }

void MOS::terminate(int EM1 , int EM2){
    task = TASK::OS; 
    if(terminateQ.empty()) return;
    PCB* temp = terminateQ.back();
    
    temp->status = STATUS::Terminate;
    string msg ;
    if(EM1 == 0) msg = "ALL GOOD";
    else if(EM1 == 1) msg="OUT OF DATA ERROR";
    else if(EM1 == 2) msg="LINE LIMIT EXCEEDED";
    else if(EM1 == 6) msg="INVALID PAGE FAULT";
    else if(EM1 == 4) msg="OPCODE ERROR";
    else if(EM1 == 5) msg="Operand Error";
    else {
        if(EM2 == -1) msg="Time Limit Exceeded Error";
        else if(EM2 == 4) msg+=" Opcode Error";
        else msg+=" Operand Error";      
    }
    temp->terminateMsg = msg;
    
    // Announce job completion in the terminal
    cout << "\n[TERMINATED] Job ID: " << temp->ID << " finished execution. Status: " << msg << endl;

    fo<<"SI: "<<SI<<" TI: "<<TI<<" PI: "<<PI<<"\n";
    fo<<"IC: "<<temp->IC<<" TTC: "<<temp->TTC<<" TTL: "<<temp->TTL<<" LLC: "<<temp->LLC<<" TLL: "<<temp->TLL<<"\n\n";	
    PI = 0 ; SI = 0 ; TI = 0;
} 

void MOS::simulation() {
    for(int i = 0 ; i<3 ; i++) {
        if(ch[i].flag) {        
            ch[i].time++;
            if(ch[i].time == ch[i].total_time) {
                IOI|= ch[i].value;
                ch[i].flag = 0; 
            }
        }
    }
}

void MOS::startCH(int channel){
    IOI &= (7-ch[channel].value);
    ch[channel].time = 0;
    ch[channel].flag = 1; 
}