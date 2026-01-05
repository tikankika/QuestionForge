# DISCOVERY BRIEF: QuestionForge

**Status:** Complete  
**Created:** 2026-01-02  
**Phase:** DISCOVER → SHAPE (Complete)  
**Source:** Extended dialogue session analyzing existing MQG ecosystem

---

## Problem Statement

The Modular Question Generation (MQG) framework has grown organically into a fragmented ecosystem of overlapping tools, duplicated functionality, and unclear boundaries. Teachers need a streamlined, pedagogically-focused workflow to create high-quality assessment questions that export to QTI format for Inspera LMS. The current state makes this unnecessarily complex.

**Core need:** Transform instructional materials into validated QTI question packages through a teacher-led, AI-assisted process.

---

## Current State Analysis

### Existing Projects (Fragmented)

| Project | Location | Language | Tools | Status |
|---------|----------|----------|-------|--------|
| QTI-Generator-for-Inspera_MPC | `/AIED_EdTech_projects/` | TypeScript | 18 tools | Active, bloated |
| MPC_MQG_v3 | `/AIED_EdTech_projects/` | TypeScript | 5 tools | Active, duplicates validation |
| Modular QGen Framework | `/AIED_EdTech_projects/` | Docs only | 46 files, ~8000 lines | BB1-BB6 methodology |
| QTI-Generator-for-Inspera | GitHub | Python | Core QTI code | Original, to be wrapped |
| Assessment_suite | `/AIED_EdTech_projects/` | TS + Python | Grading workflow | SEPARATE PROJECT (excluded) |

### The Fragmentation Problem

```
Current Reality:
                                                    
  ┌─────────────────────┐     ┌─────────────────────┐
  │ QTI-Generator-MPC   │     │ MPC_MQG_v3          │
  │ 18 tools:           │     │ 5 tools:            │
  │ - validate_bb6  ◄───┼─────┼─► validate_bb6      │  ← DUPLICATE!
  │ - edit questions    │     │ - apply_bb6         │
  │ - convert formats   │     │ - show_status       │
  │ - analyze           │     │                     │
  │ - export            │     │                     │
  └─────────────────────┘     └─────────────────────┘
           │                           │
           └───────────┬───────────────┘
                       │
                       ▼
             NO CLEAR WORKFLOW
             NO SHARED SPECS
             MIXED CONCERNS
```

### What Works (To Preserve)

1. **MQG Methodology Documentation** - 46 files of pedagogical guidance (BB1-BB5)
2. **Field Requirements Spec v6.3** - Comprehensive question type specifications
3. **QTI Generator Python Code** - Proven export functionality
4. **Assessment_suite patterns** - Phase-based MCP architecture (for reference)

---

## Pain Points Identified

### 1. Functional Duplication
- `validate_bb6` exists in TWO separate MCPs
- Validation logic not shared
- Risk of divergent behavior as each evolves independently

### 2. Unclear Boundaries
QTI-Generator-for-Inspera_MPC has 18 tools doing fundamentally different things:
- Validation (checking format)
- Editing (modifying content)
- Conversion (changing format)
- Analysis (quality checking)
- Export (generating QTI)

These should NOT be in one MCP.

### 3. Naming Confusion
- "BB" (Building Block) is internal jargon - users don't understand
- "BB6" = Export & Validation - not intuitive
- "MPC" vs "MCP" inconsistency in naming
- Version suffixes (v3, v6.5, v6.3) add confusion

### 4. No Clear Workflow
- Each tool is an island
- No pipeline connecting creation → validation → export
- Teacher doesn't know which tool to use when

### 5. Missing Coordination
- No shared specifications
- Each MCP defines its own formats
- No common metadata definitions

### 6. Pedagogical vs Technical Mixing
- Low-level utilities mixed with high-level pedagogical processes
- No concept of MCPs calling each other
- No layered architecture

---

## Constraints

