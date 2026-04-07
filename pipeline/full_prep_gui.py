"""
pipeline/full_prep_gui.py  v2.0
Full Audio Prep Pipeline — rebuilt on BaseToolWindow.
Trim, Normalize, BPM, Key, Rename, MP3, CSV
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import messagebox

from utils.base_gui import BaseToolWindow
from utils.threading_tools import run_in_thread
from utils import config
from pipeline.full_prep import export_results_csv, run_pipeline


class FullPrepGui(BaseToolWindow):
    def __init__(self):
        super().__init__(
            title="Full Prep Pipeline",
            subtitle="Trim, Normalize, BPM, Key, Rename, MP3, CSV",
            width=760,
            height=680,
        )
        self._results = []
        self._build_options()
        self._build_action_buttons()

    def _build_options(self):
        self.trim_var = ctk.BooleanVar(value=config.get("default_trim", True))
        self.norm_var = ctk.BooleanVar(value=config.get("default_norm", True))
        self.mp3_var  = ctk.BooleanVar(value=config.get("default_mp3", True))
        self.csv_var  = ctk.BooleanVar(value=config.get("default_csv", True))

        ctk.CTkLabel(
            self.options_frame, text="Pipeline Steps",
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w"
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(10, 6))

        checks = [
            ("Trim silence",        self.trim_var, 1),
            ("Normalize (-14 LUFS)", self.norm_var, 2),
            ("Export WAV to MP3",    self.mp3_var,  3),
            ("Export results CSV",   self.csv_var,  4),
        ]
        for text, var, col in checks:
            ctk.CTkCheckBox(
                self.options_frame, text=text, variable=var
            ).grid(row=1, column=col - 1, sticky="w", padx=12, pady=(0, 10))

        ctk.CTkLabel(
            self.options_frame,
            text="BPM detection and Key detection always run.",
            font=ctk.CTkFont(size=10), text_color="gray", anchor="w"
        ).grid(row=2, column=0, columnspan=4, sticky="w", padx=12, pady=(0, 8))

    def _build_action_buttons(self):
        self.run_btn = ctk.CTkButton(
            self.buttons_frame, text="Run Full Pipeline",
            command=self._start_pipeline,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
        )
        self.run_btn.grid(row=0, column=0, padx=(0, 6), pady=8, sticky="ew")

        ctk.CTkButton(
            self.buttons_frame, text="Clear",
            fg_color="transparent", border_width=1,
            command=self._reset,
        ).grid(row=0, column=2, padx=(6, 0), pady=8, sticky="ew")

    def on_files_selected(self, files):
        self._results = []
        self.clear_log()
        self.log(f"Queued {len(files)} file(s) for processing.", "info")

    def _start_pipeline(self):
        if not self._dropped_files:
            messagebox.showerror("No Files", "Please browse or drop audio files first.")
            return
        self.clear_log()
        self.show_progress()
        self.set_status("Pipeline running…")
        self.run_btn.configure(state="disabled")
        run_in_thread(self._run_pipeline, on_error=self._on_error)

    def _run_pipeline(self):
        results = run_pipeline(
            files=self._dropped_files,
            do_trim=self.trim_var.get(),
            do_normalize=self.norm_var.get(),
            do_export_mp3=self.mp3_var.get(),
            log_fn=self.log,
        )
        self._results = results
        self.after(0, self._finish, results)

    def _finish(self, results):
        self.hide_progress()
        self.run_btn.configure(state="normal")

        ok     = sum(1 for r in results if r["status"] == "ok")
        failed = len(results) - ok
        self.set_status(f"Pipeline complete — {ok} succeeded, {failed} failed")
        self.log(f"\n{'─'*48}", "info")
        self.log(f"{ok} succeeded   {failed} failed", "success" if failed == 0 else "error")

        if self.csv_var.get() and results:
            folder = os.path.dirname(self._dropped_files[0])
            try:
                csv_path = export_results_csv(results, folder)
                self.log(f"CSV saved: {csv_path}", "info")
            except Exception as e:
                self.log(f"CSV export failed: {e}", "error")

        if messagebox.askyesno("Done", f"Pipeline finished.\n{ok} succeeded / {failed} failed\n\nProcess more files?"):
            self._reset()

    def _on_error(self, e):
        self.hide_progress()
        self.run_btn.configure(state="normal")
        self.log(f"Fatal error: {e}", "error")
        self.set_status("Error — see log")

    def _reset(self):
        self._dropped_files = []
        self._results = []
        self._drop_label.configure(text="Drop audio files here  |  or Browse")
        self.clear_log()
        self.set_status("Ready")


if __name__ == "__main__":
    app = FullPrepGui()
    app.mainloop()
