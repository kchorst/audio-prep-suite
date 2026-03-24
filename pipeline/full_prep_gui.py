"""
pipeline/full_prep_gui.py
Full Audio Prep Pipeline — GUI frontend.

Runs: Trim → Normalize → BPM → Key → Rename → Export MP3 → CSV
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import filedialog, messagebox

from pipeline.full_prep import export_results_csv, run_pipeline
from utils.threading_tools import GuiLogger, run_in_thread


class FullPrepGui:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("Full Audio Prep Pipeline")

        self.trim_var = tk.BooleanVar(value=True)
        self.norm_var = tk.BooleanVar(value=True)
        self.mp3_var = tk.BooleanVar(value=True)
        self.csv_var = tk.BooleanVar(value=True)

        self.selected_files: list[str] = []
        self._results = []

        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self.master)
        frame.pack(padx=12, pady=10, fill="both", expand=True)

        # Options
        opts = tk.LabelFrame(frame, text="Pipeline Options", padx=8, pady=6)
        opts.pack(fill="x", pady=(0, 8))

        tk.Checkbutton(opts, text="Trim silence", variable=self.trim_var).pack(anchor="w")
        tk.Checkbutton(opts, text="Normalize audio (−14 LUFS)", variable=self.norm_var).pack(anchor="w")
        tk.Checkbutton(opts, text="Export WAV → MP3", variable=self.mp3_var).pack(anchor="w")
        tk.Checkbutton(opts, text="Export results CSV", variable=self.csv_var).pack(anchor="w")

        # Buttons
        tk.Button(frame, text="Browse Audio Files", command=self._browse).pack(pady=2, fill="x")
        self.run_btn = tk.Button(frame, text="▶  Run Full Pipeline", command=self._start_pipeline)
        self.run_btn.pack(pady=4, fill="x")

        # Log
        txt = tk.Text(frame, height=22, width=90)
        txt.pack(fill="both", expand=True)
        self.logger = GuiLogger(self.master, txt)

    def _browse(self):
        files = filedialog.askopenfilenames(
            title="Select audio files",
            filetypes=[("Audio Files", "*.wav *.mp3 *.flac *.ogg *.m4a *.aac"), ("All Files", "*.*")],
        )
        if files:
            self.selected_files = list(files)
            self.logger.clear()
            self.logger.log(f"Queued {len(files)} file(s) for processing.\n")

    def _start_pipeline(self):
        if not self.selected_files:
            messagebox.showerror("Error", "No files selected.")
            return

        self.run_btn.config(state="disabled")
        self.logger.clear()
        self.logger.log("Starting pipeline…\n")

        run_in_thread(self._run_pipeline, on_error=lambda e: self.logger.log(f"\nFatal error: {e}"))

    def _run_pipeline(self):
        results = run_pipeline(
            files=self.selected_files,
            do_trim=self.trim_var.get(),
            do_normalize=self.norm_var.get(),
            do_export_mp3=self.mp3_var.get(),
            log_fn=self.logger.log,
        )
        self._results = results
        self.master.after(0, self._finish, results)

    def _finish(self, results: list[dict]):
        ok = sum(1 for r in results if r["status"] == "ok")
        failed = len(results) - ok
        self.logger.log(f"Pipeline complete: {ok} succeeded, {failed} failed.\n")

        if self.csv_var.get() and results:
            folder = os.path.dirname(self.selected_files[0])
            try:
                csv_path = export_results_csv(results, folder)
                self.logger.log(f"CSV saved: {csv_path}")
            except Exception as e:
                self.logger.log(f"CSV export failed: {e}")

        self.run_btn.config(state="normal")

        if messagebox.askyesno("Done", f"Pipeline finished.\n{ok} ok / {failed} failed\n\nProcess more files?"):
            self.selected_files = []
            self.logger.clear()


if __name__ == "__main__":
    root = tk.Tk()
    FullPrepGui(root)
    root.mainloop()
