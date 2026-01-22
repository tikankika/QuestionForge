# RFC-001: CourseExtractor MCP Server

**Status:** Draft → **v3.0 CRITICAL REVISION**  
**Author:** Niklas Karlsson  
**Created:** 2026-01-20  
**Updated:** 2026-01-20 (v3.0 - Post-Critical Review)

---

## ABSTRACT

CourseExtractor MCP är en minimal, säker MCP-server designad för att extrahera innehåll från svenska kursmaterial **inklusive full bildextraktion till disk**. Fokus ligger på säkerhet, transparens och svenska språket.

**v3.0 KRITISKA ÄNDRINGAR:**
- ✅ Verifierat att alla dependencies faktiskt kan göra vad RFC påstår
- ⚠️ Lagt till `docxpy` för DOCX-bildextraktion (python-docx kan INTE detta!)
- ⚠️ Dokumenterat Tesseract systeminstallation (inte bara pip!)
- ✅ Realistiska tidsestimat (90-120 min, inte 65 min)
- ✅ Uppdaterat kodrad-estimat (400-500 rader, inte 200)

---

## MOTIVATION

### Problem
- Befintliga MCP-servrar (t.ex. MarkItDown) har onödigt många dependencies
- Ingen optimering för svenska kursmaterial
- Black-box implementation - svårt att granska säkerhet
- Overhead för funktioner som aldrig används
- **Bilder i presentationer och dokument förloras ofta**

### Lösning
Bygg en minimal MCP-server med:
- **Endast nödvändiga format:** PDF, DOCX, PPTX, JPG/PNG
- **Svenska språkstöd:** OCR med svenska + engelska
- **Full transparens:** All kod granskningsbar (~400-500 rader)
- **Minimal attack surface:** 7 Python packages + 1 systeminstall
- **Pedagogiskt värde:** Lär dig MCP-protokollet
- **✨ Full bildextraktion med disk-spara**

---

## REQUIREMENTS

### Functional Requirements

#### FR1: PDF Extraktion
- **FR1.1:** Extrahera text från PDF med layout-bevarande
- **FR1.2:** Extrahera bilder från PDF som base64 OCH spara till disk
- **FR1.3:** Bevara struktur (headings, listor, tabeller)
- **FR1.4:** Returnera metadata (sidantal, titel, författare)
- **✨ FR1.5:** Spara bilder till `output_folder/pdf_images/page_X_img_Y.{ext}`

#### FR2: DOCX Extraktion  
- **FR2.1:** Extrahera text från Word-dokument
- **FR2.2:** Extrahera tabeller med struktur bevarad
- **FR2.3:** Hantera formatering (bold, italic, headings)
- **✨ FR2.4:** Extrahera bilder från dokument **via docxpy**
- **✨ FR2.5:** Spara bilder till `output_folder/docx_images/img_X.{ext}`

#### FR3: PPTX Extraktion
- **FR3.1:** Extrahera text från slides
- **FR3.2:** Bevara slide-ordning och struktur
- **FR3.3:** Extrahera speaker notes
- **FR3.4:** Identifiera slide-titlar
- **✨ FR3.5:** Extrahera bilder från slides
- **✨ FR3.6:** Hantera både Picture och SlidePicture shapes
- **✨ FR3.7:** Spara bilder till `output_folder/pptx_images/slide_X_img_Y.{ext}`

#### FR4: Bildextraktion (JPG/PNG)
- **FR4.1:** OCR med svenska + engelska språkstöd
- **FR4.2:** Extrahera EXIF metadata
- **FR4.3:** Returnera bildstorlek och format
- **⚠️ FR4.4:** Kräver Tesseract systeminstallation (se Installation)

#### FR5: Auto-detektion
- **FR5.1:** Automatisk filformat-detektion via extension
- **FR5.2:** Fallback till MIME-type om extension saknas
- **FR5.3:** Tydligt felmeddelande för ostödda format

