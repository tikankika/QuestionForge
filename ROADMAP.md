# QuestionForge Roadmap

**Last updated:** 2026-02-04

---

## Project Overview

QuestionForge is an MCP-based tool for creating, validating, and exporting quiz questions to QTI format for Inspera.

---

## Phase 1: Basic Pipeline ✅ COMPLETE

| Task | Status | Date |
|------|--------|------|
| Export wrappers (parser, generator, packager) | ✅ Complete | 2025-12 |
| MCP server setup | ✅ Complete | 2025-12 |
| Validator wrapper | ✅ Complete | 2025-12 |
| Session management (step0_start, step0_status) | ✅ Complete | 2026-01-05 |
| GitHub repo created | ✅ Complete | 2026-01-05 |

---

## Phase 1.5: Refactoring ✅ COMPLETE

### 1.5.1 Tool Naming Convention (ADR-007) ✅ COMPLETE
| Task | Status | Date |
|------|--------|------|
| Decision: `stepN_` prefix | ✅ Complete | 2026-01-06 |
| Documented in ADR-007 | ✅ Complete | 2026-01-06 |
| Implemented in server.py | ✅ Complete | 2026-01-07 |

### 1.5.2 Standalone Migration (ADR-008) ✅ COMPLETE
| Task | Status | Date |
|------|--------|------|
| DISCOVER phase | ✅ Complete | 2026-01-06 |
| Decision: Alternative A (full copy) | ✅ Complete | 2026-01-06 |
| Implementation: qti-core copied | ✅ Complete | 2026-01-07 |

**Result:**
- QTI-Generator-for-Inspera copied as `packages/qti-core/`
- 114 files (excl. .git, .venv, __pycache__, output)
- Wrapper paths updated from absolute to relative
- QuestionForge is now fully standalone

---

## Phase 2: Guided Build ✅ REFACTORED

### Step 1: Minimal Safety Net (Vision A) ✅ (2026-01-28)

**Refactoring:** Step 1 redesigned from "Interactive Guided Build" (3700 lines) to "Minimal Safety Net" (~289 lines).

| Task | Status | Date |
|------|--------|------|
| RFC-013 v2.5: Step 1 Vision A spec | ✅ Complete | 2026-01-28 |
| Archive old modules (7 files → `_archived/`) | ✅ Complete | 2026-01-28 |
| `step1_review` - show question + issues | ✅ Complete | 2026-01-28 |
| `step1_manual_fix` - manual fix | ✅ Complete | 2026-01-28 |
| `step1_delete` - delete question | ✅ Complete | 2026-01-28 |
| `step1_skip` - skip question | ✅ Complete | 2026-01-28 |
| Old tools → deprecation stubs | ✅ Complete | 2026-01-28 |

**Vision A Principles:**
- Step 1 used ONLY when Step 3 auto-fix fails
- Normal flow: M5 → Step 2 → Step 3 → Step 4 (Step 1 skipped)
- Step 1 handles: unknown errors, Step 3 failures, structural issues

**Archived modules (3200+ lines):**
- `analyzer.py` → Replaced by Step 2 validator
- `transformer.py` → Replaced by Step 3 auto-fix
- `structural_issues.py` → Replaced by pipeline_router
- `detector.py`, `patterns.py`, `prompts.py`, `session.py`

**Retained modules (~520 lines):**
- `frontmatter.py` - YAML progress tracking
- `parser.py` - Question parsing
- `decision_logger.py` - Decision logging

### Step 2: Validator ✅ COMPLETE
| Task | Status | Date |
|------|--------|------|
| Validation output improvement (ADR-012) | ✅ Complete | 2026-01-06 |
| `^tags` as alternative to `^labels` | ✅ Complete | 2026-01-07 |
| step2_complete signal | ✅ Complete | 2026-01-08 |

---

## Phase 2.5: Shared Session (ADR-014) ✅ COMPLETE

**Description:** Shared session between qf-pipeline and qf-scaffolding

