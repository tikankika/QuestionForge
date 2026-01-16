# QuestionForge Session Init Design

**Version:** 0.1 (DRAFT)
**Date:** 2026-01-15
**Status:** Under discussion

---

## Overview

This document specifies what happens when `step0_start` creates a new QuestionForge session, including file management, sources tracking, and logging.

---

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Source tracking | `sources.yaml` | Same pattern as Assessment_suite |
| Copy strategy | Smart (Nextcloud=reference, other=copy) | Avoid duplication in synced folders |
| README format | Wikilinks (Obsidian-style) | Teacher can navigate in Obsidian |
| Methodology | Copy to project | Allows project-specific modifications |
| Logging | Dual format (log + jsonl) | Human + machine readable |

---

## 1. Project Structure (After step0_start)

```
project_name/
├── session.yaml              # Session state (qf-pipeline + qf-scaffolding)
├── sources.yaml              # NEW: Source file references
├── pipeline.log              # Human-readable log
├── pipeline.jsonl            # Structured JSON log
│
├── 00_materials/             # Input materials
│   ├── README.md             # Wikilinks to source files
│   └── (uploaded files)      # Only if NOT in Nextcloud
│
├── 01_source/                # Source questions (if entry_point != m1)
│   └── questions.md          # Original markdown (never modified)
│
├── 02_working/               # Working copies
│   └── questions.md          # Editable copy
│
├── 03_output/                # Export output
│   └── questions_QTI.zip     # QTI packages
│
└── methodology/              # COPIED from QuestionForge root
    ├── m1/                   # Content Analysis (8 files)
    ├── m2/                   # Assessment Planning (9 files)
    ├── m3/                   # Question Generation (5 files)
    └── m4/                   # Quality Assurance (6 files)
```

---

## 2. sources.yaml Format

```yaml
# sources.yaml - QuestionForge Source Tracking
# Based on Assessment_suite pattern

project:
  name: "Celler_Virus_BIOG1_2025"
  focus: "Celler och virus uppbyggnad och funktion"
  course: "BIOG001x"
  level: "Biologi nivå 1"
  created: "2026-01-15T10:33:40Z"

sources:
  # === UNDERVISNINGSMATERIAL ===
  transkription_cellen:
    original_path: /Users/.../Recording Cellen.txt
    type: transkription
    storage: nextcloud           # nextcloud | local | uploaded
    copied_to: null              # null = referenced only
    priority: high               # high | medium | low
    topics:
      - cellen
      - organeller
      - membran
    metadata:
      date: "2025-10-20"
      duration: "45 min"

  transkription_virus:
    original_path: /Users/.../Recording 2 virus.txt
    type: transkription
    storage: nextcloud
    copied_to: null
    priority: high
    topics:
      - virus
      - replikation
      - liv_eller_inte

  # === STYRDOKUMENT ===
  gy25_biologi:
    url: https://syllabuswebb.skolverket.se/...
    type: styrdokument
    storage: web
    fetched_to: 00_materials/gy25_biologi.md
    fetched_at: "2026-01-15T10:35:00Z"

  # === UPPLADDADE FILER (kopierade) ===
  uploaded_slides:
    original_path: /Users/Desktop/slides.pdf
    type: presentation
    storage: local               # NOT in Nextcloud = copied
    copied_to: 00_materials/slides.pdf
    copied_at: "2026-01-15T10:36:00Z"

# === M1 ANALYSIS OUTPUT ===
m1_outputs:
  objectives: null               # Will be: 02_working/m1_objectives.md
  examples: null
  misconceptions: null

# === M2 BLUEPRINT OUTPUT ===
m2_outputs:
  blueprint: null                # Will be: 02_working/m2_blueprint.md
```

---

## 3. Copy Strategy Logic

```python
def should_copy_file(file_path: str) -> bool:
    """Determine if file should be copied or referenced."""

    path = Path(file_path)

    # URLs are always fetched
    if is_url(file_path):
        return True  # Fetch and save

    # Nextcloud files are NEVER copied (just referenced)
    if "/Nextcloud/" in str(path):
        return False

    # iCloud files are NEVER copied
    if "Library/Mobile Documents" in str(path):
        return False

    # Dropbox files are NEVER copied
    if "/Dropbox/" in str(path):
        return False

    # Everything else gets copied to project
    return True
```

---

## 4. README.md with Wikilinks

