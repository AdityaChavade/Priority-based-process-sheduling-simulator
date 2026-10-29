"""
Allocation Workbench View
─────────────────────────
Interactive resource request and release console with live Allocation
and Request (Need) matrices.
"""

import tkinter as tk
from tkinter import ttk
from gui.theme import (
    BG_BASE, BG_PANEL, BG_CARD, BG_CARD_ALT, BG_INPUT,
    BORDER_DEFAULT, BORDER_FOCUS, CYAN, PURPLE,
    SUCCESS, WARNING, DANGER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    get_fonts
)
from gui.components.cards import SectionCard


class AllocationView(tk.Frame):
    """Resource allocation workbench and matrix inspection view."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_BASE)
        self.app = app
        self.fonts = get_fonts()

        self._pid_var = tk.StringVar()
        self._rid_var = tk.StringVar()
        self._count_var = tk.IntVar(value=1)

        self._build_layout()

    def _build_layout(self):
        # 1. Top Section: Workbench Controls
        bench_card = SectionCard(
            self,
            title="Resource Allocation & Acquisition Console",
            subtitle="Perform synchronized OS request, grant, and release operations",
            badge_text="MUTUAL EXCLUSION ENGINE",
            badge_color=CYAN
        )
        bench_card.pack(fill="x", padx=16, pady=(16, 12))

        form = tk.Frame(bench_card, bg=BG_CARD)
        form.pack(fill="x", pady=6)

        # Process Selector
        tk.Label(
            form, text="Process:", bg=BG_CARD, fg=TEXT_SECONDARY, font=self.fonts["caption_bold"]
        ).pack(side="left", padx=(0, 6))

        self.cb_pid = ttk.Combobox(form, textvariable=self._pid_var, width=18, state="readonly")
        self.cb_pid.pack(side="left", padx=(0, 16))

        # Resource Selector
        tk.Label(
            form, text="Resource:", bg=BG_CARD, fg=TEXT_SECONDARY, font=self.fonts["caption_bold"]
        ).pack(side="left", padx=(0, 6))

        self.cb_rid = ttk.Combobox(form, textvariable=self._rid_var, width=18, state="readonly")
        self.cb_rid.pack(side="left", padx=(0, 16))

        # Count
        tk.Label(
            form, text="Units:", bg=BG_CARD, fg=TEXT_SECONDARY, font=self.fonts["caption_bold"]
        ).pack(side="left", padx=(0, 6))

        spin_count = ttk.Spinbox(form, from_=1, to=10, textvariable=self._count_var, width=4)
        spin_count.pack(side="left", padx=(0, 16))

        # Buttons
        btn_req = ttk.Button(
            form,
            text="🔒 Request / Lock Resource",
            style="Accent.TButton",
            command=self._on_request
        )
        btn_req.pack(side="left", padx=(0, 8))

        btn_rel = ttk.Button(
            form,
            text="🔓 Release / Unlock Resource",
            style="Ghost.TButton",
            command=self._on_release
        )
        btn_rel.pack(side="left")

        # 2. Main Matrix Deck (Split Paned: Allocation Matrix + Request Matrix)
        paned = tk.PanedWindow(self, orient="horizontal", bg=BG_BASE, sashwidth=6, sashrelief="flat")
        paned.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Left Matrix: Current Allocations (Holdings)
        left_card = SectionCard(
            paned,
            title="Allocation Matrix [A]",
            subtitle="Units currently held by each process"
        )
        paned.add(left_card, minsize=400, stretch="always")

        self.alloc_tree = ttk.Treeview(
            left_card,
            columns=("process", "resource", "held", "available", "state"),
            show="headings",
            selectmode="browse"
        )
        self.alloc_tree.heading("process", text="PROCESS", anchor="w")
        self.alloc_tree.heading("resource", text="RESOURCE", anchor="w")
        self.alloc_tree.heading("held", text="HELD UNITS", anchor="center")
        self.alloc_tree.heading("available", text="POOL AVAILABLE", anchor="center")
        self.alloc_tree.heading("state", text="PROCESS STATE", anchor="center")

        self.alloc_tree.column("process", width=120)
        self.alloc_tree.column("resource", width=120)
        self.alloc_tree.column("held", width=80, anchor="center")
        self.alloc_tree.column("available", width=100, anchor="center")
        self.alloc_tree.column("state", width=100, anchor="center")

        scroll_left = ttk.Scrollbar(left_card, orient="vertical", command=self.alloc_tree.yview)
        self.alloc_tree.configure(yscrollcommand=scroll_left.set)
        scroll_left.pack(side="right", fill="y")
        self.alloc_tree.pack(fill="both", expand=True)

        # Right Matrix: Pending Requests (Needs)
        right_card = SectionCard(
            paned,
            title="Request / Need Matrix [R]",
            subtitle="Outstanding blocked requests waiting for availability"
        )
        paned.add(right_card, minsize=400, stretch="always")

        self.req_tree = ttk.Treeview(
            right_card,
            columns=("process", "resource", "requested", "free_units", "queue_status"),
            show="headings",
            selectmode="browse"
        )
        self.req_tree.heading("process", text="PROCESS", anchor="w")
        self.req_tree.heading("resource", text="RESOURCE", anchor="w")
        self.req_tree.heading("requested", text="REQUESTED", anchor="center")
        self.req_tree.heading("free_units", text="FREE IN POOL", anchor="center")
        self.req_tree.heading("queue_status", text="QUEUE STATUS", anchor="center")

        self.req_tree.column("process", width=120)
        self.req_tree.column("resource", width=120)
        self.req_tree.column("requested", width=80, anchor="center")
        self.req_tree.column("free_units", width=100, anchor="center")
        self.req_tree.column("queue_status", width=110, anchor="center")

        scroll_right = ttk.Scrollbar(right_card, orient="vertical", command=self.req_tree.yview)
        self.req_tree.configure(yscrollcommand=scroll_right.set)
        scroll_right.pack(side="right", fill="y")
        self.req_tree.pack(fill="both", expand=True)

    # ── User Actions ──────────────────────────────────────────────────────────

    def _parse_pid(self) -> str:
        val = self._pid_var.get()
        return val.split()[0] if val else ""

    def _parse_rid(self) -> str:
        val = self._rid_var.get()
        return val.split()[0] if val else ""

    def _on_request(self):
        pid = self._parse_pid()
        rid = self._parse_rid()
        count = max(1, self._count_var.get())

        if not pid or not rid:
            self.app.toast("Select both a process and resource first.", "warn")
            return

        ok = self.app.manager.request_resource(pid, rid, count)
        if ok:
            self.app.toast(f"Granted {count}× {rid} to {pid}", "success")
        else:
            self.app.toast(f"{pid} blocked waiting for {count}× {rid} (Insufficient free units)", "warn")
        self.app.refresh_all()

    def _on_release(self):
        pid = self._parse_pid()
        rid = self._parse_rid()
        count = max(1, self._count_var.get())

        if not pid or not rid:
            self.app.toast("Select both a process and resource first.", "warn")
            return

        ok = self.app.manager.release_resource(pid, rid, count)
        if ok:
            self.app.toast(f"{pid} released {count}× {rid}", "info")
        else:
            self.app.toast(f"{pid} does not hold {rid} to release.", "error")
        self.app.refresh_all()

    # ── Update Routine ────────────────────────────────────────────────────────

    def update_view(self, snapshot: dict, detection_result=None):
        processes = snapshot.get("processes", {})
        resources = snapshot.get("resources", {})

        # Update combobox choices
        p_choices = [f"{pid} — {p.get('name')}" for pid, p in processes.items()]
        r_choices = [f"{rid} — {r.get('name')} ({r.get('available')}/{r.get('total')} free)" for rid, r in resources.items()]

        self.cb_pid["values"] = p_choices
        self.cb_rid["values"] = r_choices

        if p_choices and not self._pid_var.get():
            self._pid_var.set(p_choices[0])
        if r_choices and not self._rid_var.get():
            self._rid_var.set(r_choices[0])

        # 1. Populate Allocation Matrix Tree
        for item in self.alloc_tree.get_children():
            self.alloc_tree.delete(item)

        for pid, p in processes.items():
            for rid, count in p.get("allocated", {}).items():
                r = resources.get(rid, {})
                self.alloc_tree.insert(
                    "", "end",
                    values=(
                        f"{pid} ({p.get('name')})",
                        f"{rid} ({r.get('name', rid)})",
                        f"{count} unit(s)",
                        f"{r.get('available', 0)} free",
                        p.get("state", "running").upper()
                    )
                )

        # 2. Populate Request Matrix Tree
        for item in self.req_tree.get_children():
            self.req_tree.delete(item)

        for pid, p in processes.items():
            for rid, count in p.get("requested", {}).items():
                r = resources.get(rid, {})
                self.req_tree.insert(
                    "", "end",
                    values=(
                        f"{pid} ({p.get('name')})",
                        f"{rid} ({r.get('name', rid)})",
                        f"{count} unit(s)",
                        f"{r.get('available', 0)} free",
                        "BLOCKED (WAITING)"
                    )
                )
