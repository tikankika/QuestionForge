"""Session management for qf-pipeline.

Handles project structure creation, session state via session.yaml,
and workflow tracking.
"""

import shutil
import uuid
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def get_timestamp() -> str:
    """Generate ISO 8601 timestamp with Z suffix."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


class SessionManager:
    """Manages QF pipeline sessions with project structure and state.

    Project structure:
        project_name/
        ├── 01_source/          ← Original (NEVER modified)
        │   └── original_file.md
        ├── 02_working/         ← Working copy (editable)
        │   └── original_file.md
        ├── 03_output/          ← Exported files
        │   └── (QTI packages, ZIP files)
        └── session.yaml        ← Metadata and state
    """

    FOLDERS = ["01_source", "02_working", "03_output"]
    SESSION_FILE = "session.yaml"

    def __init__(self, project_path: Optional[Path] = None):
        """Initialize session manager.

        Args:
            project_path: Path to existing project (for loading session)
        """
        self._project_path: Optional[Path] = project_path
        self._session_data: Optional[dict] = None

        if project_path:
            self._load_session()

    @property
    def project_path(self) -> Optional[Path]:
        """Get current project path."""
        return self._project_path

    @property
    def session_id(self) -> Optional[str]:
        """Get current session ID."""
        if self._session_data:
            return self._session_data.get("session", {}).get("id")
        return None

    @property
    def working_file(self) -> Optional[Path]:
        """Get path to working file."""
        if self._project_path and self._session_data:
            working_path = self._session_data.get("working", {}).get("path")
            if working_path:
                return self._project_path / working_path
        return None

    @property
    def source_file(self) -> Optional[Path]:
        """Get path to source file copy."""
        if self._project_path and self._session_data:
            copied_to = self._session_data.get("source", {}).get("copied_to")
            if copied_to:
                return self._project_path / copied_to
        return None

    @property
    def output_folder(self) -> Optional[Path]:
        """Get path to output folder."""
        if self._project_path:
            return self._project_path / "03_output"
        return None

    def create_session(
        self,
        source_file: str,
        output_folder: str,
        project_name: Optional[str] = None
    ) -> dict:
        """Create a new session with project structure.

        Args:
            source_file: Absolute path to markdown file
            output_folder: Directory where project will be created
            project_name: Optional project name (auto-generated from filename if None)

        Returns:
            dict with success status and paths
        """
        source_path = Path(source_file).resolve()
        output_base = Path(output_folder).resolve()

        # Validate source file
        if not source_path.exists():
            return {
                "success": False,
                "error": {
                    "type": "file_not_found",
                    "message": f"Source file not found: {source_file}"
                }
            }

        if not source_path.is_file():
            return {
                "success": False,
                "error": {
                    "type": "invalid_path",
                    "message": f"Source path is not a file: {source_file}"
                }
            }

        # Generate project name if not provided
        if not project_name:
            project_name = source_path.stem  # filename without extension

        # Create project directory
        project_path = output_base / project_name

        try:
            # Create output base if needed
            output_base.mkdir(parents=True, exist_ok=True)

            # Create project structure
            project_path.mkdir(parents=True, exist_ok=True)
            for folder in self.FOLDERS:
                (project_path / folder).mkdir(exist_ok=True)

            # Copy source file
            source_dest = project_path / "01_source" / source_path.name
            shutil.copy2(source_path, source_dest)

            # Create working copy
            working_dest = project_path / "02_working" / source_path.name
            shutil.copy2(source_path, working_dest)

            # Generate session ID
            session_id = str(uuid.uuid4())

            # Create session data
            self._session_data = {
                "session": {
                    "id": session_id,
                    "created": get_timestamp(),
                    "updated": get_timestamp(),
                },
                "source": {
                    "original_path": str(source_path),
                    "filename": source_path.name,
                    "copied_to": f"01_source/{source_path.name}",
                },
                "working": {
                    "path": f"02_working/{source_path.name}",
                    "last_validated": None,
                    "validation_status": "not_validated",
                    "question_count": None,
                },
                "exports": []
            }

            self._project_path = project_path
            self._save_session()

            return {
                "success": True,
                "session_id": session_id,
                "project_path": str(project_path),
                "working_file": str(working_dest),
                "source_file": str(source_dest),
                "output_folder": str(project_path / "03_output"),
                "message": f"Session startad. Arbetar med: {source_path.name}"
            }

        except PermissionError as e:
            return {
                "success": False,
                "error": {
                    "type": "permission_error",
                    "message": f"Cannot write to directory: {e}"
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

    def get_status(self) -> dict:
        """Get current session status.

        Returns:
            dict with session status and paths
        """
        if not self._session_data or not self._project_path:
            return {
                "active": False,
                "message": "No active session"
            }

        working_data = self._session_data.get("working", {})
        exports = self._session_data.get("exports", [])

        return {
            "active": True,
            "session_id": self.session_id,
            "project_path": str(self._project_path),
            "working_file": str(self.working_file) if self.working_file else None,
            "validation_status": working_data.get("validation_status", "not_validated"),
            "question_count": working_data.get("question_count"),
            "last_validated": working_data.get("last_validated"),
            "last_export": exports[-1].get("output_file") if exports else None,
            "export_count": len(exports)
        }

    def update_validation(self, is_valid: bool, question_count: int) -> None:
        """Update validation status in session.

        Args:
            is_valid: Whether validation passed
            question_count: Number of questions found
        """
        if self._session_data:
            self._session_data["working"]["last_validated"] = get_timestamp()
            self._session_data["working"]["validation_status"] = "valid" if is_valid else "invalid"
            self._session_data["working"]["question_count"] = question_count
            self._session_data["session"]["updated"] = get_timestamp()
            self._save_session()

    def log_export(self, output_file: str, questions_exported: int) -> None:
        """Log an export to session.

        Args:
            output_file: Path to exported file (relative to project)
            questions_exported: Number of questions exported
        """
        if self._session_data:
            self._session_data["exports"].append({
                "timestamp": get_timestamp(),
                "output_file": output_file,
                "questions_exported": questions_exported
            })
            self._session_data["session"]["updated"] = get_timestamp()
            self._save_session()

    def end_session(self) -> dict:
        """End current session.

        Returns:
            dict with session summary
        """
        if not self._session_data or not self._project_path:
            return {
                "success": False,
                "error": {
                    "type": "no_session",
                    "message": "No active session to end"
                }
            }

        exports = self._session_data.get("exports", [])
        project_path = str(self._project_path)

        # Clear session state
        self._session_data = None
        self._project_path = None

        return {
            "success": True,
            "exports_created": [e.get("output_file") for e in exports],
            "project_path": project_path,
            "message": f"Session avslutad. {len(exports)} export(er) skapade."
        }

    def _load_session(self) -> None:
        """Load session data from session.yaml."""
        if not self._project_path:
            return

        session_file = self._project_path / self.SESSION_FILE
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                self._session_data = yaml.safe_load(f)

    def _save_session(self) -> None:
        """Save session data to session.yaml."""
        if not self._project_path or not self._session_data:
            return

        session_file = self._project_path / self.SESSION_FILE
        with open(session_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(
                self._session_data,
                f,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False
            )

    @classmethod
    def load_from_path(cls, project_path: str) -> "SessionManager":
        """Load session from existing project path.

        Args:
            project_path: Path to project directory

        Returns:
            SessionManager instance with loaded session
        """
        path = Path(project_path).resolve()
        if not (path / cls.SESSION_FILE).exists():
            raise FileNotFoundError(f"No session found at {project_path}")
        return cls(path)
