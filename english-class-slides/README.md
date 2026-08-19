# English Class Slides Skill (`v1.3`)

A production-grade Antigravity agent skill for creating **multilingual educational presentations** (canonical English, Latin American Spanish, authentic Japanese) producing a complete package of **six core deliverables**: 3 Google-Slides-compatible PowerPoint slide decks (`.pptx`) and 3 synchronized Full HD 1080p presentation videos (`.mp4`).

---

## 1. The Six Core Deliverables

Every full project execution of this skill produces exactly **six final deliverables**:

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          SIX CORE PRODUCTION DELIVERABLES                       │
├───────────────────────────────────────┬─────────────────────────────────────────┤
│ 3 PowerPoint Presentations (.pptx)    │ 3 Synchronized Presentation Videos (.mp4)│
├───────────────────────────────────────┼─────────────────────────────────────────┤
│ 1. slides_<topic>_en.pptx (English)   │ 4. <topic>_presentation_en.mp4 (English)│
│ 2. slides_<topic>_es.pptx (Spanish)   │ 5. <topic>_presentation_es.mp4 (Spanish)│
│ 3. slides_<topic>_ja.pptx (Japanese)  │ 6. <topic>_presentation_ja.mp4 (Japanese)│
└───────────────────────────────────────┴─────────────────────────────────────────┘
```

---

## 2. Features & Design Philosophy

* **Target Audience**: A1–A2 English and foreign language learners, Japanese classroom environments, international education.
* **Pedagogical Core**: **One Image + One Sentence**. Eliminates cognitive overload and maximizes read-aloud clarity.
* **Language-Differentiated Audio Pipeline**:
  * **English & Spanish**: Real human audio recorded by the user (1 track per slide, non-destructive preservation, natural lead-in headroom).
  * **Japanese**: Automated VOICEVOX GPU TTS synthesis with continuous Kana orthography and sacrificial startup cue.
* **100% Google Slides Native**: Automated assembly produces `.pptx` presentations styled with Google Fonts (`Cormorant Garamond`, `Nunito Sans`, `Noto Serif JP`, `Noto Sans JP`) ready for 1-click import into Google Drive.
* **Background-Aware Typography & Numbering**: Automatically adapts text positioning, font sizes, and contrast colors for daytime (`#1A2433`), twilight matsuri (`#E1BC95`), and night fireworks (`#FFFFFF`).
* **Continuous Master Video Architecture**: Single-pass 1080p CFR 30 fps MP4 video rendering with sample-accurate audio/video synchronization, midpoint slide transitions, and YouTube chapter markers.

---

## 3. Directory Structure

```text
your-project/
├── .agents/skills/english-class-slides/
│   ├── SKILL.md                        # Core agent instructions & rules (v1.3)
│   ├── README.md                       # Comprehensive operational guide
│   ├── CHANGELOG.md                    # Version history & architectural updates
│   ├── templates/
│   │   ├── deck_config.template.json
│   │   ├── slides_content_en.template.txt
│   │   └── image_prompts.template.txt
│   ├── examples/
│   │   └── summer_vacation_japan/
│   ├── notebooks/
│   │   └── [Python]_Voicevox_text_to_speech_from_Japanese_text_to_Japanese_Speech.ipynb
│   └── scripts/
│       ├── build_pptx.py               # Assembles EN, ES, and JA presentations
│       ├── validate_pptx.py            # Validates slide counts, dimensions, typography
│       ├── check_image_status.py       # Tracks background image generation progress
│       ├── setup_voicevox_local_gpu.py # Launches local native VOICEVOX GPU Engine
│       ├── synthesize_presentation_audio.py # Synthesizes Japanese presentation audio
│       ├── validate_audio.py           # Audits audio tracks (EN, ES, JA)
│       ├── build_presentation_video.py # Universal 1080p video builder (EN, ES, JA)
│       └── validate_video.py           # Validates video streams, CFR, and frame visibility
```

---

## 4. End-to-End Execution Workflow

