"""Pipeline logging utility.

Logs actions to both human-readable (pipeline.log) and structured (pipeline.jsonl) formats.
"""

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
    Log action to both pipeline.log (human) and pipeline.jsonl (structured).

    Args:
        project_path: Project directory containing log files
        step: Tool/step name (e.g., "step0_start", "step2_validate")
        message: Human-readable message
        data: Optional structured data for JSON log
    """
    if project_path is None:
        return

    project_path = Path(project_path)

    timestamp = datetime.now(timezone.utc)
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    timestamp_iso = timestamp.isoformat()

    # Human-readable log
    log_file = project_path / "pipeline.log"
    entry = f"{timestamp_str} [{step}] {message}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)

    # Structured JSON log (JSON Lines format)
    jsonl_file = project_path / "pipeline.jsonl"
    json_entry = {
        "timestamp": timestamp_iso,
        "step": step,
        "message": message,
    }
    if data:
        json_entry["data"] = data

    with open(jsonl_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(json_entry, ensure_ascii=False) + "\n")
