"""QuestionForge Pipeline MCP Server.

Provides tools for validating markdown questions and exporting to QTI format.
Includes session management for project-based workflows.

Tool naming convention (ADR-007):
  stepN_ = Step N in pipeline (consistent with Assessment_suite phaseN_)

  step0_* = Session Management
  step2_* = Validator
  step4_* = Export

  Cross-step utilities have no prefix (list_types)
"""

import asyncio
import json
import subprocess
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .wrappers import (
    # Parser - used by step1_* tools
    parse_markdown,
    parse_file,
    # Generator - used by list_types
    get_supported_types,
    # Validator - used by step2_validate_content
    validate_markdown,
    # Errors
    WrapperError,
    # NOTE: RFC-012 - These are now OBSOLETE (replaced by subprocess):
    # - generate_all_xml, create_qti_package (step4_export uses scripts)
    # - validate_file, validate_resources, copy_resources (subprocess)
)
from .tools import (
    start_session_tool,
    get_session_status_tool,
    load_session_tool,
    get_current_session,
    # Step 1 tools - RFC-013 core
    step1_start,
    step1_status,
    step1_navigate,
    step1_next,
    step1_previous,
    step1_jump,
    step1_analyze_question,
    step1_apply_fix,
    step1_skip,
    step1_finish,
    # Step 1 tools - Legacy (backwards compatibility)
    step1_analyze,
    step1_fix_auto,
    step1_fix_manual,
    step1_suggest,
    step1_batch_preview,
    step1_batch_apply,
    step1_transform,
    step1_preview,
    # Project file tools
    read_project_file,
    write_project_file,
)
from .utils.logger import log_action, log_event

# Create server instance
server = Server("qf-pipeline")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools."""
    return [
        # System
        Tool(
            name="init",
            description=(
                "CALL THIS FIRST! Returns M1/M2/M3/M4/Pipeline entry point routing. "
                "Ask user: 'Vad har du?' "
                "M1=Material, M2=Lärandemål, M3=Blueprint, M4=Frågor för QA, Pipeline=Direkt export. "
                "Then use step0_start with correct entry_point."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        # Step 0: Session Management
        Tool(
            name="step0_start",
            description=(
                "Start a new session OR load existing. "
                "For new: provide output_folder + entry_point (+ source_file for m2/m3/m4/pipeline OR materials_folder for m1). "
                "source_file can be a local path OR a URL (auto-fetched as .md). "
                "For existing: provide project_path."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "output_folder": {
                        "type": "string",
                        "description": "NEW SESSION: Directory where project will be created",
                    },
                    "source_file": {
                        "type": "string",
                        "description": "NEW SESSION: Path OR URL to source (required for m2/m3/m4/pipeline). URLs auto-fetched to .md",
                    },
                    "project_name": {
                        "type": "string",
                        "description": "NEW SESSION: Optional project name (auto-generated if not provided)",
                    },
                    "entry_point": {
                        "type": "string",
                        "description": (
                            "NEW SESSION: Entry point - "
                            "'m1' (material), 'm2' (lärandemål), 'm3' (blueprint), 'm4' (QA), 'pipeline' (direkt). "
                            "Default: 'pipeline'"
                        ),
                        "enum": ["m1", "m2", "m3", "m4", "pipeline"],
                    },
                    "materials_folder": {
                        "type": "string",
                        "description": "NEW SESSION: Path to folder containing instructional materials (required for entry_point m1). Entire folder structure copied to materials/ (junk files filtered).",
                    },
                    "project_path": {
                        "type": "string",
                        "description": "LOAD SESSION: Path to existing project directory",
                    },
                },
            },
        ),
        Tool(
            name="step0_status",
            description="Get status of current session including validation status and exports",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        # Step 2: Validator
        Tool(
            name="step2_validate",
            description="Validate markdown file. If session active: uses working_file by default.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to markdown file (optional if session active)",
                    },
                },
            },
        ),
        Tool(
            name="step2_validate_content",
            description="Validate markdown content string directly (for testing snippets)",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Markdown content to validate",
                    },
                },
                "required": ["content"],
            },
        ),
        Tool(
            name="step2_read",
            description=(
                "Read the working file content for inspection/fixing. "
                "Use when validation fails and you need to see the file. "
                "Requires active session."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "max_lines": {
                        "type": "integer",
                        "description": "Maximum lines to return (default: all)",
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Start from this line (1-indexed, default: 1)",
                    },
                },
            },
        ),
        # Step 3: Auto-Fix
        Tool(
            name="step3_autofix",
            description=(
                "Auto-fix mechanical errors in markdown. "
                "Runs validation → fix → validation loop until valid or max rounds. "
                "Fixes: colon in metadata (^type: → ^type), field positioning. "
                "Returns 'valid', 'needs_m5' (pedagogical errors), or 'max_rounds'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to markdown file",
                    },
                    "content": {
                        "type": "string",
                        "description": "Or provide content directly (instead of file_path)",
                    },
                    "max_rounds": {
                        "type": "integer",
                        "description": "Maximum fix iterations (default: 10)",
                        "default": 10,
                    },
                    "save": {
                        "type": "boolean",
                        "description": "Save fixed content to file (default: true)",
                        "default": True,
                    },
                },
            },
        ),
        # Step 4: Export
        Tool(
            name="step4_export",
            description="Export to QTI package. If session active: uses questions/ and output/. Or provide paths directly.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to markdown file (optional if session active)",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path for output ZIP file (optional if session active)",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code (sv/en)",
                        "default": "sv",
                    },
                },
            },
        ),
        # Step 1: Guided Build (Convert to QFMD)
        Tool(
            name="step1_start",
            description="Start Step 1 Guided Build session. Uses Step 0 session if active, otherwise requires project_path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to project folder (optional if Step 0 session exists)",
                    },
                    "source_file": {
                        "type": "string",
                        "description": "Override source file path (optional)",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="step1_status",
            description="Get Step 1 session status and progress",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="step1_analyze",
            description="Analyze a question. Returns auto_fixable and needs_input categories.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question_id": {
                        "type": "string",
                        "description": "Question ID to analyze (default: current)",
                    },
                },
            },
        ),
        Tool(
            name="step1_fix_auto",
            description="Apply ONLY auto-fixable transforms. Returns remaining issues that need user input.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question_id": {
                        "type": "string",
                        "description": "Question ID (default: current)",
                    },
                },
            },
        ),
        Tool(
            name="step1_fix_manual",
            description="Apply a single manual fix based on user input.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question_id": {
                        "type": "string",
                        "description": "Question ID",
                    },
                    "field": {
                        "type": "string",
                        "description": "Field to update (bloom, difficulty, partial_feedback, etc.)",
                    },
                    "value": {
                        "type": "string",
                        "description": "Value from user",
                    },
                },
                "required": ["question_id", "field", "value"],
            },
        ),
        Tool(
            name="step1_suggest",
            description="Generate a suggestion for a field. User can accept/modify.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question_id": {
                        "type": "string",
                        "description": "Question ID",
                    },
                    "field": {
                        "type": "string",
                        "description": "Field to suggest for",
                    },
                },
                "required": ["question_id", "field"],
            },
        ),
        Tool(
            name="step1_batch_preview",
            description="Show all questions with the same issue type.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_type": {
                        "type": "string",
                        "description": "E.g. missing_partial_feedback, missing_bloom",
                    },
                },
                "required": ["issue_type"],
            },
        ),
        Tool(
            name="step1_batch_apply",
            description="Apply the same fix to multiple questions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_type": {
                        "type": "string",
                        "description": "Issue type",
                    },
                    "fix_type": {
                        "type": "string",
                        "description": "How to fix (copy_from_correct, add_bloom_remember, etc.)",
                    },
                    "question_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Question IDs (optional, None = all affected)",
                    },
                },
                "required": ["issue_type", "fix_type"],
            },
        ),
        Tool(
            name="step1_skip",
            description="Skip an issue or entire question.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question_id": {
                        "type": "string",
                        "description": "Question ID (default: current)",
                    },
                    "issue_field": {
                        "type": "string",
                        "description": "Specific field to skip, or None for whole question",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for skipping",
                    },
                },
            },
        ),
        Tool(
            name="step1_transform",
            description="[LEGACY] Apply ALL transforms at once. Use step1_fix_auto for interactive flow.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question_id": {
                        "type": "string",
                        "description": "Question ID (default: all questions)",
                    },
                },
            },
        ),
        Tool(
            name="step1_preview",
            description="Preview the working file content",
            inputSchema={
                "type": "object",
                "properties": {
                    "lines": {
                        "type": "integer",
                        "description": "Number of lines to show (default: 50)",
                    },
                },
            },
        ),
        Tool(
            name="step1_finish",
            description="Finish Step 1 and generate summary report",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="step1_next",
            description="Navigate to next/previous question or jump to specific question ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "description": "Navigation: 'forward', 'back', or a question_id (e.g. 'Q005')",
                        "default": "forward",
                    },
                },
            },
        ),
        # RFC-013 Step 1 tools
        Tool(
            name="step1_navigate",
            description="[RFC-013] Navigate between questions. Direction: 'next', 'previous', or question_id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "description": "'next', 'previous', or question_id (e.g. 'Q007')",
                        "default": "next",
                    },
                },
            },
        ),
        Tool(
            name="step1_previous",
            description="[RFC-013] Move to previous question.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="step1_jump",
            description="[RFC-013] Jump to specific question by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question_id": {
                        "type": "string",
                        "description": "Question ID to jump to (e.g. 'Q007')",
                    },
                },
                "required": ["question_id"],
            },
        ),
        Tool(
            name="step1_analyze_question",
            description=(
                "[RFC-013] Analyze question for STRUCTURAL issues only. "
                "Pedagogical issues are reported but should go to M5. "
                "Returns AI suggestions from learned patterns."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question_id": {
                        "type": "string",
                        "description": "Question to analyze (default: current)",
                    },
                },
            },
        ),
        Tool(
            name="step1_apply_fix",
            description=(
                "[RFC-013] Apply a teacher-approved fix. "
                "Actions: 'accept_ai' (use AI suggestion), 'modify' (teacher edits), 'manual' (teacher writes), 'skip'. "
                "Updates pattern confidence and logs decision."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question_id": {
                        "type": "string",
                        "description": "Question being fixed",
                    },
                    "issue_type": {
                        "type": "string",
                        "description": "Type of structural issue",
                    },
                    "action": {
                        "type": "string",
                        "description": "'accept_ai', 'modify', 'manual', or 'skip'",
                        "enum": ["accept_ai", "modify", "manual", "skip"],
                    },
                    "fix_content": {
                        "type": "string",
                        "description": "Content for 'modify' or 'manual' actions",
                    },
                    "teacher_note": {
                        "type": "string",
                        "description": "Optional teacher reasoning",
                    },
                },
                "required": ["question_id", "issue_type", "action"],
            },
        ),
        # Cross-step utility
        Tool(
            name="list_types",
            description="List supported question types",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="list_projects",
            description="List configured MQG folders with status. Shows available projects for quick selection.",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_files": {
                        "type": "boolean",
                        "description": "Also count markdown files in each folder",
                        "default": False
                    }
                }
            },
        ),
        # Project file tools (read/write anywhere in project)
        Tool(
            name="read_project_file",
            description="Read any file within a project directory. Security: prevents path traversal outside project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Root project directory",
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "Path relative to project_path, e.g. 'output/questions.md'",
                    },
                },
                "required": ["project_path", "relative_path"],
            },
        ),
        Tool(
            name="write_project_file",
            description="Write any file within a project directory. Creates parent dirs by default. Security: prevents path traversal.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Root project directory",
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "Path relative to project_path",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write",
                    },
                    "create_dirs": {
                        "type": "boolean",
                        "description": "Create parent directories if needed (default: true)",
                        "default": True,
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Overwrite if file exists (default: true)",
                        "default": True,
                    },
                },
                "required": ["project_path", "relative_path", "content"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "init":
            return await handle_init()
        elif name == "step0_start":
            return await handle_step0_start(arguments)
        elif name == "step0_status":
            return await handle_step0_status(arguments)
        elif name == "step2_validate":
            return await handle_step2_validate(arguments)
        elif name == "step2_validate_content":
            return await handle_step2_validate_content(arguments)
        elif name == "step2_read":
            return await handle_step2_read(arguments)
        elif name == "step3_autofix":
            return await handle_step3_autofix(arguments)
        elif name == "step4_export":
            return await handle_step4_export(arguments)
        elif name == "list_types":
            return await handle_list_types()
        elif name == "list_projects":
            return await handle_list_projects(arguments)
        # Project file tools
        elif name == "read_project_file":
            return await handle_read_project_file(arguments)
        elif name == "write_project_file":
            return await handle_write_project_file(arguments)
        # Step 1: Guided Build
        elif name == "step1_start":
            return await handle_step1_start(arguments)
        elif name == "step1_status":
            return await handle_step1_status()
        elif name == "step1_analyze":
            return await handle_step1_analyze(arguments)
        elif name == "step1_fix_auto":
            return await handle_step1_fix_auto(arguments)
        elif name == "step1_fix_manual":
            return await handle_step1_fix_manual(arguments)
        elif name == "step1_suggest":
            return await handle_step1_suggest(arguments)
        elif name == "step1_batch_preview":
            return await handle_step1_batch_preview(arguments)
        elif name == "step1_batch_apply":
            return await handle_step1_batch_apply(arguments)
        elif name == "step1_skip":
            return await handle_step1_skip(arguments)
        elif name == "step1_transform":
            return await handle_step1_transform(arguments)
        elif name == "step1_preview":
            return await handle_step1_preview(arguments)
        elif name == "step1_finish":
            return await handle_step1_finish()
        elif name == "step1_next":
            return await handle_step1_next(arguments)
        # RFC-013 Step 1 tools
        elif name == "step1_navigate":
            return await handle_step1_navigate(arguments)
        elif name == "step1_previous":
            return await handle_step1_previous()
        elif name == "step1_jump":
            return await handle_step1_jump(arguments)
        elif name == "step1_analyze_question":
            return await handle_step1_analyze_question(arguments)
        elif name == "step1_apply_fix":
            return await handle_step1_apply_fix(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except WrapperError as e:
        return [TextContent(type="text", text=f"Error: {e}")]
    except FileNotFoundError as e:
        return [TextContent(type="text", text=f"File not found: {e}")]
    except PermissionError as e:
        return [TextContent(type="text", text=f"Permission denied: {e}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {type(e).__name__}: {e}")]


# =============================================================================
# System: Init
# =============================================================================

async def handle_init() -> List[TextContent]:
    """Handle init tool call - return critical instructions with M1/M2/M3/M4/Pipeline routing."""
    instructions = """# QuestionForge - Kritiska Instruktioner