### Step 1: Slide Decks & Background Images

1. **Phase 1: Canonical English & Prompts**
   * Generate `output/slides_content_en.txt`, `output/image_prompts.txt`, and `deck_config.json`.
   * **Review Gate**: Stop and inspect canonical phrasing and image prompts before proceeding.

2. **Phase 2: Multilingual Localization**
   * Generate `output/slides_content_es.txt`, `output/slides_content_ja.txt`, and `output/slides_reading_ja_kana.txt`.

3. **Phase 3: Image Generation**
   * Generate 16:9 background illustrations into `output/images/`.

4. **Phase 4: PowerPoint Assembly**
   ```bash
   python scripts/build_pptx.py --config deck_config.json --lang all
   python scripts/validate_pptx.py
   ```

---

### Step 2: Audio Production (Differentiated by Language)

1. **English & Spanish (Human Recorded Voice Tracks)**:
   * Record and export 1 track per slide to `Audio/English/Tracks/` and `Audio/Spanish/Tracks/` (`01.mp3`, `02.mp3`, ...).
   * **DO NOT** apply automatic trimming or silence deletion.
   * Validate audio assets:
     ```bash
     python scripts/validate_audio.py --audio-dir Audio/English/Tracks --expected-count 53
     python scripts/validate_audio.py --audio-dir Audio/Spanish/Tracks --expected-count 53
     ```

2. **Japanese (Automated VOICEVOX TTS)**:
   * **Route A (Local Windows GPU)**:
     ```bash
     python scripts/setup_voicevox_local_gpu.py
     python scripts/synthesize_presentation_audio.py --kana-file output/slides_reading_ja_kana.txt
     python scripts/validate_audio.py --audio-dir Audio/Japanese --expected-count 53
     ```
   * **Route B (Google Colab)**:
     Open `notebooks/[Python]_Voicevox_text_to_speech_from_Japanese_text_to_Japanese_Speech.ipynb` and run on a GPU runtime.

---

### Step 3: Synchronized Video Assembly & Quality Assurance

1. **Render All Three Presentation Videos**:
   ```bash
   # 1. English Presentation Video (from human recordings)
   python scripts/build_presentation_video.py --config deck_config.json --lang en --audio-dir Audio/English/Tracks

   # 2. Spanish Presentation Video (from human recordings)
   python scripts/build_presentation_video.py --config deck_config.json --lang es --audio-dir Audio/Spanish/Tracks

   # 3. Japanese Presentation Video (from synthesized TTS)
   python scripts/build_presentation_video.py --config deck_config.json --lang ja --audio-dir Audio/Japanese
   ```

2. **Run Full Video Quality Assurance Audit**:
   ```bash
   python scripts/validate_video.py --video output/summer_vacation_presentation_en.mp4
   python scripts/validate_video.py --video output/summer_vacation_presentation_es.mp4
   python scripts/validate_video.py --video output/summer_vacation_presentation_ja.mp4
   ```

---

## 5. Key Production Safeguards

* **Continuous Master Audio Architecture**: Merges per-slide audio tracks with 500 ms digital silence into a single master WAV, encoding to AAC in one single pass. Eliminates playback DAC sleep, decoder restarts, and consonant clipping across all transitions.
* **Non-Destructive Human Audio Policy**: Preserves natural recording lead-in headroom in English and Spanish without destructive slicing or trimming.
* **Midpoint Visual Transition**: Shifts slides at $t = \text{audio\_end} + 250\text{ ms}$ (midpoint of inter-slide silence) to guarantee zero audio overlap.
* **Concluding Slide Protection**: Slide 53 remains visible throughout its entire duration plus a 500 ms closing margin.
* **Constant Frame Rate (CFR) Video Encoding**: Enforces `-vf fps=30,format=yuv420p` with hardware NVENC (`h264_nvenc`) acceleration.

---

## 6. License & Credits

* **Framework & Design**: Favio Leiva (FL)
* **License**: MIT
