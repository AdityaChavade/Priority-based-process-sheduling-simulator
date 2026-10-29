"""
Deadlock Detection Control Center
─────────────────────────────────
Primary OS analysis workbench: Algorithm selection (RAG DFS, Banker's, WFG),
instant execution, and rich diagnostic inspection of cycles and safety sequences.
"""

import tkinter as tk
from tkinter import ttk
from gui.theme import (
    BG_BASE, BG_PANEL, BG_CARD, BG_CARD_ALT, BG_INPUT,
    BORDER_DEFAULT, BORDER_SUBTLE, BORDER_FOCUS, CYAN, PURPLE,
    SUCCESS, WARNING, DANGER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    get_fonts
)
from gui.components.cards import SectionCard, StatusBadge


class DetectionView(tk.Frame):
    """Dedicated detection control center and diagnostic reporting engine."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_BASE)
        self.app = app
        self.fonts = get_fonts()

        self._algo_var = tk.StringVar(value="rag")
        self._build_layout()

    def _build_layout(self):
        # 1. Top Section: Algorithm Selection Bar
        selector_card = SectionCard(
            self,
            title="Algorithm Selection",
            subtitle="Choose theoretical OS analysis technique"
        )
        selector_card.pack(fill="x", padx=16, pady=(12, 10))

        algo_grid = tk.Frame(selector_card, bg=BG_CARD)
        algo_grid.pack(fill="x", pady=4)
        algo_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="algos")

        # 1. RAG
        c_rag = tk.Frame(algo_grid, bg=BG_INPUT, highlightbackground=BORDER_DEFAULT, highlightthickness=1, padx=10, pady=8)
        c_rag.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        rb_rag = ttk.Radiobutton(c_rag, text="Resource Allocation Graph (RAG)", variable=self._algo_var, value="rag")
        rb_rag.pack(anchor="w")
        tk.Label(c_rag, text="DFS cycle detection on bipartite graph.\nComplexity: O(V + E)", bg=BG_INPUT, fg=TEXT_MUTED, font=self.fonts["caption"], justify="left").pack(anchor="w", pady=(2, 0))

        # 2. Banker's
        c_bank = tk.Frame(algo_grid, bg=BG_INPUT, highlightbackground=BORDER_DEFAULT, highlightthickness=1, padx=10, pady=8)
        c_bank.grid(row=0, column=1, sticky="nsew", padx=2)
        rb_bank = ttk.Radiobutton(c_bank, text="Banker's Safety Algorithm", variable=self._algo_var, value="bankers")
        rb_bank.pack(anchor="w")
        tk.Label(c_bank, text="Matrix safety state simulation.\nComplexity: O(n² · m)", bg=BG_INPUT, fg=TEXT_MUTED, font=self.fonts["caption"], justify="left").pack(anchor="w", pady=(2, 0))

        # 3. WFG
        c_wfg = tk.Frame(algo_grid, bg=BG_INPUT, highlightbackground=BORDER_DEFAULT, highlightthickness=1, padx=10, pady=8)
        c_wfg.grid(row=0, column=2, sticky="nsew", padx=(4, 0))
        rb_wfg = ttk.Radiobutton(c_wfg, text="Wait-For Graph (WFG)", variable=self._algo_var, value="wfg")
        rb_wfg.pack(anchor="w")
        tk.Label(c_wfg, text="Process-only circular wait reduction.\nComplexity: O(P + E')", bg=BG_INPUT, fg=TEXT_MUTED, font=self.fonts["caption"], justify="left").pack(anchor="w", pady=(2, 0))

        # Action Bar: Prominent Execute Button
        act_bar = tk.Frame(selector_card, bg=BG_CARD)
        act_bar.pack(fill="x", pady=(8, 2))

        btn_run = ttk.Button(
            act_bar,
            text="Run Detection",
            style="Accent.TButton",
            command=self._on_run_detection
        )
        btn_run.pack(side="left")

        # 2. Main Diagnostic Results Panel
        self.result_card = SectionCard(
            self,
            title="Analysis & Diagnostic Report",
            subtitle="Calculated cycle dependencies, safe sequences, and system state"
        )
        self.result_card.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        self.text_result = tk.Text(
            self.result_card,
            bg=BG_INPUT,
            fg=TEXT_PRIMARY,
            font=self.fonts["mono"],
            wrap="word",
            state="disabled",
            borderwidth=0,
            padx=14,
            pady=12
        )
        
        scroll = ttk.Scrollbar(self.result_card, orient="vertical", command=self.text_result.yview)
        self.text_result.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.text_result.pack(fill="both", expand=True)

        # Style tags
        self.text_result.tag_config("banner_safe", foreground=SUCCESS, font=self.fonts["title"])
        self.text_result.tag_config("banner_deadlock", foreground=DANGER, font=self.fonts["title"])
        self.text_result.tag_config("heading", foreground=CYAN, font=self.fonts["subheading"])
        self.text_result.tag_config("cycle", foreground=DANGER, font=self.fonts["mono_bold"])
        self.text_result.tag_config("safe_seq", foreground=SUCCESS, font=self.fonts["mono_bold"])
        self.text_result.tag_config("warn", foreground=WARNING)
        self.text_result.tag_config("muted", foreground=TEXT_MUTED)
        self.text_result.tag_config("detail", foreground=TEXT_PRIMARY)

    # ── User Actions ──────────────────────────────────────────────────────────

    def _on_run_detection(self):
        algo = self._algo_var.get()
        snap = self.app.manager.get_snapshot()
        result = self.app.detector.detect(snap, algo)
        self.app.last_detection = result
        
        if result.detected:
            self.app.toast(f"Deadlock detected ({algo.upper()})", "danger")
        else:
            self.app.toast(f"System safe ({algo.upper()})", "success")

        self.app.refresh_all()
        self.display_result(result)

    # ── Display Routine ───────────────────────────────────────────────────────

    def display_result(self, result):
        if not result:
            return

        t = self.text_result
        t.configure(state="normal")
        t.delete("1.0", "end")

        # Status Banner
        if result.detected:
            t.insert("end", "DEADLOCK DETECTED\n", "banner_deadlock")
            t.insert("end", f"Algorithm: {result.algorithm}  •  Execution Time: {result.timestamp}\n", "muted")
            t.insert("end", "─" * 72 + "\n\n", "muted")

            # Deadlocked processes
            t.insert("end", f"Affected Processes ({len(result.deadlocked_processes)}):\n", "heading")
            snap = self.app.manager.get_snapshot()
            for pid in result.deadlocked_processes:
                pname = snap.get("processes", {}).get(pid, {}).get("name", pid)
                pri = snap.get("processes", {}).get(pid, {}).get("priority", 1)
                t.insert("end", f"  • {pid:<6} — {pname:<20} Priority={pri}\n", "cycle")

            # Contested resources
            if result.deadlocked_resources:
                t.insert("end", f"\nContested Resources ({len(result.deadlocked_resources)}):\n", "heading")
                for rid in result.deadlocked_resources:
                    rname = snap.get("resources", {}).get(rid, {}).get("name", rid)
                    rtype = snap.get("resources", {}).get(rid, {}).get("type", "mutex")
                    t.insert("end", f"  • {rid:<6} — {rname:<20} Type={rtype}\n", "warn")

            # Highlighted Cycle Paths
            if result.cycle_path:
                t.insert("end", f"\nCircular Wait Dependencies:\n", "heading")
                for idx, cpath in enumerate(result.cycle_path, start=1):
                    t.insert("end", f"  Cycle #{idx}:  {cpath}\n", "cycle")

            # Safe Sequence if Banker's
            if result.safe_sequence:
                t.insert("end", f"\nPartial Safe Sequence:\n", "heading")
                t.insert("end", f"  {' → '.join(result.safe_sequence)}\n", "warn")

        else:
            t.insert("end", "SYSTEM SAFE — NO DEADLOCK\n", "banner_safe")
            t.insert("end", f"Algorithm: {result.algorithm}  •  Execution Time: {result.timestamp}\n", "muted")
            t.insert("end", "─" * 72 + "\n\n", "muted")

            if result.safe_sequence:
                t.insert("end", "Banker's Valid Safe Sequence:\n", "heading")
                t.insert("end", f"  {' → '.join(result.safe_sequence)}\n\n", "safe_seq")

        # Academic Diagnostic Analysis
        t.insert("end", "Analysis & Theoretical Diagnosis:\n", "heading")
        t.insert("end", f"{result.details}\n\n", "detail")

        if result.detected:
            t.insert("end", "Recovery Action:\n", "muted")
            t.insert("end", "Navigate to the Recovery section to resolve deadlocks using process termination, preemption, or rollback.\n", "warn")

        t.configure(state="disabled")

    def update_view(self, snapshot: dict, detection_result=None):
        if detection_result:
            self.display_result(detection_result)
