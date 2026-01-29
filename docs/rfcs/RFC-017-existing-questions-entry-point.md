# RFC-017: Entry Point for Existing Questions

**Status:** Draft
**Created:** 2026-01-29
**Author:** Niklas Karlsson + Claude
**Related:** RFC-014 (Resource Handling), RFC-016 (M5 Self-Learning Format Recognition)

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
    source_file="prov.docx",              # Questions in any format
    resources_folder="/path/to/images/",  # Optional: accompanying resources
    output_folder="/path/to/projects",
    project_name="Matematik_Prov1"        # Optional
)
```

### Supported Formats

| Type | Formats | Notes |
|------|---------|-------|
| Questions | `.docx`, `.xlsx`, `.txt`, `.pdf`, `.md`, `.csv`, `.rtf` | Converted via MarkItDown if needed |
| Resources | `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.pdf`, `.mp3`, `.wav`, `.mp4`, `.webm` | Copied to resources folder |

### Project Structure

```
Matematik_Prov1_abc123/
├── session.yaml
├── sources.yaml
├── logs/
│   └── session.jsonl
├── questions/
│   ├── source_original.docx      ← Original file (preserved)
│   ├── source_converted.md       ← After format conversion
│   ├── m5_output.md              ← After M5 processing
│   └── resources/                ← NEW: Question resources
│       ├── figur1.png
│       ├── diagram.pdf
│       └── audio_q5.mp3
├── pipeline/
│   └── working.md
└── output/
    └── qti_package.zip
```

---

## Workflow

### Step 0: Project Setup

```
step0_start(entry_point="questions", source_file="prov.docx", resources_folder="./bilder/")
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ ✅ Project created: Matematik_Prov1_abc123/                                 │
│ ✅ Questions copied: questions/source_original.docx                         │
│ ✅ Resources copied: questions/resources/ (12 files)                        │
│                                                                             │
│ ⚠️  FORMAT: .docx detected - conversion needed before M5                    │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ NÄSTA STEG - Välj baserat på dina behov:                                │ │
│ │                                                                         │ │
│ │  A) Definiera taxonomi/taggar först?          → Använd M2               │ │
│ │  B) Granska & lägg till Bloom/difficulty?     → Använd M4               │ │
│ │  C) Frågorna har all metadata?                → Använd M5 → Pipeline    │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Decision Flow

```
                         ┌──────────────┐
                         │  questions   │
                         │ entry point  │
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

### When to Use Each Path

| Path | Scenario | Example |
|------|----------|---------|
| → M2 | Questions lack taxonomi/labels | "Frågorna har inga taggar, behöver definiera kategorier" |
| → M4 | Questions need QA review | "Frågorna behöver Bloom-nivåer och svårighetsgrad" |
| → M5 | Questions are complete | "Frågorna har allt, behöver bara konvertera format" |

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
}

# Add resources_folder parameter
"resources_folder": {
    "type": "string",
    "description": "Path to folder with resources (images, audio) for questions",
}
```

**File:** `packages/qf-pipeline/src/qf_pipeline/utils/session_manager.py`

```python
def create_session_for_questions(
    output_folder: Path,
    source_file: Path,
    resources_folder: Optional[Path] = None,
    project_name: Optional[str] = None,
) -> Session:
    """Create session for 'questions' entry point."""

    # 1. Create project structure
    project_path = create_project_folder(output_folder, project_name)

    # 2. Copy source file
    dest_source = project_path / "questions" / f"source_original{source_file.suffix}"
    shutil.copy2(source_file, dest_source)

    # 3. Copy resources if provided
    if resources_folder and resources_folder.exists():
        dest_resources = project_path / "questions" / "resources"
        copy_resources(resources_folder, dest_resources)

    # 4. Create session.yaml
    session = Session(
        project_path=project_path,
        entry_point="questions",
        source_file=dest_source,
        # ...
    )

    return session
```

### Phase 2: Resource Handling

**File:** `packages/qf-pipeline/src/qf_pipeline/utils/resources.py` (NEW)

```python
ALLOWED_RESOURCE_EXTENSIONS = {
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
    # Documents (for reference)
    ".pdf",
    # Audio
    ".mp3", ".wav", ".ogg", ".m4a",
    # Video
    ".mp4", ".webm",
}

def copy_resources(src_folder: Path, dest_folder: Path) -> dict:
    """
    Copy resources from source to destination.

    Returns:
        {
            "copied": ["figur1.png", "audio.mp3"],
            "skipped": ["notes.txt"],
            "total_size_mb": 12.5
        }
    """
    dest_folder.mkdir(parents=True, exist_ok=True)

    copied = []
    skipped = []
    total_size = 0

    for file in src_folder.iterdir():
        if file.is_file() and file.suffix.lower() in ALLOWED_RESOURCE_EXTENSIONS:
            shutil.copy2(file, dest_folder / file.name)
            copied.append(file.name)
            total_size += file.stat().st_size
        else:
            skipped.append(file.name)

    return {
        "copied": copied,
        "skipped": skipped,
        "total_size_mb": round(total_size / (1024 * 1024), 2)
    }
```

