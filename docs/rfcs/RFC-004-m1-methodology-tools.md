# RFC-004: M1 Methodology Tools for qf-scaffolding

| Field | Value |
|-------|-------|
| **Status** | Phase 2 Complete |
| **Created** | 2026-01-17 |
| **Updated** | 2026-01-19 (v3.1 - clarified Claude vs MCP roles) |
| **Author** | Niklas Karlsson |
| **Relates to** | qf-scaffolding, RFC-001 (logging), RFC-002 (QFMD), SPEC_M1_M4_OUTPUTS_FULL.md |

## Key Decisions (2026-01-19)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Output strategy | **Single document** `m1_analysis.md` | Easier to review, pass to M2, resume |
| Tool name | `save_m1_progress` | General name for all M1 stages |
| Stage numbering | `load_stage(stage=0)` = Material Analysis | Intuitive: stage parameter = methodology stage |
| Stage 0 saving | Progressive (after each PDF) | 60-90 min stage, prevents data loss |
| Stage 1-5 saving | After each dialogue completes | Shorter stages, natural save points |
| **PDF reading** | **Claude Desktop reads directly** | MCP's `read_materials` är fallback |

### ⚠️ CRITICAL: Role Separation (Claude vs MCP)

| Task | Who | How |
|------|-----|-----|
| List materials | MCP | `read_materials(filename=null)` |
| **Read PDF content** | **Claude Desktop** | Native file reading (better quality) |
| Analyze content | Claude Desktop | AI reasoning |
| Save progress | MCP | `save_m1_progress` |
| Load methodology | MCP | `load_stage` |

**Why?** Claude Desktop has better PDF reading than MCP's simple text extraction. MCP's `read_materials(filename="X.pdf")` is only a **fallback** if Claude cannot read the file directly.

```
❌ WRONG: MCP reads PDF → Claude analyses text → MCP saves
✅ CORRECT: MCP lists files → CLAUDE reads PDF → Claude analyses → MCP saves
```

## Summary

This RFC proposes adding specific MCP tools to qf-scaffolding for M1 (Material Analysis) workflow. Currently, Claude.ai sessions improvise with generic filesystem tools instead of using proper MCP tools, leading to inconsistent behavior, files outside the project, and outputs that don't follow QFMD standards.

## Problem Statement

### Critical Bug: `load_stage` Ignores Project Path

**Discovery:** While debugging user session, we found that `load_stage` reads methodology from the WRONG location:

```typescript
// load_stage.ts lines 388-399 - CURRENT (BROKEN)
const methodologyPath = join(
  __dirname,           // build/tools/
  "..", "..", "..", "..",  // → QuestionForge root
  "methodology",       // QuestionForge/methodology/  ← WRONG!
  module,
  stageInfo.filename
);
```

**The Design (from CHANGELOG 2026-01-15):**
```
1. step0_start copies methodology → project/methodology/ ✅
2. load_stage reads from project/methodology/            ❌ BROKEN
```

**What Actually Happens:**
```
1. step0_start copies 28 files → project/methodology/    ✅ Works
2. load_stage reads from QuestionForge/methodology/      ❌ Ignores project!
3. Project's methodology/ folder is NEVER used           ❌ Wasted copy
```

**Impact:**
- Projects are NOT self-contained (contrary to design intent)
- Project-specific methodology changes would be ignored
- `project_path` parameter exists but is only used for logging, not file reading

**Required Fix:**
```typescript
// load_stage.ts - FIXED
const methodologyPath = project_path
  ? join(project_path, "methodology", module, stageInfo.filename)
  : join(__dirname, "..", "..", "..", "..", "methodology", module, stageInfo.filename);
```

---

### Observed Issues (2026-01-17)

During a real user session attempting to use QuestionForge M1:

**0. Methodology Not Loaded From Project (CRITICAL - see above)**
```
Expected: load_stage reads from project/methodology/m1/
Actual:   load_stage reads from QuestionForge/methodology/m1/
Result:   Project's methodology files are never used
```

