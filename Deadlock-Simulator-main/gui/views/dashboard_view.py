"""
Dashboard View — Primary OS Control Center
──────────────────────────────────────────
Displays the 4 core system metrics, prominent Resource Allocation Graph,
compact system health telemetry, and operations toolbar.
"""

import tkinter as tk
from tkinter import ttk
from gui.theme import (
    BG_BASE, BG_PANEL, BG_CARD, BG_CARD_ALT, BG_INPUT,
    BORDER_DEFAULT, BORDER_SUBTLE, BORDER_FOCUS, CYAN, CYAN_DIM, PURPLE,
    SUCCESS, WARNING, DANGER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    get_fonts
)
from gui.components.cards import StatCard, SectionCard, StatusBadge
from gui.graph_renderer import GraphRenderer


class DashboardView(tk.Frame):
    """Primary system dashboard presenting real-time system metrics and graph."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_BASE)
        self.app = app
        self.fonts = get_fonts()

        self._build_layout()

    def _build_layout(self):
        # 1. Top Metrics Deck: Exactly 4 metrics (Processes, Resources, Allocated Units, System State)
        metrics_deck = tk.Frame(self, bg=BG_BASE)
        metrics_deck.pack(fill="x", padx=16, pady=(12, 10))

        for i in range(4):
            metrics_deck.grid_columnconfigure(i, weight=1, uniform="stat_cards")

        # Metric 1: Processes
        self.card_proc = StatCard(
            metrics_deck,
            title="Processes",
            initial_value="0",
            accent_color=CYAN,
            subtext="0 active"
        )
        self.card_proc.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Metric 2: Resources
        self.card_res = StatCard(
            metrics_deck,
            title="Resources",
            initial_value="0",
            accent_color=PURPLE,
            subtext="0 free"
        )
        self.card_res.grid(row=0, column=1, sticky="nsew", padx=(0, 8))

        # Metric 3: Allocated Units
        self.card_alloc = StatCard(
            metrics_deck,
            title="Allocated Units",
            initial_value="0",
            accent_color=SUCCESS,
            subtext="0 total capacity"
        )
        self.card_alloc.grid(row=0, column=2, sticky="nsew", padx=(0, 8))

        # Metric 4: System State
        self.card_state = StatCard(
            metrics_deck,
            title="System State",
            initial_value="SAFE",
            accent_color=SUCCESS,
            subtext="No deadlocks detected"
        )
        self.card_state.grid(row=0, column=3, sticky="nsew")

        # 2. Main Work Area: Large Graph (Primary) + Compact Operations & Telemetry (Right)
        main_paned = tk.PanedWindow(
            self,
            orient="horizontal",
            bg=BG_BASE,
            sashwidth=4,
            sashrelief="flat"
        )
        main_paned.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # Left / Center: Graph Container (Receives maximum visual priority)
        graph_container = tk.Frame(
            main_paned,
            bg=BG_CARD,
            highlightbackground=BORDER_DEFAULT,
            highlightthickness=1
        )
        main_paned.add(graph_container, minsize=600, stretch="always")
        self._build_graph_section(graph_container)

        # Right: Operations & System Health (Compact, technical)
        right_container = tk.Frame(
            main_paned,
            bg=BG_PANEL,
            width=320
        )
        main_paned.add(right_container, minsize=290, stretch="never")
        self._build_right_section(right_container)

    def _build_graph_section(self, parent):
        # Graph Toolbar Header
        toolbar = tk.Frame(parent, bg=BG_CARD, height=38)
        toolbar.pack(fill="x", padx=10, pady=(6, 4))
        toolbar.pack_propagate(False)

        # Mode Selection
        tk.Label(
            toolbar,
            text="Graph Mode:",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=self.fonts["caption_bold"]
        ).pack(side="left", padx=(0, 8))

        btn_rag = ttk.Radiobutton(
            toolbar,
            text="Resource Allocation Graph (RAG)",
            variable=self.app.graph_mode,
            value="rag",
            command=self.app.refresh_graph
        )
        btn_rag.pack(side="left", padx=(0, 10))

        btn_wfg = ttk.Radiobutton(
            toolbar,
            text="Wait-For Graph (WFG)",
            variable=self.app.graph_mode,
            value="wfg",
            command=self.app.refresh_graph
        )
        btn_wfg.pack(side="left", padx=(0, 12))

        # Viewport Navigation Controls
        btn_reset = ttk.Button(
            toolbar,
            text="↺ Reset",
            style="Ghost.TButton",
            command=lambda: self.renderer.reset_view()
        )
        btn_reset.pack(side="right", padx=(3, 0))

        btn_zoom_out = ttk.Button(
            toolbar,
            text="− Zoom",
            style="Ghost.TButton",
            command=lambda: self.renderer.zoom_out()
        )
        btn_zoom_out.pack(side="right", padx=(3, 0))

        btn_zoom_in = ttk.Button(
            toolbar,
            text="+ Zoom",
            style="Ghost.TButton",
            command=lambda: self.renderer.zoom_in()
        )
        btn_zoom_in.pack(side="right", padx=(3, 0))

        # Graph Canvas
        self.canvas = tk.Canvas(
            parent,
            bg=BG_BASE,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=4, pady=(0, 6))
        self.renderer = GraphRenderer(self.canvas)
        self.app.renderer = self.renderer

    def _build_right_section(self, parent):
        # 1. System Health & Safety (Technical list, non-decorative)
        health_card = SectionCard(
            parent,
            title="System Health",
            subtitle="Multi-algorithm validation"
        )
        health_card.pack(fill="x", padx=2, pady=(0, 8))

        health_box = tk.Frame(health_card, bg=BG_INPUT, highlightbackground=BORDER_SUBTLE, highlightthickness=1, padx=10, pady=8)
        health_box.pack(fill="x", pady=2)

        self.row_rag_status = self._create_health_row(health_box, "RAG / DFS", "No cycles detected", SUCCESS)
        self.row_banker_status = self._create_health_row(health_box, "Banker", "Safe state confirmed", SUCCESS)
        self.row_wfg_status = self._create_health_row(health_box, "Wait-For Graph", "No circular waits", SUCCESS)

        # 2. Operations (Ranked: Primary Run Detection, Secondary Simulation/Scenario, Destructive Clear)
        ops_card = SectionCard(
            parent,
            title="Operations",
            subtitle="Simulation & detection commands"
        )
        ops_card.pack(fill="x", padx=2, pady=(0, 8))

        # Primary Operation: Run Detection
        ttk.Button(
            ops_card,
            text="Run Detection",
            style="Accent.TButton",
            command=self.app.run_detection
        ).pack(fill="x", pady=(2, 4))

        # Secondary Operations
        sec_grid = tk.Frame(ops_card, bg=BG_CARD)
        sec_grid.pack(fill="x", pady=(0, 6))
        sec_grid.grid_columnconfigure((0, 1), weight=1)

        ttk.Button(
            sec_grid,
            text="Run Simulation",
            style="TButton",
            command=self.app.run_simulation
        ).grid(row=0, column=0, sticky="ew", padx=(0, 3))

        ttk.Button(
            sec_grid,
            text="Load Scenario",
            style="TButton",
            command=lambda: self.app.load_scenario_by_name("dining_philosophers")
        ).grid(row=0, column=1, sticky="ew", padx=(3, 0))

        # Divider for destructive action
        sep = tk.Frame(ops_card, bg=BORDER_SUBTLE, height=1)
        sep.pack(fill="x", pady=(2, 6))

        # Destructive Clear System (Separated with warning style)
        ttk.Button(
            ops_card,
            text="Clear System State",
            style="Danger.TButton",
            command=self.app.clear_all_with_confirm
        ).pack(fill="x")

        # 3. Recent Events Mini-Feed
        event_card = SectionCard(
            parent,
            title="Recent Events",
            action_btn_text="Full Log →",
            on_action=lambda: self.app.navigate_to("event_log")
        )
        event_card.pack(fill="both", expand=True, padx=2)

        self.event_feed = tk.Text(
            event_card,
            bg=BG_INPUT,
            fg=TEXT_PRIMARY,
            font=self.fonts["mono_sm"],
            wrap="word",
            state="disabled",
            borderwidth=0,
            padx=8,
            pady=6
        )
        self.event_feed.pack(fill="both", expand=True)

        self.event_feed.tag_config("time", foreground=TEXT_MUTED)
        self.event_feed.tag_config("allocate", foreground=SUCCESS)
        self.event_feed.tag_config("request", foreground=WARNING)
        self.event_feed.tag_config("release", foreground=CYAN)
        self.event_feed.tag_config("terminate", foreground=DANGER)
        self.event_feed.tag_config("rollback", foreground=PURPLE)
        self.event_feed.tag_config("scenario", foreground=CYAN)
        self.event_feed.tag_config("default", foreground=TEXT_SECONDARY)

    def _create_health_row(self, parent, title: str, initial_text: str, color: str):
        row = tk.Frame(parent, bg=BG_INPUT)
        row.pack(fill="x", pady=2)

        lbl_title = tk.Label(
            row,
            text=f"{title:<16}",
            bg=BG_INPUT,
            fg=TEXT_SECONDARY,
            font=self.fonts["caption"]
        )
        lbl_title.pack(side="left")

        lbl_val = tk.Label(
            row,
            text=initial_text,
            bg=BG_INPUT,
            fg=color,
            font=self.fonts["mono_sm"]
        )
        lbl_val.pack(side="right")
        return lbl_val

    # ── Update Routine ────────────────────────────────────────────────────────

    def update_view(self, snapshot: dict, detection_result=None):
        processes = snapshot.get("processes", {})
        resources = snapshot.get("resources", {})
        events = snapshot.get("events", [])

        num_proc = len(processes)
        active_proc = sum(1 for p in processes.values() if p.get("state") == "running")

        total_res = len(resources)
        total_capacity = sum(r.get("total", 0) for r in resources.values())
        allocated_units = sum(r.get("allocated", 0) for r in resources.values())
        avail_units = sum(r.get("available", 0) for r in resources.values())

        # Update 4 Core Top Metrics
        self.card_proc.update_value(
            str(num_proc),
            f"{active_proc} running"
        )
        self.card_res.update_value(
            str(total_res),
            f"{avail_units} free units"
        )
        self.card_alloc.update_value(
            str(allocated_units),
            f"of {total_capacity} capacity"
        )

        is_deadlocked = detection_result and detection_result.detected
        if is_deadlocked:
            self.card_state.update_value(
                "DEADLOCK",
                f"{len(detection_result.deadlocked_processes)} processes stuck",
                accent_color=DANGER
            )
            self.row_rag_status.configure(
                text=f"{len(getattr(detection_result, 'cycle_path', []))} cycle(s) detected",
                fg=DANGER
            )
            self.row_banker_status.configure(text="Unsafe state", fg=DANGER)
            self.row_wfg_status.configure(
                text=f"{len(detection_result.deadlocked_processes)} circular waits",
                fg=DANGER
            )
        else:
            self.card_state.update_value(
                "SAFE",
                "Deadlock-free",
                accent_color=SUCCESS
            )
            self.row_rag_status.configure(text="No cycles detected", fg=SUCCESS)
            if detection_result and getattr(detection_result, "safe_sequence", None):
                self.row_banker_status.configure(text="Safe state confirmed", fg=SUCCESS)
            else:
                self.row_banker_status.configure(text="Safe state confirmed", fg=SUCCESS)
            self.row_wfg_status.configure(text="No circular waits", fg=SUCCESS)

        # Update Recent Events stream
        self.event_feed.configure(state="normal")
        self.event_feed.delete("1.0", "end")
        for ev in reversed(events[-12:]):
            tag = ev.get("type", "default")
            self.event_feed.insert("end", f"[{ev['timestamp']}] ", "time")
            self.event_feed.insert("end", f"{ev['message']}\n", tag)
        self.event_feed.configure(state="disabled")
