"""
trimmers/trim_silence.py
Silence Trimmer — GUI frontend.
Trims leading/trailing silence from audio files and saves trimmed copies.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import soundfile as sf
import tkinter as tk
from tkinter import filedialog, messagebox

from utils.audio_tools import load_and_trim
from utils.file_tools import append_tag_to_filename
from utils.threading_tools import GuiLogger, run_in_thread


class TrimGui:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("Silence Trimmer")

        self.top_db_var = tk.IntVar(value=30)
        self.selected_files: list[str] = []

        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self.master)
        frame.pack(padx=12, pady=10, fill="both", expand=True)

        # Threshold control
        thresh_row = tk.Frame(frame)
        thresh_row.pack(anchor="w", pady=4)
        tk.Label(thresh_row, text="Silence threshold (top_db):").pack(side="left")
        tk.Spinbox(thresh_row, from_=10, to=60, textvariable=self.top_db_var, width=5).pack(side="left", padx=6)
        tk.Label(thresh_row, text="(lower = more aggressive trim)").pack(side="left")

        tk.Button(frame, text="Browse Audio Files", command=self._browse).pack(pady=(6, 2), fill="x")
        tk.Button(frame, text="Trim Silence", command=self._start_trim).pack(pady=2, fill="x")

        txt = tk.Text(frame, height=16, width=80)
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

    def _start_trim(self):
        if not self.selected_files:
            messagebox.showerror("Error", "No files selected.")
            return
        self.logger.clear()
        self.logger.log("Trimming… please wait.\n")
        run_in_thread(self._run_trim, on_error=lambda e: self.logger.log(f"Error: {e}"))

    def _run_trim(self):
        top_db = self.top_db_var.get()

        for path in self.selected_files:
            try:
                y, sr = load_and_trim(path, top_db=top_db)
                out_path = append_tag_to_filename(path, "trimmed")
                # Force WAV output for lossless storage
                out_wav = os.path.splitext(out_path)[0] + ".wav"
                sf.write(out_wav, y, sr)
                self.logger.log(f"✓  {os.path.basename(out_wav)}")
            except Exception as e:
                self.logger.log(f"✗  {os.path.basename(path)}: {e}")

        self.master.after(0, lambda: messagebox.showinfo("Done", "Trimming complete."))


if __name__ == "__main__":
    root = tk.Tk()
    TrimGui(root)
    root.mainloop()