## FLEXIBEL WORKFLOW

```
┌─────────────────────────────────────────────────────────────────────┐
│                         QUESTIONFORGE                                │
│                                                                      │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌──────┐ │
│   │   M1    │   │   M2    │   │   M3    │   │   M4    │   │Export│ │
│   │ Analys  │──▶│Blueprint│──▶│ Frågor  │──▶│   QA    │──▶│ QTI  │ │
│   └────▲────┘   └────▲────┘   └────▲────┘   └────▲────┘   └──▲───┘ │
│        │             │             │              │           │      │
│   ┌────┴────┐   ┌────┴────┐   ┌────┴────┐   ┌────┴────┐  ┌───┴───┐ │
│   │   m1    │   │   m2    │   │   m3    │   │   m4    │  │pipeline│
│   │Material │   │  Mål    │   │  Plan   │   │Frågor QA│  │ Direkt │
│   └─────────┘   └─────────┘   └─────────┘   └─────────┘  └───────┘ │
│                                                                      │
│         ◀── ── KAN HOPPA MELLAN MODULER ── ──▶                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Entry point = var du STARTAR, men du kan hoppa fritt mellan moduler!**

## STEG 1: FRÅGA VAD ANVÄNDAREN HAR

"Vad har du att börja med?"

**M1) MATERIAL** (föreläsningar, slides, transkriberingar)
   - Startar: M1 (Content Analysis)
   - Väg: M1 → M2 → M3 → M4 → Pipeline
   - source_file: Nej (valfri)

**M2) LÄRANDEMÅL** (kursplan, Skolverket, etc.)
   - Startar: M2 (Assessment Design)
   - Väg: M2 → M3 → M4 → Pipeline
   - source_file: Ja (fil/URL)

**M3) BLUEPRINT** (bedömningsplan, question matrix)
   - Startar: M3 (Question Generation)
   - Väg: M3 → M4 → Pipeline
   - source_file: Ja (fil/URL)

**M4) FRÅGOR FÖR QA** (frågor som behöver granskas)
   - Startar: M4 (Quality Assurance)
   - Väg: M4 → Pipeline
   - source_file: Ja (fil/URL)

**PIPELINE) FÄRDIGA FRÅGOR** (validera och exportera direkt)
   - Startar: Step 1-4 (Pipeline)
   - Hoppar: Alla moduler (M1-M4)
   - source_file: Ja (fil/URL)

## MODULER

| Modul | Namn | Vad den gör |
|-------|------|-------------|
| M1 | Content Analysis | Analyserar material, hittar lärandemål |
| M2 | Assessment Design | Skapar blueprint, planerar bedömning |
| M3 | Question Generation | Genererar frågor |
| M4 | Quality Assurance | Pedagogisk granskning |

## STEG 2: BEKRÄFTA VAL

INNAN step0_start, bekräfta:
"Du valde [entry_point] och startar på [modul]. Du kan hoppa mellan moduler. OK?"

## STEG 3: SKAPA SESSION

| Val      | entry_point | source_file |
|----------|-------------|-------------|
| Material | "m1"        | Nej (valfri)|
| Mål      | "m2"        | Ja (fil/URL)|
| Blueprint| "m3"        | Ja (fil/URL)|
| QA       | "m4"        | Ja (fil/URL)|
| Direkt   | "pipeline"  | Ja (fil/URL)|

Fråga:
- "Var ska projektet sparas?" (output_folder)
- "Vad ska projektet heta?" (project_name, valfritt)
- För m2/m3/m4/pipeline: "Var ligger filen?" (source_file) - kan vara URL!

## REGLER

1. **VÄNTA** på svar - GISSA INTE sökvägar!
2. **BEKRÄFTA** entry point innan step0_start
3. **VALIDERA** alltid innan export

## VERKTYG

Session: init, step0_start, step0_status
Metodologi: list_modules, load_stage, module_status (qf-scaffolding)
Pipeline: step1_*, step2_validate, step4_export
"""
    return [TextContent(type="text", text=instructions)]


# =============================================================================
# Step 0: Session Management
# =============================================================================

async def handle_step0_start(arguments: dict) -> List[TextContent]:
    """Handle step0_start - create new session OR load existing."""

    # Load existing session
    if arguments.get("project_path"):
        result = await load_session_tool(arguments["project_path"])
        if result.get("success"):
            # Log session_resume (TIER 2)
            log_event(
                project_path=Path(result['project_path']),
                session_id=result['session_id'],
                tool="step0_start",
                event="session_resume",
                level="info",
                data={
                    "resumed_at": result.get('validation_status', 'unknown'),
                    "working_file": result.get('working_file'),
                    "export_count": result.get('export_count', 0),
                }
            )
            return [TextContent(
                type="text",
                text=f"Session laddad!\n"
                     f"  ID: {result['session_id']}\n"
                     f"  Projekt: {result['project_path']}\n"
                     f"  Arbetsfil: {result.get('working_file', 'N/A')}\n"
                     f"  Validering: {result.get('validation_status', 'unknown')}"
            )]
        else:
            error = result.get("error", {})
            return [TextContent(
                type="text",
                text=f"Kunde inte ladda session: {error.get('message')}"
            )]

    # Create new session - requires output_folder
    if not arguments.get("output_folder"):
        return [TextContent(
            type="text",
            text=(
                "Error: output_folder krävs för ny session.\n\n"
                "Användning:\n"
                "  - Ny session: output_folder + entry_point (+ source_file för m2/m3/m4/pipeline)\n"
                "  - Ladda befintlig: project_path\n\n"
                "Entry points:\n"
                "  - m1: Börja från undervisningsmaterial (Content Analysis)\n"
                "  - m2: Börja från lärandemål (Assessment Design)\n"
                "  - m3: Börja från blueprint (Question Generation)\n"
                "  - m4: Börja från frågor för QA (Quality Assurance)\n"
                "  - pipeline: Validera och exportera direkt [default]"
            )
        )]

    # Get entry_point (default to "pipeline")
    entry_point = arguments.get("entry_point", "pipeline")

    # Validate materials_folder for m1 entry point
    materials_folder = arguments.get("materials_folder")

    if entry_point == "m1":
        if not materials_folder:
            return [TextContent(
                type="text",
                text=(
                    "Error: materials_folder krävs för entry point 'm1'.\n\n"
                    "Entry point m1 (Content Analysis) startar från undervisningsmaterial.\n"
                    "Ange sökväg till mapp med:\n"
                    "  - Presentationer (PDF, PPTX)\n"
                    "  - Föreläsningsanteckningar\n"
                    "  - Transkriptioner\n"
                    "  - Läroböcker/artiklar\n\n"
                    "Exempel:\n"
                    "  materials_folder='/Users/niklas/Nextcloud/Biologi_VT2025/Föreläsningar'"
                )
            )]

        # Validate materials_folder exists and is directory
        materials_path = Path(materials_folder)
        if not materials_path.exists():
            return [TextContent(
                type="text",
                text=f"Error: materials_folder finns inte: {materials_folder}"
            )]

        if not materials_path.is_dir():
            return [TextContent(
                type="text",
                text=f"Error: materials_folder är inte en mapp: {materials_folder}"
            )]

    # If materials_folder provided for non-m1 entry point, warn but continue
    if materials_folder and entry_point != "m1":
        logger.warning(
            f"materials_folder provided for '{entry_point}' entry point - "
            f"will be ignored. This parameter is only used for 'm1'."
        )
        materials_folder = None  # Clear it

    result = await start_session_tool(
        output_folder=arguments["output_folder"],
        source_file=arguments.get("source_file"),
        project_name=arguments.get("project_name"),
        entry_point=entry_point,
        materials_folder=materials_folder
    )

    if result.get("success"):
        log_action(
            Path(result['project_path']),
            "step0_start",
            f"Session created: {result['session_id']} (entry_point: {entry_point})",
            data={
                "session_id": result['session_id'],
                "source_file": arguments.get("source_file"),
                "project_path": result['project_path'],
                "entry_point": entry_point,
                "next_module": result.get('next_module'),
                "action": "create",
            }
        )

        # Build next steps guidance based on entry_point
        if result.get('pipeline_ready'):
            next_steps = (
                "Nästa steg (Pipeline):\n"
                "  1. step2_validate: Validera arbetsfilen\n"
                "  2. step4_export: Exportera till QTI"
            )
        else:
            next_module = result.get('next_module', 'm1')
            next_steps = (
                f"Nästa steg (qf-scaffolding):\n"
                f"  1. list_modules: Visa tillgängliga moduler\n"
                f"  2. load_stage({next_module}, 0): Börja med {next_module.upper()}"
            )

        # Build response text
        response_text = (
            f"Session startad!\n"
            f"  Session ID: {result['session_id']}\n"
            f"  Projekt: {result['project_path']}\n"
            f"  Entry point: {entry_point}\n"
        )

        if result.get('questions_file'):
            response_text += f"  Frågefil: {result['questions_file']}\n"

        if result.get('materials_copied'):
            response_text += f"  Material: {result['materials_copied']} filer kopierade till materials/\n"

        response_text += f"  Output: {result['output_folder']}\n\n{next_steps}"

        return [TextContent(type="text", text=response_text)]
    else:
        error = result.get("error", {})
        return [TextContent(
            type="text",
            text=f"Kunde inte starta session:\n"
                 f"  Typ: {error.get('type')}\n"
                 f"  Meddelande: {error.get('message')}"
        )]


async def handle_step0_status(arguments: dict) -> List[TextContent]:
    """Handle step0_status - get session status."""
    result = await get_session_status_tool()

    if result.get("active"):
        return [TextContent(
            type="text",
            text=f"Session aktiv\n"
                 f"  ID: {result['session_id']}\n"
                 f"  Projekt: {result['project_path']}\n"
                 f"  Arbetsfil: {result['working_file']}\n"
                 f"  Validering: {result['validation_status']} ({result.get('question_count', '?')} fragor)\n"
                 f"  Exporter: {result['export_count']}"
        )]
    else:
        return [TextContent(
            type="text",
            text="Ingen aktiv session. Anvand step0_start for att borja."
        )]


# =============================================================================
# Step 2: Validator
# =============================================================================

def format_validation_output(result: dict, file_path: str, question_count: int) -> str:
    """Format validation result like Terminal QTI-Generator."""
    lines = [
        "=" * 60,
        "QFMD FORMAT VALIDATION REPORT",
        "=" * 60,
        "",
    ]

    issues = result.get("issues", [])
    error_count = sum(1 for i in issues if i.get("level") == "ERROR")
    warning_count = sum(1 for i in issues if i.get("level") == "WARNING")

    if not result["valid"]:
        lines.append("❌ ERRORS FOUND:\n")

        # Group by question
        by_question = {}
        for issue in issues:
            q_num = issue.get("question_num") or 0
            q_id = issue.get("question_id") or "?"
            key = (q_num, q_id)
            if key not in by_question:
                by_question[key] = []
            by_question[key].append(issue)

        # Output grouped
        for (q_num, q_id), q_issues in sorted(by_question.items()):
            lines.append(f"Question {q_num} ({q_id}):")
            for issue in q_issues:
                lines.append(f"  {issue['message']}")
            lines.append("")
    else:
        lines.append("✅ No errors found.\n")

    # Summary
    valid_count = question_count - len(set(
        (i.get("question_num"), i.get("question_id"))
        for i in issues if i.get("level") == "ERROR"
    ))

    lines.extend([
        "=" * 60,
        "SUMMARY",
        "=" * 60,
        f"File: {file_path}",
        f"Total Questions: {question_count}",
        f"✅ Valid: {valid_count}",
        f"❌ Errors: {error_count}",
        f"⚠️  Warnings: {warning_count}",
        "",
    ])

    if result["valid"]:
        lines.extend([
            "STATUS: ✅ READY FOR QTI GENERATION",
            "",
            "=" * 60,
            "NEXT STEP",
            "=" * 60,
            "Validation complete! Proceed to Step 3:",
            "  → Use step3_decide to choose export type",
            "  → Or use step4_export to export directly",
            "",
            "STOP: Do not run step2_validate again - file is ready.",
        ])
    else:
        lines.append(f"STATUS: ❌ NOT READY - Fix {error_count} error(s) before QTI generation")

    return "\n".join(lines)


async def handle_step2_validate(arguments: dict) -> List[TextContent]:
    """
    Handle step2_validate - validate markdown file using subprocess.

    RFC-012: Run step1_validate.py script instead of wrapper to guarantee
    consistency with manual terminal workflow.
    """
    session = get_current_session()
    start_time = time.time()

    # Determine file path
    if arguments.get("file_path"):
        file_path = arguments["file_path"]
    elif session and session.working_file:
        file_path = str(session.working_file)
    else:
        return [TextContent(
            type="text",
            text="Ange file_path eller starta session forst (step0_start)"
        )]

    # Validate file exists
    if not Path(file_path).exists():
        return [TextContent(
            type="text",
            text=f"Filen finns inte: {file_path}"
        )]

    # Path to qti-core
    qti_core_path = Path(__file__).parent.parent.parent.parent / "qti-core"
    if not qti_core_path.exists():
        return [TextContent(
            type="text",
            text=f"qti-core not found at: {qti_core_path}"
        )]

    # Log tool_start (TIER 1)
    if session:
        log_event(
            project_path=session.project_path,
            session_id=session.session_id,
            tool="step2_validate",
            event="tool_start",
            level="info",
            data={"file": file_path, "method": "subprocess"}
        )

    try:
        # Run step1_validate.py via subprocess (RFC-012)
        result = subprocess.run(
            ['python3', 'scripts/step1_validate.py', str(file_path), '--verbose'],
            cwd=qti_core_path,
            capture_output=True,
            text=True,
            timeout=60
        )

        duration_ms = int((time.time() - start_time) * 1000)

        # Parse validation status from exit code
        is_valid = (result.returncode == 0)

        # Try to extract question count from output
        question_count = 0
        for line in result.stdout.split('\n'):
            if 'Total Questions:' in line:
                try:
                    question_count = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass

        # Log tool_end (TIER 1)
        if session:
            log_event(
                project_path=session.project_path,
                session_id=session.session_id,
                tool="step2_validate",
                event="tool_end",
                level="info",
                data={
                    "success": True,
                    "valid": is_valid,
                    "question_count": question_count,
                    "exit_code": result.returncode,
                },
                duration_ms=duration_ms
            )

        # Update session if active
        if session:
            session.update_validation(is_valid, question_count)

            # Log validation_complete (TIER 2) when validation passes
            if is_valid:
                log_event(
                    project_path=session.project_path,
                    session_id=session.session_id,
                    tool="step2_validate",
                    event="validation_complete",
                    level="info",
                    data={
                        "valid": True,
                        "question_count": question_count
                    }
                )

        # Combine stdout and stderr for output
        output = result.stdout
        if result.stderr:
            output += f"\n\nStderr:\n{result.stderr}"

        # Save report to session folder if active
        if session:
            report_path = session.project_path / "validation_report.txt"
            try:
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(output)
                output += f"\n\nReport saved to: {report_path}"
            except Exception as e:
                output += f"\n\n(Could not save report: {e})"

        return [TextContent(type="text", text=output)]

    except subprocess.TimeoutExpired:
        return [TextContent(
            type="text",
            text="Validation timeout (>60s). File may be too large."
        )]

    except Exception as e:
        # Log tool_error (TIER 1)
        if session:
            log_event(
                project_path=session.project_path,
                session_id=session.session_id,
                tool="step2_validate",
                event="tool_error",
                level="error",
                data={
                    "error_type": type(e).__name__,
                    "message": str(e),
                    "stacktrace": traceback.format_exc(),
                    "context": {"file": file_path}
                }
            )
        raise


async def handle_step2_validate_content(arguments: dict) -> List[TextContent]:
    """Handle step2_validate_content - validate markdown content string."""
    content = arguments.get("content")
    if not content:
        return [TextContent(type="text", text="Error: content kravs")]

    result = validate_markdown(content)

    if result["valid"]:
        return [TextContent(type="text", text="Innehallet ar giltigt")]

    issues_text = "\n".join(
        f"  [{i['level']}] {i['message']}" for i in result["issues"]
    )
    return [TextContent(type="text", text=f"Ogiltigt innehall:\n{issues_text}")]


async def handle_step2_read(arguments: dict) -> List[TextContent]:
    """Handle step2_read - read working file content."""
    session = get_current_session()

    if not session or not session.working_file:
        return [TextContent(
            type="text",
            text="Error: Ingen aktiv session. Kor step0_start forst."
        )]

    working_file = Path(session.working_file)

    if not working_file.exists():
        return [TextContent(
            type="text",
            text=f"Error: Arbetsfilen finns inte: {working_file}"
        )]

    try:
        with open(working_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        start_line = arguments.get('start_line', 1) - 1
        max_lines = arguments.get('max_lines')

        if start_line < 0:
            start_line = 0

        if max_lines:
            selected_lines = lines[start_line:start_line + max_lines]
        else:
            selected_lines = lines[start_line:]

        content = ''.join(selected_lines)
        line_count = len(selected_lines)
        total_lines = len(lines)

        header = f"Fil: {working_file.name}\n"
        header += f"Visar rad {start_line + 1}-{start_line + line_count} av {total_lines}\n"
        header += "-" * 40 + "\n"

        log_action(
            session.project_path,
            "step2_read",
            f"Read lines {start_line + 1}-{start_line + line_count}",
            data={
                "start_line": start_line + 1,
                "lines_read": line_count,
                "total_lines": total_lines,
            }
        )

        return [TextContent(type="text", text=header + content)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: Kunde inte lasa filen: {e}"
        )]


# =============================================================================
# Step 3: Auto-Fix
# =============================================================================

async def handle_step3_autofix(arguments: dict) -> List[TextContent]:
    """
    Handle step3_autofix - auto-fix mechanical errors.

    Runs validation → fix → validation loop until valid or max rounds.
    """
    from .tools.step3_autofix import autofix_file, autofix_content, Step3Result

    file_path = arguments.get('file_path')
    content = arguments.get('content')
    max_rounds = arguments.get('max_rounds', 10)
    save = arguments.get('save', True)

    # Check for active session
    session = get_current_session()
    project_path = None

    if session:
        project_path = session.project_path
        # If no file_path, use session's questions file
        if not file_path and not content:
            questions_dir = project_path / "questions"
            if questions_dir.exists():
                md_files = list(questions_dir.glob("*.md"))
                if md_files:
                    file_path = str(md_files[0])

    # Need either file_path or content
    if not file_path and not content:
        return [TextContent(
            type="text",
            text="Error: Provide file_path or content"
        )]

    try:
        if content:
            # Fix content string
            result, fixed_content = autofix_content(
                content,
                max_rounds=max_rounds,
                project_path=project_path
            )

            # Build response
            lines = [
                "# Step 3: Auto-Fix Result",
                "",
                f"**Status:** {result.status}",
                f"**Rounds:** {result.rounds}",
                f"**Fixes applied:** {len(result.fixes_applied)}",
                "",
            ]

            if result.fixes_applied:
                lines.append("## Fixes Applied")
                for fix in result.fixes_applied:
                    lines.append(f"- [{fix.rule_id}] {fix.fix_applied}")
                lines.append("")

            if result.remaining_errors:
                lines.append(f"## Remaining Errors ({len(result.remaining_errors)})")
                for err in result.remaining_errors[:10]:
                    q_id = err.get('question_id', '?')
                    msg = err.get('message', 'Unknown')
                    lines.append(f"- [{q_id}] {msg}")
                lines.append("")

            lines.append(f"**Message:** {result.message}")

            # If valid and caller wants the content back
            if result.status == "valid":
                lines.append("")
                lines.append("---")
                lines.append("")
                lines.append("## Fixed Content")
                lines.append("```markdown")
                lines.append(fixed_content[:2000] + ("..." if len(fixed_content) > 2000 else ""))
                lines.append("```")

            return [TextContent(type="text", text="\n".join(lines))]

        else:
            # Fix file
            input_path = Path(file_path)

            if not input_path.exists():
                return [TextContent(
                    type="text",
                    text=f"Error: File not found: {file_path}"
                )]

            result = autofix_file(
                input_path,
                output_path=input_path if save else None,
                max_rounds=max_rounds,
                project_path=project_path
            )

            # Log summary if session active (detailed logs in step3_iterations.jsonl)
            if project_path:
                log_event(
                    str(project_path),
                    session.session_id if session else "",
                    "step3_autofix",
                    "autofix_complete",
                    "info",
                    {
                        "status": result.status,
                        "rounds": result.rounds,
                        "fixes_applied": len(result.fixes_applied),
                        "remaining_errors": len(result.remaining_errors),
                    }
                )

            # Build response
            lines = [
                "# Step 3: Auto-Fix Result",
                "",
                f"**File:** {input_path.name}",
                f"**Status:** {result.status}",
                f"**Rounds:** {result.rounds}",
                f"**Fixes applied:** {len(result.fixes_applied)}",
                "",
            ]

            if result.fixes_applied:
                lines.append("## Fixes Applied")
                for fix in result.fixes_applied:
                    lines.append(f"- [{fix.rule_id}] {fix.fix_applied}")
                lines.append("")

            if result.remaining_errors:
                lines.append(f"## Remaining Errors ({len(result.remaining_errors)})")
                for err in result.remaining_errors[:10]:
                    q_id = err.get('question_id', '?')
                    msg = err.get('message', 'Unknown')
                    lines.append(f"- [{q_id}] {msg}")
                lines.append("")

            lines.append(f"**Message:** {result.message}")

            # Next step suggestion
            if result.status == "valid":
                lines.append("")
                lines.append("---")
                lines.append("**Next:** `step4_export` to create QTI package")
            elif result.status == "needs_m5":
                lines.append("")
                lines.append("---")
                lines.append("**Next:** Return to M5 to fix pedagogical errors")
            elif result.status == "needs_step1":
                lines.append("")
                lines.append("---")
                lines.append("**Next:** Use `step1_*` tools to fix structural errors")

            return [TextContent(type="text", text="\n".join(lines))]

    except Exception as e:
        error_msg = f"Step 3 error: {str(e)}\n\n{traceback.format_exc()}"
        return [TextContent(type="text", text=error_msg)]


