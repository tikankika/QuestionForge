# QF-SCAFFOLDING-MCP Specification

**Version:** 2.2  
**Status:** Draft  
**Date:** 2026-01-14  
**MCP Name:** qf-scaffolding  
**Language:** TypeScript (Node.js)  
**Related ADRs:** ADR-001, ADR-002, ADR-003, ADR-004, ADR-013, ADR-014

---

## Overview

qf-scaffolding is a methodology guidance MCP that helps teachers create assessment questions through a structured, pedagogical process. It implements Modules M1-M4, providing **flexible entry points** with teacher control at every stage.

**Core Principles:**
- **FLEXIBLE ENTRY:** Teachers can start at ANY module based on what they already have
- **TEACHER CHOICE:** Always ask what teacher has - never assume
- **PROGRESSIVE LOADING:** Load methodology documents one stage at a time
- **SHARED SESSION:** Uses qf-pipeline session (step0_start) for project management

**Pattern:** NON-LINEAR, independent modules  
**Output:** Markdown questions ready for qf-pipeline validation/export

---

## Shared Session Architecture (CRITICAL)

### Two MCPs, One Session

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUESTIONFORGE ARCHITECTURE                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  qf-pipeline (Python)              qf-scaffolding (TypeScript)              │
│  ──────────────────────            ─────────────────────────────            │
│  init ←─────────────────────────→  init (SAME output)                      │
│  step0_start (creates session)      (reads session.yaml)                     │
│  step0_status                      module_status                            │
│  step1_* (guided build)            list_modules                             │
│  step2_* (validate)                load_stage                               │
│  step4_* (export)                                                           │
│                                                                              │
│          ↓                                   ↓                               │
│     session.yaml ←───── SHARED ──────→ session.yaml                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Project Structure (Extended)

```
project_name/
├── 00_materials/           ← INPUT for M1 (instructional materials)
├── 01_source/              ← Original markdown (from M3 or external)
├── 02_working/             ← Working copy for pipeline
├── 03_output/              ← QTI export
├── methodology/            ← M1-M4 outputs
│   ├── m1_objectives.md    ← Learning objectives from M1
│   ├── m1_examples.md      ← Example catalog
│   ├── m1_misconceptions.md
│   ├── m2_blueprint.md     ← Blueprint from M2
│   └── m3_questions.md     ← Generated questions (copied to 01_source)
├── session.yaml            ← Extended with methodology progress
└── logs/                   ← Action logs
```

### session.yaml (Extended)

```yaml
# ===== QF-PIPELINE (existing) =====
session_id: "abc123"
created_at: "2026-01-14T10:30:00"
source_file: "/path/to/questions.md"
working_file: "/path/to/02_working/questions.md"
output_folder: "/path/to/03_output"
validation_status: "pending"
question_count: 0
exports: []

# ===== QF-SCAFFOLDING (new) =====
methodology:
  entry_point: "materials"  # materials | objectives | blueprint | questions
  active_module: "m1"
  
  m1:
    status: "in_progress"   # not_started | in_progress | completed | skipped
    loaded_stages: [0, 1, 2]
    current_stage: 2
    outputs:
      objectives: "methodology/m1_objectives.md"
      examples: "methodology/m1_examples.md"
      misconceptions: "methodology/m1_misconceptions.md"
  
  m2:
    status: "not_started"
    loaded_stages: []
    outputs: {}
  
  m3:
    status: "not_started"
    loaded_stages: []
    outputs: {}
  
  m4:
    status: "not_started"
    loaded_stages: []
    outputs: {}
```

---

## User Flow

### Step 1: Common Init

```
User: "I want to create quiz questions"

Claude: Runs init (qf-pipeline OR qf-scaffolding - same output)
        ↓
        "What do you have to start with?"
        
        A) Materials (lectures, slides, transcriptions)
           → Create questions from scratch with M1-M4
           
        B) Learning Objectives / Course Plan
           → Skip to M2 (Assessment Planning)
           
        C) Blueprint / Plan
           → Skip to M3 (Question Generation)
           
        D) Markdown file with questions
           → Direct to Pipeline (validate → export)
```

### Step 2: Create Session

```
User: Answers A, B, C or D

Claude: Runs step0_start
        - For A: materials_folder = input
        - For B: objectives_file = input  
        - For C: blueprint_file = input
        - For D: source_file = markdown with questions

        → Session created!
```

