# RFC-017: Entry Point for Existing Questions

**Status:** Draft → Ready for Implementation
**Created:** 2026-01-29
**Updated:** 2026-01-30
**Author:** Niklas Karlsson + Claude
**Related:** RFC-014 (Resource Handling), RFC-016 (M5 Self-Learning Format Recognition)
**Scrutiny:** Passed with revisions (2026-01-30)

---

## Summary

Add a new entry point `questions` to `step0_start` for teachers who already have existing questions in various formats (Word, Excel, PDF, etc.) and may have accompanying resources (images, audio, etc.).

---

## Problem

Current entry points assume a specific workflow:

| Entry Point | Assumption | Problem |
|-------------|------------|---------|
| m1 | Teacher has materials, no questions | What if questions exist? |
| m2 | Teacher has learning objectives | What if questions exist? |
| m3 | Teacher has blueprint, will generate | What if questions exist? |
| m4 | Teacher has QFMD questions | What if not in QFMD? |
| pipeline | Teacher has validated QFMD | What if not validated? |

**Missing scenario:** Teacher has existing questions in arbitrary format (Word, Excel, PDF, etc.) that need to be processed.

---

## Proposed Solution

### New Entry Point: `questions`

```python
step0_start(
    entry_point="questions",
    source_file="source_converted.md",    # Markdown (efter MarkItDown-konvertering)
    resources_folder="/path/to/images/",  # Optional: accompanying resources
    output_folder="/path/to/projects",
    project_name="Matematik_Prov1"        # Optional
)
```

**OBS:** `source_file` ska vara markdown. Claude konverterar via MarkItDown MCP FÖRE step0_start.

### Supported Formats

| Type | Formats | Notes |
|------|---------|-------|
| Questions | `.docx`, `.xlsx`, `.txt`, `.pdf`, `.md`, `.csv`, `.rtf` | Converted via MarkItDown if needed |
| Resources | `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.mp3`, `.wav`, `.ogg`, `.m4a`, `.mp4`, `.webm` | Copied to resources folder |

**Note:** `.pdf` in `resources_folder` = resource. `.pdf` as `source_file` = questions.

### Project Structure

```
Matematik_Prov1_abc123/
├── session.yaml
├── sources.yaml
├── logs/
│   └── session.jsonl
├── questions/
│   ├── source_original.docx      ← Original file (preserved)
│   ├── source_converted.md       ← After format conversion (auto or manual)
│   ├── m5_output.md              ← After M5 processing
│   └── resources/                ← Question resources
│       ├── figur1.png
│       ├── diagram.pdf
│       └── audio_q5.mp3
├── pipeline/
│   └── working.md
└── output/
    └── qti_package.zip
```

---

## Key Decisions (Resolved)

### Decision 1: Conversion via Separate MarkItDown MCP

**DECIDED:** Claude orkestrerar konvertering via separat MarkItDown MCP (inte integrerat i qf-pipeline)

**Arkitektur:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CLAUDE DESKTOP                                                             │
│       │                                                                     │
│       ├── MarkItDown MCP ──── convert_to_markdown(uri)                     │
│       │         │                                                           │
│       │         ↓                                                           │
│       │    docx/xlsx/pdf → markdown                                        │
│       │         │                                                           │
│       │         ↓                                                           │
│       │    Sparar till: questions/source_converted.md                      │
│       │                                                                     │
│       └── qf-pipeline MCP ── step0_start(source_file="source_converted.md")│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Workflow (Claude orkestrerar):**
```python
# Steg 1: Lärare ger Claude en Word-fil
# "Konvertera prov.docx och skapa QF-projekt"

# Steg 2: Claude anropar MarkItDown MCP
markdown_content = convert_to_markdown("file:///Users/.../prov.docx")

# Steg 3: Claude sparar till projektmappen
# Sparar till: /Nextcloud/Courses/.../questions/source_converted.md

# Steg 4: Claude anropar qf-pipeline
step0_start(
    entry_point="questions",
    source_file="/Nextcloud/Courses/.../questions/source_converted.md",
    resources_folder="/path/to/bilder/"  # Optional
)
```

