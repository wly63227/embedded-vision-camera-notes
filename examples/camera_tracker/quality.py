"""Image metrics and a deterministic synthetic demonstration, no camera writes."""
import argparse
import json


def assess(image):
    import cv2
    import numpy as np
    if image is None or image.size == 0:
        raise ValueError("empty image or ROI")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    median = float(np.median(gray))
    clipped = float(np.mean(gray >= 250))
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    advice = "reduce exposure" if clipped > 0.05 else "increase exposure if motion permits" if median < 70 else "keep; inspect subject"
    return {"median_gray": median, "highlight_fraction": clipped,
            "laplacian_variance": sharpness, "advice_only": advice}


def main():
    import cv2
    import numpy as np
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image")
    parser.add_argument("--roi", type=int, nargs=4, metavar=("X", "Y", "W", "H"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        result = {name: assess(np.full((80, 80, 3), value, np.uint8))
                  for name, value in (("dark", 30), ("middle", 120), ("clipped", 255))}
    else:
        if not args.image:
            parser.error("choose --image or --self-test")
        image = cv2.imdecode(np.fromfile(args.image, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("image cannot be read")
        if args.roi:
            x, y, w, h = args.roi
            ih, iw = image.shape[:2]
            if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > iw or y + h > ih:
                raise ValueError("ROI outside image")
            image = image[y:y+h, x:x+w]
        result = assess(image)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
