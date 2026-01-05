# QF-PIPELINE-MCP Specification

**Version:** 1.0  
**Status:** Draft  
**MCP Name:** qf-pipeline  
**Language:** Python  
**Related ADRs:** ADR-001, ADR-003, ADR-005

---

## Overview

qf-pipeline is a technical pipeline MCP that builds, validates, and exports questions to QTI format for Inspera. It wraps existing QTI-Generator-for-Inspera Python code and provides a structured workflow.

**Pattern:** LINEAR pipeline with validation loops  
**Input:** Markdown questions (from qf-scaffolding or direct)  
**Output:** QTI package for Inspera import

---

## Pipeline Steps

```
┌─────────────────────────────────────────────────────────────────┐
│  qf-pipeline WORKFLOW                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INPUT: Markdown questions file                                 │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  STEP 1: GUIDED BUILD                                       ││
│  │  Question-by-question format validation                     ││
│  │  Fix once → Apply to all similar types                      ││
│  └──────────────────────────┬──────────────────────────────────┘│
│                             │                                    │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  STEP 1.5: SUMMARY ANALYSIS (FUTURE)                        ││
│  │  Calls qf-scaffolding M4 for pedagogical analysis           ││
│  └──────────────────────────┬──────────────────────────────────┘│
│                             │                                    │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  STEP 2: VALIDATOR                                          ││
│  │  Batch validation of all questions                          ││
│  │  If errors → Loop back to Step 1                            ││
│  └──────────────────────────┬──────────────────────────────────┘│
│                             │                                    │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  STEP 3: DECISION                                           ││
│  │  Teacher chooses: QTI Questions OR Question Set             ││
│  └──────────────────────────┬──────────────────────────────────┘│
│                             │                                    │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  STEP 4: EXPORT                                             ││
│  │  Generate QTI package for Inspera                           ││
│  └──────────────────────────┬──────────────────────────────────┘│
│                             │                                    │
│                             ▼                                    │
│  OUTPUT: QTI package (XML + manifest + ZIP)                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step Details

### Step 1: Guided Build

Interactive, question-by-question format checking:

```
For each question in file:
  1. READ question (Q001)
  2. IDENTIFY question type (from @type field)
  3. LOAD specification for that type
  4. COMPARE question to specification
  5. SUGGEST corrections to teacher
  6. TEACHER decides: accept / modify / skip
  7. APPLY fix to current question
  8. APPLY same fix to ALL similar question types  ← KEY FEATURE
  9. MOVE to next question (Q002...)
```

**Key innovation:** Fix once, apply to all. If Q001 (MC single) has wrong feedback structure, fixing it fixes ALL MC single questions in the file.

### Step 1.5: Summary Analysis (FUTURE)

Comprehensive analysis after all questions built:

- Variation analysis across question bank
- Final distractor quality check (calls qf-scaffolding)
- Language/terminology consistency (calls qf-scaffolding)
- Pedagogical quality review (calls qf-scaffolding)

**Note:** This step is planned for future development. Steps 1-4 work without it.

### Step 2: Validator

Batch validation of entire file:

- Validates all questions against specifications
- Reports errors and warnings
- If errors found → Teacher decides to loop back to Step 1 or fix manually

### Step 3: Decision

Teacher chooses export format:

- **Option A:** QTI Questions (individual items)
- **Option B:** Question Set (grouped collection)
  - With labels
  - Without labels

### Step 4: Export

Generate final QTI package:

- QTI XML files (one per question or grouped)
- Manifest file
- ZIP package for Inspera import

---

## Tools

### Step 1: Guided Build Tools

```python
def start_build_session(file_path: str) -> BuildSession:
    """Start a new guided build session."""
    return {
        "session_id": str,
        "file_path": str,
        "total_questions": int,
        "first_question": QuestionInfo,
        "question_types_found": list[str]
    }

def get_question(session_id: str, question_id: str) -> Question:
    """Get a specific question's content."""
    return {
        "question_id": str,
        "question_type": str,
        "content": str,
        "parsed_fields": dict
    }

def get_question_spec(question_type: str) -> Specification:
    """Load specification for a question type."""
    return {
        "type": str,
        "required_fields": list[str],
        "optional_fields": list[str],
        "feedback_structure": str,
        "examples": list[str]
    }

def compare_to_spec(question_id: str, session_id: str) -> Comparison:
    """Compare question to its type specification."""
    return {
        "matches": bool,
        "differences": list[Difference],
        "suggestions": list[Suggestion]
    }

def suggest_fixes(question_id: str, session_id: str) -> Fixes:
    """Get suggested fixes for a question."""
    return {
        "fixes": list[Fix],
        "similar_questions": list[str],  # Other Qs of same type
        "apply_to_similar_available": bool
    }

def apply_fix(
    session_id: str,
    question_id: str,
    fix: Fix,
    apply_to_similar: bool = False
) -> ApplyResult:
    """Apply a fix, optionally to all similar question types."""
    return {
        "updated_question": str,
        "similar_questions_updated": int,
        "updated_question_ids": list[str]
    }

