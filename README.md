# QuestionForge

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-green.svg)](LICENSE.md)

> AI-assisted framework for creating high-quality educational assessment questions from instructional materials.

## What is QuestionForge?

QuestionForge helps educators create pedagogically sound assessment questions through a structured, AI-assisted process. It bridges the gap between what was actually taught (conducted instruction) and fair assessment by analyzing teaching materials and guiding question development.

**Key Innovation:** Most assessment tools work from curriculum documents. QuestionForge analyzes your actual teaching materials (lectures, slides, recordings) to ensure assessments match what students experienced.

## Features

- **Flexible Entry Points** - Start from materials, objectives, blueprints, or existing questions
- **Methodology Guidance** - Structured M1-M4 process with teacher control at every stage
- **QTI Export** - Generate Inspera-compatible QTI packages
- **15 Question Types** - Multiple choice, text entry, matching, hotspot, and more
- **Self-Learning** - System learns your formatting preferences over time

## Quick Start

```bash
# Clone the repository
git clone https://github.com/tikankika/QuestionForge.git
cd QuestionForge

# Install qf-pipeline (Python)
cd packages/qf-pipeline
pip install -e .

# Install qf-scaffolding (TypeScript)
cd ../qf-scaffolding
npm install
npm run build
```

See [Getting Started](docs/GETTING_STARTED.md) for detailed setup instructions.

## Architecture

QuestionForge consists of two MCP (Model Context Protocol) servers:

| Component | Language | Purpose |
|-----------|----------|---------|
| **qf-scaffolding** | TypeScript | Methodology guidance (M1-M4) |
| **qf-pipeline** | Python | Validation and QTI export |

```
┌─────────────────────────────────────────────────────────────┐
│                     QUESTIONFORGE                            │
├─────────────────────────────────────────────────────────────┤
│  qf-scaffolding          │  qf-pipeline                     │
│  ─────────────────       │  ────────────                    │
│  M1: Content Analysis    │  Validation (Step 2)             │
│  M2: Assessment Design   │  Auto-fix (Step 3)               │
│  M3: Question Generation │  QTI Export (Step 4)             │
│  M4: Quality Assurance   │                                  │
│                          │                                  │
│     Methodology ←────────┼────→ Technical Pipeline          │
└─────────────────────────────────────────────────────────────┘
```

## Workflow Overview

1. **M1: Content Analysis** - Analyze instructional materials, identify emphasis patterns
2. **M2: Assessment Design** - Define objectives, Bloom's distribution, question types
3. **M3: Question Generation** - Create questions aligned with conducted instruction
4. **M4: Quality Assurance** - Review, validate, refine
5. **Pipeline** - Validate format, auto-fix issues, export to QTI

## Documentation

- [Getting Started](docs/GETTING_STARTED.md) - Installation and first project
- [Workflow Guide](WORKFLOW.md) - Complete workflow documentation
- [Architecture Decisions](docs/adr/) - ADRs explaining design choices
- [RFCs](docs/rfcs/) - Design proposals and specifications
- [Technical Specs](docs/specs/) - Detailed specifications

## Project Structure

```
QuestionForge/
├── methodology/           # M1-M4 methodology guides
│   ├── m1/               # Content Analysis (8 stages)
│   ├── m2/               # Assessment Design (9 stages)
│   ├── m3/               # Question Generation (5 stages)
│   ├── m4/               # Quality Assurance (6 stages)
│   └── m5/               # Format Reference
├── packages/
│   ├── qf-pipeline/      # Python MCP - validation & export
│   ├── qf-scaffolding/   # TypeScript MCP - methodology
│   └── qti-core/         # QTI generation logic
├── docs/
│   ├── adr/              # Architecture Decision Records
│   ├── rfcs/             # Request for Comments
│   └── specs/            # Technical specifications
└── qf-specifications/    # Shared specifications (logging schema)
```

## Requirements

- Python 3.10+
- Node.js 18+
- Claude Desktop (for MCP integration)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

CC BY-NC-SA 4.0 - See [LICENSE.md](LICENSE.md)

This means you can:
- ✅ Use for educational purposes
- ✅ Adapt and build upon
- ✅ Share with attribution
- ❌ Use commercially without permission

## Acknowledgments

QuestionForge builds on research in:
- Constructive alignment (Biggs & Tang)
- Formative assessment (Black & Wiliam)
- Swedish assessment research (Lundahl, Hirsh)

---

*QuestionForge - Forging Quality Questions*