**Fördelar med separat MCP:**
- Inga extra dependencies i qf-pipeline
- MarkItDown underhålls av Microsoft
- Claude har full kontroll över processen
- Filen sparas permanent (inte temp)

**Krav:**
- MarkItDown MCP måste vara installerad och konfigurerad i Claude Desktop
- Filesystem MCP behövs för att spara den konverterade filen

### Decision 2: Resource Linking in QFMD

**DECIDED:** Relative paths with `resources/` prefix

```markdown
^id Q001
^type multiple_choice_single
^title Fotosyntesdiagram

# Stem
Se på diagrammet nedan och identifiera delen märkt X:

![Fotosyntesdiagram](resources/photosynthesis_diagram.png)

# Options
* Kloroplast [correct]
* Mitokondrie
* Cellkärna
* Vakuol
```

**Syntax by resource type:**
| Type | Syntax | Example |
|------|--------|---------|
| Image | `![alt](resources/file.png)` | `![Diagram](resources/fig1.png)` |
| Audio | `[audio](resources/file.mp3)` | `[Lyssna](resources/question5.mp3)` |
| Video | `[video](resources/file.mp4)` | `[Se klipp](resources/experiment.mp4)` |
| PDF ref | `[pdf](resources/file.pdf)` | `[Referens](resources/table.pdf)` |

**Export behavior:**
- QTI exporter resolves paths relative to `questions/resources/`
- Resources embedded in QTI package
- Validates resource existence before export

### Decision 3: PDF Format Disambiguation

**DECIDED:** Context determines interpretation

| Parameter | PDF Interpretation |
|-----------|-------------------|
| `source_file="questions.pdf"` | Questions document → `questions/source_original.pdf` |
| `resources_folder="./bilder/"` containing `ref.pdf` | Resource → `questions/resources/ref.pdf` |

**Rule:** `source_file` is ALWAYS questions. Files in `resources_folder` are ALWAYS resources.

### Decision 4: Conversion Pipeline Responsibilities

**DECIDED:** Clear separation of concerns

```
┌─────────────────────────────────────────────────────────────────┐
│  CONVERSION PIPELINE                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MarkItDown MCP          M5 (RFC-016)           Pipeline        │
│  ───────────────         ───────────            ────────        │
│  docx → markdown         markdown → QFMD        QFMD → QTI      │
│  xlsx → markdown         format detection       validation      │
│  pdf  → markdown         field normalization    export          │
│                          self-learning                          │
│                                                                 │
│  [Technical conversion]  [Format recognition]   [Export]        │
└─────────────────────────────────────────────────────────────────┘
```

**M5 does NOT receive docx/xlsx/pdf** - that's MarkItDown's job.

---

## Error Handling

### Error Scenarios

| Scenario | Behavior | User Message |
|----------|----------|--------------|
| Source file not found | ABORT | `"Källfil hittades inte: {path}"` |
| Source file unreadable | ABORT | `"Kan inte läsa källfil: åtkomst nekad"` |
| Source file not markdown | WARNING | `"⚠️ Källfil är inte markdown. Claude bör konvertera via MarkItDown MCP först."` |
| Resources folder not found | CONTINUE (warning) | `"⚠️ Resursmapp hittades inte, fortsätter utan resurser"` |
| Resource file too large (>50MB) | SKIP file (warning) | `"⚠️ Hoppade över 'video.mp4' (85MB > 50MB gräns)"` |
| Total resources too large (>500MB) | ABORT | `"Totala resurser 650MB överskrider 500MB gräns"` |
| Duplicate resource names | ABORT | `"Dublett: 'fig1.png' finns redan i resursmappen"` |

**OBS:** Konverteringsfel hanteras av Claude + MarkItDown MCP, inte av qf-pipeline.

### Resource Limits

```python
RESOURCE_LIMITS = {
    "max_file_mb": 50,      # Single file limit - REJECT if exceeded
    "max_total_mb": 500,    # Total project resources - REJECT if exceeded
    "warn_file_mb": 10,     # Warning threshold - WARN but copy
}
```

### Rollback on Failure

