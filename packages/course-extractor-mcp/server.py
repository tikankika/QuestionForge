#!/usr/bin/env python3
"""
CourseExtractor MCP Server - Minimal MVP (Unix/macOS/Linux Only)
Extracts text and images from PDF course materials.

Platform Support:
- macOS ✅
- Linux ✅
- Windows ❌ (signal.SIGALRM not available)

License: AGPL 3.0
Copyright (C) 2026 Niklas Karlsson

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import signal
from glob import glob
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
import pymupdf4llm
from fastmcp import FastMCP

# Platform check (CRITICAL: Fail fast on Windows)
if not hasattr(signal, 'SIGALRM'):
    print("ERROR: CourseExtractor requires Unix (macOS/Linux)", file=sys.stderr)
    print("Windows is not supported due to signal.SIGALRM dependency", file=sys.stderr)
    sys.exit(1)

# Initialize MCP server
mcp = FastMCP("CourseExtractor")

# SECURITY: Allowed output directories (whitelist)
# IMPORTANT: Customize these paths for your environment!
ALLOWED_OUTPUT_ROOTS = [
    Path("/tmp"),
    Path("/private/tmp"),  # macOS: /tmp is symlink to /private/tmp
    Path.home() / "course_extractor",
    Path.home() / "Nextcloud" / "Courses",
]


# Timeout handler
class TimeoutError(Exception):
    """Raised when PDF processing takes too long"""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout"""
    raise TimeoutError("PDF-bearbetning tog för lång tid (max 60s)")


def _extract_pdf_impl(
    file_path: str,
    output_folder: str = "/tmp/course_extractor",
    image_format: str = "png",
    dpi: int = 300
) -> dict[str, Any]:
    """
    Extract text and images from a PDF file.

    Args:
        file_path: Absolute path to PDF file
        output_folder: Where to save extracted images
        image_format: Image format (png, jpg)
        dpi: Image resolution

    Returns:
        Dictionary with text, images, and metadata

    Security:
        - Input validation (file exists, size < 100MB, is PDF)
        - Output path whitelist (prevents /etc/cron.d attacks)
        - Timeout (60s max per PDF, Unix only)
        - Encrypted PDF detection

    Platform:
        - Requires Unix (macOS/Linux)
        - Windows NOT supported (signal.SIGALRM)
    """

    # ===== INPUT VALIDATION =====

    pdf_path = Path(file_path).resolve()

    # Check file exists
    if not pdf_path.exists():
        return {"error": f"Filen hittades inte: {file_path}"}

    # Check file extension
    if not pdf_path.suffix.lower() == '.pdf':
        return {"error": "Filen måste vara en PDF"}

    # Check file size (max 100MB)
    file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 100:
        return {"error": f"PDF för stor ({file_size_mb:.1f}MB, max 100MB)"}

    # ===== OUTPUT PATH SECURITY =====

    output_path = Path(output_folder).resolve()

    # SECURITY: Whitelist allowed output directories
    if not any(output_path.is_relative_to(root) for root in ALLOWED_OUTPUT_ROOTS):
        allowed_paths = ", ".join(str(p) for p in ALLOWED_OUTPUT_ROOTS)
        return {"error": f"Output folder måste vara under: {allowed_paths}"}

    images_folder = output_path / "images"

    try:
        images_folder.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        return {"error": f"Kan inte skapa output folder: {images_folder}"}

    # ===== EDGE CASE HANDLING =====

    try:
        # Check for encrypted/password-protected PDF
        doc = fitz.open(str(pdf_path))

        if doc.is_encrypted:
            doc.close()
            return {"error": "Krypterad eller lösenordsskyddad PDF ej stödd"}

        # Get metadata early
        metadata = doc.metadata or {}
        total_pages = len(doc)
        doc.close()

    except Exception as e:
        return {"error": f"Kunde inte öppna PDF: {str(e)}"}

    # ===== PDF EXTRACTION WITH TIMEOUT =====

    # Set timeout (60 seconds)
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)

    try:
        # Extract with pymupdf4llm (handles text + images!)
        md_text = pymupdf4llm.to_markdown(
            str(pdf_path),
            write_images=True,
            image_path=str(images_folder),
            image_format=image_format,
            dpi=dpi,
            page_chunks=True  # Get metadata per page
        )

        # Parse text results
        if isinstance(md_text, list):
            # page_chunks=True returns list of dicts
            text_parts = []

            for page_data in md_text:
                text_parts.append(page_data.get('text', ''))

            full_text = '\n\n'.join(text_parts)
        else:
            # Single string returned
            full_text = md_text

        # ===== IMAGE COLLECTION =====

        # pymupdf4llm saves images to disk but doesn't return image info
        # We need to glob the directory to find saved images

        image_pattern = str(images_folder / f"*.{image_format}")
        saved_image_paths = sorted(glob(image_pattern))

        # SIMPLIFIED: Just return list of images, no fragile page parsing
        all_images = [
            {
                'index': idx,
                'saved_path': img_path,
                'format': image_format,
                'filename': Path(img_path).name
            }
            for idx, img_path in enumerate(saved_image_paths)
        ]

        return {
            "text_markdown": full_text,
            "images": all_images,
            "metadata": {
                "pages": total_pages,
                "title": metadata.get('title', ''),
                "author": metadata.get('author', '')
            },
            "summary": {
                "total_images": len(all_images),
                "output_folder": str(images_folder)
            }
        }

    except TimeoutError:
        return {"error": "PDF-bearbetning tog för lång tid (max 60s)"}

    except Exception as e:
        return {"error": f"Fel vid PDF-bearbetning: {str(e)}"}

    finally:
        # Always cancel alarm (runs even on exception or return)
        signal.alarm(0)


@mcp.tool()
def extract_pdf(
    file_path: str,
    output_folder: str = "/tmp/course_extractor",
    image_format: str = "png",
    dpi: int = 300
) -> dict[str, Any]:
    """
    Extract text and images from a PDF file.

    Args:
        file_path: Absolute path to PDF file
        output_folder: Where to save extracted images
        image_format: Image format (png, jpg)
        dpi: Image resolution

    Returns:
        Dictionary with text, images, and metadata
    """
    return _extract_pdf_impl(file_path, output_folder, image_format, dpi)


if __name__ == "__main__":
    # Run MCP server
    mcp.run()
