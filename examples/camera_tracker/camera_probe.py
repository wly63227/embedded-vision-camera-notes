"""Read camera properties. Optional exposure write has driver-specific units."""
import argparse
import json


def main():
    import cv2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--set-exposure", type=float,
                        help="only use a value confirmed for your device/backend")
    args = parser.parse_args()
    cap = cv2.VideoCapture(args.camera)
    try:
        if not cap.isOpened():
            raise RuntimeError("Camera unavailable")
        result = {"backend": cap.getBackendName()}
        for name in ("FRAME_WIDTH", "FRAME_HEIGHT", "FPS", "AUTO_EXPOSURE", "EXPOSURE", "GAIN", "FOCUS"):
            result[name] = cap.get(getattr(cv2, "CAP_PROP_" + name))
        if args.set_exposure is not None:
            result["exposure_request"] = args.set_exposure
            result["set_returned"] = bool(cap.set(cv2.CAP_PROP_EXPOSURE, args.set_exposure))
            for _ in range(10):
                cap.read()
            result["exposure_readback"] = cap.get(cv2.CAP_PROP_EXPOSURE)
        print(json.dumps(result, indent=2))
        print("Units and automatic mode are backend-specific; readback alone is not proof of sensor exposure.")
    finally:
        cap.release()


if __name__ == "__main__":
    main()
