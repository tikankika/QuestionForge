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
from pathlib import Path
from typing import List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .wrappers import (
    parse_markdown,
    parse_file,
    generate_all_xml,
    create_qti_package,
    validate_markdown,
    validate_file,
    get_supported_types,
    validate_resources,
    copy_resources,
    WrapperError,
    ResourceError,
)
from .tools import (
    start_session_tool,
    get_session_status_tool,
    load_session_tool,
    get_current_session,
    # Step 1 tools
    step1_start,
    step1_status,
    step1_analyze,
    step1_fix_auto,
    step1_fix_manual,
    step1_suggest,
    step1_batch_preview,
    step1_batch_apply,
    step1_skip,
    step1_transform,
    step1_next,
    step1_preview,
    step1_finish,
)
from .utils.logger import log_action

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
                        "description": "NEW SESSION: Path to folder containing instructional materials (required for entry_point m1). Entire folder structure copied to 00_materials/ (junk files filtered).",
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
        # Step 4: Export
        Tool(
            name="step4_export",
            description="Export to QTI package. If session active: uses working_file and 03_output/. Or provide paths directly.",
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
        # Step 1: Guided Build (v6.3 → v6.5)
        Tool(
            name="step1_start",
            description="Start Step 1 Guided Build session. Uses Step 0 session if active, otherwise requires source_file and output_folder.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_file": {
                        "type": "string",
                        "description": "Path to v6.3 markdown file (optional if Step 0 session exists)",
                    },
                    "output_folder": {
                        "type": "string",
                        "description": "Directory for output files (optional if Step 0 session exists)",
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Optional project name",
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
        elif name == "step4_export":
            return await handle_step4_export(arguments)
        elif name == "list_types":
            return await handle_list_types()
        elif name == "list_projects":
            return await handle_list_projects(arguments)
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
            log_action(
                Path(result['project_path']),
                "step0_start",
                f"Session loaded: {result['session_id']}",
                data={
                    "session_id": result['session_id'],
                    "project_path": result['project_path'],
                    "action": "load",
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

        if result.get('working_file'):
            response_text += f"  Arbetsfil: {result['working_file']}\n"

        if result.get('materials_copied'):
            response_text += f"  Material: {result['materials_copied']} filer kopierade till 00_materials/\n"

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
        "MQG FORMAT VALIDATION REPORT (v6.5)",
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
    """Handle step2_validate - validate markdown file."""
    session = get_current_session()

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

    result = validate_file(file_path)

    # Count questions from parsing
    try:
        parse_result = parse_file(file_path)
        question_count = len(parse_result.get("questions", []))
    except Exception:
        question_count = 0

    # Count errors and warnings (levels are UPPERCASE from validator)
    error_count = sum(1 for i in result.get("issues", []) if i.get("level") == "ERROR")
    warning_count = sum(1 for i in result.get("issues", []) if i.get("level") == "WARNING")

    # Update session if active
    if session:
        # Check if this is the first time validation passes
        was_valid_before = session.get_status().get("validation_status") == "valid"

        session.update_validation(result["valid"], question_count)
        log_action(
            session.project_path,
            "step2_validate",
            f"Validated: {question_count} questions, {error_count} errors",
            data={
                "question_count": question_count,
                "error_count": error_count,
                "warning_count": warning_count,
                "valid": result["valid"],
            }
        )

        # Log step2_complete when validation passes for the first time
        if result["valid"] and not was_valid_before:
            log_action(
                session.project_path,
                "step2_complete",
                f"Step 2 complete: {question_count} questions validated successfully",
                data={
                    "question_count": question_count,
                    "next_step": "step3_decide or step4_export",
                }
            )

    # Format output like Terminal QTI-Generator
    formatted_output = format_validation_output(result, file_path, question_count)

    # Save report to session folder if active
    report_path = None
    if session:
        report_path = session.project_path / "validation_report.txt"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(formatted_output)
            formatted_output += f"\n\nReport saved to: {report_path}"
        except Exception as e:
            formatted_output += f"\n\n(Could not save report: {e})"

    return [TextContent(type="text", text=formatted_output)]


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
# Step 4: Export
# =============================================================================

async def handle_step4_export(arguments: dict) -> List[TextContent]:
    """Handle step4_export - export to QTI package."""
    session = get_current_session()

    # Determine paths
    if session and session.working_file:
        file_path = arguments.get("file_path") or str(session.working_file)
        if arguments.get("output_path"):
            output_path = arguments["output_path"]
        else:
            source_name = session.working_file.stem
            output_path = str(session.output_folder / f"{source_name}_QTI.zip")
    else:
        file_path = arguments.get("file_path")
        output_path = arguments.get("output_path")

    if not file_path:
        return [TextContent(
            type="text",
            text="Ange file_path eller starta session forst (step0_start)"
        )]
    if not output_path:
        return [TextContent(
            type="text",
            text="Ange output_path eller starta session forst"
        )]

    # Validate input file exists
    if not Path(file_path).exists():
        return [TextContent(
            type="text",
            text=f"Filen finns inte: {file_path}"
        )]

    language = arguments.get("language", "sv")

    # Parse markdown
    data = parse_file(file_path)
    questions = data.get("questions", [])
    metadata = data.get("metadata", {})

    if not questions:
        return [TextContent(type="text", text="Inga fragor hittades i filen")]

    # === Resource handling ===
    resource_count = 0
    try:
        # 1. Validate resources exist
        resource_result = validate_resources(
            input_file=file_path,
            questions=questions,
            media_dir=None,  # Auto-detect
            strict=False
        )

        # Log warnings but continue
        if resource_result.get("warning_count", 0) > 0:
            for issue in resource_result.get("issues", []):
                if issue.get("level") == "WARNING":
                    if session:
                        log_action(session.project_path, "step4_export",
                                   f"Resource warning: {issue.get('message')}")

        # Fail on errors
        if resource_result.get("error_count", 0) > 0:
            error_msgs = [i.get("message") for i in resource_result.get("issues", [])
                         if i.get("level") == "ERROR"]
            return [TextContent(
                type="text",
                text=f"Resource-fel:\n" + "\n".join(f"  - {m}" for m in error_msgs) +
                     "\n\nFixa bilderna och kor igen."
            )]

        # 2. Determine output folder for resources
        output_folder = session.output_folder if session else Path(output_path).parent

        # 3. Copy resources to output
        copy_result = copy_resources(
            input_file=file_path,
            output_dir=str(output_folder),
            questions=questions
        )
        resource_count = copy_result.get("count", 0)

    except ResourceError as e:
        # Log but don't fail - resources might not exist
        if session:
            log_action(session.project_path, "step4_export",
                       f"Resource handling skipped: {e}")

    # Generate XML
    xml_list = generate_all_xml(questions, language)

    # Add questions to metadata for packager (needed for labels export)
    metadata['questions'] = questions

    # Create package
    result = create_qti_package(xml_list, metadata, output_path)

    # Log export to session if active
    if session:
        try:
            relative_output = str(Path(output_path).relative_to(session.project_path))
        except ValueError:
            relative_output = output_path
        session.log_export(relative_output, len(questions))

        zip_path = Path(result.get('zip_path', output_path))
        log_action(
            session.project_path,
            "step4_export",
            f"Exported {len(questions)} questions, {resource_count} resources to {zip_path.name}",
            data={
                "question_count": len(questions),
                "resource_count": resource_count,
                "output_file": str(zip_path),
                "file_size_bytes": zip_path.stat().st_size if zip_path.exists() else 0,
            }
        )

    return [TextContent(
        type="text",
        text=f"QTI-paket skapat!\n"
             f"  ZIP: {result.get('zip_path')}\n"
             f"  Mapp: {result.get('folder_path')}\n"
             f"  Fragor: {len(questions)}\n"
             f"  Resurser: {resource_count} filer kopierade"
    )]


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
# Step 1: Guided Build (v6.3 → v6.5)
# =============================================================================

async def handle_step1_start(arguments: dict) -> List[TextContent]:
    """Handle step1_start - start guided build session.

    Uses Step 0 session if active, otherwise requires source_file and output_folder.
    """
    result = await step1_start(
        source_file=arguments.get("source_file"),
        output_folder=arguments.get("output_folder"),
        project_name=arguments.get("project_name")
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
    result = await step1_analyze(arguments.get("question_id"))

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    return [TextContent(
        type="text",
        text=f"Analys: {result['question_id']} ({result['question_type']})\n\n"
             f"Problem: {result['total_issues']} "
             f"(kritiska: {result['by_severity']['critical']}, "
             f"varningar: {result['by_severity']['warning']})\n"
             f"Auto-fixbara: {result['auto_fixable']}\n\n"
             f"{result['issues_summary']}"
    )]


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
    result = await step1_fix_auto(arguments.get("question_id"))

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    # Log to pipeline
    session = get_current_session()
    if session and result.get("fixed"):
        log_action(
            session.project_path,
            "step1_fix_auto",
            f"Auto-fixed {result['fixed_count']} issues on {result['question_id']}",
            data={
                "question_id": result['question_id'],
                "fixed_count": result['fixed_count'],
                "remaining_count": result['remaining_count'],
            }
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


async def handle_step1_fix_manual(arguments: dict) -> List[TextContent]:
    """Handle step1_fix_manual - apply single manual fix."""
    question_id = arguments.get("question_id")
    field = arguments.get("field")
    value = arguments.get("value")

    if not question_id or not field or not value:
        return [TextContent(type="text", text="Error: question_id, field och value krävs")]

    result = await step1_fix_manual(question_id, field, value)

    if result.get("error"):
        return [TextContent(type="text", text=f"Error: {result['error']}")]

    # Log to pipeline
    session = get_current_session()
    if session and result.get("success"):
        log_action(
            session.project_path,
            "step1_fix_manual",
            f"Manual fix: {field}={value} on {question_id}",
            data={
                "question_id": question_id,
                "field": field,
                "value": value[:50] if len(value) > 50 else value,
            }
        )

    return [TextContent(
        type="text",
        text=result.get("message", "")
    )]


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
