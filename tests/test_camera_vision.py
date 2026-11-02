import importlib.util
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples/camera_tracker"))
HAS_CV = importlib.util.find_spec("cv2") is not None


@unittest.skipUnless(HAS_CV, "install requirements-camera.txt for image tests")
class VisionTests(unittest.TestCase):
    def test_trainable_color_baseline(self):
        from histogram_classifier import self_test
        self_test()

    def test_synthetic_green_and_empty(self):
        import numpy as np
        from live import detect
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        self.assertEqual(detect(frame, "green", None, 300), (None, None))
        frame[60:100, 180:220] = (0, 255, 0)
        center, box = detect(frame, "green", None, 300)
        self.assertAlmostEqual(center[0], 200/320)
        self.assertAlmostEqual(center[1], 80/240)
        self.assertEqual(box, (180, 60, 40, 40))

    def test_exposure_advice_and_blur(self):
        import cv2
        import numpy as np
        from quality import assess
        self.assertIn("increase", assess(np.full((80, 80), 30, np.uint8))["advice_only"])
        self.assertIn("reduce", assess(np.full((80, 80), 255, np.uint8))["advice_only"])
        image = ((np.indices((80, 80)).sum(axis=0) // 8 % 2) * 255).astype(np.uint8)
        blur = cv2.GaussianBlur(image, (9, 9), 2)
        self.assertGreater(assess(image)["laplacian_variance"], assess(blur)["laplacian_variance"])

    def test_face_cascade_is_loadable(self):
        import cv2
        import numpy as np
        from live import detect, load_face_cascade
        cascade = load_face_cascade()
        self.assertFalse(cascade.empty())
        self.assertEqual(detect(np.zeros((240, 320, 3), np.uint8), "face", cascade, 300), (None, None))


if __name__ == "__main__":
    unittest.main()
