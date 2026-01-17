# RFC-001: Unified Logging for QuestionForge

| Field | Value |
|-------|-------|
| **Status** | Implemented |
| **Created** | 2026-01-16 |
| **Updated** | 2026-01-17 |
| **Author** | Niklas Karlsson |
| **Relates to** | qf-pipeline, qf-scaffolding, qti-core |

## Implementation Status

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Python Logger | ✅ Complete | `logger.py` updated, tested |
| Phase 2: TypeScript Logger | ✅ Complete | `logger.ts` created, load_stage integrated |
| Phase 3: Schema Validation | ✅ Complete | `qf-specifications/logging/schema.json` |

## Summary

This RFC proposes a unified logging system for all QuestionForge packages. The system uses a single JSON log file per project (`session.jsonl`) with a standardized schema, designed to support:

1. **Debugging** - Trace why operations failed
2. **Session resumption** - Know where work stopped
3. **Audit trail** - Track M1-M4 stages and user decisions
4. **Future ML training** - Structured data for machine learning

## Motivation

### Current Problems

The current logging implementation has several issues:

1. **Multiple redundant files** - `log_event()` writes to THREE files:
   - `logs/session.jsonl` (shared)
   - `logs/qf-pipeline.jsonl` (duplicate!)
   - `logs/session.log` (human-readable)

2. **Inconsistent naming** - Old projects have `pipeline.jsonl` at root, new ones use `logs/session.jsonl`

3. **qf-scaffolding has no logging** - M1-M4 module activities are not logged at all

4. **No schema validation** - JSON structure varies between calls

5. **Bug-prone API** - `log_action()` crashed when `data` dict contained `project_path` key (fixed in commit TBD)

### Requirements

| Requirement | Priority | Notes |
|-------------|----------|-------|
| Single log file per project | Must | `logs/session.jsonl` |
| Works for Python + TypeScript | Must | Shared schema |
| Session resumption support | Must | Know current state |
| User decision tracking | Must | For ML training |
| Deep error logging | Must | Stacktrace + context |
| PostgreSQL-ready schema | Should | Future migration |
| Log rotation | Could | For long-running systems |

## Design

### 1. Log File Structure

Each project has ONE log file:

```
project/
└── logs/
    └── session.jsonl    ← All events from all MCPs
```

**Removed:**
- `logs/qf-pipeline.jsonl` (redundant)
- `logs/qf-scaffolding.jsonl` (never implemented)
- `logs/session.log` (JSON is sufficient)
- `pipeline.jsonl` at root (legacy)
- `pipeline.log` at root (legacy)

### 2. JSON Schema

