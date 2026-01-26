# Changelog

All notable changes to QuestionForge will be documented in this file.

## [Unreleased]

### Added - 2026-01-26

#### Step 0: Auto-register materials in sources.yaml
- **Enhancement:** Step 0 now automatically registers all copied materials in sources.yaml
- **Materials registration:**
  - All files copied to `materials/` are registered with type detection (pdf→lecture_slides, etc.)
  - Reference documents (kursplan for m1) registered as type "syllabus"
  - Questions files (for m2/m3/m4 entry points) registered as type "questions"
- **Metadata tracked:**
  - `path`: relative path in project
  - `type`: auto-detected from file extension
  - `location`: "local" or "fetched"
  - `original_path`: where file came from
  - `copied_at`: timestamp
- **Files modified:**
  - `packages/qf-pipeline/src/qf_pipeline/utils/session_manager.py`

### Changed - 2026-01-25

#### RFC-013: Pipeline Architecture v2.1 + Updated Folder Structure
- **New folder structure** for cleaner data flow:
  ```
  project/
  ├── materials/       ← Input (lectures, slides)
  ├── methodology/     ← Method guides (copied in Step 0)
  ├── preparation/     ← M1 + M2 output (foundation for questions)
  ├── questions/       ← M3 creates, M4/M5 edit + history/
  ├── pipeline/        ← Step 1-3 working area + history/
  ├── output/qti/      ← Step 4 final output
  └── logs/
  ```
- **Key decisions documented:**
  - Question IDs sufficient for tracking (removed line numbering)
  - M5 generates structurally correct output
  - Step 1 is safety net for unexpected issues
  - Separate pattern databases for Step 1 and Step 3
- **Files modified:**
  - `WORKFLOW.md` - Updated folder structure and data flow (v1.2)
  - `docs/rfcs/RFC-013-Questionforge pipeline architecture v2.md` - Complete architecture
  - `docs/rfcs/RFC-013-updates-for-desktop.md` - 10 implementation decisions
- **RFC:** `docs/rfcs/RFC-013-Questionforge pipeline architecture v2.md`

### Fixed - 2026-01-25

#### Extended Validator: Question-Type-Specific Validation
- **Enhancement:** Validator now checks question-type-specific fields
  - Previously: Only checked `^type`, `^identifier`, `^points` (basic structure)
  - Now: Also validates content fields required by each question type
- **Question types validated:**
  - `text_entry`: requires `blanks` with `@@field` format
  - `inline_choice`: requires `dropdown_N` fields with `*` markers
  - `multiple_choice_single`: requires `options` and `answer`
  - `multiple_response`: requires `options` and `correct_answers`
  - `true_false`: requires `answer`
  - `match`: requires `pairs`
  - `hotspot`: requires `image` and `hotspots`
  - `graphicgapmatch_v2`: requires `image` and `drop_zones`
- **Guarantee:** validate() OK → export GUARANTEED to work
- **Files modified:**
  - `packages/qti-core/src/parser/markdown_parser.py` - added `_validate_question_type_fields()`

#### Parser Consistency Fix (RFC-012 Appendix)
- **Critical Bug Fixed:** Validation passed but export found 0 questions
  - `validate_mqg_format.py` used flexible regex: `\^type:?\s+(\S+)` (accepts colons)
  - `markdown_parser.py` used strict regex: `^\^type\s+(.+)` (no colons, start of line)
  - Result: Files validated OK but failed to export
- **Root Cause:** Two parsers with different rules - architectural violation
- **Solution:** Single Source of Truth architecture
  - Added `validate()` method to `markdown_parser.py` (~100 lines)
  - Simplified `validate_mqg_format.py` from 554 to 185 lines (thin wrapper)
  - Now calls `parser.validate()` instead of own parsing logic
- **Guarantee:** Validate pass → Export works (same parser, same rules)
- **Files modified:**
  - `packages/qti-core/src/parser/markdown_parser.py` - added validate() method
  - `packages/qti-core/validate_mqg_format.py` - simplified to thin wrapper
