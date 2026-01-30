"""Step 0 tools for flexible project initialization (ADR-015).

Provides tools for:
- step0_add_file: Add files to existing project
- step0_analyze: Analyze project and recommend workflow
"""

import logging
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.session_manager import SessionManager, ENTRY_POINT_REQUIREMENTS
from ..utils.sources import update_sources_yaml
from ..utils.logger import log_event
from .session import get_current_session, set_current_session

logger = logging.getLogger(__name__)

# File type detection based on extension
FILE_TYPE_MAP = {
    # Questions/documents
    ".md": "markdown",
    ".markdown": "markdown",
    ".docx": "document",
    ".doc": "document",
    ".xlsx": "spreadsheet",
    ".xls": "spreadsheet",
    ".pdf": "pdf",
    ".txt": "text",
    # Resources
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".gif": "image",
    ".svg": "image",
    ".webp": "image",
    ".mp3": "audio",
    ".wav": "audio",
    ".ogg": "audio",
    ".m4a": "audio",
    ".mp4": "video",
    ".webm": "video",
}

# Extensions that are resources (go to questions/resources/)
RESOURCE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
                       ".mp3", ".wav", ".ogg", ".m4a", ".mp4", ".webm"}

# Extensions that need conversion via MarkItDown
CONVERTIBLE_EXTENSIONS = {".docx", ".doc", ".xlsx", ".xls", ".pdf", ".pptx", ".ppt"}


def detect_file_type(file_path: Path) -> str:
    """Detect file type based on extension."""
    ext = file_path.suffix.lower()
    return FILE_TYPE_MAP.get(ext, "unknown")


def is_resource_file(file_path: Path) -> bool:
    """Check if file is a resource (image/audio/video)."""
    return file_path.suffix.lower() in RESOURCE_EXTENSIONS


def needs_conversion(file_path: Path) -> bool:
    """Check if file needs conversion via MarkItDown."""
    return file_path.suffix.lower() in CONVERTIBLE_EXTENSIONS


async def step0_add_file(
    project_path: str,
    file_path: str,
    file_type: str = "auto",
    target_folder: str = "auto"
) -> Dict[str, Any]:
    """Add a file to an existing project (ADR-015).

    Can be called multiple times to add multiple files.

    Args:
        project_path: Path to project directory
        file_path: Path to file to add (local path)
        file_type: File type hint: "auto", "questions", "materials", "resources", "blueprint"
        target_folder: Target folder: "auto", "questions", "materials", "questions/resources"

    Returns:
        dict with success status, copied path, and recommendations
    """
    project = Path(project_path).resolve()
    source = Path(file_path).resolve()

    # Validate project exists
    if not project.exists():
        return {
            "success": False,
            "error": {
                "type": "project_not_found",
                "message": f"Projekt hittades inte: {project_path}"
            }
        }

    # Validate source file exists
    if not source.exists():
        return {
            "success": False,
            "error": {
                "type": "file_not_found",
                "message": f"Fil hittades inte: {file_path}"
            }
        }

    if not source.is_file():
        return {
            "success": False,
            "error": {
                "type": "not_a_file",
                "message": f"Sökvägen är inte en fil: {file_path}"
            }
        }

    # Determine target folder
    file_ext = source.suffix.lower()
    detected_type = detect_file_type(source)

    if target_folder == "auto":
        if is_resource_file(source):
            target_folder = "questions/resources"
        elif file_type in ("materials", "lecture", "slides"):
            target_folder = "materials"
        else:
            target_folder = "questions"

    # Create target folder if needed
    target_dir = project / target_folder
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy file
    dest_path = target_dir / source.name

    # Check for existing file
    if dest_path.exists():
        # Generate unique name
        counter = 1
        stem = source.stem
        while dest_path.exists():
            dest_path = target_dir / f"{stem}_{counter}{source.suffix}"
            counter += 1

    shutil.copy2(source, dest_path)

    # Determine relative path for sources.yaml
    relative_path = str(dest_path.relative_to(project))

    # Register in sources.yaml
    source_entry = {
        "path": relative_path,
        "type": file_type if file_type != "auto" else detected_type,
        "location": "local",
        "metadata": {
            "original_path": str(source),
            "added_by": "step0_add_file",
        }
    }

    # Update sources.yaml
    try:
        update_sources_yaml(
            project,
            [source_entry],
            updated_by="qf-pipeline:step0_add_file",
            append=True
        )
    except Exception as e:
        logger.warning(f"Could not update sources.yaml: {e}")

    # Load session if exists
    session = get_current_session()
    if session is None:
        try:
            session = SessionManager.load_from_path(project_path)
            set_current_session(session)
        except Exception:
            pass

    # Log event
    if session:
        log_event(
            project_path=project,
            session_id=session.session_id,
            tool="step0_add_file",
            event="file_added",
            level="info",
            data={
                "source": str(source),
                "destination": relative_path,
                "file_type": detected_type,
                "target_folder": target_folder,
            }
        )

    # Build response
    response = {
        "success": True,
        "file_added": {
            "original": str(source),
            "copied_to": relative_path,
            "file_type": detected_type,
            "target_folder": target_folder,
        },
        "needs_conversion": needs_conversion(source),
        "is_resource": is_resource_file(source),
    }

    # Add conversion hint
    if needs_conversion(source):
        response["conversion_hint"] = (
            f"⚠️ Filen '{source.name}' behöver konverteras till markdown.\n"
            f"Använd MarkItDown MCP: convert_to_markdown(\"file://{dest_path}\")\n"
            f"Spara resultatet som: {target_folder}/source_converted.md"
        )
        response["message"] = (
            f"Fil tillagd: {source.name} → {relative_path}\n"
            f"OBS: Filen behöver konverteras till markdown innan den kan användas."
        )
    else:
        response["message"] = f"Fil tillagd: {source.name} → {relative_path}"

    # Add next step hint
    response["next_step"] = "Kör step0_analyze() för att få rekommenderat arbetsflöde."

    return response


