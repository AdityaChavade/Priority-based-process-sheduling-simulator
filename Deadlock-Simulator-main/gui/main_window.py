"""
DEADLOCKNEXUS — Main Window & Application Shell
────────────────────────────────────────────────
Deadlock Detection & Recovery Simulator
Academic Operating Systems Visualization Platform.
"""

import tkinter as tk
from tkinter import ttk
import time
import sys
import os

# Ensure import paths resolve cleanly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.resource_manager import ResourceManager
from core.deadlock_detector import DeadlockDetector, DeadlockResult
from core.recovery_engine import RecoveryEngine
from core.simulation_engine import SimulationEngine
from gui.theme import (
    BG_BASE, BG_SIDEBAR, BG_PANEL, BG_CARD, BG_CARD_ALT, BG_INPUT,
    BORDER_DEFAULT, BORDER_SUBTLE, BORDER_FOCUS, CYAN, CYAN_DIM, PURPLE,
    SUCCESS, SUCCESS_BG, WARNING, WARNING_BG, DANGER, DANGER_BG,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, TEXT_DARK,
    configure_app_styles, get_fonts
)
from gui.components.toast import ToastNotification
from gui.components.dialogs import ConfirmDialog
from gui.components.cards import StatusBadge

from gui.views.dashboard_view import DashboardView
from gui.views.process_view import ProcessView
from gui.views.resource_view import ResourceView
from gui.views.allocation_view import AllocationView
from gui.views.detection_view import DetectionView
from gui.views.recovery_view import RecoveryView
from gui.views.scenario_view import ScenarioView
from gui.views.event_log_view import EventLogView
from gui.views.analytics_view import AnalyticsView


