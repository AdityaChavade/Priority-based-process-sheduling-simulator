"""
Process Management View
───────────────────────
Comprehensive process control center with creation form, interactive process
table/cards, state telemetry, priority badges, and lifecycle actions.
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


class ProcessView(tk.Frame):
    """Process management screen for viewing, creating, and altering process states."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_BASE)
        self.app = app
        self.fonts = get_fonts()

        self._pname_var = tk.StringVar(value="Process-1")
        self._ppri_var = tk.IntVar(value=2)
        self._filter_var = tk.StringVar(value="All")

        self._build_layout()

    def _build_layout(self):
        # Top Container: Add Process Bar
        add_card = SectionCard(
            self,
            title="Create New Process",
            subtitle="Register an operating system task competing for resources",
            badge_text="PID AUTO-ASSIGN",
            badge_color=CYAN
        )
        add_card.pack(fill="x", padx=16, pady=(16, 12))

        form_frame = tk.Frame(add_card, bg=BG_CARD)
        form_frame.pack(fill="x", pady=6)

        # Process Name Input
        tk.Label(
            form_frame,
            text="Process Name:",
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
            font=self.fonts["caption_bold"]
        ).pack(side="left", padx=(0, 6))

        entry_name = ttk.Entry(form_frame, textvariable=self._pname_var, width=18)
        entry_name.pack(side="left", padx=(0, 16))

        # Priority Input
        tk.Label(
            form_frame,
            text="Priority (1=Low … 5=Critical):",
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
            font=self.fonts["caption_bold"]
        ).pack(side="left", padx=(0, 6))

        spin_pri = ttk.Spinbox(form_frame, from_=1, to=5, textvariable=self._ppri_var, width=5)
        spin_pri.pack(side="left", padx=(0, 16))

        # Submit Button
        btn_add = ttk.Button(
            form_frame,
            text="➕ Add Process",
            style="Accent.TButton",
            command=self._on_add_process
        )
        btn_add.pack(side="left")

        # Main Processes Table Section
        self.table_card = SectionCard(
            self,
            title="Active Process Inventory",
            subtitle="Real-time process allocation states and dependencies"
        )
        self.table_card.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Controls Bar: Filter & Action Buttons
        ctrl_bar = tk.Frame(self.table_card, bg=BG_CARD)
        ctrl_bar.pack(fill="x", pady=(0, 8))

        tk.Label(
            ctrl_bar,
            text="Filter State:",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=self.fonts["caption_bold"]
        ).pack(side="left", padx=(0, 6))

        cb_filter = ttk.Combobox(
            ctrl_bar,
            textvariable=self._filter_var,
            values=["All", "running", "waiting", "blocked", "terminated", "rolled_back"],
            width=12,
            state="readonly"
        )
        cb_filter.pack(side="left", padx=(0, 16))
        cb_filter.bind("<<ComboboxSelected>>", lambda e: self.app.refresh_current_view())

        # Action Buttons
        btn_rollback = ttk.Button(
            ctrl_bar,
            text="↩ Rollback Selected",
            style="Warning.TButton",
            command=self._on_rollback_selected
        )
        btn_rollback.pack(side="right", padx=(6, 0))

        btn_term = ttk.Button(
            ctrl_bar,
            text="✕ Terminate Selected",
            style="Danger.TButton",
            command=self._on_terminate_selected
        )
        btn_term.pack(side="right")

        # Treeview Table
        columns = ("pid", "name", "priority", "state", "allocated", "requested", "status")
        self.tree = ttk.Treeview(
            self.table_card,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        self.tree.heading("pid", text="PID", anchor="w")
        self.tree.heading("name", text="NAME", anchor="w")
        self.tree.heading("priority", text="PRIORITY", anchor="center")
        self.tree.heading("state", text="STATE", anchor="center")
        self.tree.heading("allocated", text="ALLOCATED RESOURCES", anchor="w")
        self.tree.heading("requested", text="REQUESTED (WAITING)", anchor="w")
        self.tree.heading("status", text="HEALTH STATUS", anchor="center")

        self.tree.column("pid", width=70, minwidth=60)
        self.tree.column("name", width=140, minwidth=100)
        self.tree.column("priority", width=80, anchor="center")
        self.tree.column("state", width=100, anchor="center")
        self.tree.column("allocated", width=220, minwidth=140)
        self.tree.column("requested", width=220, minwidth=140)
        self.tree.column("status", width=120, anchor="center")

        scroll = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Empty State Label
        self.lbl_empty = tk.Label(
            self.tree,
            text="◈ NO PROCESSES CONFIGURED ◈\nUse the form above to spawn a process or load a scenario.",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=self.fonts["body"],
            justify="center"
        )

    # ── User Actions ──────────────────────────────────────────────────────────

    def _on_add_process(self):
        name = self._pname_var.get().strip()
        pri = self._ppri_var.get()
        pid = f"P{self.app.pid_counter[0]}"
        self.app.pid_counter[0] += 1
        
        if not name:
            name = f"Process-{self.app.pid_counter[0] - 1}"

        self.app.manager.add_process(pid, name, pri)
        self.app.toast(f"Process {name} ({pid}) created with priority {pri}", "success")
        self._pname_var.set(f"Process-{self.app.pid_counter[0]}")
        self.app.refresh_all()

    def _get_selected_pid(self):
        selected = self.tree.selection()
        if not selected:
            self.app.toast("Please select a process row from the table first.", "warn")
            return None
        return self.tree.item(selected[0])["values"][0]

    def _on_terminate_selected(self):
        pid = self._get_selected_pid()
        if not pid:
            return
        
        if self.app.confirm_action("Terminate Process", f"Are you sure you want to terminate process {pid}?", is_danger=True):
            ok = self.app.manager.terminate_process(pid, reason="manual_user_action")
            if ok:
                self.app.toast(f"Process {pid} terminated and resources released", "danger")
            self.app.refresh_all()

    def _on_rollback_selected(self):
        pid = self._get_selected_pid()
        if not pid:
            return
        
        if self.app.confirm_action("Rollback Process", f"Reset process {pid} to safe checkpoint and release held resources?"):
            ok = self.app.manager.rollback_process(pid)
            if ok:
                self.app.toast(f"Process {pid} rolled back to initial state", "warn")
            self.app.refresh_all()

    # ── Update Routine ────────────────────────────────────────────────────────

    def update_view(self, snapshot: dict, detection_result=None):
        processes = snapshot.get("processes", {})
        filter_mode = self._filter_var.get()

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        deadlocked_pids = set()
        if detection_result and detection_result.detected:
            deadlocked_pids = set(detection_result.deadlocked_processes)

        visible_count = 0
        for pid, p in processes.items():
            state = p.get("state", "running")
            if filter_mode != "All" and state != filter_mode:
                continue

            visible_count += 1
            allocated_str = ", ".join(f"{r} ({c}×)" for r, c in p.get("allocated", {}).items()) or "None (0 held)"
            requested_str = ", ".join(f"{r} ({c}×)" for r, c in p.get("requested", {}).items()) or "None (0 waiting)"
            
            is_deadlocked = pid in deadlocked_pids
            status_text = "⚠ DEADLOCKED" if is_deadlocked else ("WAITING" if state == "waiting" else "HEALTHY")

            self.tree.insert(
                "", "end",
                values=(
                    pid,
                    p.get("name", ""),
                    f"P{p.get('priority', 1)}",
                    state.upper(),
                    allocated_str,
                    requested_str,
                    status_text
                )
            )

        # Toggle Empty State
        if visible_count == 0:
            self.lbl_empty.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.lbl_empty.place_forget()
