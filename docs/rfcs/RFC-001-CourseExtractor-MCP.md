# RFC-001: CourseExtractor MCP Server

**Status:** APPROVED - macOS/Linux Only  
**Author:** Niklas Karlsson  
**Created:** 2026-01-20  
**Updated:** 2026-02-04 (Consolidated from v4.2-FINAL, translated to English)

---

## Platform Compatibility

**Supported:**
- ✅ macOS
- ✅ Linux

**NOT Supported:**
- ❌ Windows (signal.SIGALRM not available)

**Rationale:** 
- Uses Unix signal handling for timeout
- Threading-based alternative is complex and cannot kill threads
- Developer runs macOS (no Windows requirement)
- This is an MVP/learning project, not commercial software

---

## Version History

This RFC consolidates the following versions (archived in `_archive/`):
- v3.0: Original broad scope (PDF, DOCX, PPTX, images)
- v4.0-MINIMAL: Narrowed to PDF-only MVP
- v4.1-CORRECTED: Post-Code Review fixes
- v4.1-PRODUCTION-READY: Production labelling
- v4.2-FINAL: Final approved version with platform documentation

---

## Abstract

CourseExtractor MCP is a **minimal, Unix-only, production-ready** MCP server designed to extract text and images from Swedish PDF course materials. Built on pymupdf4llm with AGPL 3.0 licence.

**Philosophy:** 
> "Production-ready for the platform we need" - macOS/Linux only, robust, simple.

---

## Motivation

### Problem
- QuestionForge needs to extract text + images from PDF course files
- Existing `read_materials` extracts only text (misses images)
- MarkItDown is a backup option, but provides no MCP learning opportunity

### Solution
Build a minimal MCP server that:
- **Handles PDF only** (focused scope)
- Extracts text AND images
- Saves images to disk
- Teaches MCP protocol development
- **Production-ready on Unix systems**
- **Simple and robust**

---

## Requirements

### Platform Requirements

**Operating System:**
- macOS 10.15+ ✅
- Linux (Ubuntu 20.04+, Debian, Fedora, etc.) ✅
- Windows ❌ NOT SUPPORTED

**Why Unix-only:**
- Uses `signal.SIGALRM` for timeout (Unix signal)
- Alternative (threading) is complex and cannot kill threads
- Developer environment is macOS
- MVP scope - focus on working solution for target platform

---

## Dependencies

**Runtime:**
```txt
mcp>=1.0.0              # MCP SDK (MIT)
pymupdf4llm>=0.0.17     # PDF extraction (AGPL 3.0)
PyMuPDF>=1.23.0         # For fitz (PDF metadata, encryption check)
```

**Platform:** Python 3.11+ on macOS or Linux

**Total:** 3 Python packages

**Licence Strategy:**
```yaml
CourseExtractor: AGPL 3.0
  ↓
Uses pymupdf4llm: AGPL 3.0  ← COMPATIBLE! ✅
  ↓
Distribution: Open source on GitHub
Use case: Educational (AGPL-compliant)

QuestionForge: MIT/Own Licence  ← NOT AFFECTED!
  ↓
Communicates via MCP (STDIO/JSON-RPC)
  ↓
CourseExtractor (AGPL 3.0)

AGPL "aggregation" exception applies
```

---

## Implementation

### server.py (Complete Production-Ready Implementation - Unix Only)