**1. Duplicate File Copying**
```
User provides: materials_folder → 00_materials/ (via step0_start)
Claude then: Copies same files AGAIN to /mnt/user-data/uploads (Claude's computer)
```
Files exist in two places, causing confusion and wasted operations.

**2. Work Outside Project**
```
Claude: "Ah, upload-mappen är read-only! Låt mig spara till min arbetsmapp istället"
Result: Analysis data saved to /home/claude/pdf_texts/ instead of project
```
User loses access to intermediate analysis data.

**3. Methodology Not Loaded**
```
Expected: Claude loads /methodology/m1/ instructions, follows them
Actual: Claude improvises based on load_stage output text
```
The methodology files were copied to the project but never actually used.

**4. Output Doesn't Follow QFMD Standard**
```
Expected: stage0_materialanalys.md with YAML frontmatter (RFC-002)
Actual: Plain markdown without proper metadata, incomplete content
```
We implemented M1 output schemas (learning_objectives, misconceptions, etc.) but they weren't used.

**5. No Proper Tools for M1 Work**
```
Current tools: load_stage, complete_stage
Missing tools: read_material, analyze_materials, generate_output
```
`load_stage` returns instructions, but there's no tool to actually DO the work.

### Root Cause Analysis

**Layer 1: Critical Bug (load_stage path)**
```
step0_start (qf-pipeline):
├── Creates project structure                    ✅
├── Copies methodology/ to project               ✅
└── Project should be self-contained             ✅ (design intent)

load_stage (qf-scaffolding):
├── Receives project_path parameter              ✅
├── Uses project_path for LOGGING                ✅
├── Uses project_path for FILE READING           ❌ IGNORES IT!
└── Reads from QuestionForge source instead      ❌ BUG
```

**Layer 2: Missing Tools**
```
qf-scaffolding tools:
├── load_stage      ← Returns markdown instructions (but from wrong location!)
├── complete_stage  ← Saves output + updates session.yaml ✅
└── ??? (missing)   ← Tools to read materials from 00_materials/
```

**Layer 3: Claude.ai Improvisation**
```
Claude.ai session (with broken load_stage):
├── Receives instructions (from wrong methodology source)
├── Has NO MCP tools to read materials → uses Filesystem tools
├── Copies files to Claude's VM → duplicates, outside project
├── Improvises output format → doesn't match schemas
└── Files scattered across Claude's VM and user's project
```

**Cascade of Failures:**
```
load_stage reads from wrong location
    → Claude doesn't get project-specific methodology
        → Claude doesn't know about read_materials need
            → Claude uses Filesystem tools
                → Files outside project
                    → Session not resumable
```

**The fix must address all layers:**
1. **Phase 0:** Fix `load_stage` to read from `project_path/methodology/`
2. **Phase 1:** Add `read_materials` tool so Claude doesn't need Filesystem
3. **Phase 2:** Optionally add `get_methodology` for combined instructions+schema

### Impact

| Issue | User Impact | System Impact |
|-------|-------------|---------------|
| Duplicate files | Confusion, wasted space | Inconsistent state |
| Work outside project | Data loss, can't resume | No audit trail |
| No methodology loading | Inconsistent quality | Unpredictable outputs |
| Non-standard outputs | Can't use in later stages | Schema validation fails |

## Proposed Solution

### New MCP Tools for qf-scaffolding

Add the following tools to qf-scaffolding:

#### 1. `read_materials` - List files from 00_materials/ (+ fallback read)

