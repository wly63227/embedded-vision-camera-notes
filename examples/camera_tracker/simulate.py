"""Run a deliberately simple virtual camera; requires only Python."""
import argparse
import csv
from pathlib import Path
from core import Controller, clamp


def run(target_x=0.5, kp=240.0, output=None):
    controller = Controller(target_x=target_x, kp=kp)
    x, y = 0.82, 0.25
    previous_pan, previous_tilt = 1500, 1500
    rows = []
    for index in range(150):
        now = index / 15.0
        # Pulse changes move the virtual image in the opposite direction.
        # This is NOT a physical plant model or real timing measurement.
        if index:
            x = clamp(x - (command.pan_us - previous_pan) / 500, 0, 1)
            y = clamp(y - (command.tilt_us - previous_tilt) / 500, 0, 1)
            previous_pan, previous_tilt = command.pan_us, command.tilt_us
        center = None if index >= 120 else (x, y)
        command = controller.step(center, now)
        rows.append([round(now, 4), round(x, 5), round(y, 5),
                     command.error_x, command.error_y,
                     command.pan_us, command.tilt_us, command.mode])
    output = output or Path(__file__).resolve().parents[2] / "results/simulation.csv"
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["time_s", "x", "y", "error_x", "error_y", "pan_us", "tilt_us", "mode"])
        writer.writerows(rows)
    tracked = [r for r in rows if r[-1] == "TRACK"]
    print(f"Virtual only: target=({target_x:.3f}, 0.5), last tracking row={tracked[-1]}")
    print(f"Final mode={rows[-1][-1]}; saved {output}")
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-x", type=float, default=0.5)
    parser.add_argument("--kp", type=float, default=240)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    run(args.target_x, args.kp, args.output)