# =============================================================================
# Step 4: Export
# =============================================================================

async def handle_step4_export(arguments: dict) -> List[TextContent]:
    """
    Handle step4_export - export to QTI package using ALL 5 scripts sequentially.

    RFC-012: Run actual scripts instead of wrappers to guarantee:
    1. apply_resource_mapping() is called (fixes critical image path bug)
    2. Consistency with manual terminal workflow
    3. Scripts = source of truth
    """
    session = get_current_session()
    start_time = time.time()

    # Determine file path
    if arguments.get("file_path"):
        file_path = arguments["file_path"]
    elif session and session.working_file:
        file_path = str(session.working_file)
    else:
        return [TextContent(
            type="text",
            text="Ange file_path eller starta session forst (step0_start)"
        )]

    # Validate input file exists
    if not Path(file_path).exists():
        return [TextContent(
            type="text",
            text=f"Filen finns inte: {file_path}"
        )]

    language = arguments.get("language", "sv")

    # Path to qti-core
    qti_core_path = Path(__file__).parent.parent.parent.parent / "qti-core"
    if not qti_core_path.exists():
        return [TextContent(
            type="text",
            text=f"qti-core not found at: {qti_core_path}"
        )]

    # Quiz name from file
    quiz_name = Path(file_path).stem

    # Output directory (map to project's output folder or qti-core/output)
    output_dir = Path(session.output_folder) if session and session.output_folder else qti_core_path / "output"

    # Quiz directory (where step2 creates the structure)
    quiz_dir = output_dir / quiz_name

    # Log tool_start (TIER 1)
    if session:
        log_event(
            project_path=session.project_path,
            session_id=session.session_id,
            tool="step4_export",
            event="tool_start",
            level="info",
            data={
                "file": file_path,
                "output_dir": str(output_dir),
                "language": language,
                "method": "subprocess"
            }
        )

    # Scripts to run sequentially
    # NOTE: step3/4/5 need explicit --quiz-dir because they can't auto-detect
    # when output is outside qti-core/output/ (which is where they look by default)
    scripts = [
        {
            'name': 'step1_validate.py',
            'args': [str(file_path), '--verbose'],
            'description': 'Validerar markdown format',
            'timeout': 60
        },
        {
            'name': 'step2_create_folder.py',
            'args': [str(file_path), '--output-dir', str(output_dir), '--output-name', quiz_name],
            'description': 'Skapar output-struktur',
            'timeout': 30
        },
        {
            'name': 'step3_copy_resources.py',
            'args': ['--markdown-file', str(file_path), '--quiz-dir', str(quiz_dir), '--verbose'],
            'description': 'Kopierar och byter namn pa resurser',
            'timeout': 60
        },
        {
            'name': 'step4_generate_xml.py',
            'args': ['--markdown-file', str(file_path), '--quiz-dir', str(quiz_dir), '--language', language, '--verbose'],
            'description': 'Genererar QTI XML-filer (+ apply_resource_mapping)',
            'timeout': 120
        },
        {
            'name': 'step5_create_zip.py',
            'args': ['--quiz-dir', str(quiz_dir), '--verbose'],
            'description': 'Skapar QTI-paket (ZIP)',
            'timeout': 60
        }
    ]

    # Collect output
    all_output = []
    all_output.append("=" * 70)
    all_output.append("QTI EXPORT - SUBPROCESS APPROACH (RFC-012)")
    all_output.append("=" * 70)
    all_output.append(f"Source: {file_path}")
    all_output.append(f"Output: {output_dir}")
    all_output.append(f"Language: {language}")
    all_output.append("")

    # Run each script
    for i, script in enumerate(scripts, 1):
        all_output.append(f"\n{'=' * 70}")
        all_output.append(f"STEG {i}/5: {script['name']}")
        all_output.append(f"{script['description']}")
        all_output.append(f"{'=' * 70}\n")

        try:
            result = subprocess.run(
                ['python3', f"scripts/{script['name']}"] + script['args'],
                cwd=qti_core_path,
                capture_output=True,
                text=True,
                timeout=script['timeout']
            )

            # Append output
            all_output.append(result.stdout)

            # Check for errors
            if result.returncode != 0:
                all_output.append(f"\n❌ FEL i {script['name']}!")
                all_output.append(f"\nStderr:\n{result.stderr}")

                # Log error
                if session:
                    log_action(
                        session.project_path,
                        "step4_export",
                        f"Error in {script['name']}: exit {result.returncode}"
                    )

                return [TextContent(type="text", text="\n".join(all_output))]

            all_output.append(f"✓ {script['name']} slutford!\n")

        except subprocess.TimeoutExpired:
            all_output.append(f"\n❌ TIMEOUT i {script['name']} (>{script['timeout']}s)!")
            return [TextContent(type="text", text="\n".join(all_output))]

        except Exception as e:
            all_output.append(f"\n❌ EXCEPTION i {script['name']}: {str(e)}")
            return [TextContent(type="text", text="\n".join(all_output))]

    duration_ms = int((time.time() - start_time) * 1000)

    # Success - update session state
    question_count = 0
    zip_path = ""
    try:
        # Read package_info.json to get ZIP path
        package_info_path = quiz_dir / ".workflow" / "package_info.json"

        if package_info_path.exists():
            with open(package_info_path) as f:
                package_info = json.load(f)

            zip_path = package_info.get('zip_path', str(output_dir / f"{quiz_name}.zip"))

            # Try to get question count from xml_files.json
            xml_files_path = quiz_dir / ".workflow" / "xml_files.json"
            if xml_files_path.exists():
                with open(xml_files_path) as f:
                    xml_info = json.load(f)
                question_count = xml_info.get('xml_count', 0)

            # Update session
            if session:
                session.log_export(zip_path, question_count)

                # Log tool_end (TIER 1)
                log_event(
                    project_path=session.project_path,
                    session_id=session.session_id,
                    tool="step4_export",
                    event="tool_end",
                    level="info",
                    data={
                        "success": True,
                        "question_count": question_count,
                        "output_file": zip_path,
                    },
                    duration_ms=duration_ms
                )

                # Log export_complete (TIER 2)
                log_event(
                    project_path=session.project_path,
                    session_id=session.session_id,
                    tool="step4_export",
                    event="export_complete",
                    level="info",
                    data={
                        "output_file": zip_path,
                        "question_count": question_count,
                        "format": "QTI 2.1"
                    }
                )

    except Exception as e:
        all_output.append(f"\n⚠️  Warning: Could not update session state: {e}")

    # Final summary
    all_output.append("\n" + "=" * 70)
    all_output.append("✅ EXPORT SLUTFORD!")
    all_output.append("=" * 70)
    all_output.append(f"\nZIP: {zip_path}")
    all_output.append(f"Fragor: {question_count}")
    all_output.append(f"\nKontrollera: {quiz_dir}")

    return [TextContent(type="text", text="\n".join(all_output))]