```typescript
interface ReadMaterialsInput {
  project_path: string;
  filename?: string | null;  // null → list files only, "X.pdf" → read specific file (FALLBACK)
  file_pattern?: string;     // e.g., "*.pdf" - DEPRECATED, use filename instead
  extract_text?: boolean;    // For PDFs: extract text content (default: true)
}

interface ReadMaterialsResult {
  success: boolean;
  // When filename=null (list mode):
  files?: Array<{
    filename: string;
    size_bytes: number;
    content_type: "pdf" | "md" | "txt" | "pptx" | "other";
  }>;
  // When filename="X.pdf" (read mode - FALLBACK):
  material?: {
    filename: string;
    path: string;
    content_type: "pdf" | "md" | "txt" | "pptx" | "other";
    size_bytes: number;
    text_content?: string;  // If extract_text=true
    error?: string;         // If extraction failed
  };
  total_files: number;
  total_chars?: number;
}
```

**Purpose:** ⚠️ Primarily for **listing** files in 00_materials/ - Claude Desktop should read PDFs directly!

| Mode | Usage | When to use |
|------|-------|-------------|
| **List** (`filename=null`) | Returns file metadata, no content | ✅ **Always** - to see which files exist |
| **Read** (`filename="X.pdf"`) | Extracts text from ONE file | ⚠️ **Fallback** - only if Claude cannot read directly |

**Why?** Claude Desktop has better native PDF reading than MCP's `pdf-parse` text extraction.

- Supports PDF text extraction (built-in via `pdf-parse`) - but Claude Desktop is better!
- Supports markdown, text, and other formats
- Returns content within MCP response (no file copying needed)
- Logs read operations (RFC-001 compliant)

**Usage pattern for Stage 0:**
```
1. read_materials(filename=null)       → List all files in 00_materials/  [MCP]
2. Claude reads "A.pdf" directly       → Claude Desktop reads PDF          [CLAUDE]
3. Claude analyzes content             → Identifies topics, tiers, etc.   [CLAUDE]
4. save_m1_progress(action="add_material")  → Save the analysis            [MCP]
5. Claude reads "B.pdf" directly       → Next file                       [CLAUDE]
6. Claude analyzes content                                                [CLAUDE]
7. save_m1_progress(action="add_material")                                [MCP]
... repeat for each material

NOTE: read_materials(filename="X.pdf") is only a FALLBACK if Claude cannot read the file!
```

#### 2. `read_reference` - Read reference documents (kursplan, etc.)

```typescript
interface ReadReferenceInput {
  project_path: string;
  filename?: string;  // Specific file, or all reference docs
}

interface ReadReferenceResult {
  success: boolean;
  references: Array<{
    filename: string;
    content: string;
    source_url?: string;  // If fetched from URL
  }>;
}
```

**Purpose:** Read reference documents (syllabus, grading criteria) from project root.
- Returns content of reference docs saved by step0_start
- Includes source URL metadata if originally fetched from URL

#### 3. `get_methodology` - Load methodology instructions

```typescript
interface GetMethodologyInput {
  project_path: string;
  module: "m1" | "m2" | "m3" | "m4";
  stage: number;
  include_examples?: boolean;
}

interface GetMethodologyResult {
  success: boolean;
  instructions: string;     // Full methodology content
  output_schema?: object;   // Zod schema for stage output (if any)
  output_type?: string;     // e.g., "learning_objectives"
  examples?: string;        // Example outputs (if include_examples=true)
}
```

**Purpose:** Load methodology instructions AND output schema from project's methodology/ folder.
- Returns both the "how to" instructions and the expected output format
- Includes Zod schema so Claude knows exact output structure
- Optionally includes example outputs

#### 4. `save_m1_progress` - Progressive saving for ALL M1 stages