```python
#!/usr/bin/env python3
"""
CourseExtractor MCP Server - Minimal MVP (Unix/macOS/Linux Only)
Extracts text and images from PDF course materials.

Platform Support:
- macOS ✅
- Linux ✅
- Windows ❌ (signal.SIGALRM not available)

Licence: AGPL 3.0
Copyright (C) 2026 Niklas Karlsson

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public Licence as published by
the Free Software Foundation, either version 3 of the Licence, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public Licence for more details.

You should have received a copy of the GNU Affero General Public Licence
along with this program. If not, see &lt;https://www.gnu.org/licenses/&gt;.
"""

import os
import sys
import signal
from glob import glob
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
import pymupdf4llm
from mcp.server.fastmcp import FastMCP

# Platform check
if not hasattr(signal, 'SIGALRM'):
    print("ERROR: CourseExtractor requires Unix (macOS/Linux)", file=sys.stderr)
    print("Windows is not supported due to signal.SIGALRM dependency", file=sys.stderr)
    sys.exit(1)

# Initialise MCP server
mcp = FastMCP("CourseExtractor")

# SECURITY: Allowed output directories (whitelist)
ALLOWED_OUTPUT_ROOTS = [
    Path("/tmp"),
    Path.home() / "course_extractor",
    # Add your specific paths:
    Path.home() / "Nextcloud" / "Courses",
]

# Timeout handler
class TimeoutError(Exception):
    """Raised when PDF processing takes too long"""
    pass

def timeout_handler(signum, frame):
    """Signal handler for timeout"""
    raise TimeoutError("PDF processing took too long (max 60s)")


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
        
    Security:
        - Input validation (file exists, size &lt; 100MB, is PDF)
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
        return {"error": f"File not found: {file_path}"}
    
    # Check file extension
    if not pdf_path.suffix.lower() == '.pdf':
        return {"error": "File must be a PDF"}
    
    # Check file size (max 100MB)
    file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 100:
        return {"error": f"PDF too large ({file_size_mb:.1f}MB, max 100MB)"}
    
    # ===== OUTPUT PATH SECURITY =====
    
    output_path = Path(output_folder).resolve()
    
    # SECURITY: Whitelist allowed output directories
    if not any(output_path.is_relative_to(root) for root in ALLOWED_OUTPUT_ROOTS):
        allowed_paths = ", ".join(str(p) for p in ALLOWED_OUTPUT_ROOTS)
        return {"error": f"Output folder must be under: {allowed_paths}"}
    
    images_folder = output_path / "images"
    
    try:
        images_folder.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        return {"error": f"Cannot create output folder: {images_folder}"}
    
    # ===== EDGE CASE HANDLING =====
    
    try:
        # Check for encrypted/password-protected PDF
        doc = fitz.open(str(pdf_path))
        
        if doc.is_encrypted:
            doc.close()
            return {"error": "Encrypted or password-protected PDF not supported"}
        
        # Get metadata early
        metadata = doc.metadata or {}
        total_pages = len(doc)
        doc.close()
        
    except Exception as e:
        return {"error": f"Could not open PDF: {str(e)}"}
    
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
        
        # SIMPLIFIED: Just return list of images, no page parsing
        # (Filename format from pymupdf4llm may vary, parsing is fragile)
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
        return {"error": "PDF processing took too long (max 60s)"}
    
    except Exception as e:
        return {"error": f"Error processing PDF: {str(e)}"}
    
    finally:
        # Always cancel alarm (runs even if exception raised)
        signal.alarm(0)


if __name__ == "__main__":
    # Run MCP server
    mcp.run()
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_pdf.py
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server import extract_pdf


def test_extract_pdf_file_not_found():
    """Test file not found error"""
    result = extract_pdf(file_path="/nonexistent.pdf")
    assert "error" in result
    assert "not found" in result["error"]


def test_extract_pdf_not_pdf():
    """Test non-PDF file"""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(b"not a pdf")
        temp_path = f.name
    
    try:
        result = extract_pdf(file_path=temp_path)
        assert "error" in result
        assert "must be a PDF" in result["error"]
    finally:
        Path(temp_path).unlink()


def test_extract_pdf_too_large():
    """Test file size limit"""
    with patch.object(Path, 'resolve') as mock_resolve:
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        type(mock_path).suffix = PropertyMock(return_value='.pdf')
        mock_path.stat.return_value.st_size = 101 * 1024 * 1024  # 101 MB
        mock_resolve.return_value = mock_path
        
        result = extract_pdf(file_path="/tmp/large.pdf")
        assert "error" in result
        assert "too large" in result["error"]


def test_extract_pdf_encrypted():
    """Test encrypted PDF rejection"""
    with patch.object(Path, 'resolve') as mock_resolve:
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        type(mock_path).suffix = PropertyMock(return_value='.pdf')
        mock_path.stat.return_value.st_size = 1024
        mock_resolve.return_value = mock_path
        
        with patch('fitz.open') as mock_open:
            mock_doc = MagicMock()
            mock_doc.is_encrypted = True
            mock_open.return_value = mock_doc
            
            result = extract_pdf(file_path="/tmp/encrypted.pdf")
            assert "error" in result
            assert "Encrypted" in result["error"]


def test_output_path_whitelist():
    """Test output path security"""
    with patch.object(Path, 'resolve') as mock_resolve:
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        type(mock_path).suffix = PropertyMock(return_value='.pdf')
        mock_path.stat.return_value.st_size = 1024
        mock_resolve.return_value = mock_path
        
        result = extract_pdf(
            file_path="/tmp/sample.pdf",
            output_folder="/etc/cron.d"  # Dangerous path!
        )
        
        assert "error" in result
        assert "must be under" in result["error"]


@pytest.mark.skipif(not Path("examples/sample.pdf").exists(), 
                    reason="Requires examples/sample.pdf")
def test_extract_pdf_basic():
    """Test basic PDF extraction (requires real PDF)"""
    result = extract_pdf(
        file_path="examples/sample.pdf",
        output_folder="/tmp/test_course_extractor"
    )
    
    assert "error" not in result
    assert "text_markdown" in result
    assert "images" in result
    assert "metadata" in result
    assert result["metadata"]["pages"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Platform Support Details

### Why Unix-only?

**Technical Reason:**
```python
# Unix (macOS/Linux) - WORKS ✅
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(60)

