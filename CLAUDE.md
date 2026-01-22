# QuestionForge

## Overview

QuestionForge is a teacher-led, AI-assisted framework for creating high-quality assessment questions that export to QTI format for Inspera LMS. It consists of two focused MCPs: one for pedagogical scaffolding (methodology guidance) and one for the technical pipeline (validation and export).

**Core workflow:** Instructional Materials → Pedagogical Scaffolding (M1-M4) → Markdown Questions → Pipeline (Build/Validate/Export) → QTI Package

## Quick Start

```bash
# Project structure
cd /Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge

# MCPs (to be implemented)
packages/qf-scaffolding/   # TypeScript - methodology guidance
packages/qf-pipeline/      # Python - validation & export
```

## Project Status

- **Phase:** IMPLEMENT (qf-pipeline active, shared session ready)
- **Next:** qf-scaffolding (M1-M4) or Step 3 Decision Tool
- **Created:** 2026-01-02
- **Method:** ACDM v1.0
- **Name Origin:** "Forge" implies craftsmanship in creating questions

## Architecture (Two MCPs)

```
┌─────────────────────────────────────────────────────────────┐
│  MCP 1: qf-scaffolding (TypeScript)                         │
│  ├── M1: Content Analysis (what was taught?)                │
│  ├── M2: Assessment Planning (types, distribution, labels)  │
│  ├── M3: Question Generation (create questions)             │
│  └── M4: Quality Assurance (pedagogical validation)         │
│  PATTERN: Non-linear, flexible entry points                 │
│  OUTPUT: Markdown questions                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  MCP 2: qf-pipeline (Python)                                │
│  ├── Step 1: Guided Build (question-by-question)            │
│  ├── Step 2: Validator (batch validation)                   │
│  ├── Step 3: Decision (QTI questions vs Question Set)       │
│  └── Step 4: Export (generate QTI package)                  │
│  PATTERN: Linear with validation loops                      │
│  OUTPUT: QTI package for Inspera                            │
└─────────────────────────────────────────────────────────────┘
```

## Structure

```
QuestionForge/
├── packages/
│   ├── qf-scaffolding/     # TypeScript MCP (methodology) ⬜
│   ├── qf-pipeline/        # Python MCP (validation/export) ✅
│   └── qti-core/           # Standalone QTI logic ✅
├── qf-specifications/      # Shared specs (both MCPs use) ⬜
├── docs/
│   ├── DISCOVERY_BRIEF.md  # Problem analysis ✅
│   ├── acdm/               # ACDM session logs ✅
│   ├── adr/                # Architecture decisions (12 ADRs) ✅
│   ├── specs/              # Implementation specs ✅
│   └── analysis/           # Technical analyses ✅
└── .claude/commands/       # ACDM workflow commands
```

## Key Decisions (12 ADRs)

| Decision | Choice | ADR |
|----------|--------|-----|
| Number of MCPs | 2 (scaffolding + pipeline) | ADR-001 |
| Module naming | M1-M4 (not BB1-BB6) | ADR-002 |
| Languages | TS (scaffolding), Python (pipeline) | ADR-003 |
| Tool naming | stepN_ prefix convention | ADR-007 |
| Standalone | qti-core local package | ADR-008 |

## Key Commands

See `.claude/commands/README.md` for ACDM workflow commands.

## Question Types Supported (15)

```
multiple_choice_single    text_entry              match
multiple_response         text_entry_math         hotspot
true_false                text_entry_numeric      graphicgapmatch_v2
inline_choice             text_area               text_entry_graphic
essay                     audio_record            composite_editor
nativehtml
```

## Related Documents

- [WORKFLOW](WORKFLOW.md) - Complete workflow diagram
- [ROADMAP](ROADMAP.md) - Current status and next steps
- [CHANGELOG](CHANGELOG.md) - Detailed change log
- [Discovery Brief](docs/DISCOVERY_BRIEF.md) - Problem analysis
- [ACDM Logs](docs/acdm/) - Session logs and reflections
- [ADRs](docs/adr/) - Architecture decisions (14 ADRs)
- [Specs](docs/specs/) - Implementation specs

## Origins

Consolidates and replaces:
- QTI-Generator-for-Inspera_MPC (18 tools)
- MPC_MQG_v3 (5 tools)
- Modular QGen Framework (methodology docs)

---

*Created with ACDM v1.0*
*QuestionForge - Forging Quality Questions*