```python
try:
    # 1. Create project structure
    project_path = create_project_folder(output_folder, project_name)

    # 2. Copy source file
    copy_source_file(source_file, project_path)

    # 3. Copy resources
    if resources_folder:
        copy_resources(resources_folder, project_path)

    # 4. Auto-convert if enabled
    if auto_convert and not is_markdown(source_file):
        convert_with_markitdown(project_path)

    # 5. Create session.yaml
    session.save()

except Exception as e:
    # Rollback: delete incomplete project
    if project_path.exists():
        shutil.rmtree(project_path)
    log_error("project_creation_failed", str(e))
    raise
```

---

## Workflow

### Komplett Workflow (Claude Orkestrerar)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEG 1: Lärare ber om hjälp                                                │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Lärare: "Jag har ett prov i Word-format som jag vill göra om till Inspera"│
│          📎 Fil: /Nextcloud/Courses/Matematik/prov.docx                     │
│          📎 Bilder: /Nextcloud/Courses/Matematik/bilder/                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEG 2: Claude konverterar med MarkItDown MCP                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Claude: "Jag konverterar Word-filen till markdown..."                      │
│                                                                             │
│  → Anropar MarkItDown: convert_to_markdown("file:///Nextcloud/.../prov.docx")│
│  → Får tillbaka markdown-text                                               │
│  → Sparar till: /Nextcloud/Courses/Matematik/questions/source_converted.md │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEG 3: Claude skapar QF-projekt med qf-pipeline MCP                       │
│  ─────────────────────────────────────────────────────────────────────────  │
│  → Anropar qf-pipeline: step0_start(                                        │
│        entry_point="questions",                                             │
│        source_file="/Nextcloud/.../questions/source_converted.md",          │
│        resources_folder="/Nextcloud/.../bilder/"                            │
│     )                                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEG 4: qf-pipeline returnerar projektinfo                                 │
│  ─────────────────────────────────────────────────────────────────────────  │
│ ✅ PROJEKT SKAPAT                                                           │
│ 📁 Projekt: Matematik_Prov1_abc123/                                         │
│ 📄 Frågor:  questions/source_converted.md                                   │
│ 🖼️  Resurser: questions/resources/ (8 filer, 2.3 MB)                        │
│                                                                             │
│ ════════════════════════════════════════════════════════════════════════   │
│ 📋 VAD VILL DU GÖRA MED FRÅGORNA?                                           │
│ ────────────────────────────────────────────────────────────────────────── │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────┐    │
│ │ 1️⃣  DEFINIERA TAXONOMI (→ M2)                                       │    │
│ │     Välj detta om frågorna saknar taggar/kategorier                 │    │
│ ├─────────────────────────────────────────────────────────────────────┤    │
│ │ 2️⃣  GRANSKA & METADATA (→ M4)                                       │    │
│ │     Välj detta om frågorna behöver Bloom-nivåer, svårighetsgrad     │    │
│ ├─────────────────────────────────────────────────────────────────────┤    │
│ │ 3️⃣  KONVERTERA DIREKT (→ M5 → Pipeline)                             │    │
│ │     Välj detta om frågorna redan har all metadata                   │    │
│ └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│ 💡 Tips: Berätta vad som finns i dina frågor så hjälper jag dig välja!     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Decision Criteria

| Fråga | Om JA → | Om NEJ → |
|-------|---------|----------|
| Har frågorna taggar/kategorier? | Fortsätt | → M2 (definiera taxonomi) |
| Har frågorna Bloom-nivåer? | Fortsätt | → M4 (lägg till) |
| Har frågorna svårighetsgrad? | Fortsätt | → M4 (lägg till) |
| Är formatet korrekt (QFMD-liknande)? | → M5 → Pipeline | → M5 (format-konvertering) |

### Decision Flow