#### ✨ FR6: Bildhantering
- **FR6.1:** Automatisk output_folder skapas om den inte finns
- **FR6.2:** Strukturerad namngivning: `{format}_images/{context}_img_{index}.{ext}`
- **FR6.3:** Return paths till alla sparade bilder
- **FR6.4:** Deduplicering av identiska bilder (optional)

---

### Non-Functional Requirements

#### NFR1: Säkerhet
- **NFR1.1:** Inga hårdkodade credentials
- **NFR1.2:** Read-only filaccess för input, Write-only för output_folder
- **NFR1.3:** Input validation för alla filepaths
- **NFR1.4:** Säker hantering av temporära filer
- **NFR1.5:** Logging av alla filoperationer
- **✨ NFR1.6:** Path traversal protection för output_folder

#### NFR2: Performance
- **NFR2.1:** PDF-extraktion < 5 sekunder för 10-sidors dokument (reviderat från 3s)
- **NFR2.2:** Minnesanvändning < 500MB för normala dokument
- **NFR2.3:** Concurrent processing ej nödvändigt (enkelhet prioriteras)
- **✨ NFR2.4:** Bildspara < 2 sekunder för typiska filer (reviderat från 1s)

#### NFR3: Maintainability
- **NFR3.1:** Kod ska vara self-documenting med tydliga kommentarer
- **NFR3.2:** Varje tool ska ha egen funktion (separation of concerns)
- **NFR3.3:** Dependencies ska vara stabila, välunderhållna projekt
- **NFR3.4:** Versionshantering enligt SemVer

#### NFR4: Usability
- **NFR4.1:** Tydliga felmeddelanden på svenska
- **NFR4.2:** JSON output för strukturerad data
- **NFR4.3:** Markdown output för textdata
- **NFR4.4:** Logging till fil för debugging
- **✨ NFR4.5:** Progress feedback för stora filer med många bilder

---

## DESIGN

### Architecture

```
┌─────────────────────────────────────────────────┐
│           Claude Desktop (MCP Client)           │
└────────────────┬────────────────────────────────┘
                 │ STDIO
                 │
┌────────────────▼────────────────────────────────┐
│         CourseExtractor MCP Server              │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  MCP Protocol Handler (FastMCP)          │  │
│  └──────────────┬───────────────────────────┘  │
│                 │                                │
│  ┌──────────────▼───────────────────────────┐  │
│  │  Tool Router                             │  │
│  │  - extract_pdf()                         │  │
│  │  - extract_docx()                        │  │
│  │  - extract_pptx()                        │  │
│  │  - extract_image()                       │  │
│  │  - extract_any()                         │  │
│  └──────────────┬───────────────────────────┘  │
│                 │                                │
│  ┌──────────────▼───────────────────────────┐  │
│  │  Extraction Engines                      │  │
│  │  - pymupdf4llm (PDF text + images!)      │  │
│  │  - python-docx (DOCX text/tables)        │  │
│  │  - docxpy (DOCX images!)                 │  │
│  │  - python-pptx (PPTX text/images)        │  │
│  │  - pytesseract (OCR)                     │  │
│  │  - Pillow (Image handling)               │  │
│  └──────────────┬───────────────────────────┘  │
│                 │                                │
│  ┌──────────────▼───────────────────────────┐  │
│  │  File System                             │  │
│  │  - READ: Input files                     │  │
│  │  - WRITE: output_folder/images/          │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  SYSTEM: Tesseract OCR (brew/apt)        │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

### MCP Tools Specification

#### Tool 1: `extract_pdf`
**Purpose:** Extrahera komplett innehåll från PDF inklusive bilder sparade till disk

**Input Schema:**
```json
{
  "file_path": "string (required)",
  "output_folder": "string (optional, default: '/tmp/course_extractor')",
  "save_images": "boolean (optional, default: true)",
  "include_metadata": "boolean (optional, default: true)",
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
      "format": "string",
      "saved_path": "string",
      "width": "integer",
      "height": "integer"
    }
  ],
  "metadata": {
    "pages": "integer",
    "title": "string",
    "author": "string"
  },
  "output_summary": {
    "total_images": "integer",
    "images_folder": "string"
  }
}
```

**Implementation Details:**
```python
# pymupdf4llm HAR write_images inbyggt!
import pymupdf4llm