```typescript
interface SaveM1ProgressInput {
  project_path: string;
  stage: 0 | 1 | 2 | 3 | 4 | 5;  // Which M1 stage
  action: "add_material" | "save_stage" | "finalize_m1";
  data: M1ProgressData;
}

interface M1ProgressData {
  // For action="add_material" (Stage 0 only - after each PDF)
  material?: {
    filename: string;
    summary: string;
    key_topics: string[];
    tier_classification: {
      tier1_core: string[];
      tier2_important: string[];
      tier3_supplementary: string[];
      tier4_reference: string[];
    };
    examples_found: Array<{
      topic: string;
      example: string;
      location: string;
    }>;
    potential_misconceptions: string[];
  };

  // For action="save_stage" (Stage 0-5 - after dialogue completes)
  stage_output?: {
    stage_name: string;
    content: string;           // Markdown content for this stage
    teacher_approved: boolean;
  };

  // For action="finalize_m1" (after Stage 5)
  final_summary?: {
    total_materials: number;
    learning_objectives_count: number;
    ready_for_m2: boolean;
  };
}

interface SaveM1ProgressResult {
  success: boolean;
  current_stage: number;
  stages_completed: number[];
  document_path: string;  // Always "01_methodology/m1_analysis.md"
}
```

**Purpose:** Single tool for ALL M1 saving - both progressive (during Stage 0) and stage-completion saves.

**Three actions:**
1. **`add_material`** (Stage 0 only): Appends one material's analysis during the long PDF analysis phase
2. **`save_stage`** (Stage 0-5): Saves a completed stage's output to the document
3. **`finalize_m1`** (after Stage 5): Marks M1 complete, ready for M2

**All saves go to ONE document:** `01_methodology/m1_analysis.md`

**Usage patterns:**

```
Stage 0 (Material Analysis - 60-90 min):
  FOR EACH PDF:
    1. read_materials(filename="X.pdf")
    2. Claude analyzes
    3. save_m1_progress(stage=0, action="add_material", data={material: {...}})
  AFTER ALL PDFs:
    4. save_m1_progress(stage=0, action="save_stage", data={stage_output: {...}})

Stage 1-5 (Dialogues - 15-45 min each):
  1. load_stage(module="m1", stage=N)
  2. Teacher-Claude dialogue
  3. Teacher approves
  4. save_m1_progress(stage=N, action="save_stage", data={stage_output: {...}})

After Stage 5:
  save_m1_progress(action="finalize_m1", data={final_summary: {...}})
```

### Output Strategy: Single Document with Progressive Saving

**Key Decision:** M1 produces ONE output document (`m1_analysis.md`) that grows progressively through all 6 stages.

**Rationale:**
- Stage 0 (Material Analysis) takes 60-90 minutes - needs in-stage saves
- Single document is easier to review and pass to M2
- Clear audit trail via YAML frontmatter (updated on each save)
- Session can resume from any point

**Output Document Structure:**
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

**Tier 1 Topic Rationales:**
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

**File Locations:**
```
project/
├── 01_methodology/
│   └── m1_analysis.md      ← SINGLE output document for ALL M1 stages
├── session.yaml            ← Tracks m1.status
└── logs/session.jsonl      ← Audit trail (RFC-001)
```

**session.yaml Updates:**
```yaml
methodology:
  m1:
    status: in_progress     # → complete when finalize_m1 called
    current_stage: 2        # Which stage we're on
    stages_completed: [0, 1]
    output: "01_methodology/m1_analysis.md"

    # Stage 0 specific (Material Analysis)
    materials_analyzed: 5
    total_materials: 5
```

**Important:** There is only ONE output file for M1. All 6 stages (0-5) save to the same `m1_analysis.md` document.

### M1 Complete Workflow

**Stage Numbering (IMPORTANT):**
```
load_stage(stage=N) loads methodology for Stage N

Stage 0: Material Analysis   (60-90 min, Claude solo, progressive saves)
Stage 1: Validation          (20-30 min, dialogue)
Stage 2: Emphasis Refinement (30-45 min, dialogue)
Stage 3: Example Cataloging  (20-30 min, dialogue)
Stage 4: Misconception Analysis (20-30 min, dialogue)
Stage 5: Learning Objectives (45-60 min, dialogue)
```