```
                         ┌──────────────┐
                         │  questions   │
                         │ entry point  │
                         └──────┬───────┘
                                │
                         ┌──────┴───────┐
                         │ auto_convert │
                         │  (default)   │
                         └──────┬───────┘
                                │
                    ┌───────────┼───────────┐
                    ↓           ↓           ↓
             ┌──────────┐ ┌──────────┐ ┌──────────┐
             │   M2     │ │   M4     │ │   M5     │
             │ Taxonomi │ │   QA     │ │  Format  │
             │ saknas   │ │ granska  │ │ convert  │
             └────┬─────┘ └────┬─────┘ └────┬─────┘
                  │            │            │
                  └────────────┼────────────┘
                               ↓
                         ┌──────────┐
                         │    M5    │
                         │  QFMD    │
                         └────┬─────┘
                              ↓
                    ┌─────────────────┐
                    │    Pipeline     │
                    │  Step 2 → 3 → 4 │
                    └─────────────────┘
```

---

## Implementation

### Phase 1: Core Entry Point

**File:** `packages/qf-pipeline/src/qf_pipeline/server.py`

```python
# Update step0_start schema
"entry_point": {
    "type": "string",
    "enum": ["m1", "m2", "m3", "m4", "questions", "pipeline"],
    "description": (
        "Entry point: "
        "'m1' (materials), 'm2' (objectives), 'm3' (blueprint), "
        "'m4' (QA), 'questions' (existing questions), 'pipeline' (QFMD ready)"
    ),
},
"resources_folder": {
    "type": "string",
    "description": "Path to folder with resources (images, audio) for questions",
},
# OBS: Ingen auto_convert parameter - Claude konverterar via MarkItDown MCP först
```

**File:** `packages/qf-pipeline/src/qf_pipeline/utils/session_manager.py`

```python
def create_session_for_questions(
    output_folder: Path,
    source_file: Path,
    resources_folder: Optional[Path] = None,
    project_name: Optional[str] = None,
) -> Session:
    """Create session for 'questions' entry point.

    OBS: source_file ska vara markdown (Claude konverterar via MarkItDown MCP först).
    """

    # Validate source file exists
    if not source_file.exists():
        raise FileNotFoundError(f"Källfil hittades inte: {source_file}")

    if not source_file.is_file():
        raise ValueError(f"Källfil är inte en fil: {source_file}")

    # Warn if not markdown (Claude should have converted first)
    if source_file.suffix.lower() not in [".md", ".markdown"]:
        log_warning("non_markdown_source",
            f"source_file '{source_file.name}' är inte markdown. "
            "Claude bör konvertera via MarkItDown MCP först.")

    project_path = None
    try:
        # 1. Create project structure
        project_path = create_project_folder(output_folder, project_name)

        # 2. Create questions directory
        questions_dir = project_path / "questions"
        questions_dir.mkdir(exist_ok=True)

        # 3. Copy source file (already markdown from MarkItDown)
        dest_source = questions_dir / f"source_converted{source_file.suffix}"
        shutil.copy2(source_file, dest_source)

        # 4. Copy resources if provided
        resources_result = None
        if resources_folder:
            if resources_folder.exists():
                dest_resources = questions_dir / "resources"
                resources_result = copy_resources(resources_folder, dest_resources)
            else:
                log_warning("resources_folder_not_found", str(resources_folder))

        # 5. Create session
        session = Session(
            project_path=project_path,
            entry_point="questions",
            source_file=dest_source,
            resources=resources_result,
        )
        session.save()

        # 6. Log success
        log_event("project_created", {
            "entry_point": "questions",
            "source_file": str(dest_source),
            "resources_copied": resources_result["copied"] if resources_result else [],
        })

        return session

    except Exception as e:
        # Rollback on failure
        if project_path and project_path.exists():
            shutil.rmtree(project_path)
        log_error("project_creation_failed", str(e))
        raise
```

### Phase 2: Resource Handling

**File:** `packages/qf-pipeline/src/qf_pipeline/utils/resources.py` (NEW)

