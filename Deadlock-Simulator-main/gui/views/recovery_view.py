"""
Deadlock Recovery Center
────────────────────────
Structured academic workflow:
1. Detected Deadlock State
2. Affected Processes & Contested Resources
3. Available Recovery Actions
4. Execute Recovery (with confirmation safety check)
5. System State After Recovery & Execution Audit Log
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


class RecoveryView(tk.Frame):
    """Deadlock recovery control center with structured step-down workflow."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_BASE)
        self.app = app
        self.fonts = get_fonts()

        self._build_layout()

    def _build_layout(self):
        # Step 1 & 2: Detected Deadlock & Affected Processes Card
        self.status_card = SectionCard(
            self,
            title="Step 1: Deadlock State Assessment & Affected Processes",
            subtitle="Identifies current circular waits and contested resources"
        )
        self.status_card.pack(fill="x", padx=16, pady=(12, 8))

        self.lbl_deadlock_info = tk.Label(
            self.status_card,
            text="System is currently in a SAFE state. Recovery strategies are enabled once a deadlock is detected.",
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
            font=self.fonts["body"]
        )
        self.lbl_deadlock_info.pack(anchor="w", pady=2)

        # Step 3 & 4: Available Recovery Actions & Execution Card
        actions_card = SectionCard(
            self,
            title="Step 2: Select & Execute Recovery Action",
            subtitle="Dispatch theoretical OS resolution mechanisms based on cost profile"
        )
        actions_card.pack(fill="x", padx=16, pady=(0, 8))

        strat_grid = tk.Frame(actions_card, bg=BG_CARD)
        strat_grid.pack(fill="x", pady=2)
        strat_grid.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="strats")

        # Action 1: Kill Victim
        c1 = tk.Frame(strat_grid, bg=BG_INPUT, highlightbackground=BORDER_DEFAULT, highlightthickness=1, padx=8, pady=8)
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        tk.Label(c1, text="Kill Victim", bg=BG_INPUT, fg=DANGER, font=self.fonts["subheading"]).pack(anchor="w")
        tk.Label(c1, text="Terminates lowest-priority process.\nCost: Medium", bg=BG_INPUT, fg=TEXT_MUTED, font=self.fonts["caption"], justify="left").pack(anchor="w", pady=(2, 6))
        ttk.Button(c1, text="Kill Victim", style="Danger.TButton", command=lambda: self._execute_recovery("terminate")).pack(fill="x")

        # Action 2: Preempt Resource
        c2 = tk.Frame(strat_grid, bg=BG_INPUT, highlightbackground=BORDER_DEFAULT, highlightthickness=1, padx=8, pady=8)
        c2.grid(row=0, column=1, sticky="nsew", padx=2)
        tk.Label(c2, text="Preempt Resource", bg=BG_INPUT, fg=WARNING, font=self.fonts["subheading"]).pack(anchor="w")
        tk.Label(c2, text="Steals resource, gives to waiter.\nCost: Low-Medium", bg=BG_INPUT, fg=TEXT_MUTED, font=self.fonts["caption"], justify="left").pack(anchor="w", pady=(2, 6))
        ttk.Button(c2, text="Preempt Resource", style="Warning.TButton", command=lambda: self._execute_recovery("preempt")).pack(fill="x")

        # Action 3: Rollback
        c3 = tk.Frame(strat_grid, bg=BG_INPUT, highlightbackground=BORDER_DEFAULT, highlightthickness=1, padx=8, pady=8)
        c3.grid(row=0, column=2, sticky="nsew", padx=2)
        tk.Label(c3, text="Rollback Process", bg=BG_INPUT, fg=SUCCESS, font=self.fonts["subheading"]).pack(anchor="w")
        tk.Label(c3, text="Resets victim, releases resources.\nCost: Low", bg=BG_INPUT, fg=TEXT_MUTED, font=self.fonts["caption"], justify="left").pack(anchor="w", pady=(2, 6))
        ttk.Button(c3, text="Rollback Process", style="Success.TButton", command=lambda: self._execute_recovery("rollback")).pack(fill="x")

        # Action 4: Kill All
        c4 = tk.Frame(strat_grid, bg=BG_INPUT, highlightbackground=BORDER_DEFAULT, highlightthickness=1, padx=8, pady=8)
        c4.grid(row=0, column=3, sticky="nsew", padx=(4, 0))
        tk.Label(c4, text="Kill All Deadlocked", bg=BG_INPUT, fg=DANGER, font=self.fonts["subheading"]).pack(anchor="w")
        tk.Label(c4, text="Terminates all deadlocked tasks.\nCost: High", bg=BG_INPUT, fg=TEXT_MUTED, font=self.fonts["caption"], justify="left").pack(anchor="w", pady=(2, 6))
        ttk.Button(c4, text="Kill All", style="Danger.TButton", command=lambda: self._execute_recovery("kill_all")).pack(fill="x")

        # Step 5: System State After Recovery & Audit Log Card
        self.log_card = SectionCard(
            self,
            title="Step 3: Post-Recovery State & Execution Audit Log",
            subtitle="Step-by-step trace of actions, resources released, and final state verification"
        )
        self.log_card.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        self.text_log = tk.Text(
            self.log_card,
            bg=BG_INPUT,
            fg=TEXT_PRIMARY,
            font=self.fonts["mono"],
            wrap="word",
            state="disabled",
            borderwidth=0,
            padx=14,
            pady=10
        )
        
        scroll = ttk.Scrollbar(self.log_card, orient="vertical", command=self.text_log.yview)
        self.text_log.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.text_log.pack(fill="both", expand=True)

        self.text_log.tag_config("heading", foreground=CYAN, font=self.fonts["subheading"])
        self.text_log.tag_config("step", foreground=TEXT_PRIMARY)
        self.text_log.tag_config("success", foreground=SUCCESS)
        self.text_log.tag_config("error", foreground=DANGER)
        self.text_log.tag_config("cost", foreground=WARNING, font=self.fonts["mono_bold"])
        self.text_log.tag_config("muted", foreground=TEXT_MUTED)

    # ── User Actions ──────────────────────────────────────────────────────────

    def _execute_recovery(self, strategy: str):
        if not self.app.last_detection or not self.app.last_detection.detected:
            snap = self.app.manager.get_snapshot()
            self.app.last_detection = self.app.detector.detect(snap, "rag")

        if not self.app.last_detection.detected:
            self.app.toast("No active deadlock detected — recovery is not needed.", "info")
            return

        strat_names = {
            "terminate": "Kill Lowest-Priority Victim",
            "preempt": "Resource Preemption",
            "rollback": "Process Rollback",
            "kill_all": "Kill All Deadlocked Processes"
        }
        name = strat_names.get(strategy, strategy)
        is_danger = strategy in ("terminate", "kill_all")

        if self.app.confirm_action("Confirm Recovery Action", f"Execute {name} on deadlocked processes?", is_danger=is_danger):
            action = self.app.recovery.recover(self.app.manager, self.app.last_detection, strategy)
            self._display_recovery_action(action)
            self.app.last_detection = None
            self.app.toast(f"Recovery executed: {action.strategy}", "success" if action.success else "warn")
            self.app.refresh_all()

    # ── Display Routine ───────────────────────────────────────────────────────

    def _display_recovery_action(self, action):
        t = self.text_log
        t.configure(state="normal")
        t.delete("1.0", "end")

        t.insert("end", f"Recovery Strategy Executed: {action.strategy}\n", "heading")
        t.insert("end", f"Timestamp: {action.timestamp}  •  Status: {'✓ SUCCESSFUL' if action.success else '✕ FAILED'}\n", "muted")
        t.insert("end", "─" * 70 + "\n\n", "muted")

        for step in action.steps:
            if "✗" in step or "error" in step.lower():
                t.insert("end", f"  {step}\n", "error")
            elif "✓" in step or "success" in step.lower() or "terminated" in step.lower():
                t.insert("end", f"  {step}\n", "success")
            else:
                t.insert("end", f"  {step}\n", "step")

        t.insert("end", f"\nTheoretical OS Cost Assessment:\n", "heading")
        t.insert("end", f"  {action.cost_estimate}\n\n", "cost")

        # Post-recovery state check
        snap = self.app.manager.get_snapshot()
        res_after = self.app.detector.detect(snap, "rag")
        t.insert("end", f"Post-Recovery Verification: {'✓ SYSTEM DEADLOCK-FREE' if not res_after.detected else '⚠ REMAINING DEADLOCK PRESENT'}\n", "success" if not res_after.detected else "error")

        t.configure(state="disabled")

    def update_view(self, snapshot: dict, detection_result=None):
        if detection_result and detection_result.detected:
            pids = ", ".join(detection_result.deadlocked_processes)
            rids = ", ".join(detection_result.deadlocked_resources) or "None"
            self.lbl_deadlock_info.configure(
                text=f"Deadlock Detected: {len(detection_result.deadlocked_processes)} process(es) in circular wait.\nAffected Processes: [{pids}]  •  Contested Resources: [{rids}]",
                fg=DANGER
            )
        else:
            self.lbl_deadlock_info.configure(
                text="System is currently in a SAFE state. Resource claims and locks are balanced.",
                fg=TEXT_SECONDARY
            )
