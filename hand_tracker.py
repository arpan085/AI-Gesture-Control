"""MediaPipe based hand tracking abstraction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import cv2
import mediapipe as mp
import numpy as np


@dataclass(slots=True)
class TrackedHand:
    """Container for normalized hand landmarks and metadata."""

    landmarks: np.ndarray  # shape: (21, 3)
    handedness: str


class HandTracker:
    """Detects one or two hands and returns 21 landmarks per hand."""

    def __init__(
        self,
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.7,
    ) -> None:
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            model_complexity=1,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._drawer = mp.solutions.drawing_utils

    def process(self, frame_bgr: np.ndarray, draw: bool = True) -> List[TrackedHand]:
        """Run MediaPipe hand detection on a frame and return tracked hands."""

        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)
        if not results.multi_hand_landmarks:
            return []

        tracked_hands: List[TrackedHand] = []
        for landmarks_proto, handedness_proto in zip(
            results.multi_hand_landmarks,
            results.multi_handedness,
        ):
            if draw:
                # Draw landmarks and skeleton for visual feedback and debugging.
                self._drawer.draw_landmarks(
                    frame_bgr,
                    landmarks_proto,
                    self._mp_hands.HAND_CONNECTIONS,
                )

            landmarks = np.array(
                [(lm.x, lm.y, lm.z) for lm in landmarks_proto.landmark],
                dtype=np.float32,
            )
            tracked_hands.append(
                TrackedHand(
                    landmarks=landmarks,
                    handedness=handedness_proto.classification[0].label,
                )
            )
        return tracked_hands

    def close(self) -> None:
        """Release MediaPipe resources."""

        self._hands.close()
