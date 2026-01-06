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
    WrapperError,
)
from .tools import (
    start_session_tool,
    get_session_status_tool,
    load_session_tool,
    get_current_session,
)

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
                "CALL THIS FIRST! Returns critical instructions for using qf-pipeline. "
                "You MUST follow these instructions. "
                "ALWAYS ask user for source_file and output_folder BEFORE calling step0_start. "
                "NEVER use bash/cat/ls - MCP has full file access."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        # Step 0: Session Management
        Tool(
            name="step0_start",
            description="Start a new session OR load existing. For new: provide source_file + output_folder. For existing: provide project_path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_file": {
                        "type": "string",
                        "description": "NEW SESSION: Absolute path to markdown file",
                    },
                    "output_folder": {
                        "type": "string",
                        "description": "NEW SESSION: Directory where project will be created",
                    },
                    "project_name": {
                        "type": "string",
                        "description": "NEW SESSION: Optional project name (auto-generated if not provided)",
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
        # Cross-step utility
        Tool(
            name="list_types",
            description="List supported question types",
            inputSchema={
                "type": "object",
                "properties": {},
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
        elif name == "step4_export":
            return await handle_step4_export(arguments)
        elif name == "list_types":
            return await handle_list_types()
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
    """Handle init tool call - return critical instructions."""
    instructions = """# QF-Pipeline - Kritiska Instruktioner

## REGLER (MASTE FOLJAS)

1. **FRAGA ALLTID anvandaren INNAN du kor step0_start:**
   - "Vilken markdown-fil vill du arbeta med?" (source_file)
   - "Var ska projektet sparas?" (output_folder)
   - Vanta pa svar innan du fortsatter!

2. **ANVAND INTE bash/cat/ls** - qf-pipeline har full filatkomst

3. **SAG ALDRIG "ladda upp filen"** - MCP kan lasa filer direkt

4. **FOLJ PIPELINE-ORDNINGEN:**
   - step0_start -> step2_validate -> step4_export
   - Validera ALLTID innan export!

## STANDARD WORKFLOW

1. User: "Anvand qf-pipeline" / "Exportera till QTI"
2. Claude: "Vilken markdown-fil vill du arbeta med?"
3. User: anger sokvag
4. Claude: "Var ska projektet sparas?"
5. User: anger output-mapp
6. Claude: [step0_start] -> Skapar session
7. Claude: [step2_validate] -> Validerar
8. Om valid: [step4_export] -> Exporterar
   Om invalid: Visa fel, hjalp anvandaren fixa

## TILLGANGLIGA VERKTYG

- init: CALL THIS FIRST (denna instruktion)
- step0_start: Starta ny session eller ladda befintlig
- step0_status: Visa sessionstatus
- step2_validate: Validera markdown-fil
- step2_validate_content: Validera markdown-innehall
- step4_export: Exportera till QTI-paket
- list_types: Lista stodda fragetyper (16 st)
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
            return [TextContent(
                type="text",
                text=f"Session laddad!\n"
                     f"  ID: {result['session_id']}\n"
                     f"  Projekt: {result['project_path']}\n"
                     f"  Arbetsfil: {result['working_file']}\n"
                     f"  Validering: {result['validation_status']}"
            )]
        else:
            error = result.get("error", {})
            return [TextContent(
                type="text",
                text=f"Kunde inte ladda session: {error.get('message')}"
            )]

    # Create new session
    if arguments.get("source_file"):
        if not arguments.get("output_folder"):
            return [TextContent(
                type="text",
                text="Error: output_folder kravs for ny session"
            )]

        result = await start_session_tool(
            source_file=arguments["source_file"],
            output_folder=arguments["output_folder"],
            project_name=arguments.get("project_name")
        )

        if result.get("success"):
            return [TextContent(
                type="text",
                text=f"Session startad!\n"
                     f"  Session ID: {result['session_id']}\n"
                     f"  Projekt: {result['project_path']}\n"
                     f"  Arbetsfil: {result['working_file']}\n"
                     f"  Output: {result['output_folder']}\n\n"
                     f"Nasta steg:\n"
                     f"  - step2_validate: Validera arbetsfilen\n"
                     f"  - step4_export: Exportera till QTI"
            )]
        else:
            error = result.get("error", {})
            return [TextContent(
                type="text",
                text=f"Kunde inte starta session:\n"
                     f"  Typ: {error.get('type')}\n"
                     f"  Meddelande: {error.get('message')}"
            )]

    # No valid arguments
    return [TextContent(
        type="text",
        text="Ange source_file + output_folder (ny session) eller project_path (ladda befintlig)"
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

    # Update session if active
    if session:
        session.update_validation(result["valid"], question_count)

    if result["valid"]:
        return [TextContent(
            type="text",
            text=f"Valid: {file_path}\n  Fragor: {question_count}"
        )]

    issues_text = "\n".join(
        f"  [{i['level']}] {i['message']} (rad {i.get('line_num', '?')})"
        for i in result["issues"]
    )
    return [TextContent(
        type="text",
        text=f"Invalid: {file_path}\n  Fragor: {question_count}\n{issues_text}"
    )]


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

    # Generate XML
    xml_list = generate_all_xml(questions, language)

    # Create package
    result = create_qti_package(xml_list, metadata, output_path)

    # Log export to session if active
    if session:
        try:
            relative_output = str(Path(output_path).relative_to(session.project_path))
        except ValueError:
            relative_output = output_path
        session.log_export(relative_output, len(questions))

    return [TextContent(
        type="text",
        text=f"QTI-paket skapat!\n"
             f"  ZIP: {result.get('zip_path')}\n"
             f"  Mapp: {result.get('folder_path')}\n"
             f"  Fragor: {len(questions)}"
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
