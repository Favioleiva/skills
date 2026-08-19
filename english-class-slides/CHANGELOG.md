# Changelog

All notable changes to the `english-class-slides` skill will be documented in this file.

---

## [1.3] — 2026-08-19

### Added
- **Explicit Six Core Deliverables Definition**:
  - Formalized the complete skill output package as exactly **six deliverables**: 3 PowerPoint decks (`.pptx`) and 3 synchronized Full HD presentation videos (`.mp4`) across English, Spanish, and Japanese.
- **Language-Differentiated Audio Narration Architecture**:
  - **English (EN) & Spanish (ES)**: Dedicated human audio ingest workflow supporting DAW exports (e.g. REAPER) with 1:1 slide matching (`01.mp3` ... `53.mp3` or `slide_01.wav` ...).
  - **Zero Destructive Audio Processing Policy**: Strictly prohibits automatic trimming, silence deletion, aggressive gating, or destructive filtering on human audio, ensuring initial consonants remain 100% intact.
  - **Natural Lead-In Headroom**: Validated that natural 300–700 ms pre-speech silence in human recordings provides native DAC/decoder wake-up headroom, eliminating the need for artificial sacrificial tones in EN/ES.
  - **Japanese (JA)**: Automated VOICEVOX GPU synthesis pipeline with continuous Kana reading layer (`slides_reading_ja_kana.txt`), per-slide synthesis, and single initial sacrificial startup cue (`ピッ` + 150 ms) to wake up DACs for TTS without initial silence.
- **Universal Multi-Format Presentation Video Builder (`scripts/build_presentation_video.py`)**:
  - Universal CLI parameter support (`--lang en`, `--lang es`, `--lang ja`).
  - Flexible multi-format audio discovery (`01.mp3`, `01.wav`, `slide_01.mp3`, `slide_01.wav`, `Tracks/01.mp3`, etc.).
  - Multi-channel stereo preservation across master PCM concatenation and final AAC encoding.
  - Automatic hardware acceleration detection (`h264_nvenc` with CPU `libx264` fallback).
  - Automated generation of `<topic>_<lang>_timeline.txt` and `<topic>_<lang>_chapters.txt`.
  - Midpoint visual transitions ($t = \text{audio\_end} + 250\text{ ms}$) preventing narration overlap.
  - Concluding slide persistence with FFmpeg concat demuxer last-frame repeat rule.
- **Enhanced Quality Assurance Suite**:
  - Upgraded `scripts/validate_audio.py` to inspect any naming pattern, decodability, duration, channels, sample rate, and non-destructive lead-in headroom.
  - Upgraded `scripts/validate_video.py` to perform container stream audits, duration synchronization verification, and multi-timestamp visual frame extraction with MAD checks against source PNG renders.

---

## [1.2] — 2026-08-17

### Added
- **Full Multimedia Production Architecture**: Expanded skill from slide-deck generation into a complete 6-phase pipeline supporting slides, audio synthesis, and synchronized Full HD 1080p presentation video assembly.
- **Continuous Master Audio Architecture (Strategy B)**:
  - Replaced legacy per-slide segmented MP4 concatenation with a single continuous Master Audio WAV pipeline.
  - Eliminates DAC wake-up attenuation, audio driver sleep, decoder restarts, and consonant clipping across all slide transitions.
  - Reduces final video file size by over 50% through single-pass AAC encoding.
- **Acoustic Playback Rationale Correction**:
  - The validated video architecture uses a single sacrificial startup signal (`ピッ` + 150 ms gap) followed by one continuous master audio stream and a single final AAC encode.
- **Continuous Japanese Kana Prosody & Zero-Whitespace Rule**:
  - Enforced continuous Japanese orthography in `slides_reading_ja_kana.txt` (eliminated artificial spaces that caused VOICEVOX phrase fragmentation).
  - Preserves natural katakana for loanwords and onomatopoeia with prosodic punctuation (`、`, `。`).
- **VOICEVOX Audio Synthesis Engine (Local Windows GPU & Colab Linux)**:
  - Added `scripts/setup_voicevox_local_gpu.py` supporting native Windows DirectML GPU acceleration (`tools/windows-directml/run.exe`) without Docker.
  - Added Zero-Docker Google Colab workflow running official Linux GPU/CUDA binary builds directly on Tesla T4 accelerators.
  - Added query validation verifying submitted text against returned `query["kana"]` before synthesis.
  - Added `TEST_MODE` for rapid sample slide verification (`[1, 2, 10, 30]`).
- **Configurable Visible Slide Numbering (Phase 4B)**:
  - Added native slide numbering across EN, ES, and JA presentations with background-aware contrast presets (`#1A2433` daytime, `#E1BC95` twilight, `#FFFFFF` night).
- **Full HD 1080p Video Generator**:
  - Single-pass continuous rendering with hardware-accelerated NVIDIA NVENC (`h264_nvenc`) and high-quality `libx264` fallback.
  - Enforced constant frame rate (CFR) filter: `-vf fps=30,format=yuv420p`.

---

## [1.1] — 2026-08-17

### Added
- Formal pedagogical slide architecture (Slide 1 Cover + Slides 2–51 Single-Sentence + Slides 52–53 Vocabulary).
- Target-language vocabulary localization (1-to-1 semantic equivalences).
- Japanese Kana reading layer draft (`slides_reading_ja_kana.txt`).
- Automated PPTX assembly pipeline (`scripts/build_pptx.py`, `scripts/validate_pptx.py`, `scripts/check_image_status.py`).
- Background-aware typography presets.
- Motif-leakage prevention and zero-text enforcement in image prompts.

---

## [1.0] — Initial Release

- Initial baseline skill for English class slide creation.
