"""
Scenario Library & Simulation Engine View
─────────────────────────────────────────
Interactive scenario cards, step-by-step background simulation runner,
speed control slider, and scenario reset options.
"""

import tkinter as tk
from tkinter import ttk
from gui.theme import (
    BG_BASE, BG_PANEL, BG_CARD, BG_CARD_ALT, BG_INPUT,
    BORDER_DEFAULT, BORDER_FOCUS, CYAN, PURPLE,
    SUCCESS, WARNING, DANGER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    get_fonts
)
from gui.components.cards import SectionCard, StatusBadge


class ScenarioView(tk.Frame):
    """Preset scenario library and background simulation execution panel."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_BASE)
        self.app = app
        self.fonts = get_fonts()

        self._scenario_var = tk.StringVar(value="dining_philosophers")
        self._speed_var = tk.DoubleVar(value=0.6)

        self._build_layout()

    def _build_layout(self):
        # 1. Top Section: Global Simulation Runner Bar
        ctrl_card = SectionCard(
            self,
            title="Simulation Engine Controls",
            subtitle="Control real-time asynchronous process competition and allocation speed",
            badge_text="BACKGROUND RUNNER",
            badge_color=CYAN
        )
        ctrl_card.pack(fill="x", padx=16, pady=(16, 12))

        ctrl_bar = tk.Frame(ctrl_card, bg=BG_CARD)
        ctrl_bar.pack(fill="x", pady=6)

        # Run Simulation
        btn_run = ttk.Button(
            ctrl_bar,
            text="▶  Run Simulation Steps",
            style="Success.TButton",
            command=self._on_run_simulation
        )
        btn_run.pack(side="left", padx=(0, 8))

        # Stop Simulation
        btn_stop = ttk.Button(
            ctrl_bar,
            text="⏹  Stop Simulation",
            style="Danger.TButton",
            command=self._on_stop_simulation
        )
        btn_stop.pack(side="left", padx=(0, 20))

        # Speed Slider
        tk.Label(
            ctrl_bar,
            text="Step Delay (Speed):",
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
            font=self.fonts["caption_bold"]
        ).pack(side="left", padx=(0, 8))

        scale = ttk.Scale(
            ctrl_bar,
            from_=0.1,
            to=2.0,
            variable=self._speed_var,
            orient="horizontal",
            length=160,
            command=self._on_speed_change
        )
        scale.pack(side="left", padx=(0, 8))

        self.lbl_speed_val = tk.Label(
            ctrl_bar,
            text="0.6s / step",
            bg=BG_CARD,
            fg=CYAN,
            font=self.fonts["mono_sm_bold"]
        )
        self.lbl_speed_val.pack(side="left", padx=(0, 20))

        # Clear All Button
        btn_clear = ttk.Button(
            ctrl_bar,
            text="🗑 Reset & Clear All",
            style="Ghost.TButton",
            command=self.app.clear_all_with_confirm
        )
        btn_clear.pack(side="right")

        # 2. Main Section: Scenario Cards Grid
        lib_card = SectionCard(
            self,
            title="Preset Scenario Library",
            subtitle="Curated classic OS concurrency models demonstrating deadlock behaviors"
        )
        lib_card.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Scrollable container for cards
        canvas = tk.Canvas(lib_card, bg=BG_CARD, highlightthickness=0)
        scroll = ttk.Scrollbar(lib_card, orient="vertical", command=canvas.yview)
        scroll.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        canvas.configure(yscrollcommand=scroll.set)

        self.cards_frame = tk.Frame(canvas, bg=BG_CARD)
        canvas.create_window((0, 0), window=self.cards_frame, anchor="nw", width=880)

        self.cards_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Define Scenario Definitions
        scenarios = [
            {
                "id": "dining_philosophers",
                "title": "🍝 Dining Philosophers Problem",
                "procs": "5 Processes (Philosophers)",
                "res": "5 Resources (Chopstick Mutexes)",
                "expected": "Circular Ring Deadlock",
                "desc": "Five philosophers sitting around a table share five chopsticks. Each philosopher requires both the left and right chopstick to eat. When all pick up their left chopstick simultaneously, a circular wait deadlock occurs.",
                "badge": "CLASSIC OS MODEL",
                "color": DANGER
            },
            {
                "id": "bankers_classic",
                "title": "🏦 Banker's Algorithm Classic Scenario",
                "procs": "4 Processes (A, B, C, D)",
                "res": "3 Devices (Tape, Disk, Printer)",
                "expected": "Unsafe Allocation State",
                "desc": "Models a multi-resource operating system where processes make heavy overlapping claims on tape drives, disk units, and printers, triggering an unsafe Banker's state where no safe sequence exists.",
                "badge": "BANKER TEST",
                "color": WARNING
            },
            {
                "id": "producer_consumer",
                "title": "📦 Producer-Consumer Buffer Contention",
                "procs": "4 Processes (2 Producers, 2 Consumers)",
                "res": "4 Resources (Buffer Mutex, Semaphores)",
                "expected": "Lock Starvation Deadlock",
                "desc": "Producers and consumers interact across a bounded buffer. Nested locking between buffer mutexes and semaphore counters leads to mutual resource lockup.",
                "badge": "SEMAPHORE SYNC",
                "color": PURPLE
            },
            {
                "id": "readers_writers",
                "title": "📖 Readers-Writers Lock Starvation",
                "procs": "5 Processes (2 Writers, 3 Readers)",
                "res": "3 Resources (Read Lock, Write Lock, Log)",
                "expected": "Write Starvation Deadlock",
                "desc": "Multiple reader threads and writer threads compete for database read-write locks and logging handles, causing write lock contention and circular dependency.",
                "badge": "READ/WRITE LOCKS",
                "color": CYAN
            },
            {
                "id": "random_chaos",
                "title": "🎲 Random Chaos Procedural Generator",
                "procs": "3–6 Randomized Processes",
                "res": "2–5 Randomized Resources",
                "expected": "Unpredictable Concurrency",
                "desc": "Procedurally generates random processes, resource types, instance counts, and asynchronous requests to simulate unpredictable stress-testing conditions.",
                "badge": "STRESS TEST",
                "color": SUCCESS
            }
        ]

        for s in scenarios:
            self._create_scenario_card(self.cards_frame, s)

    def _create_scenario_card(self, parent, s: dict):
        card = tk.Frame(
            parent,
            bg=BG_INPUT,
            highlightbackground=BORDER_DEFAULT,
            highlightthickness=1,
            padx=16,
            pady=14
        )
        card.pack(fill="x", pady=6, padx=4)

        # Header Row: Title & Badges
        hdr = tk.Frame(card, bg=BG_INPUT)
        hdr.pack(fill="x")

        tk.Label(
            hdr, text=s["title"], bg=BG_INPUT, fg=TEXT_PRIMARY, font=self.fonts["subheading"]
        ).pack(side="left")

        StatusBadge(hdr, text=s["badge"], color=s["color"]).pack(side="right")

        # Metadata Row
        meta = tk.Frame(card, bg=BG_INPUT)
        meta.pack(fill="x", pady=(6, 8))

        tk.Label(
            meta, text=f"⚙ {s['procs']}   •   ◈ {s['res']}   •   ⚠ Expected: {s['expected']}",
            bg=BG_INPUT, fg=CYAN, font=self.fonts["mono_sm_bold"]
        ).pack(side="left")

        # Description
        tk.Label(
            card, text=s["desc"], bg=BG_INPUT, fg=TEXT_SECONDARY, font=self.fonts["caption"],
            wraplength=700, justify="left"
        ).pack(anchor="w", pady=(0, 10))

        # Bottom Action Bar
        act_bar = tk.Frame(card, bg=BG_INPUT)
        act_bar.pack(fill="x")

        btn_load = ttk.Button(
            act_bar,
            text=f"📂 Load '{s['title'].split()[1]}' Scenario",
            style="Accent.TButton",
            command=lambda sid=s["id"]: self._on_load_scenario(sid)
        )
        btn_load.pack(side="left")

    # ── User Actions ──────────────────────────────────────────────────────────

    def _on_speed_change(self, val):
        delay = round(float(val), 2)
        self.lbl_speed_val.configure(text=f"{delay}s / step")
        self.app.sim.set_speed(delay)

    def _on_load_scenario(self, scenario_id: str):
        self._scenario_var.set(scenario_id)
        self.app.load_scenario_by_name(scenario_id)

    def _on_run_simulation(self):
        scenario_id = self._scenario_var.get()
        self.app.sim.set_speed(self._speed_var.get())
        self.app.sim.run_scenario_steps(scenario_id)
        self.app.toast(f"Simulation steps executing in background ({scenario_id})", "info")

    def _on_stop_simulation(self):
        self.app.sim.stop()
        self.app.toast("Simulation background runner halted", "warn")

    def update_view(self, snapshot: dict, detection_result=None):
        pass
