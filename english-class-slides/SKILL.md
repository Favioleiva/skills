---
name: english-class-slides
description: Generic production-grade multimedia workflow for creating multilingual slide decks (canonical English, Latin American Spanish, natural Japanese), continuous kana reading layers, 16:9 anime watercolor backgrounds, automated PowerPoint assembly with configurable slide numbering, optional VOICEVOX audio synthesis, and synchronized Full HD presentation video generation.
---

# English Class Slides Skill (`v1.2`)

A comprehensive, topic-independent production workflow for creating **multilingual educational presentations** (A1–A2 English learners, Japanese classroom settings, and international education) with optional synchronized audio narration and 1080p presentation video generation.

---

## 1. Pedagogical Architecture & Core Rules

* **Pedagogical Core**: **One Image + One Sentence**. Eliminates cognitive overload and maximizes read-aloud clarity for A1–A2 learners.
* **Canonical Language**: English (`slides_content_en.txt`) is canonical.
* **Slide Structure**:
  * **Slide 1**: Cover Slide (Creative Title + Subtitle + Author credit + AI-Assisted Production metadata block).
  * **Slides 2 to N+1**: $N$ Content Slides (Single short, engaging sentence; zero slide titles).
  * **Slides N+2 & N+3**: 2 Dedicated Vocabulary Slides (10 items each, 20 unique concepts total).
* **Total Slide Count**: Exactly $N + 2$ slides.
* **Design Allocation**: Exactly $D$ content designs + 1 dedicated Vocabulary design $\implies$ Total image prompts = $D + 1$. Both vocabulary slides use Design $D+1$.

---

## 2. Six-Phase Production Workflow

```text
[Phase 1: Canonical English & Prompts] ──(Human Review Gate)──► [Phase 2: Localization ES/JA]
                                                                        │
                                                                 [Phase 2B: Kana Layer]
                                                                        │
                                                                 [Phase 3: Image Generation]
                                                                        │
                                                                 [Phase 4: PPTX Assembly & Numbering]
                                                                        │
                                                      ┌─────────────────┴─────────────────┐
                                                      ▼ (Optional)                        ▼ (Optional)
                                            [Phase 5: Audio Synthesis]           [Phase 6: Video Assembly]
```

### Phase 1 — Canonical Content & Image Prompts (STOP FOR REVIEW)
1. Agent generates:
   * `output/slides_content_en.txt` (Slide 1 Cover + $N$ Content slides + 2 Vocabulary slides).
   * `output/image_prompts.txt` (Designs 00 to $D+1$ with 16:9 composition, left text-safe zone, and zero-text prohibition).
   * `deck_config.json` (Configuration file specifying paths, slide counts, and layout mappings).
2. **STRICT REVIEW GATE**: Stop execution and wait for explicit user approval before proceeding.

### Phase 2 — Multilingual Localization (ES & JA)
1. Upon explicit user approval (`GO` / `approved`):
   * `output/slides_content_es.txt` (Natural Latin American Spanish).
   * `output/slides_content_ja.txt` (Authentic modern Japanese).
2. **Semantic Equivalence Rule**: EN = ES = JA in meaning, facts, examples, numbers, and pedagogical purpose. Vocabulary slides feature native target-language headwords and definitions.

### Phase 2B — Japanese Kana Reading Layer (`slides_reading_ja_kana.txt`)
When Japanese narration or TTS is required, generate `slides_reading_ja_kana.txt` derived directly from `slides_content_ja.txt`:
* **Continuous Japanese Orthography**: **Do NOT insert artificial spaces between words**. VOICEVOX interprets whitespace as phrase boundaries, causing fragmented prosody.
* **Preserve Natural Katakana**: Loanwords, foreign names, and onomatopoeia remain in katakana (e.g. `ラジオたいそう`, `カブトムシ`, `スイカ`, `ラムネ`).
* **Deterministic Phonetic Readings**: Convert kanji, numbers, dates, counters, and abbreviations into spoken readings with standard Japanese punctuation (`、`, `。`).
* **Zero Romaji / Ruby**: No latin characters, furigana tags, or unexpected CJK ideographs.

### Phase 3 — Image Generation (16:9 Backgrounds)
* **Composition Rule**: LEFT 40–45% calm text-safe area; RIGHT 55–60% focal storytelling, characters, and architecture. Vocabulary design protects LEFT 50–55%.
* **Zero-Text Enforcement**: Every prompt explicitly includes:
  `No visible text. No letters. No captions. No readable signs or labels. No logo. No signature. No visible watermark. No branding. No UI elements.`
