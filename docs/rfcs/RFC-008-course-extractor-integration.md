# RFC-008: Course Extractor MCP Integration

| Field | Value |
|-------|-------|
| Status | Draft |
| Created | 2026-01-20 |
| Author | Niklas Karlsson |
| Context | M1 PDF extraction needs images |
| Relates to | RFC-004, RFC-007 |

## Summary

Integrate `course-extractor-mcp` (Python) with QuestionForge M1 to extract text **and images** from PDF course materials.

## Problem

`read_materials.ts` uses `pdf-parse` which only extracts text. Course materials often contain diagrams, figures and tables that are important for creating good questions.

## Solution: Claude Orchestration

Two separate MCPs, Claude coordinates:

```
┌─────────────────────────────────────────────────────────┐
│  course-extractor-mcp (Python, AGPL)                    │
│  └── extract_pdf → text_markdown + images[]            │
└─────────────────────────────────────────────────────────┘
                          │
                    Claude reads
                    images (vision)
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  qf-scaffolding (TypeScript, MIT)                       │
│  └── M1 workflow with content from course-extractor    │
└─────────────────────────────────────────────────────────┘
```

## Why Separation?

1. **AGPL isolation**: course-extractor uses PyMuPDF (AGPL). Separate repo = no licence contamination.
2. **RFC-004 philosophy**: "Claude reads content, MCP handles project"
3. **Simplicity**: No MCP-to-MCP bridges needed

## M1 Workflow with Integration

```
Stage 0:
1. Teacher uploads PDF
2. Claude calls: course-extractor.extract_pdf(file_path)
   → Returns: { text_markdown, images: [{saved_path}] }
3. Claude reads images (multimodal vision)
4. Claude calls: qf-scaffolding.load_stage(stage=0)
5. Claude analyses content (text + image understanding)
6. Continue M1 workflow according to RFC-007 Option A
```

## Configuration

### Claude Desktop (claude_desktop_config.json)

```json
{
  "mcpServers": {
    "course-extractor": {
      "command": "python",
      "args": ["/path/to/course-extractor-mcp/server.py"]
    },
    "qf-scaffolding": {
      "command": "node",
      "args": ["/path/to/QuestionForge/packages/qf-scaffolding/dist/index.js"]
    }
  }
}
```

## Repos

| Repo | Licence | Purpose |
|------|---------|---------|
| `course-extractor-mcp` | AGPL 3.0 | PDF text+images |
| `QuestionForge` | MIT | Scaffolding + Pipeline |

## Implementation

**No code change required in qf-scaffolding.**

Only:
1. Document workflow in M1 instructions
2. Update Stage 0 prompt to mention course-extractor

## Verification

1. Start both MCPs
2. Upload PDF with images in Claude Desktop
3. Verify that Claude:
   - Calls extract_pdf first
   - Reads extracted images
   - Continues with M1 workflow

## Decision

- [x] Approved for implementation
