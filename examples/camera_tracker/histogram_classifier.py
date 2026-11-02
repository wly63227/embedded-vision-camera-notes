"""Tiny trainable pattern-recognition baseline: HSV histogram + class centroid."""
import argparse
import json
from pathlib import Path


def feature(image):
    import cv2
    import numpy as np
    if image is None or image.size == 0:
        raise ValueError("empty image")
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [18, 8], [0, 180, 0, 256]).ravel()
    return (hist / max(float(hist.sum()), 1)).astype(np.float32)


def read_image(path):
    import cv2
    import numpy as np
    image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"unreadable image: {path}")
    return image


def images(root):
    for directory in sorted(Path(root).iterdir()):
        if directory.is_dir():
            for path in sorted(directory.iterdir()):
                if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}:
                    yield directory.name, path


def train(root, model):
    import numpy as np
    grouped = {}
    for label, path in images(root):
        grouped.setdefault(label, []).append(feature(read_image(path)))
    if len(grouped) < 2:
        raise ValueError("need at least two class folders containing images")
    labels = sorted(grouped)
    centers = np.stack([np.mean(grouped[label], axis=0) for label in labels])
    Path(model).parent.mkdir(parents=True, exist_ok=True)
    np.savez(model, labels=np.array(labels), centers=centers)
    print(json.dumps({"samples": {label: len(grouped[label]) for label in labels}}, ensure_ascii=False))


def evaluate(root, model):
    import numpy as np
    with np.load(model, allow_pickle=False) as data:
        labels, centers = data["labels"].tolist(), data["centers"]
    matrix = np.zeros((len(labels), len(labels)), dtype=int)
    for label, path in images(root):
        if label not in labels:
            raise ValueError(f"test label absent from model: {label}")
        prediction = int(np.argmin(np.sum((centers - feature(read_image(path))) ** 2, axis=1)))
        matrix[labels.index(label), prediction] += 1
    total = int(matrix.sum())
    if not total:
        raise ValueError("empty test set")
    result = {"labels": labels, "confusion_rows_true_cols_predicted": matrix.tolist(),
              "accuracy": float(np.trace(matrix) / total),
              "warning": "classification only; always chooses one class, no unknown-object rejection"}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def self_test():
    import numpy as np
    colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0)]
    centers = np.stack([feature(np.full((40, 40, 3), c, np.uint8)) for c in colors])
    predictions = []
    for color in colors:
        darker = tuple(int(v * .6) for v in color)
        f = feature(np.full((25, 25, 3), darker, np.uint8))
        predictions.append(int(np.argmin(np.sum((centers - f) ** 2, axis=1))))
    if predictions != [0, 1, 2]:
        raise AssertionError(predictions)
    print("Synthetic color-centroid test passed; not a real-world accuracy estimate.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("train", "test", "self-test"))
    parser.add_argument("--data", type=Path)
    parser.add_argument("--model", type=Path, default=Path("build/histogram-model.npz"))
    args = parser.parse_args()
    if args.mode == "self-test":
        self_test()
    else:
        if not args.data:
            parser.error("--data is required")
        (train if args.mode == "train" else evaluate)(args.data, args.model)