# =============================================================================
# Cross-step Utilities
# =============================================================================

async def handle_list_types() -> List[TextContent]:
    """Handle list_types - list supported question types."""
    types = get_supported_types()
    return [TextContent(
        type="text",
        text=f"Fragetyper ({len(types)}):\n" + "\n".join(f"  - {t}" for t in types)
    )]


async def handle_list_projects(arguments: dict) -> List[TextContent]:
    """Handle list_projects - list configured MQG folders."""
    from .utils.config import list_projects, ConfigError

    include_files = arguments.get("include_files", False)

    try:
        result = list_projects(include_files=include_files)
    except ConfigError as e:
        return [TextContent(type="text", text=f"Konfigurationsfel: {e}")]

    lines = [f"MQG Projekt ({result['count']} st):\n"]

    for p in result['projects']:
        status = "+" if p['exists'] else "-"
        lines.append(f"  {p['index']}. [{status}] {p['name']}")
        lines.append(f"     Path: {p['path']}")
        if p['description']:
            lines.append(f"     {p['description']}")
        if include_files and p.get('md_file_count') is not None:
            lines.append(f"     Filer: {p['md_file_count']} markdown")
        lines.append("")

    if result['default_output_dir']:
        lines.append(f"Default output: {result['default_output_dir']}")

    lines.append(f"\nConfig: {result['config_path']}")
    lines.append("\nTips: Anvand step0_start med source_file fran onskad mapp.")

    return [TextContent(type="text", text="\n".join(lines))]


