"""
Event Log & System Audit Stream View
────────────────────────────────────
Full chronological event log with category filters, keyword search,
timestamped entries, and color-coded event types.
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


class EventLogView(tk.Frame):
    """System event log stream with search and category filters."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_BASE)
        self.app = app
        self.fonts = get_fonts()

        self._filter_cat = tk.StringVar(value="All")
        self._search_var = tk.StringVar(value="")
        self._all_events = []

        self._build_layout()

    def _build_layout(self):
        # 1. Filter and Search Bar Card
        filter_card = SectionCard(
            self,
            title="System Audit & Event Timeline",
            subtitle="Search, filter, and inspect chronological kernel logs",
            badge_text="LIVE TELEMETRY",
            badge_color=CYAN
        )
        filter_card.pack(fill="x", padx=16, pady=(16, 12))

        bar = tk.Frame(filter_card, bg=BG_CARD)
        bar.pack(fill="x", pady=4)

        # Search Bar
        tk.Label(
            bar, text="Search Keywords:", bg=BG_CARD, fg=TEXT_SECONDARY, font=self.fonts["caption_bold"]
        ).pack(side="left", padx=(0, 6))

        entry_search = ttk.Entry(bar, textvariable=self._search_var, width=20)
        entry_search.pack(side="left", padx=(0, 16))
        entry_search.bind("<KeyRelease>", lambda e: self._render_events())

        # Category Filter
        tk.Label(
            bar, text="Event Category:", bg=BG_CARD, fg=TEXT_SECONDARY, font=self.fonts["caption_bold"]
        ).pack(side="left", padx=(0, 6))

        cb_cat = ttk.Combobox(
            bar,
            textvariable=self._filter_cat,
            values=["All", "allocate", "request", "release", "terminate", "rollback", "scenario", "step"],
            width=14,
            state="readonly"
        )
        cb_cat.pack(side="left", padx=(0, 16))
        cb_cat.bind("<<ComboboxSelected>>", lambda e: self._render_events())

        # Clear Log Button
        btn_clear = ttk.Button(
            bar,
            text="🗑 Clear Event Log",
            style="Ghost.TButton",
            command=self._on_clear_log
        )
        btn_clear.pack(side="right")

        # 2. Main Event Stream Section
        self.stream_card = SectionCard(
            self,
            title="Chronological Event Stream",
            subtitle="Real-time OS allocation, blocking, and recovery transitions"
        )
        self.stream_card.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.text_log = tk.Text(
            self.stream_card,
            bg=BG_INPUT,
            fg=TEXT_PRIMARY,
            font=self.fonts["mono"],
            wrap="word",
            state="disabled",
            borderwidth=0,
            padx=14,
            pady=12
        )

        scroll = ttk.Scrollbar(self.stream_card, orient="vertical", command=self.text_log.yview)
        self.text_log.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.text_log.pack(fill="both", expand=True)

        # Style tags
        self.text_log.tag_config("time", foreground=TEXT_MUTED)
        self.text_log.tag_config("cat_allocate", foreground=SUCCESS, font=self.fonts["mono_sm_bold"])
        self.text_log.tag_config("cat_request", foreground=WARNING, font=self.fonts["mono_sm_bold"])
        self.text_log.tag_config("cat_release", foreground=CYAN, font=self.fonts["mono_sm_bold"])
        self.text_log.tag_config("cat_terminate", foreground=DANGER, font=self.fonts["mono_sm_bold"])
        self.text_log.tag_config("cat_rollback", foreground=PURPLE, font=self.fonts["mono_sm_bold"])
        self.text_log.tag_config("cat_scenario", foreground=CYAN, font=self.fonts["mono_sm_bold"])
        self.text_log.tag_config("cat_step", foreground=TEXT_SECONDARY, font=self.fonts["mono_sm_bold"])
        self.text_log.tag_config("cat_default", foreground=TEXT_MUTED, font=self.fonts["mono_sm_bold"])
        self.text_log.tag_config("msg", foreground=TEXT_PRIMARY)

    # ── User Actions ──────────────────────────────────────────────────────────

    def _on_clear_log(self):
        if self.app.confirm_action("Clear Event Log", "Are you sure you want to clear the system event log history?"):
            self.app.manager._event_log.clear()
            self._all_events.clear()
            self._render_events()
            self.app.toast("Event log cleared", "info")

    # ── Display Routine ───────────────────────────────────────────────────────

    def update_view(self, snapshot: dict, detection_result=None):
        self._all_events = snapshot.get("events", [])
        self._render_events()

    def _render_events(self):
        cat_filter = self._filter_cat.get().lower()
        search_query = self._search_var.get().strip().lower()

        t = self.text_log
        t.configure(state="normal")
        t.delete("1.0", "end")

        matching_count = 0
        for ev in reversed(self._all_events):
            ev_type = ev.get("type", "default").lower()
            ev_msg = ev.get("message", "")
            ev_time = ev.get("timestamp", "--:--:--")

            # Check Category
            if cat_filter != "all" and ev_type != cat_filter:
                continue

            # Check Search Query
            if search_query and (search_query not in ev_msg.lower() and search_query not in ev_type):
                continue

            matching_count += 1
            cat_tag = f"cat_{ev_type}" if f"cat_{ev_type}" in (
                "cat_allocate", "cat_request", "cat_release", "cat_terminate", "cat_rollback", "cat_scenario", "cat_step"
            ) else "cat_default"

            t.insert("end", f"[{ev_time}] ", "time")
            t.insert("end", f"[{ev_type.upper():^10}] ", cat_tag)
            t.insert("end", f"{ev_msg}\n", "msg")

        if matching_count == 0:
            t.insert("end", "◈ No system events matching the selected filters ◈\n", "time")

        t.configure(state="disabled")