md_text = pymupdf4llm.to_markdown(
    doc=file_path,
    write_images=True,
    image_path=f"{output_folder}/pdf_images",
    image_format=image_format,
    dpi=dpi
)
```

---

#### Tool 2: `extract_docx`
**Purpose:** Extrahera text, tabeller OCH bilder från Word-dokument

**Input Schema:**
```json
{
  "file_path": "string (required)",
  "output_folder": "string (optional, default: '/tmp/course_extractor')",
  "save_images": "boolean (optional, default: true)",
  "include_tables": "boolean (optional, default: true)"
}
```

**Output Schema:**
```json
{
  "text": "string",
  "tables": [
    {
      "index": "integer",
      "rows": "integer",
      "cols": "integer",
      "data": "array of arrays"
    }
  ],
  "images": [
    {
      "index": "integer",
      "format": "string",
      "saved_path": "string",
      "description": "string (optional)"
    }
  ],
  "output_summary": {
    "total_images": "integer",
    "images_folder": "string"
  }
}
```

**Implementation Details:**
```python
# Text: python-docx
from docx import Document
doc = Document(file_path)
text = "\n".join([p.text for p in doc.paragraphs])

# Images: docxpy (python-docx KAN INTE extrahera bilder!)
import docxpy
docxpy.process(file_path, f"{output_folder}/docx_images")
```

**CRITICAL NOTE:** python-docx HAR INTE bildextraktion! Vi använder docxpy istället.

---

#### Tool 3: `extract_pptx`
**Purpose:** Extrahera slides inklusive bilder och text

**Input Schema:**
```json
{
  "file_path": "string (required)",
  "output_folder": "string (optional, default: '/tmp/course_extractor')",
  "save_images": "boolean (optional, default: true)",
  "include_notes": "boolean (optional, default: true)"
}
```

**Output Schema:**
```json
{
  "slides": [
    {
      "number": "integer",
      "title": "string",
      "content": "string",
      "notes": "string",
      "images": [
        {
          "index": "integer",
          "type": "string",
          "saved_path": "string"
        }
      ]
    }
  ],
  "output_summary": {
    "total_slides": "integer",
    "total_images": "integer",
    "images_folder": "string"
  }
}
```

**Implementation Details:**
```python
from pptx import Presentation

prs = Presentation(file_path)
for slide_idx, slide in enumerate(prs.slides):
    for shape in slide.shapes:
        if hasattr(shape, "image"):
            # Picture shape
            image_bytes = shape.image.blob
            ext = shape.image.ext
            path = f"{output_folder}/pptx_images/slide_{slide_idx}_img_{i}.{ext}"
            with open(path, "wb") as f:
                f.write(image_bytes)
