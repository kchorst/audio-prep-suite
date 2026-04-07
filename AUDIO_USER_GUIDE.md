# User Guide — Audio Prep Suite

This guide is a feature-oriented overview of Audio Prep Suite and a practical “menu” of how to use each tool.

If you only want the quick start, see `README.md`.

---

## 1) What this tool is

Audio Prep Suite is a modular set of Python GUI tools for preparing audio files for production workflows:

- Trim silence
- Normalize loudness
- Detect BPM
- Detect musical key (and Camelot code)
- Convert WAV → MP3
- Run the full pipeline end-to-end

You can run:

- A single tool, directly
- Or the launcher (`main.py`) to access all tools

### Optional companion to the YouTube Video Creator suite

Audio Prep Suite is standalone, but it can also be used as an optional companion to the YouTube Video Creator suite.

If you use the YouTube suite’s Master Launcher, you can enable these audio tools by setting:

- Settings → **Audio Prep Suite** folder path → point it to this repo’s folder

---

## 2) Supported platforms

- **Windows**: primary supported platform (best tested)
- **macOS/Linux**: supported in principle; ensure Python + Tkinter + FFmpeg are set up

---

## 3) Requirements and dependencies

### System

- **Python**: 3.10 or 3.11 (3.12+ may work but is not the primary target)
- **FFmpeg**: must be installed and available on PATH

### Python packages

Install:

```bash
pip install -r requirements.txt
```

---

## 4) Installation (recommended)

1) Clone or download the repo

```bash
git clone https://github.com/YOUR_USERNAME/audio-prep-suite.git
cd audio-prep-suite
```

2) Create and activate a virtual environment

```bash
python -m venv venv
```

Activate:

- Windows (CMD): `venv\Scripts\activate`
- Windows (PowerShell): `venv\Scripts\Activate.ps1`
- macOS/Linux: `source venv/bin/activate`

3) Install dependencies

```bash
pip install -r requirements.txt
```

4) Verify FFmpeg

```bash
ffmpeg -version
```

---

## 5) How to run (launcher and direct)

### Option A: Launcher (recommended)

From repo root:

```bash
python main.py
```

### Option B: Run tools directly

```bash
python bpm_tool/bpm_gui.py
python converters/wav_to_mp3.py
python trimmers/trim_silence.py
python key_detection/key_gui.py
python pipeline/full_prep_gui.py
```

---

## 6) Tool “menu”: which tool should I use?

### 6.1 BPM Analyzer (`bpm_tool/bpm_gui.py`)

Use this when:

- You want to estimate BPM for a batch
- You want automatic rename with BPM tags
- You want optional WAV→MP3 export

Typical flow:

- Select files
- (Optional) trim silence / normalize
- Analyze BPM
- Save results (rename/export)

---

### 6.2 WAV → MP3 Converter (`converters/wav_to_mp3.py`)

Use this when:

- You already have WAVs and just want MP3s
- You want optional normalize/trim during export

---

### 6.3 Silence Trimmer (`trimmers/trim_silence.py`)

Use this when:

- Tracks have dead space at the beginning/end
- BPM detection is skewed by long intros/outros

Key setting:

- `top_db` (threshold). Lower trims more aggressively.

---

### 6.4 Key Detector (`key_detection/key_gui.py`)

Use this when:

- You want key + Camelot code for mixing
- You want optional rename tagging (e.g. `Am`, `8A`)

---

### 6.5 Full Prep Pipeline (`pipeline/full_prep_gui.py`)

Use this when:

- You want to process a batch end-to-end
- You want consistent naming and a CSV summary

Typical steps:

- (Optional) trim silence
- (Optional) normalize loudness
- BPM detect
- Key detect
- Rename
- (Optional) export MP3
- (Optional) export CSV

---

## 7) Workflow examples

### Example A: “Make everything upload-ready”

- Run **Full Prep Pipeline**
- Enable normalize
- Enable export MP3
- Enable export CSV

### Example B: “Just fix silence then detect BPM”

- Run **Silence Trimmer**
- Then run **BPM Analyzer** on the trimmed outputs

### Example C: “Harmonic mixing library”

- Run **Key Detector**
- Rename files with key + Camelot

---

## 8) Troubleshooting

- **FFmpeg not found**: confirm it’s installed and on PATH; restart terminal
- **No tkinter on Linux**: install `python3-tk`
- **Librosa installs slowly**: normal; use a venv

---

## 9) Notes for integration with other projects

Audio Prep Suite is designed to be useful standalone.

If another project wants to call the pipeline programmatically, the core logic lives in:

- `pipeline/full_prep.py`

---

## 10) License

MIT
