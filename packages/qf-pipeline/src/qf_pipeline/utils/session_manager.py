"""Session management for qf-pipeline.

Handles project structure creation, session state via session.yaml,
and workflow tracking.
"""

import logging
import shutil
import uuid
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .methodology import copy_methodology
from .sources import create_empty_sources_yaml, update_sources_yaml
from .logger import log_event

logger = logging.getLogger(__name__)


# Entry point configuration for shared session
# Named after the module they start with (M1-M4) or "pipeline" for direct export
ENTRY_POINT_REQUIREMENTS = {
    "m1": {
        "requires_source_file": False,
        "next_module": "m1",
        "description": "Börja från undervisningsmaterial → Content Analysis",
        "next_steps": ["M1", "M2", "M3", "M4", "Pipeline"],
        "skips": []
    },
    "m2": {
        "requires_source_file": True,
        "next_module": "m2",
        "description": "Börja från lärandemål → Assessment Planning",
        "next_steps": ["M2", "M3", "M4", "Pipeline"],
        "skips": ["M1"]
    },
    "m3": {
        "requires_source_file": True,
        "next_module": "m3",
        "description": "Börja från blueprint → Question Generation",
        "next_steps": ["M3", "M4", "Pipeline"],
        "skips": ["M1", "M2"]
    },
    "m4": {
        "requires_source_file": True,
        "next_module": "m4",
        "description": "Börja från frågor för QA → Quality Assurance",
        "next_steps": ["M4", "Pipeline"],
        "skips": ["M1", "M2", "M3"]
    },
    "pipeline": {
        "requires_source_file": True,
        "next_module": None,  # → Pipeline direkt
        "description": "Validera och exportera färdiga frågor direkt",
        "next_steps": ["Step1", "Step2", "Step3", "Step4"],
        "skips": ["M1", "M2", "M3", "M4"]
    }
}