async def step0_analyze(project_path: str) -> Dict[str, Any]:
    """Analyze project contents and recommend workflow (ADR-015).

    Examines what files exist in the project and suggests the appropriate
    entry point / workflow based on content.

    Args:
        project_path: Path to project directory

    Returns:
        dict with analysis results and recommendations
    """
    project = Path(project_path).resolve()

    # Validate project exists
    if not project.exists():
        return {
            "success": False,
            "error": {
                "type": "project_not_found",
                "message": f"Projekt hittades inte: {project_path}"
            }
        }

    # Analyze project contents
    analysis = {
        "materials": [],
        "questions": [],
        "resources": [],
        "other": [],
    }

    # Scan materials folder
    materials_dir = project / "materials"
    if materials_dir.exists():
        for f in materials_dir.rglob("*"):
            if f.is_file() and not f.name.startswith("."):
                analysis["materials"].append({
                    "path": str(f.relative_to(project)),
                    "name": f.name,
                    "type": detect_file_type(f),
                    "needs_conversion": needs_conversion(f),
                })

    # Scan questions folder
    questions_dir = project / "questions"
    if questions_dir.exists():
        for f in questions_dir.iterdir():
            if f.is_file() and not f.name.startswith("."):
                file_info = {
                    "path": str(f.relative_to(project)),
                    "name": f.name,
                    "type": detect_file_type(f),
                    "needs_conversion": needs_conversion(f),
                }

                # Try to count questions if markdown
                if f.suffix.lower() in (".md", ".markdown"):
                    try:
                        content = f.read_text(encoding="utf-8")
                        # Count question separators (---)
                        separator_count = len(re.findall(r'\n---\n', content))
                        # Count ^type declarations
                        type_count = len(re.findall(r'^\^type\s+', content, re.MULTILINE))
                        file_info["estimated_questions"] = max(separator_count, type_count)
                    except Exception:
                        pass

                analysis["questions"].append(file_info)

        # Scan resources subfolder
        resources_dir = questions_dir / "resources"
        if resources_dir.exists():
            for f in resources_dir.rglob("*"):
                if f.is_file() and not f.name.startswith("."):
                    analysis["resources"].append({
                        "path": str(f.relative_to(project)),
                        "name": f.name,
                        "type": detect_file_type(f),
                    })

    # Determine recommendation
    has_materials = len(analysis["materials"]) > 0
    has_questions = len(analysis["questions"]) > 0
    has_resources = len(analysis["resources"]) > 0

    # Check if any questions file has QFMD format
    has_qfmd = False
    has_markdown_questions = False
    needs_conversion_files = []

    for q in analysis["questions"]:
        if q.get("needs_conversion"):
            needs_conversion_files.append(q["name"])
        elif q["type"] == "markdown" and q.get("estimated_questions", 0) > 0:
            has_markdown_questions = True
            # Check for QFMD markers
            try:
                qpath = project / q["path"]
                content = qpath.read_text(encoding="utf-8")
                if "^type " in content and "^identifier " in content:
                    has_qfmd = True
            except Exception:
                pass

    # Determine recommended flow
    if not has_materials and not has_questions:
        # Empty project
        recommendation = {
            "status": "empty",
            "message": "Projektet är tomt. Lägg till filer med step0_add_file().",
            "recommended_flow": None,
            "alternatives": [],
        }
    elif needs_conversion_files:
        # Files need conversion first
        recommendation = {
            "status": "needs_conversion",
            "message": (
                f"Filer behöver konverteras till markdown: {', '.join(needs_conversion_files)}\n"
                f"Använd MarkItDown MCP för att konvertera."
            ),
            "recommended_flow": "MarkItDown → M5 → Pipeline",
            "files_to_convert": needs_conversion_files,
            "alternatives": [],
        }
    elif has_qfmd:
        # Ready for pipeline
        recommendation = {
            "status": "ready_for_pipeline",
            "message": "Frågorna är i QFMD-format. Redo för validering och export.",
            "recommended_flow": "Pipeline (Step 2 → Step 3 → Step 4)",
            "next_command": "step2_validate()",
            "alternatives": [
                "M4 → Pipeline (granska pedagogiskt först)",
            ],
        }
    elif has_markdown_questions:
        # Has markdown questions but not QFMD
        total_questions = sum(q.get("estimated_questions", 0) for q in analysis["questions"])
        recommendation = {
            "status": "needs_m5",
            "message": f"Hittade ~{total_questions} frågor i markdown-format. Behöver konverteras till QFMD.",
            "recommended_flow": "M5 → Pipeline",
            "next_command": "m5_start()",
            "alternatives": [
                "M4 → M5 → Pipeline (granska pedagogiskt först)",
                "M2 → M5 → Pipeline (lägg till taxonomi först)",
            ],
        }
    elif has_materials and not has_questions:
        # Only materials
        recommendation = {
            "status": "needs_m1",
            "message": "Har undervisningsmaterial men inga frågor ännu.",
            "recommended_flow": "M1 → M2 → M3 → M4 → M5 → Pipeline",
            "next_command": "load_stage(module='m1', stage=0)",
            "alternatives": [],
        }
    else:
        # Other cases
        recommendation = {
            "status": "unclear",
            "message": "Kunde inte avgöra optimalt arbetsflöde. Kontrollera projektinnehåll.",
            "recommended_flow": None,
            "alternatives": list(ENTRY_POINT_REQUIREMENTS.keys()),
        }

    # Load session for logging
    session = get_current_session()
    if session is None:
        try:
            session = SessionManager.load_from_path(project_path)
            set_current_session(session)
        except Exception:
            pass

    # Log event
    if session:
        log_event(
            project_path=project,
            session_id=session.session_id,
            tool="step0_analyze",
            event="project_analyzed",
            level="info",
            data={
                "materials_count": len(analysis["materials"]),
                "questions_count": len(analysis["questions"]),
                "resources_count": len(analysis["resources"]),
                "recommendation": recommendation["status"],
            }
        )

    return {
        "success": True,
        "project_path": str(project),
        "analysis": {
            "materials_count": len(analysis["materials"]),
            "questions_count": len(analysis["questions"]),
            "resources_count": len(analysis["resources"]),
            "materials": analysis["materials"][:10],  # Limit to first 10
            "questions": analysis["questions"],
            "resources": analysis["resources"][:20],  # Limit to first 20
        },
        "recommendation": recommendation,
    }
