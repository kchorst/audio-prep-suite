"""
bpm_tool/bpm_gui.py  v2.0
Batch BPM Analyzer — rebuilt on BaseToolWindow (customtkinter).
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import messagebox
import subprocess

# Handle librosa import with fallback for missing dependencies
try:
    import librosa
    LIBROSA_AVAILABLE = True
    LIBROSA_ERROR = None
except ImportError as e:
    print(f"Warning: librosa not available: {e}")
    LIBROSA_AVAILABLE = False
    LIBROSA_ERROR = str(e)
    librosa = None

from utils.base_gui import BaseToolWindow
from utils.audio_tools import analyze_bpm
from utils.ffmpeg_tools import export_to_mp3
from utils.file_tools import append_tag_to_filename, replace_extension, safe_rename
from utils.threading_tools import run_in_thread
from utils import config


class BPMGui(BaseToolWindow):
    def __init__(self):
        if not LIBROSA_AVAILABLE:
            messagebox.showerror(
                "Dependency Missing",
                "librosa is not available.\n\n"
                "Please install dependencies with:\n"
                "pip install librosa setuptools\n\n"
                "Error: " + (LIBROSA_ERROR or 'Unknown error')
            )
            return
            
        super().__init__(
            title="BPM Analyzer",
            subtitle="Detect BPM across a batch of audio files"
        )
        self.results: list[list] = []
        self._build_options()
        self._build_action_buttons()

    def _build_options(self):
        self.trim_var = ctk.BooleanVar(value=config.get("default_trim", False))
        self.norm_var = ctk.BooleanVar(value=config.get("default_norm", False))

        ctk.CTkLabel(
            self.options_frame, text="Processing Options",
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        ctk.CTkCheckBox(
            self.options_frame,
            text="Trim silence before analysis",
            variable=self.trim_var
        ).grid(row=1, column=0, sticky="w", padx=16, pady=4)

        ctk.CTkCheckBox(
            self.options_frame,
            text="Normalize audio before analysis",
            variable=self.norm_var
        ).grid(row=2, column=0, sticky="w", padx=16, pady=(4, 10))

    def _build_action_buttons(self):
        self.analyze_btn = ctk.CTkButton(
            self.buttons_frame, text="Analyze BPM",
            command=self._start_analysis
        )
        self.analyze_btn.grid(row=0, column=0, padx=(0, 6), pady=8, sticky="ew")

        self.save_btn = ctk.CTkButton(
            self.buttons_frame, text="Save BPM and Export",
            state="disabled",
            command=self._save_bpm,
            fg_color=("gray75", "gray30"),
        )
        self.save_btn.grid(row=0, column=1, padx=6, pady=8, sticky="ew")

        ctk.CTkButton(
            self.buttons_frame, text="Clear",
            fg_color="transparent",
            border_width=1,
            command=self._reset,
        ).grid(row=0, column=2, padx=(6, 0), pady=8, sticky="ew")

    # ── File selection callback ──────────────────────────────────
    def on_files_selected(self, files):
        self.results = []
        self.save_btn.configure(state="disabled", fg_color=("gray75", "gray30"))
        self.clear_log()
        self.log(f"Loaded {len(files)} file(s):", "info")
        for f in files:
            self.log(f"  {os.path.basename(f)}", "info")

    # ── Analysis ─────────────────────────────────────────────────
    def _start_analysis(self):
        if not self._dropped_files:
            messagebox.showerror("No Files", "Please browse or drop audio files first.")
            return
        self.clear_log()
        self.show_progress()
        self.set_status("Analyzing…")
        self.analyze_btn.configure(state="disabled")
        run_in_thread(self._run_analysis, on_error=self._on_error)

    def _run_analysis(self):
        results = []
        total = len(self._dropped_files)
        for i, path in enumerate(self._dropped_files, 1):
            self.set_status(f"Analyzing {i} of {total}…")
            try:
                bpm = analyze_bpm(
                    path,
                    trim_silence=self.trim_var.get(),
                    normalize=self.norm_var.get(),
                )
                results.append([path, bpm])
                self.log(f"OK  {os.path.basename(path)}  ->  {bpm} BPM", "success")
            except (FileNotFoundError, RuntimeError, Exception) as e:
                self.log(f"ERR {os.path.basename(path)}  ->  {e}", "error")

        self.results = results
        self.after(0, self._finish_analysis)

    def _finish_analysis(self):
        self.hide_progress()
        self.analyze_btn.configure(state="normal")
        self.set_status(f"Done — {len(self.results)} file(s) analyzed")
        self.log(f"\n{'─'*48}", "info")
        if self.results:
            self.save_btn.configure(state="normal", fg_color=("#1f6aa5", "#1f538d"))

    def _on_error(self, e):
        self.hide_progress()
        self.analyze_btn.configure(state="normal")
        self.log(f"Unexpected error: {e}", "error")
        self.set_status("Error — see log")

    # ── Save / rename / export ───────────────────────────────────
    def _save_bpm(self):
        if not self.results:
            return

        if messagebox.askyesno("Rename Files", "Append BPM tag to filenames?"):
            for entry in self.results:
                old_path, bpm = entry
                new_path = append_tag_to_filename(old_path, f"BPM{bpm}")
                try:
                    actual = safe_rename(old_path, new_path)
                    entry[0] = actual
                    self.log(f"Renamed: {os.path.basename(old_path)} -> {os.path.basename(actual)}", "success")
                except (OSError, FileNotFoundError) as e:
                    self.log(f"Rename failed: {os.path.basename(old_path)}: {e}", "error")

        wav_results = [e for e in self.results if os.path.splitext(e[0])[1].lower() == ".wav"]
        if wav_results and messagebox.askyesno("Export MP3", "Export WAV files to MP3?"):
            for current_path, bpm in wav_results:
                mp3_path = replace_extension(current_path, ".mp3")
                try:
                    export_to_mp3(current_path, mp3_path, quality=config.get("mp3_quality", 2))
                    self.log(f"Exported: {os.path.basename(mp3_path)}", "success")
                except RuntimeError as e:
                    self.log(f"MP3 export failed: {os.path.basename(current_path)}: {e}", "error")

        if messagebox.askyesno("More Files", "Analyze more files?"):
            self._reset()
        else:
            self.quit()

    def _reset(self):
        self._dropped_files = []
        self.results = []
        self.save_btn.configure(state="disabled", fg_color=("gray75", "gray30"))
        self._drop_label.configure(text="Drop audio files here  |  or Browse")
        self.clear_log()
        self.set_status("Ready")


if __name__ == "__main__":
    app = BPMGui()
    app.mainloop()
