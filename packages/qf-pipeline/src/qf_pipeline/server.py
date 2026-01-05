"""QuestionForge Pipeline MCP Server.

Provides tools for validating markdown questions and exporting to QTI format.
"""

import asyncio
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

# Create server instance
server = Server("qf-pipeline")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="export_questions",
            description="Parse markdown, generate QTI XML, and create package",
            inputSchema={
                "type": "object",
                "properties": {
                    "markdown_path": {
                        "type": "string",
                        "description": "Path to markdown file with questions",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path for output ZIP file",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code (sv/en)",
                        "default": "sv",
                    },
                },
                "required": ["markdown_path", "output_path"],
            },
        ),
        Tool(
            name="validate_file",
            description="Validate markdown file format",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to markdown file to validate",
                    },
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="validate_content",
            description="Validate markdown content string",
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
            name="parse_markdown",
            description="Parse markdown into structured question data",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Markdown content to parse",
                    },
                },
                "required": ["content"],
            },
        ),
        Tool(
            name="list_question_types",
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
        if name == "export_questions":
            return await handle_export_questions(arguments)
        elif name == "validate_file":
            return await handle_validate_file(arguments)
        elif name == "validate_content":
            return await handle_validate_content(arguments)
        elif name == "parse_markdown":
            return await handle_parse_markdown(arguments)
        elif name == "list_question_types":
            return await handle_list_question_types()
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except WrapperError as e:
        return [TextContent(type="text", text=f"Error: {e}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {e}")]


async def handle_export_questions(arguments: dict) -> List[TextContent]:
    """Handle export_questions tool call."""
    markdown_path = arguments["markdown_path"]
    output_path = arguments["output_path"]
    language = arguments.get("language", "sv")

    # Parse markdown
    data = parse_file(markdown_path)
    questions = data.get("questions", [])
    metadata = data.get("metadata", {})

    if not questions:
        return [TextContent(type="text", text="No questions found in file")]

    # Generate XML
    xml_list = generate_all_xml(questions, language)

    # Create package
    result = create_qti_package(xml_list, metadata, output_path)

    return [
        TextContent(
            type="text",
            text=f"Created QTI package:\n"
            f"  ZIP: {result.get('zip_path')}\n"
            f"  Folder: {result.get('folder_path')}\n"
            f"  Questions: {len(questions)}",
        )
    ]


async def handle_validate_file(arguments: dict) -> List[TextContent]:
    """Handle validate_file tool call."""
    result = validate_file(arguments["file_path"])

    if result["valid"]:
        return [TextContent(type="text", text=f"Valid: {arguments['file_path']}")]

    issues_text = "\n".join(
        f"  [{i['level']}] {i['message']} (line {i.get('line_num', '?')})"
        for i in result["issues"]
    )
    return [
        TextContent(
            type="text",
            text=f"Invalid: {arguments['file_path']}\n{issues_text}",
        )
    ]


async def handle_validate_content(arguments: dict) -> List[TextContent]:
    """Handle validate_content tool call."""
    result = validate_markdown(arguments["content"])

    if result["valid"]:
        return [TextContent(type="text", text="Content is valid")]

    issues_text = "\n".join(
        f"  [{i['level']}] {i['message']}" for i in result["issues"]
    )
    return [TextContent(type="text", text=f"Invalid content:\n{issues_text}")]


async def handle_parse_markdown(arguments: dict) -> List[TextContent]:
    """Handle parse_markdown tool call."""
    import json

    result = parse_markdown(arguments["content"])
    questions = result.get("questions", [])

    summary = f"Parsed {len(questions)} question(s)\n"
    for i, q in enumerate(questions, 1):
        q_type = q.get("type", "unknown")
        q_id = q.get("identifier", f"Q{i}")
        summary += f"  {i}. [{q_type}] {q_id}\n"

    return [TextContent(type="text", text=summary)]


async def handle_list_question_types() -> List[TextContent]:
    """Handle list_question_types tool call."""
    types = get_supported_types()
    return [
        TextContent(
            type="text",
            text=f"Supported question types ({len(types)}):\n"
            + "\n".join(f"  - {t}" for t in types),
        )
    ]


def main():
    """Run the MCP server."""
    asyncio.run(stdio_server(server))


if __name__ == "__main__":
    main()
