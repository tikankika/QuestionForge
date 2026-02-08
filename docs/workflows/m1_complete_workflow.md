# M1 Complete Workflow

> **Document Information**
> - Version: 3.1
> - Last Updated: 2026-01-19
> - Purpose: Complete workflow documentation for M1 (6 stages)
> - Audience: Developers implementing qf-scaffolding MCP
> - **Canonical Source:** [RFC-004](../rfcs/RFC-004-m1-methodology-tools.md)

---

## ⚠️ CRITICAL: Role Separation

### Who Does What?

| Task | Who | Tool/Method |
|------|-----|-------------|
| **List materials** | MCP | `read_materials(filename=null)` |
| **Read PDF content** | **Claude Desktop** | Native file reading |
| **Analyze content** | **Claude Desktop** | AI reasoning |
| **Save progress** | MCP | `save_m1_progress` |
| **Load methodology** | MCP | `load_stage` |

### Why This Matters

**Claude Desktop has better PDF reading** than MCP's simple text extraction. MCP's `read_materials(filename="X.pdf")` is only a **fallback** if Claude cannot read the file directly.

```
❌ WRONG: MCP reads PDF → Claude analyses text → MCP saves
✅ CORRECT: MCP lists files → CLAUDE reads PDF → Claude analyses → MCP saves
```

---

## Table of Contents