**Pre-requisites (qf-pipeline):**
```
step0_start(
  output_folder="/path/to/output",
  entry_point="m1",
  materials_folder="/path/to/lectures",
  source_file="https://skolverket.se/kursplan..."  ← Optional URL
)
    ↓
Creates:
project/
├── 00_materials/           ← Copies from materials_folder
├── 01_methodology/         ← Empty (for m1_analysis.md output)
├── methodology/            ← Copies M1-M4 from QuestionForge
│   └── m1/
│       ├── m1_0_material_analysis.md
│       ├── m1_1_validation.md
│       └── ...
├── session.yaml
├── kursplan.md             ← Fetched from URL
└── logs/
```

**M1 Workflow (qf-scaffolding):**
```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 0: Material Analysis (Claude solo, 60-90 min)             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. load_stage(module="m1", stage=0, project_path="...")  [MCP]  │
│    → Returns: How to analyze materials, tier definitions        │
│                                                                 │
│ 2. read_materials(project_path="...", filename=null)     [MCP]  │
│    → Returns: List of files in 00_materials/                    │
│                                                                 │
│ 3. read_reference(project_path="...")                    [MCP]  │
│    → Returns: Kursplan content                                  │
│                                                                 │
│ 4. FOR EACH material file:                                      │
│                                                                 │
│    a. ⭐ CLAUDE READS PDF DIRECTLY (NOT MCP!)                    │
│       → Claude Desktop has better PDF reading                   │
│       → Path: {project_path}/00_materials/{filename}            │
│       → Fallback: read_materials(filename="X.pdf") if needed   │
│                                                                 │
│    b. Claude analyzes (identifies topics, tiers, examples)      │
│                                                                 │
│    c. save_m1_progress(                                  [MCP]  │
│         stage=0,                                                │
│         action="add_material",                                  │
│         data={ material: {...} }                                │
│       )                                                         │
│       → SAVES to m1_analysis.md                                 │
│       → Session can resume if interrupted!                      │
│                                                                 │
│ 5. After ALL materials:                                         │
│    save_m1_progress(                                     [MCP]  │
│      stage=0,                                                   │
│      action="save_stage",                                       │
│      data={ stage_output: { synthesis... } }                    │
│    )                                                            │
│    → Adds Stage 0 synthesis                                     │
│    → Marks Stage 0 complete                                     │
│                                                                 │
│ 6. Claude presents findings to teacher                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1-5: Dialogue Stages (15-45 min each)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ FOR EACH stage N (1 to 5):                                      │
│                                                                 │
│   1. load_stage(module="m1", stage=N, project_path="...")       │
│      → Returns: Stage instructions                              │
│                                                                 │
│   2. Claude facilitates dialogue with teacher                   │
│      → Stage 1: Validate tier structure                         │
│      → Stage 2: Refine emphasis rationales                      │
│      → Stage 3: Catalog effective examples                      │
│      → Stage 4: Analyze misconceptions                          │
│      → Stage 5: Synthesize learning objectives                  │
│                                                                 │
│   3. Teacher approves                                           │
│                                                                 │
│   4. save_m1_progress(                                          │
│        stage=N,                                                 │
│        action="save_stage",                                     │
│        data={ stage_output: {...} }                             │
│      )                                                          │
│      → APPENDS to m1_analysis.md (same document!)               │
│      → Marks Stage N complete                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ FINALIZE M1                                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ save_m1_progress(                                               │
│   action="finalize_m1",                                         │
│   data={ final_summary: {...} }                                 │
│ )                                                               │
│ → Adds final summary section                                    │
│ → Marks M1 complete in session.yaml                             │
│ → Ready for M2                                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ M1 COMPLETE → Continue to M2                                    │
│                                                                 │
│ Output: 01_methodology/m1_analysis.md (ONE document, all data)  │
└─────────────────────────────────────────────────────────────────┘
```

### Comparison: Before vs After