# =============================================================================
# Project File Tools (read/write anywhere in project)
# =============================================================================

async def handle_read_project_file(arguments: dict) -> List[TextContent]:
    """Handle read_project_file - read any file within project."""
    project_path = arguments.get("project_path")
    relative_path = arguments.get("relative_path")

    if not project_path or not relative_path:
        return [TextContent(
            type="text",
            text="Error: Both project_path and relative_path are required"
        )]

    result = await read_project_file(project_path, relative_path)

    if not result.get("success"):
        return [TextContent(
            type="text",
            text=f"Error: {result.get('error', 'Unknown error')}"
        )]

    # Format successful response
    lines = [
        f"File: {result['relative_path']}",
        f"Size: {result['size_bytes']} bytes",
        "-" * 40,
        result['content']
    ]

    return [TextContent(type="text", text="\n".join(lines))]


async def handle_write_project_file(arguments: dict) -> List[TextContent]:
    """Handle write_project_file - write any file within project."""
    project_path = arguments.get("project_path")
    relative_path = arguments.get("relative_path")
    content = arguments.get("content")
    create_dirs = arguments.get("create_dirs", True)
    overwrite = arguments.get("overwrite", True)

    if not project_path or not relative_path or content is None:
        return [TextContent(
            type="text",
            text="Error: project_path, relative_path, and content are required"
        )]

    result = await write_project_file(
        project_path,
        relative_path,
        content,
        create_dirs=create_dirs,
        overwrite=overwrite
    )

    if not result.get("success"):
        return [TextContent(
            type="text",
            text=f"Error: {result.get('error', 'Unknown error')}"
        )]

    # Format successful response
    msg = f"Wrote {result['bytes_written']} bytes to {result['relative_path']}"
    if result.get('created_dirs'):
        msg += " (created parent directories)"

    return [TextContent(type="text", text=msg)]


