"""Camera composition prototype. NO MOTOR OUTPUT unless --port is supplied."""
import argparse
import csv
from pathlib import Path
import time
from core import Controller, encode_position


def load_face_cascade():
    """Load via memory so Windows paths with Chinese characters also work."""
    import cv2
    xml = Path(cv2.data.haarcascades, "haarcascade_frontalface_default.xml").read_text(encoding="utf-8")
    storage = cv2.FileStorage(xml, cv2.FILE_STORAGE_READ | cv2.FILE_STORAGE_MEMORY)
    try:
        cascade = cv2.CascadeClassifier()
        if not cascade.read(storage.getFirstTopLevelNode()) or cascade.empty():
            raise RuntimeError("OpenCV bundled face cascade missing or invalid")
        return cascade
    finally:
        storage.release()


def detect(frame, detector, cascade, min_area):
    import cv2
    h, w = frame.shape[:2]
    if detector == "face":
        faces = cascade.detectMultiScale(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                                         scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
        boxes = [(int(x), int(y), int(bw), int(bh)) for x, y, bw, bh in faces
                 if bw * bh >= min_area]
    else:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (35, 80, 50), (85, 255, 255))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) >= min_area]
    if not boxes:
        return None, None
    x, y, bw, bh = max(boxes, key=lambda b: b[2] * b[3])
    return ((x + bw / 2) / w, (y + bh / 2) / h), (x, y, bw, bh)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--port", help="actual serial port, e.g. COM5; omitted = preview only")
    parser.add_argument("--detector", choices=("green", "face"), default="green")
    parser.add_argument("--target-x", type=float, default=0.5)
    parser.add_argument("--target-y", type=float, default=0.5)
    parser.add_argument("--pan-sign", type=int, choices=(-1, 1), default=1)
    parser.add_argument("--tilt-sign", type=int, choices=(-1, 1), default=1)
    parser.add_argument("--kp", type=float, default=240)
    parser.add_argument("--max-rate", type=float, default=120)
    parser.add_argument("--min-area", type=int, default=300)
    parser.add_argument("--log", type=Path, default=Path("results/live.csv"))
    args = parser.parse_args()
    import cv2
    controller = Controller(target_x=args.target_x, target_y=args.target_y, kp=args.kp,
                            max_rate=args.max_rate, pan_sign=args.pan_sign, tilt_sign=args.tilt_sign)
    if args.min_area <= 0:
        parser.error("min-area must be positive")
    cap, link = None, None
    try:
        cap = cv2.VideoCapture(args.camera)
        if not cap.isOpened():
            raise RuntimeError("Camera unavailable; try another index or close other camera apps")
        print("Camera backend:", cap.getBackendName())
        cascade = None
        if args.detector == "face":
            cascade = load_face_cascade()
        if args.port:
            import serial
            link = serial.Serial(args.port, 115200, timeout=0.05, write_timeout=0.1)
            time.sleep(1.0)  # allow any connection-triggered board reset to settle
            link.write(b"STOP\nARM\n")
            print("MOTOR OUTPUT ENABLED. Space or q: latch STOP and exit.")
        else:
            print("PREVIEW ONLY; no serial device opened. q: exit.")
        args.log.parent.mkdir(parents=True, exist_ok=True)
        with args.log.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["time_monotonic_s", "frame", "x", "y", "target_x", "target_y",
                             "error_x", "error_y", "pan_us", "tilt_us", "mode", "sent"])
            seq, frame_index, last_tx = 0, 0, float("-inf")
            while True:
                ok, frame = cap.read()
                received_at = time.monotonic()
                if not ok:
                    raise RuntimeError("Camera read failed")
                center, box = detect(frame, args.detector, cascade, args.min_area)
                # Include processing delay in the watchdog gap check.
                now = time.monotonic()
                command = controller.step(center, now)
                if now - received_at >= 0.2:
                    command = controller.stop()
                sent = False
                if command.mode == "TRACK" and link and now - last_tx >= 1 / 15:
                    link.write(encode_position(seq, command.pan_us, command.tilt_us))
                    seq = (seq + 1) % 65536
                    last_tx, sent = now, True
                writer.writerow([now, frame_index, *(center or (None, None)),
                                 args.target_x, args.target_y, command.error_x, command.error_y,
                                 command.pan_us, command.tilt_us, command.mode, int(sent)])
                stream.flush()
                if command.mode == "STOP":
                    if link:
                        link.write(b"STOP\n")
                    print("STOP latched after stale/missing target; inspect and restart manually.")
                    break
                h, w = frame.shape[:2]
                target = (round(args.target_x * (w - 1)), round(args.target_y * (h - 1)))
                cv2.drawMarker(frame, target, (255, 200, 0), cv2.MARKER_CROSS, 20, 2)
                if box:
                    x, y, bw, bh = box
                    cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
                cv2.putText(frame, f"{command.mode} {command.pan_us}/{command.tilt_us} us",
                            (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.imshow("Composition lab - q/space stops", frame)
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27, ord(" ")):
                    controller.stop()
                    break
                frame_index += 1
    finally:
        if link is not None:
            try:
                link.write(b"STOP\n")
            except Exception:
                # Broken USB: firmware watchdog remains responsible for stopping.
                print("STOP could not be delivered; MCU watchdog must stop pulses.")
            finally:
                link.close()
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted; STOP attempted by cleanup.")
