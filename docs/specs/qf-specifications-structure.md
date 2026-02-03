# QF-SPECIFICATIONS Structure

**Version:** 1.0  
**Status:** Draft  
**Purpose:** Shared specifications used by both qf-scaffolding and qf-pipeline  
**Related ADRs:** ADR-001

---

## Overview

qf-specifications is a shared folder containing question type definitions, format specifications, metadata schemas, and label taxonomies. Both MCPs reference this single source of truth.

**Location:** `/QuestionForge/qf-specifications/`

---

## Directory Structure

```
qf-specifications/
│
├── question-format-v7.md          # Overall format specification
│
├── question-types/                # Per-type specifications (15 types)
│   ├── multiple_choice_single.md
│   ├── multiple_choice_multiple.md
│   ├── true_false.md
│   ├── text_entry.md
│   ├── text_entry_math.md
│   ├── text_entry_numeric.md
│   ├── inline_choice.md
│   ├── match.md
│   ├── text_area.md
│   ├── essay.md
│   ├── audio_record.md
│   ├── hotspot.md
│   ├── graphicgapmatch_v2.md
│   ├── text_entry_graphic.md
│   ├── composite_editor.md
│   └── nativehtml.md
│
├── metadata-schema.json           # JSON Schema for question metadata
│
├── label-taxonomy.yaml            # Valid labels and hierarchy
│
├── platforms/                     # Platform-specific requirements
│   └── inspera/
│       ├── field_mapping.md       # Our fields → Inspera fields
│       ├── limitations.md         # What Inspera can't do
│       └── best_practices.md      # Inspera tips
│
└── modules/                       # Module methodology docs (from BB1-BB5)
    ├── m1-content-analysis/
    │   ├── overview.md
    │   ├── stage-0-material-analysis.md
    │   ├── stage-1-validation.md
    │   ├── stage-2-emphasis.md
    │   ├── stage-3-examples.md
    │   ├── stage-4-misconceptions.md
    │   └── stage-5-objectives.md
    │
    ├── m2-assessment-planning/
    │   ├── overview.md
    │   ├── stage-1-metadata-schema.md
    │   ├── stage-2-label-taxonomy.md
    │   ├── stage-3-question-types.md
    │   ├── stage-4-distribution.md
    │   └── stage-5-platform-requirements.md
    │
    ├── m3-question-generation/
    │   ├── overview.md
    │   ├── stage-1-templates.md
    │   ├── stage-2-drafts.md
    │   ├── stage-3-review.md
    │   └── stage-4-iteration.md
    │
    └── m4-quality-assurance/
        ├── overview.md
        ├── stage-1-distractor-analysis.md
        ├── stage-2-cognitive-verification.md
        ├── stage-3-language-review.md
        └── stage-4-alignment-check.md
```

---

## File Specifications

### question-format-v7.md

Evolution from Field Requirements v6.3. Defines:

- File structure (header, separator, questions)
- @ prefix metadata format
- @field: section identifiers
- Tags format (#hashtags)
- Question header format

**Key format elements:**

```markdown
# Q001 Question Title
@question: Q001
@type: multiple_choice_single
@identifier: COURSE_TOPIC_Q001
@title: Question Title
@points: 1
@tags: #Course #Topic #Bloom #Difficulty

---

## Question Text
@field: question_text
Content...

## Options
@field: options
A. Choice 1
B. Choice 2
...
```

### question-types/*.md

One file per question type. Each contains:

1. **Type Overview** - What this type is for
2. **Required Fields** - Fields that MUST be present
3. **Optional Fields** - Fields that CAN be present
4. **Feedback Structure** - Auto-graded (5 subsections) or Manual (3 subsections)
5. **Inspera Requirements** - Platform-specific needs
6. **Complete Template** - Copy-paste example
7. **Common Errors** - What to avoid

### metadata-schema.json

JSON Schema defining valid metadata:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["question", "type", "identifier", "points", "tags"],
  "properties": {
    "question": {
      "type": "string",
      "pattern": "^Q[0-9]{3}$"
    },
    "type": {
      "type": "string",
      "enum": [
        "multiple_choice_single",
        "multiple_response",
        "true_false",
        "text_entry",
        "text_entry_math",
        "text_entry_numeric",
        "inline_choice",
        "match",
        "text_area",
        "essay",
        "audio_record",
        "hotspot",
        "graphicgapmatch_v2",
        "text_entry_graphic",
        "composite_editor",
        "nativehtml"
      ]
    },
    "identifier": {
      "type": "string",
      "pattern": "^[A-Z0-9_]+$"
    },
    "points": {
      "type": "integer",
      "minimum": 0
    },
    "tags": {
      "type": "string",
      "pattern": "^#[\\w-]+(\\s+#[\\w-]+)*$"
    }
  }
}
```

### label-taxonomy.yaml

Hierarchical label definitions:

```yaml
# Label Taxonomy for QuestionForge

