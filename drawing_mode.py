"""Air drawing mode with color and eraser support."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from utils import ensure_directory


@dataclass(slots=True)
class BrushSettings:
    color: tuple[int, int, int] = (0, 255, 0)
    thickness: int = 6
    eraser_thickness: int = 25


class DrawingCanvas:
    """In-memory drawing canvas overlaid on camera frames."""

    def __init__(self) -> None:
        self.canvas: np.ndarray | None = None
        self.prev_point: tuple[int, int] | None = None
        self.brush = BrushSettings()
        self.eraser_mode = False

    def reset(self, width: int, height: int) -> None:
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.prev_point = None

    def clear(self) -> None:
        if self.canvas is not None:
            self.canvas[:] = 0
            self.prev_point = None

    def set_color(self, color: tuple[int, int, int]) -> None:
        self.eraser_mode = False
        self.brush.color = color

    def toggle_eraser(self, enabled: bool) -> None:
        self.eraser_mode = enabled

    def draw(self, x: int, y: int) -> None:
        if self.canvas is None:
            return

        if self.prev_point is None:
            self.prev_point = (x, y)
            return

        color = (0, 0, 0) if self.eraser_mode else self.brush.color
        thickness = self.brush.eraser_thickness if self.eraser_mode else self.brush.thickness
        cv2.line(self.canvas, self.prev_point, (x, y), color, thickness)
        self.prev_point = (x, y)

    def blend(self, frame: np.ndarray) -> np.ndarray:
        if self.canvas is None:
            self.reset(frame.shape[1], frame.shape[0])
        return cv2.addWeighted(frame, 0.8, self.canvas, 0.9, 0)

    def save(self, output_dir: str = "screenshots") -> Path | None:
        if self.canvas is None:
            return None

        ensure_directory(output_dir)
        path = Path(output_dir) / f"drawing-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
        cv2.imwrite(str(path), self.canvas)
        return path
