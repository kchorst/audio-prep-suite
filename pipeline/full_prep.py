"""
pipeline/full_prep.py
Full Audio Prep Pipeline — core logic (no GUI).

Fixes:
  - All temp files use mkstemp + os.close() so Windows never gets WinError 32
  - Temp files tracked in a list and cleaned up in finally block
  - ffmpeg console window suppressed
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
import soundfile as sf

from utils.audio_tools import detect_key
from utils.ffmpeg_tools import decode_to_wav, export_to_mp3, normalize_audio_ffmpeg
from utils.file_tools import append_tag_to_filename, replace_extension, safe_rename, export_csv


def _make_temp_wav() -> str:
    """Create a closed temp WAV file path safe for Windows."""
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    return path


def _cleanup(paths: list[str]):
    """Delete a list of temp files, ignoring errors."""
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
        except Exception:
            pass


def run_pipeline(
    files: list[str],
    do_trim: bool = True,
    do_normalize: bool = True,
    do_export_mp3: bool = True,
    log_fn=print,
) -> list[dict]:
    results = []

    for path in files:
        result = {
            "original":   os.path.basename(path),
            "final_path": path,
            "bpm":        None,
            "key":        None,
            "camelot":    None,
            "mp3_path":   None,
            "status":     "ok",
        }

        temp_files = []   # all temps tracked here for guaranteed cleanup

        try:
            log_fn(f"Processing: {os.path.basename(path)}")

            # ── Decode to WAV if needed ──────────────────────────
            wav_path, is_temp = decode_to_wav(path)
            if is_temp:
                temp_files.append(wav_path)
            work_path = wav_path

            # ── Trim silence ─────────────────────────────────────
            if do_trim:
                import librosa, librosa.effects
                import numpy as np
                y, sr = librosa.load(work_path, sr=44100)
                y, _ = librosa.effects.trim(y, top_db=30)
                trimmed = _make_temp_wav()
                temp_files.append(trimmed)
                sf.write(trimmed, y, sr)
                work_path = trimmed
                log_fn("  Trimmed silence")

            # ── Normalize ────────────────────────────────────────
            if do_normalize:
                normed = _make_temp_wav()
                temp_files.append(normed)
                normalize_audio_ffmpeg(work_path, normed)
                work_path = normed
                log_fn("  Normalized")

            # ── BPM ──────────────────────────────────────────────
            import librosa
            import numpy as np
            y, sr = librosa.load(work_path, sr=44100)
            tempos = librosa.beat.tempo(y=y, sr=sr, aggregate=None)
            bpm = int(round(float(np.median(tempos))))
            result["bpm"] = bpm
            log_fn(f"  BPM: {bpm}")

            # ── Key ───────────────────────────────────────────────
            key_info = detect_key(work_path)
            result["key"]     = f"{key_info['key']} {key_info['mode']}"
            result["camelot"] = key_info["camelot"]
            log_fn(f"  Key: {key_info['label']}")

            # ── Rename original ───────────────────────────────────
            tag = (f"BPM{bpm}_{key_info['key']}"
                   f"{key_info['mode'][0].upper()}_{key_info['camelot']}")
            new_path   = append_tag_to_filename(path, tag)
            final_path = safe_rename(path, new_path)
            result["final_path"] = final_path
            log_fn(f"  Renamed: {os.path.basename(final_path)}")

            # ── Export MP3 ────────────────────────────────────────
            if do_export_mp3:
                mp3_path = replace_extension(final_path, ".mp3")
                export_to_mp3(work_path, mp3_path)
                result["mp3_path"] = os.path.basename(mp3_path)
                log_fn(f"  MP3: {os.path.basename(mp3_path)}")

        except Exception as e:
            result["status"] = f"ERROR: {e}"
            log_fn(f"  Failed: {e}")

        finally:
            _cleanup(temp_files)

        results.append(result)
        log_fn("")

    return results


def export_results_csv(results: list[dict], output_folder: str) -> str:
    csv_path = os.path.join(output_folder, "audio_prep_results.csv")
    export_csv(results, csv_path)
    return csv_path
