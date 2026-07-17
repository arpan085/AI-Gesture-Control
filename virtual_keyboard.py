"""Simple on-screen virtual keyboard controlled by fingertip position."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Iterable

import cv2
try:
    import pyautogui
except Exception:  # pragma: no cover - environment dependent
    pyautogui = None


@dataclass(slots=True)
class KeyButton:
    label: str
    x: int
    y: int
    w: int
    h: int


class VirtualKeyboard:
    """Draws and handles interaction with a virtual keyboard overlay."""

    def __init__(self) -> None:
        self.keys = self._build_layout()
        self._last_press_time = 0.0

    def _build_layout(self) -> list[KeyButton]:
        rows = [
            list("QWERTYUIOP"),
            list("ASDFGHJKL"),
            list("ZXCVBNM"),
        ]
        key_w = 55
        key_h = 55
        gap = 8

        buttons: list[KeyButton] = []
        start_y = 80
        for row_idx, row in enumerate(rows):
            start_x = 40 + (len(rows[0]) - len(row)) * ((key_w + gap) // 2)
            for col_idx, ch in enumerate(row):
                buttons.append(KeyButton(ch, start_x + col_idx * (key_w + gap), start_y + row_idx * (key_h + gap), key_w, key_h))

        buttons.extend(
            [
                KeyButton("SPACE", 140, 280, 330, key_h),
                KeyButton("ENTER", 485, 280, 110, key_h),
                KeyButton("BACK", 600, 80, 110, key_h),
            ]
        )
        return buttons

    def draw(self, frame) -> None:
        for button in self.keys:
            cv2.rectangle(frame, (button.x, button.y), (button.x + button.w, button.y + button.h), (60, 60, 60), -1)
            cv2.rectangle(frame, (button.x, button.y), (button.x + button.w, button.y + button.h), (0, 220, 255), 2)
            cv2.putText(frame, button.label, (button.x + 8, button.y + button.h // 2 + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    def press_if_hit(self, x: int, y: int) -> str | None:
        now = time.monotonic()
        if now - self._last_press_time < 0.25:
            return None

        for button in self.keys:
            if button.x <= x <= button.x + button.w and button.y <= y <= button.y + button.h:
                self._last_press_time = now
                return self._type_key(button.label)
        return None

    def _type_key(self, label: str) -> str:
        if label == "SPACE":
            if pyautogui is not None:
                pyautogui.press("space")
        elif label == "ENTER":
            if pyautogui is not None:
                pyautogui.press("enter")
        elif label == "BACK":
            if pyautogui is not None:
                pyautogui.press("backspace")
        else:
            if pyautogui is not None:
                pyautogui.write(label.lower())
        return label
