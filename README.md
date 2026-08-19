# Skills

A collection of reusable AI agent skills, workflows, templates, and automation utilities developed and maintained by Favio Leiva.

This repository serves as a centralized hub for modular, domain-agnostic skills designed to be plugged into AI agents (Antigravity, Claude, ChatGPT, etc.) across various projects.

## Available Skills

### [`english-class-slides`](english-class-slides/) (`v1.3`)

A production-grade multimedia workflow for creating multilingual educational presentations (canonical English, Latin American Spanish, natural Japanese) producing **six core deliverables**:
* **3 Google-Slides-compatible PowerPoint presentations** (`.pptx`)
* **3 synchronized Full HD 1080p presentation videos** (`.mp4`)

#### Core Architectural Features
* **Formula**: **One Image + One Short Sentence + Reusable Visual System**
* **Six Deliverables Package**: Complete EN/ES/JA presentations and Full HD synchronized videos.
* **Language-Differentiated Audio Pipeline**:
  * **English & Spanish**: Ingests user-recorded voice tracks (`01.mp3`, `02.mp3`...) with 100% non-destructive preservation (no auto-trimming) and natural lead-in headroom.
  * **Japanese**: Automated VOICEVOX GPU TTS synthesis with continuous Kana orthography and sacrificial startup cue.
* **Continuous Master Audio Architecture**: Single-pass AAC encode with sample-accurate audio/video synchronization, 500 ms inter-slide silence with midpoint visual transitions, and final-slide end-tail protection.
* **Widescreen 16:9 Illustrations**: Left text-safe zone (40–45%), focal storytelling on right, strict zero-text safeguards.
* **Automated Assembly & QA**: Native Google Fonts typography, background-aware contrast numbering, and full multi-point QA audit suite.

See the [english-class-slides documentation](english-class-slides/README.md) for full operational guides and API references.

---

## Repository Structure

```text
skills/
├── README.md
├── LICENSE
├── .gitignore
│
└── english-class-slides/               # Multilingual Slide Generation Skill (v1.3)
    ├── SKILL.md                        # Core agent instructions & workflow rules
    ├── README.md                       # Comprehensive operational guide
    ├── CHANGELOG.md                    # Version history & architectural updates
    ├── templates/                      # Reusable deck configurations & text templates
    ├── examples/                       # Full working examples (e.g. Summer Vacation)
    │   └── summer_vacation_japan/
    ├── notebooks/                      # Colab TTS GPU synthesis notebooks
    └── scripts/                        # PPTX builder, audio/video synthesizers, and QA validators
```

---

## License

This repository is licensed under the [MIT License](LICENSE).
