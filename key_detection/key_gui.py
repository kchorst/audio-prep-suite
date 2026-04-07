"""
key_detection/key_gui.py  v2.0
Key Detector — rebuilt on BaseToolWindow.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import messagebox
import librosa
import subprocess

from utils.base_gui import BaseToolWindow
from utils.audio_tools import detect_key
from utils.file_tools import append_tag_to_filename, safe_rename
from utils.threading_tools import run_in_thread


class KeyGui(BaseToolWindow):
    def __init__(self):
        super().__init__(
            title="Key Detector",
            subtitle="Detect musical key and Camelot wheel code"
        )
        self.results: list[list] = []
        self._build_options()
        self._build_action_buttons()

    def _build_options(self):
        ctk.CTkLabel(
            self.options_frame,
            text="Detects major/minor key using the Krumhansl-Schmuckler algorithm on chroma features.\n"
                 "Camelot wheel codes are included for harmonic mixing.",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w",
            justify="left",
        ).grid(row=0, column=0, sticky="w", padx=12, pady=10)

    def _build_action_buttons(self):
        self.detect_btn = ctk.CTkButton(
            self.buttons_frame, text="Detect Keys",
            command=self._start_detect
        )
        self.detect_btn.grid(row=0, column=0, padx=(0, 6), pady=8, sticky="ew")

        self.rename_btn = ctk.CTkButton(
            self.buttons_frame, text="Rename with Key",
            state="disabled",
            fg_color=("gray75", "gray30"),
            command=self._rename_files,
        )
        self.rename_btn.grid(row=0, column=1, padx=6, pady=8, sticky="ew")

        ctk.CTkButton(
            self.buttons_frame, text="Clear",
            fg_color="transparent", border_width=1,
            command=self._reset,
        ).grid(row=0, column=2, padx=(6, 0), pady=8, sticky="ew")

    def on_files_selected(self, files):
        self.results = []
        self.rename_btn.configure(state="disabled", fg_color=("gray75", "gray30"))
        self.clear_log()
        self.log(f"Loaded {len(files)} file(s).", "info")

    def _start_detect(self):
        if not self._dropped_files:
            messagebox.showerror("No Files", "Please browse or drop audio files first.")
            return
        self.clear_log()
        self.show_progress()
        self.set_status("Detecting keys…")
        self.detect_btn.configure(state="disabled")
        run_in_thread(self._run_detect, on_error=self._on_error)

    def _run_detect(self):
        results = []
        total = len(self._dropped_files)
        for i, path in enumerate(self._dropped_files, 1):
            self.set_status(f"Analyzing {i} of {total}…")
            try:
                info = detect_key(path)
                results.append([path, info])
                self.log(
                    f"OK  {os.path.basename(path)}", "success"
                )
                self.log(
                    f"    Key: {info['key']} {info['mode']}  |  Camelot: {info['camelot']}",
                    "info"
                )
            except (FileNotFoundError, RuntimeError, Exception) as e:
                self.log(f"ERR {os.path.basename(path)}: {e}", "error")

        self.results = results
        self.after(0, self._finish)

    def _finish(self):
        self.hide_progress()
        self.detect_btn.configure(state="normal")
        self.set_status(f"Done — {len(self.results)} file(s) analyzed")
        self.log(f"\n{'─'*48}", "info")
        if self.results:
            self.rename_btn.configure(state="normal", fg_color=("#1f6aa5", "#1f538d"))

    def _on_error(self, e):
        self.hide_progress()
        self.detect_btn.configure(state="normal")
        self.log(f"Error: {e}", "error")
        self.set_status("Error — see log")

    def _rename_files(self):
        if not self.results:
            return
        if not messagebox.askyesno("Rename", "Append key tag to filenames?\n(e.g. track_Aminor_8A.wav)"):
            return
        for entry in self.results:
            path, info = entry
            tag = f"{info['key']}{info['mode'][0].upper()}_{info['camelot']}"
            new_path = append_tag_to_filename(path, tag)
            try:
                actual = safe_rename(path, new_path)
                entry[0] = actual
                self.log(f"Renamed: {os.path.basename(path)} -> {os.path.basename(actual)}", "success")
            except (OSError, FileNotFoundError) as e:
                self.log(f"Rename failed {os.path.basename(path)}: {e}", "error")

    def _reset(self):
        self._dropped_files = []
        self.results = []
        self.rename_btn.configure(state="disabled", fg_color=("gray75", "gray30"))
        self._drop_label.configure(text="Drop audio files here  |  or Browse")
        self.clear_log()
        self.set_status("Ready")


if __name__ == "__main__":
    app = KeyGui()
    app.mainloop()
