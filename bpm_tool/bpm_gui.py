"""
bpm_tool/bpm_gui.py
Batch BPM Analyzer — GUI frontend.

Fix vs original bpm_picker_multi.py:
  - Rename-before-export bug fixed: paths in self.results are updated
    immediately after each rename so the subsequent WAV→MP3 export
    always has the correct on-disk path.
  - Refactored to use shared utils (ffmpeg_tools, audio_tools,
    file_tools, threading_tools).
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import filedialog, messagebox

from utils.audio_tools import analyze_bpm
from utils.ffmpeg_tools import export_to_mp3
from utils.file_tools import append_tag_to_filename, replace_extension, safe_rename
from utils.threading_tools import GuiLogger, run_in_thread


class BPMGui:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("Batch BPM Analyzer")
        master.resizable(True, True)

        self.trim_var = tk.BooleanVar(value=False)
        self.norm_var = tk.BooleanVar(value=False)

        # list of (current_path, bpm) — path is updated after rename
        self.results: list[tuple[str, int]] = []
        self.selected_files: list[str] = []

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        frame = tk.Frame(self.master)
        frame.pack(padx=12, pady=10, fill="both", expand=True)

        # Options
        tk.Checkbutton(
            frame, text="Trim silence (beginning and end)", variable=self.trim_var
        ).pack(anchor="w")
        tk.Checkbutton(
            frame, text="Normalize audio", variable=self.norm_var
        ).pack(anchor="w")

        # Buttons
        tk.Button(frame, text="Browse Files", command=self._browse_files).pack(
            pady=(8, 2), fill="x"
        )
        tk.Button(frame, text="Analyze", command=self._start_analysis).pack(
            pady=2, fill="x"
        )

        self.save_btn = tk.Button(
            frame,
            text="Save BPM  (rename + export WAV → MP3)",
            command=self._save_bpm,
            state="disabled",
        )
        self.save_btn.pack(pady=2, fill="x")

        # Log output
        txt = tk.Text(frame, height=18, width=84)
        txt.pack(fill="both", expand=True, pady=(6, 0))

        self.logger = GuiLogger(self.master, txt)

    # ------------------------------------------------------------------
    # File browsing
    # ------------------------------------------------------------------

    def _browse_files(self):
        files = filedialog.askopenfilenames(
            title="Select audio files",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a *.aac"),
                ("All Files", "*.*"),
            ],
        )
        if files:
            self.selected_files = list(files)
            self.logger.log("Files selected:")
            for f in self.selected_files:
                self.logger.log("  " + os.path.basename(f))
            self.logger.log("")

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def _start_analysis(self):
        if not self.selected_files:
            messagebox.showerror("Error", "No files selected.")
            return

        self.save_btn.config(state="disabled")
        self.logger.clear()
        self.logger.log("Analyzing… please wait.\n")

        run_in_thread(self._run_analysis, on_error=self._on_analysis_error)

    def _run_analysis(self):
        results = []
        for path in self.selected_files:
            try:
                bpm = analyze_bpm(
                    path,
                    trim_silence=self.trim_var.get(),
                    normalize=self.norm_var.get(),
                )
                results.append([path, bpm])
                self.logger.log(f"{os.path.basename(path)}  →  {bpm} BPM")
            except Exception as e:
                self.logger.log(f"{os.path.basename(path)}  →  ERROR: {e}")

        self.results = results
        self.master.after(0, self._finish_analysis)

    def _finish_analysis(self):
        self.logger.log("\n" + "=" * 44 + "\n")
        if self.results:
            self.save_btn.config(state="normal")

    def _on_analysis_error(self, e: Exception):
        self.logger.log(f"\nUnexpected error during analysis: {e}")

    # ------------------------------------------------------------------
    # Save / rename / export
    # ------------------------------------------------------------------

    def _save_bpm(self):
        if not self.results:
            return

        # --- Step 1: Rename files (append _BPMxxx) ---
        if messagebox.askyesno("Rename Files", "Append BPM to filenames?"):
            for entry in self.results:
                old_path, bpm = entry
                new_path = append_tag_to_filename(old_path, f"BPM{bpm}")
                try:
                    actual_path = safe_rename(old_path, new_path)
                    # ✅ FIX: update the stored path so export uses the new name
                    entry[0] = actual_path
                    self.logger.log(
                        f"Renamed: {os.path.basename(old_path)}  →  {os.path.basename(actual_path)}"
                    )
                except Exception as e:
                    self.logger.log(f"Could not rename {os.path.basename(old_path)}: {e}")

        # --- Step 2: Export WAV → MP3 ---
        wav_results = [e for e in self.results if os.path.splitext(e[0])[1].lower() == ".wav"]
        if wav_results and messagebox.askyesno("Export MP3", "Export WAV files to MP3?"):
            for current_path, bpm in wav_results:
                mp3_path = replace_extension(current_path, ".mp3")
                try:
                    export_to_mp3(current_path, mp3_path)
                    self.logger.log(f"Exported: {os.path.basename(mp3_path)}")
                except Exception as e:
                    self.logger.log(f"MP3 export failed for {os.path.basename(current_path)}: {e}")

        # --- Step 3: Continue or quit ---
        if messagebox.askyesno("More Files", "Analyze more audio files?"):
            self._reset()
        else:
            self.master.quit()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _reset(self):
        self.selected_files = []
        self.results = []
        self.save_btn.config(state="disabled")
        self.logger.clear()


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = BPMGui(root)
    root.mainloop()