| Task | Status | Date |
|------|--------|------|
| ADR-014: Shared Session architecture | ✅ Complete | 2026-01-14 |
| 5 Entry Points (m1/m2/m3/m4/pipeline) | ✅ Complete | 2026-01-14 |
| source_file Optional for m1 | ✅ Complete | 2026-01-14 |
| New folders: 00_materials/, methodology/ | ✅ Complete | 2026-01-14 |
| methodology section in session.yaml | ✅ Complete | 2026-01-14 |
| URL auto-fetch for source_file | ✅ Complete | 2026-01-14 |
| materials_folder parameter (m1) | ✅ Complete | 2026-01-16 |
| sources.yaml tracking | ✅ Complete | 2026-01-15 |
| Methodology copy to project | ✅ Complete | 2026-01-15 |

**Entry Points:**
| Entry Point | source_file | Next Module |
|-------------|-------------|-------------|
| m1 | ❌ Optional | M1 (scaffolding) |
| m2 | ✅ Required | M2 (scaffolding) |
| m3 | ✅ Required | M3 (scaffolding) |
| m4 | ✅ Required | M4 (scaffolding) |
| pipeline | ✅ Required | Pipeline direct |

---

## Phase 3: Decision & Export ⏳ NEXT

### Step 3: Decision Tool (ADR-010, ADR-011)
| Task | Status |
|------|--------|
| ADR-010: Step 3 architecture | ✅ Proposed |
| ADR-011: Question Set Builder | ✅ Proposed |
| `step3_question_set` implementation | ⬜ Planned |

**Two export paths:**
- **Path A:** Direct export (simple questions → QTI)
- **Path B:** Question Set Builder (filtering, sections, random selection)

### Step 4: Export ✅ COMPLETE (RFC-012 Resolved)
| Task | Status | Date |
|------|--------|------|
| `step4_export` - generate QTI package | ✅ Complete | 2026-01 |
| Tags → Labels mapping | ✅ Complete | 2026-01 |
| Resource handling (images etc) | ✅ Fixed | 2026-01-28 |
| Auto-load session from project folder | ✅ Complete | 2026-01-28 |

**RFC-012 RESOLVED:**
- Subprocess approach: Pipeline calls `scripts/` for validation + export
- `apply_resource_mapping()` now runs correctly via `generate_qti_package.py`
- Session auto-loads from project if input is in `pipeline/` or `questions/`

### Pipeline Router ✅ NEW (2026-01-28)

| Task | Status | Date |
|------|--------|------|
| `pipeline_route` tool | ✅ Complete | 2026-01-28 |
| Error categorisation (MECHANICAL/STRUCTURAL/PEDAGOGICAL) | ✅ Complete | 2026-01-28 |
| Routing to correct handler | ✅ Complete | 2026-01-28 |

**Routing logic:**
| Category | Handler | Description |
|----------|---------|-------------|
| MECHANICAL | Step 3 | Syntax errors that can be auto-fixed |
| STRUCTURAL | Step 1 | Requires teacher decision |
| PEDAGOGICAL | M5 | Content problems, back to M5 |
| NONE | Step 4 | All validated, ready for export |

**File:** `tools/pipeline_router.py`

### RFC-014: Resource Handling 📋 DRAFT

**Description:** Handling resources for complex question types (images, audio, coordinates)

| Task | Status | Date |
|------|--------|------|
| RFC-014 placeholder created | ✅ Complete | 2026-01-28 |
| Implementation | ⬜ Planned | - |

**Question types requiring resource handling:**
- `hotspot` - Image + coordinates
- `graphicgapmatch_v2` - Image + drop zones
- `audio_record` - Audio file
- `text_entry_graphic` - Image + text fields

**Features (planned):**
- Resource discovery (find referenced files)
- Coordinate editor (visualise zones)
- File path management (normalise, copy)
- Preview in terminal or GUI

**Priority:** Low - awaiting pipeline stabilisation

---

## Phase 4: Unified Logging (RFC-001) ✅ COMPLETE

**Status:** TIER 1-2 Complete, TIER 3-4 planned

### TIER 1-2: Implemented ✅