```

---

#### Tool 4: `extract_image`
**Purpose:** OCR på bilder

**Input Schema:**
```json
{
  "file_path": "string (required)",
  "language": "string (optional, default: 'swe+eng')"
}
```

**Output Schema:**
```json
{
  "text": "string",
  "metadata": {
    "width": "integer",
    "height": "integer",
    "format": "string"
  }
}
```

**System Requirements:**
```bash
# MÅSTE installeras FÖRE pip install pytesseract:
brew install tesseract tesseract-lang  # macOS
apt install tesseract-ocr tesseract-ocr-swe  # Linux
```

---

#### Tool 5: `extract_any`
**Purpose:** Auto-detektera och extrahera från vilken fil som helst

**Input Schema:**
```json
{
  "file_path": "string (required)",
  "output_folder": "string (optional, default: '/tmp/course_extractor')"
}
```

**Output:** Delegerar till rätt tool baserat på extension, inkluderar bildextraktion

---

### Dependencies

**Core:**
```
mcp>=1.0.0              # MCP SDK
```

**Extraction:**
```
pymupdf4llm>=0.0.17     # PDF → Markdown + IMAGES! (MIT license)
python-docx>=1.1.0      # DOCX text/tables (MIT license)
docxpy>=0.8.5           # DOCX images (python-docx kan EJ detta!)
python-pptx>=0.6.23     # PPTX text/images (MIT license)
pytesseract>=0.3.10     # OCR wrapper (Apache 2.0)
Pillow>=10.0.0          # Image handling (HPND license)
```

**System Dependencies (MÅSTE installeras separat):**
```bash
# Tesseract OCR Engine
brew install tesseract tesseract-lang  # macOS
apt install tesseract-ocr tesseract-ocr-swe  # Linux
```

**Total:** 7 Python packages + 1 systeminstallation

**vs MarkItDown:** 20+ Python packages + 1 systeminstallation

---

### File Structure

```
course-extractor-mcp/
├── server.py                 # Main MCP server (~250 rader)
├── extractors/
│   ├── __init__.py
│   ├── pdf_extractor.py     # PDF logic (~80 rader)
│   ├── docx_extractor.py    # DOCX logic (~100 rader)
│   ├── pptx_extractor.py    # PPTX logic (~90 rader)
│   └── image_extractor.py   # OCR logic (~50 rader)
├── utils/
│   ├── __init__.py
│   ├── validation.py        # Input validation (~50 rader)
│   └── logging.py           # Logging setup (~30 rader)
├── requirements.txt          # Dependencies
├── INSTALLATION.md           # Install guide (inkl. Tesseract!)
├── README.md                 # Documentation
├── CHANGELOG.md              # Version history
├── LICENSE                   # MIT License
├── .gitignore                # Git ignore
├── tests/
│   ├── test_pdf.py          # PDF tests
│   ├── test_docx.py         # DOCX tests
│   ├── test_pptx.py         # PPTX tests
│   ├── test_images.py       # Image tests
│   └── fixtures/            # Test files
└── docs/
    ├── SECURITY.md          # Security notes
    └── DEVELOPMENT.md       # Dev guide

TOTAL ESTIMATED: ~450 rader kod
```

---

## INSTALLATION

### Prerequisites

**1. System Dependencies:**
```bash
# macOS
brew install tesseract tesseract-lang

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-swe tesseract-ocr-eng

# Verify installation
tesseract --version
```

**2. Python Environment:**
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install Python packages
pip install -r requirements.txt
```

**3. Claude Desktop Configuration:**
```json
{
  "mcpServers": {
    "course-extractor": {
      "command": "python",
      "args": ["/path/to/course-extractor-mcp/server.py"],
      "env": {}
    }
  }
}
```

---

## SECURITY CONSIDERATIONS

### Threat Model

**Threats:**
1. **Malicious PDFs** - Crafted to exploit PDF parsers
2. **Path Traversal** - `../../etc/passwd` attacks
3. **Resource Exhaustion** - Huge files causing OOM
4. **Dependency Vulnerabilities** - Compromised packages
5. **✨ Output Path Injection** - `../../../sensitive/area` i output_folder
6. **⚠️ Tesseract Exploits** - System-level binary vulnerabilities

**Mitigations:**
1. **Input Validation:**
   - Resolve absolute paths
   - Check file exists before processing
   - Validate file size < 100MB
   - ✨ Validate output_folder path (no traversal)
   - Sanitize filenames
   
2. **Sandboxing:**
   - No shell execution
   - Read-only file access för input
   - ✨ Write-only access för output_folder
   - No network calls
   - Isolate Tesseract calls

3. **Dependency Management:**
   - Pin exact versions in requirements.txt
   - Monthly security audits with `pip-audit`
   - Only use dependencies from PyPI
   - Monitor CVEs for Tesseract

4. **Error Handling:**
   - Never expose full paths in errors
   - Log errors to file, not to user
   - Graceful degradation
   - ✨ Fail safe: Om bildspara misslyckas, returnera text ändå

---

## IMPLEMENTATION PLAN

### Phase 1: Core Infrastructure (20 min)
- [ ] Set up project structure
- [ ] Create MCP server with FastMCP
- [ ] Implement basic tool routing
- [ ] Add logging
- [ ] ✨ Create extractors/ och utils/ modules

