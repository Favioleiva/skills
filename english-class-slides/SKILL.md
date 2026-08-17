---
name: english-class-slides
version: 1.1
description: Production skill for generating high-quality multilingual educational slide decks (EN canonical, ES, JA) with paired 16:9 anime watercolor image prompts, pedagogical single-sentence layouts, and automated Google-Slides-compatible PPTX assembly.
---

# Skill: English Class Slides (v1.1)

## 1. Overview & Core Philosophy

This skill orchestrates the end-to-end production of reusable, multilingual educational presentations designed specifically for:
* **Target Audience**: A1–A2 English/foreign language learners, young students, and international classrooms.
* **Languages**: Canonical English (`EN`), natural Latin American Spanish (`ES`), and authentic Japanese (`JA`).
* **Pedagogical Formula**: **One Image + One Short Sentence + Reusable Visual System**.
* **Economic Objective**: **Maximize sufficient quality per minute of human work**. Keep designs clean, elegant, and low-friction rather than adding decorative complexity.

---

## 2. Core Staged Workflow (Strict Gate Rules)

```
[Phase 1: Canonical EN + Image Prompts]
                 │
                 ▼
        [Human Review Gate] ────(Feedback / Edits)────┐
                 │                                    │
           (Explicit GO)                              │
                 │                                    │
                 ▼                                    │
    [Phase 2: Localization ES & JA]                   │
                 │                                    │
                 ▼                                    │
   [Optional Phase 3: PPTX Assembly]                  │
                 │                                    │
                 ▼                                    │
        [Validated Presentations] ◄───────────────────┘
```

### PHASE 1 — Canonical English + Image Prompts (MANDATORY GATE)
On the initial request, generate ONLY:
1. `output/slides_content_en.txt`
2. `output/image_prompts.txt`

**STOP IMMEDIATELY FOR USER REVIEW.**
* Do **NOT** generate Spanish or Japanese translations yet.
* Do **NOT** generate image assets yet.
* The English deck is canonical: all pedagogical pacing, vocabulary items, and slide counts are finalized here first.

### PHASE 2 — Localization (Only After Explicit Approval)
Only after the user provides explicit approval (e.g. `GO`, `approved`), generate:
1. `output/slides_content_es.txt`
2. `output/slides_content_ja.txt`
3. *(Optional)* `output/slides_reading_ja_kana.txt` (Japanese Kana Reading Layer for TTS / speech engines)

**Localization Workflow & Sequence**:
```text
Canonical EN -> ES + JA localization -> JA text review -> Japanese kana reading layer -> TTS / external reader
```

**Localization Rules**:
* **Semantic equivalence, not syntactic equivalence**: Reconstruct sentences as a native speaker naturally expresses the proposition.
* **Spanish (`ES`)**: Use natural Latin American Spanish (Peruvian standard). Avoid mechanical translations of English adjective order (e.g. avoid *"Los rápidos trenes bala"*, use *"Los trenes bala llevan a los viajeros a gran velocidad por el campo"*). Use authentic regional terminology when natural (e.g. *"choclo"*, *"bolita de vidrio"*).
* **Japanese (`JA`) Distinction — Visible vs. Spoken Layers**:
  * **Visible Japanese Layer (`slides_content_ja.txt`)**: Natural written Japanese for slide display (standard kanji, hiragana, katakana, and natural orthography).
  * **Spoken Japanese Layer (`slides_reading_ja_kana.txt`)**: Deterministic phonetic input for the external reading/TTS program.
    * **Preserve Natural Katakana**: The reading program supports both hiragana and katakana. Preserve katakana for loanwords, foreign names, and words normally written in katakana (e.g. `ラジオたいそう`, `カブトムシ`, `スイカ`, `ラムネ`, `ビーだま`, `ポイ`, `パラソル`, `ドライブ`, `クラスメイト`, `テーブル`, `ボードゲーム`, `スーツケース`, `スタミナ`, `エーアイ`, `エフエル`). Do NOT force all text into hiragana.
    * **Deterministic Kanji & Number Conversion**: Convert all kanji, dates, counters, numbers, and abbreviations into their intended spoken pronunciation (e.g. `7月下旬` → `しちがつ げじゅん`, `8月` → `はちがつ`, `9月` → `くがつ`, `6本足` → `ろっぽんあし`, `AI` → `エーアイ`, `FL` → `エフエル`).
    * **1-to-1 Alignment & Natural Wording**: Must derive directly from `slides_content_ja.txt` preserving exact 1-to-1 slide ordering (53 entries) without paraphrasing, simplifying, or translating independently.
    * **No Romaji / No Ruby Tags**: Output only directly pronounceable kana without romaji or annotation tags like `漢字(かんじ)`.
    * **Prosodic Punctuation**: Keep commas (`、`), periods (`。`), and spacing to guide speech engines (VOICEVOX, VOICEPEAK, ElevenLabs, Google/Azure TTS) toward natural phrasing and breathing pauses.
    * **TTS Execution Strategy**: Default to the Google Colab workflow (`[Python]_Voicevox_text_to_speach_from_Japanese_text_to_Japanese_Speech.ipynb`) to avoid local Docker/engine setup overhead. Local GPU synthesis is strictly optional and should only be attempted when VOICEVOX Engine is already verified as running locally on `http://127.0.0.1:50021`.
