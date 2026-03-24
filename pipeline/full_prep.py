"""
pipeline/full_prep.py
Full Audio Prep Pipeline — core logic (no GUI).

Pipeline steps per file:
  1. Trim silence (optional)
  2. Normalize (optional)
  3. Analyze BPM
  4. Detect key
  5. Rename with BPM + key tags
  6. Export WAV → MP3 (optional)
  7. Collect results into a CSV-ready list

Use from the GUI or call run_pipeline() directly.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import soundfile as sf
import tempfile

from utils.audio_tools import analyze_bpm, detect_key, trim_silence
from utils.ffmpeg_tools import decode_to_wav, export_to_mp3, normalize_audio_ffmpeg
from utils.file_tools import append_tag_to_filename, replace_extension, safe_rename, export_csv


def run_pipeline(
    files: list[str],
    do_trim: bool = True,
    do_normalize: bool = True,
    do_export_mp3: bool = True,
    log_fn=print,
) -> list[dict]:
    """
    Run the full prep pipeline on a list of audio files.

    Parameters
    ----------
    files        : list of absolute paths to audio files
    do_trim      : trim leading/trailing silence
    do_normalize : loudness-normalize audio
    do_export_mp3: export a final MP3 alongside the renamed source
    log_fn       : callable(str) used to emit progress messages

    Returns
    -------
    List of result dicts with keys:
        original, final_path, bpm, key, camelot, mp3_path, status
    """
    results = []

    for path in files:
        result = {
            "original": os.path.basename(path),
            "final_path": path,
            "bpm": None,
            "key": None,
            "camelot": None,
            "mp3_path": None,
            "status": "ok",
        }

        try:
            log_fn(f"Processing: {os.path.basename(path)}")

            # ---- Decode to WAV working copy if needed ----
            wav_path, is_temp_wav = decode_to_wav(path)
            work_path = wav_path  # we'll chain operations on this

            # ---- Trim silence ----
            if do_trim:
                import librosa, librosa.effects, numpy as np
                y, sr = librosa.load(work_path, sr=44100)
                y, _ = librosa.effects.trim(y, top_db=30)
                tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                sf.write(tmp.name, y, sr)
                if is_temp_wav and os.path.exists(work_path):
                    os.remove(work_path)
                work_path = tmp.name
                is_temp_wav = True
                log_fn("  ✓ Trimmed silence")

            # ---- Normalize ----
            if do_normalize:
                normed = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
                normalize_audio_ffmpeg(work_path, normed)
                if is_temp_wav and os.path.exists(work_path):
                    os.remove(work_path)
                work_path = normed
                is_temp_wav = True
                log_fn("  ✓ Normalized")

            # ---- BPM ----
            import librosa, numpy as np
            y, sr = librosa.load(work_path, sr=44100)
            tempos = librosa.beat.tempo(y=y, sr=sr, aggregate=None)
            bpm = int(round(float(np.median(tempos))))
            result["bpm"] = bpm
            log_fn(f"  ✓ BPM: {bpm}")

            # ---- Key ----
            key_info = detect_key(work_path)
            result["key"] = f"{key_info['key']} {key_info['mode']}"
            result["camelot"] = key_info["camelot"]
            log_fn(f"  ✓ Key: {key_info['label']}")

            # ---- Rename original file ----
            tag = f"BPM{bpm}_{key_info['key']}{key_info['mode'][0].upper()}_{key_info['camelot']}"
            new_path = append_tag_to_filename(path, tag)
            final_path = safe_rename(path, new_path)
            result["final_path"] = final_path
            log_fn(f"  ✓ Renamed → {os.path.basename(final_path)}")

            # ---- Export MP3 ----
            if do_export_mp3:
                mp3_path = replace_extension(final_path, ".mp3")
                export_to_mp3(work_path, mp3_path)
                result["mp3_path"] = os.path.basename(mp3_path)
                log_fn(f"  ✓ Exported MP3: {os.path.basename(mp3_path)}")

            # ---- Cleanup temp WAV ----
            if is_temp_wav and os.path.exists(work_path):
                os.remove(work_path)

        except Exception as e:
            result["status"] = f"ERROR: {e}"
            log_fn(f"  ✗ Failed: {e}")

        results.append(result)
        log_fn("")

    return results


def export_results_csv(results: list[dict], output_folder: str) -> str:
    """Write pipeline results to a CSV file in output_folder."""
    csv_path = os.path.join(output_folder, "audio_prep_results.csv")
    export_csv(results, csv_path)
    return csv_path
