"""
utils/threading_tools.py
Thread-safe helpers for Tkinter GUI applications.
"""

import threading
from typing import Callable, Any


def run_in_thread(fn: Callable, *args, on_error: Callable[[Exception], None] = None, **kwargs) -> threading.Thread:
    """
    Run a function in a background daemon thread.
    Optionally calls on_error(e) if the function raises.
    Returns the started Thread.
    """
    def wrapper():
        try:
            fn(*args, **kwargs)
        except Exception as e:
            if on_error:
                on_error(e)

    t = threading.Thread(target=wrapper, daemon=True)
    t.start()
    return t


class GuiLogger:
    """
    Thread-safe logger that appends messages to a Tkinter Text widget.
    Use .log(msg) from any thread — it schedules the update on the main thread.
    """

    def __init__(self, master, text_widget):
        self.master = master
        self.text = text_widget

    def log(self, msg: str):
        self.master.after(0, self._append, msg)

    def _append(self, msg: str):
        self.text.insert("end", msg + "\n")
        self.text.see("end")

    def clear(self):
        self.master.after(0, self._clear)

    def _clear(self):
        self.text.delete("1.0", "end")


def after_main(master, fn: Callable, *args):
    """
    Schedule fn(*args) to run on the Tkinter main thread.
    """
    master.after(0, fn, *args)
