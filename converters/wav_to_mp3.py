"""
converters/wav_to_mp3.py
Batch WAV → MP3 converter — GUI frontend.
Supports optional normalization and silence trimming before export.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import soundfile as sf
import tkinter as tk
from tkinter import filedialog, messagebox

from utils.ffmpeg_tools import export_to_mp3, normalize_audio_ffmpeg
from utils.file_tools import replace_extension
from utils.threading_tools import GuiLogger, run_in_thread


class WavToMp3Gui:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("Batch WAV → MP3 Converter")

        self.norm_var = tk.BooleanVar(value=False)
        self.trim_var = tk.BooleanVar(value=False)
        self.selected_files: list[str] = []

        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self.master)
        frame.pack(padx=12, pady=10, fill="both", expand=True)

        tk.Checkbutton(frame, text="Normalize audio before export", variable=self.norm_var).pack(anchor="w")
        tk.Checkbutton(frame, text="Trim silence before export", variable=self.trim_var).pack(anchor="w")

        tk.Button(frame, text="Browse WAV Files", command=self._browse).pack(pady=(8, 2), fill="x")
        tk.Button(frame, text="Convert to MP3", command=self._start_convert).pack(pady=2, fill="x")

        txt = tk.Text(frame, height=16, width=80)
        txt.pack(fill="both", expand=True, pady=(6, 0))
        self.logger = GuiLogger(self.master, txt)

    def _browse(self):
        files = filedialog.askopenfilenames(
            title="Select WAV files",
            filetypes=[("WAV Files", "*.wav"), ("All Files", "*.*")],
        )
        if files:
            self.selected_files = list(files)
            self.logger.log(f"Selected {len(files)} file(s):")
            for f in self.selected_files:
                self.logger.log("  " + os.path.basename(f))
            self.logger.log("")

    def _start_convert(self):
        if not self.selected_files:
            messagebox.showerror("Error", "No files selected.")
            return

        self.logger.clear()
        self.logger.log("Converting… please wait.\n")
        run_in_thread(self._run_convert, on_error=lambda e: self.logger.log(f"Error: {e}"))

    def _run_convert(self):
        norm = self.norm_var.get()
        trim = self.trim_var.get()

        for path in self.selected_files:
            try:
                src = path

                if norm:
                    normed = replace_extension(path, "_normalized.wav")
                    normalize_audio_ffmpeg(src, normed)
                    src = normed

                if trim:
                    import tempfile, librosa, librosa.effects, soundfile as sf
                    y, sr = librosa.load(src, sr=None)
                    y, _ = librosa.effects.trim(y, top_db=30)
                    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                    sf.write(tmp.name, y, sr)
                    src = tmp.name

                mp3_path = replace_extension(path, ".mp3")
                export_to_mp3(src, mp3_path)
                self.logger.log(f"✓  {os.path.basename(mp3_path)}")

            except Exception as e:
                self.logger.log(f"✗  {os.path.basename(path)}: {e}")

        self.master.after(0, lambda: messagebox.showinfo("Done", "Conversion complete."))


if __name__ == "__main__":
    root = tk.Tk()
    WavToMp3Gui(root)
    root.mainloop()
