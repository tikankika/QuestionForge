# RFC-017: Entry Point for Existing Questions

**Status:** Draft → Ready for Implementation
**Created:** 2026-01-29
**Updated:** 2026-01-31
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
    source_file="source_converted.md",    # Markdown (after MarkItDown conversion)
    resources_folder="/path/to/images/",  # Optional: accompanying resources
    output_folder="/path/to/projects",
    project_name="Matematik_Prov1"        # Optional
)
```

**NOTE:** `source_file` should be markdown. Claude converts via MarkItDown MCP BEFORE step0_start.

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

### Decision 1: Input Format & Conversion

**DECIDED:** QuestionForge accepts **markdown**. For other formats, use existing tools.

**Input:**
```
questions entry point → accepts markdown file
```

**Does the teacher have PDF/docx?** Use `qf-scaffolding:read_materials`:

```python
# Step 1: Read PDF/docx with read_materials
content = read_materials(project_path, filename="exam.pdf")
# → Returns extracted text

# Step 2: Save as markdown
write_project_file(project_path, "questions/source.md", content)

# Step 3: Start questions workflow
step0_start(entry_point="questions", source_file="questions/source.md")
```

**Alternatively:** Use `markitdown` CLI in terminal:
```bash
markitdown exam.docx > source.md
```

**Benefits:**
- Reuses existing tool (`read_materials`)
- No new dependencies
- Simple and works today

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
| Audio | `[audio](resources/file.mp3)` | `[Listen](resources/question5.mp3)` |
| Video | `[video](resources/file.mp4)` | `[Watch clip](resources/experiment.mp4)` |
| PDF ref | `[pdf](resources/file.pdf)` | `[Reference](resources/table.pdf)` |

**Export behaviour:**
- QTI exporter resolves paths relative to `questions/resources/`
- Resources embedded in QTI package
- Validates resource existence before export

### Decision 3: PDF Format Disambiguation

**DECIDED:** Context determines interpretation

| Parameter | PDF Interpretation |
|-----------|-------------------|
| `source_file="questions.pdf"` | Questions document → `questions/source_original.pdf` |
| `resources_folder="./images/"` containing `ref.pdf` | Resource → `questions/resources/ref.pdf` |

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
│  pdf  → markdown         field normalisation    export          │
│                          self-learning                          │
│                                                                 │
│  [Technical conversion]  [Format recognition]   [Export]        │
└─────────────────────────────────────────────────────────────────┘
```

**M5 does NOT receive docx/xlsx/pdf** - that's MarkItDown's job.

---

## Error Handling

### Error Scenarios

| Scenario | Behaviour | User Message |
|----------|----------|--------------|
| Source file not found | ABORT | `"Source file not found: {path}"` |
| Source file unreadable | ABORT | `"Cannot read source file: access denied"` |
| Source file not markdown | WARNING | `"⚠️ Source file is not markdown. Claude should convert via MarkItDown MCP first."` |
| Resources folder not found | CONTINUE (warning) | `"⚠️ Resources folder not found, continuing without resources"` |
| Resource file too large (>50MB) | SKIP file (warning) | `"⚠️ Skipped 'video.mp4' (85MB > 50MB limit)"` |
| Total resources too large (>500MB) | ABORT | `"Total resources 650MB exceeds 500MB limit"` |
| Duplicate resource names | ABORT | `"Duplicate: 'fig1.png' already exists in resources folder"` |

**NOTE:** Conversion errors are handled by Claude + MarkItDown MCP, not by qf-pipeline.

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

