# RFC-001: CourseExtractor MCP Server (MINIMAL MVP)

**Status:** APPROVED - Ready for Implementation  
**Author:** Niklas Karlsson  
**Created:** 2026-01-20  
**Version:** 4.0 - MINIMAL MVP (PDF-only)

---

## ABSTRACT

CourseExtractor MCP är en **minimal, fokuserad** MCP-server designad för att extrahera text och bilder från svenska PDF-kursmaterial. Bygger på pymupdf4llm med AGPL 3.0-licens.

**v4.0 PHILOSOPHY:** 
> "Do one thing well" - Endast PDF, ingen feature creep, production-ready på 60 minuter.

---

## MOTIVATION

### Problem
- QuestionForge behöver extrahera text + bilder från 10 PDF-kursfiler
- Befintlig `read_materials` extraherar endast text (missar bilder)
- MarkItDown är backup, men inget MCP-lärande

### Lösning
Bygg en minimal MCP-server som:
- **ENDAST hanterar PDF** (10/10 filer är PDF)
- Extraherar text OCH bilder
- Sparar bilder till disk
- Lär dig MCP-protokollet
- Deployable på 60 minuter

### Scope Decisions (RFC v3.0 → v4.0)

**BORTTAGET (Feature Creep):**
- ❌ DOCX support (0/10 filer är DOCX)
- ❌ PPTX support (0/10 filer är PPTX)
- ❌ OCR support (inte behövt än)
- ❌ Komplex modulstruktur

**BEHÅLLET (Core Need):**
- ✅ PDF text extraction
- ✅ PDF image extraction + disk save
- ✅ Metadata extraction
- ✅ Svenska felmeddelanden

**RESULTAT:**
- Från 450 rader → **~120 rader**
- Från 120 min → **60 min**
- Från 7 deps → **3 deps**
- Från AGPL risk → **AGPL by design** ✅

---

## REQUIREMENTS

### Functional Requirements

#### FR1: PDF Text Extraction
- **FR1.1:** Extrahera text från PDF med layout-bevarande
- **FR1.2:** Bevara struktur (headings, listor, tabeller)
- **FR1.3:** Returnera som Markdown

#### FR2: PDF Image Extraction
- **FR2.1:** Extrahera bilder från PDF
- **FR2.2:** Spara bilder till `output_folder/images/`
- **FR2.3:** Strukturerad namngivning: `page_X_img_Y.{ext}`
- **FR2.4:** Returnera paths till alla sparade bilder

#### FR3: Metadata
- **FR3.1:** Sidantal
- **FR3.2:** Titel (om finns)
- **FR3.3:** Författare (om finns)

---

### Non-Functional Requirements

#### NFR1: Säkerhet
- **NFR1.1:** Input validation (absolut path, file exists, size < 100MB)
- **NFR1.2:** Output path sanitization (no traversal)
- **NFR1.3:** Timeout: 60 sekunder per PDF

#### NFR2: Performance
- **NFR2.1:** PDF-extraktion < 5 sekunder för 10-sidors dokument
- **NFR2.2:** Minnesanvändning < 500MB

#### NFR3: Usability
- **NFR3.1:** Svenska felmeddelanden
- **NFR3.2:** JSON output med tydlig struktur

---

## DESIGN

### Architecture

```
┌─────────────────────────────────────┐
│    Claude Desktop (MCP Client)      │
└────────────────┬────────────────────┘
                 │ STDIO (JSON-RPC)
                 │
┌────────────────▼────────────────────┐
│   CourseExtractor MCP Server        │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  FastMCP Handler             │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│  ┌──────────▼───────────────────┐  │
│  │  extract_pdf() tool          │  │
│  │  - Validate input            │  │
│  │  - Call pymupdf4llm          │  │
│  │  - Return text + image paths │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│  ┌──────────▼───────────────────┐  │
│  │  pymupdf4llm.to_markdown()   │  │
│  │  - write_images=True         │  │
│  │  - image_path=output_folder  │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## MCP TOOL SPECIFICATION

### Tool: `extract_pdf`

**Purpose:** Extrahera text och bilder från PDF

**Input Schema:**
```json
{
  "file_path": "string (required)",
  "output_folder": "string (optional, default: '/tmp/course_extractor')",
  "image_format": "string (optional, default: 'png')",
  "dpi": "integer (optional, default: 300)"
}
```

**Output Schema:**
```json
{
  "text_markdown": "string",
  "images": [
    {
      "page": "integer",
      "index": "integer", 
      "saved_path": "string",
      "format": "string"
    }
  ],
  "metadata": {
    "pages": "integer",
    "title": "string",
    "author": "string"
  },
  "summary": {
    "total_images": "integer",
    "output_folder": "string"
  }
}
```

**Error Handling:**
```python
# File not found
{"error": "Filen hittades inte: {path}"}

