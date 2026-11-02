"""Reproducible software checks; deliberately does not claim hardware validation."""
import argparse
import contextlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def command(args):
    process = subprocess.run(args, cwd=ROOT, text=True, encoding="utf-8", errors="replace",
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if process.returncode:
        raise RuntimeError(f"Command failed: {args}\n{process.stdout}")
    return process.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cc", nargs="+", default=["cc"], help="C compiler command, e.g. --cc zig cc")
    args = parser.parse_args()
    os.chdir(ROOT)
    (ROOT / "build").mkdir(exist_ok=True)
    os.environ.setdefault("ZIG_GLOBAL_CACHE_DIR", str(ROOT / "build/zig-cache"))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        result = unittest.TextTestRunner(stream=capture, verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped:
        raise RuntimeError(capture.getvalue())
    print(capture.getvalue())
    executable = ROOT / "build" / ("test_gimbal.exe" if os.name == "nt" else "test_gimbal")
    command(args.cc + ["-std=c11", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                      "-Ifirmware/stm32_gimbal", "firmware/stm32_gimbal/gimbal.c",
                      "tests/test_gimbal.c", "-o", str(executable)])
    c_output = command([str(executable)])
    simulation = command([sys.executable, "examples/camera_tracker/simulate.py"])
    versions = {name: importlib.metadata.version(name) for name in ("opencv-python", "numpy", "pyserial")}
    report = {
        "checked_date": "2026-11-02",
        "platform": platform.system(), "python": platform.python_version(), "dependencies": versions,
        "python_tests": {"passed": result.testsRun, "skipped": len(result.skipped)},
        "c_application": {"compiler_command": [Path(args.cc[0]).name, *args.cc[1:]],
                          "warnings_as_errors": True, "result": c_output},
        "simulation": {"result": simulation.splitlines()[0], "scope": "simplified_virtual_camera_only"},
        "status": "software_checks_passed",
        "hardware_validation": "not_run_no_hardware_available",
        "unverified": ["CubeIDE/HAL integration", "physical PWM/power/load/limits", "real camera performance",
                       "real camera parameter writes", "end-to-end sensor latency"],
    }
    path = ROOT / "results/validation.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    command([sys.executable, "tools/build_camera_book.py"])
    links = command([sys.executable, "tools/check_links.py"])
    report["internal_links"] = links
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    command([sys.executable, "tools/build_camera_book.py"])
    print(c_output)
    print(links)
    print("Software checks passed; hardware remains untested.")


if __name__ == "__main__":
    main()
