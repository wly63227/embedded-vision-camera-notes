"""Dependency-free composition controller and short serial protocol.

Commands are pulses in microseconds, not measured servo angles.
"""
from dataclasses import dataclass
import math


def clamp(value, low, high):
    return max(low, min(high, value))


def finite(*values):
    return all(math.isfinite(v) for v in values)


def xor_checksum(body: str) -> int:
    value = 0
    for byte in body.encode("ascii"):
        value ^= byte
    return value


def encode_position(seq: int, pan_us: int, tilt_us: int) -> bytes:
    if not all(type(v) is int for v in (seq, pan_us, tilt_us)):
        raise ValueError("sequence and pulse values must be integers")
    if not (0 <= seq <= 65535 and 1200 <= pan_us <= 1800 and 1200 <= tilt_us <= 1800):
        raise ValueError("command out of range")
    body = f"P,{seq},{pan_us},{tilt_us}"
    return f"{body},{xor_checksum(body):02X}\n".encode("ascii")


def decode_position(frame: bytes):
    if not frame.endswith(b"\n") or len(frame) > 63:
        raise ValueError("missing newline or oversized frame")
    text = frame[:-1].decode("ascii")
    fields = text.split(",")
    if len(fields) != 5 or fields[0] != "P":
        raise ValueError("invalid fields")
    if any(not v or any(c not in "0123456789" for c in v) for v in fields[1:4]):
        raise ValueError("invalid decimal")
    check = fields[4]
    if len(check) != 2 or any(c not in "0123456789ABCDEF" for c in check):
        raise ValueError("invalid checksum format")
    values = tuple(int(v) for v in fields[1:4])
    if encode_position(*values) != frame:
        raise ValueError("checksum mismatch or noncanonical frame")
    return values


@dataclass(frozen=True)
class Command:
    pan_us: int
    tilt_us: int
    mode: str
    error_x: float | None = None
    error_y: float | None = None


class Controller:
    def __init__(self, target_x=0.5, target_y=0.5, kp=240.0,
                 deadband=0.025, max_rate=120.0, timeout=0.3,
                 pan_sign=1, tilt_sign=1):
        if not finite(target_x, target_y, kp, deadband, max_rate, timeout):
            raise ValueError("non-finite configuration")
        if not (0 <= target_x <= 1 and 0 <= target_y <= 1
                and 0 <= kp <= 2000 and 0 <= deadband < 0.5
                and 0 < max_rate <= 300 and 0 < timeout <= 0.3
                and pan_sign in (-1, 1) and tilt_sign in (-1, 1)):
            raise ValueError("invalid configuration")
        self.target = (target_x, target_y)
        self.kp, self.deadband = kp, deadband
        self.max_rate, self.timeout = max_rate, timeout
        self.signs = (pan_sign, tilt_sign)
        self.pulses = [1500.0, 1500.0]
        self.last_tick = None
        self.last_seen = None
        self.stopped = False

    def stop(self):
        self.stopped = True
        return Command(*(round(v) for v in self.pulses), "STOP")

    def step(self, center, now: float):
        if not finite(now) or (self.last_tick is not None and now < self.last_tick):
            return self.stop()
        dt = 0.0 if self.last_tick is None else min(now - self.last_tick, 0.1)
        self.last_tick = now
        # A long gap cannot be hidden by a new frame arriving after the gap.
        if self.last_seen is not None and now - self.last_seen >= self.timeout:
            self.stopped = True
        if self.stopped:
            return self.stop()
        valid = (center is not None and len(center) == 2
                 and finite(*center) and all(0 <= v <= 1 for v in center))
        if not valid:
            return Command(*(round(v) for v in self.pulses), "LOST")
        self.last_seen = now
        errors = [center[i] - self.target[i] for i in range(2)]
        for axis, error in enumerate(errors):
            rate = 0.0 if abs(error) <= self.deadband else clamp(
                self.signs[axis] * self.kp * error, -self.max_rate, self.max_rate)
            self.pulses[axis] = clamp(self.pulses[axis] + rate * dt, 1200, 1800)
        return Command(*(round(v) for v in self.pulses), "TRACK", *errors)
