# CourseExtractor MCP Server

Minimal MCP server for extracting text and images from PDF course materials.

## Platform Support

**Supported:**
- macOS (tested on 10.15+)
- Linux (Ubuntu 20.04+, Debian, Fedora, etc.)

**NOT Supported:**
- **Windows** (uses Unix signal handling)

**Windows Users:** Run in WSL2, use Docker, or use MarkItDown alternative.

## Why Unix-only?

Uses `signal.SIGALRM` for timeout enforcement, which is not available on Windows.
Threading-based alternatives cannot kill threads in Python, making them unsuitable
for production use (threads continue running indefinitely).

## Features

- Extract text from PDF (preserves layout)
- Extract images from PDF (saves to disk)
- Production-ready security (timeout, whitelist, encryption check)
- Swedish error messages
- Simple, focused, robust

## Installation

### Prerequisites

```bash
# Verify platform
uname  # Should show: Darwin (macOS) or Linux

# Python 3.11+
python --version

# pip
pip --version
```

### Setup

```bash
# Clone or download
cd course-extractor-mcp

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # macOS/Linux only

# Install dependencies
pip install -r requirements.txt
```

### Configure Allowed Output Paths

Edit `server.py` and find `ALLOWED_OUTPUT_ROOTS`:

```python
ALLOWED_OUTPUT_ROOTS = [
    Path("/tmp"),
    Path.home() / "course_extractor",
    # ADD YOUR PATHS:
    Path("/Users/yourusername/Nextcloud/Courses"),
]
```

### Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "course-extractor": {
      "command": "python",
      "args": ["/absolute/path/to/course-extractor-mcp/server.py"]
    }
  }
}
```

Restart Claude Desktop.

## Usage

In Claude Desktop:

```
Extract content from /path/to/course.pdf
```

Claude will use the `extract_pdf` tool and return:
- Text as Markdown
- List of extracted images (with paths)
- Metadata (pages, title, author)

## Security

- Input validation (file exists, is PDF, < 100MB)
- Output path whitelist (prevents path traversal)
- Timeout (60s max per PDF, Unix signal)
- Encrypted PDF detection

## Development

Run tests:

```bash
pytest tests/ -v
```

## License

AGPL 3.0 (due to PyMuPDF dependency)

### Does this affect QuestionForge?

**NO.** AGPL does NOT infect QuestionForge because:
- CourseExtractor runs as separate MCP server
- Communication via STDIO/JSON-RPC (not import/linking)
- AGPL "aggregation" exception applies
- QuestionForge retains its own license

## Credits

Based on RFC-001-CourseExtractor-MCP-v4.2-FINAL.md
Code reviewed by Claude Code (13 issues total, all fixed)
Platform decision: Unix-only for MVP simplicity