### Step 3: Route Based on Choice

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  OPTION A: Materials → M1-M4 → Pipeline                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  list_modules → Shows M1-M4                                                 │
│  "Start with M1?"                                                            │
│  load_stage(m1, 0) → intro                                                  │
│  load_stage(m1, 1) → stage0 material analysis                               │
│  ... M1 stages ...                                                          │
│  → Output: m1_objectives.md                                                 │
│                                                                              │
│  "M1 complete! Continue to M2?"                                               │
│  load_stage(m2, 0) → intro                                                  │
│  ... M2 stages ...                                                          │
│  → Output: m2_blueprint.md                                                  │
│                                                                              │
│  ... M3 → m3_questions.md ...                                               │
│  ... M4 → validated questions ...                                             │
│                                                                              │
│  → Copies to 01_source/                                                 │
│  → step2_validate → step4_export                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  OPTION B: Objectives → M2-M4 → Pipeline                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Skips M1                                                                  │
│  load_stage(m2, 0) → starts M2                                              │
│  ...                                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  OPTION C: Blueprint → M3-M4 → Pipeline                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Skips M1, M2                                                              │
│  load_stage(m3, 0) → starts M3                                              │
│  ...                                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  OPTION D: Questions → Pipeline directly                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Skips M1-M4                                                               │
│  step2_validate → validates markdown                                        │
│  step4_export → exports to QTI                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Init Output (Shared)

Both qf-pipeline and qf-scaffolding return the SAME init output:

```markdown
# QuestionForge - Critical Instructions

## STEP 1: ASK WHAT THE USER HAS

"What do you have to start with?"

A) **Materials** (lectures, slides, transcriptions)
   → You want to CREATE questions from scratch
   → Use M1-M4 methodology (qf-scaffolding)

B) **Learning Objectives / Course Plan**
   → You already have objectives, want to plan assessment
   → Start M2 (qf-scaffolding)

C) **Blueprint / Plan**
   → You already have a plan, want to generate questions
   → Start M3 (qf-scaffolding)

D) **Markdown file with questions**
   → You want to VALIDATE or EXPORT
   → Use Pipeline directly (step2 → step4)

## STEP 2: CREATE SESSION

AFTER user responds, run step0_start:
- Ask for output_folder
- Ask for project_name (optional)

## STEP 3: ROUTE BASED ON CHOICE

A) → list_modules → load_stage(m1, 0)
B) → list_modules → load_stage(m2, 0)  
C) → list_modules → load_stage(m3, 0)
D) → step2_validate → step4_export

## IMPORTANT

- WAIT for response before continuing
- Do NOT guess paths
- ALWAYS ask which module for A/B/C
```

---

## Architecture

### Follows assessment-mcp Pattern

```
qf-scaffolding/
├── methodology/                    ← SEPARATE from code (editable markdown)
│   ├── m1/                         ← From MQG_0.2 bb1a-bb1h (8 files)
│   ├── m2/                         ← From MQG_0.2 bb2a-bb2i (9 files)
│   ├── m3/                         ← From MQG_0.2 bb4a-bb4e (5 files)
│   └── m4/                         ← From MQG_0.2 bb5a-bb5f (6 files)
│
├── src/
│   ├── index.ts                    ← MCP server entry
│   ├── core/
│   │   ├── module_loader.ts        ← Reads methodology/ at runtime
│   │   └── session_reader.ts       ← Reads qf-pipeline session.yaml
│   ├── tools/
│   │   ├── init.ts                 ← CALL THIS FIRST (same as qf-pipeline)
│   │   ├── list_modules.ts         ← Show all with requirements
│   │   ├── load_stage.ts           ← Progressive loading
│   │   └── module_status.ts        ← Progress tracking
│   ├── types/
│   │   └── index.ts
│   └── utils/
│       └── file_ops.ts
│
├── package.json
├── tsconfig.json
└── README.md
```

### Methodology Mapping

| MQG_0.2 | qf-scaffolding | Stages |
|---------|----------------|--------|
| bb1a-bb1h | methodology/m1/ | 8 (intro + 6 stages + best practices) |
| bb2a-bb2i | methodology/m2/ | 9 (intro + 7 stages + best practices) |
| bb4a-bb4e | methodology/m3/ | 5 (intro + 4 stages) |
| bb5a-bb5f | methodology/m4/ | 6 (intro + 4 phases + output) |

---

## Modules

### M1: Content Analysis
**Purpose:** Analyze what was actually taught  
**Requires:** Instructional materials (lectures, slides, transcripts)  
**Produces:** Learning objectives, examples catalog, misconceptions registry  
**Stages:** 8

| Index | File | Description |
|-------|------|-------------|
| 0 | intro.md | Framework overview, principles |
| 1 | stage0_material_analysis.md | AI reads materials, identifies emphasis |
| 2 | stage1_initial_validation.md | Teacher validates AI analysis |
| 3 | stage2_emphasis_refinement.md | Deep dive into priorities |
| 4 | stage3_example_catalog.md | Document effective examples |
| 5 | stage4_misconception_analysis.md | Identify common errors |
| 6 | stage5_scope_objectives.md | Finalize learning objectives |
| 7 | best_practices.md | Facilitation principles |

