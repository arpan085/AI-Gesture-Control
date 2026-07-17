"""Screen brightness control from hand gestures."""

from __future__ import annotations

from dataclasses import dataclass

from utils import clamp


@dataclass(slots=True)
class BrightnessState:
    percent: int = 50


class BrightnessController:
    """Controls monitor brightness with graceful fallback."""

    def __init__(self, sensitivity: float = 180.0) -> None:
        self.sensitivity = sensitivity
        self.state = BrightnessState()
        try:
            import screen_brightness_control as sbc

            self._sbc = sbc
        except Exception:
            self._sbc = None

    def set_from_distance(self, distance: float) -> int:
        """Map thumb-pinky distance into screen brightness percentage."""

        value = int(clamp(distance * self.sensitivity, 0, 100))
        self.state.percent = value

        if self._sbc is not None:
            try:
                self._sbc.set_brightness(value)
            except Exception:
                pass
        return value
