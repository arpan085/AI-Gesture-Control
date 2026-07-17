"""System volume control using hand pinch distance."""

from __future__ import annotations

import platform
from dataclasses import dataclass

import numpy as np

from utils import clamp


@dataclass(slots=True)
class VolumeState:
    level_percent: int = 50


class VolumeController:
    """Cross-platform volume abstraction with pycaw support on Windows."""

    def __init__(self, sensitivity: float = 180.0) -> None:
        self.sensitivity = sensitivity
        self.state = VolumeState()
        self._volume = None

        if platform.system() == "Windows":
            try:
                from comtypes import CLSCTX_ALL  # type: ignore
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore

                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self._volume = interface.QueryInterface(IAudioEndpointVolume)
            except Exception:
                self._volume = None

    def set_from_distance(self, distance: float) -> int:
        """Map normalized thumb-index distance to system volume percentage."""

        percentage = int(clamp((distance * self.sensitivity), 0, 100))
        self.state.level_percent = percentage

        if self._volume is not None:
            vol = percentage / 100.0
            self._volume.SetMasterVolumeLevelScalar(vol, None)
        return percentage

    def volume_bar_height(self, max_height: int = 220) -> int:
        """Return an animated bar height for UI overlays."""

        return int(np.interp(self.state.level_percent, [0, 100], [0, max_height]))