* **Never alter approved Phase 1 files** during Phase 2 unless explicitly instructed.

### PHASE 3 — Automated PPTX Assembly (Optional)
When image assets are ready in `output/images/`, run the assembly pipeline (`scripts/build_pptx.py`) to generate widescreen 16:9 Google-Slides-compatible presentations:
* `output/slides_<topic>_en.pptx`
* `output/slides_<topic>_es.pptx`
* `output/slides_<topic>_ja.pptx`

---

## 3. Pedagogical Slide Architecture

Each standard deck comprises **53 slides** (Slide 1 Cover + 50 Content + 2 Vocabulary) unless a different count is explicitly specified.

```
┌────────────────────────────────────────────────────────┐
│ SLIDE 1: COVER                                         │
│ - Design 00                                            │
│ - Main Title, Subtitle, Author: Favio Leiva (FL)       │
│ - Bottom Frame: Production & AI credits                │
├────────────────────────────────────────────────────────┤
│ SLIDES 2–51: 50 CONTENT SLIDES                         │
│ - Designs 01–12 (grouped by thematic blocks)           │
│ - Exactly ONE short, natural sentence (A1–A2 level)    │
│ - ZERO slide titles, ZERO bullet points, ZERO clutter  │
├────────────────────────────────────────────────────────┤
│ SLIDES 52–53: VOCABULARY (10 items each, 20 total)     │
│ - Design 13 (Dedicated calm background)                │
│ - Slide 52: Vocabulary 1 / Vocabulario 1 / 重要単語 1   │
│ - Slide 53: Vocabulary 2 / Vocabulario 2 / 重要単語 2   │
│ - 1-to-1 semantic parity with native headwords         │
└────────────────────────────────────────────────────────┘
```

### Slide 1 — Cover
* **Top-Left Frame**:
  * Title (Large editorial font)
  * Subtitle (Medium italic/serif)
  * Author: `Favio Leiva (FL)` (Full name once, abbreviated `FL` subsequently)
* **Bottom-Left Separate Frame**:
  * AI-Assisted Production summary
  * 3-line production credits:
    ```text
    AI-assisted content, design and illustrations.

    Skill framework crafted by GPT and FL.
    Content drafts and illustrations created with Gemini.
    Final selection, auditing and revision by FL.
    ```

### Slides 2–51 — Content Slides
* **Rule**: Exactly **ONE short, natural sentence** per slide.
* **No Slide Titles**: The sentence itself is the complete text.
* **Classroom Readability**: 25–30 pt body font size, 1.3 line spacing.
* **Left Safe Area**: Positioned in the left 40–45% negative space of the illustration.

### Slides 52–53 — Vocabulary Slides
* **Rule**: Exactly **10 vocabulary concepts** on Slide 52, and **10 concepts** on Slide 53 (20 total).
* **Target-Language Headwords**: Do **NOT** keep English headwords in Spanish or Japanese decks. Each file uses native headwords and definitions:
  * **EN**: `fireworks — colorful lights in the night sky`
  * **ES**: `fuegos artificiales — luces de colores en el cielo nocturno`
  * **JA**: `花火 — 夜空を彩る光`
* **Format**: Bold headword (22–24 pt) + em-dash + regular definition (20–24 pt).

---

## 4. Visual System & Prompt Engineering

### Dimensions & Layout
* **Aspect Ratio**: 16:9 widescreen landscape.
* **Composition**:
  * **Left 40–45%**: Calm text-safe zone (pale sky, soft water, blurred background, smooth gradient).
  * **Right 55–60%**: Rich storytelling, characters, architecture, focal action.
  * **Vocabulary (Design 13)**: Left 50–55% clean safe zone; subtle framing on right.
* **Art Style**: Studio Ghibli-inspired warm Japanese anime editorial watercolor and gouache.

### Safeguard 1: Preventing "Reference Motif Leakage"
When using a reference image (e.g. Design 00) for visual style consistency, models often copy specific scene props (e.g., morning glory vines, wind chimes) into unrelated scenes (bullet trains, riverbanks, beaches).
* **Requirement**: Prompts inheriting a style reference MUST explicitly separate **STYLE** from **SCENE PROPS**:
  ```text
  Maintain the exact watercolor rendering style, lighting softness, and visual finish of the reference image, but do NOT copy its specific objects, morning glory vines, wind chimes, or porch decorations. Use only the objects explicitly requested for this new scene.
  ```

### Safeguard 2: Zero-Text Enforcement on Cultural Props
Anime illustrations of Japanese festivals, storefronts, and train stations frequently hallucinate pseudo-kanji or gibberish letters.
* **Requirement**: Prompts MUST explicitly require plain, unlettered surfaces:
  ```text
  All paper lanterns must be plain and unlettered. All stall awnings must be plain solid colors. All decorative paper fans must be blank with simple floral patterns. No kanji. No hiragana. No katakana. No Roman letters. No numbers. No logos. No signatures. No readable writing of any kind anywhere in the image.
  ```

