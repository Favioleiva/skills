# English Class Slides Skill (`v1.1`)

A production-grade Antigravity agent skill for creating **multilingual educational slide decks** (English canonical, Latin American Spanish, authentic Japanese) with paired 16:9 anime watercolor backgrounds, single-sentence pedagogical layouts, and automated Google-Slides-compatible PowerPoint assembly.

---

## 1. Features & Design Philosophy

* **Target Audience**: A1–A2 English/foreign language learners, Japanese classroom settings, international education.
* **Pedagogical Core**: **One Image + One Sentence**. Eliminates cognitive overload and maximizes read-aloud clarity.
* **Staged Human-in-the-Loop Review**: Strict gating ensures English canonical content and image prompts are audited before localization begins.
* **100% Google Slides Native**: Automated assembly produces `.pptx` presentations styled with Google Fonts (`Cormorant Garamond`, `Nunito Sans`, `Noto Serif JP`, `Noto Sans JP`) ready for 1-click import into Google Drive.
* **Background-Aware Typography**: Automatically adapts text positioning and colors for daytime (`#1A2433`), twilight (`#E1BC95`), and fireworks night (`#FFFFFF`) scenes.
* **Production Economics**: Designed to maximize quality per minute of human effort while avoiding over-engineered presentations.

---

## 2. Installation & Directory Setup

Place the `english-class-slides/` folder in your workspace or global Antigravity skills directory:

### Workspace Installation:
```text
your-project/
└── .agents/
    └── skills/
        └── english-class-slides/
            ├── SKILL.md
            ├── README.md
            ├── CHANGELOG.md
            ├── templates/
            ├── examples/
            └── scripts/
```

### Add to `AGENTS.md`:
```markdown
# Slide Deck Generation
Use the workspace skill `.agents/skills/english-class-slides/SKILL.md` for all slide-deck creation tasks.
```

---

## 3. Workflow Overview

### Phase 1: Canonical English + Image Prompts
1. Agent creates:
   * `output/slides_content_en.txt` (Slide 1 Cover + 50 single-sentence content slides + 2 vocabulary slides).
   * `output/image_prompts.txt` (Designs 00–13 with 16:9 composition, left safe zones, and zero-text rules).
2. **STOP FOR REVIEW**: Human audits the English phrasing, vocabulary selection, and visual prompts.

### Phase 2: Multilingual Localization
1. After receiving explicit `GO` or `approved`:
   * `output/slides_content_es.txt` (Natural Latin American Spanish).
   * `output/slides_content_ja.txt` (Culturally authentic Japanese).
   * *(Optional)* `output/slides_reading_ja_kana.txt` (Japanese Kana Reading Layer preserving natural katakana for TTS engines).
2. **Semantic Equivalence Rule**: Sentences and vocabulary are translated naturally for the target audience rather than mimicking English syntax.

### Phase 3: Slide Deck Assembly (Optional Automated Step)
1. Ensure image backgrounds exist in `output/images/` (`design_00_cover.png` through `design_13.png`).
2. Run the build script:
   ```bash
   python scripts/build_pptx.py --config templates/deck_config.template.json
   ```
3. Run the automated QA validator:
   ```bash
   python scripts/validate_pptx.py --config templates/deck_config.template.json
   ```

---

## 4. Image Generation Strategy & Quota Management

* **Antigravity CLI vs. Google AI Studio**:
  * **CLI**: Ideal for initial style anchoring (Design 00 Cover) and prompt iteration, but may hit Cloud Code quota limits (`429 RESOURCE_EXHAUSTED`) during large multi-image runs.
  * **Google AI Studio / Direct API**: Recommended for full 14+ image batch generation with Google AI Pro accounts without CLI session interruptions.
* **Resume Logic**:
  * Run `python scripts/check_image_status.py` to inspect missing vs. completed designs.
  * Never restart from Design 00 or overwrite existing approved images.

---

## 5. Script Utilities Reference

* `scripts/check_image_status.py`: Inspects `output/images/` and reports completed and pending design numbers.
* `scripts/build_pptx.py`: Generates the 3 `.pptx` decks using full-bleed backgrounds, split textframes, dynamic font sizing, and background-aware contrast colors.
* `scripts/validate_pptx.py`: Verifies slide count (53), 16:9 dimensions, single-sentence content slides, vocabulary item counts, and font size compliance.

---

## 6. License & Credits
* **Author**: Favio Leiva (FL)
* **Framework**: Crafted with GPT and FL; drafts and illustrations with Gemini.
