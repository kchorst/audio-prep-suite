"""
key_detection/key_gui.py
Musical Key Detector — GUI frontend.
Detects key + Camelot wheel code. Optionally renames files with key tag.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import filedialog, messagebox

from utils.audio_tools import detect_key
from utils.file_tools import append_tag_to_filename, safe_rename
from utils.threading_tools import GuiLogger, run_in_thread


class KeyGui:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("Key Detector")

        self.selected_files: list[str] = []
        self.results: list[list] = []  # [[path, key_dict], ...]

        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self.master)
        frame.pack(padx=12, pady=10, fill="both", expand=True)

        tk.Button(frame, text="Browse Audio Files", command=self._browse).pack(pady=(4, 2), fill="x")
        tk.Button(frame, text="Detect Key", command=self._start_detect).pack(pady=2, fill="x")

        self.rename_btn = tk.Button(
            frame,
            text="Rename Files with Key Tag",
            command=self._rename_files,
            state="disabled",
        )
        self.rename_btn.pack(pady=2, fill="x")

        txt = tk.Text(frame, height=18, width=84)
        txt.pack(fill="both", expand=True, pady=(6, 0))
        self.logger = GuiLogger(self.master, txt)

    def _browse(self):
        files = filedialog.askopenfilenames(
            title="Select audio files",
            filetypes=[("Audio Files", "*.wav *.mp3 *.flac *.ogg *.m4a *.aac"), ("All Files", "*.*")],
        )
        if files:
            self.selected_files = list(files)
            self.logger.log(f"Selected {len(files)} file(s).")

    def _start_detect(self):
        if not self.selected_files:
            messagebox.showerror("Error", "No files selected.")
            return
        self.rename_btn.config(state="disabled")
        self.logger.clear()
        self.logger.log("Detecting keys… please wait.\n")
        run_in_thread(self._run_detect, on_error=lambda e: self.logger.log(f"Error: {e}"))

    def _run_detect(self):
        results = []
        for path in self.selected_files:
            try:
                info = detect_key(path)
                results.append([path, info])
                self.logger.log(
                    f"{os.path.basename(path)}\n"
                    f"    Key: {info['key']} {info['mode']}  |  Camelot: {info['camelot']}\n"
                )
            except Exception as e:
                self.logger.log(f"✗  {os.path.basename(path)}: {e}\n")

        self.results = results
        self.master.after(0, self._finish)

    def _finish(self):
        self.logger.log("=" * 44 + "\n")
        if self.results:
            self.rename_btn.config(state="normal")

    def _rename_files(self):
        if not self.results:
            return
        if not messagebox.askyesno("Rename", "Append key tag to filenames?\n(e.g. track_Aminor_5A.wav)"):
            return

        for entry in self.results:
            path, info = entry
            tag = f"{info['key']}{info['mode'][0].upper()}_{info['camelot']}"
            new_path = append_tag_to_filename(path, tag)
            try:
                actual = safe_rename(path, new_path)
                entry[0] = actual  # keep path in sync
                self.logger.log(f"Renamed: {os.path.basename(path)}  →  {os.path.basename(actual)}")
            except Exception as e:
                self.logger.log(f"Could not rename {os.path.basename(path)}: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    KeyGui(root)
    root.mainloop()