# =============================================================================
# Step 1: Guided Build (Convert to QFMD)
# =============================================================================

async def handle_step1_start(arguments: dict) -> List[TextContent]:
    """Handle step1_start - start guided build session.

    Uses Step 0 session if active, otherwise requires project_path.
    """
    result = await step1_start(
        project_path=arguments.get("project_path"),
        source_file=arguments.get("source_file")
    )

    if result.get("error"):
        return [TextContent(
            type="text",
            text=f"Error: {result['error']}\n"
                 f"Recommendation: {result.get('recommendation', '')}"
        )]

    if result.get("message") and "redan" in result.get("message", ""):
        return [TextContent(
            type="text",
            text=f"{result['message']}\n{result.get('recommendation', '')}"
        )]

    # Log to pipeline
    session = get_current_session()
    if session:
        log_action(
            session.project_path,
            "step1_start",
            f"Started guided build: {result['total_questions']} questions in {result['format']} format",
            data={
                "session_id": result['session_id'],
                "format": result['format'],
                "total_questions": result['total_questions'],
                "auto_fixable": result.get("first_question", {}).get("auto_fixable", 0),
            }
        )

    first_q = result.get("first_question", {})
    return [TextContent(
        type="text",
        text=f"Step 1 Session startad!\n"
             f"  Session ID: {result['session_id']}\n"
             f"  Format: {result['format']} ({result['format_description']})\n"
             f"  Frågor: {result['total_questions']}\n"
             f"  Working file: {result['working_file']}\n\n"
             f"Första fråga: {first_q.get('id')} - {first_q.get('title')}\n"
             f"  Typ: {first_q.get('type')}\n"
             f"  Problem: {first_q.get('issues_count')} ({first_q.get('auto_fixable')} auto-fixbara)\n\n"
             f"{first_q.get('issues_summary', '')}\n\n"
             f"{result.get('message', '')}"
    )]


async def handle_step1_status() -> List[TextContent]:
    """Handle step1_status - get session status."""
    result = await step1_status()

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    return [TextContent(
        type="text",
        text=f"Step 1 Status\n"
             f"  Session: {result['session_id']}\n"
             f"  Format: {result['format']}\n"
             f"  Ändringar: {result['changes_made']}\n\n"
             f"{result['progress_display']}\n\n"
             f"Working file: {result['working_file']}"
    )]


async def handle_step1_analyze(arguments: dict) -> List[TextContent]:
    """Handle step1_analyze - analyze question."""
    session = get_current_session()
    start_time = time.time()
    question_id = arguments.get("question_id")

    # Log tool_start (TIER 1)
    if session:
        log_event(
            project_path=session.project_path,
            session_id=session.session_id,
            tool="step1_analyze",
            event="tool_start",
            level="info",
            data={"question_id": question_id}
        )

    try:
        result = await step1_analyze(question_id)
        duration_ms = int((time.time() - start_time) * 1000)

        if result.get("error"):
            # Log tool_end with failure
            if session:
                log_event(
                    project_path=session.project_path,
                    session_id=session.session_id,
                    tool="step1_analyze",
                    event="tool_end",
                    level="warn",
                    data={"success": False, "error": result['error']},
                    duration_ms=duration_ms
                )
            return [TextContent(type="text", text=f"Error: {result['error']}")]

        # Log tool_end with success
        if session:
            log_event(
                project_path=session.project_path,
                session_id=session.session_id,
                tool="step1_analyze",
                event="tool_end",
                level="info",
                data={
                    "success": True,
                    "question_id": result['question_id'],
                    "total_issues": result['total_issues'],
                    "auto_fixable_count": result['auto_fixable_count']
                },
                duration_ms=duration_ms
            )

        return [TextContent(
            type="text",
            text=f"Analys: {result['question_id']} ({result['question_type']})\n\n"
                 f"Problem: {result['total_issues']} "
                 f"(kritiska: {result['by_severity']['critical']}, "
                 f"varningar: {result['by_severity']['warning']})\n"
                 f"Auto-fixbara: {result['auto_fixable']}\n\n"
                 f"{result['issues_summary']}"
        )]

    except Exception as e:
        # Log tool_error (TIER 1)
        if session:
            log_event(
                project_path=session.project_path,
                session_id=session.session_id,
                tool="step1_analyze",
                event="tool_error",
                level="error",
                data={
                    "error_type": type(e).__name__,
                    "message": str(e),
                    "stacktrace": traceback.format_exc(),
                    "context": {"question_id": question_id}
                }
            )
        raise


