# Audio Prep Suite — User Guide

## v2.3.4 User Guide

Audio Prep Suite is a GUI-first Python toolkit for preparing audio for YouTube/video projects. It is designed to create prepared copies while protecting original files by default.

Use this guide if you are operating the app. Use `README.md` for setup, development, and repository notes.

---

## 1. Product Rule

Audio Prep Suite is a non-destructive prep tool.

Default rule:

```text
Originals stay untouched.
Prepared audio goes to audio_prepped/.
```

This matters because the app is often used before a sister YouTube Video Toolkit assembles images, clips, and audio into a final video.

---

## 2. Recommended Launch Flow

On Windows, open Command Prompt in the Audio Prep Suite folder and run:

```bat
install_or_update_deps.bat
preflight.bat
launch.bat
```

Normally, after the first setup, you only need:

```bat
launch.bat
```

The app uses a local `.venv` when available. This avoids the common problem where Librosa is installed in one Python environment but the app launches with another.

---

## 3. Home Screen / Launcher

The launcher opens the main Audio Prep Suite menu.

You will see buttons for:

- Full Prep Pipeline
- BPM Analyzer
- Audio to MP3
- Silence Trimmer
- Key Detector
- YouTube Toolkit
- Settings

### Setup Banner

If dependencies are missing, the launcher may show a setup warning.

Use:

- **Fix Setup** — run/update dependencies
- **Refresh Check** — recheck after install
- **Details** — see Python path, package status, and FFmpeg status

If Python packages are installed but the banner remains, check whether FFmpeg is missing.

---

## 4. YouTube Toolkit Button

The old COT Launcher wording has been replaced.

The button should say:

```text
YouTube Toolkit
```

When clicked, Audio Prep Suite searches for the sister toolkit launcher in nearby folders. If it cannot find the toolkit, it asks you to browse to one of:

```text
master_launcher.py
main.py
launcher.py
```

After you select it once, the path is saved locally in `master_config.json`.

---

## 5. Full Prep Pipeline

Use this when you want the normal YouTube audio-prep workflow.

It can:

- trim silence,
- normalize loudness,
- estimate BPM,
- estimate key and Camelot code,
- export compressed MP3,
- export CSV handoff.

### Output

The Full Pipeline writes to:

```text
audio_prepped/
```

Example:

```text
audio_prepped/
  song_BPM120_Am_8A.mp3
  audio_prep_results.csv
```

The original file should remain unchanged.

### Best use

Use Full Pipeline when you are preparing multiple audio files for a video project and want the YouTube Video Toolkit to consume clean prepared outputs.

---

## 6. BPM Analyzer

Use BPM Analyzer when you only need tempo estimates.

Good for:

- beat matching,
- selecting music with similar tempo,
- naming prepared assets with BPM tags.

Notes:

- BPM detection requires Librosa.
- Very short clips, silence, speech, or unusual music may produce weak estimates.
- Trimming silence first can improve results.

---

## 7. Key Detector

Use Key Detector when you want estimated musical key and Camelot code.

Good for:

- harmonic mixing,
- selecting compatible music beds,
- organizing music for video mood/flow.

Notes:

- Key detection is an estimate, not a professional guarantee.
- It works best on music with clear harmony.
- It may be unreliable on speech, drums-only clips, noisy files, or very short clips.

---

## 8. Audio to MP3 Converter

Use Audio to MP3 when you mainly want smaller files for video projects.

Recommended wording:

```text
Compressed MP3 for video
```

This is better than “downgrade” because the goal is not to damage audio; the goal is to reduce final project size.

Important behavior:

- Export should preserve stereo unless a smaller mono option is explicitly selected.
- Originals should remain untouched.
- Outputs should be written as prepared copies.

---

## 9. Silence Trimmer

Use Silence Trimmer when files have dead space at the beginning or end.

Good for:

- cleaning voiceovers,
- improving BPM detection,
- reducing awkward gaps before video transitions.

The trim threshold controls how aggressively silence is removed. If too much is removed, use a less aggressive threshold.

---

## 10. Settings

Settings may include:

- theme,
- accent color,
- last folder,
- default trim setting,
- default normalization setting,
- default MP3 setting,
- default CSV setting,
- MP3 quality,
- silence trim threshold,
- audio/images/toolkit paths.

Local settings are stored in `config.json` and/or `master_config.json`.

These are local machine files and should not be committed to GitHub.

---

## 11. Dependency Troubleshooting

### Librosa missing

Run:

```bat
install_or_update_deps.bat
preflight.bat
launch.bat
```

If the launcher still says Librosa is missing, open **Details** and check the Python executable. The app may be using a different Python than the one where packages were installed.

### FFmpeg missing

Run:

```bat
ffmpeg -version
```

If the command fails, install FFmpeg and add its `bin` folder to PATH.

### Do not use npm/Expo here

Audio Prep Suite is Python. These commands do not install Librosa or FFmpeg:

```bat
npx expo install --fix
npm audit fix
```

Those commands belong to the sister YouTube Toolkit only if that toolkit is an Expo/React Native project.

---

## 12. Safe Testing Checklist

Before trusting a new build, do this with copied files:

```text
1. Create a test folder.
2. Put 2–3 copied audio files inside.
3. Run launch.bat.
4. Open Full Prep Pipeline.
5. Enable MP3 and CSV.
6. Run the batch.
7. Confirm originals were not renamed or overwritten.
8. Confirm audio_prepped/ was created.
9. Confirm output MP3 files exist.
10. Confirm audio_prep_results.csv exists.
```

Pass condition:

```text
Originals untouched. Prepared outputs created. CSV created.
```

---

## 13. Recommended Normal Workflow

For YouTube project prep:

```text
1. Put source audio in a project folder.
2. Run Full Prep Pipeline.
3. Use audio_prepped/ as the audio asset folder.
4. Use audio_prep_results.csv as the handoff/reference file.
5. Open the YouTube Toolkit to continue video assembly.
```

---

## 14. License

MIT