```
BEFORE (broken):
1. load_stage → instructions from WRONG location (QuestionForge source)
2. NO tool to read materials → Claude uses Filesystem tools
3. Files copied to Claude's VM → outside project
4. Claude improvises output format → doesn't match schema
5. complete_stage not called → output not saved properly

AFTER (fixed):
1. load_stage → instructions from project/methodology/m1/
2. read_materials → content from project/00_materials/
3. read_reference → kursplan from project root
4. Claude analyzes (no file operations, all in MCP responses)
5. complete_stage → validates schema, saves QFMD to 01_methodology/
```

### Integration with Existing Tools

| Existing Tool | Change Needed |
|---------------|---------------|
| `load_stage` | Update stage numbering: stage=0 → Material Analysis |
| `complete_stage` | Keep for M2-M4; M1 uses `save_m1_progress` instead |
| `read_materials` | Add `filename` parameter (Phase 2) |
| `read_reference` | Keep as-is ✅ |

| New Tool | Purpose |
|----------|---------|
| `save_m1_progress` | **NEW** All M1 saving (progressive + stage completion) |

**Note:** `get_methodology` is optional and may not be needed since `load_stage` already provides instructions.

### File Handling Principles

**All file operations stay within the project:**

```
project/
├── 00_materials/      ← read_materials reads FROM here (read-only)
├── 01_methodology/    ← complete_stage writes TO here
├── methodology/       ← get_methodology reads FROM here (read-only)
├── session.yaml       ← Tools update metadata here
├── logs/              ← RFC-001 logging here
└── *.txt/.md          ← read_reference reads FROM here
```

**No files created outside project:**
- No `/tmp/` files
- No `/home/claude/` files
- No `/mnt/user-data/` copies

**Content returned in MCP responses:**
- PDFs extracted to text inline
- Markdown content returned directly
- No intermediate files needed

### Output Format: Single Document (QFMD Compliant)

**M1 produces ONE output document** that grows through all 6 stages:

| Output | File | Tool |
|--------|------|------|
| All M1 data | `01_methodology/m1_analysis.md` | `save_m1_progress` |

**Document sections (added progressively):**

| Stage | Section Added |
|-------|---------------|
| 0 | Material-by-material analysis, tier classifications, examples, misconceptions |
| 1 | Validated tier structure, teacher corrections |
| 2 | Emphasis rationales for Tier 1 topics |
| 3 | Curated example catalog |
| 4 | Misconception registry with severity levels |
| 5 | Final learning objectives |
| finalize | M1 summary, ready-for-M2 checklist |

**YAML frontmatter tracks progress:**
```yaml
qf_type: m1_analysis
status: in_progress | complete
current_stage: 2
stages_completed: [0, 1]
materials_analyzed: 5
total_materials: 5
```

### Logging (RFC-001 Compliance)

New tools log events:

```jsonl
{"ts":"...","mcp":"qf-scaffolding","tool":"read_materials","event":"tool_start","data":{"pattern":"*.pdf"}}
{"ts":"...","mcp":"qf-scaffolding","tool":"read_materials","event":"tool_end","data":{"files_read":10,"total_chars":45000}}
{"ts":"...","mcp":"qf-scaffolding","tool":"get_methodology","event":"tool_start","data":{"module":"m1","stage":0}}
```

## Implementation Plan

### Phase 0: Fix `load_stage` Bug (CRITICAL) ✅ COMPLETED
**Implemented 2026-01-17**

1. **Fixed methodology path resolution:**
   ```typescript
   // If project_path provided, read from project
   // Otherwise, fall back to QuestionForge source
   const methodologyPath = project_path
     ? join(project_path, "methodology", module, stageInfo.filename)
     : join(__dirname, "..", "..", "..", "..", "methodology", module, stageInfo.filename);
   ```

2. **Added fallback with warning:**
   - Tries to read from `project_path/methodology/{module}/` first
   - If file not found, falls back to QuestionForge source
   - Logs warning via `logEvent()` when fallback used

3. **Tested:** All 136 tests pass, TypeScript build clean