async def handle_step1_transform(arguments: dict) -> List[TextContent]:
    """Handle step1_transform - apply transformations."""
    result = await step1_transform(arguments.get("question_id"))

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    changes = result.get("changes", [])

    # Log to pipeline
    session = get_current_session()
    if session:
        log_action(
            session.project_path,
            "step1_transform",
            f"Transformed: {len(changes)} changes applied",
            data={
                "question_id": arguments.get("question_id", "ALL"),
                "changes_count": len(changes),
                "changes": changes[:10],  # Log first 10 changes
                "questions_processed": result.get("questions_processed", 1),
            }
        )

    if not changes:
        return [TextContent(type="text", text=result.get("message", "Inga ändringar"))]

    changes_text = "\n".join(f"  - {c}" for c in changes)
    return [TextContent(
        type="text",
        text=f"Transformationer applicerade!\n\n"
             f"Ändringar ({len(changes)}):\n{changes_text}\n\n"
             f"{result.get('message', '')}\n"
             f"{result.get('next_step', '')}"
    )]


async def handle_step1_preview(arguments: dict) -> List[TextContent]:
    """Handle step1_preview - preview working file."""
    result = await step1_preview(arguments.get("lines", 50))

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    return [TextContent(
        type="text",
        text=f"Fil: {result['file']}\n"
             f"Visar {result['showing']} av {result['total_lines']} rader\n"
             f"{'=' * 50}\n"
             f"{result['content']}"
    )]


async def handle_step1_finish() -> List[TextContent]:
    """Handle step1_finish - finish and generate report."""
    result = await step1_finish()

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    summary = result.get("summary", {})
    changes = result.get("changes", [])

    # Log to pipeline
    session = get_current_session()
    if session:
        log_action(
            session.project_path,
            "step1_finish",
            f"Finished: {summary['completed']}/{summary['total_questions']} questions, {summary['total_changes']} changes",
            data={
                "total_questions": summary['total_questions'],
                "completed": summary['completed'],
                "skipped": summary['skipped'],
                "total_changes": summary['total_changes'],
                "ready_for_step2": result['ready_for_step2'],
            }
        )

    changes_text = "\n".join(
        f"  - {c['question']}: {c['description']}" for c in changes[:5]
    )
    if len(changes) > 5:
        changes_text += f"\n  ... och {len(changes) - 5} fler"

    status = "REDO för Step 2" if result['ready_for_step2'] else "EJ REDO"

    return [TextContent(
        type="text",
        text=f"Step 1 Avslutad!\n"
             f"{'=' * 50}\n\n"
             f"Session: {result['session_id']}\n"
             f"Working file: {result['working_file']}\n\n"
             f"Sammanfattning:\n"
             f"  Totalt: {summary['total_questions']} frågor\n"
             f"  Klara: {summary['completed']}\n"
             f"  Hoppade: {summary['skipped']}\n"
             f"  Ändringar: {summary['total_changes']}\n\n"
             f"Ändringar:\n{changes_text}\n\n"
             f"Status: {status}\n"
             f"Nästa steg: {result['next_action']}"
    )]


# =============================================================================
# Step 1: Interactive Tools (NEW)
# =============================================================================

async def handle_step1_fix_auto(arguments: dict) -> List[TextContent]:
    """Handle step1_fix_auto - apply only auto transforms."""
    session = get_current_session()
    start_time = time.time()
    question_id = arguments.get("question_id")

    # Log tool_start (TIER 1)
    if session:
        log_event(
            project_path=session.project_path,
            session_id=session.session_id,
            tool="step1_fix_auto",
            event="tool_start",
            level="info",
            data={"question_id": question_id}
        )

    try:
        result = await step1_fix_auto(question_id)
        duration_ms = int((time.time() - start_time) * 1000)

        if result.get("error"):
            # Log tool_end with failure
            if session:
                log_event(
                    project_path=session.project_path,
                    session_id=session.session_id,
                    tool="step1_fix_auto",
                    event="tool_end",
                    level="warn",
                    data={"success": False, "error": result['error']},
                    duration_ms=duration_ms
                )
            return [TextContent(type="text", text=f"Error: {result['error']}")]

        # Log tool_end with success
        if session:
            log_event(
                project_path=session.project_path,
                session_id=session.session_id,
                tool="step1_fix_auto",
                event="tool_end",
                level="info",
                data={
                    "success": True,
                    "question_id": result['question_id'],
                    "fixed_count": result['fixed_count'],
                    "remaining_count": result['remaining_count'],
                },
                duration_ms=duration_ms
            )

        fixed_text = "\n".join(f"  - {c}" for c in result.get("fixed", []))
        remaining = result.get("remaining", [])
        remaining_text = "\n".join(f"  - {r['message']}" for r in remaining)

        return [TextContent(
            type="text",
            text=f"Auto-fix på {result['question_id']}\n\n"
                 f"Fixat ({result['fixed_count']}):\n{fixed_text or '  (inga)'}\n\n"
                 f"Kvar ({result['remaining_count']}):\n{remaining_text or '  (inga)'}\n\n"
                 f"{result.get('instruction', '')}"
        )]

    except Exception as e:
        # Log tool_error (TIER 1)
        if session:
            log_event(
                project_path=session.project_path,
                session_id=session.session_id,
                tool="step1_fix_auto",
                event="tool_error",
                level="error",
                data={
                    "error_type": type(e).__name__,
                    "message": str(e),
                    "stacktrace": traceback.format_exc(),
                    "context": {"question_id": question_id}
                }
            )
        raise


async def handle_step1_fix_manual(arguments: dict) -> List[TextContent]:
    """Handle step1_fix_manual - apply single manual fix."""
    session = get_current_session()
    start_time = time.time()
    question_id = arguments.get("question_id")
    field = arguments.get("field")
    value = arguments.get("value")

    if not question_id or not field or not value:
        return [TextContent(type="text", text="Error: question_id, field och value krävs")]

    # Log tool_start (TIER 1)
    if session:
        log_event(
            project_path=session.project_path,
            session_id=session.session_id,
            tool="step1_fix_manual",
            event="tool_start",
            level="info",
            data={"question_id": question_id, "field": field}
        )

    try:
        result = await step1_fix_manual(question_id, field, value)
        duration_ms = int((time.time() - start_time) * 1000)

        if result.get("error"):
            # Log tool_end with failure
            if session:
                log_event(
                    project_path=session.project_path,
                    session_id=session.session_id,
                    tool="step1_fix_manual",
                    event="tool_end",
                    level="warn",
                    data={"success": False, "error": result['error']},
                    duration_ms=duration_ms
                )
            return [TextContent(type="text", text=f"Error: {result['error']}")]

        # Log tool_end with success
        if session:
            log_event(
                project_path=session.project_path,
                session_id=session.session_id,
                tool="step1_fix_manual",
                event="tool_end",
                level="info",
                data={
                    "success": result.get("success", False),
                    "question_id": question_id,
                    "field": field,
                    "value": value[:50] if len(value) > 50 else value,
                },
                duration_ms=duration_ms
            )

        return [TextContent(
            type="text",
            text=result.get("message", "")
        )]

    except Exception as e:
        # Log tool_error (TIER 1)
        if session:
            log_event(
                project_path=session.project_path,
                session_id=session.session_id,
                tool="step1_fix_manual",
                event="tool_error",
                level="error",
                data={
                    "error_type": type(e).__name__,
                    "message": str(e),
                    "stacktrace": traceback.format_exc(),
                    "context": {"question_id": question_id, "field": field}
                }
            )
        raise


