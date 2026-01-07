# Changelog

All notable changes to QuestionForge will be documented in this file.

## [Unreleased]

### Added - 2026-01-07

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
├── docs/
│   ├── DISCOVERY_BRIEF.md       ✅ Complete
│   ├── adr/
│   │   ├── ADR-001-two-mcp-architecture.md    ✅
│   │   ├── ADR-002-module-naming.md           ✅
│   │   ├── ADR-003-language-choices.md        ✅
│   │   ├── ADR-004-m2-m3-merge.md             ✅
│   │   └── ADR-005-mcp-integration.md         ✅
│   ├── specs/
│   │   ├── qf-scaffolding-spec.md             ✅
│   │   ├── qf-pipeline-spec.md                ✅
│   │   └── qf-specifications-structure.md     ✅
│   ├── chat_claude_desctop/
│   │   └── Restructuring...2026-01-02.md      ✅
│   ├── instructions/                          ⬜ Empty
│   └── rfcs/                                  ⬜ Empty
├── packages/
│   ├── qf-scaffolding/                        ⬜ To be built
│   └── qf-pipeline/                           ⬜ To be built
└── qf-specifications/                         ⬜ To be created
```

### ACDM Progress

| Phase | Status | Outputs |
|-------|--------|---------|
| DISCOVER | ✅ Complete | DISCOVERY_BRIEF.md |
| SHAPE | ✅ Complete | Architecture in brief |
| DECIDE | ✅ Complete | 5 ADRs |
| COORDINATE | ✅ Complete | 3 specs |
| EXPLORE | ⬜ Next | - |
| PLAN | ⬜ Pending | - |
| CODE | ⬜ Pending | - |
| COMMIT | ⬜ Pending | - |

---

## Future

### Planned
- Create qf-specifications/ folder structure
- Migrate Field Requirements v6.3 to v7
- Build qf-scaffolding MCP (TypeScript)
- Build qf-pipeline MCP (Python)
- Implement Step 1.5 (MCP integration)
- Archive legacy MCPs

---

*QuestionForge - Forging Quality Questions*
