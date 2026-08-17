# English Class Slides Skill (`v1.2`)

A production-grade Antigravity agent skill for creating **multilingual educational slide decks** (English canonical, Latin American Spanish, authentic Japanese) with paired 16:9 anime watercolor backgrounds, single-sentence pedagogical layouts, Google-Slides-compatible PowerPoint assembly, optional VOICEVOX audio synthesis, and synchronized Full HD presentation video generation.

---

## 1. Features & Design Philosophy

* **Target Audience**: A1–A2 English and foreign language learners, Japanese classroom environments, international education.
* **Pedagogical Core**: **One Image + One Sentence**. Eliminates cognitive overload and maximizes read-aloud clarity.
* **Three Flexible Production Levels**:
  * **Level 1 — Slides Only**: Content generation, visual prompt engineering, and automated PowerPoint assembly.
  * **Level 2 — Slides + Narration**: Adds Japanese kana phonetic layer and VOICEVOX TTS or recorded voice tracks.
  * **Level 3 — Complete Multimedia Lesson**: Full HD 1080p MP4 presentation video with continuous master audio synchronization and YouTube chapter markers.
* **100% Google Slides Native**: Automated assembly produces `.pptx` presentations styled with Google Fonts (`Cormorant Garamond`, `Nunito Sans`, `Noto Serif JP`, `Noto Sans JP`) ready for 1-click import into Google Drive.
* **Background-Aware Typography & Numbering**: Automatically adapts text positioning, font sizes, and contrast colors for daytime (`#1A2433`), travel open horizon, twilight matsuri (`#E1BC95`), and fireworks night (`#FFFFFF`).

---

## 2. Directory Structure

```text
your-project/
├── .agents/skills/english-class-slides/
│   ├── SKILL.md
│   ├── README.md
│   ├── CHANGELOG.md
│   ├── templates/
│   │   ├── deck_config.template.json
│   │   ├── slides_content_en.template.txt
│   │   └── image_prompts.template.txt
│   ├── examples/
│   │   └── summer_vacation_japan/
│   ├── notebooks/
│   │   └── [Python]_Voicevox_text_to_speech_from_Japanese_text_to_Japanese_Speech.ipynb
│   └── scripts/
│       ├── build_pptx.py
│       ├── validate_pptx.py
│       ├── check_image_status.py
│       ├── setup_voicevox_local_gpu.py
│       ├── synthesize_presentation_audio.py
│       ├── validate_audio.py
│       ├── build_presentation_video.py
│       └── validate_video.py
```

---

## 3. Workflow Quickstart

### Level 1: Slide Decks Only

1. **Phase 1: Canonical English & Prompts**
   * Generate `output/slides_content_en.txt`, `output/image_prompts.txt`, and `deck_config.json`.
   * **Review Gate**: Stop and inspect canonical phrasing and image prompts.

2. **Phase 2: Localization**
   * After approval, generate `output/slides_content_es.txt` and `output/slides_content_ja.txt`.

3. **Phase 3: Image Generation**
   * Generate 16:9 background illustrations into `output/images/`.

4. **Phase 4: PowerPoint Assembly**
   ```bash
   python scripts/build_pptx.py --config deck_config.json --lang all
   python scripts/validate_pptx.py
   ```

---

### Level 2: Slides + Narration (VOICEVOX Audio)

1. **Phase 2B: Japanese Kana Reading Layer**
   * Generate `output/slides_reading_ja_kana.txt` using continuous Japanese orthography (zero artificial whitespace).

2. **Phase 5: Audio Synthesis**
   * **Route A (Local Windows GPU)**:
     ```bash
     python scripts/setup_voicevox_local_gpu.py
     python scripts/synthesize_presentation_audio.py --kana-file output/slides_reading_ja_kana.txt
     python scripts/validate_audio.py --audio-dir Audio/Japanese
     ```
   * **Route B (Google Colab)**:
     Open `notebooks/[Python]_Voicevox_text_to_speech_from_Japanese_text_to_Japanese_Speech.ipynb` and select *T4 GPU*.

---

### Level 3: Complete Multimedia Lesson (1080p Video)

1. **Phase 6: Presentation Video Generation**
   ```bash
   # Japanese Presentation (with continuous master audio and hardware NVENC)
   python scripts/build_presentation_video.py --config deck_config.json --lang ja

   # English Presentation (with custom human voice recordings)
   python scripts/build_presentation_video.py --config deck_config.json --lang en --audio-dir Audio/English

   # Spanish Presentation (with custom human voice recordings)
   python scripts/build_presentation_video.py --config deck_config.json --lang es --audio-dir Audio/Spanish
   ```

2. **Validate Final Video**:
   ```bash
   python scripts/validate_video.py --video output/summer_vacation_presentation_ja.mp4
   ```

---

## 4. Key Production Safeguards

* **Continuous Japanese Prosody**: No whitespace between Japanese words in `slides_reading_ja_kana.txt` to prevent unnatural TTS pauses.
* **Continuous Master Audio Architecture**: Merges all slide tracks into a single continuous master WAV to prevent playback DAC sleep, decoder resets, or initial consonant clipping.
* **Constant Frame Rate (CFR) Video Encoding**: Enforces `-vf fps=30,format=yuv420p` and repeats the final frame in concat lists to ensure 100% video display compatibility across all media players.
* **Zero-Docker GPU Execution**: Direct binary engine execution in both local Windows DirectML and Colab Linux GPU environments.

---

## 5. License & Credits

* **Framework & Design**: Favio Leiva (FL)
* **License**: MIT