| Task | Status | Date |
|------|--------|------|
| RFC-001 specification | ✅ Complete | 2026-01-16 |
| JSON Schema (qf-specifications/logging/) | ✅ Complete | 2026-01-16 |
| Python logger (RFC-001 compliant) | ✅ Complete | 2026-01-16 |
| TypeScript logger (qf-scaffolding) | ✅ Complete | 2026-01-17 |
| **TIER 1:** tool_start/end/error | ✅ Complete | 2026-01-17 |
| **TIER 2:** session_start/resume/end | ✅ Complete | 2026-01-17 |
| **TIER 2:** stage_start/complete | ✅ Complete | 2026-01-17 |
| **TIER 2:** validation_complete, export_complete | ✅ Complete | 2026-01-17 |

**TIER 1-2 events:**
| Event | File | Description |
|-------|------|-------------|
| tool_start/end/error | server.py, load_stage.ts | All tool calls |
| session_start | session_manager.py | New session |
| session_resume | server.py | Resume session |
| session_end | session_manager.py | End session |
| stage_start/complete | load_stage.ts | M1-M4 stages |
| validation_complete | server.py | Validation successful |
| export_complete | server.py | Export complete |

### TIER 3: Audit Trail 🔄 Partial

| Task | Status | Dependency |
|------|--------|------------|
| format_detected | ✅ Complete | - |
| format_converted | ✅ Complete | - |
| user_decision | ⬜ Planned | M1-M4 implementation |

**Awaiting:** M1-M4 scaffolding implementation to define user_decision events.

### TIER 4: ML Training ⏸️ Parked

| Task | Status | Timeline |
|------|--------|----------|
| user_decision (full context) | ⏸️ Parked | Q2-Q3 2026 |
| ai_suggestion | ⏸️ Parked | Q2-Q3 2026 |
| correction_made | ⏸️ Parked | Q2-Q3 2026 |

**Requirements:** TIER 1-3 complete + >100 sessions collected. See RFC-003.

**Files:**
- `docs/rfcs/RFC-001-unified-logging.md`
- `docs/rfcs/RFC-003-ml-training-placeholder.md`
- `qf-specifications/logging/schema.json`

---

## Phase 5: qf-scaffolding 🔶 M1 IMPLEMENTATION COMPLETE

**Description:** TypeScript MCP for pedagogical scaffolding (M1-M4)

### Basic Setup ✅
| Task | Status | Date |
|------|--------|------|
| MVP: `load_stage` tool | ✅ Complete | 2026-01-14 |
| M1-M4 stage loading | ✅ Complete | 2026-01-16 |
| `requiresApproval` field | ✅ Complete | 2026-01-16 |
| Methodology files imported (28 files) | ✅ Complete | 2026-01-14 |
| TypeScript logger (RFC-001) | ✅ Complete | 2026-01-17 |
| TIER 1-2 logging | ✅ Complete | 2026-01-17 |

### RFC-004: M1 Methodology Tools ✅
| Task | Status | Date |
|------|--------|------|
| Phase 0: `load_stage` path fix | ✅ Complete | 2026-01-17 |
| Phase 1: `read_materials`, `read_reference` | ✅ Complete | 2026-01-17 |
| Phase 2: `save_m1_progress` tool | ✅ Complete | 2026-01-19 |
| Phase 2: `read_materials` filename param | ✅ Complete | 2026-01-19 |
| Phase 2: `load_stage` stage numbering fix | ✅ Complete | 2026-01-19 |
| Workflow documentation (v3.0) | ✅ Complete | 2026-01-19 |

**RFC-004 Key Decisions:**
- Single document strategy: `m1_analysis.md`
- 6 stages (0-5) instead of 8
- Progressive saving during Stage 0 (after each PDF)
- Stage-completion saves for dialogue stages (1-5)

### M1 Tools (complete) ✅
| Tool | Description |
|------|-------------|
| `load_stage` | Load methodology for stage 0-5 |
| `read_materials` | List files (list mode) or read ONE file (read mode) |
| `read_reference` | Read curriculum etc. |
| `save_m1_progress` | Progressive saving to `m1_analysis.md` |
| `write_m1_stage` | **NEW** Direct file writing per stage (separate files) |

