---
name: english-class-slides
description: Comprehensive production-grade multimedia workflow for creating multilingual educational presentations (canonical English, Latin American Spanish, natural Japanese) producing six core deliverables - 3 Google-Slides-compatible PowerPoint decks (.pptx) and 3 synchronized Full HD 1080p presentation videos (.mp4) with differentiated human audio ingest (EN/ES) and automated VOICEVOX TTS synthesis (JA).
---

# English Class Slides Skill (`v1.3`)

A comprehensive, topic-independent production workflow for creating **multilingual educational presentations** (A1–A2 English learners, Japanese classroom settings, and international education) producing a complete package of **six core deliverables**: 3 PowerPoint slide decks and 3 synchronized Full HD 1080p presentation videos.

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

## 2. Pedagogical Architecture & Core Principles

* **Pedagogical Core**: **One Image + One Sentence**. Eliminates cognitive overload and maximizes read-aloud clarity for A1–A2 learners.
* **Canonical Language**: English (`slides_content_en.txt`) is canonical and sets the baseline for structure, facts, and timing.
* **Slide Structure**:
  * **Slide 1**: Cover Slide (Creative Title + Subtitle + Author credit + AI-Assisted Production metadata block).
  * **Slides 2 to N+1**: $N$ Content Slides (Single short, engaging sentence; zero slide titles).
  * **Slides N+2 & N+3**: 2 Dedicated Vocabulary Slides (10 items each, 20 unique concepts total).
* **Total Slide Count**: Exactly $N + 2$ slides (e.g., 50 content slides $\implies$ 53 slides total).
* **Design Allocation**: Exactly $D$ content designs + 1 dedicated Vocabulary design $\implies$ Total image prompts = $D + 1$. Both vocabulary slides use Design $D+1$.

---

## 3. Language-Differentiated Audio Production Logic

Audio narration logic is strictly differentiated by target language:

```text
┌───────────────────────────┬─────────────────────────────────────────────────────────────────┐
│ Language                  │ Audio Narration Architecture                                    │
├───────────────────────────┼─────────────────────────────────────────────────────────────────┤
│ English (EN)              │ Real human audio recorded by user (1 track per slide)           │
│ Spanish (ES)              │ Real human audio recorded by user (1 track per slide)           │
│ Japanese (JA)             │ Automated VOICEVOX TTS synthesis pipeline (1 track per slide)   │
└───────────────────────────┴─────────────────────────────────────────────────────────────────┘
```

### Human Recorded Audio Guidelines (English & Spanish)
1. **Strict 1:1 Correspondence**: Exactly 1 audio file per slide named in zero-padded sequential order (`01.mp3`, `02.mp3`, ... or `slide_01.wav`, `slide_02.wav`, ...).
2. **Zero Destructive Processing**:
   * **DO NOT** apply automatic trimming or silence-stripping to the beginning of human audio.
   * **DO NOT** apply destructive noise reduction, aggressive high-pass filtering, or compression that damages consonant attacks.
   * Natural human lead-in silence (typically 200–600 ms from DAW export) acts as native hardware DAC/decoder wake-up headroom.
3. **No Sacrificial Tone Needed**: Human audio does **NOT** require an artificial sacrificial startup sound (`ピッ`) because the natural recording lead-in preserves the initial consonants.
4. **Decodability & Integrity**: All tracks must be verified non-empty, decodable, and non-corrupt prior to video assembly.

### Automated TTS Synthesis Guidelines (Japanese)
1. **Continuous Japanese Orthography**: `slides_reading_ja_kana.txt` must contain **zero artificial whitespace** between words. Whitespace in VOICEVOX creates unwanted phrase boundaries and broken prosody.
2. **Katakana Preservation**: Loanwords, foreign names, and onomatopoeia remain in natural Katakana (e.g. `ラジオたいそう`, `カブトムシ`, `スイカ`, `ラムネ`).
3. **Synthesis Headroom**: Standard synthesis parameters: `prePhonemeLength = 0.10` and `postPhonemeLength = 0.10`.
4. **Sacrificial Startup Cue**: For Japanese TTS, add a single startup cue (`ピッ` + 150 ms gap) at $t=0$ of the continuous master to prime hardware DACs/decoders against cold-start initial mora clipping.

---

## 4. End-to-End Seven-Phase Production Workflow

```text
[Phase 1: Canonical English & Prompts] ──(Human Review Gate)──► [Phase 2: Localization ES/JA]
                                                                        │
                                                                 [Phase 2B: Kana Layer]
                                                                        │
                                                                 [Phase 3: Image Generation]
                                                                        │
                                                                 [Phase 4: PPTX Assembly & Numbering]
                                                                        │
                                                       ┌────────────────┴────────────────┐
                                                       ▼                                 ▼
                                          [Phase 5A: Human Audio Ingest]    [Phase 5B: VOICEVOX TTS (JA)]
                                          (English & Spanish Audits)        (Mora-Validated Synthesis)
                                                       │                                 │
                                                       └────────────────┬────────────────┘
                                                                        │
                                                                 [Phase 6: Continuous Video Assembly]
                                                                 (Single-Pass CFR 1080p Encode)
                                                                        │
                                                                 [Phase 7: Comprehensive QA Validation]
```

### Phase 1 — Canonical Content & Image Prompts (REVIEW GATE)
1. Agent generates:
   * `output/slides_content_en.txt` (Slide 1 Cover + $N$ Content slides + 2 Vocabulary slides).
   * `output/image_prompts.txt` (Designs 00 to $D+1$ with 16:9 composition, left text-safe zone, and zero-text prohibition).
   * `deck_config.json` (Configuration file specifying paths, slide counts, and layout mappings).