- **Verification:**
  - v1 file (with colons): Validate FAIL → Export FAIL (consistent)
  - v2 file (correct format): Validate PASS → Export PASS (consistent)
- **RFC:** `docs/rfcs/rfc-012-pipeline-script-alignment.md` (Appendix A)

### Fixed - 2026-01-24

#### RFC-012 Phase 1: Subprocess Implementation (Critical Bug Fix)
- **Critical Bug Fixed:** `apply_resource_mapping()` was missing in MCP pipeline
  - Images copied correctly (e.g., `resources/Q001_image.png`)
  - But XML referenced OLD paths (e.g., `image.png`)
  - Result: Broken images in Inspera import
- **Solution:** MCP now calls qti-core scripts via subprocess
  - `handle_step2_validate()` → calls `step1_validate.py`
  - `handle_step4_export()` → calls all 5 scripts sequentially
  - Scripts are now single source of truth (terminal + MCP identical)
- **Key Detail:** Added explicit `--quiz-dir` for step3/4/5
  - Scripts auto-detect only works in `qti-core/output/`
  - MCP outputs to project's `03_output/` - requires explicit path
- **Files modified:**
  - `packages/qf-pipeline/src/qf_pipeline/server.py` - subprocess implementation
- **Verification:**
  - Created image test proving scripts fix the bug
  - XML contains `resources/IMG_TEST_Q001_test_image.png` (correct path)
- **RFC:** `docs/rfcs/rfc-012-pipeline-script-alignment.md` (Phase 1 complete)
- **Handoff:** `docs/handoffs/2026-01-24_rfc012_subprocess_implementation_COMPLETE.md`

### Fixed - 2026-01-22

#### qf-pipeline: Claude Desktop PYTHONPATH Configuration
- **Bug:** MCP server couldn't find qti-core modules
  - `step2_validate` and `step4_export` failed with import errors
  - Parser found 0 questions despite file having valid content
- **Cause:** PYTHONPATH in `claude_desktop_config.json` pointed to old location
  - Old: `/Users/niklaskarlsson/QTI-Generator-for-Inspera`
  - New: `.../QuestionForge/packages/qti-core`
