"""
trimmers/trim_silence.py  v2.0
Silence Trimmer — rebuilt on BaseToolWindow.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import messagebox
import soundfile as sf

from utils.base_gui import BaseToolWindow
from utils.audio_tools import load_and_trim
from utils.file_tools import append_tag_to_filename
from utils.threading_tools import run_in_thread
from utils import config


class TrimGui(BaseToolWindow):
    def __init__(self):
        super().__init__(
            title="Silence Trimmer",
            subtitle="Trim leading and trailing silence from audio files"
        )
        self._build_options()
        self._build_action_buttons()

    def _build_options(self):
        ctk.CTkLabel(
            self.options_frame, text="Trim Settings",
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w"
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 4))

        ctk.CTkLabel(
            self.options_frame,
            text="Silence threshold (top_db):",
            anchor="w"
        ).grid(row=1, column=0, sticky="w", padx=16, pady=8)

        self.topdb_var = ctk.IntVar(value=config.get("trim_top_db", 30))
        ctk.CTkSlider(
            self.options_frame,
            from_=10, to=60,
            variable=self.topdb_var,
            number_of_steps=50,
            width=200,
        ).grid(row=1, column=1, padx=8, pady=8)

        self.topdb_label = ctk.CTkLabel(self.options_frame, text="30 dB", width=50)
        self.topdb_label.grid(row=1, column=2, padx=4, pady=8)
        self.topdb_var.trace_add("write", self._update_db_label)

        ctk.CTkLabel(
            self.options_frame,
            text="Lower = more aggressive trim.  Output saved as  _trimmed.wav  alongside originals.",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        ).grid(row=2, column=0, columnspan=3, sticky="w", padx=16, pady=(0, 10))

    def _update_db_label(self, *_):
        self.topdb_label.configure(text=f"{self.topdb_var.get()} dB")

    def _build_action_buttons(self):
        self.trim_btn = ctk.CTkButton(
            self.buttons_frame, text="Trim Silence",
            command=self._start_trim
        )
        self.trim_btn.grid(row=0, column=0, padx=(0, 6), pady=8, sticky="ew")

        ctk.CTkButton(
            self.buttons_frame, text="Clear",
            fg_color="transparent", border_width=1,
            command=self._reset,
        ).grid(row=0, column=2, padx=(6, 0), pady=8, sticky="ew")

    def on_files_selected(self, files):
        self.clear_log()
        self.log(f"Loaded {len(files)} file(s).", "info")

    def _start_trim(self):
        if not self._dropped_files:
            messagebox.showerror("No Files", "Please browse or drop audio files first.")
            return
        self.clear_log()
        self.show_progress()
        self.set_status("Trimming…")
        self.trim_btn.configure(state="disabled")
        run_in_thread(self._run_trim, on_error=self._on_error)

    def _run_trim(self):
        top_db = self.topdb_var.get()
        total = len(self._dropped_files)

        for i, path in enumerate(self._dropped_files, 1):
            self.set_status(f"Trimming {i} of {total}…")
            try:
                y, sr = load_and_trim(path, top_db=top_db)
                out_path = append_tag_to_filename(path, "trimmed")
                out_wav = os.path.splitext(out_path)[0] + ".wav"
                sf.write(out_wav, y, sr)
                self.log(f"OK  {os.path.basename(out_wav)}", "success")
            except Exception as e:
                self.log(f"ERR {os.path.basename(path)}: {e}", "error")

        self.after(0, self._finish)

    def _finish(self):
        self.hide_progress()
        self.trim_btn.configure(state="normal")
        self.set_status("Trimming complete")
        self.log(f"\n{'─'*48}", "info")
        messagebox.showinfo("Done", "Trimming complete.")

    def _on_error(self, e):
        self.hide_progress()
        self.trim_btn.configure(state="normal")
        self.log(f"Error: {e}", "error")
        self.set_status("Error — see log")

    def _reset(self):
        self._dropped_files = []
        self._drop_label.configure(text="Drop audio files here  |  or Browse")
        self.clear_log()
        self.set_status("Ready")


if __name__ == "__main__":
    app = TrimGui()
    app.mainloop()