2. **STRICT REVIEW GATE**: Stop execution and wait for explicit user approval (`GO` / `approved`) before proceeding.

### Phase 2 — Multilingual Localization (ES & JA)
1. Upon user approval:
   * `output/slides_content_es.txt` (Natural Latin American Spanish).
   * `output/slides_content_ja.txt` (Authentic modern Japanese).
2. **Semantic Equivalence Rule**: EN = ES = JA in meaning, facts, examples, numbers, and pedagogical purpose. Vocabulary slides feature native target-language headwords and definitions.

### Phase 2B — Japanese Kana Reading Layer (`slides_reading_ja_kana.txt`)
* Derived directly from `slides_content_ja.txt`.
* Continuous orthography without spaces.
* Deterministic readings for kanji, numbers, dates, counters, and abbreviations with standard punctuation (`、`, `。`).
* Zero romaji / ruby markup.

### Phase 3 — Image Generation (16:9 Backgrounds)
* **Composition Rule**: LEFT 40–45% calm text-safe area; RIGHT 55–60% focal storytelling, characters, and scenery. Vocabulary design protects LEFT 50–55%.
* **Zero-Text Enforcement**: Every prompt explicitly includes:
  `No visible text. No letters. No captions. No readable signs or labels. No logo. No signature. No visible watermark. No branding. No UI elements.`
* **Quota-Aware Resume**: Verify existing images in `output/images/` before generating to prevent duplicate API cost.

### Phase 4 — PowerPoint Assembly & Visible Slide Numbering
* Assemble Google-Slides-compatible widescreen 16:9 presentations using `python scripts/build_pptx.py`:
  * `slides_<topic>_en.pptx`, `slides_<topic>_es.pptx`, `slides_<topic>_ja.pptx`.
* **Configurable Slide Numbering**:
  * Cover: Unnumbered.
  * Content slides: Sequential lesson numbering (`01` to `N`).
  * Vocabulary slides: Unnumbered.
  * Background-aware contrast colors (`#1A2433` daytime, `#E1BC95` twilight, `#FFFFFF` night).

### Phase 5 — Audio Production & Preparation
* **5A (English & Spanish)**:
  * Ingest user's recorded tracks from `Audio/English/Tracks` and `Audio/Spanish/Tracks`.
  * Validate presence of exactly $N+2$ tracks named `01` to `N+2`.
  * Run `python scripts/validate_audio.py --audio-dir <path>` to confirm all files are non-empty and decodable.
* **5B (Japanese TTS)**:
  * Launch local Windows DirectML GPU engine via `python scripts/setup_voicevox_local_gpu.py` or run Colab GPU notebook.
  * Synthesize raw narration tracks with `python scripts/synthesize_presentation_audio.py`.

### Phase 6 — Continuous Master Video Assembly (EN / ES / JA)
* Render 3 synchronized Full HD presentation videos with `python scripts/build_presentation_video.py`:
  1. **Continuous Master Audio**: Merges all per-slide audio tracks into a single continuous PCM WAV with **500 ms digital silence** between slides and a **500 ms post-gap** on the final slide.
  2. **Midpoint Visual Transition**: Visual transition occurs at $t = \text{audio\_end} + 250\text{ ms}$ (the exact midpoint of the inter-slide gap), guaranteeing that no slide changes while speech is active.
  3. **Last Slide Persistence**: Slide $N+2$ remains 100% visible throughout its full narration plus the closing margin. The final frame is repeated in the concat list without duration to satisfy FFmpeg concat demuxer requirements.
  4. **CFR Video Encoding**: Always enforce `-vf fps=30,format=yuv420p` in FFmpeg to prevent black-screen artifacts.
  5. **Hardware Acceleration**: Automatic NVIDIA NVENC (`h264_nvenc`) with CPU fallback (`libx264`).
  6. **Timeline & Chapters**: Automatically exports `<topic>_<lang>_timeline.txt` and `<topic>_<lang>_chapters.txt`.

### Phase 7 — Quality Assurance & Verification
* Run automated QA validation:
  ```bash
  # Validate PPTX Decks
  python scripts/validate_pptx.py

  # Validate Audio Tracks
  python scripts/validate_audio.py --audio-dir Audio/English/Tracks --expected-count 53
  python scripts/validate_audio.py --audio-dir Audio/Spanish/Tracks --expected-count 53
  python scripts/validate_audio.py --audio-dir Audio/Japanese --expected-count 53

  # Validate Final Presentation Videos
  python scripts/validate_video.py --video output/summer_vacation_presentation_en.mp4
  python scripts/validate_video.py --video output/summer_vacation_presentation_es.mp4
  python scripts/validate_video.py --video output/summer_vacation_presentation_ja.mp4
  ```

---

## 5. Scripts & Automation Reference

| Script | Purpose |
| :--- | :--- |
| `scripts/build_pptx.py` | Assembles EN, ES, and JA presentations with full-bleed backgrounds and slide numbering. |
| `scripts/validate_pptx.py` | Quality assurance audit for slide counts, dimensions, typography, and numbering. |
| `scripts/check_image_status.py` | Reports completed and missing background image designs. |
| `scripts/setup_voicevox_local_gpu.py` | Health check and launcher for local native VOICEVOX GPU Engine (DirectML). |
| `scripts/synthesize_presentation_audio.py` | Synthesizes Japanese presentation audio with query validation and test mode. |
| `scripts/validate_audio.py` | Verifies presence, non-emptiness, decodability, and format of slide audio tracks. |
| `scripts/build_presentation_video.py` | Universal video builder for EN, ES, and JA with continuous master audio and NVENC. |
| `scripts/validate_video.py` | Audits video stream, dimensions, CFR, audio/video duration match, and frame visibility. |
