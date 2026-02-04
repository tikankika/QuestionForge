# qf-pipeline

QuestionForge Pipeline MCP - validation and QTI export for Inspera.

## Setup

### Option 1: Using uv (Recommended)

```bash
# Install uv if not installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to package
cd packages/qf-pipeline

# Create virtual environment and install
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Test
pytest tests/ -v
```

### Option 2: Using Homebrew Python

```bash
# Install Python 3.11+
brew install python@3.11

# Use the new Python
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Test
pytest tests/ -v
```

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "qf-pipeline": {
      "command": "/path/to/packages/qf-pipeline/.venv/bin/python",
      "args": ["-m", "qf_pipeline.server"],
      "env": {
        "PYTHONPATH": "/path/to/packages/qf-pipeline/src"
      }
    }
  }
}
```

Replace `/path/to` with actual paths.

## MCP Tools

| Tool | Description |
|------|-------------|
| `export_questions` | Full pipeline: parse → generate → package |
| `validate_file` | Validate markdown file format |
| `validate_content` | Validate markdown string |
| `parse_markdown` | Parse markdown into structured data |
| `list_question_types` | List 15 supported question types |

## Testing Wrappers (without MCP)

The wrappers work independently of MCP:

```bash
cd packages/qf-pipeline
PYTHONPATH="src:$PYTHONPATH" python3 -m pytest tests/ -v
```

## Dependencies

- **QTI-Generator-for-Inspera**: Must exist at `/path/to/qti-generator`
- **Python**: 3.10+ recommended
- **mcp**: MCP SDK for Python

## Project Structure

```
qf-pipeline/
├── pyproject.toml
├── src/qf_pipeline/
│   ├── __init__.py
│   ├── server.py           # MCP server
│   └── wrappers/
│       ├── parser.py       # MarkdownQuizParser
│       ├── generator.py    # XMLGenerator
│       ├── packager.py     # QTIPackager
│       ├── validator.py    # validate_content
│       ├── resources.py    # ResourceManager
│       └── errors.py       # Custom exceptions
└── tests/
    └── test_wrappers.py
```

## License

CC BY-NC-SA 4.0 - See [LICENSE.md](../../LICENSE.md)
