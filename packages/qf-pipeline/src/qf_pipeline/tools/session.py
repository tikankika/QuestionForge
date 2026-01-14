"""Session management tools for qf-pipeline MCP.

Provides tools for creating and managing QF pipeline sessions.
"""

from pathlib import Path
from typing import Optional

from ..utils.session_manager import SessionManager


# Global session manager instance
_current_session: Optional[SessionManager] = None


def get_current_session() -> Optional[SessionManager]:
    """Get the current active session manager."""
    return _current_session


def set_current_session(session: Optional[SessionManager]) -> None:
    """Set the current active session manager."""
    global _current_session
    _current_session = session


async def start_session_tool(
    output_folder: str,
    source_file: Optional[str] = None,
    project_name: Optional[str] = None,
    entry_point: str = "questions"
) -> dict:
    """Start a new QF pipeline session.

    Creates project structure:
        project_name/
        ├── 00_materials/   ← Instructional materials (entry point A)
        ├── 01_source/      ← Original source file (never modified)
        ├── 02_working/     ← Working copy (editable)
        ├── 03_output/      ← Exported files
        ├── methodology/    ← M1-M4 methodology outputs
        └── session.yaml    ← Session metadata

    Args:
        output_folder: Directory where project will be created
        source_file: Path to source file (required for entry points B/C/D)
        project_name: Optional project name (auto-generated if not provided)
        entry_point: One of "materials" (A), "objectives" (B),
                    "blueprint" (C), "questions" (D). Default: "questions"

    Returns:
        dict with success status, paths, and next_module
    """
    global _current_session

    manager = SessionManager()
    result = manager.create_session(
        output_folder=output_folder,
        source_file=source_file,
        project_name=project_name,
        entry_point=entry_point
    )

    if result.get("success"):
        _current_session = manager

    return result


async def get_session_status_tool(session_id: Optional[str] = None) -> dict:
    """Get status of current or specified session.

    Args:
        session_id: Optional session ID (uses current session if None)

    Returns:
        dict with session status and paths
    """
    if _current_session:
        return _current_session.get_status()

    return {
        "active": False,
        "message": "No active session. Use start_session to begin."
    }


async def end_session_tool(session_id: Optional[str] = None) -> dict:
    """End current session.

    Args:
        session_id: Optional session ID (uses current session if None)

    Returns:
        dict with session summary
    """
    global _current_session

    if not _current_session:
        return {
            "success": False,
            "error": {
                "type": "no_session",
                "message": "No active session to end"
            }
        }

    result = _current_session.end_session()
    _current_session = None
    return result


async def load_session_tool(project_path: str) -> dict:
    """Load an existing session from project path.

    Args:
        project_path: Path to existing project directory

    Returns:
        dict with loaded session info
    """
    global _current_session

    try:
        manager = SessionManager.load_from_path(project_path)
        _current_session = manager
        return {
            "success": True,
            **manager.get_status(),
            "message": f"Session loaded from {project_path}"
        }
    except FileNotFoundError as e:
        return {
            "success": False,
            "error": {
                "type": "session_not_found",
                "message": str(e)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": type(e).__name__,
                "message": str(e)
            }
        }
