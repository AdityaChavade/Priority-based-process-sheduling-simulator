# OSim Nexus — Operating Systems Simulation & Visualization Lab

**OSim Nexus** is an educational OS simulation and benchmarking suite built with a modern decoupled client-server architecture:
- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS + Framer Motion + Lucide React + Recharts
- **Backend**: FastAPI + Python 3.14 + Pydantic v2 + Uvicorn + Pytest

---

## 🌟 Modules & Features

### 1. CPU Scheduling (`/cpu`)
- **Algorithms**: FCFS, SJF, SRTF, Round Robin, Priority (Non-Preemptive), Priority (Preemptive).
- **Visuals**: Dynamic color-coded Gantt chart, metrics table (Completion Time, Turnaround Time, Waiting Time, Response Time), CPU utilization %, throughput, and context switch counts.
- **Controls**: Interactive process table editor, customizable time quantum, preset workloads.

### 2. Contiguous Memory Management (`/memory`)
- **Algorithms**: First Fit, Best Fit, Worst Fit, Next Fit.
- **Visuals**: Dynamic segmented memory bar, hole size tracking, allocation/deallocation queues.
- **Metrics**: External fragmentation calculation, allocation failures, contiguous hole coalescing.

### 3. Page Replacement (`/paging`)
- **Algorithms**: FIFO, LRU, Optimal (Bélády), Second Chance (Clock).
- **Visuals**: Step-by-step frame matrix, hit/fault badges, hit/fault ratio progress bars.
- **Controls**: Reference string input, configurable frame count (1–10).

### 4. Deadlock Analysis Lab (`/deadlock`)
- **Banker's Algorithm**:
  - Validates Need matrix ($Max - Allocation$).
  - Determines if system is in a Safe State and calculates a valid Safe Sequence.
  - Detects unsafe states with explanatory messages.
- **Deadlock Detection**:
  - Resource allocation matrix algorithm using Available, Allocation, and Request matrices.
  - Detects deadlocked cycles and flags exact deadlocked processes ($P_0, P_1, \dots$).
  - Presets: Deadlocked Cycle ($P_0 \leftrightarrow P_1$) and Deadlock-Free Allocation.

### 5. Disk Scheduling (`/disk`)
- **Algorithms**: FCFS, SSTF, SCAN (Elevator), C-SCAN, LOOK, C-LOOK.
- **Visuals**: Head movement seek sequence plot, direction toggle (Right / Left).
- **Metrics**: Total head movement (cylinders), average seek distance.

### 6. Process Synchronization Lab (`/sync`)
- **Bounded Buffer (Producer-Consumer)**:
  - Genuine step-interactive execution backed by deterministic semaphore engine.
  - Interactive **Produce** and **Consume** actions.
  - Semaphores tracking: `empty`, `full`, `mutex`.
  - Visual bounded buffer shelf and capacity overflow/underflow blocking states.
- **Dining Philosophers**:
  - Genuine step-interactive state machine ($N=2\dots8$ philosophers).
  - Direct individual philosopher actions: **Pick Up** and **Put Down**.
  - State indicators: `THINKING` (purple), `HUNGRY` (amber), `EATING` (green).
  - Shared fork resource locks and neighbor contention detection.

### 7. Algorithm Benchmarking Lab (`/lab`)
- Head-to-head multi-algorithm comparisons across:
  - **CPU Scheduling**: Side-by-side comparison matrix and Gantt charts with best-in-category (★) highlights.
  - **Page Replacement**: Direct benchmark of FIFO, LRU, Optimal, and Second Chance with Page Faults and Hit Ratios.
  - **Disk Scheduling**: Comparison of FCFS, SSTF, SCAN, C-SCAN, LOOK, and C-LOOK with Total Head Movement.

### 8. Documentation (`/docs`)
- Comprehensive interactive algorithm cards detailing concepts, time complexity, space complexity, advantages, and limitations.

---

## 🚀 Getting Started

### Backend Setup (FastAPI)
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup (React 19 + Vite)
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173/` in your browser.

---

## 🧪 Testing & QA

### Backend Pytest Suite
```bash
cd backend
python -m pytest tests/ -v
```
*Current test suite: 60/60 passing tests covering all algorithms, edge cases, preemption, and REST API endpoints.*

### Frontend Production Build
```bash
cd frontend
npm run build
```

### ESLint Verification
```bash
cd frontend
npm run lint
```

---

## 📝 Limitations & Notes
1. **Deterministic Concurrency Simulation**:
   - The Synchronization lab is an educational discrete-event model demonstrating semaphore arithmetic and state machine transitions. It simulates concurrency deterministically rather than spawning asynchronous OS threads or IPC semaphores.
2. **Textbook Scope**:
   - Algorithms adhere strictly to standard textbook specifications (Silberschatz, Galvin, Gagne).