courses:
  - code: EXAMPLE_COURSE
    name: Grundläggande biologi
    topics:
      - Celler
      - Genetik
      - Evolution
      - Ekologi

bloom_levels:
  - Remember
  - Understand
  - Apply
  - Analyze
  - Evaluate
  - Create

difficulty:
  - Easy
  - Medium
  - Hard

# Format: @tags: #CourseCode #Topic #BloomLevel #Difficulty
# Example: @tags: #EXAMPLE_COURSE #Celler #Apply #Medium
```

---

## Valid Question Types (15)

| Type | Category | Grading |
|------|----------|---------|
| `multiple_choice_single` | Selection | Auto |
| `multiple_response` | Selection | Auto |
| `true_false` | Selection | Auto |
| `text_entry` | Fill-in | Auto |
| `text_entry_math` | Fill-in | Auto |
| `text_entry_numeric` | Fill-in | Auto |
| `inline_choice` | Dropdown | Auto |
| `match` | Matching | Auto |
| `text_area` | Open text | Manual |
| `essay` | Open text | Manual |
| `audio_record` | Media | Manual |
| `hotspot` | Image | Auto |
| `graphicgapmatch_v2` | Image | Auto |
| `text_entry_graphic` | Image | Auto |
| `composite_editor` | Complex | Mixed |
| `nativehtml` | Custom | Varies |

---

## Feedback Structures

### Auto-Graded (5 subsections)

For: MC, MR, TF, text_entry, inline_choice, match, hotspot, etc.

```markdown
## Feedback
@field: feedback

### General Feedback
@field: general_feedback
[Explanation]

### Correct Response Feedback
@field: correct_feedback
[Explanation]

### Incorrect Response Feedback
@field: incorrect_feedback
[Explanation]

### Partially Correct Response Feedback
@field: partial_feedback
[Explanation]

### Unanswered Feedback
@field: unanswered_feedback
[Explanation]
```

### Manual-Graded (3 subsections)

For: text_area, essay, audio_record

```markdown
## Feedback
@field: feedback

### General Feedback
@field: general_feedback
[Explanation]

### Answered Feedback
@field: answered_feedback
[Explanation]

### Unanswered Feedback
@field: unanswered_feedback
[Explanation]
```

---

## Migration from v6.3

Current Field Requirements v6.3 location:
`/Modular QGen Framework/docs/MQG_0.2/MQG_bb6_Field_Requirements_v06.md`

Migration tasks:
1. Split into question-format-v7.md (structure) and question-types/*.md (per-type)
2. Extract metadata schema to JSON
3. Extract label taxonomy to YAML
4. Add platform-specific content to platforms/inspera/
5. Migrate BB1-BB5 documentation to modules/

---

## Usage by MCPs

### qf-scaffolding (MCP 1)

Uses:
- `modules/m1-*/` through `modules/m4-*/` for methodology guidance
- `question-types/*.md` in M2 Stage 3 (show technical requirements)
- `question-format-v7.md` in M3 (question generation)

### qf-pipeline (MCP 2)

Uses:
- `question-types/*.md` in Step 1 (Guided Build comparison)
- `metadata-schema.json` in Step 2 (Validation)
- `platforms/inspera/` in Step 4 (Export)

---

## Versioning

Specifications are versioned in the filename or header:
- `question-format-v7.md` (major version in filename)
- Individual type specs have version in header

Changes require:
1. Update specification file
2. Update both MCPs if interface changes
3. Document in CHANGELOG

---

*Specification v1.0 | QuestionForge | 2026-01-02*
