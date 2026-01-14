# Changelog

All notable changes to QuestionForge will be documented in this file.

## [Unreleased]

### Added - 2026-01-14

#### Shared Session: 4 Entry Points (ADR-014)
- **Feature:** Flexible entry points for different starting contexts
  - **A (materials):** Start from instructional materials → M1 (qf-scaffolding)
  - **B (objectives):** Start from learning objectives → M2 (qf-scaffolding)
  - **C (blueprint):** Start from assessment plan → M3 (qf-scaffolding)
  - **D (questions):** Direct pipeline (validate/export) [default]
- **Enhancement:** `source_file` now Optional (only required for B/C/D)
- **Enhancement:** New project folders: `00_materials/`, `methodology/`
- **Enhancement:** Auto-generated README in `00_materials/`
- **Enhancement:** `methodology` section in session.yaml for M1-M4 tracking
- **Enhancement:** `step0_start` returns routing guidance based on entry_point
- **Enhancement:** `init` tool now returns full A/B/C/D routing guide
- **Validation:** `validate_entry_point()` ensures correct source_file requirements
- **Docs:** ADR-014-shared-session.md, HANDOFF_FIXES_shared_session.md

### Added - 2026-01-08

#### Step 2: Validation Complete Signal
- **Bug fix:** Step 2 now logs `step2_complete` when validation passes for the first time
- **Enhancement:** Added "NEXT STEP" section in validation output with clear instructions
- **Enhancement:** Added "STOP: Do not run step2_validate again" message when file is ready
- Prevents Claude from running validation repeatedly after file is valid

#### Step 1: Interactive Guided Build (Rebuild)
- **Feature:** Rebuilt Step 1 to be interactive with teacher involvement
- **New tools:**
  - `step1_fix_auto` - Apply only auto-fixable transforms, return remaining issues
  - `step1_fix_manual` - Apply single manual fix from user input
  - `step1_suggest` - Generate suggestions for fields based on context
  - `step1_batch_preview` - Show all questions with same type of issue
  - `step1_batch_apply` - Apply same fix to multiple questions at once
  - `step1_skip` - Skip an issue or entire question
- **Enhancement:** `step1_analyze` now returns categorized issues (auto_fixable, needs_input, other)
- **Enhancement:** Step 1 now uses Step 0 session automatically (no need to re-enter paths)
- **Enhancement:** Added logging for all Step 1 actions to pipeline.jsonl/pipeline.log
- **Legacy:** Marked `step1_transform` as [LEGACY] - kept for backwards compatibility
- **Spec:** Created `docs/specs/STEP1_REBUILD_INSTRUCTIONS.md`

### Added - 2026-01-07

#### ACDM Documentation Structure
- **Feature:** Created `docs/acdm/` folder for structured ACDM logging
- **Structure:**
  - `docs/acdm/README.md` - Explains documentation structure
  - `docs/acdm/logs/` - Chronological session logs (YYYY-MM-DD_PHASE_topic.md)
  - `docs/acdm/meta/` - ACDM process reflections
- **Logs created:**
  - `2026-01-06_DISCOVER_Terminal_vs_qf-pipeline.md`
  - `2026-01-06_DISCOVER_qf-pipeline_wrapper_analysis.md`
  - `2026-01-06_DISCOVER_consolidated_analysis.md`
  - `2026-01-06_DISCOVER_detailed_comparison.md`
  - `2026-01-07_DISCOVER_MQG_vs_qfpipeline_analysis.md`
  - `2026-01-07_DISCOVER_input_format_inventory.md`
  - `2026-01-07_DISCOVER_step1_documentation_analysis.md`
  - `2026-01-07_DISCOVER_v63_vs_v65_comparison.md`

#### qti-core: Local package (standalone)
- Copied QTI-Generator-for-Inspera as `packages/qti-core/`
- 114 files (excluding .git, .venv, __pycache__, output)
- Updated wrapper path from absolute to relative
- QuestionForge is now fully standalone

#### Tags to Labels Export
- **Feature:** `^tags` now exported as labels in Inspera
- Added `^tags` parsing in markdown_parser.py (maps to `labels` if no `^labels` field)
- Fixed metadata flow: questions now passed to packager for label generation
- Labels appear in imsmanifest.xml as `<imsmd:taxon>` entries