### Phase 3: Format Detection & Conversion

Leverage existing infrastructure:
- **MarkItDown MCP** for docx/xlsx/pdf → markdown conversion
- **M5 format_learner** for markdown → QFMD conversion

```
source_original.docx
        ↓ (MarkItDown)
source_converted.md
        ↓ (M5)
m5_output.md (QFMD)
        ↓ (Pipeline)
output/qti_package.zip
```

---

## Session.yaml Updates

```yaml
session:
  session_id: "abc123"
  entry_point: "questions"          # NEW value
  status: "active"
  created_at: "2026-01-29T15:30:00Z"

  source:
    original_file: "questions/source_original.docx"
    original_format: "docx"
    converted_file: "questions/source_converted.md"  # After MarkItDown

  resources:                        # NEW section
    folder: "questions/resources/"
    count: 12
    total_size_mb: 8.5
    files:
      - "figur1.png"
      - "diagram.pdf"
      - "audio_q5.mp3"
```

---

## Integration with Existing RFCs

| RFC | Integration |
|-----|-------------|
| RFC-014 (Resource Handling) | `questions/resources/` folder, resource copying |
| RFC-016 (M5 Format Recognition) | M5 processes converted markdown |
| RFC-001 (Unified Logging) | Log resource copying, format conversion |

---

## User Stories

### US-1: Teacher with Word Document
> "Jag har ett prov i Word-format med 20 frågor. Frågorna har svar men saknar Bloom-nivåer."

1. `step0_start(entry_point="questions", source_file="prov.docx")`
2. System suggests: "Frågorna behöver metadata → Använd M4"
3. Teacher runs M4 to add Bloom levels
4. Then M5 → Pipeline → QTI export

### US-2: Teacher with Excel + Images
> "Jag har en frågebank i Excel och en mapp med bilder som används i frågorna."

1. `step0_start(entry_point="questions", source_file="bank.xlsx", resources_folder="./bilder/")`
2. System copies both questions and resources
3. Teacher chooses path based on completeness
4. Resources automatically linked in QTI export

### US-3: Teacher with Complete Questions
> "Jag har frågor i markdown-format med all metadata. Vill bara exportera."

1. `step0_start(entry_point="questions", source_file="fragor.md")`
2. System detects markdown, suggests: "Ser komplett ut → Direkt till M5"
3. M5 validates and converts to QFMD
4. Pipeline → QTI export

---

## Verification

### Test 1: Basic Entry Point
```bash
# Create project with Word file
step0_start(entry_point="questions", source_file="test.docx", output_folder="/tmp/test")

# Verify structure
ls /tmp/test/*/questions/
# Expected: source_original.docx
```

### Test 2: With Resources
```bash
# Create project with resources
step0_start(
    entry_point="questions",
    source_file="test.docx",
    resources_folder="./images/",
    output_folder="/tmp/test"
)

# Verify resources copied
ls /tmp/test/*/questions/resources/
# Expected: figur1.png, diagram.pdf, etc.
```

### Test 3: Full Workflow
```bash
# 1. Setup
step0_start(entry_point="questions", source_file="prov.docx")

# 2. Convert format (MarkItDown)
# ... manual or via MCP ...

# 3. M5 processing
m5_start(project_path="...")
m5_detect_format()
m5_analyze()
m5_finish()

# 4. Pipeline
step2_validate()
step3_autofix()
step4_export()
```

---

## Open Questions

1. **Automatic format conversion?**
   - Should step0_start automatically call MarkItDown for non-markdown files?
   - Or leave it manual/explicit?

2. **Resource linking in QFMD?**
   - How to reference resources in questions?
   - Relative paths: `![](resources/figur1.png)`?

3. **Large resource handling?**
   - Max file size? (Suggest: 50MB per file, 500MB total)
   - Compression for export?

---

## Timeline

| Phase | Description | Estimate |
|-------|-------------|----------|
| 1 | Core entry point + resources_folder param | 2h |
| 2 | Resource copying utility | 1h |
| 3 | Session.yaml updates | 1h |
| 4 | Integration testing | 2h |
| **Total** | | **6h** |

---

## Summary

RFC-017 introduces:
1. **New entry point `questions`** for existing questions in any format
2. **`resources_folder` parameter** for accompanying images/audio
3. **Flexible routing** to M2, M4, or M5 based on teacher needs
4. **`questions/resources/` folder** in project structure

This fills the gap for teachers who have existing questions but don't fit the current M1→M2→M3→M4→Pipeline workflow.

---

*RFC-017 created 2026-01-29*