```markdown
# Material för M1 Analysis

## Projekt: Celler och Virus (BIOG001x)

### Transkriptioner

| Fil | Prioritet | Ämnen |
|-----|-----------|-------|
| [[/Users/.../Recording Cellen.txt\|Cellen]] | HIGH | cellen, organeller |
| [[/Users/.../Recording 2 virus.txt\|Virus]] | HIGH | virus, replikation |

### Styrdokument

- [[00_materials/gy25_biologi.md\|GY25 Ämnesplan Biologi]]

### Uppladdade filer

- [[00_materials/slides.pdf\|Föreläsningsslides]]

---

## Workflow Status

- [ ] M1 Stage 0: Material Analysis
- [ ] M1 Stage 1: Initial Validation
- [ ] M1 Stage 2: Emphasis Refinement
- [ ] M1 Stage 3: Example Catalog
- [ ] M1 Stage 4: Misconception Registry
- [ ] M1 Stage 5: Scope & Objectives
- [ ] M2: Assessment Design
- [ ] M3: Question Generation
- [ ] M4: Quality Assurance
- [ ] Export to QTI

---

*Generated by QuestionForge*
```

---

## 5. Methodology Copy

When `step0_start` creates a session with `entry_point=m1`:

```python
def copy_methodology_to_project(project_path: Path):
    """Copy all methodology files to project for customization."""

    # Source: QuestionForge root
    qf_root = Path(__file__).parent.parent.parent.parent.parent
    methodology_src = qf_root / "methodology"

    # Destination: project/methodology/
    methodology_dst = project_path / "methodology"

    # Copy entire tree
    shutil.copytree(methodology_src, methodology_dst)

    # Log
    log_action(
        project_path,
        "step0_start",
        f"Copied methodology: {count_files(methodology_dst)} files",
        data={"modules": ["m1", "m2", "m3", "m4"]}
    )
```

**Files copied:**
- `methodology/m1/` - 8 files (m1_0 to m1_7)
- `methodology/m2/` - 9 files (m2_0 to m2_8)
- `methodology/m3/` - 5 files (m3_0 to m3_4)
- `methodology/m4/` - 6 files (m4_0 to m4_5)

**Total:** 28 files

---

## 6. Logging Strategy

### Current: Dual Format

```
pipeline.log   → Human-readable, one line per action
pipeline.jsonl → Structured JSON Lines, machine-parseable
```

### Proposed Enhancement: Separate Logs per Phase

```
project_name/
├── logs/
│   ├── pipeline.log           # Main pipeline log
│   ├── pipeline.jsonl         # Structured pipeline log
│   ├── m1_analysis.log        # M1-specific log (human)
│   ├── m1_analysis.jsonl      # M1-specific log (structured)
│   ├── m2_blueprint.log       # M2-specific
│   └── ...
```

### Log Entry Format

**Human (pipeline.log):**
```
2026-01-15 10:33:40 [step0_start] Session created: c227c3af (entry_point: m1)
2026-01-15 10:35:00 [m1_stage0] Started material analysis
2026-01-15 10:36:00 [m1_stage0] Analyzing: transkription_cellen
2026-01-15 10:37:00 [m1_stage0] Found 5 learning objectives
2026-01-15 10:38:00 [m1_stage0] Found 3 misconceptions
```

**Structured (pipeline.jsonl):**
```json
{
  "timestamp": "2026-01-15T10:35:00Z",
  "step": "m1_stage0",
  "phase": "material_analysis",
  "message": "Started material analysis",
  "data": {
    "sources": ["transkription_cellen", "transkription_virus"],
    "total_files": 2,
    "estimated_time": "60-90 min"
  }
}
```

### What to Log

| Event | Log Level | Data |
|-------|-----------|------|
| Session created | INFO | entry_point, sources |
| Source added | INFO | path, type, copied |
| Stage started | INFO | stage, sources |
| Stage completed | INFO | duration, outputs |
| Validation run | INFO | errors, warnings |
| Export created | INFO | format, file_path |
| Error | ERROR | exception, context |

---

## 7. Implementation Tasks

### Phase 1: Core Changes

- [ ] Update `session_manager.py` with sources.yaml support
- [ ] Add `copy_methodology_to_project()` function
- [ ] Add `should_copy_file()` smart copy logic
- [ ] Generate README.md with wikilinks

### Phase 2: Logging Enhancement

- [ ] Create `logs/` directory structure
- [ ] Add phase-specific logging
- [ ] Add log rotation (optional)

### Phase 3: Integration

- [ ] Update qf-scaffolding to read from `project/methodology/`
- [ ] Update session.yaml to track sources
- [ ] Test full M1 workflow

---

## Open Questions

1. **Log rotation** - Do we need it? Or just append indefinitely?
2. **Source validation** - Should we verify files exist before adding?
3. **Wikilink format** - Obsidian `[[path|name]]` or standard `[name](path)`?
4. **Methodology updates** - If root methodology updates, should projects be notified?

---

*Draft specification - ready for review*