Every log entry follows this schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["ts", "v", "session_id", "mcp", "tool", "event", "level"],
  "properties": {
    "ts": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp in UTC with Z suffix"
    },
    "v": {
      "type": "integer",
      "const": 1,
      "description": "Schema version for future compatibility"
    },
    "session_id": {
      "type": "string",
      "format": "uuid",
      "description": "Links all events in a session"
    },
    "mcp": {
      "type": "string",
      "enum": ["qf-pipeline", "qf-scaffolding", "qti-core"],
      "description": "Which package generated this event"
    },
    "tool": {
      "type": "string",
      "description": "Tool or function name (e.g., step2_validate, load_stage)"
    },
    "event": {
      "type": "string",
      "description": "Event type (see Event Types section)"
    },
    "level": {
      "type": "string",
      "enum": ["debug", "info", "warn", "error"],
      "description": "Log level"
    },
    "data": {
      "type": "object",
      "description": "Event-specific structured data"
    },
    "duration_ms": {
      "type": "integer",
      "description": "Operation duration in milliseconds"
    },
    "parent_id": {
      "type": "string",
      "description": "Links to parent event for hierarchical logging"
    }
  }
}
```

### 3. Event Types

#### Session Events

| Event | When | Data |
|-------|------|------|
| `session_start` | New session created | `{entry_point, source_file}` |
| `session_resume` | Existing session loaded | `{previous_state}` |
| `session_end` | Session completed/closed | `{summary}` |

#### Tool Events (qf-pipeline)

| Event | When | Data |
|-------|------|------|
| `tool_start` | Tool begins execution | `{arguments}` |
| `tool_end` | Tool completes | `{result, success}` |
| `tool_progress` | Long operation update | `{percent, current, total}` |
| `tool_error` | Error occurred | `{error_type, message, stacktrace, input_context}` |

#### Module Events (qf-scaffolding)

| Event | When | Data |
|-------|------|------|
| `stage_start` | M1-M4 stage begins | `{module, stage, stage_name}` |
| `stage_complete` | Stage approved by user | `{module, stage, outputs}` |
| `stage_skip` | Stage skipped | `{module, stage, reason}` |
| `user_decision` | User made a choice | `{decision_type, options, choice, rationale}` |

#### Validation Events (qti-core)

| Event | When | Data |
|-------|------|------|
| `file_parsed` | Source file read | `{path, lines, questions_found}` |
| `question_validated` | Single question checked | `{question_id, valid, errors, warnings}` |
| `validation_summary` | Batch complete | `{total, valid, invalid, errors}` |
| `export_complete` | QTI package created | `{output_path, questions, format}` |

#### User Interaction Events

| Event | When | Data |
|-------|------|------|
| `user_input` | User provided text | `{prompt_type, input_length}` |
| `user_decision` | User selected option | `{decision_type, options_presented, user_choice}` |
| `user_edit` | User modified content | `{content_type, before_length, after_length}` |

### 4. Error Logging (Deep)

Errors include full context for debugging:

```json
{
  "ts": "2026-01-16T23:05:00.123Z",
  "v": 1,
  "session_id": "abc-123-def",
  "mcp": "qf-pipeline",
  "tool": "step2_validate",
  "event": "tool_error",
  "level": "error",
  "data": {
    "error_type": "ValidationError",
    "error_message": "Invalid question format at line 45",
    "stacktrace": "Traceback (most recent call last):\n  File \"validator.py\", line 123...",
    "input_context": {
      "file": "/path/to/questions.md",
      "line_number": 45,
      "line_content": "## Fråga 5",
      "surrounding_lines": ["", "## Fråga 5", "Typ: multiple_choce", ""]
    },
    "system_state": {
      "questions_processed": 4,
      "current_question_id": "Q5",
      "validation_mode": "strict"
    },
    "environment": {
      "python_version": "3.12.0",
      "qf_pipeline_version": "0.1.0",
      "os": "darwin"
    }
  }
}
```

### 5. Implementation

#### Python (qf-pipeline, qti-core)

Location: `packages/qf-pipeline/src/qf_pipeline/utils/logger.py`

```python
from typing import Optional, Any
from pathlib import Path
from datetime import datetime, timezone
import json
import fcntl

SCHEMA_VERSION = 1

def log_event(
    project_path: Path,
    session_id: str,
    mcp: str,
    tool: str,
    event: str,
    level: str = "info",
    data: Optional[dict] = None,
    duration_ms: Optional[int] = None,
    parent_id: Optional[str] = None
) -> None:
    """Log event to session.jsonl."""
    if project_path is None:
        return

    logs_dir = Path(project_path) / "logs"
    logs_dir.mkdir(exist_ok=True)

    entry = {
        "ts": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "v": SCHEMA_VERSION,
        "session_id": session_id,
        "mcp": mcp,
        "tool": tool,
        "event": event,
        "level": level,
    }

    if data:
        entry["data"] = data
    if duration_ms is not None:
        entry["duration_ms"] = duration_ms
    if parent_id:
        entry["parent_id"] = parent_id

    log_file = logs_dir / "session.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
```

#### TypeScript (qf-scaffolding)

Location: `packages/qf-scaffolding/src/utils/logger.ts`

```typescript
import * as fs from 'fs';
import * as path from 'path';

const SCHEMA_VERSION = 1;

interface LogEvent {
  ts: string;
  v: number;
  session_id: string;
  mcp: string;
  tool: string;
  event: string;
  level: 'debug' | 'info' | 'warn' | 'error';
  data?: Record<string, unknown>;
  duration_ms?: number;
  parent_id?: string;
}

export function logEvent(
  projectPath: string,
  sessionId: string,
  tool: string,
  event: string,
  level: LogEvent['level'] = 'info',
  data?: Record<string, unknown>,
  durationMs?: number,
  parentId?: string
): void {
  const logsDir = path.join(projectPath, 'logs');
  fs.mkdirSync(logsDir, { recursive: true });

  const entry: LogEvent = {
    ts: new Date().toISOString(),
    v: SCHEMA_VERSION,
    session_id: sessionId,
    mcp: 'qf-scaffolding',
    tool,
    event,
    level,
  };

  if (data) entry.data = data;
  if (durationMs !== undefined) entry.duration_ms = durationMs;
  if (parentId) entry.parent_id = parentId;

  const logFile = path.join(logsDir, 'session.jsonl');
  fs.appendFileSync(logFile, JSON.stringify(entry) + '\n', 'utf-8');
}
```

### 6. Future: PostgreSQL Migration

The JSON schema is designed to map directly to a SQL table:

```sql
CREATE TABLE log_events (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL,
    v INTEGER NOT NULL DEFAULT 1,
    session_id UUID NOT NULL,
    mcp VARCHAR(50) NOT NULL,
    tool VARCHAR(100) NOT NULL,
    event VARCHAR(100) NOT NULL,
    level VARCHAR(10) NOT NULL,
    data JSONB,
    duration_ms INTEGER,
    parent_id BIGINT REFERENCES log_events(id),

    -- Indexes for common queries
    INDEX idx_session (session_id),
    INDEX idx_ts (ts),
    INDEX idx_mcp_tool (mcp, tool),
    INDEX idx_event (event),
    INDEX idx_level (level),
    INDEX idx_data_gin (data) USING GIN
);

