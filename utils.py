"""Utility helpers for the AI Virtual Mouse project."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import time
from typing import Tuple


@dataclass(slots=True)
class AppConfig:
    """User-configurable runtime settings."""

    cursor_speed: float = 1.0
    click_threshold: float = 0.035
    smoothening: float = 5.0
    brightness_sensitivity: float = 180.0
    volume_sensitivity: float = 180.0
    camera_width: int = 1280
    camera_height: int = 720
    camera_index: int = 0
    mouse_acceleration: bool = False


class FPSCounter:
    """Tracks camera frames-per-second using rolling updates."""

    def __init__(self) -> None:
        self.prev_time = time.perf_counter()
        self.fps = 0.0

    def update(self) -> float:
        now = time.perf_counter()
        dt = now - self.prev_time
        self.prev_time = now
        if dt > 0:
            self.fps = 0.85 * self.fps + 0.15 * (1.0 / dt)
        return self.fps


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a value into a bounded range."""

    return max(minimum, min(maximum, value))


def distance_2d(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Compute Euclidean distance in 2D."""

    return math.dist(a, b)


def ensure_directory(path: str | Path) -> Path:
    """Create a directory if it does not exist and return Path."""

    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def smooth_value(current: float, target: float, smoothening: float) -> float:
    """Interpolate current value toward target for smoother motion."""

    factor = clamp(1.0 / max(1.0, smoothening), 0.01, 1.0)
    return current + (target - current) * factor