```python
from pathlib import Path
import shutil
from typing import Optional

ALLOWED_RESOURCE_EXTENSIONS = {
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
    # Audio
    ".mp3", ".wav", ".ogg", ".m4a",
    # Video
    ".mp4", ".webm",
    # Documents (as resources, not questions)
    ".pdf",
}

RESOURCE_LIMITS = {
    "max_file_mb": 50,
    "max_total_mb": 500,
    "warn_file_mb": 10,
}


def copy_resources(src_folder: Path, dest_folder: Path) -> dict:
    """
    Copy resources from source to destination with validation.

    Returns:
        {
            "copied": ["figur1.png", "audio.mp3"],
            "skipped": ["notes.txt"],
            "warnings": ["large_video.mp4 is 45MB"],
            "total_size_mb": 12.5,
            "max_file_mb": 45.0,
        }

    Raises:
        ValueError: If total size exceeds limit or duplicate names found.
    """
    dest_folder.mkdir(parents=True, exist_ok=True)

    copied = []
    skipped = []
    warnings = []
    total_size = 0
    max_file_size = 0
    seen_names = set()

    for file in src_folder.iterdir():
        if not file.is_file():
            continue

        # Check for duplicates
        if file.name.lower() in seen_names:
            raise ValueError(f"Dublett: '{file.name}' finns redan")
        seen_names.add(file.name.lower())

        # Check extension
        if file.suffix.lower() not in ALLOWED_RESOURCE_EXTENSIONS:
            skipped.append(file.name)
            continue

        # Check file size
        file_size_mb = file.stat().st_size / (1024 * 1024)

        if file_size_mb > RESOURCE_LIMITS["max_file_mb"]:
            skipped.append(file.name)
            warnings.append(f"Hoppade över '{file.name}' ({file_size_mb:.1f}MB > {RESOURCE_LIMITS['max_file_mb']}MB)")
            continue

        if file_size_mb > RESOURCE_LIMITS["warn_file_mb"]:
            warnings.append(f"'{file.name}' är {file_size_mb:.1f}MB (stor fil)")

        # Check total size
        if total_size + file.stat().st_size > RESOURCE_LIMITS["max_total_mb"] * 1024 * 1024:
            raise ValueError(
                f"Totala resurser överskrider {RESOURCE_LIMITS['max_total_mb']}MB gräns"
            )

        # Copy file
        shutil.copy2(file, dest_folder / file.name)
        copied.append(file.name)
        total_size += file.stat().st_size
        max_file_size = max(max_file_size, file.stat().st_size)

    return {
        "copied": copied,
        "skipped": skipped,
        "warnings": warnings,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "max_file_mb": round(max_file_size / (1024 * 1024), 2),
    }
```

### Phase 3: MarkItDown MCP (Separat Installation)

**OBS:** MarkItDown är en SEPARAT MCP-server, inte integrerad i qf-pipeline.

**Installation:** Se `docs/guides/markitdown-mcp-installation.md`

**Claude Desktop konfiguration:**
```json
{
  "mcpServers": {
    "markitdown": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-v", "/Users/niklaskarlsson/Nextcloud/Courses:/workdir:ro",
        "markitdown-mcp:latest"
      ]
    }
  }
}
```

**Hur Claude använder det:**
```python
# Claude anropar MarkItDown MCP
markdown_content = convert_to_markdown("file:///workdir/Matematik/prov.docx")

# Claude sparar resultatet till projektmappen
# (via Filesystem MCP eller direkt i chatten)
# Sparar till: /Nextcloud/Courses/Matematik/questions/source_converted.md

# Sen anropar Claude qf-pipeline
step0_start(
    entry_point="questions",
    source_file="/Nextcloud/Courses/Matematik/questions/source_converted.md"
)
```

---

## Session.yaml Updates

```yaml
session:
  session_id: "abc123"
  entry_point: "questions"
  status: "active"
  created_at: "2026-01-29T15:30:00Z"

  source:
    # OBS: Filen är redan markdown (Claude konverterade via MarkItDown MCP)
    file: "questions/source_converted.md"
    original_format: "md"
    # Original-filen (docx/pdf) ligger kvar i Nextcloud, inte kopierad hit

  resources:
    folder: "questions/resources/"
    count: 12
    total_size_mb: 8.5
    max_file_mb: 3.2
    validated_at: "2026-01-29T15:30:05Z"
    skipped_files:
      - "notes.txt"
      - "backup.zip"
    warnings:
      - "video.mp4 är 45MB (stor fil)"
    files:  # First 20 shown
      - "figur1.png"
      - "figur2.png"
      - "diagram.pdf"
      - "audio_q5.mp3"
      # ... and 8 more
```

