"""Tkinter dashboard for live status and settings controls."""

from __future__ import annotations

from dataclasses import asdict
import threading
import tkinter as tk
from tkinter import ttk
from typing import Any

from utils import AppConfig


class Dashboard:
    """Dark-themed settings dashboard updated by the main application."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.root = tk.Tk()
        self.root.title("AI Virtual Mouse & Gesture Control")
        self.root.configure(bg="#1e1e1e")
        self.root.geometry("460x420")

        self.current_gesture = tk.StringVar(value="None")
        self.current_mode = tk.StringVar(value="Cursor")
        self.current_fps = tk.StringVar(value="0.0")

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TLabel", background="#1e1e1e", foreground="#f1f1f1")

        self._build_header()
        self._build_status()
        self._build_settings()

    def _build_header(self) -> None:
        ttk.Label(self.root, text="AI Virtual Mouse & Gesture Control", font=("Segoe UI", 13, "bold")).pack(pady=(16, 10))

    def _build_status(self) -> None:
        panel = tk.Frame(self.root, bg="#2a2a2a")
        panel.pack(fill="x", padx=12, pady=6)

        ttk.Label(panel, text="Current Gesture:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Label(panel, textvariable=self.current_gesture).grid(row=0, column=1, sticky="w", padx=8)

        ttk.Label(panel, text="Active Mode:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        ttk.Label(panel, textvariable=self.current_mode).grid(row=1, column=1, sticky="w", padx=8)

        ttk.Label(panel, text="FPS:").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        ttk.Label(panel, textvariable=self.current_fps).grid(row=2, column=1, sticky="w", padx=8)

    def _build_settings(self) -> None:
        self.controls: dict[str, tk.DoubleVar] = {
            "cursor_speed": tk.DoubleVar(value=self.config.cursor_speed),
            "click_threshold": tk.DoubleVar(value=self.config.click_threshold),
            "smoothening": tk.DoubleVar(value=self.config.smoothening),
            "brightness_sensitivity": tk.DoubleVar(value=self.config.brightness_sensitivity),
            "volume_sensitivity": tk.DoubleVar(value=self.config.volume_sensitivity),
        }

        panel = tk.Frame(self.root, bg="#2a2a2a")
        panel.pack(fill="x", padx=12, pady=6)

        row = 0
        for key, variable in self.controls.items():
            ttk.Label(panel, text=key.replace("_", " ").title()).grid(row=row, column=0, sticky="w", padx=8, pady=5)
            tk.Scale(
                panel,
                from_=0.01 if "threshold" in key else 0.1,
                to=10.0 if key in {"cursor_speed", "smoothening"} else 250.0,
                resolution=0.01,
                orient="horizontal",
                variable=variable,
                bg="#2a2a2a",
                fg="#f1f1f1",
                troughcolor="#444",
                highlightthickness=0,
                command=lambda _value, setting=key: self._apply_setting(setting),
            ).grid(row=row, column=1, sticky="ew", padx=8, pady=5)
            row += 1

        self.mouse_acceleration = tk.BooleanVar(value=self.config.mouse_acceleration)
        tk.Checkbutton(
            panel,
            text="Mouse Acceleration",
            variable=self.mouse_acceleration,
            bg="#2a2a2a",
            fg="#f1f1f1",
            selectcolor="#111",
            command=self._apply_mouse_acceleration,
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=8, pady=8)

    def _apply_setting(self, setting: str) -> None:
        setattr(self.config, setting, float(self.controls[setting].get()))

    def _apply_mouse_acceleration(self) -> None:
        self.config.mouse_acceleration = bool(self.mouse_acceleration.get())

    def update_status(self, gesture: str, mode: str, fps: float) -> None:
        self.current_gesture.set(gesture)
        self.current_mode.set(mode)
        self.current_fps.set(f"{fps:.1f}")

    def run_in_background(self) -> threading.Thread:
        """Run tkinter main loop in daemon thread so camera loop stays responsive."""

        thread = threading.Thread(target=self.root.mainloop, daemon=True)
        thread.start()
        return thread

    def settings_snapshot(self) -> dict[str, Any]:
        """Expose current settings for telemetry or persistence."""

        return asdict(self.config)
