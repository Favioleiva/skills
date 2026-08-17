# Skills

A collection of reusable AI agent skills, workflows, templates, and automation utilities developed and maintained by Favio Leiva.

This repository serves as a centralized hub for modular, domain-agnostic skills designed to be plugged into AI agents (Antigravity, Claude, ChatGPT, etc.) across various projects.

## Available Skills

### [`english-class-slides`](english-class-slides/)

A production-grade, multilingual educational slide deck generator designed for international classrooms and A1–A2 language learners.

* **Formula**: **One Image + One Short Sentence + Reusable Visual System**
* **Languages**: Canonical English (`EN`), natural Latin American Spanish (`ES`), and authentic Japanese (`JA`).
* **Speech / TTS Layer**: Dedicated Japanese Kana reading layer (`slides_reading_ja_kana.txt`) preserving natural katakana for loanwords and foreign names.
* **Visual Pairing**: 16:9 widescreen Japanese anime watercolor and gouache illustrations with left text-safe zones and strict zero-text safeguards.
* **Assembly Pipeline**: Automated Google-Slides-compatible PowerPoint (`.pptx`) generator with native Google Fonts and contrast-aware typography presets.
* **Asset Tracking & Quota Resume**: Resilient image asset tracking and quota-recovery logic.

See the [english-class-slides documentation](english-class-slides/README.md) for detailed installation and usage instructions.

---

## Repository Structure

```text
skills/
├── README.md
├── LICENSE
├── .gitignore
│
└── english-class-slides/               # Multilingual Slide Generation Skill (v1.1)
    ├── SKILL.md                        # Core agent instructions & workflow rules
    ├── README.md                       # Comprehensive operational guide
    ├── CHANGELOG.md                    # Version history & architectural updates
    ├── templates/                      # Reusable deck configurations & text templates
    ├── examples/                       # Full working examples (e.g. Summer Vacation)
    │   └── summer_vacation_japan/
    └── scripts/                        # PPTX builder, asset tracker, and QA validator
```

---

## License

This repository is licensed under the [MIT License](LICENSE).