---

## Integration with Existing RFCs

| RFC | Integration |
|-----|-------------|
| RFC-014 (Resource Handling) | Uses same resource extensions, complements with entry point |
| RFC-016 (M5 Format Recognition) | M5 processes `source_converted.md`, not original format |
| RFC-001 (Unified Logging) | Events: `project_created`, `resources_copied`, `conversion_complete` |

---

## User Stories (Updated)

### US-1: Teacher with Word Document
> "Jag har ett prov i Word-format med 20 frågor. Frågorna har svar men saknar Bloom-nivåer."

1. `step0_start(entry_point="questions", source_file="prov.docx")`
2. System auto-converts docx → markdown
3. System analyzes and detects: "20 frågor, saknar Bloom-nivåer"
4. System suggests: "Frågorna behöver metadata → Använd M4"
5. Teacher CHOOSES M4 (or can override to M2 or M5)
6. Teacher runs M4 to add Bloom levels
7. Then M5 → Pipeline → QTI export

### US-2: Teacher with Excel + Images
> "Jag har en frågebank i Excel och en mapp med bilder som används i frågorna."

1. `step0_start(entry_point="questions", source_file="bank.xlsx", resources_folder="./bilder/")`
2. System copies and converts:
   - `questions/source_original.xlsx`
   - `questions/source_converted.md`
   - `questions/resources/` (12 images)
3. Teacher updates QFMD to reference images: `![](resources/fig1.png)`
4. Then M5 → Pipeline → QTI export (resources embedded)

### US-3: Teacher with Complete Markdown Questions
> "Jag har frågor i markdown-format med all metadata. Vill bara exportera."

1. `step0_start(entry_point="questions", source_file="fragor.md")`
2. System detects markdown, skips conversion
3. System analyzes: "Frågorna ser kompletta ut (har Bloom, difficulty, tags)"
4. System suggests: "Direkt till M5 för format-validering"
5. M5 validates → Pipeline Step 2 → Step 3 → Step 4 → QTI export

---

## Verification (Complete Tests)

### Test 1: Basic Entry Point

```bash
#!/bin/bash
# Test 1: Basic entry point with Word file

TEST_DIR=/tmp/test_rfc017_t1
rm -rf $TEST_DIR
mkdir -p $TEST_DIR

# Create test file (simulate Word doc)
echo "Question 1: What is 2+2?" > $TEST_DIR/test.docx

# Run via Python
python3 << 'EOF'
import sys
sys.path.insert(0, '/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qf-pipeline/src')
from qf_pipeline.utils.session_manager import create_session_for_questions
from pathlib import Path

session = create_session_for_questions(
    output_folder=Path("/tmp/test_rfc017_t1/output"),
    source_file=Path("/tmp/test_rfc017_t1/test.docx"),
    auto_convert=False  # Skip MarkItDown for basic test
)
print(f"Project created: {session.project_path}")
EOF

# Verify structure
PROJECT_DIR=$(ls -d /tmp/test_rfc017_t1/output/*/ 2>/dev/null | head -1)
test -f "$PROJECT_DIR/session.yaml" && echo "✅ session.yaml exists" || echo "❌ session.yaml missing"
test -f "$PROJECT_DIR/questions/source_original.docx" && echo "✅ source copied" || echo "❌ source missing"
test -d "$PROJECT_DIR/questions/resources" && echo "✅ resources dir exists" || echo "❌ resources dir missing"

echo "✅ Test 1 PASSED"
```

### Test 2: With Resources