### M2: Assessment Planning
**Purpose:** Design the assessment structure  
**Requires:** Learning objectives (from M1 OR existing)  
**Produces:** Blueprint with question distribution  
**Stages:** 9

### M3: Question Generation
**Purpose:** Create the questions  
**Requires:** Blueprint (from M2 OR existing)  
**Produces:** Draft questions in markdown format  
**Stages:** 5

### M4: Quality Assurance
**Purpose:** Validate questions pedagogically  
**Requires:** Questions (from M3 OR existing)  
**Produces:** Reviewed, validated questions  
**Stages:** 6

---

## Tools (4 Core Tools)

### 1. init

**CALL THIS FIRST!** Returns critical instructions (same as qf-pipeline).

```typescript
interface InitResult {
  instructions: string;      // Critical rules for Claude
  available_tools: string[]; // List of tools  
  entry_points: EntryPoint[];// A, B, C, D options
}
```

---

### 2. list_modules

Shows all modules with requirements and what they produce.

```typescript
interface ListModulesResult {
  modules: ModuleInfo[];
  prompt: string;  // Always ask teacher to choose
}

interface ModuleInfo {
  id: "m1" | "m2" | "m3" | "m4";
  name: string;
  description: string;
  requires: string[];
  produces: string[];
  stages: number;
  status: "not_started" | "in_progress" | "completed" | "skipped";
  loaded_stages: number[];
}
```

---

### 3. load_stage

Progressively load methodology documents one stage at a time.

```typescript
interface LoadStageParams {
  module: "m1" | "m2" | "m3" | "m4";
  stage_index: number;  // 0-based
}

interface LoadStageResult {
  document: {
    name: string;
    path: string;
    content: string;      // Full markdown content
    size_bytes: number;
  };
  progress: {
    current_stage: number;
    total_stages: number;
    remaining: string[];
  };
  requires_approval: boolean;  // true = STOP and wait for teacher
  approval_prompt: string;     // "Confirm before next stage"
  next_action: string;
}
```

---

### 4. module_status

Get detailed progress for a module or all modules.

```typescript
interface ModuleStatusParams {
  module?: "m1" | "m2" | "m3" | "m4";
}

interface ModuleStatusResult {
  session_id: string;
  entry_point: string;
  modules: { [key: string]: ModuleProgress };
  overall_progress: {
    modules_started: number;
    modules_completed: number;
    total_modules: 4;
  };
  next_step: string;  // What to do next
}
```

---

## Tool Summary

| # | Tool | Purpose | Input | Output |
|---|------|---------|-------|--------|
| 1 | `init` | Critical instructions | - | Rules + entry points |
| 2 | `list_modules` | Show all M1-M4 | - | Modules with status |
| 3 | `load_stage` | Progressive loading | module, stage_index | Markdown + progress |
| 4 | `module_status` | Progress tracking | module? | Status per module |

---

## Potential Future Tools (TBD)

Decision pending after M4 methodology review.

| Tool | Purpose | Decision After |
|------|---------|----------------|
| `analyze_distractors` | QA for MC distractors | M4 review |
| `check_language` | Terminology consistency | M4 review |

---

## Session Integration

### qf-scaffolding Reads qf-pipeline Session

1. User runs `init` (either MCP)
2. User answers A/B/C/D
3. Claude runs `step0_start` (qf-pipeline) → creates session
4. qf-scaffolding reads `session.yaml` via `session_reader.ts`
5. qf-scaffolding updates `methodology` section in session.yaml

### If No Session Exists

```typescript
// list_modules or load_stage without session:
{
  error: "No active session",
  instruction: "Run step0_start first (qf-pipeline)",
  example: "step0_start source_file=/path output_folder=/path"
}
```

---

## Changelog

### v2.2 (2026-01-14)
- **NEW:** Shared session architecture with qf-pipeline
- **NEW:** Common init output for both MCPs
- **NEW:** Entry point routing (A/B/C/D)
- **NEW:** Extended project structure (00_materials, methodology/)
- **NEW:** Extended session.yaml with methodology progress
- **NEW:** requires_approval in load_stage output
- **CHANGED:** Stage counts updated (M1=8, M2=9, M3=5, M4=6)

### v2.1 (2026-01-14)
- Reduced to 4 core tools
- analyze_distractors, check_language moved to TBD

### v2.0 (2026-01-14)
- Flexible entry points as core principle
- methodology/ folder separate from src/
- Progressive loading with load_stage

### v1.0 (2026-01-02)
- Initial specification

---

*Specification v2.2 | QuestionForge | 2026-01-14*
