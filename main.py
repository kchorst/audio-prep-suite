"""
main.py  v2.2
Audio Prep Suite — Launcher
- No emojis
- Compact single-column cards
- Stays open when tools launch
- Back to COT Launcher button prominent in header
"""

import os
import sys
import json
import subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from tkinter import filedialog, messagebox
from utils import config

_POPEN_FLAGS = {}
if sys.platform == "win32":
    import subprocess as _sp
    _POPEN_FLAGS["creationflags"] = _sp.CREATE_NO_WINDOW

ctk.set_appearance_mode(config.get("theme", "system"))
ctk.set_default_color_theme(config.get("accent", "blue"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

AUDIO_TOOLS = [
    ("Full Pipeline",   "pipeline/full_prep_gui.py", "Trim, Normalize, BPM, Key, Rename, MP3, CSV"),
    ("BPM Analyzer",    "bpm_tool/bpm_gui.py",       "Detect BPM, rename files, export WAV to MP3"),
    ("WAV to MP3",      "converters/wav_to_mp3.py",  "Batch convert with optional trim + normalize"),
    ("Silence Trimmer", "trimmers/trim_silence.py",  "Trim leading/trailing silence from audio files"),
    ("Key Detector",    "key_detection/key_gui.py",  "Musical key + Camelot wheel code, rename files"),
]


class Launcher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Audio Prep Suite")
        self.geometry("520x520")
        self.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Header ──────────────────────────────────────────────
        header = ctk.CTkFrame(self, corner_radius=0, height=52)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text="Audio Prep Suite",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=14)

        # COT Launcher button — prominent in header
        ctk.CTkButton(
            header, text="COT Launcher", width=110, height=30,
            command=self._open_cot_launcher,
        ).grid(row=0, column=2, padx=(6, 6), pady=10, sticky="e")

        ctk.CTkButton(
            header, text="Settings", width=80, height=30,
            fg_color="transparent", border_width=1,
            command=self._open_settings,
        ).grid(row=0, column=3, padx=(0, 10), pady=10, sticky="e")

        # ── Tool cards ──────────────────────────────────────────
        cards = ctk.CTkScrollableFrame(self, fg_color="transparent")
        cards.grid(row=1, column=0, sticky="nsew", padx=14, pady=10)
        cards.grid_columnconfigure(0, weight=1)

        for label, script, desc in AUDIO_TOOLS:
            self._make_card(cards, label, desc,
                            on_launch=lambda s=script: self._launch(s))

        # ── Footer ──────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="Audio Prep Suite v2.2  |  github.com/kchorst/audio-prep-suite",
            font=ctk.CTkFont(size=10), text_color="gray",
        ).grid(row=2, column=0, pady=(0, 10))

    def _make_card(self, parent, label, desc, on_launch):
        card = ctk.CTkFrame(parent, corner_radius=8)
        card.pack(fill="x", pady=3)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=label,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     anchor="w"
                     ).grid(row=0, column=0, sticky="w", padx=12, pady=(7, 1))
        ctk.CTkLabel(card, text=desc,
                     font=ctk.CTkFont(size=10), text_color="gray",
                     anchor="w"
                     ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 7))
        ctk.CTkButton(card, text="Launch", width=72, height=28,
                      font=ctk.CTkFont(size=11),
                      command=on_launch,
                      ).grid(row=0, column=1, rowspan=2, padx=12, pady=8)

    def _launch(self, script: str):
        """Launch a tool — keep launcher open."""
        path = os.path.join(BASE_DIR, script)
        if not os.path.isfile(path):
            messagebox.showerror("Not found", f"Script not found:\n{path}")
            return
        subprocess.Popen([sys.executable, path], cwd=BASE_DIR, **_POPEN_FLAGS)

    def _open_cot_launcher(self):
        """Find and open master_launcher.py."""
        candidates = [
            os.path.join(os.path.expanduser("~"), "Desktop", "COTTools", "master_launcher.py"),
            os.path.join("C:\\Users\\kchor\\Desktop\\COTTools", "master_launcher.py"),
            os.path.join(os.path.expanduser("~"), "Pictures", "master_launcher.py"),
        ]
        # Check saved path
        saved_cfg = os.path.join(BASE_DIR, "master_config.json")
        if os.path.isfile(saved_cfg):
            try:
                with open(saved_cfg) as f:
                    data = json.load(f)
                saved = data.get("cot_launcher_path", "")
                if saved and os.path.isfile(saved):
                    candidates.insert(0, saved)
            except Exception:
                pass

        for path in candidates:
            if os.path.isfile(path):
                subprocess.Popen([sys.executable, path],
                                  cwd=os.path.dirname(path))
                return

        # Ask user
        messagebox.showinfo("Locate COT Launcher",
                            "Could not find master_launcher.py.\n"
                            "Please browse to it.")
        path = filedialog.askopenfilename(
            title="Select master_launcher.py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
        )
        if path and os.path.isfile(path):
            try:
                with open(saved_cfg, "w") as f:
                    json.dump({"cot_launcher_path": path}, f)
            except Exception:
                pass
            subprocess.Popen([sys.executable, path],
                              cwd=os.path.dirname(path))

    def _open_settings(self):
        from utils.base_gui import SettingsWindow
        SettingsWindow(self)


if __name__ == "__main__":
    app = Launcher()
    app.mainloop()