class DeadlockSimulatorApp(tk.Tk):
    """
    Main Application Window for DEADLOCKNEXUS.
    Implements a responsive navigation shell, live telemetry, and unified views.
    """

    def __init__(self):
        super().__init__()
        self.title("DEADLOCKNEXUS — Deadlock Detection & Recovery Simulator")
        self.geometry("1440x900")
        self.minsize(1100, 700)
        self.configure(bg=BG_BASE)

        # Initialize Themes & Design Tokens
        self.fonts = configure_app_styles(self)

        # Core OS Engines
        self.manager = ResourceManager()
        self.detector = DeadlockDetector()
        self.recovery = RecoveryEngine()
        self.sim = SimulationEngine(self.manager, self._on_sim_event)
        self.renderer = None  # Instantiated by Dashboard

        # Reactive State
        self.last_detection: DeadlockResult = None
        self.auto_detect = tk.BooleanVar(value=True)
        self.graph_mode = tk.StringVar(value="rag")
        self.current_scenario_name = "None (Manual)"
        self.pid_counter = [1]
        self.rid_counter = [1]

        # Toast Notification System
        self.toasts = ToastNotification(self)

        # Navigation State
        self.views = {}
        self.current_view_key = "dashboard"
        self.nav_buttons = {}

        # Build Application Shell
        self._build_header()
        self._build_main_shell()
        self._build_statusbar()

        # Navigate to default Dashboard
        self.navigate_to("dashboard")

        # Start Realtime Background Loop
        self._start_refresh_loop()

    # ── Application Header ────────────────────────────────────────────────────

    def _build_header(self):
        self.hdr = tk.Frame(self, bg=BG_SIDEBAR, height=52, highlightbackground=BORDER_DEFAULT, highlightthickness=1)
        self.hdr.pack(fill="x")
        self.hdr.pack_propagate(False)

        # Left Branding
        brand_frame = tk.Frame(self.hdr, bg=BG_SIDEBAR)
        brand_frame.pack(side="left", padx=16, fill="y")

        lbl_title = tk.Label(
            brand_frame,
            text="DEADLOCKNEXUS",
            bg=BG_SIDEBAR,
            fg=TEXT_PRIMARY,
            font=self.fonts["title"]
        )
        lbl_title.pack(side="left", padx=(0, 10))

        lbl_sep = tk.Label(
            brand_frame,
            text="|",
            bg=BG_SIDEBAR,
            fg=BORDER_DEFAULT,
            font=self.fonts["body"]
        )
        lbl_sep.pack(side="left", padx=(0, 10))

        lbl_subtitle = tk.Label(
            brand_frame,
            text="Deadlock Detection & Recovery Simulator",
            bg=BG_SIDEBAR,
            fg=TEXT_MUTED,
            font=self.fonts["caption"]
        )
        lbl_subtitle.pack(side="left")

        # Right Status Deck
        right_deck = tk.Frame(self.hdr, bg=BG_SIDEBAR)
        right_deck.pack(side="right", padx=16, fill="y")

        # Scenario Label
        self.lbl_scenario_badge = tk.Label(
            right_deck,
            text="Scenario: None (Manual)",
            bg=BG_SIDEBAR,
            fg=TEXT_SECONDARY,
            font=self.fonts["caption_bold"]
        )
        self.lbl_scenario_badge.pack(side="left", padx=(0, 16), pady=12)

        # Quick Counts
        self.lbl_hdr_counts = tk.Label(
            right_deck,
            text="0 Processes  •  0 Resources",
            bg=BG_SIDEBAR,
            fg=TEXT_MUTED,
            font=self.fonts["mono_sm"]
        )
        self.lbl_hdr_counts.pack(side="left", padx=(0, 16), pady=12)

        # Main Deadlock Indicator Status Badge
        self.hdr_status_pill = StatusBadge(
            right_deck,
            text="SYSTEM SAFE",
            color=SUCCESS
        )
        self.hdr_status_pill.pack(side="left", padx=(0, 12), pady=12)

        # Recalculate Button
        btn_refresh = ttk.Button(
            right_deck,
            text="↺ Recalculate",
            style="Ghost.TButton",
            command=self.refresh_all
        )
        btn_refresh.pack(side="left", pady=10)

    # ── Application Main Body Shell ───────────────────────────────────────────

    def _build_main_shell(self):
        self.body_paned = tk.Frame(self, bg=BG_BASE)
        self.body_paned.pack(fill="both", expand=True)

        # Left Sidebar (Clean, compact, grouped)
        self.sidebar = tk.Frame(
            self.body_paned,
            bg=BG_SIDEBAR,
            width=180,
            highlightbackground=BORDER_DEFAULT,
            highlightthickness=1
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self._build_sidebar_navigation()

        # Main Content Container
        self.content_container = tk.Frame(self.body_paned, bg=BG_BASE)
        self.content_container.pack(side="right", fill="both", expand=True)

        # Instantiate Views
        self.views = {
            "dashboard": DashboardView(self.content_container, self),
            "processes": ProcessView(self.content_container, self),
            "resources": ResourceView(self.content_container, self),
            "allocation": AllocationView(self.content_container, self),
            "detection": DetectionView(self.content_container, self),
            "recovery": RecoveryView(self.content_container, self),
            "scenarios": ScenarioView(self.content_container, self),
            "event_log": EventLogView(self.content_container, self),
            "analytics": AnalyticsView(self.content_container, self),
        }

    # ── Sidebar Navigation ────────────────────────────────────────────────────

    def _build_sidebar_navigation(self):
        # Academic Grouped Structure
        groups = [
            ("OVERVIEW", [
                ("dashboard", "Dashboard"),
            ]),
            ("MANAGEMENT", [
                ("processes", "Processes"),
                ("resources", "Resources"),
                ("allocation", "Allocation"),
            ]),
            ("ANALYSIS", [
                ("detection", "Detection"),
                ("recovery", "Recovery"),
            ]),
            ("TOOLS", [
                ("scenarios", "Scenarios"),
                ("event_log", "Event Log"),
                ("analytics", "Analytics"),
            ]),
        ]

        for group_title, items in groups:
            # Group Header
            lbl_group = tk.Label(
                self.sidebar,
                text=group_title,
                bg=BG_SIDEBAR,
                fg=TEXT_MUTED,
                font=self.fonts["mono_badge"]
            )
            lbl_group.pack(anchor="w", padx=14, pady=(12, 4))

            for key, label in items:
                btn_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR, cursor="hand2")
                btn_frame.pack(fill="x", padx=6, pady=1)

                indicator = tk.Frame(btn_frame, bg=BG_SIDEBAR, width=3)
                indicator.pack(side="left", fill="y", padx=(0, 8))

                lbl_title = tk.Label(
                    btn_frame,
                    text=label,
                    bg=BG_SIDEBAR,
                    fg=TEXT_SECONDARY,
                    font=self.fonts["body"],
                    anchor="w",
                    pady=4
                )
                lbl_title.pack(side="left", fill="x", expand=True)

                self.nav_buttons[key] = {
                    "frame": btn_frame,
                    "indicator": indicator,
                    "lbl_title": lbl_title,
                }

                # Bind click
                for w in (btn_frame, indicator, lbl_title):
                    w.bind("<Button-1>", lambda e, k=key: self.navigate_to(k))

    def navigate_to(self, view_key: str):
        """Switches the active view in the main container."""
        if view_key not in self.views:
            return

        self.current_view_key = view_key

        # Hide all views and show target view
        for key, view in self.views.items():
            if key == view_key:
                view.pack(fill="both", expand=True)
            else:
                view.pack_forget()

        # Update Navigation Button Styles (Clean, non-SaaS)
        for key, widgets in self.nav_buttons.items():
            is_active = (key == view_key)
            bg_color = BG_CARD if is_active else BG_SIDEBAR
            text_color = CYAN if is_active else TEXT_SECONDARY
            font_choice = self.fonts["body_bold"] if is_active else self.fonts["body"]
            ind_color = CYAN if is_active else BG_SIDEBAR

            widgets["frame"].configure(bg=bg_color)
            widgets["indicator"].configure(bg=ind_color)
            widgets["lbl_title"].configure(bg=bg_color, fg=text_color, font=font_choice)

        self.refresh_current_view()

    # ── Application Status Bar ────────────────────────────────────────────────

    def _build_statusbar(self):
        self.sb = tk.Frame(self, bg=BG_SIDEBAR, height=26, highlightbackground=BORDER_DEFAULT, highlightthickness=1)
        self.sb.pack(fill="x", side="bottom")
        self.sb.pack_propagate(False)

        # Left: Live Status / Activity Message
        self._status_var = tk.StringVar(value="System Ready • Kernel Initialized")
        lbl_msg = tk.Label(
            self.sb,
            textvariable=self._status_var,
            bg=BG_SIDEBAR,
            fg=TEXT_MUTED,
            font=self.fonts["caption"]
        )
        lbl_msg.pack(side="left", padx=12)

        # Right: Clock & Auto-detect State
        self.lbl_clock = tk.Label(
            self.sb,
            text="00:00:00",
            bg=BG_SIDEBAR,
            fg=TEXT_MUTED,
            font=self.fonts["mono_sm"]
        )
        self.lbl_clock.pack(side="right", padx=12)

        self.lbl_autodetect_status = tk.Label(
            self.sb,
            text="AUTO-DETECT ON",
            bg=BG_SIDEBAR,
            fg=SUCCESS,
            font=self.fonts["mono_sm_bold"]
        )
        self.lbl_autodetect_status.pack(side="right", padx=12)

        chk_auto = ttk.Checkbutton(
            self.sb,
            text="Auto-Detect",
            variable=self.auto_detect,
            command=self._on_autodetect_toggle
        )
        chk_auto.pack(side="right", padx=(0, 6))

    def _on_autodetect_toggle(self):
        if self.auto_detect.get():
            self.lbl_autodetect_status.configure(text="AUTO-DETECT ON", fg=SUCCESS)
        else:
            self.lbl_autodetect_status.configure(text="AUTO-DETECT OFF", fg=TEXT_MUTED)
        self.refresh_all()

    # ── Notification & Dialog Helpers ─────────────────────────────────────────

    def toast(self, message: str, level: str = "info"):
        self.toasts.show(message, level)

    def confirm_action(self, title: str, message: str, detail: str = "", is_danger: bool = False) -> bool:
        dlg = ConfirmDialog(self, title, message, detail=detail, is_danger=is_danger)
        return dlg.result

    # ── Refresh & State Synchronization Loop ──────────────────────────────────

    def _start_refresh_loop(self):
        self._sync_state()

    def _sync_state(self):
        try:
            self._update_telemetry()
        except Exception:
            pass
        self.after(1000, self._sync_state)

    def _update_telemetry(self):
        self.lbl_clock.configure(text=time.strftime("%H:%M:%S"))

        snap = self.manager.get_snapshot()
        processes = snap.get("processes", {})
        resources = snap.get("resources", {})

        self.lbl_hdr_counts.configure(
            text=f"{len(processes)} Processes  •  {len(resources)} Resources"
        )

        if self.auto_detect.get():
            algo = "rag"
            if "detection" in self.views and hasattr(self.views["detection"], "_algo_var"):
                algo = self.views["detection"]._algo_var.get()
            result = self.detector.detect(snap, algo)
            
            was_deadlock = self.last_detection and self.last_detection.detected
            is_deadlock = result.detected
            self.last_detection = result

            if is_deadlock and not was_deadlock:
                self.toast(f"Deadlock detected! {len(result.deadlocked_processes)} process(es) affected.", "danger")
            elif not is_deadlock and was_deadlock:
                self.toast("Deadlock resolved — System safe.", "success")

            if is_deadlock:
                self.hdr_status_pill.set_status(f"DEADLOCK DETECTED ({len(result.deadlocked_processes)} PROC)", DANGER)
            else:
                self.hdr_status_pill.set_status("SYSTEM SAFE", SUCCESS)
        else:
            if self.last_detection and self.last_detection.detected:
                self.hdr_status_pill.set_status("DEADLOCK (MANUAL)", DANGER)
            else:
                self.hdr_status_pill.set_status("MANUAL CHECK", WARNING)

        self.refresh_current_view()

    def refresh_current_view(self):
        snap = self.manager.get_snapshot()
        if self.current_view_key in self.views:
            view = self.views[self.current_view_key]
            view.update_view(snap, self.last_detection)

        if self.current_view_key == "dashboard" and self.renderer:
            self.renderer.render(snap, self.last_detection, self.graph_mode.get())

    def refresh_graph(self):
        snap = self.manager.get_snapshot()
        if self.renderer:
            self.renderer.render(snap, self.last_detection, self.graph_mode.get())

    def refresh_all(self):
        self._update_telemetry()
        self.toast("System state synchronized", "info")

    # ── Engine Proxy Actions ──────────────────────────────────────────────────

    def load_scenario_by_name(self, scenario_name: str):
        self.pid_counter[0] = 1
        self.rid_counter[0] = 1
        self.sim.load_scenario(scenario_name)
        self.last_detection = None
        
        nice_names = {
            "dining_philosophers": "Dining Philosophers",
            "bankers_classic": "Banker's Classic",
            "producer_consumer": "Producer-Consumer",
            "readers_writers": "Readers-Writers",
            "random_chaos": "Random Chaos",
        }
        self.current_scenario_name = nice_names.get(scenario_name, scenario_name)
        self.lbl_scenario_badge.configure(text=f"Scenario: {self.current_scenario_name}")
        self.toast(f"Loaded scenario: {self.current_scenario_name}", "info")
        self.refresh_all()

    def run_simulation(self):
        scenario_key = "dining_philosophers"
        if "scenarios" in self.views and hasattr(self.views["scenarios"], "_scenario_var"):
            scenario_key = self.views["scenarios"]._scenario_var.get()
        self.sim.run_scenario_steps(scenario_key)
        self.toast(f"Simulation executing: {scenario_key}", "info")

    def run_detection(self):
        if "detection" in self.views:
            self.views["detection"]._on_run_detection()

    def clear_all_with_confirm(self):
        if self.confirm_action("Clear System", "Are you sure you want to clear all processes, resources, and reset system state?", is_danger=True):
            self.sim.stop()
            self.manager.clear_all()
            self.last_detection = None
            self.pid_counter[0] = 1
            self.rid_counter[0] = 1
            self.current_scenario_name = "None (Manual)"
            self.lbl_scenario_badge.configure(text="Scenario: None (Manual)")
            self.toast("System cleared and reset to base state", "info")
            self.refresh_all()

    def _on_sim_event(self, event_type: str, message: str):
        self._status_var.set(f"[{event_type.upper()}] {message}")


def main():
    app = DeadlockSimulatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
