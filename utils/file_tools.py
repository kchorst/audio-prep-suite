"""
utils/file_tools.py
File renaming, path helpers, and CSV export utilities.
"""

import os
import csv
from typing import Optional
from utils.ffmpeg_tools import SUPPORTED_EXTENSIONS


def safe_rename(old_path: str, new_path: str) -> str:
    """
    Rename a file. If new_path already exists, appends _1, _2, etc.
    Returns the actual new path used.
    """
    if old_path == new_path:
        return old_path

    if not os.path.exists(new_path):
        os.rename(old_path, new_path)
        return new_path

    base, ext = os.path.splitext(new_path)
    counter = 1
    while os.path.exists(f"{base}_{counter}{ext}"):
        counter += 1
    final_path = f"{base}_{counter}{ext}"
    os.rename(old_path, final_path)
    return final_path


def append_tag_to_filename(path: str, tag: str) -> str:
    """
    Build a new path with a tag appended before the extension.
    E.g. append_tag_to_filename('/music/track.wav', 'BPM128') → '/music/track_BPM128.wav'
    Does NOT rename the file — just returns the new path string.
    """
    folder = os.path.dirname(path)
    base = os.path.basename(path)
    name, ext = os.path.splitext(base)
    return os.path.join(folder, f"{name}_{tag}{ext}")


def replace_extension(path: str, new_ext: str) -> str:
    """
    Return a new path with the extension replaced.
    E.g. replace_extension('/music/track.wav', '.mp3') → '/music/track.mp3'
    new_ext should include the dot.
    """
    base, _ = os.path.splitext(path)
    return base + new_ext


def export_csv(rows: list[dict], output_path: str) -> str:
    """
    Export a list of dicts to a CSV file.
    Column order is taken from the keys of the first row.
    Returns output_path on success.
    """
    if not rows:
        raise ValueError("No rows to export.")

    fieldnames = list(rows[0].keys())

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def collect_audio_files(folder: str, recursive: bool = False) -> list[str]:
    """
    Collects paths to all supported audio files within a specified folder.

    Supported audio file extensions are defined in `utils.ffmpeg_tools.SUPPORTED_EXTENSIONS`.
    Files are returned as absolute paths, sorted alphabetically.

    - If `recursive` is True, the function walks through all subdirectories
      of the given `folder`.
    - If `recursive` is False, only the top-level `folder` is scanned.

    Returns an empty list if no supported files are found or if the
    specified `folder` does not exist or is inaccessible.
    """

    results = []

    if recursive:
        for root, _, files in os.walk(folder):
            for f in sorted(files):
                if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS:
                    results.append(os.path.join(root, f))
    else:
        try:
            for f in sorted(os.listdir(folder)):
                full = os.path.join(folder, f)
                if os.path.isfile(full) and os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS:
                    results.append(full)
        except OSError: # Handle cases where folder might not exist or be accessible
            return []

    return results
