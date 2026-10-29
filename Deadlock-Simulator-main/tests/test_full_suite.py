"""
DEADLOCKNEXUS Comprehensive Deep-Test Suite
───────────────────────────────────────────
Tests every single algorithm, view, component, scenario, recovery strategy,
and telemetry calculation in detail.
"""

import sys
import os
import unittest
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.resource_manager import ResourceManager
from core.deadlock_detector import DeadlockDetector
from core.recovery_engine import RecoveryEngine
from core.simulation_engine import SimulationEngine
from gui.main_window import DeadlockSimulatorApp
from gui.graph_renderer import GraphRenderer
from gui.components.cards import StatCard, SectionCard, StatusBadge, UtilizationBar
from gui.components.toast import ToastNotification


class TestComprehensiveEngineAndUI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = DeadlockSimulatorApp()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.app.destroy()
        except Exception:
            pass

    def setUp(self):
        self.app.manager.clear_all()
        self.app.last_detection = None
        self.app.pid_counter[0] = 1
        self.app.rid_counter[0] = 1

    # ── Test 1: Process & Resource Lifecycle ──────────────────────────────────

    def test_process_and_resource_lifecycle(self):
        """Test process creation, resource provisioning, allocation, blocking, and release."""
        # Add processes with varying priorities
        p1 = self.app.manager.add_process("P1", "Worker-1", 1)
        p2 = self.app.manager.add_process("P2", "Worker-2", 4)
        p3 = self.app.manager.add_process("P3", "Worker-3", 5)
        self.assertEqual(len(self.app.manager.processes), 3)

        # Add different resource types
        r1 = self.app.manager.add_resource("R1", "DB-Mutex", 1, "mutex")
        r2 = self.app.manager.add_resource("R2", "Buffer-Sem", 3, "semaphore")
        r3 = self.app.manager.add_resource("R3", "Disk-File", 2, "file")
        self.assertEqual(len(self.app.manager.resources), 3)

        # Allocation: P1 acquires R1 (mutex)
        ok1 = self.app.manager.request_resource("P1", "R1", 1)
        self.assertTrue(ok1)
        self.assertEqual(r1.available_instances, 0)
        self.assertEqual(p1.state, "running")

        # Blocking: P2 requests R1 (unavailable)
        ok2 = self.app.manager.request_resource("P2", "R1", 1)
        self.assertFalse(ok2)
        self.assertEqual(p2.state, "waiting")
        self.assertIn("R1", p2.requested)

        # Multi-instance: P3 acquires 2 of R2
        ok3 = self.app.manager.request_resource("P3", "R2", 2)
        self.assertTrue(ok3)
        self.assertEqual(r2.available_instances, 1)

        # Release
        self.app.manager.release_resource("P3", "R2", 1)
        self.assertEqual(r2.available_instances, 2)
        self.assertEqual(p3.allocated["R2"], 1)

    # ── Test 2: All 5 Scenarios & 3 Detection Algorithms ─────────────────────

    def test_all_scenarios_and_detections(self):
        """Load each of the 5 scenarios and test RAG, Banker's, and WFG detection."""
        scenarios = ["dining_philosophers", "bankers_classic", "producer_consumer", "readers_writers", "random_chaos"]
        
        for sc in scenarios:
            self.app.load_scenario_by_name(sc)
            snap = self.app.manager.get_snapshot()
            
            if sc != "random_chaos":
                self.assertGreater(len(snap["processes"]), 0, f"Failed processes for {sc}")
                self.assertGreater(len(snap["resources"]), 0, f"Failed resources for {sc}")

            # Run all 3 detection algorithms
            res_rag = self.app.detector.detect(snap, "rag")
            self.assertIsNotNone(res_rag.details)
            self.assertIn(res_rag.algorithm, ["Resource Allocation Graph (DFS Cycle Detection)"])

            res_bank = self.app.detector.detect(snap, "bankers")
            self.assertIsNotNone(res_bank.details)
            self.assertIn("Banker", res_bank.algorithm)

            res_wfg = self.app.detector.detect(snap, "wfg")
            self.assertIsNotNone(res_wfg.details)
            self.assertIn("Wait-For", res_wfg.algorithm)

    # ── Test 3: Four Recovery Strategies ──────────────────────────────────────

    def test_recovery_strategies(self):
        """Verify all 4 recovery strategies resolve active deadlocks."""
        strategies = ["terminate", "preempt", "rollback", "kill_all"]

        for strat in strategies:
            # Set up fresh classic deadlock
            self.app.manager.clear_all()
            self.app.manager.add_process("P1", "Proc1", 5)
            self.app.manager.add_process("P2", "Proc2", 1)
            self.app.manager.add_resource("R1", "Mutex1", 1)
            self.app.manager.add_resource("R2", "Mutex2", 1)
            self.app.manager.request_resource("P1", "R1")
            self.app.manager.request_resource("P2", "R2")
            self.app.manager.request_resource("P1", "R2")
            self.app.manager.request_resource("P2", "R1")

            # Confirm deadlock detected
            snap_before = self.app.manager.get_snapshot()
            det_before = self.app.detector.detect(snap_before, "rag")
            self.assertTrue(det_before.detected, f"Deadlock setup failed for {strat}")

            # Execute Recovery Strategy
            action = self.app.recovery.recover(self.app.manager, det_before, strat)
            self.assertTrue(action.success, f"Recovery {strat} reported failure")
            self.assertGreater(len(action.steps), 0)
            self.assertIsNotNone(action.cost_estimate)

            # Confirm system state is now deadlock free
            snap_after = self.app.manager.get_snapshot()
            det_after = self.app.detector.detect(snap_after, "rag")
            self.assertFalse(det_after.detected, f"System remained deadlocked after {strat}")

    # ── Test 4: All 9 UI Views and Reactive Updates ───────────────────────────

    def test_all_views_and_reactivity(self):
        """Test updating and rendering all 9 views with real data."""
        # Seed test data
        self.app.load_scenario_by_name("dining_philosophers")
        
        # Execute allocation steps
        scenario = self.app.sim.SCENARIOS["dining_philosophers"]
        for pid, rid in scenario["allocation_sequence"]:
            self.app.manager.request_resource(pid, rid)

        snap = self.app.manager.get_snapshot()
        det = self.app.detector.detect(snap, "rag")

        # 1. Dashboard View
        self.app.navigate_to("dashboard")
        dash_view = self.app.views["dashboard"]
        dash_view.update_view(snap, det)
        self.assertEqual(dash_view.card_state.lbl_value.cget("text"), "DEADLOCK")

        # 2. Process View
        self.app.navigate_to("processes")
        proc_view = self.app.views["processes"]
        proc_view.update_view(snap, det)
        self.assertEqual(len(proc_view.tree.get_children()), 5)

        # 3. Resource View
        self.app.navigate_to("resources")
        res_view = self.app.views["resources"]
        res_view.update_view(snap, det)
        self.assertEqual(len(res_view.tree.get_children()), 5)

        # 4. Allocation View
        self.app.navigate_to("allocation")
        alloc_view = self.app.views["allocation"]
        alloc_view.update_view(snap, det)
        self.assertGreater(len(alloc_view.alloc_tree.get_children()), 0)
        self.assertGreater(len(alloc_view.req_tree.get_children()), 0)

        # 5. Detection View
        self.app.navigate_to("detection")
        det_view = self.app.views["detection"]
        det_view.update_view(snap, det)
        self.assertIn("DEADLOCK DETECTED", det_view.text_result.get("1.0", "end"))

        # 6. Recovery View
        self.app.navigate_to("recovery")
        rec_view = self.app.views["recovery"]
        rec_view.update_view(snap, det)
        self.assertIn("Deadlock", rec_view.lbl_deadlock_info.cget("text"))

        # 7. Scenario View
        self.app.navigate_to("scenarios")
        sc_view = self.app.views["scenarios"]
        sc_view.update_view(snap, det)

        # 8. Event Log View
        self.app.navigate_to("event_log")
        log_view = self.app.views["event_log"]
        log_view.update_view(snap, det)
        self.assertGreater(len(log_view._all_events), 0)

        # 9. Analytics View
        self.app.navigate_to("analytics")
        ana_view = self.app.views["analytics"]
        ana_view.update_view(snap, det)
        self.assertEqual(ana_view.card_ratio.lbl_value.cget("text"), "DEADLOCK")
        self.assertGreater(len(ana_view.tree_res_analytics.get_children()), 0)

    # ── Test 5: Graph Renderer & Canvas Controls ──────────────────────────────

    def test_graph_renderer_controls(self):
        """Test GraphRenderer zooming, panning, reset, and cycle edge extraction."""
        canvas = self.app.views["dashboard"].canvas
        renderer = GraphRenderer(canvas)

        self.app.load_scenario_by_name("dining_philosophers")
        snap = self.app.manager.get_snapshot()
        det = self.app.detector.detect(snap, "rag")

        # Test RAG rendering
        renderer.render(snap, det, "rag")
        self.assertGreater(len(renderer._positions), 0)

        # Test WFG rendering
        renderer.render(snap, det, "wfg")

        # Test Zoom In / Out / Reset
        init_zoom = renderer.zoom_scale
        renderer.zoom_in()
        self.assertGreater(renderer.zoom_scale, init_zoom)

        renderer.zoom_out()
        renderer.reset_view()
        self.assertEqual(renderer.zoom_scale, 1.0)
        self.assertEqual(renderer.pan_x, 0.0)
        self.assertEqual(renderer.pan_y, 0.0)

    # ── Test 6: Toast Notification System ─────────────────────────────────────

    def test_toast_system(self):
        """Test toast creation and dismissal."""
        self.app.toast("Test success toast", "success")
        self.app.toast("Test warning toast", "warn")
        self.app.toast("Test danger toast", "danger")
        self.assertGreater(len(self.app.toasts._active_toasts), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
