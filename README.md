# AI Virtual Mouse & Gesture Control

A professional, modular Python project that uses webcam hand tracking (MediaPipe) to control the computer with gestures.

## Features

- **Hand Detection**: Tracks up to 2 hands with all 21 landmarks, handedness detection, and FPS overlay.
- **Virtual Mouse**: Index finger cursor control with smoothing, speed settings, and optional acceleration.
- **Mouse Clicks**:
  - Left click: thumb + index pinch
  - Right click: thumb + middle pinch
  - Double click: thumb + index + middle pinch
  - Drag support scaffold (available in controller)
- **Scrolling**: Vertical and horizontal scrolling support.
- **Volume Control**: Thumb/index distance controls system volume, with live percentage + bar.
- **Brightness Control**: Thumb/pinky distance controls brightness percentage.
- **Air Drawing**: Draw with index finger, color/eraser support, save/clear canvas.
- **Screenshot Capture**: Gesture-triggered screenshots with timestamped file names.
- **Media Controls**: Play/Pause and next track gestures.
- **Presentation Mode**: Slide next/previous and pointer tracking.
- **Virtual Keyboard**: On-screen keyboard with letters, Space, Enter, and Backspace.
- **Pause System**: Fist gesture toggles pause/resume of gesture actions.
- **GUI Dashboard**: Dark-themed tkinter dashboard for status and settings.

## Project Structure

```text
AI-Virtual-Mouse/
├── main.py
├── requirements.txt
├── README.md
├── gestures.py
├── hand_tracker.py
├── mouse_controller.py
├── volume_controller.py
├── brightness_controller.py
├── screenshot.py
├── drawing_mode.py
├── virtual_keyboard.py
├── gui.py
├── utils.py
├── assets/
└── screenshots/
```

## Installation

1. **Clone the repo**
2. **Create a virtual environment (Python 3.12+)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Run

```bash
python main.py
```

Optional arguments:

```bash
python main.py --camera-index 0 --camera-width 1280 --camera-height 720
python main.py --no-gui
```

## Keyboard Shortcuts

- `q` → Quit
- `1` → Cursor mode
- `2` → Drawing mode
- `3` → Virtual keyboard mode
- `4` → Presentation mode
- `5` → Media mode
- `c` → Clear drawing canvas
- `s` → Save current drawing

## Gesture Guide

- **Cursor**: Index finger up
- **Left Click**: Thumb-index pinch
- **Right Click**: Thumb-middle pinch
- **Double Click**: Thumb-index-middle pinch
- **Scroll**: Index + middle + ring up
- **Volume**: Thumb + index gesture
- **Brightness**: Thumb + pinky gesture
- **Screenshot**: Open hand (all fingers up)
- **Pause/Resume**: Closed fist

## Settings Available

- Cursor speed
- Click threshold
- Smoothening
- Brightness sensitivity
- Volume sensitivity
- Mouse acceleration
- Camera selection and resolution (CLI)

## Performance Notes

- Camera capture runs in a separate thread to reduce blocking.
- FPS counter displays real-time frame rate.
- Uses smoothing to reduce cursor jitter.

## Screenshots

Add application screenshots to `/screenshots` and assets/icons to `/assets`.

## Windows 11 Compatibility

- Designed for Windows 11 gesture control workflows.
- Uses `pycaw` for native Windows volume control (when available).
- Brightness control uses `screen-brightness-control` with graceful fallback.

## Future Improvements

- Gesture customization profiles
- Voice feedback
- Face authentication gate
- AI gesture learning and recording
- Gesture analytics dashboard
- Theme switching
- Webcam recording
- Real-time performance graphs

## Disclaimer

Automation features can move the mouse and trigger system actions. Start slowly, test in a safe environment, and tune sensitivity before daily use.