---

## 5. Image Generation & Execution Strategy

### Platform Differences: CLI vs. Google AI Studio
1. **Antigravity CLI**:
   * Uses native `generate_image` tool via Cloud Code (`cloudcode-pa.googleapis.com` / `gemini-3.1-flash-image`).
   * Enforces a **strict session rate-limit** (typically `429 RESOURCE_EXHAUSTED` with multi-hour reset windows after generating ~8–9 high-res images).
2. **Google AI Studio / Direct API**:
   * Has significantly higher / unthrottled generation limits for Google AI Pro users.
   * Ideal for rapid batch processing of all 14 prompts in one pass.

### Recommended Hybrid Strategy
* **Step 1 (CLI)**: Generate the Cover (Design 00) and representative style anchor image using `generate_image` in Antigravity CLI. Refine prompts iteratively.
* **Step 2 (Batch)**: If the CLI session hits a 429 quota threshold, export `output/image_prompts.txt` and generate the remaining batch in **Google AI Studio** or via a direct API script.
* **Step 3 (Resume Logic)**: Run `scripts/check_image_status.py` to inspect `output/images/`.

### Quota Recovery & Resume Protocol (MANDATORY)
* **Never discard completed images** or restart from Design 00 upon hitting a quota limit.
* Identify existing files (`design_00_cover.png`, `design_01.png`, etc.) and resume generation from the first missing design index.
* Report status clearly: `Completed: Designs 00–08 | Pending: Designs 09–13`.

---

## 6. Background-Aware Typography & Presets

To ensure optimal contrast across varied watercolor backgrounds, use these established presets:

| Scene Type | Example Designs | Text Position | Text Color | Font Specs |
| :--- | :--- | :--- | :--- | :--- |
| **Standard Daytime** | 01, 02, 03, 04, 06, 09, 10, 11, 12 | `L: 0.90"`, `T: 2.20"`, `W: 4.70"` | `#1A2433` (Charcoal Navy) | 26–30 pt Bold, 1.3 line spacing |
| **Open Horizon / Travel** | 05 (Shinkansen / Planes) | `L: 0.30"`, `T: 2.20"`, `W: 4.70"` | `#1A2433` (Charcoal Navy) | 28–30 pt Bold (uses wide left space) |
| **Twilight / Matsuri** | 07 (Festival Night) | `L: 0.50"`, `T: 1.00"`, `W: 4.70"` | `#E1BC95` (Warm Peach/Gold) | 28–30 pt Bold (sits in dark twilight sky) |
| **Night / Fireworks** | 08 (Hanabi Riverbank) | `L: 0.90"`, `T: 2.83"`, `W: 4.70"` | `#FFFFFF` (Pure White) | 28–30 pt Bold (sits in dark river sky) |
| **Vocabulary 1 & 2** | 13 (Dedicated Clean Background) | Title: `T: 0.75"`<br>List: `T: 1.32"`, `W: 7.10"` | Headword: `#102238`<br>Def: `#1A2433` | Title: 25 pt Bold<br>Headword: 24 pt Bold<br>Def: 20–24 pt Regular |

### Font System (Google Slides Native)
* **English & Spanish**:
  * Cover Title & Subtitle: `Cormorant Garamond` (Semibold / Medium)
  * Body, Author, Credits, Vocabulary: `Nunito Sans` (Bold / Regular)
* **Japanese**:
  * Cover Title & Subtitle: `Noto Serif JP` (Bold / Medium)
  * Body, Author, Credits, Vocabulary: `Noto Sans JP` (Medium / Bold)

---

## 7. Background Library & Reuse Strategy

Before generating new illustrations, check if existing approved backgrounds from previous decks can be reused:
* **Reusable Categories**: Beach, Matsuri, Shinkansen, Countryside, Obon, Hanabi Fireworks, Tatami Room/Engawa, School Gate, Autumn Sunset, Sakura Spring, Winter Holiday.
* **Economic Threshold**: A background is acceptable when it looks good, fits the visual family, provides text safe space, and contains zero unwanted text. **Do NOT regenerate an otherwise strong image because a single minor noun is absent.**

---

## 8. Quality Assurance & Validation Checklist

Before delivering final presentations, execute `python scripts/validate_pptx.py`:

1. **Slide Count**: Exactly 53 slides in each presentation (1 Cover + 50 Content + 2 Vocabulary).
2. **One-Sentence Rule**: Zero slide titles on Slides 2–51; exactly one sentence per content slide.
3. **Vocabulary Count**: Exactly 10 items on Slide 52 and 10 items on Slide 53 (20 total).
4. **Multilingual Parity**: EN, ES, and JA slide counts and semantic meanings are 1-to-1 aligned.
5. **No Text Overflow**: No text frames overflow beyond slide boundaries; zero font reductions below 24 pt on content slides.
6. **Full-Bleed Images**: Background images fill the 16:9 canvas (13.333″ × 7.500″) without distortion or white borders.
7. **Color Contrast**: Dark scenes (07, 08) use light text (`#E1BC95`, `#FFFFFF`); daytime scenes use dark charcoal (`#1A2433`).
