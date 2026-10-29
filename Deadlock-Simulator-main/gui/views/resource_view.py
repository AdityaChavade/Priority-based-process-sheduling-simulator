"""
Resource Management View
────────────────────────
Resource inventory deck, instance utilization bars, allocation tracking,
and resource registration workspace.
"""

import tkinter as tk
from tkinter import ttk
from gui.theme import (
    BG_BASE, BG_PANEL, BG_CARD, BG_CARD_ALT, BG_INPUT,
    BORDER_DEFAULT, BORDER_FOCUS, CYAN, PURPLE,
    SUCCESS, WARNING, DANGER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    get_fonts
)
from gui.components.cards import SectionCard, UtilizationBar


class ResourceView(tk.Frame):
    """Resource inventory and instance provisioning view."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_BASE)
        self.app = app
        self.fonts = get_fonts()

        self._rname_var = tk.StringVar(value="Mutex-1")
        self._rinst_var = tk.IntVar(value=1)
        self._rtype_var = tk.StringVar(value="mutex")

        self._build_layout()

    def _build_layout(self):
        # 1. Top Section: Add Resource Form
        add_card = SectionCard(
            self,
            title="Provision New Resource",
            subtitle="Define system locks, semaphores, file descriptors, or device interfaces",
            badge_text="MUTEX / SEMAPHORE",
            badge_color=PURPLE
        )
        add_card.pack(fill="x", padx=16, pady=(16, 12))

        form = tk.Frame(add_card, bg=BG_CARD)
        form.pack(fill="x", pady=6)

        # Name
        tk.Label(
            form, text="Resource Name:", bg=BG_CARD, fg=TEXT_SECONDARY, font=self.fonts["caption_bold"]
        ).pack(side="left", padx=(0, 6))

        entry_name = ttk.Entry(form, textvariable=self._rname_var, width=16)
        entry_name.pack(side="left", padx=(0, 16))

        # Instances
        tk.Label(
            form, text="Instances (1-20):", bg=BG_CARD, fg=TEXT_SECONDARY, font=self.fonts["caption_bold"]
        ).pack(side="left", padx=(0, 6))

        spin_inst = ttk.Spinbox(form, from_=1, to=20, textvariable=self._rinst_var, width=5)
        spin_inst.pack(side="left", padx=(0, 16))

        # Type
        tk.Label(
            form, text="Type:", bg=BG_CARD, fg=TEXT_SECONDARY, font=self.fonts["caption_bold"]
        ).pack(side="left", padx=(0, 6))

        cb_type = ttk.Combobox(
            form,
            textvariable=self._rtype_var,
            values=["mutex", "semaphore", "file", "device"],
            width=12,
            state="readonly"
        )
        cb_type.pack(side="left", padx=(0, 16))

        # Submit
        btn_add = ttk.Button(
            form,
            text="➕ Add Resource",
            style="Accent.TButton",
            command=self._on_add_resource
        )
        btn_add.pack(side="left")

        # 2. Main Resource Inventory Table
        self.table_card = SectionCard(
            self,
            title="Active Resource Inventory",
            subtitle="Instance capacities, active holders, and pending request queues"
        )
        self.table_card.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Table Control bar
        ctrl_bar = tk.Frame(self.table_card, bg=BG_CARD)
        ctrl_bar.pack(fill="x", pady=(0, 8))

        btn_remove = ttk.Button(
            ctrl_bar,
            text="🗑 Remove Selected Resource",
            style="Danger.TButton",
            command=self._on_remove_selected
        )
        btn_remove.pack(side="right")

        # Treeview Table
        columns = ("rid", "name", "type", "capacity", "available", "allocated", "holders", "waiters")
        self.tree = ttk.Treeview(
            self.table_card,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.tree.heading("rid", text="RID", anchor="w")
        self.tree.heading("name", text="NAME", anchor="w")
        self.tree.heading("type", text="TYPE", anchor="center")
        self.tree.heading("capacity", text="TOTAL UNITS", anchor="center")
        self.tree.heading("available", text="AVAILABLE", anchor="center")
        self.tree.heading("allocated", text="ALLOCATED", anchor="center")
        self.tree.heading("holders", text="HOLDING PROCESSES", anchor="w")
        self.tree.heading("waiters", text="WAITING PROCESSES", anchor="w")

        self.tree.column("rid", width=70, minwidth=60)
        self.tree.column("name", width=140, minwidth=100)
        self.tree.column("type", width=100, anchor="center")
        self.tree.column("capacity", width=90, anchor="center")
        self.tree.column("available", width=90, anchor="center")
        self.tree.column("allocated", width=90, anchor="center")
        self.tree.column("holders", width=220, minwidth=140)
        self.tree.column("waiters", width=220, minwidth=140)

        scroll = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Empty state label
        self.lbl_empty = tk.Label(
            self.tree,
            text="◈ NO SYSTEM RESOURCES REGISTERED ◈\nProvision resources above or load an architectural scenario.",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=self.fonts["body"],
            justify="center"
        )

    # ── User Actions ──────────────────────────────────────────────────────────

    def _on_add_resource(self):
        name = self._rname_var.get().strip()
        inst = max(1, self._rinst_var.get())
        rtype = self._rtype_var.get()
        rid = f"R{self.app.rid_counter[0]}"
        self.app.rid_counter[0] += 1

        if not name:
            name = f"Resource-{self.app.rid_counter[0] - 1}"

        self.app.manager.add_resource(rid, name, inst, rtype)
        self.app.toast(f"Resource {name} ({rid}) provisioned with {inst} instance(s)", "success")
        self._rname_var.set(f"Mutex-{self.app.rid_counter[0]}")
        self.app.refresh_all()

    def _on_remove_selected(self):
        selected = self.tree.selection()
        if not selected:
            self.app.toast("Select a resource to remove.", "warn")
            return

        rid = self.tree.item(selected[0])["values"][0]
        if self.app.confirm_action("Remove Resource", f"Remove {rid}? (Only unallocated resources can be removed)", is_danger=True):
            ok = self.app.manager.remove_resource(rid)
            if ok:
                self.app.toast(f"Resource {rid} removed successfully", "info")
            else:
                self.app.toast(f"Cannot remove {rid} while instances are held by active processes.", "error")
            self.app.refresh_all()

    # ── Update Routine ────────────────────────────────────────────────────────

    def update_view(self, snapshot: dict, detection_result=None):
        resources = snapshot.get("resources", {})
        processes = snapshot.get("processes", {})

        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Map holders and waiters
        holders_map = {rid: [] for rid in resources}
        waiters_map = {rid: [] for rid in resources}

        for pid, p in processes.items():
            for rid, count in p.get("allocated", {}).items():
                if rid in holders_map:
                    holders_map[rid].append(f"{pid}({count}×)")
            for rid, count in p.get("requested", {}).items():
                if rid in waiters_map:
                    waiters_map[rid].append(f"{pid}({count}×)")

        count = 0
        for rid, r in resources.items():
            count += 1
            h_str = ", ".join(holders_map[rid]) or "None"
            w_str = ", ".join(waiters_map[rid]) or "None"
            
            self.tree.insert(
                "", "end",
                values=(
                    rid,
                    r.get("name", ""),
                    r.get("type", "mutex").upper(),
                    r.get("total", 1),
                    r.get("available", 0),
                    r.get("allocated", 0),
                    h_str,
                    w_str
                )
            )

        if count == 0:
            self.lbl_empty.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.lbl_empty.place_forget()
