# ADR-006: Session Management for qf-pipeline

## Status
**Proposed** → Pending implementation

## Date
2026-01-05

## Context

qf-pipeline (QuestionForge pipeline MCP) was initially built with a focus on export functionality. During testing it was discovered that:

1. **File access missing** - The MCP server could not read files from the user's local filesystem
2. **No working copy** - The user could not edit files without affecting the original
3. **No project structure** - Export occurred without an organised folder structure

### Reference Implementation

Assessment_suite/pre-assessment-mcp has a proven pattern:
- `phase1_explore` - Scans and identifies files
- `phase1_setup` - Creates project structure, copies files

See: `/path/to/assessment-suite/packages/pre-assessment-mcp/src/pre_assessment_mcp/tools/`

## Decision

Implement session management in qf-pipeline with the following components:

### New Tool: `start_session`

```python
start_session(
    source_file: str,      # Path to markdown file
    output_folder: str,    # Where the project should be created
    project_name: str = None  # Optional, auto-generate from filename
) -> dict
```

**Returns:**
```json
{
  "success": true,
  "project_path": "/path/to/project",
  "working_file": "/path/to/project/02_working/file.md",
  "session_id": "uuid",
  "message": "Session started. Working with: file.md"
}
```

### Project Folder Structure

```
project_name/
├── 01_source/          ← Original (NEVER modified)
│   └── original_file.md
├── 02_working/         ← Working copy (can be edited)
│   └── original_file.md
├── 03_output/          ← Exported files
│   └── (QTI packages, ZIP files)
└── session.yaml        ← Metadata and state
```

### session.yaml Schema

```yaml
session:
  id: "uuid"
  created: "2026-01-05T23:30:00Z"
  updated: "2026-01-05T23:45:00Z"
  
source:
  original_path: "/Users/.../EXAMPLE_COURSE_Fys_v65_5.md"
  filename: "EXAMPLE_COURSE_Fys_v65_5.md"
  copied_to: "01_source/EXAMPLE_COURSE_Fys_v65_5.md"
  
working:
  path: "02_working/EXAMPLE_COURSE_Fys_v65_5.md"
  last_validated: "2026-01-05T23:35:00Z"
  validation_status: "valid"
  question_count: 27
  
exports:
  - timestamp: "2026-01-05T23:45:00Z"
    output_file: "03_output/EXAMPLE_COURSE_Fys_QTI.zip"
    questions_exported: 27
```

### Updates to Existing Tools

| Tool | Change |
|------|--------|
| `validate_file` | Accepts absolute path OR relative within session |
| `export_questions` | Writes to 03_output/ if session active |
| `parse_markdown` | Unchanged (already works) |

## Consequences

### Positive
- User can work with local files
- Original is always preserved (01_source)
- Working copy can be edited freely
- Clear separation: input → work → output
- Metadata tracks the session

### Negative
- Extra step: must start session before work
- More code to maintain
- Project folders created (uses disk space)

### Neutral
- Follows established pattern from pre-assessment-mcp
- Consistent with Assessment_suite architecture

## Alternatives Considered

### A: File reading only (no session)
- Simpler implementation
- But: no working copy, no structure
- **Rejected:** Too limited for production use

### B: In-memory work
- Read file → work in memory → export
- But: loses work on crash
- **Rejected:** Risky for larger projects

### C: Session management (chosen)
- Inspired by pre-assessment-mcp
- Proven pattern
- **Chosen:** Best balance between simplicity and functionality

## Implementation

### Files to Create/Update

```
packages/qf-pipeline/src/qf_pipeline/
├── tools/
│   └── session.py          ← NEW: start_session, get_session_status
├── utils/
│   └── session_manager.py  ← NEW: SessionManager class
└── server.py               ← UPDATE: register new tools
```

### Priority

Part of Phase 1.5 (after basic MCP works, before PostgreSQL logging)

## Related Documents

- [ADR-005: MCP Integration](ADR-005-mcp-integration.md)
- [qf-pipeline-spec.md](../specs/qf-pipeline-spec.md)
- [qf-logging-specification.md](../specs/qf-logging-specification.md) - Session logging integrates here later

---

*Documented 2026-01-05 as part of ACDM IMPLEMENT phase*