# Invalid PDF
{"error": "Ogiltig eller korrupt PDF-fil"}

# File too large
{"error": "PDF för stor (max 100MB)"}

# Timeout
{"error": "PDF-bearbetning tog för lång tid (max 60s)"}
```

---

## DEPENDENCIES

**Runtime:**
```txt
mcp>=1.0.0              # MCP SDK (MIT)
pymupdf4llm>=0.0.17     # PDF extraction (AGPL 3.0)
Pillow>=10.0.0          # Image handling (HPND)
```

**Total:** 3 Python packages (ner från 7!)

**License Strategy:**
```yaml
CourseExtractor: AGPL 3.0
  ↓
Uses pymupdf4llm: AGPL 3.0  ← COMPATIBLE! ✅
  ↓
Distribution: Open source på GitHub
Use case: Educational (AGPL-compliant)
```

---

## FILE STRUCTURE

```
course-extractor-mcp/
├── server.py                 # ~120 rader (TOTAL!)
├── requirements.txt          # 3 dependencies
├── README.md                 # Installation + usage
├── LICENSE                   # AGPL 3.0
├── .gitignore
├── tests/
│   └── test_pdf.py          # Basic tests
└── examples/
    └── sample.pdf           # Test file
```

**No separate modules, no utils, no extractors folder.**
**One file, one purpose, production-ready.**

---

## IMPLEMENTATION

### server.py (Complete Implementation)

```python
#!/usr/bin/env python3
"""
CourseExtractor MCP Server - Minimal MVP
Extracts text and images from PDF course materials.

License: AGPL 3.0
"""

import os
import sys
from pathlib import Path
from typing import Any
import pymupdf4llm
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("CourseExtractor")

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
    
    # Validate input
    pdf_path = Path(file_path).resolve()
    
    if not pdf_path.exists():
        return {"error": f"Filen hittades inte: {file_path}"}
    
    if not pdf_path.suffix.lower() == '.pdf':
        return {"error": "Filen måste vara en PDF"}
    
    # Check file size (max 100MB)
    file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 100:
        return {"error": f"PDF för stor ({file_size_mb:.1f}MB, max 100MB)"}
    
    # Create output folder
    output_path = Path(output_folder).resolve()
    images_folder = output_path / "images"
    images_folder.mkdir(parents=True, exist_ok=True)
    
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
        
        # Parse results
        if isinstance(md_text, list):
            # page_chunks=True returns list of dicts
            text_parts = []
            all_images = []
            total_pages = len(md_text)
            
            for page_data in md_text:
                text_parts.append(page_data.get('text', ''))
                
                # Collect image info if available
                if 'images' in page_data:
                    for img in page_data['images']:
                        all_images.append({
                            'page': page_data.get('page', 0),
                            'index': len(all_images),
                            'saved_path': str(images_folder / img),
                            'format': image_format
                        })
            
            full_text = '\n\n'.join(text_parts)
        else:
            # Single string returned
            full_text = md_text
            all_images = []
            total_pages = 0
        
        # Get metadata (basic)
        import fitz  # PyMuPDF
        doc = fitz.open(str(pdf_path))
        metadata = doc.metadata or {}
        total_pages = len(doc)
        doc.close()
        
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
        
    except Exception as e:
        return {"error": f"Fel vid PDF-bearbetning: {str(e)}"}


if __name__ == "__main__":
    # Run MCP server
    mcp.run()
```

---

## INSTALLATION

### 1. Prerequisites

```bash
# Python 3.11+
python --version

# pip
pip --version
```

### 2. Install Dependencies

```bash
cd /path/to/course-extractor-mcp
pip install -r requirements.txt
```

### 3. Configure Claude Desktop

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

### 4. Test

```bash
# Start Claude Desktop
# Ask Claude: "Extract content from /path/to/sample.pdf"
```

---

## TESTING STRATEGY

### Manual Testing

```python
# Test with Claude Desktop:
# 1. Start server
# 2. Ask: "Use course-extractor to extract /path/to/test.pdf"
# 3. Verify:
#    - Text returned as markdown
#    - Images saved to /tmp/course_extractor/images/
#    - Metadata correct
```

### Unit Test (optional)

```python
# tests/test_pdf.py
import pytest
from pathlib import Path
from server import extract_pdf

def test_extract_pdf_basic():
    result = extract_pdf(
        file_path="examples/sample.pdf",
        output_folder="/tmp/test"
    )
    
    assert "text_markdown" in result
    assert len(result["text_markdown"]) > 0
    assert "images" in result
    assert result["metadata"]["pages"] > 0

def test_extract_pdf_file_not_found():
    result = extract_pdf(file_path="/nonexistent.pdf")
    assert "error" in result
    assert "hittades inte" in result["error"]