### write_m1_stage Tool ✅ (2026-01-21)
| Task | Status | Date |
|------|--------|------|
| Tool implementation | ✅ Complete | 2026-01-21 |
| Separate files per stage (0-5) | ✅ Complete | 2026-01-21 |
| m1_progress.yaml tracking | ✅ Complete | 2026-01-21 |
| Overwrite protection | ✅ Complete | 2026-01-21 |

**Principle:** "What Claude writes = what gets saved"
- Each stage gets its own file: `m1_stage0_materials.md`, `m1_stage1_validation.md`, etc.
- Automatic progress tracking in `m1_progress.yaml`
- Safety: Does not overwrite without explicit `overwrite=true`

### RFC-007: LLM Workflow Control Patterns ✅
| Task | Status | Date |
|------|--------|------|
| Problem analysis (M1 session failures) | ✅ Complete | 2026-01-19 |
| Core principles documented | ✅ Complete | 2026-01-19 |
| Patterns that work (A/B/C) | ✅ Complete | 2026-01-19 |
| Reality Check section | ✅ Complete | 2026-01-19 |
| Final Recommendation: Option A | ✅ Complete | 2026-01-19 |
| Teacher-facing methodology | ✅ Complete | 2026-01-19 |

**RFC-007 Key Findings:**
- MCP cannot "control" Claude - only provide tools and guidance
- User-driven workflows (Option A): ~95% reliable
- Tool constraints (Option B/C): ~70% reliable
- "One-at-a-time with feedback" requires user to drive each step

**Decision:** Option A (User-Driven) for M1 Stage 0
- Teacher says: "Analyse [file]" → Claude analyses → "Save and continue"
- Methodology rewritten as teacher guide

### RFC-009: M3 Conversation Capture 📋 DRAFT
| Task | Status | Date |
|------|--------|------|
| Problem analysis (M3 vs M1/M2 patterns) | ✅ Complete | 2026-01-21 |
| RFC-009 draft created | ✅ Complete | 2026-01-21 |
| `append_m3_question` tool design | 📋 Draft | - |
| Implementation | ⬜ Planned | - |

**RFC-009 Key Insight:**
- M1/M2: Stage-based → save complete document at once
- M3: Iterative conversation → accumulate questions incrementally
- M3 needs different tooling than `write_m1_stage`

### RFC-016: M5 Self-Learning Format Recognition ✅ COMPLETE (2026-01-29)

**Description:** M5 (Content Completeness & QFMD Generation) with self-learning format recognition.

| Task | Status | Date |
|------|--------|------|
| RFC-016 specification | ✅ Complete | 2026-01-26 |
| Format learner implementation | ✅ Complete | 2026-01-27 |
| BUG 1-2: Separator regex + format detection | ✅ Fixed | 2026-01-28 |
| BUG 3: Parse validation | ✅ Fixed | 2026-01-29 |
| BUG 4: Field normalisation | ✅ Fixed | 2026-01-29 |
| BUG 6: STOP points (teacher gates) | ✅ Fixed | 2026-01-29 |
| BUG 7: Missing field warnings | ✅ Fixed | 2026-01-29 |
| Option B: Data-driven field aliases | ✅ Complete | 2026-01-29 |

**M5 Tools (complete):**
| Tool | Description |
|------|-------------|
| `m5_start` | Start M5 session, load format patterns |
| `m5_detect_format` | Detect/confirm question format |
| `m5_analyze` | Parse questions, show validation |
| `m5_approve` | Approve question (with STOP points) |
| `m5_manual_fix` | Manual correction |
| `m5_finish` | End session, save patterns |
| `m5_add_field_alias` | **NEW** Add field alias |
| `m5_remove_field_alias` | **NEW** Remove field alias |
| `m5_list_field_aliases` | **NEW** List all field aliases |

**Option B - Data-Driven Field Aliases:**
- Default aliases for Swedish/English variants (30+)
- Customisable per project via `logs/m5_format_patterns.json`
- Self-learning: new aliases saved automatically
- Example: `stem → question_text`, `svårighetsgrad → difficulty`

**Files:**
- `packages/qf-scaffolding/src/m5/format_learner.ts`
- `packages/qf-scaffolding/src/tools/m5_interactive_tools.ts`
- `docs/rfcs/RFC-016-m5-self-learning-format-recognition.md`

