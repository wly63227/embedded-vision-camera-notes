from pathlib import Path
import sys
import unittest

EXAMPLES = Path(__file__).resolve().parents[1] / "examples/camera_tracker"
sys.path.insert(0, str(EXAMPLES))
from core import Controller, encode_position, decode_position
from simulate import run


class ProtocolTests(unittest.TestCase):
    def test_roundtrip_and_corruption(self):
        frame = encode_position(65535, 1200, 1800)
        self.assertEqual(decode_position(frame), (65535, 1200, 1800))
        with self.assertRaises(ValueError):
            decode_position(frame.replace(b"1200", b"1300"))

    def test_invalid_input(self):
        for values in ((-1, 1500, 1500), (0, 1900, 1500), (0, 1500.5, 1500)):
            with self.assertRaises(ValueError):
                encode_position(*values)
        for frame in (b"P,0,1500,1500,00", b"P,0,1500,1500,00\r\n", b"P,0,1500,1500,zz\n"):
            with self.assertRaises(ValueError):
                decode_position(frame)


class ControlTests(unittest.TestCase):
    def test_deadband_and_rate_limit(self):
        c = Controller()
        c.step((0.51, 0.5), 0)
        self.assertEqual(c.step((0.51, 0.5), .05).pan_us, 1500)
        cmd = c.step((1, 0), .1)
        self.assertEqual((cmd.pan_us, cmd.tilt_us), (1506, 1494))

    def test_limits_and_sign(self):
        c = Controller(pan_sign=-1)
        for index in range(200):
            cmd = c.step((1, 0), index / 15)
        self.assertEqual((cmd.pan_us, cmd.tilt_us), (1200, 1200))

    def test_target_loss_latches_stop(self):
        c = Controller()
        c.step((.8, .5), 0)
        self.assertEqual(c.step(None, .1).mode, "LOST")
        self.assertEqual(c.step(None, .31).mode, "STOP")
        self.assertEqual(c.step((.5, .5), .32).mode, "STOP")

    def test_stale_recovery_cannot_hide_gap(self):
        c = Controller()
        c.step((.8, .5), 1)
        self.assertEqual(c.step((.8, .5), 2).mode, "STOP")

    def test_nonfinite_and_backwards_clock(self):
        c = Controller()
        self.assertEqual(c.step((float("nan"), .5), 0).mode, "LOST")
        c.step((.8, .5), 1)
        self.assertEqual(c.step((.8, .5), .9).mode, "STOP")

    def test_simulation_tracks_then_stops(self):
        output = EXAMPLES.parents[1] / "build/test-simulation.csv"
        rows = run(1/3, output=output)
        tracked = [r for r in rows if r[-1] == "TRACK"]
        self.assertLess(abs(tracked[-1][3]), .05)
        self.assertLess(abs(tracked[-1][4]), .05)
        self.assertEqual(rows[-1][-1], "STOP")


if __name__ == "__main__":
    unittest.main()