### Phase 1: Core Read Tools ✅ COMPLETED
**Implemented 2026-01-17**

1. **`read_materials`** - PDF text extraction, file listing from `00_materials/`
   - Uses `pdf-parse` library for PDF text extraction
   - Supports pattern filtering (e.g., `*.pdf`, `lecture*`)
   - Returns content within MCP response
   - RFC-001 compliant logging

2. **`read_reference`** - Reference document reading from project root
   - Reads `.md`, `.txt`, `.html` files from project root
   - Includes source URL metadata from companion `.url` files

3. **Tool descriptions** updated in index.ts for Claude.ai prompting

### Phase 2: Progressive Saving & Interface Updates (DESIGN COMPLETE)

**2a. Update `read_materials` interface:**
```typescript
interface ReadMaterialsInput {
  project_path: string;
  filename?: string | null;  // NEW: null → list files, "X.pdf" → read one file
  file_pattern?: string;     // DEPRECATED: kept for backwards compatibility
  extract_text?: boolean;
}
```
- `filename=null` (or omitted): Returns file list with metadata (no content)
- `filename="X.pdf"`: Returns content of ONE specific file
- Deprecate `file_pattern` in favor of `filename`

**2b. Implement `save_m1_progress` tool:**
```typescript
save_m1_progress(
  project_path: string,
  stage: 0 | 1 | 2 | 3 | 4 | 5,
  action: "add_material" | "save_stage" | "finalize_m1",
  data: M1ProgressData
)
```
- Creates/updates `01_methodology/m1_analysis.md`
- `add_material`: Progressive saves during Stage 0 (after each PDF)
- `save_stage`: Saves completed stage output (Stage 0-5)
- `finalize_m1`: Marks M1 complete, ready for M2
- Updates `session.yaml` with current_stage and stages_completed

**2c. Update `load_stage` mappings:**
- Fix stage numbering: `load_stage(stage=0)` = Material Analysis
- Update tool hints to reference `save_m1_progress`

**2d. Update methodology file names (optional):**
- Consider renaming to match stage numbers:
  - `m1_0_material_analysis.md` (Stage 0)
  - `m1_1_validation.md` (Stage 1)
  - etc.

### Phase 3: Testing & Documentation
1. Update WORKFLOW.md with correct tool usage
2. Add Claude.ai prompt guidance for M1 workflow
3. Create example M1 session transcript showing correct flow

### Dependency Graph

```
Phase 0: Fix load_stage path ✅ DONE
    ↓
Phase 1: read_materials, read_reference ✅ DONE
    ↓
Phase 2: save_m1_progress + read_materials filename param ← NEXT
    ↓
Phase 3: Update load_stage mappings + tool hints
    ↓
Phase 4: Testing & Documentation
```

**Phase 2 is the current blocker** - without `save_m1_progress`, M1 sessions cannot save progress.

## Alternatives Considered

### Alternative 1: Rely on Claude.ai's Filesystem Tools
**Rejected:** Leads to files outside project, no schema validation, inconsistent outputs.

### Alternative 2: Single "do_m1_stage" Tool
```typescript
do_m1_stage(project_path, stage) → automatically reads materials, generates output
```
**Rejected:** Too opaque, removes teacher oversight, can't handle edge cases.

### Alternative 3: External PDF Processing
**Rejected:** Adds dependencies, complicates installation. Better to use built-in JavaScript/TypeScript PDF libraries.

## Questions for Discussion

1. ~~**PDF Library:** Use `pdf-parse` or `pdfjs-dist` for text extraction?~~ **RESOLVED:** Using `pdf-parse` v2.4.5
2. **Content Size Limits:** Maximum chars to return from `read_materials`? (Context window limits)
3. **Caching:** Should extracted text be cached in project for resume?
4. **Progress:** Should `read_materials` report progress for large material sets?

## Success Criteria

