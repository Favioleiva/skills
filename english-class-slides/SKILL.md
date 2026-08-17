# Skill: English Class Slides — Staged Multilingual TXT Workflow

## Purpose
Create English-class slide decks in a staged review workflow. English is always the canonical/source deck. Image prompts are created alongside English. Spanish and Japanese are generated only after explicit user approval.

This skill creates plain-text deliverables only. Do not create PPTX/PDF/DOCX unless explicitly requested in a later task.

## Required workflow — DO NOT SKIP GATES

### PHASE 1 — English + image prompts
On the initial request, generate ONLY:
1. `output/slides_content_en.txt`
2. `output/image_prompts.txt`

Then STOP. Do not generate Spanish or Japanese yet. Tell the user Phase 1 is ready for review and wait for explicit approval such as `GO`, `approved`, or an equivalent instruction.

If the user requests corrections, edit the English deck and/or image prompts, re-run QA, save the corrected files, and STOP again for review.

### PHASE 2 — translations, only after explicit approval
After explicit approval of Phase 1, generate ONLY:
3. `output/slides_content_es.txt`
4. `output/slides_content_ja.txt`

Spanish and Japanese must be translations of the FINAL APPROVED English deck, never independent rewrites.

Do not alter `slides_content_en.txt` or `image_prompts.txt` during Phase 2 unless the user explicitly asks.

## Preferred input
TOPIC: [topic]
CONTENT SLIDES: [number of ordinary teaching slides]
DESIGNS: [number of visual designs]
LEVEL: [English learner level]
SPECIAL CONTENT: [required topics]
AUDIENCE: [optional]
TONE: [optional]
VISUAL STYLE: [optional]

If the user says `SLIDES: N`, interpret N as CONTENT SLIDES unless they explicitly say the count includes vocabulary slides.

Defaults:
- CONTENT SLIDES: 50
- DESIGNS: 12
- LEVEL: A1–A2
- English: clear international English
- Visual format: 16:9 landscape
- Text-safe zone: left 40–45%

## Slide count rule
The deck consists of:
- N ordinary content slides requested by the user, PLUS
- 2 mandatory vocabulary slides at the end.

Therefore TOTAL SLIDES = CONTENT SLIDES + 2.

Example: CONTENT SLIDES: 50 => TOTAL SLIDES: 52.

The vocabulary slides are always the final two slides:
- Slide N+1: Vocabulary 1 — 10 important English words from the deck
- Slide N+2: Vocabulary 2 — 10 additional important English words from the deck

Use 20 unique vocabulary items total. Prefer high-value words that actually appear in, or are directly necessary for, the approved deck. Avoid duplicates and trivial function words.

## Canonical language rule
English is the canonical/source version.

Workflow:
ENGLISH SEMANTIC CONTENT -> SPANISH TRANSLATION
                         -> JAPANESE TRANSLATION

Never use Spanish or Japanese to redefine the English meaning.

## Phase 1 file: `output/slides_content_en.txt`
Use this format:

PRESENTATION TITLE: [creative English title]
SUBTITLE: [optional]
LANGUAGE: English
CONTENT SLIDES: [N]
VOCABULARY SLIDES: 2
TOTAL SLIDES: [N+2]
CONTENT DESIGNS: [D]
TOTAL IMAGE DESIGNS: [D+1]

SLIDE 1
Design: 1
Title: ...
Text: ...

[continue through content slide N]

SLIDE N+1
Design: [appropriate design]
Title: Vocabulary 1
Words:
1. word — short learner-friendly English meaning
...
10. word — short learner-friendly English meaning

SLIDE N+2
Design: [appropriate design]
Title: Vocabulary 2
Words:
1. word — short learner-friendly English meaning
...
10. word — short learner-friendly English meaning

## Phase 2 Spanish file: `output/slides_content_es.txt`
It must have exactly the same slide numbers, order, design assignments, claims, examples, dates, names, quantities, certainty, and pedagogical purpose as the approved English file.

For ordinary slides:
DIAPOSITIVA N
Diseño: D
Título: [natural equivalent]
Texto: [natural semantically equivalent Spanish]

For vocabulary slides, KEEP THE SAME ENGLISH HEADWORDS so they remain useful for English class, and translate the meanings:

DIAPOSITIVA N+1
Diseño: D
Título: Vocabulario 1
Palabras:
1. English word — significado breve en español
...

Use neutral natural Spanish. Do not add explanations absent from English.

## Phase 2 Japanese file: `output/slides_content_ja.txt`
It must have exactly the same slide numbers, order, design assignments, claims, examples, dates, names, quantities, certainty, and pedagogical purpose as the approved English file.

For ordinary slides:
スライド N
デザイン: D
タイトル: [natural equivalent]
本文: [natural semantically equivalent Japanese]

For vocabulary slides, KEEP THE SAME ENGLISH HEADWORDS and translate the meanings:

スライド N+1
デザイン: D
タイトル: Vocabulary 1 / 重要単語 1
単語:
1. English word — 日本語の短い意味
...

Use natural modern classroom Japanese. Common kanji are preferred. Do not add furigana unless requested. Do not over-explain Japanese cultural concepts.

## Translation equivalence — mandatory
For every ordinary slide, EN = ES = JA in semantic content.

Translations may change grammar, word order, idiom, or sentence segmentation for naturalness, but must not:
- add or omit facts;
- add examples in only one language;
- soften or intensify claims;
- change dates, numbers, places, people, activities, or cultural references;
- change singular/plural or time reference in a meaning-changing way;
- make Japanese more detailed than English;
- simplify Spanish until information disappears.

For vocabulary slides:
- the 20 English headwords must be identical in all three files;
- the short definitions/translations must be equivalent;
- order must be identical.

