"""Pipeline logging utility.

All logging goes to logs/ folder (shared by qf-pipeline and qf-scaffolding).
"""

import fcntl
import json
from pathlib import Path
from datetime import datetime, timezone


def log_action(
    project_path: Path,
    step: str,
    message: str,
    data: dict = None
):
    """
    Log action to logs/ folder.

    This is a wrapper around log_event for backwards compatibility.
    All logs now go to logs/session.jsonl and logs/session.log.

    Args:
        project_path: Project directory containing log files
        step: Tool/step name (e.g., "step0_start", "step2_validate")
        message: Human-readable message
        data: Optional structured data for JSON log
    """
    # Delegate to log_event (consolidates all logging)
    # Filter out 'project_path' from data to avoid duplicate argument error
    safe_data = {k: v for k, v in (data or {}).items() if k != 'project_path'}
    log_event(
        project_path,
        event_type=message,
        tool=step,
        **safe_data
    )


def log_event(
    project_path: Path,
    event_type: str,
    tool: str = "unknown",
    **kwargs
) -> None:
    """Log event to logs/session.jsonl (append-only, thread-safe).

    This is the shared logging format used by both qf-pipeline and qf-scaffolding.

    Args:
        project_path: Project directory
        event_type: Event type (e.g., "session_start", "stage_loaded")
        tool: Tool name (e.g., "step0_start", "load_stage")
        **kwargs: Additional event data
    """
    import fcntl

    if project_path is None:
        return

    project_path = Path(project_path)
    logs_dir = project_path / "logs"
    logs_dir.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc)

    log_entry = {
        "ts": timestamp.isoformat().replace('+00:00', 'Z'),
        "mcp": "qf-pipeline",
        "tool": tool,
        "event": event_type,
        **kwargs
    }

    # Append to session.jsonl (shared log)
    session_log = logs_dir / "session.jsonl"
    with open(session_log, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

    # Also append to MCP-specific log
    mcp_log = logs_dir / "qf-pipeline.jsonl"
    with open(mcp_log, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

    # Human-readable log (simpler format)
    human_log = logs_dir / "session.log"
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    extra = " ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
    entry = f"{timestamp_str} [{tool}] {event_type} {extra}\n"
    with open(human_log, "a", encoding="utf-8") as f:
        f.write(entry)
