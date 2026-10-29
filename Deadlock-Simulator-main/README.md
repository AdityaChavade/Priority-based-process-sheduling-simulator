# ⚡ DEADLOCKNEXUS — Adaptive Deadlock Detection & Recovery Simulator

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Modern%20Tkinter-00C6FF?style=flat-square)
![OS](https://img.shields.io/badge/Topic-Operating%20Systems-23D18B?style=flat-square)
![Tests](https://img.shields.io/badge/Tests-23%20Passing-success?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

An advanced Operating Systems research and simulation platform that models, detects, visualizes, and automatically recovers from deadlocks using classic OS algorithms and recovery strategies — featuring a high-contrast cyber control center UI and interactive Resource Allocation Graph.

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Algorithms](#-algorithms) • [Project Structure](#-project-structure)

---

## 📌 What is DEADLOCKNEXUS?

In an Operating System, a **deadlock** occurs when two or more processes are each waiting for a resource held by the other — forming a circular dependency that none can escape without external intervention.

**DEADLOCKNEXUS** provides a technical OS command center to:

- 🔧 **Provision & Manage** processes and resources with real-time state tracking
- 👁️ **Visualize Topologies** with an interactive pan/zoom Resource Allocation & Wait-For Graph
- 🔍 **Execute Formal Detection** using 3 standard OS detection algorithms (RAG/DFS, Banker's, WFG)
- 🛠️ **Automate Recovery** using 4 standard resolution strategies with step-by-step audit logging
- 📊 **Analyze Contention** with real system metrics, bottleneck rankings, and utilization telemetry
- 📋 **Audit Activity** with a filterable, timestamped OS event stream

> Built with **pure Python** standard library — no external web servers, heavy dependencies, or fake metrics.

---

## 📁 Project Structure

```
Deadlock-Simulator/
│
├── main.py                      ← Entry point (GUI)
├── cli.py                       ← Headless CLI demo
├── requirements.txt             ← Optional testing dependencies
├── README.md
│
├── core/                        ← Core OS Business & Algorithmic Logic
│   ├── resource_manager.py      ← Thread-safe OS resource allocation table
│   ├── deadlock_detector.py     ← RAG / Banker's / WFG algorithms
│   ├── recovery_engine.py       ← 4 recovery strategies (Kill, Preempt, Rollback, Kill All)
│   └── simulation_engine.py     ← Preset scenarios & background execution thread
│
├── gui/                         ← Modern Cyber UI / UX Presentation Layer
│   ├── theme.py                 ← Unified design tokens, color palette, and TTK styles
│   ├── graph_renderer.py        ← High-contrast canvas graph with pan/zoom & cycle glow
│   ├── main_window.py           ← Primary application shell & navigation
│   ├── components/              ← Reusable UI widgets
│   │   ├── cards.py             ← Stat cards, section containers & badges
│   │   ├── dialogs.py           ← Styled modal confirmation dialogs
│   │   └── toast.py             ← Floating animated toast notifications
│   └── views/                   ← Screen controllers
│       ├── dashboard_view.py    ← Primary overview, metrics & graph
│       ├── process_view.py      ← Process creation & lifecycle control
│       ├── resource_view.py     ← Resource provisioning & instance tracking
│       ├── allocation_view.py   ← Request/release workbench & matrices
│       ├── detection_view.py    ← Detection engine & diagnostic analysis
│       ├── recovery_view.py     ← Recovery center & execution audit log
│       ├── scenario_view.py     ← Scenario library & speed runner
│       ├── event_log_view.py    ← Filterable chronological audit log
│       └── analytics_view.py    ← Telemetry, utilization & bottleneck analysis
│
└── tests/                       ← Automated Unit & Integration Test Suite
    ├── test_core.py             ← 18 core algorithmic unit tests
    └── test_gui.py              ← 5 GUI integration & automation tests
```

---

## 🧪 Running Tests

```bash
# Run all automated tests:
python -m unittest discover tests

# Or run individual test suites:
python tests/test_core.py
python -m unittest tests/test_gui.py
```

Tests cover:

- Resource allocation and blocking
- All 3 detection algorithms (2-process and 3-process cycles)
- All 4 recovery strategies
- Priority-based victim selection
- Clean-state (no deadlock) verification

---

## 📚 OS Concepts Covered

| Concept                   | Where in Project                                          |
| ------------------------- | --------------------------------------------------------- |
| Mutual Exclusion          | Resources with limited instances                          |
| Hold and Wait             | Processes hold one resource while requesting another      |
| No Preemption             | Default system behaviour (overridden by preempt strategy) |
| Circular Wait             | Detected by RAG and WFG cycle detection                   |
| Banker's Algorithm        | `deadlock_detector.py` — `_bankers_detection()`           |
| Resource Allocation Graph | `graph_renderer.py` + `deadlock_detector.py`              |
| Process Termination       | `recovery_engine.py` — `_terminate_victim()`              |
| Thread Safety             | `threading.Lock` in `resource_manager.py`                 |

---

## 🔧 Technologies Used

- **Python 3.8+** — Core language
- **Tkinter** — GUI framework (built-in)
- **threading** — Concurrency and thread safety
- **dataclasses** — Clean data modelling
- **unittest** — Automated testing
- **psutil** — System monitoring (optional)

---

## 📖 References

- Silberschatz, Galvin & Gagne — _Operating System Concepts_ (10th ed.)
- Tanenbaum & Bos — _Modern Operating Systems_ (4th ed.)
- Dijkstra, E.W. (1965) — _Solution of a problem in concurrent programming control_
- Coffman, Elphick & Shoshani (1971) — _System Deadlocks_

---

## 👨‍💻 Author

**Owais Tanoli**

- GitHub: [@OwaisTanoli71](https://github.com/OwaisTanoli71)
- Course: Operating Systems — Pak-Austria Fachhochschule Institute of Applied Sciences and Technology

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

⭐ **If you found this useful, please give it a star!** ⭐

</div>

---

## 🙏 Acknowledgement

I would like to express my sincere gratitude to my **Operating Systems Lab Instructor**, **Ms. Hamna Iqbal**, for her continuous guidance, support, and encouragement throughout this project. Her teaching made complex OS concepts easy to understand and implement practically. 

🔗 GitHub: [@HamnaIqbal44](https://github.com/HamnaIqbal44)