def validate_entry_point(
    entry_point: str,
    source_file: Optional[str],
    materials_folder: Optional[str] = None
) -> None:
    """Validate entry point and source_file/materials_folder combination.

    Args:
        entry_point: One of "m1", "m2", "m3", "m4", "pipeline"
        source_file: Path to source file (required for m2/m3/m4/pipeline)
        materials_folder: Path to materials folder (required for m1)

    Raises:
        ValueError: If entry_point is invalid or requirements not met
    """
    if entry_point not in ENTRY_POINT_REQUIREMENTS:
        valid_options = list(ENTRY_POINT_REQUIREMENTS.keys())
        raise ValueError(
            f"Invalid entry point: '{entry_point}'. "
            f"Valid options: {valid_options}"
        )

    config = ENTRY_POINT_REQUIREMENTS[entry_point]

    # m1 requires materials_folder
    if entry_point == "m1":
        if not materials_folder:
            raise ValueError(
                f"Entry point 'm1' requires materials_folder.\n"
                f"Description: {config['description']}\n"
                f"Expected workflow: {' → '.join(config['next_steps'])}"
            )
        if source_file:
            logger.warning(
                f"source_file provided for 'm1' entry point - "
                f"will be ignored. Use materials_folder instead."
            )
    # Other entry points require source_file
    elif config["requires_source_file"] and not source_file:
        raise ValueError(
            f"Entry point '{entry_point}' requires source_file.\n"
            f"Description: {config['description']}\n"
            f"Expected workflow: {' → '.join(config['next_steps'])}"
        )

    # Warn if materials_folder provided for non-m1
    if materials_folder and entry_point != "m1":
        logger.warning(
            f"materials_folder provided for '{entry_point}' entry point - "
            f"will be ignored. This parameter is only used for 'm1'."
        )


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

    FOLDERS = [
        "00_materials",    # For entry point A (materials)
        "01_source",       # Original source file (entry point B/C/D)
        "02_working",      # Working copy during transformation
        "03_output",       # Exported QTI files
        "methodology",     # For M1-M4 methodology (copied from QuestionForge)
        "logs",            # Session logs (shared by both MCPs)
    ]
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
        output_folder: str,
        source_file: Optional[str] = None,
        project_name: Optional[str] = None,
        entry_point: str = "pipeline",
        materials_folder: Optional[str] = None,
        initial_sources: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create a new session with project structure.

        Args:
            output_folder: Directory where project will be created
            source_file: Path to source file (required for m2/m3/m4/pipeline)
            project_name: Optional project name (auto-generated if not provided)
            entry_point: One of "m1", "m2", "m3", "m4", "pipeline"
            materials_folder: Path to folder with instructional materials (required for m1)
            initial_sources: Optional list of initial sources for sources.yaml
                Each source should have: path, type (optional), location (optional)

        Returns:
            dict with success status, paths, and next_module
        """
        output_base = Path(output_folder).resolve()

        # Validate entry point and source_file/materials_folder combination
        try:
            validate_entry_point(entry_point, source_file, materials_folder)
        except ValueError as e:
            return {
                "success": False,
                "error": {
                    "type": "validation_error",
                    "message": str(e)
                }
            }

        # Get entry point config
        ep_config = ENTRY_POINT_REQUIREMENTS[entry_point]

        # Handle source file if provided
        source_path = None
        if source_file:
            source_path = Path(source_file).resolve()

            # Validate source file exists
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
            if source_path:
                project_name = source_path.stem  # filename without extension
            else:
                # For materials entry point, generate timestamp-based name
                project_name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create project directory
        # Avoid duplicate folders if output_folder already ends with project_name
        if output_base.name == project_name:
            project_path = output_base
        else:
            project_path = output_base / project_name

        try:
            # Create output base if needed
            output_base.mkdir(parents=True, exist_ok=True)

            # Create project structure
            project_path.mkdir(parents=True, exist_ok=True)
            for folder in self.FOLDERS:
                folder_path = project_path / folder
                folder_path.mkdir(exist_ok=True)

                # Add README for 00_materials folder ONLY if no materials_folder provided
                # (otherwise user's own README might be in materials_folder)
                if folder == "00_materials" and not materials_folder:
                    readme_path = folder_path / "README.md"
                    readme_path.write_text(
                        "# Undervisningsmaterial\n\n"
                        "Ladda upp allt material från din undervisning här:\n"
                        "- Presentationer (PDF, PPTX)\n"
                        "- Föreläsningsanteckningar\n"
                        "- Transkriptioner från inspelningar\n"
                        "- Läroböcker/artiklar som använts\n",
                        encoding="utf-8"
                    )

            # Copy materials if provided (for m1 entry point)
            materials_copied = 0
            if materials_folder:
                materials_src = Path(materials_folder)
                materials_dest = project_path / "00_materials"

                logger.info(f"Copying materials from {materials_src} to {materials_dest}")

                # Define junk files to ignore
                def ignore_junk(directory, files):
                    """Ignore junk files and hidden files."""
                    ignored = []
                    for f in files:
                        # Ignore hidden files (except .md files which might be intentional)
                        if f.startswith('.') and not f.endswith('.md'):
                            ignored.append(f)
                        # Ignore OS junk
                        elif f in ('Thumbs.db', 'desktop.ini', 'ehthumbs.db'):
                            ignored.append(f)
                        # Ignore Office temp files
                        elif f.startswith('~$'):
                            ignored.append(f)
                        # Ignore Python cache
                        elif f == '__pycache__' or f.endswith('.pyc'):
                            ignored.append(f)
                    return ignored

                # Copy entire tree (including subdirectories)
                shutil.copytree(
                    materials_src,
                    materials_dest,
                    dirs_exist_ok=True,  # Merge with existing (00_materials already exists)
                    ignore=ignore_junk
                )

                # Count files recursively for reporting
                for item in materials_dest.rglob('*'):
                    if item.is_file():
                        materials_copied += 1

                logger.info(f"Copied {materials_copied} files to 00_materials/")

            # Copy methodology from QuestionForge (makes project self-contained)
            methodology_result = copy_methodology(project_path)
            if not methodology_result["success"]:
                logger.warning(f"Could not copy methodology: {methodology_result.get('error')}")
            else:
                logger.info(f"Copied {methodology_result['files_copied']} methodology files")

            # Initialize sources.yaml
            if initial_sources:
                sources_result = update_sources_yaml(
                    project_path,
                    initial_sources,
                    updated_by="qf-pipeline:step0_start",
                    append=False
                )
                logger.info(f"Initialized sources.yaml with {sources_result.get('sources_added', 0)} sources")
            else:
                create_empty_sources_yaml(project_path, created_by="qf-pipeline:step0_start")
                logger.info("Created empty sources.yaml")

            # Copy source file if provided (entry points B/C/D)
            source_dest = None
            working_dest = None
            if source_path:
                source_dest = project_path / "01_source" / source_path.name
                shutil.copy2(source_path, source_dest)

                # Create working copy
                working_dest = project_path / "02_working" / source_path.name
                shutil.copy2(source_path, working_dest)

            # Generate session ID
            session_id = str(uuid.uuid4())

            # Create session data with methodology section
            self._session_data = {
                "session": {
                    "id": session_id,
                    "created": get_timestamp(),
                    "updated": get_timestamp(),
                },
                "source": {
                    "original_path": str(source_path) if source_path else None,
                    "filename": source_path.name if source_path else None,
                    "copied_to": f"01_source/{source_path.name}" if source_path else None,
                },
                "working": {
                    "path": f"02_working/{source_path.name}" if source_path else None,
                    "last_validated": None,
                    "validation_status": "not_validated",
                    "question_count": None,
                },
                "exports": [],
                # NEW: Methodology section for shared session
                "methodology": {
                    "entry_point": entry_point,
                    "active_module": ep_config["next_module"],
                    "m1": {"status": "not_started", "loaded_stages": [], "outputs": {}},
                    "m2": {"status": "not_started", "loaded_stages": [], "outputs": {}},
                    "m3": {"status": "not_started", "loaded_stages": [], "outputs": {}},
                    "m4": {"status": "not_started", "loaded_stages": [], "outputs": {}},
                }
            }

            self._project_path = project_path
            self._save_session()

            # Log session creation (RFC-001 compliant)
            log_event(
                project_path=project_path,
                session_id=session_id,
                tool="step0_start",
                event="session_start",
                level="info",
                data={"entry_point": entry_point}
            )
            log_event(
                project_path=project_path,
                session_id=session_id,
                tool="step0_start",
                event="session_created",
                level="info",
                data={
                    "methodology_files": methodology_result.get("files_copied", 0),
                    "sources_count": len(initial_sources) if initial_sources else 0,
                    "materials_copied": materials_copied
                }
            )

            # Build response
            response = {
                "success": True,
                "session_id": session_id,
                "project_path": str(project_path),
                "output_folder": str(project_path / "03_output"),
                "entry_point": entry_point,
                "next_module": ep_config["next_module"],
                "pipeline_ready": entry_point == "pipeline",
                "methodology_copied": methodology_result.get("files_copied", 0),
                "sources_initialized": len(initial_sources) if initial_sources else 0,
                "materials_copied": materials_copied,
            }

            # Add file paths if source was provided
            if source_path:
                response["working_file"] = str(working_dest)
                response["source_file"] = str(source_dest)
                response["message"] = f"Session startad. Arbetar med: {source_path.name}"
            elif materials_folder:
                # Materials folder provided (m1 entry point)
                response["working_file"] = None
                response["source_file"] = None
                response["materials_folder"] = str(project_path / "00_materials")
                response["message"] = (
                    f"Session startad med entry point '{entry_point}'. "
                    f"{materials_copied} filer kopierade till 00_materials/ (mappstruktur bevarad). "
                    f"Nästa steg: {ep_config['next_module']} (qf-scaffolding)"
                )
            else:
                response["working_file"] = None
                response["source_file"] = None
                response["message"] = (
                    f"Session startad med entry point '{entry_point}'. "
                    f"Nästa steg: {ep_config['next_module']} (qf-scaffolding)"
                )

            return response

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
