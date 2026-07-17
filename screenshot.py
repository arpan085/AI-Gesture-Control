"""Screenshot capture feature for gesture-triggered snapshots."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

try:
    import pyautogui
except Exception:  # pragma: no cover - environment dependent
    pyautogui = None

from utils import ensure_directory


class ScreenshotManager:
    """Saves desktop screenshots with a timestamped naming pattern."""

    def __init__(self, output_dir: str = "screenshots") -> None:
        self.output_dir: Path = ensure_directory(output_dir)

    def capture(self) -> Path:
        """Capture a screenshot and return the saved path."""

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = self.output_dir / f"screenshot-{timestamp}.png"
        if pyautogui is not None:
            pyautogui.screenshot(str(path))
        return path