```bash
#!/bin/bash
# Test 2: Entry point with resources folder

TEST_DIR=/tmp/test_rfc017_t2
rm -rf $TEST_DIR
mkdir -p $TEST_DIR/images

# Create test files
echo "Question doc" > $TEST_DIR/test.docx
echo "PNG" > $TEST_DIR/images/fig1.png
echo "JPG" > $TEST_DIR/images/fig2.jpg
echo "TXT" > $TEST_DIR/images/notes.txt  # Should be SKIPPED

# Run
python3 << 'EOF'
import sys
sys.path.insert(0, '/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qf-pipeline/src')
from qf_pipeline.utils.session_manager import create_session_for_questions
from pathlib import Path

session = create_session_for_questions(
    output_folder=Path("/tmp/test_rfc017_t2/output"),
    source_file=Path("/tmp/test_rfc017_t2/test.docx"),
    resources_folder=Path("/tmp/test_rfc017_t2/images"),
    auto_convert=False
)
print(f"Resources: {session.resources}")
EOF

# Verify
PROJECT_DIR=$(ls -d /tmp/test_rfc017_t2/output/*/ 2>/dev/null | head -1)
test -f "$PROJECT_DIR/questions/resources/fig1.png" && echo "✅ fig1.png copied" || echo "❌ fig1.png missing"
test -f "$PROJECT_DIR/questions/resources/fig2.jpg" && echo "✅ fig2.jpg copied" || echo "❌ fig2.jpg missing"
test ! -f "$PROJECT_DIR/questions/resources/notes.txt" && echo "✅ notes.txt skipped" || echo "❌ notes.txt should be skipped"

echo "✅ Test 2 PASSED"
```

### Test 3: Full Workflow

```bash
#!/bin/bash
# Test 3: Complete workflow from questions entry point to QTI export

TEST_DIR=/tmp/test_rfc017_t3
rm -rf $TEST_DIR
mkdir -p $TEST_DIR

# Create realistic test markdown (simulating converted content)
cat > $TEST_DIR/questions.md << 'MARKDOWN'
# Prov: Matematik Grund

---

^id Q001
^type multiple_choice_single
^bloom understand
^difficulty medium

# Stem
Vad är 2 + 2?

# Options
* 3
* 4 [correct]
* 5
* 6

---

^id Q002
^type multiple_choice_single
^bloom apply
^difficulty easy

# Stem
Beräkna arean av en rektangel med sidorna 3 och 4.

# Options
* 7
* 10
* 12 [correct]
* 14

---
MARKDOWN

echo "=== Step 1: Create project ==="
# In Claude Desktop, this would be:
# step0_start(entry_point="questions", source_file="questions.md")

echo "=== Step 2: M5 processing ==="
# m5_start(project_path="...")
# m5_detect_format()  → Detects QFMD-like format
# m5_analyze()        → Parses 2 questions
# m5_approve()        → Teacher approves
# m5_finish()         → Saves m5_output.md

echo "=== Step 3: Pipeline ==="
# step2_validate()    → Validates QFMD
# step3_autofix()     → Fixes any issues
# step4_export()      → Generates QTI package

echo "✅ Test 3 workflow documented"
```

---

## Timeline

| Phase | Description | Estimate |
|-------|-------------|----------|
| 1 | Core entry point `questions` | 1.5h |
| 2 | Resource copying with validation | 1.5h |
| 3 | Session.yaml updates | 0.5h |
| 4 | Error handling + rollback | 0.5h |
| 5 | Integration testing | 1h |
| **Subtotal qf-pipeline** | | **5h** |
| 6 | MarkItDown MCP installation (separat) | 1h |
| **Total** | | **6h** |

**OBS:** Konverteringslogik är nu i MarkItDown MCP (separat), inte i qf-pipeline.

---

## Summary

RFC-017 introduces:
1. **New entry point `questions`** for existing questions (markdown format)
2. **`resources_folder` parameter** for accompanying images/audio
3. **Claude-orkestrerad konvertering** via separat MarkItDown MCP
4. **Flexible routing** to M2, M4, or M5 based on teacher needs
5. **`questions/resources/` folder** in project structure
6. **Resource linking syntax** in QFMD: `![](resources/filename)`
7. **Comprehensive error handling** with rollback on failure

**Arkitektur:**
- MarkItDown MCP (separat): docx/xlsx/pdf → markdown
- qf-pipeline: tar emot markdown, hanterar resurser, kör M5 → Pipeline
- Claude: orkestrerar hela flödet

This fills the gap for teachers who have existing questions but don't fit the current M1→M2→M3→M4→Pipeline workflow.

---

*RFC-017 created 2026-01-29, updated 2026-01-30 (MarkItDown som separat MCP, Claude orkestrerar)*