#### Validator: Accept ^tags as alternative to ^labels
- **Feature:** Validator (Step 2) now accepts `^tags` as valid alternative to `^labels`
- Teachers can use either `^tags` or `^labels` in markdown - both pass validation
- Aligns validation rules with export behavior (tags → labels mapping)

### Fixed - 2026-01-07

#### qf-pipeline: Validation Output Improvement (ADR-012)
- **BUG FIX:** Fixed case mismatch bug where error count was always 0 (`"error"` → `"ERROR"`)
- **Enhancement:** Added `format_validation_output()` function with Terminal-style output
- **Enhancement:** Errors now grouped by question with question ID
- **Enhancement:** Added summary section with Total/Valid/Errors/Warnings counts
- **Enhancement:** Clear status message: "READY" or "NOT READY"
- **Feature:** Validation report saved to `validation_report.txt` in session folder

### Added - 2026-01-02

#### ACDM DISCOVER Phase
- Created `docs/DISCOVERY_BRIEF.md` - comprehensive problem analysis
- Analyzed fragmented MQG ecosystem (5 overlapping tools)
- Identified pain points: duplication, unclear workflow, BB naming
- Documented current state and migration path

#### ACDM SHAPE Phase
- Designed Two-MCP architecture (qf-scaffolding + qf-pipeline)
- Renamed Building Blocks to Modules (BB → M1-M4)
- Merged BB2+BB3 into M2 (Assessment Planning)
- Defined MCP integration pattern (Step 1.5)

#### ACDM DECIDE Phase
- Created `docs/adr/ADR-001-two-mcp-architecture.md`
- Created `docs/adr/ADR-002-module-naming.md`
- Created `docs/adr/ADR-003-language-choices.md`
- Created `docs/adr/ADR-004-m2-m3-merge.md`
- Created `docs/adr/ADR-005-mcp-integration.md`

#### ACDM COORDINATE Phase
- Created `docs/specs/qf-scaffolding-spec.md` - MCP 1 specification
- Created `docs/specs/qf-pipeline-spec.md` - MCP 2 specification
- Created `docs/specs/qf-specifications-structure.md` - shared specs structure

#### Documentation
- Updated `CLAUDE.md` with project overview
- Saved full dialogue to `docs/chat_claude_desctop/`
- Linked DISCOVERY_BRIEF to source dialogue

### Project Structure

```
QuestionForge/
├── CLAUDE.md                    ✅ Updated
├── CHANGELOG.md                 ✅ Updated
├── ROADMAP.md                   ✅ Updated
├── docs/
│   ├── DISCOVERY_BRIEF.md       ✅ Complete
│   ├── acdm/                    ✅ ACDM documentation
│   │   ├── README.md            ✅ Structure guide
│   │   ├── logs/                ✅ 8 session logs
│   │   └── meta/                ✅ Process reflections
│   ├── adr/                     ✅ 12 ADRs
│   │   ├── ADR-001 to ADR-005   ✅ Architecture
│   │   ├── ADR-006 to ADR-009   ✅ Session/Resources
│   │   └── ADR-010 to ADR-012   ✅ Step 3/Validation
│   ├── specs/                   ✅ Implementation specs
│   ├── analysis/                ✅ Technical analyses
│   └── chat_claude_desctop/     ✅ Saved dialogues
├── packages/
│   ├── qf-scaffolding/          ⬜ To be built
│   ├── qf-pipeline/             ✅ MCP server active
│   └── qti-core/                ✅ Standalone QTI logic
└── qf-specifications/           ⬜ To be created
```

### ACDM Progress

| Phase | Status | Outputs |
|-------|--------|---------|
| DISCOVER | ✅ Complete | DISCOVERY_BRIEF.md, docs/acdm/logs/ |
| SHAPE | ✅ Complete | Architecture in brief |
| DECIDE | ✅ Complete | 12 ADRs |
| COORDINATE | ✅ Complete | specs/ |
| IMPLEMENT | ✅ Active | qf-pipeline, qti-core |

---

## Future

### Planned
- Step 3: Decision tool (simple export vs Question Set)
- qf-scaffolding MCP (TypeScript, M1-M4)
- Create qf-specifications/ shared folder
- Archive legacy MCPs

---

*QuestionForge - Forging Quality Questions*