### Remaining Work
| Task | Status |
|------|--------|
| Test M1 with Option A workflow | ⬜ Next |
| Update M1 methodology for `write_m1_stage` | ⬜ Next |
| User decision logging (TIER 3) | ⬜ Planned |
| M2 tools (can use write_m1_stage) | ⬜ Planned |
| M3 tools (RFC-009: append_m3_question) | ⬜ Planned |
| M4 tools implementation | ⬜ Planned |

**Methodology structure:**
```
methodology/
├── m1/  (6 files) - Material Analysis (Stage 0-5)
├── m2/  (9 files) - Assessment Design
├── m3/  (5 files) - Question Generation
└── m4/  (6 files) - Quality Assurance
```

---

## Pipeline Status

| Step | Name | Status | Updated |
|------|------|--------|---------|
| Step 0 | Session + Entry Points | ✅ Complete | 2026-01 |
| Step 1 | Minimal Safety Net (Vision A) | ✅ Refactored | 2026-01-28 |
| Step 2 | Validator | ✅ Complete | 2026-01 |
| Router | Pipeline Router | ✅ NEW | 2026-01-28 |
| Step 3 | Auto-fix | ✅ Complete | 2026-01-22 |
| Step 4 | Export | ✅ Complete (RFC-012 resolved) | 2026-01-28 |

**New Pipeline Flow (2026-01-28):**
```
M5 output → Step 2 (validate) → Router → Step 3 (auto-fix) → Step 4 (export)
                                   ↓
                              [if STRUCTURAL → Step 1 teacher fix]
                              [if PEDAGOGICAL → M5 redo]
```

---

## Bug Fixes (2026-01-16)

| Bug | Status |
|-----|--------|
| markdownify strip/convert conflict | ✅ Fixed |
| Duplicate folder creation | ✅ Fixed |
| log_event() argument error | ✅ Fixed |

---

## Phase 6: MarkItDown MCP Integration 🔶 NEXT

**Description:** Microsoft's official MCP server for file conversion (29+ formats → Markdown)

**Decision (2026-01-21):** Using MarkItDown MCP instead of custom `course-extractor-mcp`.
- ✅ Officially maintained by Microsoft
- ✅ 29+ formats (not just PDF)
- ✅ MIT licence (no AGPL complication)
- ✅ Production-ready

### Supported Formats
| Category | Formats |
|----------|---------|
| Office | PDF, DOCX, PPTX, XLSX |
| Media | JPG, PNG, MP3, WAV (with OCR/transcription) |
| Web | HTML, RSS, Wikipedia |
| Data | CSV, JSON, XML, ZIP |
| Publishing | EPUB, Jupyter notebooks |

### Roadmap

| Task | Status | Date |
|------|--------|------|
| Documentation complete | ✅ Complete | 2026-01-20 |
| Decision: Use MarkItDown (not custom MCP) | ✅ Complete | 2026-01-21 |
| Installation (~30-45 min) | ⬜ Next | - |
| Test with course materials (PDF) | ⬜ Planned | - |
| Configure for QuestionForge workflow | ⬜ Planned | - |

### Installation Methods
1. **Standard Python** (simplest) - uv + virtual environment
2. **Docker** (safest) - isolated execution with read-only mounts

### Security Requirements
- `:ro` (read-only) volume mounts mandatory
- Limit folder access to specific directories
- Localhost binding only (`127.0.0.1`)
- Disable plugins if uncertain