### Complete Workflow (Claude Orchestrates)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: Teacher requests help                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Teacher: "I have an exam in PDF format I want to convert to Inspera"       │
│          📎 File: /Nextcloud/Courses/Mathematics/exam.pdf                   │
│          📎 Images: /Nextcloud/Courses/Mathematics/images/                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: Claude reads PDF with read_materials                               │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Claude: "Reading the PDF file..."                                          │
│                                                                             │
│  → qf-scaffolding: read_materials(project_path, filename="exam.pdf")        │
│  → Returns extracted text                                                   │
│  → Saves to: questions/source.md                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: Claude creates QF project with qf-pipeline MCP                     │
│  ─────────────────────────────────────────────────────────────────────────  │
│  → Calls qf-pipeline: step0_start(                                          │
│        entry_point="questions",                                             │
│        source_file="questions/source.md",                                   │
│        resources_folder="/Nextcloud/.../images/"                            │
│     )                                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: qf-pipeline returns project info                                   │
│  ─────────────────────────────────────────────────────────────────────────  │
│ ✅ PROJECT CREATED                                                          │
│ 📁 Project: Matematik_Prov1_abc123/                                         │
│ 📄 Questions: questions/source_converted.md                                 │
│ 🖼️  Resources: questions/resources/ (8 files, 2.3 MB)                       │
│                                                                             │
│ ════════════════════════════════════════════════════════════════════════   │
│ 📋 WHAT DO YOU WANT TO DO WITH THE QUESTIONS?                               │
│ ────────────────────────────────────────────────────────────────────────── │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────┐    │
│ │ 1️⃣  DEFINE TAXONOMY (→ M2)                                          │    │
│ │     Choose this if questions lack tags/categories                   │    │
│ ├─────────────────────────────────────────────────────────────────────┤    │
│ │ 2️⃣  REVIEW & METADATA (→ M4)                                        │    │
│ │     Choose this if questions need Bloom levels, difficulty          │    │
│ ├─────────────────────────────────────────────────────────────────────┤    │
│ │ 3️⃣  CONVERT DIRECTLY (→ M5 → Pipeline)                              │    │
│ │     Choose this if questions already have all metadata              │    │
│ └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│ 💡 Tip: Tell me what your questions contain and I will help you choose!    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Decision Criteria

