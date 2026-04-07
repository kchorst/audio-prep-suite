"""
utils/ffmpeg_tools.py
Shared FFmpeg helpers. No console window on Windows.
"""

import os
import subprocess
import tempfile
import sys

SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac"}

# Suppress console window on Windows
_POPEN_FLAGS = {}
if sys.platform == "win32":
    _POPEN_FLAGS["creationflags"] = subprocess.CREATE_NO_WINDOW


def is_supported(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in SUPPORTED_EXTENSIONS


def decode_to_wav(path: str) -> tuple[str, bool]:
    """
    Decode any supported audio file to a temporary WAV file.
    Returns (wav_path, is_temp). Caller must delete temp file if is_temp=True.
    WAV files are returned as-is (is_temp=False).
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".wav":
        return path, False

    # Create temp file, close it immediately so ffmpeg can write to it on Windows
    fd, tmp_wav = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    result = subprocess.run(
        ["ffmpeg", "-y", "-i", path, "-ac", "1", "-ar", "44100", tmp_wav],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        **_POPEN_FLAGS,
    )

    if result.returncode != 0:
        if os.path.exists(tmp_wav):
            os.remove(tmp_wav)
        raise RuntimeError(
            f"FFmpeg failed to decode '{os.path.basename(path)}':\n"
            + result.stderr.decode(errors="replace")
        )

    return tmp_wav, True


def export_to_mp3(input_path: str, output_path: str, quality: int = 2) -> str:
    """
    Export any audio file to MP3 using libmp3lame.
    quality: 0 (best) to 9 (worst).
    """
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-i", input_path,
            "-codec:a", "libmp3lame",
            "-qscale:a", str(quality),
            output_path,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        **_POPEN_FLAGS,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg failed to export MP3 '{os.path.basename(output_path)}':\n"
            + result.stderr.decode(errors="replace")
        )

    return output_path


def normalize_audio_ffmpeg(input_path: str, output_path: str) -> str:
    """
    Normalize audio loudness to -14 LUFS using ffmpeg loudnorm filter.
    """
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-i", input_path,
            "-af", "loudnorm=I=-14:LRA=11:TP=-1",
            output_path,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        **_POPEN_FLAGS,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg normalization failed for '{os.path.basename(input_path)}':\n"
            + result.stderr.decode(errors="replace")
        )

    return output_path
