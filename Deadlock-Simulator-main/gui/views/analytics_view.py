"""
Analytics & System Telemetry View
─────────────────────────────────
Calculates and displays real OS metrics, resource utilization rates,
process state distributions, and bottleneck rankings using genuine application data.
"""

import tkinter as tk
from tkinter import ttk
from gui.theme import (
    BG_BASE, BG_PANEL, BG_CARD, BG_CARD_ALT, BG_INPUT,
    BORDER_DEFAULT, BORDER_FOCUS, CYAN, PURPLE,
    SUCCESS, WARNING, DANGER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    get_fonts
)
from gui.components.cards import SectionCard, StatCard, UtilizationBar


class AnalyticsView(tk.Frame):
    """Telemetry dashboard analyzing live system capacity and concurrency bottlenecks."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_BASE)
        self.app = app
        self.fonts = get_fonts()

        self._build_layout()

    def _build_layout(self):
        # 1. Top Metrics Summary
        metrics_deck = tk.Frame(self, bg=BG_BASE)
        metrics_deck.pack(fill="x", padx=16, pady=(16, 12))
        for i in range(4):
            metrics_deck.grid_columnconfigure(i, weight=1, uniform="analytics_stats")

        self.card_util = StatCard(metrics_deck, title="Global Utilization", initial_value="0.0%", icon="📊", accent_color=CYAN, subtext="Allocated / Capacity")
        self.card_util.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.card_contention = StatCard(metrics_deck, title="Contention Index", initial_value="0", icon="⚡", accent_color=WARNING, subtext="Blocked request count")
        self.card_contention.grid(row=0, column=1, sticky="nsew", padx=(0, 8))

        self.card_events = StatCard(metrics_deck, title="Kernel Audit Events", initial_value="0", icon="📋", accent_color=PURPLE, subtext="Total events logged")
        self.card_events.grid(row=0, column=2, sticky="nsew", padx=(0, 8))

        self.card_ratio = StatCard(metrics_deck, title="Safety State", initial_value="SAFE", icon="🛡", accent_color=SUCCESS, subtext="Realtime validation")
        self.card_ratio.grid(row=0, column=3, sticky="nsew")

        # 2. Middle Section: Split Analytics Panes
        paned = tk.PanedWindow(self, orient="horizontal", bg=BG_BASE, sashwidth=6, sashrelief="flat")
        paned.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Left: Resource Utilization & Bottleneck Breakdown
        left_card = SectionCard(
            paned,
            title="Resource Utilization & Bottleneck Analysis",
            subtitle="Calculated utilization rate and pending queues per resource"
        )
        paned.add(left_card, minsize=420, stretch="always")

        self.tree_res_analytics = ttk.Treeview(
            left_card,
            columns=("rid", "name", "type", "utilization", "capacity", "wait_queue"),
            show="headings",
            selectmode="browse"
        )
        self.tree_res_analytics.heading("rid", text="RID", anchor="w")
        self.tree_res_analytics.heading("name", text="RESOURCE", anchor="w")
        self.tree_res_analytics.heading("type", text="TYPE", anchor="center")
        self.tree_res_analytics.heading("utilization", text="UTILIZATION", anchor="center")
        self.tree_res_analytics.heading("capacity", text="HELD / TOTAL", anchor="center")
        self.tree_res_analytics.heading("wait_queue", text="PENDING QUEUE", anchor="center")

        self.tree_res_analytics.column("rid", width=60)
        self.tree_res_analytics.column("name", width=120)
        self.tree_res_analytics.column("type", width=80, anchor="center")
        self.tree_res_analytics.column("utilization", width=100, anchor="center")
        self.tree_res_analytics.column("capacity", width=100, anchor="center")
        self.tree_res_analytics.column("wait_queue", width=110, anchor="center")

        scroll_left = ttk.Scrollbar(left_card, orient="vertical", command=self.tree_res_analytics.yview)
        self.tree_res_analytics.configure(yscrollcommand=scroll_left.set)
        scroll_left.pack(side="right", fill="y")
        self.tree_res_analytics.pack(fill="both", expand=True)

        # Right: Process State Distribution & Event Telemetry
        right_card = SectionCard(
            paned,
            title="Process State Distribution & Telemetry",
            subtitle="Kernel process lifecycle counters and event metrics"
        )
        paned.add(right_card, minsize=400, stretch="always")

        self.text_proc_telemetry = tk.Text(
            right_card,
            bg=BG_INPUT,
            fg=TEXT_PRIMARY,
            font=self.fonts["mono"],
            wrap="word",
            state="disabled",
            borderwidth=0,
            padx=14,
            pady=12
        )
        self.text_proc_telemetry.pack(fill="both", expand=True)

        self.text_proc_telemetry.tag_config("heading", foreground=CYAN, font=self.fonts["subheading"])
        self.text_proc_telemetry.tag_config("val", foreground=SUCCESS, font=self.fonts["mono_bold"])
        self.text_proc_telemetry.tag_config("warn_val", foreground=WARNING, font=self.fonts["mono_bold"])
        self.text_proc_telemetry.tag_config("danger_val", foreground=DANGER, font=self.fonts["mono_bold"])
        self.text_proc_telemetry.tag_config("muted", foreground=TEXT_MUTED)

    # ── Update Routine ────────────────────────────────────────────────────────

    def update_view(self, snapshot: dict, detection_result=None):
        processes = snapshot.get("processes", {})
        resources = snapshot.get("resources", {})
        events = snapshot.get("events", [])

        total_cap = sum(r.get("total", 0) for r in resources.values())
        total_alloc = sum(r.get("allocated", 0) for r in resources.values())
        global_util_pct = (total_alloc / total_cap * 100) if total_cap > 0 else 0.0

        # Contention: count total blocked units requested
        total_blocked_requests = 0
        waiters_per_res = {rid: 0 for rid in resources}
        for pid, p in processes.items():
            for rid, count in p.get("requested", {}).items():
                total_blocked_requests += count
                if rid in waiters_per_res:
                    waiters_per_res[rid] += count

        # Update Stat Cards
        self.card_util.update_value(f"{global_util_pct:.1f}%", f"{total_alloc}/{total_cap} units in use")
        self.card_contention.update_value(
            str(total_blocked_requests),
            f"{total_blocked_requests} blocked units" if total_blocked_requests > 0 else "Zero contention",
            accent_color=DANGER if total_blocked_requests > 0 else SUCCESS
        )
        self.card_events.update_value(str(len(events)), "Chronological records")

        is_deadlock = detection_result and detection_result.detected
        if is_deadlock:
            self.card_ratio.update_value("DEADLOCK", f"{len(detection_result.deadlocked_processes)} processes stuck", accent_color=DANGER)
        else:
            self.card_ratio.update_value("SAFE", "No circular dependencies", accent_color=SUCCESS)

        # Update Resource Table
        for item in self.tree_res_analytics.get_children():
            self.tree_res_analytics.delete(item)

        for rid, r in resources.items():
            cap = r.get("total", 1)
            alloc = r.get("allocated", 0)
            u_pct = (alloc / cap * 100) if cap > 0 else 0.0
            wq = waiters_per_res.get(rid, 0)

            self.tree_res_analytics.insert(
                "", "end",
                values=(
                    rid,
                    r.get("name", ""),
                    r.get("type", "mutex").upper(),
                    f"{u_pct:.1f}%",
                    f"{alloc} / {cap}",
                    f"{wq} units waiting" if wq > 0 else "0 (Free)"
                )
            )

        # Update Process Telemetry Text
        state_counts = {"running": 0, "waiting": 0, "blocked": 0, "terminated": 0, "rolled_back": 0}
        for pid, p in processes.items():
            st = p.get("state", "running")
            if st in state_counts:
                state_counts[st] += 1

        t = self.text_proc_telemetry
        t.configure(state="normal")
        t.delete("1.0", "end")

        t.insert("end", "▶ PROCESS STATE DISTRIBUTION:\n", "heading")
        t.insert("end", f"   • Running:      {state_counts['running']:>3} process(es)\n", "val")
        t.insert("end", f"   • Waiting:      {state_counts['waiting']:>3} process(es)\n", "warn_val" if state_counts['waiting'] > 0 else "muted")
        t.insert("end", f"   • Blocked:      {state_counts['blocked']:>3} process(es)\n", "danger_val" if state_counts['blocked'] > 0 else "muted")
        t.insert("end", f"   • Terminated:   {state_counts['terminated']:>3} process(es)\n", "muted")
        t.insert("end", f"   • Rolled Back:  {state_counts['rolled_back']:>3} process(es)\n\n", "muted")

        t.insert("end", "▶ SYSTEM TELEMETRY SUMMARY:\n", "heading")
        t.insert("end", f"   • Total Active Tasks:       {len(processes)}\n")
        t.insert("end", f"   • Total System Resources:   {len(resources)}\n")
        t.insert("end", f"   • Global Utilization:       {global_util_pct:.1f}%\n")
        t.insert("end", f"   • Outstanding Requests:     {total_blocked_requests}\n")
        t.insert("end", f"   • Total Logged Events:      {len(events)}\n\n")

        # Bottleneck note
        if total_blocked_requests > 0:
            top_bottleneck = max(waiters_per_res.items(), key=lambda x: x[1])
            rname = resources.get(top_bottleneck[0], {}).get("name", top_bottleneck[0])
            t.insert("end", f"⚡ Primary Bottleneck: [{top_bottleneck[0]} — {rname}] ({top_bottleneck[1]} units waiting)\n", "warn_val")
        else:
            t.insert("end", "✓ No resource contention bottlenecks detected.\n", "val")

        t.configure(state="disabled")
