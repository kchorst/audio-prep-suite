"""
utils/audio_tools.py
Shared audio processing helpers: BPM, silence trimming, normalization, key detection.
"""

import os
import numpy as np
import librosa
import librosa.effects
import librosa.util

from utils.ffmpeg_tools import decode_to_wav


# -------------------------------------------------
# BPM Detection
# -------------------------------------------------

def analyze_bpm(path: str, trim_silence: bool = False, normalize: bool = False) -> int:
    """
    Analyze the BPM of an audio file.
    Decodes to WAV first if needed. Returns BPM as integer.
    """
    wav_path, is_temp = decode_to_wav(path)

    try:
        y, sr = librosa.load(wav_path, sr=44100)

        if trim_silence:
            y, _ = librosa.effects.trim(y, top_db=30)

        if normalize:
            y = librosa.util.normalize(y)

        tempos = librosa.beat.tempo(y=y, sr=sr, aggregate=None)
        bpm = int(round(float(np.median(tempos))))
    finally:
        if is_temp and os.path.exists(wav_path):
            os.remove(wav_path)

    return bpm


# -------------------------------------------------
# Silence Trimming
# -------------------------------------------------

def trim_silence(y: np.ndarray, sr: int, top_db: float = 30) -> np.ndarray:
    """
    Trim leading and trailing silence from an audio array.
    Returns trimmed audio array.
    """
    trimmed, _ = librosa.effects.trim(y, top_db=top_db)
    return trimmed


def load_and_trim(path: str, top_db: float = 30) -> tuple[np.ndarray, int]:
    """
    Load an audio file and trim silence.
    Returns (y, sr).
    """
    wav_path, is_temp = decode_to_wav(path)
    try:
        y, sr = librosa.load(wav_path, sr=44100)
        y = trim_silence(y, sr, top_db=top_db)
    finally:
        if is_temp and os.path.exists(wav_path):
            os.remove(wav_path)
    return y, sr


# -------------------------------------------------
# Key Detection
# -------------------------------------------------

# Camelot wheel mapping: pitch class index (major/minor) → Camelot code
CAMELOT_MAJOR = {
    0: "8B",  # C major
    1: "3B",  # C# major
    2: "10B", # D major
    3: "5B",  # Eb major
    4: "12B", # E major
    5: "7B",  # F major
    6: "2B",  # F# major
    7: "9B",  # G major
    8: "4B",  # Ab major
    9: "11B", # A major
    10: "6B", # Bb major
    11: "1B", # B major
}

CAMELOT_MINOR = {
    0: "5A",  # C minor
    1: "12A", # C# minor
    2: "7A",  # D minor
    3: "2A",  # Eb minor
    4: "9A",  # E minor
    5: "4A",  # F minor
    6: "11A", # F# minor
    7: "6A",  # G minor
    8: "1A",  # Ab minor
    9: "8A",  # A minor
    10: "3A", # Bb minor
    11: "10A",# B minor
}

NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def detect_key(path: str) -> dict:
    """
    Detect the musical key of an audio file.
    Returns dict with keys: key, mode, camelot, note_index.
    """
    wav_path, is_temp = decode_to_wav(path)

    try:
        y, sr = librosa.load(wav_path, sr=44100)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_mean = chroma.mean(axis=1)

        # Krumhansl-Schmuckler key profiles
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
                                   2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
                                   2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

        major_scores = [
            np.corrcoef(np.roll(major_profile, i), chroma_mean)[0, 1]
            for i in range(12)
        ]
        minor_scores = [
            np.corrcoef(np.roll(minor_profile, i), chroma_mean)[0, 1]
            for i in range(12)
        ]

        best_major = int(np.argmax(major_scores))
        best_minor = int(np.argmax(minor_scores))

        if major_scores[best_major] >= minor_scores[best_minor]:
            note_idx = best_major
            mode = "major"
            camelot = CAMELOT_MAJOR[note_idx]
        else:
            note_idx = best_minor
            mode = "minor"
            camelot = CAMELOT_MINOR[note_idx]

    finally:
        if is_temp and os.path.exists(wav_path):
            os.remove(wav_path)

    return {
        "key": NOTE_NAMES[note_idx],
        "mode": mode,
        "camelot": camelot,
        "note_index": note_idx,
        "label": f"{NOTE_NAMES[note_idx]} {mode} ({camelot})",
    }