### Phase 0 (Critical Fix) ✅ COMPLETED
- [x] `load_stage` reads methodology from `project_path/methodology/` when provided
- [x] Falls back to QuestionForge source only if `project_path` not provided (with warning)
- [x] Projects are truly self-contained (can be moved/copied)

### Phase 1 (Core Read Tools) ✅ COMPLETED
- [x] `read_materials` tool implemented with PDF text extraction
- [x] `read_reference` tool implemented for reference documents
- [x] Tools registered in MCP server with proper descriptions
- [x] RFC-001 compliant logging in both tools
- [x] **Tool hints in load_stage response** - Claude sees which tools to use per stage

### Phase 2 (Progressive Saving) 📋 DESIGN COMPLETE
- [ ] `read_materials` updated with `filename` parameter (list vs read mode)
- [ ] `save_m1_progress` tool implemented with three actions:
  - [ ] `add_material` - progressive saves during Stage 0
  - [ ] `save_stage` - saves completed stage (0-5)
  - [ ] `finalize_m1` - marks M1 complete
- [ ] Single output document `m1_analysis.md` grows through all stages
- [ ] `load_stage` updated: stage=0 → Material Analysis
- [ ] Tool hints reference `save_m1_progress`

### Full Implementation
- [ ] M1 session completes using ONLY qf-scaffolding tools (no Filesystem tools)
- [ ] All 6 stages save to ONE document (`m1_analysis.md`)
- [ ] YAML frontmatter tracks: current_stage, stages_completed, materials_analyzed
- [ ] Session can resume from any point via session.yaml + document state
- [ ] Logs capture full audit trail (RFC-001)

### Verification Test
```
Phase 2 Verification:

1. Create project with step0_start
2. Call read_materials(project_path, filename=null)
   → Should return file list WITHOUT content
3. Call read_materials(project_path, filename="lecture1.pdf")
   → Should return content of ONE file
4. Call save_m1_progress(stage=0, action="add_material", data={...})
   → Should create/update m1_analysis.md
5. Call save_m1_progress(stage=0, action="save_stage", data={...})
   → Should mark Stage 0 complete in document
6. Repeat for stages 1-5
7. Call save_m1_progress(action="finalize_m1", data={...})
   → Should mark M1 complete, ready for M2
```

## Next Steps (Implementation Order)

### Immediate (Phase 2 Implementation)

1. **Update `read_materials.ts`:**
   - Add `filename` parameter
   - `filename=null/undefined` → list mode (no content)
   - `filename="X.pdf"` → single file read mode
   - Keep `file_pattern` for backwards compatibility but mark deprecated

2. **Create `save_m1_progress.ts`:**
   - New tool file in `packages/qf-scaffolding/src/tools/`
   - Implement three actions: `add_material`, `save_stage`, `finalize_m1`
   - Handle m1_analysis.md creation and updating
   - Update session.yaml tracking

3. **Update `load_stage.ts`:**
   - Change M1_STAGES mapping so stage=0 loads Material Analysis
   - Update tool hints to reference `save_m1_progress`

4. **Register new tool in `index.ts`:**
   - Add `save_m1_progress` to TOOLS array
   - Add handler in CallToolRequestSchema

### Then (Phase 3)

5. **Update `m1_complete_workflow.md`:**
   - Align with RFC-004 single-doc strategy
   - Update tool names and workflow diagrams

6. **Testing:**
   - Create integration test for full M1 workflow
   - Test progressive saving and resume capability

## Related Documents

- [RFC-001: Unified Logging](RFC-001-unified-logging.md)
- [RFC-002: QFMD Naming](RFC-002-markdown-format-naming.md)
- [SPEC_M1_M4_OUTPUTS_FULL.md](../specs/SPEC_M1_M4_OUTPUTS_FULL.md)
- [ADR-007: Tool Naming Convention](../adr/ADR-007-tool-naming-convention.md)
- [m1_complete_workflow.md](../workflows/m1_complete_workflow.md) - Needs sync with this RFC