### Resources
- GitHub: https://github.com/microsoft/markitdown
- MCP Package: https://github.com/microsoft/markitdown/tree/main/packages/markitdown-mcp
- Complete installation guide: [Microsoft MarkItDown MCP](https://github.com/microsoft/markitdown)

### Deprecated: course-extractor-mcp
- Moved to separate repo (AGPL isolation)
- **Status:** Archived - use MarkItDown instead
- **Reason:** Microsoft's solution is better maintained and has more formats

---

## Priority Order

1. ~~**qf-scaffolding logging** - TypeScript logger per RFC-001~~ ✅ Complete
2. ~~**RFC-004 Phase 2** - M1 progressive saving tools~~ ✅ Complete
3. ~~**RFC-007** - LLM Workflow Control Patterns + Option A~~ ✅ Complete
4. ~~**RFC-012** - Pipeline-Script Alignment~~ ✅ Complete (2026-01-28)
5. ~~**RFC-013 v2.5** - Step 1 Vision A refactor~~ ✅ Complete (2026-01-28)
6. **MarkItDown MCP** - Installation and configuration ⬅️ **NEXT**
7. **Test M1 with MarkItDown** - End-to-end test with PDF extraction
8. **M2-M4 Tools** - Implement tools for other modules
9. **RFC-001 TIER 3** - user_decision logging (after M1-M4 run)
10. **RFC-014** - Resource handling (images, audio, coordinates) - LOW PRIORITY

---

## Technical Debt / Future Improvements

### RFC-XXX: qti-core Refactoring ⬜ Planned

**Description:** Clean up internal structure in `packages/qti-core/`

**Background:**
- qti-core is originally `QTI-Generator-for-Inspera` (standalone project)
- Imported to QuestionForge as local package (ADR-008)
- Works excellently but has messy internal structure
- Much work has been done on validation and QTI generation - MUST NOT be lost!

**Current structure (messy):**
```
qti-core/
├── validate_mqg_format.py   ← Loose in root
├── main.py                   ← Loose in root
├── src/parser/               ← Organised
├── src/generators/           ← Organised
└── scripts/                  ← CLI tools
```

**Proposed (cleaned up):**
```
qti-core/
└── src/
    ├── parser/          # MarkdownQuizParser (exists)
    ├── validator/       # Move validate_mqg_format.py here
    ├── generator/       # QTI XML generation (exists)
    └── packager/        # ZIP packaging
```

**Requirements:**
- [ ] Create RFC with migration plan
- [ ] No functionality may be lost
- [ ] Wrappers in qf-pipeline must be updated
- [ ] All tests must pass after move
- [ ] Document new import paths

**Priority:** Low (works now, clean up later)
**Estimate:** 2-4 hours

---

## Related Documents

| Document | Description |
|----------|-------------|
| `WORKFLOW.md` | Complete workflow diagram |
| `CHANGELOG.md` | Detailed changelog |
| `docs/rfcs/RFC-001-unified-logging.md` | Unified Logging RFC |
| `docs/rfcs/RFC-004-m1-methodology-tools.md` | M1 Tools RFC |
| `docs/rfcs/RFC-007-llm-workflow-control-patterns.md` | LLM Workflow Control |
| `docs/rfcs/RFC-009-m3-conversation-capture.md` | M3 Conversation Capture |
| `docs/rfcs/rfc-012-pipeline-script-alignment.md` | Pipeline-Script Alignment (RESOLVED) |
| `docs/rfcs/RFC-013-Questionforge pipeline architecture v2.md` | Pipeline architecture v2.5 |
| `docs/rfcs/RFC-014-resource-handling.md` | Resource Handling (DRAFT) |
| `docs/rfcs/RFC-016-m5-self-learning-format-recognition.md` | **NEW** M5 Self-Learning Format (COMPLETE) |
| `docs/workflows/m1_complete_workflow.md` | M1 Workflow (v3.1) |
| `methodology/m1/m1_0_stage0_material_analysis.md` | **NEW** Teacher Guide for Stage 0 |
| `docs/acdm/` | ACDM session logs and reflections |
| `docs/adr/ADR-010-step3-decision-architecture.md` | Step 3 architecture |
| `docs/adr/ADR-011-question-set-builder.md` | Question Set spec |
| `docs/adr/ADR-014-shared-session.md` | Shared Session architecture |
| `docs/specs/STEP1_REBUILD_INTERACTIVE.md` | Step 1 spec |
| `docs/DISCOVERY_BRIEF.md` | Original vision |
| [Microsoft MarkItDown MCP](https://github.com/microsoft/markitdown) | **NEW** MarkItDown MCP installation guide |

---

*Roadmap updated 2026-02-04 (Translated to British English)*
