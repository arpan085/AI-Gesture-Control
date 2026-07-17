"""Mouse movement and click actions controlled by gestures."""

from __future__ import annotations

import time
from typing import Optional

try:
    import pyautogui
except Exception:  # pragma: no cover - environment dependent
    pyautogui = None

from utils import AppConfig, clamp, smooth_value

if pyautogui is not None:
    pyautogui.FAILSAFE = False


class VirtualMouseController:
    """Maps normalized hand coordinates to desktop mouse actions."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        if pyautogui is not None:
            self.screen_w, self.screen_h = pyautogui.size()
        else:
            self.screen_w, self.screen_h = 1920, 1080
        self._smooth_x = self.screen_w / 2
        self._smooth_y = self.screen_h / 2
        self._drag_active = False
        self._last_double_click = 0.0

    def move(self, x_norm: float, y_norm: float) -> None:
        """Move cursor using calibrated hand position and smoothing."""

        x_target = clamp(x_norm * self.screen_w * self.config.cursor_speed, 0, self.screen_w - 1)
        y_target = clamp(y_norm * self.screen_h * self.config.cursor_speed, 0, self.screen_h - 1)

        if self.config.mouse_acceleration:
            x_target = clamp(x_target + (x_target - self._smooth_x) * 0.15, 0, self.screen_w - 1)
            y_target = clamp(y_target + (y_target - self._smooth_y) * 0.15, 0, self.screen_h - 1)

        self._smooth_x = smooth_value(self._smooth_x, x_target, self.config.smoothening)
        self._smooth_y = smooth_value(self._smooth_y, y_target, self.config.smoothening)
        if pyautogui is not None:
            pyautogui.moveTo(int(self._smooth_x), int(self._smooth_y), _pause=False)

    def left_click(self) -> None:
        if pyautogui is not None:
            pyautogui.click(button="left")

    def right_click(self) -> None:
        if pyautogui is not None:
            pyautogui.click(button="right")

    def double_click(self) -> None:
        now = time.monotonic()
        if now - self._last_double_click > 0.35:
            if pyautogui is not None:
                pyautogui.doubleClick()
            self._last_double_click = now

    def drag(self, enable: bool) -> None:
        if enable and not self._drag_active:
            if pyautogui is not None:
                pyautogui.mouseDown(button="left")
            self._drag_active = True
        elif not enable and self._drag_active:
            if pyautogui is not None:
                pyautogui.mouseUp(button="left")
            self._drag_active = False

    def scroll(self, delta: int, horizontal: Optional[int] = None) -> None:
        if pyautogui is not None:
            pyautogui.scroll(delta)
            if horizontal:
                pyautogui.hscroll(horizontal)