async def handle_step1_suggest(arguments: dict) -> List[TextContent]:
    """Handle step1_suggest - generate suggestion."""
    question_id = arguments.get("question_id")
    field = arguments.get("field")

    if not question_id or not field:
        return [TextContent(type="text", text="Error: question_id och field krävs")]

    result = await step1_suggest(question_id, field)

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    options_text = ""
    if result.get("options"):
        options_text = f"\nAlternativ: {', '.join(result['options'])}"

    return [TextContent(
        type="text",
        text=f"Förslag för {field} på {question_id}:\n\n"
             f"  Förslag: {result.get('suggestion', '(inget)')}\n"
             f"{options_text}\n\n"
             f"{result.get('instruction', '')}"
    )]


async def handle_step1_batch_preview(arguments: dict) -> List[TextContent]:
    """Handle step1_batch_preview - show questions with same issue."""
    issue_type = arguments.get("issue_type")

    if not issue_type:
        return [TextContent(type="text", text="Error: issue_type krävs")]

    result = await step1_batch_preview(issue_type)

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    questions = result.get("questions", [])
    questions_text = "\n".join(
        f"  - {q['question_id']}: {q.get('title', '(no title)')}"
        for q in questions
    )

    return [TextContent(
        type="text",
        text=f"Frågor med {issue_type}:\n\n"
             f"Totalt: {result['count']}\n"
             f"Förhandsgranskning:\n{questions_text or '  (inga)'}\n\n"
             f"{result.get('instruction', '')}"
    )]


async def handle_step1_batch_apply(arguments: dict) -> List[TextContent]:
    """Handle step1_batch_apply - apply fix to multiple questions."""
    issue_type = arguments.get("issue_type")
    fix_type = arguments.get("fix_type")
    question_ids = arguments.get("question_ids")

    if not issue_type or not fix_type:
        return [TextContent(type="text", text="Error: issue_type och fix_type krävs")]

    result = await step1_batch_apply(issue_type, fix_type, question_ids)

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    # Log to pipeline
    session = get_current_session()
    if session:
        log_action(
            session.project_path,
            "step1_batch_apply",
            f"Batch fixed {result['success_count']} questions for {issue_type}",
            data={
                "issue_type": issue_type,
                "fix_type": fix_type,
                "success_count": result['success_count'],
                "failed_count": result['failed_count'],
            }
        )

    return [TextContent(
        type="text",
        text=f"Batch-fix: {issue_type}\n\n"
             f"Fix-typ: {fix_type}\n"
             f"Lyckades: {result['success_count']}\n"
             f"Misslyckades: {result['failed_count']}\n\n"
             f"{result.get('message', '')}"
    )]


async def handle_step1_skip(arguments: dict) -> List[TextContent]:
    """Handle step1_skip - skip issue or question."""
    result = await step1_skip(
        question_id=arguments.get("question_id"),
        issue_field=arguments.get("issue_field"),
        reason=arguments.get("reason")
    )

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    return [TextContent(
        type="text",
        text=result.get("message", "Hoppade över")
    )]


async def handle_step1_next(arguments: dict) -> List[TextContent]:
    """Handle step1_next - navigate to next/previous question."""
    direction = arguments.get("direction", "forward")

    result = await step1_next(direction)

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    # Format progress bar
    progress = result.get("progress", {})
    progress_pct = progress.get("percent", 0)
    filled = int(progress_pct / 5)
    bar = "█" * filled + "░" * (20 - filled)

    # Build output
    current_idx = result.get('current_index', 0)
    total = result.get('total_questions', '?')
    q_id = result.get('current_question', '?')
    q_type = result.get('question_type', '?')
    q_title = result.get('question_title', '')
    issues = result.get('issues_count', 0)
    auto_fix = result.get('auto_fixable', 0)
    summary = result.get('issues_summary', '')

    return [TextContent(
        type="text",
        text=f"Navigerade till {q_id} - {q_title}\n\n"
             f"[{bar}] {progress_pct}%\n"
             f"Fråga {current_idx + 1} av {total}\n\n"
             f"Typ: {q_type}\n"
             f"Problem: {issues} ({auto_fix} auto-fixbara)\n\n"
             f"{summary}"
    )]


# =============================================================================
# RFC-013 Step 1 Handlers
# =============================================================================

async def handle_step1_navigate(arguments: dict) -> List[TextContent]:
    """Handle step1_navigate - RFC-013 navigation."""
    direction = arguments.get("direction", "next")
    result = await step1_navigate(direction)

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    q = result.get("current_question", {})
    suggestions = result.get("ai_suggestions", [])

    output = f"""Navigerade: {result.get('navigated_from')} → {result.get('navigated_to')}
Position: {result.get('position')}

**{q.get('question_id')}** ({q.get('type')})
{q.get('title', '')}

Strukturella problem: {q.get('issues_count', 0)}
"""

    if suggestions:
        output += "\n**AI-förslag:**\n"
        for s in suggestions[:3]:
            conf = int(s.get('confidence', 0) * 100)
            output += f"- {s.get('message')} (confidence: {conf}%)\n"
            output += f"  Förslag: {s.get('fix_suggestion')}\n"

    output += f"\n**Nästa:** {result.get('next_action')}"

    return [TextContent(type="text", text=output)]


async def handle_step1_previous() -> List[TextContent]:
    """Handle step1_previous - move to previous question."""
    result = await step1_previous()

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    return await handle_step1_navigate({"direction": "previous"})


async def handle_step1_jump(arguments: dict) -> List[TextContent]:
    """Handle step1_jump - jump to specific question."""
    question_id = arguments.get("question_id")
    if not question_id:
        return [TextContent(type="text", text="Error: question_id krävs")]

    result = await step1_jump(question_id)

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    q = result.get("current_question", {})
    return [TextContent(
        type="text",
        text=f"Hoppade till {q.get('question_id')}\nPosition: {result.get('position')}"
    )]


async def handle_step1_analyze_question(arguments: dict) -> List[TextContent]:
    """Handle step1_analyze_question - RFC-013 structural analysis."""
    question_id = arguments.get("question_id")
    result = await step1_analyze_question(question_id)

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    output = f"""## Analys: {result.get('question_id')} ({result.get('question_type')})

### Strukturella problem ({result.get('structural_count', 0)})
"""

    for issue in result.get("structural_issues", []):
        output += f"- **{issue.get('type')}**: {issue.get('message')}\n"
        output += f"  Förslag: {issue.get('fix_suggestion')}\n"
        if issue.get('auto_fixable'):
            output += "  ✓ Auto-fixbar\n"

    if result.get('pedagogical_count', 0) > 0:
        output += f"\n### Pedagogiska problem ({result.get('pedagogical_count')}) → M5\n"
        for issue in result.get("pedagogical_issues", [])[:3]:
            output += f"- {issue.get('message')}\n"

    output += f"\n**Instruktion:** {result.get('instruction')}"
    output += f"\n**Nästa:** {result.get('next_action')}"

    return [TextContent(type="text", text=output)]


async def handle_step1_apply_fix(arguments: dict) -> List[TextContent]:
    """Handle step1_apply_fix - RFC-013 teacher-approved fix."""
    question_id = arguments.get("question_id")
    issue_type = arguments.get("issue_type")
    action = arguments.get("action")
    fix_content = arguments.get("fix_content")
    teacher_note = arguments.get("teacher_note")

    if not all([question_id, issue_type, action]):
        return [TextContent(type="text", text="Error: question_id, issue_type och action krävs")]

    result = await step1_apply_fix(question_id, issue_type, action, fix_content, teacher_note)

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    output = f"""## Fix applicerad

**Fråga:** {result.get('question_id')}
**Åtgärd:** {result.get('action')}
**Resultat:** {'✓ Lyckades' if result.get('success') else '✗ Misslyckades'}

"""

    if result.get('pattern_updated'):
        output += f"**Pattern uppdaterad:** {result.get('pattern_updated')} "
        output += f"(confidence: {int(result.get('pattern_confidence', 0) * 100)}%)\n\n"

    output += f"**Kvarvarande problem:** {result.get('remaining_issues', 0)}\n"
    output += f"**Totalt fixade:** {result.get('issues_fixed_total', 0)}\n"
    output += f"\n**Nästa:** {result.get('next_action')}"

    return [TextContent(type="text", text=output)]


# =============================================================================
# Server Entry Point
# =============================================================================

async def run_server():
    """Run the MCP server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    """Run the MCP server."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
