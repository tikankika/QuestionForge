"""Methodology copying for qf-pipeline.

Copies the methodology files from QuestionForge/methodology/ to the project
to make it self-contained.
"""

import shutil
from pathlib import Path
from typing import Dict, Any

# Hardcoded path to QuestionForge methodology (TODO: make configurable)
METHODOLOGY_SOURCE = Path("./methodology")


def get_methodology_source() -> Path:
    """Get path to methodology source directory.

    Returns:
        Path to methodology source
    """
    return METHODOLOGY_SOURCE


def copy_methodology(project_path: Path) -> Dict[str, Any]:
    """Copy methodology files to project.

    Copies all files from QuestionForge/methodology/ to project/methodology/
    to make the project self-contained.

    Args:
        project_path: Project directory

    Returns:
        dict with success status and file count
    """
    source = get_methodology_source()
    dest = project_path / "methodology"

    if not source.exists():
        return {
            "success": False,
            "error": f"Methodology source not found: {source}",
            "files_copied": 0,
        }

    # Ensure destination exists
    dest.mkdir(exist_ok=True)

    files_copied = 0
    try:
        # Copy directory structure
        for item in source.rglob("*"):
            if item.is_file():
                # Get relative path from source
                rel_path = item.relative_to(source)
                dest_path = dest / rel_path

                # Create parent directories
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy file
                shutil.copy2(item, dest_path)
                files_copied += 1

        return {
            "success": True,
            "files_copied": files_copied,
            "source": str(source),
            "destination": str(dest),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "files_copied": files_copied,
        }


def verify_methodology(project_path: Path) -> Dict[str, Any]:
    """Verify methodology files exist in project.

    Args:
        project_path: Project directory

    Returns:
        dict with verification status
    """
    methodology_dir = project_path / "methodology"

    if not methodology_dir.exists():
        return {
            "exists": False,
            "error": "methodology/ folder not found",
            "files": [],
        }

    files = list(methodology_dir.rglob("*.md"))

    return {
        "exists": True,
        "file_count": len(files),
        "modules": {
            "m1": len(list(methodology_dir.glob("m1/*.md"))),
            "m2": len(list(methodology_dir.glob("m2/*.md"))),
            "m3": len(list(methodology_dir.glob("m3/*.md"))),
            "m4": len(list(methodology_dir.glob("m4/*.md"))),
        }
    }