| Constraint | Reason | Impact |
|------------|--------|--------|
| Inspera LMS target | Primary platform for Swedish higher ed | Must support Inspera QTI requirements |
| Swedish context | Swedish higher education focus | Swedish terminology, E-C-A grading awareness |
| Teacher-led process | Pedagogical decisions by humans | AI facilitates, doesn't decide |
| Existing QTI code | Python QTI generator works | Wrap, don't rewrite |
| Field Requirements v6.3 | Comprehensive spec exists | Use as foundation for validation |
| 15 question types | Inspera supports these | Must handle all types |

### Valid Question Types (from v6.3 spec)

```
multiple_choice_single    text_entry              match
multiple_response         text_entry_math         hotspot
true_false                text_entry_numeric      graphicgapmatch_v2
inline_choice             text_area               text_entry_graphic
essay                     audio_record            composite_editor
nativehtml
```

---

## Solution Direction (From SHAPE Phase)

### Architecture: Two Focused MCPs

```
┌─────────────────────────────────────────────────────────────────┐
│                    QuestionForge ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  MCP 1: qf-scaffolding (TypeScript/Node.js)                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  PURPOSE: Methodology guidance for Claude Desktop          │  │
│  │  PATTERN: NON-LINEAR, flexible entry points                │  │
│  │                                                            │  │
│  │  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐                    │  │
│  │  │ M1  │   │ M2  │   │ M3  │   │ M4  │                    │  │
│  │  │Content│ │Design│  │Gen  │   │ QA  │                    │  │
│  │  └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘                    │  │
│  │     └─────────┴────┬────┴─────────┘                        │  │
│  │            FLEXIBLE NAVIGATION                             │  │
│  │                                                            │  │
│  │  OUTPUT: Questions in markdown format                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  MCP 2: qf-pipeline (Python + Wrappers)                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  PURPOSE: Build, validate, and export to QTI               │  │
│  │  PATTERN: LINEAR pipeline with decision points             │  │
│  │                                                            │  │
│  │  Step 1: Guided Build ──▶ Step 2: Validate ──┐             │  │
│  │              ▲                                │             │  │
│  │              └────────── (if errors) ─────────┘             │  │
│  │                                                            │  │
│  │              Step 3: Decision ──┬──▶ QTI Questions          │  │
│  │                                 └──▶ Question Set           │  │
│  │                                           │                 │  │
│  │              Step 4: Export to QTI ◀──────┘                 │  │
│  │                                                            │  │
│  │  OUTPUT: QTI package for Inspera                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  SHARED: qf-specifications/                                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  ├── question-types/*.md    # Per-type specifications      │  │
│  │  ├── question-format-v7.md  # Overall format spec          │  │
│  │  ├── metadata-schema.json   # Metadata rules               │  │
│  │  └── label-taxonomy.yaml    # Valid labels                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Module Structure (Renamed from BB)

**Original BB structure:** BB1, BB2, BB3, BB4, BB5, BB6

**Proposed Module structure:** M1, M2, M3, M4 (4 modules instead of 6)

| Module | Name | Purpose | Entry Point |
|--------|------|---------|-------------|
| M1 | Content Analysis | What was taught? | Instructional materials |
| M2 | Assessment Planning | Types, distribution, metadata, labels | Existing objectives OR M1 output |
| M3 | Question Generation | Create the questions | Blueprint from M2 |
| M4 | Quality Assurance | Pedagogical validation | Questions from M3 |

**Key change:** M2 + M3 (old) merged into single Assessment Planning module. Original M3 (Technical Setup) was Inspera-specific; metadata/labels absorbed into M2.

**BB6 disposition:** Not a module - it's the pipeline (MCP 2). Export/validation is technical, not pedagogical.

---

## MCP 2 Pipeline Detail

### Step 1: Guided Build Process (Critical Innovation)

```
For each question in exam-set:

  1. READ question (Q001)
  2. IDENTIFY question type (from @type field)
  3. LOAD specification for that type (.md file)
  4. COMPARE question to specification
  5. SUGGEST corrections to teacher
  6. TEACHER decides: accept / modify / skip
  7. APPLY fix to Q001
  8. APPLY same fix to ALL similar question types  ← KEY FEATURE
  9. MOVE to next question (Q002...)
