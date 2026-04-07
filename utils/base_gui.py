"""
utils/base_gui.py  v2.2
Base window for all Audio Prep Suite tools.
- No emojis
- Prominent nav bar: Back to Launcher | tool title | Settings
- Fixed row layout — drop zone and buttons never overlap
- Browse button + click-on-drop-zone both trigger file dialog
- Drag and drop via tkinterdnd2 if available
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from utils import config

ctk.set_appearance_mode(config.get("theme", "system"))
ctk.set_default_color_theme(config.get("accent", "blue"))

LOG_COLORS = {
    "success": "#4CAF50",
    "error":   "#F44336",
    "info":    "#9E9E9E",
    "normal":  "",
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BaseToolWindow(ctk.CTk):
    """
    Row layout:
      0 — nav bar (Back to Launcher | title | Settings)
      1 — options_frame  (subclass fills)
      2 — drop zone + Browse button
      3 — buttons_frame  (subclass fills)
      4 — log textbox    (expands)
      5 — progress bar   (hidden until needed)
      6 — status bar
    """

    def __init__(self, title: str, subtitle: str = "",
                 width: int = 700, height: int = 640):
        super().__init__()
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.minsize(580, 500)
        self._dropped_files: list[str] = []
        self._tool_title = title
        self._build_shell(title, subtitle)
        self._setup_dnd()

    # ----------------------------------------------------------------
    # Shell
    # ----------------------------------------------------------------

    def _build_shell(self, title: str, subtitle: str):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # ── Row 0: Nav bar ───────────────────────────────────────
        nav = ctk.CTkFrame(self, corner_radius=0, height=46)
        nav.grid(row=0, column=0, sticky="ew")
        nav.grid_propagate(False)
        nav.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            nav, text="< Back to Launcher", width=140, height=30,
            fg_color="transparent", border_width=1,
            command=self._back_to_launcher,
        ).grid(row=0, column=0, padx=(10, 6), pady=8, sticky="w")

        ctk.CTkLabel(
            nav, text=title + (f"  —  {subtitle}" if subtitle else ""),
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w"
        ).grid(row=0, column=1, sticky="w", padx=4, pady=8)

        ctk.CTkButton(
            nav, text="Settings", width=80, height=30,
            fg_color="transparent", border_width=1,
            command=self._open_settings,
        ).grid(row=0, column=2, padx=(6, 10), pady=8, sticky="e")

        # ── Row 1: Options frame ─────────────────────────────────
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=1, column=0, sticky="ew", padx=14, pady=(10, 0))
        self.options_frame.grid_columnconfigure(0, weight=1)

        # ── Row 2: Drop zone + Browse ────────────────────────────
        dz = ctk.CTkFrame(self, fg_color="transparent")
        dz.grid(row=2, column=0, sticky="ew", padx=14, pady=(8, 0))
        dz.grid_columnconfigure(0, weight=1)

        self._drop_label = ctk.CTkLabel(
            dz,
            text="Drop audio files here  |  or Browse",
            font=ctk.CTkFont(size=12),
            fg_color=("gray88", "gray22"),
            corner_radius=6,
            height=40,
            cursor="hand2",
        )
        self._drop_label.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._drop_label.bind("<Button-1>", lambda e: self._on_browse())

        ctk.CTkButton(
            dz, text="Browse Files", width=120, height=40,
            command=self._on_browse,
        ).grid(row=0, column=1, sticky="e")

        # ── Row 3: Action buttons ────────────────────────────────
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.grid(row=3, column=0, sticky="ew", padx=14, pady=(8, 0))
        self.buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # ── Row 4: Log ───────────────────────────────────────────
        log_wrap = ctk.CTkFrame(self)
        log_wrap.grid(row=4, column=0, sticky="nsew", padx=14, pady=(8, 0))
        log_wrap.grid_columnconfigure(0, weight=1)
        log_wrap.grid_rowconfigure(0, weight=1)

        self._log_box = ctk.CTkTextbox(
            log_wrap,
            font=ctk.CTkFont(family="Courier New", size=11),
            wrap="word", state="disabled",
        )
        self._log_box.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        # ── Row 5: Progress bar ──────────────────────────────────
        self._progress = ctk.CTkProgressBar(self, mode="indeterminate")
        self._progress.grid(row=5, column=0, sticky="ew", padx=14, pady=(4, 0))
        self._progress.grid_remove()

        # ── Row 6: Status bar ────────────────────────────────────
        sbar = ctk.CTkFrame(self, height=26, corner_radius=0)
        sbar.grid(row=6, column=0, sticky="ew", pady=(4, 0))
        sbar.grid_propagate(False)
        sbar.grid_columnconfigure(0, weight=1)
        self._status_label = ctk.CTkLabel(
            sbar, text="Ready",
            font=ctk.CTkFont(size=10), text_color="gray", anchor="w"
        )
        self._status_label.grid(row=0, column=0, sticky="w", padx=10)

    def _setup_dnd(self):
        try:
            from tkinterdnd2 import DND_FILES
            self._drop_label.drop_target_register(DND_FILES)
            self._drop_label.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            pass

    # ----------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------

    def log(self, msg: str, kind: str = "normal"):
        self.after(0, self._append_log, msg, kind)

    def set_status(self, msg: str):
        self.after(0, self._status_label.configure, {"text": msg})

    def show_progress(self):
        self.after(0, self._progress.grid)
        self.after(0, self._progress.start)

    def hide_progress(self):
        self.after(0, self._progress.stop)
        self.after(0, self._progress.grid_remove)

    def clear_log(self):
        self.after(0, self._clear_log)

    def set_files(self, files: list[str]):
        self._dropped_files = list(files)
        n = len(files)
        self._drop_label.configure(
            text=f"{n} file{'s' if n != 1 else ''} selected  —  drop more or Browse to replace"
        )
        self.set_status(f"{n} file{'s' if n != 1 else ''} ready")
        self.on_files_selected(files)

    def on_files_selected(self, files: list[str]):
        pass

    # ----------------------------------------------------------------
    # Internal
    # ----------------------------------------------------------------

    def _append_log(self, msg: str, kind: str):
        self._log_box.configure(state="normal")
        color = LOG_COLORS.get(kind, "")
        if color:
            tag = f"tag_{kind}"
            self._log_box.tag_config(tag, foreground=color)
            self._log_box.insert("end", msg + "\n", tag)
        else:
            self._log_box.insert("end", msg + "\n")
        self._log_box.configure(state="disabled")
        self._log_box.see("end")

    def _clear_log(self):
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")

    def _on_drop(self, event):
        import re
        files = re.findall(r'\{([^}]+)\}|(\S+)', event.data)
        paths = [a or b for a, b in files]
        exts = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac"}
        valid = [p for p in paths if os.path.splitext(p)[1].lower() in exts]
        if valid:
            self.set_files(valid)
        else:
            self.log("No supported audio files in drop.", "error")

    def _on_browse(self):
        from tkinter import filedialog
        last = config.get("last_folder", "")
        files = filedialog.askopenfilenames(
            title="Select audio files",
            initialdir=last if last and os.path.isdir(last) else "/",
            filetypes=[
                ("Audio Files", "*.wav *.mp3 *.flac *.ogg *.m4a *.aac"),
                ("All Files", "*.*"),
            ],
        )
        if files:
            config.set("last_folder", os.path.dirname(files[0]))
            self.set_files(list(files))

    def _back_to_launcher(self):
        # Point to main COT launcher, not audio suite main.py
        # Main launcher is in parent directory of audio suite
        main_cot_dir = os.path.dirname(BASE_DIR)
        launcher = os.path.join(main_cot_dir, "master_launcher.py")
        if os.path.isfile(launcher):
            subprocess.Popen([sys.executable, launcher],
                             cwd=main_cot_dir, **_POPEN_FLAGS)
        self.destroy()

    def _open_settings(self):
        SettingsWindow(self)


import subprocess

_POPEN_FLAGS = {}
if sys.platform == "win32":
    _POPEN_FLAGS["creationflags"] = subprocess.CREATE_NO_WINDOW


# ----------------------------------------------------------------
# Settings window
# ----------------------------------------------------------------

def _folder_row(form, row_num, label, var, browse_title):
    """Helper: label + entry + Browse button in a form grid."""
    from tkinter import filedialog
    ctk.CTkLabel(form, text=label, anchor="w").grid(
        row=row_num, column=0, sticky="w", padx=10, pady=6)
    fr = ctk.CTkFrame(form, fg_color="transparent")
    fr.grid(row=row_num, column=1, sticky="ew", padx=10, pady=6)
    fr.grid_columnconfigure(0, weight=1)
    ctk.CTkEntry(fr, textvariable=var).grid(
        row=0, column=0, sticky="ew", padx=(0, 6))
    def _browse(v=var, t=browse_title):
        folder = filedialog.askdirectory(title=t)
        if folder:
            v.set(folder)
    ctk.CTkButton(fr, text="Browse", width=70,
                  command=_browse).grid(row=0, column=1)


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("520x440")
        self.resizable(False, False)
        self.grab_set()

        ctk.CTkLabel(self, text="Audio Prep Suite Settings",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(14, 8))

        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=20, pady=4)
        form.grid_columnconfigure(1, weight=1)

        # Folder paths
        self._tools_path  = ctk.StringVar(value=config.get("tools_path", BASE_DIR))
        self._audio_path  = ctk.StringVar(value=config.get("audio_path", ""))
        self._images_path = ctk.StringVar(value=config.get("images_path", ""))

        _folder_row(form, 0, "Audio tools folder",       self._tools_path,  "Select Audio tools folder")
        _folder_row(form, 1, "Audio files folder",       self._audio_path,  "Select Audio files folder")
        _folder_row(form, 2, "Images / Pictures folder", self._images_path, "Select Images / Pictures folder")

        # Theme
        ctk.CTkLabel(form, text="Theme", anchor="w").grid(
            row=3, column=0, sticky="w", padx=10, pady=7)
        self._theme = ctk.CTkOptionMenu(
            form, values=["system", "dark", "light"],
            command=lambda v: ctk.set_appearance_mode(v))
        self._theme.set(config.get("theme", "system"))
        self._theme.grid(row=3, column=1, padx=10, pady=7, sticky="w")

        ctk.CTkLabel(form, text="Accent color", anchor="w").grid(
            row=4, column=0, sticky="w", padx=10, pady=7)
        self._accent = ctk.CTkOptionMenu(
            form, values=["blue", "green", "dark-blue"])
        self._accent.set(config.get("accent", "blue"))
        self._accent.grid(row=4, column=1, padx=10, pady=7, sticky="w")

        ctk.CTkLabel(form, text="MP3 quality (0=best)", anchor="w").grid(
            row=5, column=0, sticky="w", padx=10, pady=7)
        self._quality = ctk.CTkOptionMenu(
            form, values=["0", "1", "2", "3", "4", "5"])
        self._quality.set(str(config.get("mp3_quality", 2)))
        self._quality.grid(row=5, column=1, padx=10, pady=7, sticky="w")

        ctk.CTkLabel(form, text="Silence threshold dB", anchor="w").grid(
            row=6, column=0, sticky="w", padx=10, pady=7)
        self._topdb = ctk.CTkEntry(form, width=60)
        self._topdb.insert(0, str(config.get("trim_top_db", 30)))
        self._topdb.grid(row=6, column=1, padx=10, pady=7, sticky="w")

        ctk.CTkButton(self, text="Save and Close",
                      command=self._save).pack(pady=14)
        ctk.CTkLabel(self, text="Theme and accent apply on next launch.",
                     font=ctk.CTkFont(size=10), text_color="gray").pack()

    def _save(self):
        from tkinter import messagebox
        for key, var, label in [
            ("tools_path",  self._tools_path,  "Audio tools"),
            ("audio_path",  self._audio_path,  "Audio files"),
            ("images_path", self._images_path, "Images"),
        ]:
            path = var.get().strip()
            if path and not os.path.isdir(path):
                messagebox.showerror("Not found", f"{label} folder not found:\n{path}")
                return
            config.set(key, path)
        config.set("theme", self._theme.get())
        config.set("accent", self._accent.get())
        config.set("mp3_quality", int(self._quality.get()))
        try:
            config.set("trim_top_db", int(self._topdb.get()))
        except ValueError:
            pass
        self.destroy()