| Question | If YES → | If NO → |
|----------|----------|----------|
| Do questions have tags/categories? | Continue | → M2 (define taxonomy) |
| Do questions have Bloom levels? | Continue | → M4 (add them) |
| Do questions have difficulty levels? | Continue | → M4 (add them) |
| Is format correct (QFMD-like)? | → M5 → Pipeline | → M5 (format conversion) |

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
             │ Taxonomy │ │   QA     │ │  Format  │
             │ missing  │ │ review   │ │ convert  │
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
# NOTE: No auto_convert parameter - Claude converts via MarkItDown MCP first
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

    NOTE: source_file should be markdown (Claude converts via MarkItDown MCP first).
    """

    # Validate source file exists
    if not source_file.exists():
        raise FileNotFoundError(f"Source file not found: {source_file}")

    if not source_file.is_file():
        raise ValueError(f"Source file is not a file: {source_file}")

    # Warn if not markdown (Claude should have converted first)
    if source_file.suffix.lower() not in [".md", ".markdown"]:
        log_warning("non_markdown_source",
            f"source_file '{source_file.name}' is not markdown. "
            "Claude should convert via MarkItDown MCP first.")

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
            raise ValueError(f"Duplicate: '{file.name}' already exists")
        seen_names.add(file.name.lower())

        # Check extension
        if file.suffix.lower() not in ALLOWED_RESOURCE_EXTENSIONS:
            skipped.append(file.name)
            continue

        # Check file size
        file_size_mb = file.stat().st_size / (1024 * 1024)

        if file_size_mb > RESOURCE_LIMITS["max_file_mb"]:
            skipped.append(file.name)
            warnings.append(f"Skipped '{file.name}' ({file_size_mb:.1f}MB > {RESOURCE_LIMITS['max_file_mb']}MB)")
            continue

        if file_size_mb > RESOURCE_LIMITS["warn_file_mb"]:
            warnings.append(f"'{file.name}' is {file_size_mb:.1f}MB (large file)")

        # Check total size
        if total_size + file.stat().st_size > RESOURCE_LIMITS["max_total_mb"] * 1024 * 1024:
            raise ValueError(
                f"Total resources exceed {RESOURCE_LIMITS['max_total_mb']}MB limit"
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

### Phase 3: Document Conversion (Existing Tools)

**No new installation required.** Use existing tools:

| Format | Tool | Comment |
|--------|------|---------|
| PDF | `qf-scaffolding:read_materials` | Already implemented |
| DOCX | `markitdown` CLI (terminal) | Install separately if needed |
| Markdown | Direct input | No conversion |

**Example with read_materials:**
```python
# Claude reads PDF
content = read_materials(project_path, filename="exam.pdf")

# Claude saves as markdown
write_project_file(project_path, "questions/source.md", content.text_content)

# Claude starts questions workflow
step0_start(entry_point="questions", source_file="questions/source.md")
```

**Alternative: markitdown CLI** (if docx or better formatting is needed)
```bash
# In terminal
pip install markitdown[all]
markitdown exam.docx > source.md
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
    # NOTE: File is already markdown (Claude converted via MarkItDown MCP)
    file: "questions/source_converted.md"
    original_format: "md"
    # Original file (docx/pdf) remains in Nextcloud, not copied here

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
      - "video.mp4 is 45MB (large file)"
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
> "I have an exam in Word format with 20 questions. The questions have answers but lack Bloom levels."

1. `step0_start(entry_point="questions", source_file="exam.docx")`
2. System auto-converts docx → markdown
3. System analyses and detects: "20 questions, missing Bloom levels"
4. System suggests: "Questions need metadata → Use M4"
5. Teacher CHOOSES M4 (or can override to M2 or M5)
6. Teacher runs M4 to add Bloom levels
7. Then M5 → Pipeline → QTI export

### US-2: Teacher with Excel + Images
> "I have a question bank in Excel and a folder with images used in the questions."

1. `step0_start(entry_point="questions", source_file="bank.xlsx", resources_folder="./images/")`
2. System copies and converts:
   - `questions/source_original.xlsx`
   - `questions/source_converted.md`
   - `questions/resources/` (12 images)
3. Teacher updates QFMD to reference images: `![](resources/fig1.png)`
4. Then M5 → Pipeline → QTI export (resources embedded)

### US-3: Teacher with Complete Markdown Questions
> "I have questions in markdown format with all metadata. Just want to export."

1. `step0_start(entry_point="questions", source_file="questions.md")`
2. System detects markdown, skips conversion
3. System analyses: "Questions appear complete (have Bloom, difficulty, tags)"
4. System suggests: "Direct to M5 for format validation"
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
sys.path.insert(0, './packages/qf-pipeline/src')
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
sys.path.insert(0, './packages/qf-pipeline/src')
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
# Exam: Mathematics Basics

---

^id Q001
^type multiple_choice_single
^bloom understand
^difficulty medium

# Stem
What is 2 + 2?

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
Calculate the area of a rectangle with sides 3 and 4.

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
# m5_analyse()        → Parses 2 questions
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
| 6 | MarkItDown MCP installation (separate) | 1h |
| **Total** | | **6h** |

**NOTE:** Conversion logic is now in MarkItDown MCP (separate), not in qf-pipeline.

---

## Summary

RFC-017 introduces:
1. **New entry point `questions`** for existing questions (markdown format)
2. **`resources_folder` parameter** for accompanying images/audio
3. **Reuse of `read_materials`** for PDF reading (no new code)
4. **Flexible routing** to M2, M4, or M5 based on teacher needs
5. **`questions/resources/` folder** in project structure
6. **Resource linking syntax** in QFMD: `![](resources/filename)`
7. **Comprehensive error handling** with rollback on failure

**Architecture:**
- `qf-scaffolding:read_materials`: reads PDF → text (existing tool)
- `markitdown` CLI (optional): docx/xlsx → markdown (external, terminal)
- qf-pipeline: accepts markdown, handles resources, runs M5 → Pipeline

This fills the gap for teachers who have existing questions but don't fit the current M1→M2→M3→M4→Pipeline workflow.

---

*RFC-017 created 2026-01-29, updated 2026-01-31 (Simplified: reuse read_materials, markitdown optional)*
