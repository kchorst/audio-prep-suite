"""
main.py
Audio Prep Suite — Main Launcher.
Opens a menu to launch any tool in the suite.
"""

import tkinter as tk
import subprocess
import sys
import os


TOOLS = [
    ("BPM Analyzer",           "bpm_tool/bpm_gui.py"),
    ("WAV → MP3 Converter",    "converters/wav_to_mp3.py"),
    ("Silence Trimmer",        "trimmers/trim_silence.py"),
    ("Key Detector",           "key_detection/key_gui.py"),
    ("Full Prep Pipeline",     "pipeline/full_prep_gui.py"),
]


class Launcher:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("Audio Prep Suite")
        master.resizable(False, False)

        tk.Label(master, text="Audio Prep Suite", font=("Helvetica", 16, "bold")).pack(pady=(16, 4))
        tk.Label(master, text="Choose a tool to launch:", font=("Helvetica", 10)).pack(pady=(0, 12))

        for label, script in TOOLS:
            tk.Button(
                master,
                text=label,
                width=30,
                command=lambda s=script: self._launch(s),
            ).pack(pady=3, padx=20)

        tk.Button(master, text="Quit", width=30, command=master.quit).pack(pady=(12, 16), padx=20)

    def _launch(self, script: str):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, script)
        subprocess.Popen([sys.executable, path], cwd=base)


if __name__ == "__main__":
    root = tk.Tk()
    Launcher(root)
    root.mainloop()