def next_question(session_id: str) -> NextResult:
    """Move to next question or signal completion."""
    return {
        "status": "next" | "complete",
        "question": QuestionInfo | None,
        "progress": Progress
    }

def save_progress(session_id: str, output_path: str) -> SaveResult:
    """Save current state of file."""
    return {
        "saved_path": str,
        "questions_processed": int,
        "questions_remaining": int
    }
```

### Step 2: Validator Tools

```python
def validate_file(file_path: str) -> ValidationResult:
    """Validate entire file against specifications."""
    return {
        "valid": bool,
        "total_questions": int,
        "errors": list[ValidationError],
        "warnings": list[ValidationWarning],
        "questions_with_errors": list[str]
    }

def validate_question(question_content: str) -> QuestionValidation:
    """Validate a single question."""
    return {
        "valid": bool,
        "question_type": str,
        "field_errors": dict[str, str],
        "missing_fields": list[str],
        "warnings": list[str]
    }

def get_validation_report(
    file_path: str,
    format: str = "markdown"  # "json" | "markdown" | "html"
) -> Report:
    """Generate detailed validation report."""
    return {
        "format": str,
        "content": str,
        "summary": ValidationSummary
    }
```

### Step 3: Decision Tools

```python
def export_questions(
    file_path: str,
    output_path: str
) -> ExportResult:
    """Export as individual QTI questions."""
    return {
        "qti_files": list[str],
        "count": int,
        "output_directory": str
    }

def create_question_set(
    file_path: str,
    config: QuestionSetConfig
) -> QuestionSetResult:
    """Create grouped question set."""
    # config = {
    #     "set_name": str,
    #     "include_labels": bool,
    #     "metadata": dict
    # }
    return {
        "set_file": str,
        "manifest": str,
        "questions_included": int
    }
```

### Step 4: Export Tool

```python
def generate_qti_package(
    input_path: str,
    output_path: str,
    options: ExportOptions
) -> PackageResult:
    """Generate final QTI package for Inspera."""
    # options = {
    #     "format": "qti2.1" | "qti3.0",
    #     "compress": bool,
    #     "include_manifest": bool
    # }
    return {
        "package_path": str,
        "manifest_path": str,
        "files_included": int,
        "package_size": int
    }
```

---

## File Structure

```
packages/qf-pipeline/
├── src/
│   └── qf_pipeline/
│       ├── __init__.py
│       ├── server.py              # MCP server entry
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── build_session.py   # Step 1 tools
│       │   ├── validator.py       # Step 2 tools
│       │   ├── decision.py        # Step 3 tools
│       │   └── exporter.py        # Step 4 tools
│       ├── wrappers/
│       │   └── qti_generator/     # Wrapped existing code
│       │       ├── __init__.py
│       │       ├── validator.py
│       │       └── exporter.py
│       └── utils/
│           ├── parser.py          # Question file parsing
│           └── spec_loader.py     # Load specifications
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Tool Summary

| Tool | Step | Purpose |
|------|------|---------|
| `start_build_session` | 1 | Initialize guided build |
| `get_question` | 1 | Read specific question |
| `get_question_spec` | 1 | Load type specification |
| `compare_to_spec` | 1 | Compare question to spec |
| `suggest_fixes` | 1 | Get fix suggestions |
| `apply_fix` | 1 | Apply fix (optionally to similar) |
| `next_question` | 1 | Move to next question |
| `save_progress` | 1 | Save current state |
| `validate_file` | 2 | Batch validate file |
| `validate_question` | 2 | Validate single question |
| `get_validation_report` | 2 | Generate report |
| `export_questions` | 3 | Export individual items |
| `create_question_set` | 3 | Create grouped set |
| `generate_qti_package` | 4 | Final QTI export |

---

## Integration with qf-scaffolding (MCP 1)

In **Step 1.5 (FUTURE)**, qf-pipeline calls qf-scaffolding tools:

```python
# Step 1.5 implementation (future)
def run_summary_analysis(session_id: str) -> AnalysisResult:
    """Call qf-scaffolding for pedagogical analysis."""
    
    # Call MCP 1 tools
    distractor_result = call_mcp1("analyze_distractors", {...})
    language_result = call_mcp1("check_language_consistency", {...})
    
    return {
        "distractor_analysis": distractor_result,
        "language_analysis": language_result,
        "recommendations": list[str]
    }
```

---

## Wrapped Code

qf-pipeline wraps existing code from QTI-Generator-for-Inspera:

| Original | Wrapper Location | Purpose |
|----------|------------------|---------|
| Validation logic | `wrappers/qti_generator/validator.py` | Format validation |
| QTI export | `wrappers/qti_generator/exporter.py` | QTI XML generation |

---

## Dependencies

- `mcp` - MCP Python SDK
- `pyyaml` - YAML parsing
- `lxml` - XML generation (QTI)
- `qf-specifications/` - Shared question type specs

---

## Configuration

```toml
[project]
name = "qf-pipeline"
version = "1.0.0"
description = "QuestionForge validation and export pipeline MCP"

[project.scripts]
qf-pipeline = "qf_pipeline.server:main"
```

---

*Specification v1.0 | QuestionForge | 2026-01-02*