## Content style
- Give the presentation a creative title.
- Build a deliberate progression: opening/context -> core experiences/concepts -> cultural/detail sections -> memorable conclusion -> vocabulary.
- Keep English concise, natural, classroom-friendly, and matched to LEVEL.
- Prefer short sentences/compact slide lines over paragraphs.
- Avoid unnecessary repetition.
- Keep cultural/factual claims accurate and avoid stereotypes or invented traditions.

## Design allocation
Create exactly D CONTENT designs, plus 1 mandatory dedicated VOCABULARY design.
Therefore TOTAL IMAGE DESIGNS = D + 1.
- Divide the N content slides approximately evenly among Designs 1..D while respecting thematic boundaries.
- Each content slide belongs to exactly one content design.
- Keep each content design on a contiguous range where practical.
- Give every design a short evocative name.
- Both vocabulary slides MUST use Design D+1.
- Design D+1 is exclusively the Vocabulary design and must not be counted inside the user-requested D content designs.
- The Vocabulary design should preserve the deck's visual identity but be calmer and more spacious than ordinary content designs.

## Phase 1 file: `output/image_prompts.txt`
This file covers all requested designs and includes the vocabulary slides in the appropriate final design assignment.

Format:
IMAGE PROMPTS
CONTENT DESIGNS: [D]
TOTAL IMAGE DESIGNS: [D+1]
FORMAT: 16:9 landscape
DEFAULT TEXT ZONE: left 40–45%

DESIGN 1 — [name]
Slides: [range]
Visual purpose: ...
Prompt:
[complete prompt]

[continue through DESIGN D]

DESIGN D+1 — Vocabulary
Slides: [N+1]-[N+2]
Visual purpose: Dedicated clean vocabulary background that visually belongs to this presentation.
Prompt:
[complete vocabulary-specific prompt]

Vocabulary prompt requirements:
- same overall visual language, palette, rendering quality, and thematic identity as the content designs;
- substantially calmer composition with approximately LEFT 50–55% clean text-safe space because each vocabulary slide contains 10 entries;
- decorative/theme-specific elements concentrated on the RIGHT 45–50% and/or subtle outer edges;
- no focal objects, faces, high contrast, or busy texture behind the vocabulary list;
- designed to work unchanged for BOTH vocabulary slides;
- obey the same no-text/no-logo/no-watermark prohibition as every other prompt.

## Permanent image composition rules
Every prompt must specify:
- 16:9 landscape presentation background;
- polished educational/editorial illustration or requested style;
- LEFT 40–45% calm text-safe area;
- RIGHT 55–60% contains main characters, faces, important objects, architecture, and detailed storytelling;
- no important focal information behind the left text zone;
- left zone visually integrated with the scene using sky, wall, gradient, sand, water, distant landscape, darkness, defocused foliage, subtle texture, etc.;
- enough tonal uniformity for several lines of readable slide text;
- coherent rendering language and quality across all designs in the deck.

Every prompt MUST explicitly include this prohibition:
`No visible text. No letters. No captions. No readable signs or labels. No logo. No signature. No visible watermark. No branding. No UI elements.`

If the scene normally contains labeled signs, bottles, banners, packages, lanterns, school signs, etc., request blank/unreadable decorative surfaces.

## Image generation is NOT part of this skill
This skill writes image prompts only. It does not call an image model and does not generate PNG/JPG files. Image generation should be handled by a separate skill/task after `image_prompts.txt` is approved.

## Phase 1 QA before stopping for review
Verify:
1. English has exactly N content slides + 2 vocabulary slides.
2. Total slide count is N+2.
3. Exactly D content designs + 1 dedicated vocabulary design exist (D+1 image prompts total).
4. Slides are consecutive and each has one design assignment.
5. Designs 1..D cover content slides exactly once; both vocabulary slides use Design D+1.
6. Vocabulary slides contain exactly 10 items each, 20 unique English headwords total.
7. Vocabulary is relevant to the deck and appropriate to LEVEL.
8. Every image prompt says 16:9.
9. Content image prompts protect left 40–45% for text; the Vocabulary prompt protects approximately left 50–55%.
10. Every image prompt puts focal detail primarily on the right.
11. Every image prompt contains the full no-text/no-logo/no-watermark prohibition.
12. `slides_content_en.txt` contains no image prompts and `image_prompts.txt` contains no unnecessary slide body copy.

Then STOP and wait for approval.

## Phase 2 QA before completion
Verify:
1. ES and JA have exactly the same total slide count as approved EN.
2. Slide numbers and design assignments match EN exactly.
3. Every ordinary slide is semantically equivalent across EN/ES/JA.
4. No substantive information was added or removed.
5. Titles preserve meaning and function.
6. Dates, numbers, names, places, examples, and certainty match.
7. The 20 English vocabulary headwords are identical and in the same order in EN/ES/JA.
8. Vocabulary meanings are equivalent in Spanish and Japanese.
9. Phase 2 did not silently modify the approved English or image-prompt files.

## Strict staged output behavior
Initial run: create ONLY
- `output/slides_content_en.txt`
- `output/image_prompts.txt`

After explicit user approval: create ONLY
- `output/slides_content_es.txt`
- `output/slides_content_ja.txt`

Never bypass the review gate.

## Japanese VOICEVOX Audio Synthesis Production Rule
- Use continuous natural Japanese kana text (`slides_reading_ja_kana.txt` with zero artificial whitespace).
- Use 0.5 seconds of native VOICEVOX pre-roll (`prePhonemeLength = 0.5`) and post-roll (`postPhonemeLength = 0.5`) for each isolated slide audio.
- Do not reinforce individual initial moras unless a future controlled diagnostic demonstrates a separate phonetic problem.

