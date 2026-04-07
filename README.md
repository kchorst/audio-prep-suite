# 🎵 Audio Prep Suite

> A modular Python toolkit for preparing audio files for production, YouTube uploads, sample packs, DJ sets, and automated pipelines.

![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![FFmpeg](https://img.shields.io/badge/Requires-FFmpeg-green?logo=ffmpeg)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What Is This?

Audio Prep Suite is a collection of GUI tools built in Python that handle the repetitive prep work that comes before every release, upload, or DJ set — detecting BPM, finding the key, trimming silence, normalizing loudness, converting formats, and renaming files consistently.

Every tool runs independently or together through a single launcher. All processing is threaded so the UI never freezes on large batches.

For a feature menu + workflow-style guide, see **`AUDIO_USER_GUIDE.md`**.

Audio Prep Suite is standalone, but it can also be used as an optional companion to the YouTube Video Creator suite.
If you use the YouTube suite’s Master Launcher, set **Settings → Audio Prep Suite** folder path to this repo folder to enable the audio tools.

---

## Tools at a Glance

| Tool | Script | What it does |
|---|---|---|
| 🎛 **Launcher** | `main.py` | Opens a menu to launch any tool |
| 🥁 **BPM Analyzer** | `bpm_tool/bpm_gui.py` | Batch BPM detection, rename files, export WAV → MP3 |
| 🔄 **WAV → MP3 Converter** | `converters/wav_to_mp3.py` | Batch convert with optional trim + normalize |
| ✂️ **Silence Trimmer** | `trimmers/trim_silence.py` | Trim leading/trailing silence, adjustable threshold |
| 🎵 **Key Detector** | `key_detection/key_gui.py` | Musical key + Camelot wheel code, optional rename |
| ⚡ **Full Pipeline** | `pipeline/full_prep_gui.py` | Trim → Normalize → BPM → Key → Rename → MP3 → CSV |

**Supported formats:** WAV · MP3 · FLAC · OGG · M4A · AAC

---

## Project Structure

```
audio_prep_suite/
│
├── main.py                         # Launcher — opens any tool from a menu
├── requirements.txt                # Python dependencies
├── setup_audio_prep_suite.ps1      # Windows folder scaffolding script
│
├── bpm_tool/
│   ├── __init__.py
│   └── bpm_gui.py                  # Batch BPM analyzer GUI
│
├── converters/
│   └── wav_to_mp3.py               # Batch WAV → MP3 converter GUI
│
├── trimmers/
│   └── trim_silence.py             # Silence trimmer GUI
│
├── key_detection/
│   └── key_gui.py                  # Key detector GUI
│
├── pipeline/
│   ├── full_prep.py                # Pipeline core logic (importable, no GUI)
│   └── full_prep_gui.py            # Full pipeline GUI
│
└── utils/
    ├── __init__.py
    ├── ffmpeg_tools.py             # FFmpeg decode / encode / normalize helpers
    ├── audio_tools.py              # BPM, silence trim, key detection logic
    ├── file_tools.py               # Rename, path building, CSV export
    └── threading_tools.py          # Thread-safe GUI logger + run_in_thread
```

---

## Requirements

### System Requirements

| Requirement | Version | Notes |
|---|---|---|
| **Python** | 3.10 or 3.11 | 3.12+ not tested |
| **FFmpeg** | Any recent | Must be on system PATH |
| **Tkinter** | Included | Bundled with Python on Windows & macOS |
| **OS** | Windows / macOS / Linux | GUI tested primarily on Windows |

### Python Packages

```
librosa==0.10.1
numpy==1.26.4
soundfile==0.12.1
audioread==3.0.1
ffmpeg-python==0.2.0
```

All installed automatically via `pip install -r requirements.txt`.

---

## Installation

### Step 1 — Install Python

Download Python **3.10 or 3.11** from the official site:

👉 https://www.python.org/downloads/

> ⚠️ **Important:** During installation, check **"Add Python to PATH"** before clicking Install.

Verify Python is installed:

```bash
python --version
```

---

### Step 2 — Install FFmpeg

FFmpeg handles all audio decoding and encoding. It must be installed separately and available on your system PATH.

#### Windows

1. Go to https://www.gyan.dev/ffmpeg/builds/
2. Download the latest **`ffmpeg-release-full.7z`** build
3. Extract it (e.g. to `C:\ffmpeg\`)
4. Add `C:\ffmpeg\bin\` to your system PATH:
   - Search **"Environment Variables"** in the Start menu
   - Under **System Variables**, select **Path** → **Edit**
   - Click **New** and paste `C:\ffmpeg\bin\`
   - Click OK on all dialogs

#### macOS (Homebrew)

```bash
brew install ffmpeg
```

#### Linux (apt)

```bash
sudo apt update && sudo apt install ffmpeg
```

Verify FFmpeg is working:

```bash
ffmpeg -version
```

You should see version info. If you get `command not found`, your PATH is not set correctly.

---

### Step 3 — Get the Code

**Clone via Git:**

```bash
git clone https://github.com/YOUR_USERNAME/audio-prep-suite.git
cd audio-prep-suite
```

**Or download the ZIP** from the GitHub repo page → **Code → Download ZIP**, then extract it.

---

### Step 4 — Create a Virtual Environment

A virtual environment keeps the suite's dependencies isolated from your system Python.

```bash
python -m venv venv
```

**Activate it:**

| Platform | Command |
|---|---|
| Windows (CMD) | `venv\Scripts\activate` |
| Windows (PowerShell) | `venv\Scripts\Activate.ps1` |
| macOS / Linux | `source venv/bin/activate` |

You should see `(venv)` at the start of your terminal prompt.

> To deactivate later, just type `deactivate`.

---

### Step 5 — Install Python Dependencies

With the virtual environment active:

```bash
pip install -r requirements.txt
```

This installs librosa, numpy, soundfile, audioread, and ffmpeg-python. It may take a minute — librosa pulls in several scientific packages.

---

### Step 6 — Windows Quick Scaffold (Optional)

If you want to scaffold the full folder structure on Windows before copying files in, run the included PowerShell script:

```powershell
.\setup_audio_prep_suite.ps1
```

This creates all folders and `__init__.py` files under `D:\Audio Prep Suite\`. Edit the `$root` path at the top of the script to change the destination.

---

## Launching the Suite

### Option A — Launcher Menu (Recommended)

From the project root, with the venv active:

```bash
python main.py
```

A window opens with buttons to launch each tool. Each tool opens in its own window.

---

### Option B — Run Tools Directly

You can launch any tool individually without going through the launcher:

```bash
python bpm_tool/bpm_gui.py
python converters/wav_to_mp3.py
python trimmers/trim_silence.py
python key_detection/key_gui.py
python pipeline/full_prep_gui.py
```

> Each script adds the project root to `sys.path` automatically, so imports always resolve regardless of where you run from.

---

## Tool Details

### 🥁 BPM Analyzer — `bpm_tool/bpm_gui.py`

Analyzes BPM across a batch of files using `librosa.beat.tempo` with median aggregation for stability.

**Workflow:**
1. Tick **Trim silence** and/or **Normalize** (optional)
2. Click **Browse Files** — select any supported audio format
3. Click **Analyze** — results appear in the log (runs in background thread)
4. Click **Save BPM** to:
   - Rename files with a `_BPM{n}` suffix (e.g. `track_BPM128.wav`)
   - Export WAV files to MP3
5. Choose to analyze more files or quit

> Rename always happens before MP3 export, so the export always targets the correct on-disk filename.

---

### 🔄 WAV → MP3 Converter — `converters/wav_to_mp3.py`

Batch-converts WAV files to MP3 using FFmpeg's `libmp3lame` encoder at ~190 kbps VBR (quality 2).

**Options:**
- **Normalize before export** — applies −14 LUFS loudness normalization (YouTube / streaming standard)
- **Trim silence before export** — removes leading and trailing silence before encoding

---

### ✂️ Silence Trimmer — `trimmers/trim_silence.py`

Trims leading and trailing silence using `librosa.effects.trim`.

**Options:**
- **Threshold (top_db)** — adjustable via spinbox (10–60 dB). Lower values trim more aggressively. Default: 30 dB.

Output files are saved as `_trimmed.wav` alongside the originals. Original files are not modified.

---

### 🎵 Key Detector — `key_detection/key_gui.py`

Detects the musical key of each file using the Krumhansl-Schmuckler algorithm on chroma features.

**Output per file:**
- Key name (e.g. `A`)
- Mode (`major` / `minor`)
- Camelot wheel code (e.g. `8A`, `5B`) — useful for harmonic mixing

**Optional:** Rename files with a key tag appended, e.g. `track_Aminor_8A.wav`.

---

### ⚡ Full Prep Pipeline — `pipeline/full_prep_gui.py`

Runs all steps in sequence on every selected file:

| Step | Option |
|---|---|
| 1. Trim silence | Optional (checkbox) |
| 2. Normalize to −14 LUFS | Optional (checkbox) |
| 3. Detect BPM | Always runs |
| 4. Detect Key | Always runs |
| 5. Rename with combined tag | Always runs — e.g. `track_BPM128_AmM_8A.wav` |
| 6. Export WAV → MP3 | Optional (checkbox) |
| 7. Export results CSV | Optional (checkbox) |

The CSV contains: original filename, final filename, BPM, key, Camelot code, MP3 path, and status per file.

The pipeline core (`pipeline/full_prep.py`) has no GUI dependency and can be imported into your own scripts:

```python
from pipeline.full_prep import run_pipeline

results = run_pipeline(
    files=["track1.wav", "track2.flac"],
    do_trim=True,
    do_normalize=True,
    do_export_mp3=True,
)
```

---

## Shared Utilities

All tools share a common `utils/` layer so logic is never duplicated:

| Module | Purpose |
|---|---|
| `utils/ffmpeg_tools.py` | `decode_to_wav()`, `export_to_mp3()`, `normalize_audio_ffmpeg()` |
| `utils/audio_tools.py` | `analyze_bpm()`, `detect_key()`, `trim_silence()`, `load_and_trim()` |
| `utils/file_tools.py` | `safe_rename()`, `append_tag_to_filename()`, `export_csv()`, `collect_audio_files()` |
| `utils/threading_tools.py` | `GuiLogger` (thread-safe Tkinter log widget), `run_in_thread()` |

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'utils'`**
Run scripts from the project root (`python bpm_tool/bpm_gui.py`), or use the launcher (`python main.py`). Each script patches `sys.path` automatically so direct execution works from any directory.

**`FileNotFoundError: ffmpeg`**
FFmpeg is not on your PATH. Re-check Step 2 and restart your terminal after editing environment variables.

**`No module named 'tkinter'`**
On Linux, Tkinter is not always bundled with Python. Install it with:
```bash
sudo apt install python3-tk
```

**Librosa install fails / takes very long**
This is normal — librosa has large scientific dependencies. Ensure you are inside the virtual environment (`(venv)` visible in your prompt) before running `pip install`.

**BPM results seem off**
Enable **Trim silence** before analyzing. Long intros or silence at the start can skew the tempo estimator. The reported BPM is the median value across all detected beats.

**PowerShell script won't run**
You may need to allow script execution:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

---

## License

MIT — free to use, modify, and distribute.