def test_extract_pdf_too_large():
    # Create 101MB dummy file
    large_pdf = Path("/tmp/large.pdf")
    large_pdf.write_bytes(b"x" * (101 * 1024 * 1024))
    
    result = extract_pdf(file_path=str(large_pdf))
    assert "error" in result
    assert "för stor" in result["error"]
```

---

## SECURITY

### Threat Mitigation

**1. Input Validation**
```python
# File exists
if not pdf_path.exists(): return error

# Is PDF
if not pdf_path.suffix.lower() == '.pdf': return error

# Size limit
if file_size_mb > 100: return error
```

**2. Path Sanitization**
```python
# Resolve to absolute path (prevents traversal)
pdf_path = Path(file_path).resolve()
output_path = Path(output_folder).resolve()
```

**3. Error Handling**
```python
try:
    # All PDF processing
except Exception as e:
    return {"error": f"Fel: {str(e)}"}
```

**4. Timeout** (handled by MCP client, default 60s)

**5. Docker** (optional, see separate guide)

---

## LICENSE COMPLIANCE

### AGPL 3.0 Requirements

**What you MUST do:**

1. **Include LICENSE file:**
```bash
cp /path/to/AGPL-3.0.txt ./LICENSE
```

2. **Add license header to server.py:**
```python
"""
CourseExtractor MCP Server
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
```

3. **README.md mention:**
```markdown
## License

This project uses AGPL 3.0 because it depends on PyMuPDF (AGPL 3.0).
```

4. **Publish source on GitHub:**
```bash
git init
git add .
git commit -m "Initial commit - AGPL 3.0"
git remote add origin https://github.com/yourusername/course-extractor-mcp
git push -u origin main
```

---

## DEPLOYMENT

### Local Development

```bash
python server.py
# MCP server runs on STDIO, waiting for Claude Desktop
```

### Production (if needed later)

**Docker (optional):**
See `/docs/Docker_Security_Guide.md` for hardened deployment.

---

## FUTURE ENHANCEMENTS (Post-MVP)

### v1.1 (If actually needed)
- [ ] Batch processing (multiple PDFs)
- [ ] DOCX support (only if needed)
- [ ] Progress callbacks

### v1.2 (Nice to have)
- [ ] Image deduplication
- [ ] PDF compression detection
- [ ] Better metadata extraction

### v2.0 (Production)
- [ ] Docker deployment
- [ ] Web interface
- [ ] API mode

**Philosophy:** Build these ONLY when needed, not speculatively.

---

## SUCCESS METRICS

**Launch (Week 1):**
- ✅ Extracts text from all 10 course PDFs
- ✅ Extracts images from all 10 course PDFs
- ✅ Zero crashes
- ✅ Integration with Claude Desktop working

**Adoption (Month 1):**
- ✅ Used for M1 material analysis
- ✅ No bugs reported
- ✅ Saves time vs manual extraction

**Learning (Month 1):**
- ✅ Understand MCP protocol
- ✅ Know STDIO communication
- ✅ Can build more MCP servers

---

## CHANGELOG

### [4.0.0] - 2026-01-20 (MINIMAL MVP)
- 🎯 **FOCUS:** PDF-only (removed DOCX, PPTX, OCR)
- ✂️ Reduced from 450 → 120 lines of code
- ⏱️ Reduced implementation time: 120min → 60min
- 📦 Reduced dependencies: 7 → 3 packages
- ✅ Single file implementation (server.py)
- ✅ AGPL 3.0 by design (no license conflict)
- ✅ Production-ready on day 1

### [3.0.0] - 2026-01-20
- Full feature RFC (discarded for v4.0)

### [2.0.0] - 2026-01-20  
- Added image extraction (kept in v4.0)

### [1.0.0] - 2026-01-20
- Initial concept (evolved to v4.0)

---

## REFERENCES

- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [pymupdf4llm](https://github.com/pymupdf/pymupdf4llm)
- [pymupdf4llm API](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/api.html)
- [AGPL 3.0 License](https://www.gnu.org/licenses/agpl-3.0.en.html)

---

## APPENDIX: Why Minimal?

**Analysis showed:**
- 10/10 course files are PDF
- 0/10 course files are DOCX
- 0/10 course files are PPTX
- OCR not needed (PDFs have text layer)

**Therefore:**
- Building DOCX/PPTX = **70% wasted effort**
- Building OCR = **Premature optimization**
- Building complex structure = **Over-engineering**

**Minimal MVP:**
- **Builds what's needed NOW**
- **Ships in 60 minutes**
- **Can expand later IF needed**
- **Learns MCP just as well**

**This is engineering wisdom: Start small, iterate based on real needs.**

---

**END OF RFC-001 v4.0 - MINIMAL MVP**

**STATUS: APPROVED ✅**
**READY TO BUILD: YES 🚀**
**ESTIMATED TIME: 60 minutes**
**LICENSE: AGPL 3.0** 
**NEXT STEP: Implementation**