-- Import from JSONL
COPY log_events (ts, v, session_id, mcp, tool, event, level, data, duration_ms, parent_id)
FROM PROGRAM 'cat /path/to/session.jsonl | jq -c "[.ts, .v, .session_id, .mcp, .tool, .event, .level, .data, .duration_ms, .parent_id]"'
WITH (FORMAT csv);
```

### 7. Session State for Resumption

To support session resumption, the logger provides a helper:

```python
def get_session_state(project_path: Path) -> dict:
    """Read session.jsonl and determine current state."""
    log_file = project_path / "logs" / "session.jsonl"
    if not log_file.exists():
        return {"status": "no_session"}

    events = []
    with open(log_file) as f:
        for line in f:
            events.append(json.loads(line))

    # Find last completed stage/tool
    last_complete = None
    for e in reversed(events):
        if e["event"] in ("stage_complete", "tool_end") and e.get("data", {}).get("success"):
            last_complete = e
            break

    return {
        "status": "resumable",
        "total_events": len(events),
        "last_activity": events[-1]["ts"] if events else None,
        "last_complete": last_complete,
        "errors": [e for e in events if e["level"] == "error"]
    }
```

## Migration Plan

### Phase 1: Update Logger (Immediate) ✅ COMPLETE

1. ✅ Modify `logger.py` to:
   - ✅ Remove writes to `qf-pipeline.jsonl`
   - ✅ Remove writes to `session.log`
   - ✅ Add `session_id` and `v` fields
   - ✅ Update function signature

2. ✅ Update all `log_event()` calls in qf-pipeline

**Commit:** `64a27c8 feat: Implement RFC-001 unified logging`

### Phase 2: Add TypeScript Logger ✅ COMPLETE

1. ✅ Created `packages/qf-scaffolding/src/utils/logger.ts`
2. ✅ Integrated logging in `load_stage.ts` (optional project_path parameter)
3. ⬜ Log user decisions (to be added with decision tracking)

### Phase 3: Schema Validation ✅ COMPLETE

1. ✅ JSON Schema file: `qf-specifications/logging/schema.json`
2. ✅ Example files: `qf-specifications/logging/examples/*.json`
3. ✅ Event documentation: `qf-specifications/logging/events.md`

## Open Questions (Resolved)

1. **Log retention** - How long to keep logs?
   - **Decision:** No auto-delete. Logs stay with project indefinitely.
   - **Rationale:** Projects are self-contained; user manages cleanup.

2. **Log size limits** - Rotate when file exceeds X MB?
   - **Decision:** No rotation for now. Revisit if projects exceed 10MB logs.
   - **Rationale:** Typical sessions produce <1MB. Future PostgreSQL will handle scale.

3. **Sensitive data** - Should user decisions include actual content or just metadata?
   - **Decision:** Log full content for user decisions (needed for ML training).
   - **Rationale:** Logs are local to project, not shared externally.

4. **Performance** - Is synchronous file writing acceptable?
   - **Decision:** Synchronous is fine for now.
   - **Rationale:** Logging is infrequent (<100 events/session). Async adds complexity.

5. **Cross-platform** - `fcntl` is Unix-only. Need Windows support?
   - **Decision:** Unix-only for now (macOS/Linux).
   - **Rationale:** Primary users on macOS. Add Windows support if needed later.

## References

- [JSON Lines format](https://jsonlines.org/)
- [JSON Schema](https://json-schema.org/)
- [Structured Logging](https://www.structlog.org/)

## Changelog

| Date | Change |
|------|--------|
| 2026-01-16 | Initial draft |
| 2026-01-16 | Phase 1 implemented (Python logger) |
| 2026-01-16 | Phase 4 implemented (JSON Schema) |
| 2026-01-16 | Open Questions resolved |
| 2026-01-16 | Status: Draft → Partially Implemented |
| 2026-01-17 | Phase 2 implemented (TypeScript logger) |
| 2026-01-17 | Removed Phase 3 (migration), renumbered. Status → Implemented |