* **Quota-Aware & Resume**: Verify existing images in `output/images/` before generating to prevent duplicate API cost.

### Phase 4 — PowerPoint Assembly & Phase 4B: Slide Numbering
* Assemble Google-Slides-compatible widescreen 16:9 presentations using `python scripts/build_pptx.py`:
  * `slides_<topic>_en.pptx`, `slides_<topic>_es.pptx`, `slides_<topic>_ja.pptx`.
* **Configurable Slide Numbering**:
  * Cover: Unnumbered.
  * Content slides: Sequential lesson numbering (`01` to `N`).
  * Position, font size (14pt Bold), and background-aware contrast colors (`#1A2433` daytime, `#E1BC95` twilight, `#FFFFFF` night) configured in `deck_config.json`.

---

## 3. Phase 5 — Optional Audio Synthesis (VOICEVOX Workflow)

### Route A: Local Windows DirectML / GPU
* Direct native execution via `tools/windows-directml/run.exe --use_gpu` binding to `http://127.0.0.1:50021`. Zero Docker required.
* Verified compatible with NVIDIA RTX 3060 and DirectML-supported GPUs.

### Route B: Google Colab Direct Linux Engine
* Zero Docker daemon dependency. Direct download of official Linux GPU/CUDA binary (`voicevox_engine-linux-nvidia`), running with `--use_gpu`.

### Synthesis Best Practices
* **Query Validation**: Inspect returned `query["kana"]` against submitted text before synthesis.
* **Test Mode**: Synthesize sample slides (`[1, 2, 10, 30]`) to audit audio quality before full batch.
* **Native Pre/Post Padding (Synthesis Headroom)**: Use `prePhonemeLength = 0.50` and `postPhonemeLength = 0.50` as standard synthesis padding headroom at the uncompressed PCM WAV stage. Do not destructively slice, trim, or manipulate moras. *(Important: Silence padding alone does not solve playback-start DAC/decoder clipping; see Phase 6 for the empirical playback solution)*.

---

## 4. Phase 6 — Optional Presentation Video Assembly

### Continuous Master Audio Architecture (Strategy B)
Controlled experiments established that silence padding alone does not protect cold-start playback from initial-consonant clipping. The validated production architecture uses an active sacrificial startup signal (`ピッ` + 150ms gap) only once at playback onset, merges all slide narrations into **one continuous Master Audio WAV** track, and renders the entire video with a **single continuous AAC encode** in one FFmpeg pass:
1. **Master Track Assembly**: Chain slide audio tracks with configurable inter-slide silence (0.50s) and a single startup audio cue (`ピッ` + 150ms gap) to initialize the playback DAC/decoder once at $t=0$. Inside this active master stream, subsequent slides require no individual dummy sounds and maintain clean consonant attacks.
2. **CFR Still-Image Filter**: Always include `-vf fps=30,format=yuv420p` when using FFmpeg's concat demuxer on still PNG images to prevent black-screen rendering.
3. **Repeat Final Image**: In image concat list files, repeat the last frame without duration so FFmpeg honors its full display time.
4. **Hardware Acceleration**: Use NVIDIA NVENC (`h264_nvenc`) with clean fallback to CPU (`libx264`).
5. **Timeline & Chapters**: Generates synchronized `<topic>_<lang>_timeline.txt` and `<topic>_<lang>_chapters.txt` for YouTube navigation.

---

## 5. Scripts & Automation Reference

| Script | Purpose |
| :--- | :--- |
| `scripts/build_pptx.py` | Assembles EN / ES / JA presentations with full-bleed backgrounds and slide numbering. |
| `scripts/validate_pptx.py` | Quality assurance audit for slide counts, dimensions, typography, and numbering. |
| `scripts/check_image_status.py` | Reports completed and missing background image designs. |
| `scripts/setup_voicevox_local_gpu.py` | Health check and launcher for local native VOICEVOX GPU Engine. |
| `scripts/synthesize_presentation_audio.py` | Synthesizes Japanese presentation audio with query validation and test mode. |
| `scripts/validate_audio.py` | Verifies presence, non-emptiness, and formatting of slide audio tracks. |
| `scripts/build_presentation_video.py` | Renders synchronized Full HD 1080p MP4 videos with continuous master audio. |
| `scripts/validate_video.py` | Audits video stream, dimensions, CFR, audio/video duration match, and frame visibility. |
