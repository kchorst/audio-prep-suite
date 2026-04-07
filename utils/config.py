"""
utils/config.py
Persistent settings — saved to config.json in the project root.
All tools read/write through this module.
"""

import os
import json

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

_DEFAULTS = {
    "theme":           "system",
    "accent":          "blue",
    "last_folder":     "",
    "tools_path":      "",
    "audio_path":      "",
    "images_path":     "",
    "default_trim":    False,
    "default_norm":    False,
    "default_mp3":     True,
    "default_csv":     True,
    "mp3_quality":     2,
    "trim_top_db":     30,
}

_cache = {}


def load():
    global _cache
    if os.path.isfile(_CONFIG_PATH):
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                _cache = {**_DEFAULTS, **json.load(f)}
            return
        except Exception:
            pass
    _cache = dict(_DEFAULTS)


def save():
    try:
        with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(_cache, f, indent=2)
    except Exception as e:
        print(f"Config save error: {e}")


def get(key, fallback=None):
    if not _cache:
        load()
    return _cache.get(key, _DEFAULTS.get(key, fallback))


def set(key, value):
    if not _cache:
        load()
    _cache[key] = value
    save()


# Load on import
load()