- **Fix:** Updated PYTHONPATH in Claude Desktop config
- **Files modified:**
  - `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Action required:** Restart Claude Desktop to apply

### Added - 2026-01-22

#### RFC-012: Pipeline-Script Alignment (Critical Bug Discovery)
- **Discovery:** Deep analysis of WORKFLOW.md Appendix A.1.2 revealed pipeline divergence
- **Critical Bug:** `apply_resource_mapping()` missing in step4_export
  - Pipeline copies resources correctly (e.g., `Q001_image.png`)
  - But XML references OLD paths (e.g., `image.png`) instead of new paths
  - Result: Broken images in Inspera import
- **Root Cause:** Wrappers reimplemented logic instead of reusing scripts
  - cli.py has ~45 lines of path mapping code (lines 425-471)
  - server.py has 0 lines - completely forgotten!
- **Solution:** Hybrid approach
  - Phase 1 (NOW): Subprocess - call scripts directly
  - Phase 2 (LATER): Refactor scripts to be importable
- **RFC:** `docs/rfcs/rfc-012-pipeline-script-alignment.md`

#### WORKFLOW.md Appendix A: QTI Export Technical Details
- Added complete technical documentation of export pipeline
- A.1: Manual scripts overview (5 steps)
- A.1.2: Step-by-step comparison table (verified)
- A.1.3: Detailed script descriptions
- A.2: MCP Pipeline flow
- A.3: Module responsibilities diagram
- A.4: Expected input format (v6.5)
- A.5: Validator vs Parser mismatch warning
- A.6: Troubleshooting guide
- A.7: Manual testing commands

#### Roadmap: qti-core Refactoring (Future RFC)
- **Added:** "Teknisk Skuld / Framtida Förbättringar" section to ROADMAP.md
- **RFC-XXX:** Plan for cleaning up qti-core internal structure
  - Currently: Files loose in root (`validate_mqg_format.py`, `main.py`)
  - Proposed: Organized under `src/` (validator/, parser/, generator/, packager/)
- **Priority:** Low (works now, clean up later)
- **Note:** All existing functionality must be preserved

### Fixed - 2026-01-21

#### qf-pipeline: step1_start accepts all file formats (Bug Fix)
- **Bug:** `step1_start` rejected files as "semi-structured" instead of trying to fix them
  - Claude Desktop went into loops trying workarounds
  - Files from M3 were incorrectly classified and rejected
- **Fix:** `step1_start` now accepts ALL file formats
  - Warns about format issues but proceeds with parsing
  - Counts severe issues and recommends M1-M4 if too many
  - No longer blocks on SEMI_STRUCTURED or UNSTRUCTURED formats
- **Files modified:**
  - `packages/qf-pipeline/src/qf_pipeline/tools/step1_tools.py`

### Added - 2026-01-21

#### qf-scaffolding: General Project File Tools (Bug Fix)
- **Bug:** Claude Desktop couldn't read files outside `00_materials/` or `00_reference/`
- **New Tool:** `read_project_file` - Read any file within project directory
  - Example: `read_project_file(project_path="...", relative_path="05/questions.md")`
  - Security: Path traversal protection (can't read outside project)
- **New Tool:** `write_project_file` - Write any file within project directory
  - Creates parent directories automatically
  - Overwrite protection option
- **Files added:**
  - `packages/qf-scaffolding/src/tools/project_files.ts` (240 lines)

#### qf-pipeline: General Project File Tools (Python)
- **Mirror of TypeScript tools:** Same functionality as qf-scaffolding version
- **Purpose:** Both MCPs can now read/write files anywhere in project
- **New Tool:** `read_project_file` - Read any file within project directory
- **New Tool:** `write_project_file` - Write any file within project directory
- **Files added:**
  - `packages/qf-pipeline/src/qf_pipeline/tools/project_files.py` (190 lines)
- **Files modified:**
  - `packages/qf-pipeline/src/qf_pipeline/server.py` - registered new tools
  - `packages/qf-pipeline/src/qf_pipeline/tools/__init__.py` - exported new tools

#### qf-scaffolding: New `write_m1_stage` Tool
- **New Tool:** `write_m1_stage` - Direct file writing for M1 stages
- **Principle:** "What Claude writes = what gets saved" (no transformation)
- **Features:**
  - Separate files per stage: `m1_stage0_materials.md` through `m1_stage5_objectives.md`
  - Auto-updates `m1_progress.yaml` for progress tracking
  - Safety: Won't overwrite existing files without explicit `overwrite=true`
- **Branch:** `feature/m1-direct-file-writing`
- **Files added:**
  - `packages/qf-scaffolding/src/tools/write_m1_stage.ts` (260 lines)
- **Files modified:**
  - `packages/qf-scaffolding/src/index.ts` - registered new tool

#### RFC-009: M3 Conversation Capture (Draft)
- **New RFC:** `docs/rfcs/RFC-009-m3-conversation-capture.md`
- **Problem:** M3 (Question Generation) needs different saving pattern than M1/M2
  - M1/M2: Stage-based → save complete document at once
  - M3: Iterative conversation → accumulate questions incrementally
- **Proposed Solution:** `append_m3_question` tool for incremental question saving
- **Status:** Draft - design phase

### Changed - 2026-01-21

#### qf-scaffolding: Simplified save_m1_progress Tool
- **Breaking Change:** `save_m1_progress` MaterialDataSchema simplified
  - **Before:** Complex schema with `summary`, `key_topics`, `tier_classification`, `emphasis_patterns`, `instructional_examples`, `potential_misconceptions`
  - **After:** Simple schema with just `filename` + `content` (raw markdown)
- **Reason:** What Claude presents = what gets saved (no transformation)
- **Benefit:** Eliminates mismatch between presentation and saved content
- **Updated:** M1 Stage 0 methodology with explicit save format instructions
- **Updated:** Tool hints in `load_stage.ts` to show correct format

#### Decision: Use MarkItDown MCP (Microsoft) for PDF Extraction
- **Decision:** Use Microsoft's MarkItDown MCP instead of custom `course-extractor-mcp`
- **Reasons:**
  - Officially maintained by Microsoft
  - 29+ formats (not just PDF)
  - MIT license (no AGPL complications)
  - Production-ready
- **Impact:**
  - `course-extractor-mcp` → Archived (moved to separate repo)
  - RFC-008 → Superseded by MarkItDown approach
- **Next:** Install MarkItDown MCP following `docs/guides/markitdown-mcp-installation.md`

### Added - 2026-01-20

#### course-extractor-mcp: PDF Extraction MCP Server (NEW)
- **Package:** Created `packages/course-extractor-mcp/` - Minimal MCP for PDF extraction
- **Features:**
  - Extracts text and images from PDF course materials
  - Uses pymupdf4llm for high-quality extraction
  - Production-ready security (timeout, path whitelist, encryption check)
  - Swedish error messages
- **Platform:** Unix-only (macOS/Linux) due to `signal.SIGALRM` timeout
- **License:** AGPL 3.0 (due to PyMuPDF dependency)
- **Tests:** 5/6 tests passing (1 skipped - needs sample.pdf)
- **Code Reviews:** 2 complete reviews, 13 issues fixed
- **RFCs:** RFC-001-CourseExtractor-MCP v4.0-v4.2 (iterative refinement)
- **Files:**
  - `packages/course-extractor-mcp/server.py` (~200 lines)
  - `packages/course-extractor-mcp/tests/test_pdf.py`
  - `docs/rfcs/RFC-001-CourseExtractor-MCP-v4.2-FINAL.md`
  - `docs/handoffs/IMPLEMENT_CourseExtractor_MCP_v4.2_FINAL.md`

#### MarkItDown MCP: Roadmap Documentation
- **Docs:** Added MarkItDown MCP integration to roadmap (Fas 6)
- **Guide:** Created `docs/guides/markitdown-mcp-installation.md` (600+ lines)
  - Complete installation guide for Microsoft's MarkItDown MCP
  - Security best practices (read-only mounts, localhost binding)
  - Troubleshooting section
- **Timeline:** Q1-Q4 2026 (future backup/comparison solution)
- **Purpose:** Alternative/complement to course-extractor-mcp for 29+ formats

### Added - 2026-01-19

#### RFC-004 Phase 2: Progressive Saving for M1
- **New Tool:** `save_m1_progress` - Progressive saving for all M1 stages
  - `add_material` action: Save after each PDF during Stage 0
  - `save_stage` action: Save completed stage output (Stage 0-5)
  - `finalize_m1` action: Mark M1 complete, ready for M2
  - All saves go to single document: `01_methodology/m1_analysis.md`
- **Updated Tool:** `read_materials` - Two modes for controlled reading
  - List mode (`filename=null`): Returns file metadata without content
  - Read mode (`filename="X.pdf"`): Returns content of ONE specific file
  - Enables progressive analysis without loading all materials at once
- **Updated Tool:** `load_stage` - Fixed M1 stage numbering
  - `stage=0` now loads Material Analysis (60-90 min, the long stage)
  - `stage=1-5` load Validation through Learning Objectives
  - Removed Introduction stage (was stage=0, now integrated)
  - M1 now has 6 stages (0-5) instead of 8
- **Key Decisions (RFC-004):**
  - Single document strategy: All M1 stages save to one `m1_analysis.md`
  - Progressive saving during Stage 0 (after each PDF analyzed)
  - Stage-completion saves for dialogue stages (1-5)
- **Files added:**
  - `packages/qf-scaffolding/src/tools/save_m1_progress.ts` (324 lines)
- **Files modified:**
  - `packages/qf-scaffolding/src/tools/read_materials.ts` - filename param
  - `packages/qf-scaffolding/src/tools/load_stage.ts` - stage mapping fix
  - `packages/qf-scaffolding/src/index.ts` - registered new tool
  - `packages/qf-scaffolding/package.json` - added yaml dependency
- **Documentation:**
  - `docs/rfcs/RFC-004-m1-methodology-tools.md` - Phase 2 design complete
  - `docs/workflows/m1_complete_workflow.md` - Rewritten (v3.0) for single-doc
- **Tests:** All 190 tests pass, TypeScript build clean

### Added - 2026-01-17 (Night)

#### Tool Hints in load_stage Response
- **Feature:** `load_stage` now includes tool hints in response
  - Shows which MCP tools to use for each stage
  - M1 Stage 1 shows: `read_materials`, `read_reference`, `complete_stage`
  - Dialogue stages show relevant `complete_stage` with output type
- **New functions:**
  - `getToolHintsForStage(module, stage)` - Returns tool hints array
  - `formatToolHints(hints)` - Formats hints as markdown
- **Impact:** Claude knows which tools to call without modifying methodology files

#### RFC-004 Phase 1: Core Read Tools for M1
- **New Tool:** `read_materials` - Read instructional materials from `00_materials/`
  - Supports PDF text extraction via `pdf-parse` library
  - Supports markdown and text files
  - Pattern filtering (e.g., `*.pdf`, `lecture*`)
  - Returns content within MCP response (no file copying)
  - RFC-001 compliant logging
- **New Tool:** `read_reference` - Read reference documents from project root
  - Reads kursplan, grading criteria, etc.
  - Includes source URL metadata if originally fetched from URL
- **Files added:**
  - `packages/qf-scaffolding/src/tools/read_materials.ts`
  - `packages/qf-scaffolding/src/tools/read_reference.ts`
- **Files modified:**
  - `packages/qf-scaffolding/src/index.ts` - Registered new tools
  - `packages/qf-scaffolding/package.json` - Added pdf-parse dependency
- **Tests:** All 190 tests pass, TypeScript build clean
- **RFC:** Phase 1 of RFC-004 complete

### Fixed - 2026-01-17 (Night)

#### RFC-004 Phase 0: load_stage Now Reads from Project Methodology
- **Critical Bug Fixed:** `load_stage` was reading methodology files from QuestionForge source instead of project's `methodology/` folder
- **Root Cause:** `project_path` parameter was only used for logging, not for file path resolution
- **Fix:** Now reads from `project_path/methodology/{module}/` when `project_path` is provided
- **Fallback:** If project methodology not found, falls back to QuestionForge source with warning log
- **Impact:** Projects are now truly self-contained (can be moved/copied, methodology edits respected)
- **Files modified:**
  - `packages/qf-scaffolding/src/tools/load_stage.ts` - Path resolution fix with fallback logic
- **Tests:** All 136 tests pass, TypeScript build clean
- **RFC:** Documented in RFC-004 as Phase 0 (critical blocker)

### Added - 2026-01-17 (Afternoon)

#### RFC-001: TIER 1-2 Logging Implementation
- **TIER 1 (Tool Logging):** tool_start, tool_end, tool_error events
  - Python: `step1_analyze()`, `step1_fix_auto()`, `step1_fix_manual()`, `step2_validate()`, `step4_export()`
  - TypeScript: `load_stage()` with duration tracking
  - All errors include stacktrace + context
- **TIER 2 (Session Resumption):** milestone events for workflow tracking
  - `session_start` - logged when new session created
  - `session_resume` - logged when existing session loaded (step0_start with project_path)
  - `session_end` - logged when session explicitly ended (SessionManager.end_session)
  - `stage_start/complete` - logged in load_stage.ts and completeStage()
  - `validation_complete` - logged when step2_validate passes
  - `export_complete` - logged when step4_export succeeds
- **Status:** RFC-001 TIER 1-2 fully complete
- **Files modified:**
  - `packages/qf-pipeline/src/qf_pipeline/server.py`
  - `packages/qf-pipeline/src/qf_pipeline/utils/session_manager.py`
  - `packages/qf-scaffolding/src/tools/load_stage.ts`
  - `packages/qf-scaffolding/src/utils/logger.ts`

### Added - 2026-01-17

#### qf-scaffolding: TypeScript Logger (RFC-001 Phase 2)
- **Feature:** Created RFC-001 compliant logger in `packages/qf-scaffolding/src/utils/logger.ts`
  - Same schema as Python logger (v:1, ts, session_id, mcp, tool, event, level, data)
  - Synchronous writes to `logs/session.jsonl`
  - Auto-reads session_id from `session.yaml`
- **Functions:** `logEvent()`, `logAction()`, `logStageEvent()`, `logUserDecision()`, `logError()`, `getSessionState()`
- **Integration:** Updated `load_stage.ts` with optional `project_path` parameter
  - Logs `stage_start` events when project_path provided
  - Exposed `project_path` in MCP tool schema
- **Status:** RFC-001 Phase 2 marked complete

#### RFC-001: Unified Logging - IMPLEMENTED
- **Status:** RFC-001 markerad som Implemented (alla faser klara)
- **Removed:** Phase 3 (Migration) - behövs inte för nya projekt
- **Final structure:** 3 faser (Python Logger, TypeScript Logger, Schema Validation)

#### RFC-002: QFMD Naming - IMPLEMENTED
- **Renamed:** FormatLevel enum values in `detector.py`
  - `VALID_V65` → `QFMD`
  - `OLD_SYNTAX_V63` → `LEGACY_SYNTAX`
  - `RAW` → `UNSTRUCTURED`
- **Updated:** All references in step1 module (detector, analyzer, transformer, parser, tools)
- **Updated:** User-facing messages to use QFMD terminology
- **Updated:** Specs (INDEX.md, multiple_choice_single.yaml)
- **Updated:** step1_guided_build_spec.md documentation
- **Zero** v6.3/v6.5 references in source code after implementation

### Added - 2026-01-16 (Evening)

#### RFC-001: Unified Logging
- **RFC:** Created `docs/rfcs/RFC-001-unified-logging.md`
  - Single log file per project: `logs/session.jsonl`
  - Standardized JSON schema with version field
  - Supports: qf-pipeline, qf-scaffolding, qti-core
  - Deep error logging (stacktrace + context + state)
  - User decision logging for ML training
  - PostgreSQL-ready schema for future migration
- **Schema:** Created `qf-specifications/logging/schema.json`
  - JSON Schema draft 2020-12
  - Required fields: ts, v, session_id, mcp, tool, event, level
  - Optional: data, duration_ms, parent_id
- **Documentation:** Created `qf-specifications/logging/events.md`
  - Session events (start, resume, end)
  - Tool events (start, end, progress, error)
  - Module events (stage_start, stage_complete, user_decision)
  - Validation events (file_parsed, question_validated, export_complete)
- **Examples:** Created 4 example files in `qf-specifications/logging/examples/`
  - session_start.json, user_decision.json, validation_complete.json, error_deep.json
- **Verified:** Schema validates, examples pass validation, backward compatible

### Fixed - 2026-01-16 (Evening)

#### qf-pipeline: URL Fetch Bug
- **BUG FIX:** Fixed `markdownify` crash when fetching URLs
  - Error: "You may specify either tags to strip or tags to convert, but not both"
  - Fix: Removed `convert` parameter, kept only `strip` in `html_to_markdown()`
  - File: `packages/qf-pipeline/src/qf_pipeline/utils/url_fetcher.py`

#### qf-pipeline: Duplicate Folder Bug
- **BUG FIX:** Fixed duplicate folder creation when `output_folder` ends with `project_name`
  - Example: `output_folder="Test/MyProject"` + `project_name="MyProject"` → `Test/MyProject/MyProject/`
  - Fix: Check if `output_base.name == project_name`, skip appending if match
  - File: `packages/qf-pipeline/src/qf_pipeline/utils/session_manager.py`

#### qf-pipeline: log_event() Argument Error
- **BUG FIX:** Fixed "multiple values for argument 'project_path'" error
  - Cause: `data` dict passed to `log_action()` contained `project_path` key
  - Fix: Filter out `project_path` from data before unpacking with `**`
  - File: `packages/qf-pipeline/src/qf_pipeline/utils/logger.py`

### Added - 2026-01-16

#### qf-scaffolding: M2-M4 Module Support
- **Feature:** Extended `load_stage` tool to support all 4 modules (was M1 only)
  - M2 (Assessment Design): 9 stages (0-8)
  - M3 (Question Generation): 5 stages (0-4)
  - M4 (Quality Assurance): 6 stages (0-5)
- **Enhancement:** Added `requiresApproval` field to stage info
  - `true` = teacher approval required before continuing
  - `false` = informational/reference material
  - `"conditional"` = auto-proceed if validation passes (M4 Phase 1)
- **Enhancement:** Dynamic validation with `MAX_STAGES` and `getStages()` helpers
- **Enhancement:** Module-specific completion messages (e.g., "M2 komplett! Fortsätt till M3")
- **Enhancement:** Updated tool description and input schema for all modules

#### qf-pipeline: materials_folder Parameter (P1)
- **Feature:** New `materials_folder` parameter for entry point `m1`
  - Automatically copies instructional materials to `00_materials/`
  - Preserves subdirectory structure with `shutil.copytree`
  - Filters junk files (.DS_Store, Thumbs.db, ~$*, hidden files)
- **Validation:** Required for m1, ignored for other entry points
- **Logging:** `materials_copied` count in session logs
- **UX:** No more manual file copying needed for M1 workflow

#### Documentation: Verified Previously Implemented Features
- **Resource handling (ADR-009):** Confirmed already implemented in `server.py`
  - `validate_resources()` checks images exist before export
  - `copy_resources()` copies media to QTI package
  - Return message shows `{resource_count} filer kopierade`
- **list_projects tool (ADR-008):** Confirmed already implemented
  - `utils/config.py` with `list_projects()`, `get_project_files()`
  - Tool definition and handler in `server.py`
  - Lists configured MQG folders with status

### Added - 2026-01-15

#### Sources, Methodology Copy, and Logging Infrastructure
- **sources.yaml:** New shared file for tracking source files
  - Sequential IDs (src001, src002, ...) for readability
  - File locking for thread-safe concurrent writes
  - Updated by both qf-pipeline and qf-scaffolding
  - Tracks: path, type, location, added_by, discovered_in
- **Methodology copy:** `copy_methodology()` copies all 28 files to project
  - Projects become self-contained
  - Copied BEFORE load_stage runs
- **Logging consolidation:** All logs now go to `logs/` folder
  - `logs/session.jsonl` - Shared structured log (both MCPs)
  - `logs/qf-pipeline.jsonl` - MCP-specific log
  - `logs/session.log` - Human-readable format
  - `log_action()` now delegates to `log_event()` (backwards compatible)
  - No more root-level `pipeline.log`/`pipeline.jsonl` duplicates
- **New utils:** `sources.py`, `methodology.py` in qf-pipeline
- **Updated:** `session_manager.py` with `initial_sources` parameter

#### Session Init Design Spec (DRAFT)
- **Spec:** Created `docs/specs/SESSION_INIT_DESIGN.md`
- **Status:** IMPLEMENTED (see above)

### Added - 2026-01-14

#### Methodology Import: M1-M4 Complete
- **Structure:** Created `methodology/` at QuestionForge root (shared by both MCPs)
- **M1 (Material Analysis):** 8 files (m1_0 to m1_7)
  - Moved from `packages/qf-scaffolding/methodology/m1/`
  - Renamed from `bb1a-bb1h` to `m1_0-m1_7` format
- **M2 (Assessment Planning):** 9 files (m2_0 to m2_8) - NEW
  - Imported from MQG_0.2 `bb2a-bb2i`
  - Covers: objectives, strategy, Bloom's, question types, difficulty, blueprint
- **M3 (Question Generation):** 5 files (m3_0 to m3_4) - NEW
  - Imported from MQG_0.2 `bb4a-bb4e`
  - Covers: generation principles, distribution review, finalization
- **M4 (Quality Assurance):** 6 files (m4_0 to m4_5) - NEW
  - Imported from MQG_0.2 `bb5a-bb5f`
  - Covers: automated validation, pedagogical review, documentation
- **Skipped:** bb3 (Technical Setup), bb4.5 (Assembly), bb6 (Field Requirements)
  - These are covered by qf-pipeline (Step 1-4)

#### qf-scaffolding MVP
- **Feature:** Created minimal qf-scaffolding MCP with `load_stage` tool
- **Tool:** `load_stage(module, stage)` - loads methodology markdown files
- **Supported:** M1 stages 0-7 (intro through best practices)
- **Config:** Added to Claude Desktop config
- **Package:** TypeScript with @modelcontextprotocol/sdk

#### URL Auto-Fetch for source_file
- **Feature:** `source_file` can now be a URL (http:// or https://)
- Automatically fetches URL content and converts HTML to markdown
- Saves fetched file to project with timestamp-based filename
- New utility: `utils/url_fetcher.py` with `is_url()` and `fetch_url_to_markdown()`
- New dependencies: `httpx>=0.27.0`, `markdownify>=0.13.0`
- Example: `step0_start(source_file="https://example.com/syllabus", ...)`

#### Entry Points Renamed: A/B/C/D → m1/m2/m3/m4/pipeline
- **Breaking change:** Entry point names now match module names
  - `"materials"` → `"m1"` (Content Analysis)
  - `"objectives"` → `"m2"` (Assessment Design)
  - `"blueprint"` → `"m3"` (Question Generation)
  - NEW: `"m4"` (Quality Assurance) - frågor som behöver QA
  - `"questions"` → `"pipeline"` (Direct validate/export)
- **Rationale:** Clearer connection between entry point and starting module
- **Default:** `entry_point="pipeline"` (was `"questions"`)
- **Files updated:** session_manager.py, session.py, server.py, WORKFLOW.md

#### Shared Session: 5 Entry Points (ADR-014)
- **Feature:** Flexible entry points for different starting contexts
  - **m1 (materials):** Start from instructional materials → M1 (qf-scaffolding)
  - **m2 (objectives):** Start from learning objectives → M2 (qf-scaffolding)
  - **m3 (blueprint):** Start from assessment plan → M3 (qf-scaffolding)
  - **m4 (questions for QA):** Start from questions needing review → M4
  - **pipeline (direct):** Validate and export directly [default]
- **Enhancement:** `source_file` now Optional (only required for m2/m3/m4/pipeline)
- **Enhancement:** New project folders: `00_materials/`, `methodology/`
- **Enhancement:** Auto-generated README in `00_materials/`
- **Enhancement:** `methodology` section in session.yaml for M1-M4 tracking
- **Enhancement:** `step0_start` returns routing guidance based on entry_point
- **Enhancement:** `init` tool now returns full m1/m2/m3/m4/pipeline routing guide
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
├── methodology/                 ✅ All modules imported
│   ├── m1/                      ✅ 8 files (Material Analysis)
│   ├── m2/                      ✅ 9 files (Assessment Planning)
│   ├── m3/                      ✅ 5 files (Question Generation)
│   └── m4/                      ✅ 6 files (Quality Assurance)
├── docs/
│   ├── DISCOVERY_BRIEF.md       ✅ Complete
│   ├── acdm/                    ✅ ACDM documentation
│   ├── adr/                     ✅ 14+ ADRs
│   ├── specs/                   ✅ Implementation specs
│   └── analysis/                ✅ Technical analyses
├── packages/
│   ├── qf-scaffolding/          ✅ MVP (load_stage for M1)
│   ├── qf-pipeline/             ✅ MCP server active
│   ├── qti-core/                ✅ Standalone QTI logic
│   └── course-extractor-mcp/    ✅ PDF extraction (AGPL)
├── qf-specifications/           🔶 Partially created
│   └── logging/                 ✅ RFC-001 schema + examples
└── docs/rfcs/                   ✅ RFC-001 unified logging
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
- **RFC-001 TIER 3:** user_decision events (after M1-M4 operational)
- **RFC-001 TIER 4:** ML training data collection (Q2-Q3 2026)
- Step 3: Decision tool (simple export vs Question Set)
- qf-scaffolding MCP completion (TypeScript, M1-M4 stages)
- Archive legacy MCPs

---

*QuestionForge - Forging Quality Questions*