# Windows - FAILS ❌
AttributeError: module 'signal' has no attribute 'SIGALRM'
```

**Alternative Considered:**
```python
# Threading-based timeout (cross-platform)
import threading

thread = threading.Thread(target=worker)
thread.start()
thread.join(timeout=60)

if thread.is_alive():
    # ⚠️ PROBLEM: Can't actually kill the thread!
    # It keeps running in background
    return {"error": "Timeout"}
```

**Why Rejected:**
- Cannot terminate thread (Python limitation)
- PDF processing continues in background (resource leak)
- Complex code for uncertain benefit
- Developer runs macOS (no Windows requirement)

**Decision:** Unix-only is acceptable for MVP/learning project

---

## Security

### Threat Mitigation

**1. Input Validation**
- File exists check
- PDF extension check
- Size limit (100MB)
- Encrypted PDF detection

**2. Output Path Security**
- Whitelist of allowed directories
- Prevents path traversal attacks

**3. Timeout (Unix only)**
- 60-second maximum processing time
- Signal-based termination

**4. Error Handling**
- Graceful error messages
- Cleanup always runs (finally block)

---

## Edge Cases Handled

| Scenario | Handling | Error Message |
|----------|----------|---------------|
| Windows OS | Exit on startup | "CourseExtractor requires Unix" |
| Encrypted PDF | Detected via `is_encrypted` | "Encrypted or password-protected..." |
| PDF > 100MB | Size check before processing | "PDF too large (X MB, max 100MB)" |
| PDF without text layer | Returns empty text | No error (graceful) |
| Corrupt PDF | Exception caught | "Could not open PDF: ..." |
| Output folder = "/" | Whitelist blocks | "Output folder must be under: ..." |
| Timeout (huge PDF) | Signal alarm (60s) | "PDF processing took too long..." |

---

## Installation

### 1. Prerequisites

```bash
# Platform check
uname  # Should return: Darwin (macOS) or Linux

# Python 3.11+
python --version
```

### 2. Install Dependencies

```bash
cd /path/to/course-extractor-mcp

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # macOS/Linux only

# Install
pip install -r requirements.txt
```

### 3. Configure Allowed Output Paths

Edit `server.py` line 44 to add your paths.

### 4. Configure Claude Desktop

```json
{
  "mcpServers": {
    "course-extractor": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

---

## Time Estimate

| Phase | Estimate |
|-------|----------|
| Basic structure + FastMCP | 15 min |
| extract_pdf implementation | 30 min |
| Test with real PDFs | 30 min |
| Claude Desktop config | 15 min |
| **TOTAL** | **90 min** |

---

## Changelog

### [Consolidated] - 2026-02-04
- Consolidated from v4.2-FINAL
- Translated to British English
- Archived previous versions

### [4.2.0] - 2026-01-20 (FINAL)
- Documented Unix-only platform support
- Fixed test mocking issues
- Simplified image collection

### [4.1.0] - 2026-01-20
- Post-Code Review fixes

### [4.0.0] - 2026-01-20
- PDF-only focus (MINIMAL MVP)

---

**STATUS: APPROVED ✅**  
**PLATFORM: macOS/Linux Only**  
**LICENCE: AGPL 3.0**
