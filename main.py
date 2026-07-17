"""Entry point for AI Virtual Mouse & Gesture Control."""

from __future__ import annotations

import argparse
from collections import deque
import threading
import time

import cv2
import numpy as np

from brightness_controller import BrightnessController
from drawing_mode import DrawingCanvas
from gestures import Gesture, GestureRecognizer
from gui import Dashboard
from hand_tracker import HandTracker
from mouse_controller import VirtualMouseController
from screenshot import ScreenshotManager
from utils import AppConfig, FPSCounter
from virtual_keyboard import VirtualKeyboard
from volume_controller import VolumeController


class CameraWorker:
    """Reads frames in a separate thread for smoother webcam processing."""

    def __init__(self, camera_index: int, width: int, height: int) -> None:
        self.capture = cv2.VideoCapture(camera_index)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self._frame: np.ndarray | None = None
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        while self._running:
            ok, frame = self.capture.read()
            if not ok:
                time.sleep(0.01)
                continue
            with self._lock:
                self._frame = frame

    def read(self) -> np.ndarray | None:
        with self._lock:
            return None if self._frame is None else self._frame.copy()

    def release(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
        self.capture.release()


class GestureControlApp:
    """Main application coordinating trackers, gestures and OS controls."""

    def __init__(self, config: AppConfig, enable_gui: bool = True) -> None:
        self.config = config
        self.enable_gui = enable_gui

        self.camera = CameraWorker(config.camera_index, config.camera_width, config.camera_height)
        self.tracker = HandTracker(max_num_hands=2)
        self.recognizer = GestureRecognizer()
        self.mouse = VirtualMouseController(config)
        self.volume = VolumeController(config.volume_sensitivity)
        self.brightness = BrightnessController(config.brightness_sensitivity)
        self.screenshots = ScreenshotManager("screenshots")
        self.canvas = DrawingCanvas()
        self.keyboard = VirtualKeyboard()

        self.dashboard = Dashboard(config) if enable_gui else None
        self.fps = FPSCounter()

        self.active_mode = Gesture.CURSOR
        self.paused = False
        self.gesture_buffer: deque[Gesture] = deque(maxlen=5)
        self.last_screenshot = 0.0

    def _set_mode_from_key(self, key: int) -> None:
        if key == ord("1"):
            self.active_mode = Gesture.CURSOR
        elif key == ord("2"):
            self.active_mode = Gesture.DRAWING
        elif key == ord("3"):
            self.active_mode = Gesture.KEYBOARD
        elif key == ord("4"):
            self.active_mode = Gesture.PRESENTATION
        elif key == ord("5"):
            self.active_mode = Gesture.MEDIA

    def _apply_media_controls(self, hands_count: int) -> None:
        if self.active_mode != Gesture.MEDIA:
            return
        # In media mode, 1 hand toggles play/pause, 2 hands skips track.
        try:
            import pyautogui
        except Exception:
            return

        if hands_count == 1:
            pyautogui.press("playpause")
        elif hands_count == 2:
            pyautogui.press("nexttrack")

    def _apply_presentation_controls(self, primary_landmarks: np.ndarray) -> None:
        if self.active_mode != Gesture.PRESENTATION:
            return

        try:
            import pyautogui
        except Exception:
            return

        index_x = primary_landmarks[8][0]
        if index_x > 0.75:
            pyautogui.press("right")
        elif index_x < 0.25:
            pyautogui.press("left")

    def _display_overlay(
        self,
        frame: np.ndarray,
        gesture: Gesture,
        fps_value: float,
        hands_count: int,
        primary_handedness: str = "-",
    ) -> np.ndarray:
        cv2.putText(frame, f"Gesture: {gesture.value}", (14, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 220, 255), 2)
        cv2.putText(frame, f"Mode: {self.active_mode.value}", (14, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (120, 255, 120), 2)
        cv2.putText(frame, f"FPS: {fps_value:.1f}", (14, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"Hands: {hands_count}", (14, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        cv2.putText(frame, f"Primary: {primary_handedness}", (14, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        vol_h = self.volume.volume_bar_height(max_height=180)
        cv2.rectangle(frame, (frame.shape[1] - 60, 220), (frame.shape[1] - 30, 40), (80, 80, 80), 2)
        cv2.rectangle(frame, (frame.shape[1] - 60, 220), (frame.shape[1] - 30, 220 - vol_h), (0, 255, 0), -1)
        cv2.putText(frame, f"V:{self.volume.state.level_percent}%", (frame.shape[1] - 140, 238), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 2)
        cv2.putText(frame, f"B:{self.brightness.state.percent}%", (frame.shape[1] - 140, 262), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 2)
        return frame

    def run(self) -> None:
        self.camera.start()
        if self.dashboard is not None:
            self.dashboard.run_in_background()

        try:
            while True:
                frame = self.camera.read()
                if frame is None:
                    continue

                frame = cv2.flip(frame, 1)
                hands = self.tracker.process(frame, draw=True)
                gesture = Gesture.NONE

                if hands:
                    primary = hands[0]
                    self.recognizer.thresholds.pinch = self.config.click_threshold
                    gesture = self.recognizer.recognize(primary.landmarks, primary.handedness, self.active_mode)
                    self.gesture_buffer.append(gesture)
                    stable_gesture = max(set(self.gesture_buffer), key=self.gesture_buffer.count)

                    index_point = primary.landmarks[8]
                    x_px = int(index_point[0] * frame.shape[1])
                    y_px = int(index_point[1] * frame.shape[0])

                    if stable_gesture == Gesture.PAUSE:
                        self.paused = not self.paused
                        self.gesture_buffer.clear()
                        time.sleep(0.35)
                    if not self.paused:
                        if stable_gesture == Gesture.CURSOR:
                            self.mouse.drag(False)
                            self.mouse.move(index_point[0], index_point[1])
                        elif stable_gesture == Gesture.DRAG:
                            self.mouse.drag(True)
                            self.mouse.move(index_point[0], index_point[1])
                        elif stable_gesture == Gesture.LEFT_CLICK:
                            self.mouse.drag(False)
                            self.mouse.left_click()
                        elif stable_gesture == Gesture.RIGHT_CLICK:
                            self.mouse.drag(False)
                            self.mouse.right_click()
                        elif stable_gesture == Gesture.DOUBLE_CLICK:
                            self.mouse.drag(False)
                            self.mouse.double_click()
                        elif stable_gesture == Gesture.SCROLL:
                            self.mouse.drag(False)
                            horizontal = 180 if index_point[0] > 0.7 else -180 if index_point[0] < 0.3 else None
                            self.mouse.scroll(delta=250 if index_point[1] < 0.4 else -250, horizontal=horizontal)
                        elif stable_gesture == Gesture.VOLUME:
                            dist = float(np.linalg.norm(primary.landmarks[4, :2] - primary.landmarks[8, :2]))
                            self.volume.set_from_distance(dist)
                        elif stable_gesture == Gesture.BRIGHTNESS:
                            dist = float(np.linalg.norm(primary.landmarks[4, :2] - primary.landmarks[20, :2]))
                            self.brightness.set_from_distance(dist)
                        elif stable_gesture == Gesture.SCREENSHOT and time.monotonic() - self.last_screenshot > 1.0:
                            self.screenshots.capture()
                            self.last_screenshot = time.monotonic()

                        if self.active_mode == Gesture.DRAWING:
                            self.canvas.draw(x_px, y_px)
                        elif self.active_mode == Gesture.KEYBOARD:
                            self.keyboard.press_if_hit(x_px, y_px)

                        self._apply_presentation_controls(primary.landmarks)
                        self._apply_media_controls(len(hands))
                else:
                    self.mouse.drag(False)

                if self.active_mode == Gesture.DRAWING:
                    frame = self.canvas.blend(frame)
                elif self.active_mode == Gesture.KEYBOARD:
                    self.keyboard.draw(frame)

                fps_value = self.fps.update()
                primary_handedness = hands[0].handedness if hands else "-"
                frame = self._display_overlay(frame, gesture, fps_value, len(hands), primary_handedness)

                if self.dashboard is not None:
                    self.dashboard.update_status(gesture.value, self.active_mode.value, fps_value)

                cv2.imshow("AI Virtual Mouse & Gesture Control", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                if key == ord("c"):
                    self.canvas.clear()
                if key == ord("s"):
                    self.canvas.save("screenshots")
                self._set_mode_from_key(key)

        finally:
            self.tracker.close()
            self.camera.release()
            cv2.destroyAllWindows()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Virtual Mouse & Gesture Control")
    parser.add_argument("--camera-index", type=int, default=0, help="Webcam index")
    parser.add_argument("--camera-width", type=int, default=1280, help="Camera width")
    parser.add_argument("--camera-height", type=int, default=720, help="Camera height")
    parser.add_argument("--no-gui", action="store_true", help="Disable tkinter dashboard")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = AppConfig(
        camera_index=args.camera_index,
        camera_width=args.camera_width,
        camera_height=args.camera_height,
    )

    app = GestureControlApp(config=config, enable_gui=not args.no_gui)
    app.run()


if __name__ == "__main__":
    main()
