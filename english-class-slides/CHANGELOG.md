# Changelog

All notable changes to the `english-class-slides` skill will be documented in this file.

---

## [1.1] — 2026-08-17

### Added
- **Formal Pedagogical Slide Architecture**:
  - Slide 1: Cover Slide with separated Title block and bottom AI-Assisted Production / Credits block.
  - Slides 2–51: Standardized **One Image + One Short Sentence** rule for A1–A2 learners with zero slide titles.
  - Slides 52–53: Dedicated Vocabulary architecture with 10 concepts per slide (20 total).
- **Target-Language Vocabulary Localization**: Replaced the v1.0 English headword constraint with true 1-to-1 semantic localization (native headwords and definitions in Spanish and Japanese).
- **Japanese Kana Reading Layer (`slides_reading_ja_kana.txt`)**:
  - Replaced the initial `slides_reading_ja_hiragana.txt` draft with natural kana representation (`slides_reading_ja_kana.txt`).
  - Preserves authentic katakana for loanwords, foreign names, and onomatopoeia (e.g. `ラジオたいそう`, `カブトムシ`, `スイカ`, `ラムネ`, `エーアイ`, `エフエル`) since external TTS engines natively read both hiragana and katakana.
  - Converts kanji, numbers, counters, dates, and abbreviations into deterministic spoken phonetic readings with prosodic punctuation (`、`, `。`).
- **Prompt Engineering Safeguards**:
  - *Motif-Leakage Prevention*: Added explicit style-vs-scene separation to prevent carry-over of anchor props (e.g. morning glory vines, wind chimes) into unrelated scenes.
  - *Zero-Text Enforcement*: Added strict explicit prompts for plain unlettered lanterns, blank stall awnings, and plain fans to prevent hallucinated kanji/kana.
- **Image Generation & Quota Recovery Strategy**:
  - Documented platform throughput differences between Antigravity CLI and Google AI Studio / Direct API.
  - Introduced quota recovery and resume logic to prevent redundant regeneration and preserve completed images upon hitting 429 limits.
- **Background-Aware Typography Presets**:
  - Added coordinate and color presets for daytime (`#1A2433`), travel open horizon (`Left: 0.30"`), twilight matsuri (`#E1BC95`, `Top: 1.00"`), and fireworks night (`#FFFFFF`, `Top: 2.83"`).
- **Automated PPTX Assembly Pipeline**:
  - Added `scripts/build_pptx.py` generating native 16:9 widescreen PowerPoint decks with Google Fonts (`Cormorant Garamond`, `Nunito Sans`, `Noto Serif JP`, `Noto Sans JP`).
  - Added `scripts/validate_pptx.py` for automated QA auditing.
  - Added `scripts/check_image_status.py` for tracking asset completion.
- **Background Library & Economic Reuse Policy**: Added guidelines for building and reusing approved background assets to reduce generation overhead for future topics.
- **VOICEVOX Audio Synthesis Production Rule**: Standardized continuous natural Japanese kana text without artificial spaces, and global 0.5s native pre-roll and post-roll padding (`prePhonemeLength = 0.5`, `postPhonemeLength = 0.5`) to protect initial consonant attacks from playback DAC/decoder clipping without artificial mora manipulation.

### Changed
- Refined Spanish translation instructions to enforce natural Latin American / Peruvian syntax and vocabulary (e.g. *"bolita de vidrio"*, *"choclo"*) over direct English calques.
- Standardized Cover author credit format: `Favio Leiva (FL)`.

---

## [1.0] — Initial Release

- Initial staged multilingual workflow (Phase 1 English + Prompts, Phase 2 Spanish & Japanese).
- 16:9 widescreen anime watercolor illustration prompt guidelines.
- Basic text template structure.