### Phase 2: PDF Support with Images (20 min)
- [ ] Implement `extract_pdf()` med pymupdf4llm
- [ ] ✨ Konfigurera write_images=True
- [ ] ✨ Verify bildspara funkar
- [ ] Add metadata extraction
- [ ] Test with course materials

### Phase 3: DOCX with Images (30 min)
- [ ] Implement `extract_docx()` text med python-docx
- [ ] Add table extraction
- [ ] ✨ Integrera docxpy för bilder
- [ ] ✨ Hantera docxpy errors gracefully
- [ ] Test with real files

### Phase 4: PPTX with Images (20 min)
- [ ] Implement `extract_pptx()` text
- [ ] Extract speaker notes
- [ ] ✨ Extract bilder via shape.image.blob
- [ ] ✨ Hantera både Picture och SlidePicture
- [ ] Test med svenska presentationer

### Phase 5: Image OCR (15 min)
- [ ] Verify Tesseract installation
- [ ] Implement `extract_image()`
- [ ] Configure Swedish language support
- [ ] Test with course images
- [ ] Document Tesseract requirement

### Phase 6: Integration & Testing (15 min)
- [ ] Implement `extract_any()` router
- [ ] Create Claude Desktop config
- [ ] End-to-end testing med bildextraktion
- [ ] Documentation
- [ ] ✨ Test output folder structure
- [ ] Security audit

**Total:** 120 minutes (2 timmar) - **REALISTISKT**

---

## TESTING STRATEGY

### Unit Tests
```python
# tests/test_pdf.py
def test_extract_pdf_text():
    result = extract_pdf("fixtures/sample.pdf")
    assert "text_markdown" in result
    assert len(result["text_markdown"]) > 0

def test_extract_pdf_images_saved():
    result = extract_pdf("fixtures/sample_with_images.pdf", 
                        output_folder="/tmp/test")
    assert len(result["images"]) > 0
    for img in result["images"]:
        assert Path(img["saved_path"]).exists()

# tests/test_docx.py
def test_docx_images_with_docxpy():
    """Verify docxpy integration works"""
    result = extract_docx("fixtures/document_with_images.docx")
    assert len(result["images"]) > 0
    
# tests/test_system.py
def test_tesseract_installed():
    """Verify Tesseract is installed on system"""
    import subprocess
    result = subprocess.run(["tesseract", "--version"], 
                          capture_output=True)
    assert result.returncode == 0
```

---

## EDGE CASES & ERROR HANDLING

| Scenario | Handling |
|----------|----------|
| Krypterade PDFs | Raise error: "Krypterad PDF ej stödd" |
| Skannade PDFs utan text-layer | pymupdf4llm hanterar automatiskt |
| Korrupta DOCX-filer | Try/catch → graceful error message |
| Filer > 100MB | Reject before processing |
| Timeout för långsamma operationer | Implement 60s timeout per file |
| Tesseract ej installerat | Clear error: "Installera Tesseract först" |
| docxpy misslyckas | Fallback: returnera text utan bilder |
| Output folder permissions | Create if possible, else error |

---

## FUTURE ENHANCEMENTS

### v1.1 (Q2 2026)
- [ ] Batch processing (multiple files)
- [ ] Progress callbacks for large files
- [ ] Caching layer for repeated extractions
- [ ] ✨ Image deduplication (same image in multiple slides)
- [ ] Parallel processing for PPTX slides

### v1.2 (Q3 2026)
- [ ] Excel support (.xlsx)
- [ ] CSV export options
- [ ] Custom templates for output
- [ ] ✨ Image optimization (resize, compress)
- [ ] Alternative till Tesseract (tesseract.js?)

### v2.0 (Q4 2026)
- [ ] Web interface for testing
- [ ] API mode (HTTP server)
- [ ] Plugin system for custom extractors
- [ ] ✨ OCR on extracted images automatically
- [ ] Docker container (inkl. Tesseract)

---

## ALTERNATIVES CONSIDERED

### Alternative 1: Use MarkItDown
**Pros:** Already exists, feature-complete  
**Cons:** Many dependencies, not optimized for Swedish, black-box  
**Decision:** Build custom for learning + control

