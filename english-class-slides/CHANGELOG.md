# Changelog

All notable changes to the `english-class-slides` skill will be documented in this file.

---

## [1.2] — 2026-08-17

### Added
- **Full Multimedia Production Architecture**: Expanded skill from slide-deck generation into a complete, optional 6-phase pipeline supporting slides, audio synthesis, and synchronized Full HD 1080p presentation video assembly.
- **Continuous Master Audio Architecture (Strategy B)**:
  - Replaced legacy per-slide segmented MP4 concatenation with a single continuous Master Audio WAV pipeline.
  - Eliminates DAC wake-up attenuation, audio driver sleep, decoder restarts, and consonant clipping across all slide transitions.
  - Reduces final video file size by over 50% through single-pass AAC encoding.
- **Continuous Japanese Kana Prosody & Zero-Whitespace Rule**:
  - Enforced continuous Japanese orthography in `slides_reading_ja_kana.txt` (eliminated artificial spaces that caused VOICEVOX phrase fragmentation).
  - Preserves natural katakana for loanwords and onomatopoeia with prosodic punctuation (`、`, `。`).
- **VOICEVOX Audio Synthesis Engine (Local Windows GPU & Colab Linux)**:
  - Added `scripts/setup_voicevox_local_gpu.py` supporting native Windows DirectML GPU acceleration (`tools/windows-directml/run.exe`) without Docker.
  - Added Zero-Docker Google Colab workflow running official Linux GPU/CUDA binary builds directly on Tesla T4 accelerators.
  - Added query validation verifying submitted text against returned `query["kana"]` before synthesis.
  - Added `TEST_MODE` for rapid sample slide verification (`[1, 2, 10, 30]`).
  - Added 3-stage raw (`.wav`), padded (`.wav`), and encoded (`.mp3`) diagnostic preservation.
  - Standardized 0.5s pre/post silence buffer at the uncompressed PCM WAV stage.
- **Configurable Visible Slide Numbering (Phase 4B)**:
  - Added native slide numbering across EN, ES, and JA presentations with background-aware contrast presets (`#1A2433` daytime, `#E1BC95` twilight, `#FFFFFF` night).
  - Full configuration support in `deck_config.json` (`exclude_cover`, `exclude_vocabulary`, `start_number`, `position`, `font_size_pt`).
- **Full HD 1080p Video Generator (`scripts/build_presentation_video.py`)**:
  - Single-pass continuous rendering with hardware-accelerated NVIDIA NVENC (`h264_nvenc`) and high-quality `libx264` fallback.
  - Fixed still-image black-screen issue by enforcing constant frame rate (CFR) filter: `-vf fps=30,format=yuv420p`.
  - Added final-image repetition in concat lists to guarantee full display of the concluding slide.
  - Automated PowerPoint COM 1080p slide frame exporter on Windows with absolute path resolution.
  - Added 15-second diagnostic preview mode with frame extraction verification at 1s, 6s, and 11s before full batch rendering.
  - Automated generation of `<topic>_<lang>_timeline.txt` and `<topic>_<lang>_chapters.txt` for YouTube and video player navigation.
- **Audio & Video Quality Assurance Scripts**:
  - Added `scripts/validate_audio.py` for audio count and integrity verification.
  - Added `scripts/validate_video.py` for stream audit, dimensions, CFR, audio/video duration match, and visual frame inspection.
- **Notebook Code-Cell Syntax Validation Safeguard**:
  - Corrected spelling to `notebooks/[Python]_Voicevox_text_to_speech_from_Japanese_text_to_Japanese_Speech.ipynb`.
  - Implemented generator safeguards for escaped newline strings (`\\n`) and AST `compile()` syntax validation across all notebook cells.

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
