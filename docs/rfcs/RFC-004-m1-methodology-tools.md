# RFC-004: M1 Methodology Tools for qf-scaffolding

| Field | Value |
|-------|-------|
| **Status** | Phase 0-1 Complete, Phase 2-3 Draft |
| **Created** | 2026-01-17 |
| **Updated** | 2026-01-17 |
| **Author** | Niklas Karlsson |
| **Relates to** | qf-scaffolding, RFC-001 (logging), RFC-002 (QFMD), SPEC_M1_M4_OUTPUTS_FULL.md |

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

#### 1. `read_materials` - Read files from 00_materials/

```typescript
interface ReadMaterialsInput {
  project_path: string;
  file_pattern?: string;  // e.g., "*.pdf", "lecture*.md"
  extract_text?: boolean; // For PDFs: extract text content
}

interface ReadMaterialsResult {
  success: boolean;
  materials: Array<{
    filename: string;
    path: string;
    content_type: "pdf" | "md" | "txt" | "pptx" | "other";
    size_bytes: number;
    text_content?: string;  // If extract_text=true
    error?: string;         // If extraction failed
  }>;
  total_files: number;
  total_chars?: number;
}
```

**Purpose:** Read instructional materials from the project's 00_materials/ folder.
- Supports PDF text extraction (built-in, no external tools needed)
- Supports markdown, text, and other formats
- Returns content within MCP response (no file copying needed)
- Logs read operations (RFC-001 compliant)

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

### M1 Complete Workflow (Correct)

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
├── 01_methodology/         ← Empty (for outputs)
├── methodology/            ← Copies M1-M4 from QuestionForge
│   └── m1/
│       ├── m1_0_intro.md
│       ├── m1_1_stage0_material_analysis.md
│       └── ...
├── session.yaml
├── kursplan.md             ← Fetched from URL (NEW: RFC-004 fix)
└── logs/
```

**M1 Workflow (qf-scaffolding):**
```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 0: Introduction                                           │
├─────────────────────────────────────────────────────────────────┤
│ 1. load_stage(module="m1", stage=0, project_path="...")         │
│    → Reads project/methodology/m1/m1_0_intro.md                 │
│    → Returns: Framework overview, principles                    │
│                                                                 │
│ 2. Teacher reads introduction                                   │
│ 3. Teacher says "fortsätt"                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: Material Analysis (Claude's solo work)                 │
├─────────────────────────────────────────────────────────────────┤
│ 1. load_stage(module="m1", stage=1, project_path="...")         │
│    → Reads project/methodology/m1/m1_1_stage0_material_analysis │
│    → Returns: How to analyze materials, output format           │
│                                                                 │
│ 2. read_materials(project_path="...", extract_text=true)        │
│    → Returns: All PDF/MD content from 00_materials/             │
│                                                                 │
│ 3. read_reference(project_path="...")                           │
│    → Returns: Kursplan content                                  │
│                                                                 │
│ 4. Claude analyzes (NO filesystem tools needed)                 │
│    → Identifies Tier 1-4 topics                                 │
│    → Catalogs examples                                          │
│    → Notes misconceptions                                       │
│                                                                 │
│ 5. Claude presents findings to teacher                          │
│                                                                 │
│ 6. complete_stage(                                              │
│      project_path="...",                                        │
│      module="m1",                                               │
│      stage=0,  ← Stage 0 OUTPUT                                 │
│      output={                                                   │
│        type: "material_analysis",                               │
│        data: { ... }  ← Validated against MaterialAnalysisSchema│
│      }                                                          │
│    )                                                            │
│    → Saves: 01_methodology/m1_material_analysis.md              │
│    → Updates: session.yaml                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2-5: Dialogue with Teacher                                │
├─────────────────────────────────────────────────────────────────┤
│ Similar pattern:                                                │
│ 1. load_stage → Get instructions                                │
│ 2. Dialogue with teacher                                        │
│ 3. complete_stage → Save output (if applicable)                 │
│                                                                 │
│ Stages and Outputs:                                             │
│ ├── Stage 2 (Emphasis)     → m1_emphasis_patterns.md            │
│ ├── Stage 3 (Examples)     → m1_examples.md                     │
│ ├── Stage 4 (Misconceptions)→ m1_misconceptions.md              │
│ └── Stage 5 (Objectives)   → m1_learning_objectives.md          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ M1 COMPLETE → Continue to M2                                    │
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
| `load_stage` | Keep as-is (returns instructions text) |
| `complete_stage` | Already validates schema, generates QFMD output |

| New Tool | Purpose |
|----------|---------|
| `read_materials` | Read content from 00_materials/ |
| `read_reference` | Read reference docs from project root |
| `get_methodology` | Load instructions + schema together |

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

### Output Format: QFMD Compliance

All M1 outputs use the schemas we already implemented:

| Stage | Output Type | Schema |
|-------|-------------|--------|
| 0 | `material_analysis` | MaterialAnalysisSchema |
| 2 | `emphasis_patterns` | EmphasisPatternsSchema |
| 3 | `examples` | ExamplesSchema |
| 4 | `misconceptions` | MisconceptionsSchema |
| 5 | `learning_objectives` | LearningObjectivesSchema |

`complete_stage` already validates against these schemas and generates YAML frontmatter + Markdown body.

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

### Phase 2: Methodology Integration
1. `get_methodology` - Combined instructions + output schema
2. Ensure `load_stage` is always called with `project_path`

### Phase 3: Documentation
1. Update WORKFLOW.md with correct tool usage
2. Add Claude.ai prompt guidance for M1 workflow
3. Create example M1 session transcript showing correct flow

### Dependency Graph

```
Phase 0: Fix load_stage
    ↓
Phase 1: read_materials, read_reference
    ↓
Phase 2: get_methodology (optional enhancement)
    ↓
Phase 3: Documentation
```

**Phase 0 is a blocker** - without it, the intended workflow cannot function.

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

### Full Implementation
- [ ] M1 session completes using ONLY qf-scaffolding tools (no Filesystem tools)
- [ ] All outputs follow QFMD standard with proper YAML frontmatter
- [ ] No files created outside project directory
- [ ] Session can be resumed from session.yaml state
- [ ] Logs capture full audit trail (RFC-001)

### Verification Test
```
1. Create project with step0_start (copies methodology)
2. Modify project/methodology/m1/m1_0_intro.md (add marker text)
3. Call load_stage(module="m1", stage=0, project_path="...")
4. Verify returned content contains marker text
5. If marker NOT found → bug still exists
```

## Related Documents

- [RFC-001: Unified Logging](RFC-001-unified-logging.md)
- [RFC-002: QFMD Naming](RFC-002-markdown-format-naming.md)
- [SPEC_M1_M4_OUTPUTS_FULL.md](../specs/SPEC_M1_M4_OUTPUTS_FULL.md)
- [ADR-007: Tool Naming Convention](../adr/ADR-007-tool-naming-convention.md)