```

**Key innovation:** Fix once, apply to all similar types. If Q001 (MC single) has a feedback structure problem, fixing it fixes ALL MC single questions.

### Steps 2-4: Validation and Export

- **Step 2:** Batch validation (loop back to Step 1 if errors)
- **Step 3:** Teacher decision (QTI questions vs Question Set, with/without labels)
- **Step 4:** Generate QTI package for Inspera

### MCP Integration: MCP 2 Can Call MCP 1

**Key design decision:** MCP 2 (pipeline) can call MCP 1 (scaffolding) for analysis tasks.

```
MCP 2: qf-pipeline
│
├── Step 1: Guided Build
│   └── Question-by-question format validation
│
├── Step 1.5: Summary Analysis (FUTURE)
│   ├── Variation of questions check
│   ├── Final distractor analysis        ← CALLS MCP 1 M4
│   ├── Language consistency check        ← CALLS MCP 1 M4
│   └── Pedagogical quality review        ← CALLS MCP 1 M4
│
├── Step 2: Validator
├── Step 3: Decision
└── Step 4: Export
```

**Rationale:** 
- Distractor/pedagogical analysis logic lives in MCP 1 (M4: QA)
- MCP 2 Step 1 focuses on FORMAT validation only
- MCP 2 Step 1.5 (future) calls MCP 1 for PEDAGOGICAL analysis
- Avoids duplicating analysis code
- Clear separation: format (MCP 2) vs pedagogy (MCP 1)

**Future development ideas (Step 1.5):**
- Summary check of all questions together
- Variation analysis across question bank
- Final distractor quality check
- Language/terminology consistency
- All pedagogical analysis delegated to MCP 1 M4

---

## Key Decisions Made (Pending ADRs)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Number of MCPs | 2 | Simple, clear responsibilities |
| MCP 1 language | TypeScript | Consistent with assessment-mcp pattern |
| MCP 2 language | Python | Wraps existing QTI-Generator code |
| BB → Module | M1-M4 | Clearer naming, less jargon |
| M2+M3 merge | Yes | Reduces cognitive load, natural grouping |
| BB6 location | MCP 2 | It's pipeline/export, not pedagogy |
| MCP 1 pattern | Non-linear | Flexible entry points, teacher choice |
| MCP 2 pattern | Linear | Step-by-step with validation loops |
| Specifications | Shared folder | Single source of truth for both MCPs |

---

## Open Questions

### Resolved in This Session

1. ✅ "Validator - wrapper or Python MCP?" → Python MCP wrapping existing code
2. ✅ "Export - wrapper or Python MCP?" → Python MCP wrapping QTI-Generator
3. ✅ "Same MCP as validator or separate?" → Same MCP (qf-pipeline), different steps
4. ✅ "BB is not a good name?" → Yes, renamed to Module (M1-M4)
5. ✅ "M3 too Inspera-specific?" → Merged into M2, made platform-agnostic

### Still Open

1. **M2 Stage Details:** Exact stages within Assessment Planning module
2. **Specification Migration:** How to migrate from v6.3 to v7 format spec
3. **Legacy Tool Migration:** Timeline for archiving old MCPs
4. **Testing Strategy:** How to validate the new architecture works

---

## Success Criteria

- [ ] Two MCPs deployed and functional
- [ ] Full workflow from materials → QTI package works
- [ ] Teacher can use flexible entry points (start at any module)
- [ ] Guided build process handles all 15 question types
- [ ] Validation catches format errors before export
- [ ] Single source of truth for specifications
- [ ] Old MCPs archived, no duplication
- [ ] Documentation complete for teacher onboarding

---

## Existing Assets to Migrate/Wrap

### From QTI-Generator-for-Inspera_MPC (18 tools)

| Tool | Destination |
|------|-------------|
| validate_bb6, validate_bb6_chunked, analyze_format | MCP 2: Step 2 |
| read_questions, update_question, delete_question, rewrite_question, batch_update | MCP 2: Step 1 |
| preview_conversion, convert_to_v65, fix_bb6_errors | MCP 2: Step 1 |
| analyze_distractors | MCP 1: M4 (QA) |
| Session tools | Redesigned in MCP 2 |
| get_metadata, execute_command | Deprecated |

### From MPC_MQG_v3 (5 tools)

| Tool | Destination |
|------|-------------|
| validate_bb6 | MCP 2: Step 2 (remove duplicate) |
| apply_bb6_conversion | MCP 2: Step 1 |
| show_bb_status | MCP 1: navigation |
| create_manifest | MCP 1: stage management |
| save_version | MCP 2: Step 1 |

### From Modular QGen Framework (Docs)

| Content | Destination |
|---------|-------------|
| BB1 (8 files) | qf-specifications/modules/m1-content-analysis/ |
| BB2 (9 files) | qf-specifications/modules/m2-assessment-planning/ (merged with BB3) |
| BB3 (7 files) | Merged into M2 |
| BB4 (5 files) | qf-specifications/modules/m3-question-generation/ |
| BB5 (6 files) | qf-specifications/modules/m4-quality-assurance/ |
| BB6 Field Requirements v6.3 | qf-specifications/question-format-v7.md |

---

## Project Name

**QuestionForge** - Selected for:
- Memorable, professional
- "Forge" implies craftsmanship and creation
- Works for git repo: `questionforge`
- Clear purpose: forging/creating questions

---

## Next Steps (ACDM Workflow)

1. **DECIDE Phase:** Create ADRs for key decisions
   - ADR-001: Two-MCP Architecture
   - ADR-002: Module Naming (BB → M1-M4)
   - ADR-003: Language Choices
   - ADR-004: M2+M3 Merge

2. **COORDINATE Phase:** Write implementation specs
   - qf-scaffolding-mcp specification
   - qf-pipeline-mcp specification
   - qf-specifications structure

3. **Build Phase:** Implementation order
   - Phase 1: Create qf-specifications/ (shared foundation)
   - Phase 2: Build MCP 2 (qf-pipeline) - more concrete, wraps existing code
   - Phase 3: Build MCP 1 (qf-scaffolding) - methodology layer
   - Phase 4: Archive old MCPs

---

## References

- **Field Requirements v6.3:** `/Modular QGen Framework/docs/MQG_0.2/MQG_bb6_Field_Requirements_v06.md`
- **MQG Complete Overview:** `/Modular QGen Framework/docs/MQG_0.2/MQG_COMPLETE_OVERVIEW.md`
- **Assessment_suite (pattern reference):** `/Assessment_suite/` (separate project)
- **ACDM Methodology:** `/Nextcloud/AIED_EdTech_Dev_documentation/AI-Collaborative Development Method (ACDM)/`

---

## Source Documentation

This brief was synthesized from an extended dialogue session exploring the fragmented MQG ecosystem and designing the QuestionForge architecture.

**Full chat history:** [Restructuring QTI generation architecture with modular MCPs 2026-01-02.md](chat_claude_desctop/Restructuring%20QTI%20generation%20architecture%20with%20modular%20MCPs%202026-01-02.md)

The chat contains:
- Deep analysis of existing tools and their overlaps
- Exploration of architectural options (5-layer vs 2-MCP)
- Discussion of M2+M3 merge decision
- Detailed tool specifications for both MCPs
- Field Requirements v6.3 analysis
- Naming discussions (BB → Module, project name)

---

*DISCOVER + SHAPE phases complete*  
*Ready for DECIDE phase*  
*Created through extended dialogue session 2026-01-02*