### Alternative 2: Spire.Doc/Spire.Presentation
**Pros:** Commercial-grade, comprehensive
**Cons:** Kommersiellt (free tier har watermarks), stora dependencies
**Decision:** Använd docxpy (free, MIT) istället

### Alternative 3: Shell scripts + pandoc
**Pros:** Minimal dependencies  
**Cons:** No MCP integration, limited extraction capabilities  
**Decision:** Not sophisticated enough

### Alternative 4: Aspose.Words/Slides
**Pros:** Enterprise-grade
**Cons:** Kommersiellt, dyrt, overkill för vårt use case
**Decision:** Alltför dyrt för learning project

---

## SUCCESS METRICS

**Launch (Week 1):**
- ✅ All tools working
- ✅ No crashes on test files
- ✅ Integration with Claude Desktop
- ✅ ✨ Images extracted from PDF, DOCX, PPTX
- ✅ Tesseract working for Swedish OCR

**Adoption (Month 1):**
- ✅ Used for M1 material analysis
- ✅ Zero security incidents
- ✅ < 1 bug per week
- ✅ ✨ All course material images captured
- ✅ Dokumentation komplett

**Quality (Month 3):**
- ✅ 95%+ accurate text extraction
- ✅ 90%+ image extraction success rate
- ✅ Swedish OCR working reliably
- ✅ Positive feedback from use
- ✅ Community contributions (om öppen källkod)

---

## CHANGELOG

### [3.0.0] - 2026-01-20 (CRITICAL REVISION)
- 🔴 **BREAKING:** Lagt till `docxpy` (python-docx kan INTE extrahera bilder!)
- ⚠️ **BREAKING:** Dokumenterat Tesseract systeminstallation
- ✅ Verifierat alla dependencies mot faktiska capabilities
- ✅ Uppdaterat tidsestimat: 120 min (från 65 min)
- ✅ Uppdaterat kodestimat: 450 rader (från 200)
- ✅ Lagt till edge case handling
- ✅ Förbättrad error handling specification
- ✅ Lagt till Installation-sektion med Tesseract

### [2.0.0] - 2026-01-20
- ✨ Added full image extraction with disk save
- ✨ Added output_folder parameter to all tools
- Updated implementation plan (+20 min for image features)

### [1.0.0] - 2026-01-20
- Initial RFC draft
- Core design finalized
- Basic extraction plan

---

## CRITICAL NOTES

**⚠️ DOCX Images:**
- python-docx KAN INTE extrahera bilder (Issue #108 från 2014)
- Vi använder `docxpy` istället - verifierat att det fungerar
- Fallback: Om docxpy misslyckas, returnera text utan bilder

**⚠️ Tesseract:**
- MÅSTE installeras via system package manager
- INTE bara `pip install` - detta är en systeminstallation
- Testa med `tesseract --version` före användning
- Dokumentera tydligt i README

**✅ PDF Images:**
- pymupdf4llm HAR `write_images=True` inbyggt!
- Funkar perfekt out-of-the-box
- Ingen extra kod behövs

**✅ PPTX Images:**
- python-pptx KAN extrahera bilder via `shape.image.blob`
- Funkar för både Picture och SlidePicture shapes
- Verifierat i dokumentation

---

## REFERENCES

- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [pymupdf4llm](https://github.com/pymupdf/pymupdf4llm)
- [pymupdf4llm API - write_images](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/api.html)
- [python-docx](https://python-docx.readthedocs.io/)
- [docxpy (DOCX images)](https://pypi.org/project/docxpy/)
- [python-pptx](https://python-pptx.readthedocs.io/)
- [python-pptx Image API](https://python-pptx.readthedocs.io/en/latest/api/image.html)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [pytesseract](https://pypi.org/project/pytesseract/)

---

**END OF RFC-001 v3.0**

**NEXT STEPS:**
1. Review denna RFC
2. Installera Tesseract (`brew install tesseract tesseract-lang`)
3. Skapa projektstruktur
4. Börja implementation enligt 120-minuters plan
