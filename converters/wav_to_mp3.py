"""
converters/wav_to_mp3.py  v2.0
Batch WAV → MP3 Converter — rebuilt on BaseToolWindow.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import messagebox

from utils.base_gui import BaseToolWindow
from utils.ffmpeg_tools import export_to_mp3, normalize_audio_ffmpeg
from utils.file_tools import replace_extension
from utils.threading_tools import run_in_thread
from utils import config


class WavToMp3Gui(BaseToolWindow):
    def __init__(self):
        super().__init__(
            title="WAV → MP3 Converter",
            subtitle="Batch convert WAV files to MP3"
        )
        self._build_options()
        self._build_action_buttons()

    def _build_options(self):
        self.norm_var = ctk.BooleanVar(value=config.get("default_norm", False))
        self.trim_var = ctk.BooleanVar(value=config.get("default_trim", False))

        ctk.CTkLabel(
            self.options_frame, text="Export Options",
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        ctk.CTkCheckBox(
            self.options_frame,
            text="Normalize to −14 LUFS before export  (YouTube / streaming standard)",
            variable=self.norm_var
        ).grid(row=1, column=0, sticky="w", padx=16, pady=4)

        ctk.CTkCheckBox(
            self.options_frame,
            text="Trim silence before export",
            variable=self.trim_var
        ).grid(row=2, column=0, sticky="w", padx=16, pady=(4, 10))

    def _build_action_buttons(self):
        self.convert_btn = ctk.CTkButton(
            self.buttons_frame, text="Convert to MP3",
            command=self._start_convert
        )
        self.convert_btn.grid(row=0, column=0, padx=(0, 6), pady=8, sticky="ew")

        ctk.CTkButton(
            self.buttons_frame, text="Clear",
            fg_color="transparent", border_width=1,
            command=self._reset,
        ).grid(row=0, column=2, padx=(6, 0), pady=8, sticky="ew")

    def on_files_selected(self, files):
        self.clear_log()
        self.log(f"Loaded {len(files)} file(s) for conversion.", "info")

    def _start_convert(self):
        if not self._dropped_files:
            messagebox.showerror("No Files", "Please browse or drop WAV files first.")
            return
        self.clear_log()
        self.show_progress()
        self.set_status("Converting…")
        self.convert_btn.configure(state="disabled")
        run_in_thread(self._run_convert, on_error=self._on_error)

    def _run_convert(self):
        import tempfile, librosa, librosa.effects, soundfile as sf
        norm = self.norm_var.get()
        trim = self.trim_var.get()
        total = len(self._dropped_files)

        for i, path in enumerate(self._dropped_files, 1):
            self.set_status(f"Converting {i} of {total}…")
            try:
                src = path
                tmp_files = []

                if norm:
                    normed = tempfile.mktemp(suffix="_norm.wav")
                    normalize_audio_ffmpeg(src, normed)
                    tmp_files.append(normed)
                    src = normed

                if trim:
                    y, sr = librosa.load(src, sr=None)
                    y, _ = librosa.effects.trim(y, top_db=config.get("trim_top_db", 30))
                    trimmed = tempfile.mktemp(suffix="_trim.wav")
                    sf.write(trimmed, y, sr)
                    tmp_files.append(trimmed)
                    src = trimmed

                mp3_path = replace_extension(path, ".mp3")
                export_to_mp3(src, mp3_path, quality=config.get("mp3_quality", 2))
                self.log(f"OK  {os.path.basename(mp3_path)}", "success")

                for t in tmp_files:
                    try: os.remove(t)
                    except: pass

            except Exception as e:
                self.log(f"ERR {os.path.basename(path)}: {e}", "error")

        self.after(0, self._finish)

    def _finish(self):
        self.hide_progress()
        self.convert_btn.configure(state="normal")
        self.set_status("Conversion complete")
        self.log(f"\n{'─'*48}", "info")
        messagebox.showinfo("Done", "Conversion complete.")

    def _on_error(self, e):
        self.hide_progress()
        self.convert_btn.configure(state="normal")
        self.log(f"Error: {e}", "error")
        self.set_status("Error — see log")

    def _reset(self):
        self._dropped_files = []
        self._drop_label.configure(text="Drop audio files here  |  or Browse")
        self.clear_log()
        self.set_status("Ready")


if __name__ == "__main__":
    app = WavToMp3Gui()
    app.mainloop()
