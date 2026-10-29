"""
GUI Automation & Integration Tests
───────────────────────────────────
Validates that the Tkinter application initializes, navigates between views,
creates processes and resources, runs detection algorithms, executes recovery,
loads scenarios, and renders the graph without exceptions.
"""

import sys
import os
import unittest
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import DeadlockSimulatorApp


class TestGUIIntegration(unittest.TestCase):

    def setUp(self):
        self.app = DeadlockSimulatorApp()
        self.app.withdraw()  # Hide window during test

    def tearDown(self):
        try:
            self.app.destroy()
        except Exception:
            pass

    def test_app_initialization(self):
        """Verify main window and components are properly initialized."""
        self.assertIsNotNone(self.app)
        self.assertEqual(len(self.app.views), 9)
        self.assertIn("dashboard", self.app.views)
        self.assertIn("processes", self.app.views)
        self.assertIn("resources", self.app.views)
        self.assertIn("allocation", self.app.views)
        self.assertIn("detection", self.app.views)
        self.assertIn("recovery", self.app.views)
        self.assertIn("scenarios", self.app.views)
        self.assertIn("event_log", self.app.views)
        self.assertIn("analytics", self.app.views)

    def test_view_navigation(self):
        """Verify seamless navigation between all 9 sidebar views."""
        views_to_test = [
            "dashboard", "processes", "resources", "allocation",
            "detection", "recovery", "scenarios", "event_log", "analytics"
        ]
        for vkey in views_to_test:
            self.app.navigate_to(vkey)
            self.assertEqual(self.app.current_view_key, vkey)
            self.app.update_idletasks()

    def test_scenario_loading_and_graph_render(self):
        """Test loading a scenario and rendering the graph."""
        self.app.load_scenario_by_name("dining_philosophers")
        snap = self.app.manager.get_snapshot()
        self.assertEqual(len(snap["processes"]), 5)
        self.assertEqual(len(snap["resources"]), 5)

        # Trigger graph render in RAG and WFG modes
        self.app.graph_mode.set("rag")
        self.app.refresh_graph()
        self.app.update_idletasks()

        self.app.graph_mode.set("wfg")
        self.app.refresh_graph()
        self.app.update_idletasks()

    def test_process_and_resource_creation(self):
        """Test UI creation handlers for processes and resources."""
        # Navigate to processes view
        self.app.navigate_to("processes")
        pview = self.app.views["processes"]
        pview._pname_var.set("TestProc")
        pview._ppri_var.set(3)
        pview._on_add_process()

        snap = self.app.manager.get_snapshot()
        self.assertIn("P1", snap["processes"])
        self.assertEqual(snap["processes"]["P1"]["name"], "TestProc")

        # Navigate to resources view
        self.app.navigate_to("resources")
        rview = self.app.views["resources"]
        rview._rname_var.set("TestMutex")
        rview._rinst_var.set(2)
        rview._rtype_var.set("mutex")
        rview._on_add_resource()

        snap2 = self.app.manager.get_snapshot()
        self.assertIn("R1", snap2["resources"])
        self.assertEqual(snap2["resources"]["R1"]["name"], "TestMutex")

    def test_detection_and_recovery_flow(self):
        """Test executing detection and recovery through the views."""
        # Create deadlock
        self.app.manager.add_process("P1", "Proc1", 2)
        self.app.manager.add_process("P2", "Proc2", 1)
        self.app.manager.add_resource("R1", "Res1", 1)
        self.app.manager.add_resource("R2", "Res2", 1)
        self.app.manager.request_resource("P1", "R1")
        self.app.manager.request_resource("P2", "R2")
        self.app.manager.request_resource("P1", "R2")
        self.app.manager.request_resource("P2", "R1")

        # Run Detection View
        self.app.navigate_to("detection")
        det_view = self.app.views["detection"]
        det_view._algo_var.set("rag")
        det_view._on_run_detection()

        self.assertIsNotNone(self.app.last_detection)
        self.assertTrue(self.app.last_detection.detected)

        # Run Recovery View (bypass confirmation dialog by testing recovery engine dispatch)
        self.app.navigate_to("recovery")
        action = self.app.recovery.recover(self.app.manager, self.app.last_detection, "terminate")
        self.assertTrue(action.success)

        # Refresh all and check resolved state
        self.app.refresh_all()
        snap = self.app.manager.get_snapshot()
        result_after = self.app.detector.detect(snap, "rag")
        self.assertFalse(result_after.detected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
