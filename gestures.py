"""Gesture definitions and recognition heuristics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

import numpy as np


class Gesture(StrEnum):
    CURSOR = "Cursor"
    LEFT_CLICK = "Left Click"
    RIGHT_CLICK = "Right Click"
    DOUBLE_CLICK = "Double Click"
    DRAG = "Drag"
    SCROLL = "Scroll"
    VOLUME = "Volume"
    BRIGHTNESS = "Brightness"
    SCREENSHOT = "Screenshot"
    DRAWING = "Drawing"
    KEYBOARD = "Keyboard"
    PRESENTATION = "Presentation"
    MEDIA = "Media"
    PAUSE = "Pause System"
    NONE = "None"


FINGER_TIPS = (4, 8, 12, 16, 20)
FINGER_PIPS = (3, 6, 10, 14, 18)


@dataclass(slots=True)
class GestureThresholds:
    pinch: float = 0.035
    open_hand_y_margin: float = 0.01


class GestureRecognizer:
    """Lightweight rule-based gesture classifier over hand landmarks."""

    def __init__(self, thresholds: GestureThresholds | None = None) -> None:
        self.thresholds = thresholds or GestureThresholds()

    def _distance(self, landmarks: np.ndarray, a: int, b: int) -> float:
        return float(np.linalg.norm(landmarks[a, :2] - landmarks[b, :2]))

    def _fingers_up(self, landmarks: np.ndarray, handedness: str) -> list[bool]:
        fingers = []
        thumb_tip, thumb_ip = landmarks[FINGER_TIPS[0]], landmarks[FINGER_PIPS[0]]
        if handedness.lower() == "right":
            fingers.append(thumb_tip[0] > thumb_ip[0])
        else:
            fingers.append(thumb_tip[0] < thumb_ip[0])

        for tip, pip in zip(FINGER_TIPS[1:], FINGER_PIPS[1:]):
            fingers.append(landmarks[tip][1] < landmarks[pip][1])
        return fingers

    def recognize(self, landmarks: np.ndarray, handedness: str, active_mode: Gesture = Gesture.NONE) -> Gesture:
        """Classify a gesture from one hand using geometric constraints."""

        fingers = self._fingers_up(landmarks, handedness)
        thumb_index = self._distance(landmarks, 4, 8)
        thumb_middle = self._distance(landmarks, 4, 12)
        thumb_pinky = self._distance(landmarks, 4, 20)

        if all(not state for state in fingers):
            return Gesture.PAUSE
        if fingers == [False, True, False, False, False]:
            return Gesture.CURSOR
        if fingers == [False, True, True, False, False]:
            return Gesture.DRAG
        if thumb_index < self.thresholds.pinch and fingers[2] is False:
            return Gesture.LEFT_CLICK
        if thumb_middle < self.thresholds.pinch and fingers[1] and fingers[2]:
            return Gesture.RIGHT_CLICK
        if thumb_index < self.thresholds.pinch and thumb_middle < self.thresholds.pinch:
            return Gesture.DOUBLE_CLICK
        if fingers[1] and fingers[2] and fingers[3] and not fingers[4]:
            return Gesture.SCROLL
        if fingers[0] and fingers[1] and not any(fingers[2:]):
            return Gesture.VOLUME
        if fingers[0] and fingers[4] and not fingers[1] and not fingers[2] and not fingers[3]:
            return Gesture.BRIGHTNESS
        if all(fingers):
            return Gesture.SCREENSHOT

        if active_mode in {Gesture.DRAWING, Gesture.KEYBOARD, Gesture.PRESENTATION, Gesture.MEDIA}:
            return active_mode
        return Gesture.NONE

    @staticmethod
    def hand_center(landmarks: np.ndarray) -> tuple[float, float]:
        """Average palm coordinates for cursor/pointer usages."""

        points: Iterable[int] = (0, 5, 9, 13, 17)
        center = landmarks[list(points), :2].mean(axis=0)
        return float(center[0]), float(center[1])