1. [Overview](#overview)
2. [Key Decisions (RFC-004)](#key-decisions-rfc-004)
3. [M1 Process Flow](#m1-process-flow)
4. [Single Document Strategy](#single-document-strategy)
5. [Stage-by-Stage Workflows](#stage-by-stage-workflows)
6. [MCP Tools Reference](#mcp-tools-reference)
7. [Session Management](#session-management)
8. [Resume Capability](#resume-capability)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### What is M1?

M1: Material Analysis transforms instructional materials (lectures, slides, transcripts) into pedagogically grounded content architecture through systematic teacher-AI dialogue.

### Duration

**Total: 160-240 minutes (2.5-4 hours)**

| Stage | Name | Duration | Type |
|-------|------|----------|------|
| 0 | Material Analysis | 60-90 min | Claude solo (progressive saves) |
| 1 | Validation | 20-30 min | Dialogue |
| 2 | Emphasis Refinement | 30-45 min | Dialogue |
| 3 | Example Cataloging | 20-30 min | Dialogue |
| 4 | Misconception Analysis | 20-30 min | Dialogue |
| 5 | Learning Objectives | 45-60 min | Dialogue |

### Key Principles

- **Teacher Authority** - Teacher makes all pedagogical decisions
- **AI Execution** - Claude handles systematic analysis and documentation
- **Progressive Building** - Each stage builds on previous
- **Single Document** - ALL stages save to ONE file (`m1_analysis.md`)
- **Resumable** - Can pause/resume at any point

---

## Key Decisions (RFC-004)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Output strategy | **Single document** `m1_analysis.md` | Easier to review, pass to M2, resume |
| Tool name | `save_m1_progress` | General name for all M1 stages |
| Stage numbering | `load_stage(stage=0)` = Material Analysis | Intuitive: parameter = methodology stage |
| Stage 0 saving | Progressive (after each PDF) | 60-90 min stage, prevents data loss |
| Stage 1-5 saving | After each dialogue completes | Shorter stages, natural save points |

---

## M1 Process Flow

### Linear Progression (6 Stages)

```
START
  │
  ├─→ Stage 0: Material Analysis (60-90 min) ← LONGEST, progressive saves
  │     │
  │     ├─→ Stage 1: Validation (20-30 min)
  │     │     │
  │     │     ├─→ Stage 2: Emphasis Refinement (30-45 min)
  │     │     │     │
  │     │     │     ├─→ Stage 3: Example Cataloging (20-30 min)
  │     │     │     │     │
  │     │     │     │     ├─→ Stage 4: Misconception Analysis (20-30 min)
  │     │     │     │     │     │
  │     │     │     │     │     └─→ Stage 5: Learning Objectives (45-60 min)
  │     │     │     │     │           │
  └─────┴─────┴─────┴─────┴───────────┘
                                      │
                                    END
                               (M1 Complete)
                                      │
                                      └─→ Ready for M2
```

### Output: ONE Document

```
project/
├── 01_methodology/
│   └── m1_analysis.md      ← ALL M1 data in ONE file
└── session.yaml            ← Tracks progress
```

**NOT multiple files** - all stages append to the same document.

---

## Single Document Strategy

### Why Single Document?

1. **Stage 0 is long (60-90 min)** - needs progressive saves during stage
2. **Easier to review** - teacher sees complete picture in one place
3. **Simpler handoff to M2** - one file contains everything
4. **Clear resume** - document + session.yaml shows exact state

### Document Structure

```markdown
---
qf_type: m1_analysis
qf_version: "1.0"
created: "2026-01-19T10:00:00Z"
updated: "2026-01-19T14:30:00Z"  # Updated on EVERY save
session_id: "de4d725a-..."

# Progress tracking
status: in_progress | complete
current_stage: 2
stages_completed: [0, 1]

# Stage 0 specific
materials_analyzed: 5
total_materials: 5
---

# M1: Material Analysis

## Stage 0: Material Analysis ✅
*Completed: 2026-01-19T11:30:00Z*

### Material 1/5: lecture_week1.pdf
**Summary:** ...
**Key Topics:** ...
**Tier Classification:**
- Tier 1 (Core): ...
- Tier 2 (Important): ...
- Tier 3 (Supplementary): ...
- Tier 4 (Reference): ...
**Examples Found:** ...
**Potential Misconceptions:** ...

### Material 2/5: lecture_week2.pdf
...

### Stage 0 Synthesis
**Cross-Material Patterns:** ...
**Initial Tier Overview:** ...

---

## Stage 1: Validation ✅
*Completed: 2026-01-19T12:00:00Z*

**Validated Tier Structure:**
...
**Teacher Corrections:**
...

---

## Stage 2: Emphasis Refinement ⏳
*In Progress*

...

---

## Stage 3: Example Cataloging
*Not started*

---

## Stage 4: Misconception Analysis
*Not started*

---

## Stage 5: Learning Objectives
*Not started*

---

## M1 Final Summary
*Added when finalize_m1 is called*
```

---

## Stage-by-Stage Workflows

### Stage 0: Material Analysis

**Duration:** 60-90 minutes (LONGEST)
**Type:** Claude solo work with progressive saves
**Purpose:** Analyze all instructional materials

#### Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 0: Material Analysis                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. load_stage(module="m1", stage=0, project_path="...")         │
│    → Returns: How to analyze materials, tier definitions        │
│    → Claude reads and understands the methodology               │
│                                                                 │
│ 2. read_materials(project_path="...", filename=null)  [MCP]     │
│    → Returns: List of files in 00_materials/                    │
│    Claude: "I see N files. Shall I start with the first one?"  │
│                                                                 │
│ 3. read_reference(project_path="...")  [MCP]                    │
│    → Returns: Kursplan content                                  │
│                                                                 │
│ 4. FOR EACH material file:                                      │
│                                                                 │
│    a. ⭐ CLAUDE READS PDF DIRECTLY (NOT MCP!)                   │
│       → Claude Desktop has better PDF reading                   │
│       → File path: {project_path}/00_materials/{filename}       │
│       → Fallback: read_materials(filename="X.pdf") if needed   │
│                                                                 │
│    b. Claude analyzes (3-8 min):                                │
│       → Identifies topics                                       │
│       → Classifies into Tiers 1-4                               │
│       → Notes examples                                          │
│       → Spots potential misconceptions                          │
│                                                                 │
│    c. Claude presents to teacher:                               │
│       "Topics: [...], Tiers: [...], Examples: [...]"             │
│                                                                 │
│    d. Teacher validates/corrects (1-2 min)                      │
│                                                                 │
│    e. save_m1_progress(  [MCP]                                  │
│         stage=0,                                                │
│         action="add_material",                                  │
│         data={ material: {...} }                                │
│       )                                                         │
│       → APPENDS to m1_analysis.md                               │
│       → Updates YAML: materials_analyzed: N                     │
│       → Session can resume if interrupted!                      │
│                                                                 │
│    f. Claude: "✅ Material N/M complete. Next?"                 │
│                                                                 │
│ 5. After ALL materials:                                         │
│    save_m1_progress(  [MCP]                                     │
│      stage=0,                                                   │
│      action="save_stage",                                       │
│      data={ stage_output: { synthesis... } }                    │
│    )                                                            │
│    → Adds "Stage 0 Synthesis" section                           │
│    → Marks Stage 0 complete                                     │
│                                                                 │
│ 6. Claude presents synthesis to teacher                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Tool Calls (Stage 0)

| Tool | Calls | Purpose |
|------|-------|---------|
| `load_stage` | 1× | Load methodology |
| `read_materials` | 1× | **List mode only** - show available files |
| `read_reference` | 1× | Load kursplan |
| `save_m1_progress` | N+1× | Save after each material (N×) + stage complete (1×) |

**Total MCP calls:** ~(N + 4) where N = number of materials

**NOTE:** Claude reads PDF files directly, not via MCP!

---

### Stage 1: Validation

**Duration:** 20-30 minutes
**Type:** Dialogue
**Purpose:** Teacher validates complete tier structure

#### Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: Validation                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. load_stage(module="m1", stage=1, project_path="...")         │
│    → Returns: Validation instructions                           │
│                                                                 │
│ 2. Claude reads Stage 0 from m1_analysis.md                     │
│                                                                 │
│ 3. Claude presents complete tier structure:                     │
│    "Here is the summary of all Tier 1 topics..."           │
│                                                                 │
│ 4. Teacher validates or requests changes:                       │
│    "Move X from Tier 2 → Tier 1"                              │
│                                                                 │
│ 5. Claude documents validated structure                         │
│                                                                 │
│ 6. save_m1_progress(                                            │
│      stage=1,                                                   │
│      action="save_stage",                                       │
│      data={ stage_output: {...} }                               │
│    )                                                            │
│    → APPENDS Stage 1 section to m1_analysis.md                  │
│    → Updates: stages_completed: [0, 1]                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### Stage 2: Emphasis Refinement

**Duration:** 30-45 minutes
**Type:** Dialogue
**Purpose:** Deep dive into WHY Tier 1 topics are prioritized

#### Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2: Emphasis Refinement                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. load_stage(module="m1", stage=2, project_path="...")         │
│                                                                 │
│ 2. Claude reads validated tiers from m1_analysis.md             │
│                                                                 │
│ 3. FOR EACH Tier 1 topic:                                       │
│    Claude: "Why is [topic] Tier 1?"                          │
│    Teacher: Explains pedagogical rationale                      │
│    Claude: Documents reasoning                                  │
│                                                                 │
│ 4. save_m1_progress(stage=2, action="save_stage", data={...})   │
│    → APPENDS Stage 2 section to m1_analysis.md                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### Stage 3: Example Cataloging

**Duration:** 20-30 minutes
**Type:** Dialogue
**Purpose:** Curate effective instructional examples

#### Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 3: Example Cataloging                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. load_stage(module="m1", stage=3, project_path="...")         │
│                                                                 │
│ 2. Claude presents examples found in Stage 0                    │
│                                                                 │
│ 3. Teacher selects most effective examples                      │
│    Teacher: "Example A is good for beginners, Example B..."      │
│                                                                 │
│ 4. Claude catalogs with effectiveness notes                     │
│                                                                 │
│ 5. save_m1_progress(stage=3, action="save_stage", data={...})   │
│    → APPENDS Stage 3 section to m1_analysis.md                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### Stage 4: Misconception Analysis

**Duration:** 20-30 minutes
**Type:** Dialogue
**Purpose:** Classify misconceptions by severity

#### Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 4: Misconception Analysis                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. load_stage(module="m1", stage=4, project_path="...")         │
│                                                                 │
│ 2. Claude presents misconceptions found in Stage 0              │
│                                                                 │
│ 3. Teacher classifies by severity:                              │
│    - Critical (blocks learning)                                 │
│    - Moderate (causes confusion)                                │
│    - Minor (occasional error)                                   │
│                                                                 │
│ 4. Teacher provides correction strategies                       │
│                                                                 │
│ 5. save_m1_progress(stage=4, action="save_stage", data={...})   │
│    → APPENDS Stage 4 section to m1_analysis.md                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### Stage 5: Learning Objectives

**Duration:** 45-60 minutes
**Type:** Dialogue
**Purpose:** Synthesize validated learning objectives

#### Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 5: Learning Objectives                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. load_stage(module="m1", stage=5, project_path="...")         │
│                                                                 │
│ 2. Claude reads ALL previous stages from m1_analysis.md         │
│                                                                 │
│ 3. Claude synthesizes learning objectives:                      │
│    - Based on Tier 1 topics                                     │
│    - Informed by emphasis patterns (Stage 2)                    │
│    - Grounded in examples (Stage 3)                             │
│    - Aware of misconceptions (Stage 4)                          │
│                                                                 │
│ 4. Teacher validates objectives                                 │
│                                                                 │
│ 5. save_m1_progress(stage=5, action="save_stage", data={...})   │
│    → APPENDS Stage 5 section to m1_analysis.md                  │
│                                                                 │
│ 6. save_m1_progress(action="finalize_m1", data={...})           │
│    → Adds "M1 Final Summary" section                            │
│    → Updates: status: complete                                  │
│    → M1 COMPLETE!                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## MCP Tools Reference

### Tools Used in M1

| Tool | Package | Purpose |
|------|---------|---------|
| `load_stage` | qf-scaffolding | Load methodology for stage N |
| `read_materials` | qf-scaffolding | **List files** (primary), read file (fallback) |
| `read_reference` | qf-scaffolding | Read kursplan etc. |
| `save_m1_progress` | qf-scaffolding | **NEW** Save to m1_analysis.md |

### `save_m1_progress` Actions

| Action | When Used | Effect |
|--------|-----------|--------|
| `add_material` | Stage 0, after each PDF | Appends material analysis |
| `save_stage` | Stage 0-5, when stage completes | Appends stage section |
| `finalize_m1` | After Stage 5 | Marks M1 complete |

### `read_materials` Modes

| Parameter | Mode | Returns | When to use? |
|-----------|------|---------|---------------|
| `filename=null` | **List** | File names + metadata (no content) | ✅ **Always** - see which files exist |
| `filename="X.pdf"` | Read | Content of ONE specific file | ⚠️ **Fallback** - only if Claude cannot read the file directly |

### ⚠️ PDF Reading: Claude vs MCP

```
┌─────────────────────────────────────────────────────────────────┐
│ RECOMMENDED FLOW                                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. MCP: read_materials(filename=null)                          │
│     → Returns: ["file1.pdf", "file2.pdf", ...]                  │
│                                                                 │
│  2. CLAUDE DESKTOP reads PDF directly:                          │
│     → Path: {project_path}/00_materials/file1.pdf               │
│     → Claude has native PDF reading (better quality!)           │
│                                                                 │
│  3. MCP: save_m1_progress(action="add_material", ...)           │
│     → Saves the analysis                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ FALLBACK (only if Claude cannot read the file)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MCP: read_materials(filename="problematic.pdf")                │
│  → Returns: Extracted text (simpler extraction)                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Session Management

### session.yaml Structure

```yaml
project:
  name: "AI Course 2026"
  created: "2026-01-18T08:00:00Z"
  last_updated: "2026-01-18T14:30:00Z"

methodology:
  m1:
    status: in_progress  # not_started | in_progress | complete
    current_stage: 2
    stages_completed: [0, 1]
    output: "01_methodology/m1_analysis.md"

    # Stage 0 specific
    materials_analyzed: 5
    total_materials: 5
```

### Log Events (logs/session.jsonl)

```jsonl
{"event": "m1_start", "timestamp": "2026-01-18T08:00:00Z"}
{"event": "stage_load", "module": "m1", "stage": 0}
{"event": "materials_list", "count": 5, "files": [...]}
{"event": "material_analyzed", "filename": "lecture1.pdf", "index": 1}
{"event": "progress_saved", "stage": 0, "action": "add_material", "materials_analyzed": 1}
...
{"event": "stage_complete", "module": "m1", "stage": 0}
{"event": "stage_load", "module": "m1", "stage": 1}
{"event": "stage_complete", "module": "m1", "stage": 1}
...
{"event": "m1_complete", "timestamp": "2026-01-18T14:30:00Z"}
```

---

## Resume Capability

### Scenario: Session interrupted at Stage 0, material 3/5

**Resume Process:**

1. **Read session.yaml:**
   ```yaml
   m1:
     status: in_progress
     current_stage: 0
     materials_analyzed: 3
     total_materials: 5
   ```

2. **Read m1_analysis.md YAML frontmatter:**
   ```yaml
   current_stage: 0
   materials_analyzed: 3
   ```

3. **Read m1_analysis.md content:**
   - Material 1 ✅
   - Material 2 ✅
   - Material 3 ✅
   - Material 4 (not present)
   - Material 5 (not present)

4. **Resume:** Claude continues from material 4/5

**No data loss** - progressive saving ensures all completed work is preserved.

---

## Troubleshooting

### Issue: "Claude can't find methodology files"

**Symptom:** `load_stage` returns error

**Solution:**
1. Check `project_path` is absolute
2. Verify `methodology/m1/` exists in project
3. Check file names match expected pattern

### Issue: "Session state out of sync"

**Symptom:** session.yaml shows different progress than m1_analysis.md

**Solution:**
1. Read m1_analysis.md YAML frontmatter (source of truth)
2. Update session.yaml to match document state
3. Resume from document state

### Issue: "PDF text extraction fails"

**Symptom:** Claude cannot read PDF directly

**Solution:**
1. **First:** Let Claude Desktop try to read the file directly (native PDF)
2. **Fallback:** Use `read_materials(filename="X.pdf")` via MCP
3. **Last resort:** Teacher copies text manually
4. **Document:** Note in the analysis if text was provided manually

### Issue: "MCP used to read PDF instead of Claude"

**Symptom:** `read_materials(filename="X.pdf")` called for every file

**Solution:**
1. MCP should only **list** files: `read_materials(filename=null)`
2. Claude Desktop should read PDF files directly
3. File path: `{project_path}/00_materials/{filename}`
4. MCP's read mode is only a **fallback** for problematic files

### Issue: "Working memory overflow in Stage 0"

**Symptom:** Claude loses track with 15+ materials

**Solution:**
1. Progressive saving already mitigates this
2. Claude can re-read m1_analysis.md to refresh context
3. Consider splitting materials into batches

---

## Summary

### M1 Essence

- **6 stages**, 2.5-4 hours total
- **ONE output document** (`m1_analysis.md`)
- Progressive saving during Stage 0
- Teacher validation at every step
- Resumable via session.yaml + document state

### Critical Success Factors

- ✅ Teacher actively engaged throughout
- ✅ Progressive saving after each material (Stage 0)
- ✅ ALL stages save to SAME document
- ✅ Logs track progress for audit trail
- ✅ `save_m1_progress` handles all saving
- ✅ **Claude reads PDF directly** - MCP only for listing/saving

### Output

```
project/
└── 01_methodology/
    └── m1_analysis.md    ← ONE document (~1500-2500 lines)
```

**Ready for M2** when `status: complete` in document frontmatter.

---

*Synced with [RFC-004](../rfcs/RFC-004-m1-methodology-tools.md) on 2026-01-19 (v3.1 - clarified Claude vs MCP roles)*
