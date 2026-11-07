"""Host-only admission/cleanup tests. Never connect to a VM or send input."""
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "external-lab2-mouse.py"
spec = importlib.util.spec_from_file_location("external_lab2_mouse", SOURCE)
mouse = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mouse)


class MouseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=mouse.ROOT / "artifacts")
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "trial"
        self.events = []
        self.client = SimpleNamespace(**{name: self.event(name) for name in
            ("mouseMove", "mouseDown", "mouseUp", "disconnect")})
        self.owner = unittest.mock.MagicMock()
        self.owner.__enter__.return_value.abandoned = False
        self.verifier = patch.object(mouse.native, "verify_identity", return_value={"vm": "same"})
        self.verify = self.verifier.start()
        self.addCleanup(self.verifier.stop)
        patches = [patch.object(mouse.native, "validate_config", return_value=object()),
                   patch.object(mouse.native, "ControlMutex", return_value=self.owner),
                   patch.object(mouse.native, "collect_identity", return_value={"vm": "same"}),
                   patch.object(mouse.native, "connect", return_value=self.client),
                   patch.object(mouse.native, "_capture", side_effect=self.capture),
                   patch.object(mouse, "read_review", return_value="reviewed reversible UI control"),
                   patch.object(mouse.time, "sleep")]
        for item in patches:
            item.start()
            self.addCleanup(item.stop)

    def event(self, name):
        return lambda *args: self.events.append((name, *args))

    def capture(self, client, destination):
        self.events.append(("capture", destination.name))
        destination.write_bytes(b"test image")
        return 1211, 757

    def args(self, action="click", x=914, y=335):
        return SimpleNamespace(action=action, x=x, y=y, output=self.output)

    def result(self):
        return json.loads((self.output / "result.json").read_text())

    def test_capture_never_sends_mouse_input(self):
        result = mouse.run(self.args("capture", None, None))
        self.assertFalse(result["inputMayHaveBeenSent"])
        self.assertEqual(self.events, [("capture", "before.png"), ("disconnect",)])

    def test_move_is_standalone_without_button_down(self):
        result = mouse.run(self.args("move"))
        self.assertTrue(result["consoleMutexReleased"])
        self.assertIn(("mouseMove", 914, 335), self.events)
        self.assertFalse(any(e[0] == "mouseDown" for e in self.events))

    def test_click_initializes_position_on_same_client_before_button_down(self):
        mouse.run(self.args())
        self.assertEqual([e[0] for e in self.events],
                         ["capture", "mouseMove", "mouseDown", "mouseUp", "capture", "mouseUp", "disconnect"])
        self.assertTrue(self.result()["buttonReleaseSent"])

    def test_declined_review_never_moves_or_clicks(self):
        with patch.object(mouse, "read_review", side_effect=ValueError("review declined")):
            with self.assertRaises(ValueError): mouse.run(self.args())
        self.assertFalse(self.result()["inputMayHaveBeenSent"])
        self.assertEqual(self.events[-1], ("disconnect",))

    def test_invalid_coordinates_never_send_input(self):
        for x, y in [(-1, 20), (1211, 20), (20, 757), (True, 20)]:
            self.output = Path(self.temp.name) / ("bad-" + str(x) + "-" + str(y))
            with self.assertRaisesRegex(ValueError, "outside reviewed"): mouse.run(self.args(x=x, y=y))
            self.assertFalse(self.result()["inputMayHaveBeenSent"])

    def test_busy_mutex_never_connects(self):
        self.owner.__enter__.side_effect = mouse.native.Blocked("controller-busy")
        with self.assertRaises(mouse.native.Blocked): mouse.run(self.args())
        self.assertEqual(self.events, [])

    def test_vm_drift_before_input_rejects(self):
        self.verify.side_effect = mouse.native.Blocked("target-drift")
        with self.assertRaises(mouse.native.Blocked): mouse.run(self.args())
        self.assertFalse(self.result()["inputMayHaveBeenSent"])

    def test_button_down_failure_still_releases_and_disconnects(self):
        self.client.mouseDown = lambda *_: (_ for _ in ()).throw(RuntimeError("transport failed"))
        with self.assertRaises(RuntimeError): mouse.run(self.args())
        self.assertIn(("mouseUp", 1), self.events)
        self.assertEqual(self.events[-1], ("disconnect",))
        self.assertEqual(self.result()["status"], "blocked")

    def test_disconnect_failure_cannot_report_completion(self):
        self.client.disconnect = lambda: (_ for _ in ()).throw(RuntimeError("close uncertain"))
        with self.assertRaises(RuntimeError): mouse.run(self.args())
        self.assertEqual(self.result()["status"], "blocked")
        self.assertFalse(self.result()["connectionClosed"])

    def test_abandoned_mutex_is_not_permission_to_input(self):
        self.owner.__enter__.return_value.abandoned = True
        with self.assertRaises(mouse.native.Blocked): mouse.run(self.args())
        self.assertFalse(self.events)


if __name__ == "__main__":
    unittest.main()
