# ADR-011: Question Set Builder

**Status:** Proposed  
**Date:** 2026-01-06  
**Deciders:** Niklas  
**Context:** qf-pipeline Step 3 Path B implementation  
**Related:** ADR-010 (Step 3 Decision Architecture)

---

## Context

When teachers choose "Path B: Question Set" in Step 3, they need a tool to filter, group, and configure questions before export. QTI-Generator already has an `AssessmentTestGenerator` that produces assessmentTest XML for Inspera.

**Key differences from direct export:**
- Questions are grouped into sections
- Each section can filter by tags
- Random selection (pull X from Y questions)
- Shuffle per section
- Output is assessmentTest XML (not just individual items)

**What QTI-Generator has:**
- `SectionConfig` dataclass with filtering
- `AssessmentTestGenerator` class
- YAML-based configuration in frontmatter

**What QTI-Generator lacks (new for qf-pipeline):**
- **Labels with/without choice** - Should exported questions keep ^labels?
- **Interactive builder** - YAML config is hard for teachers

---

## Decision

### Create `step3_question_set` tool with:

1. **Interactive section builder** (not YAML)
2. **Filter options** per section:
   - Bloom's Taxonomy (Remember, Understand, Apply, Analyze, Evaluate, Create)
   - Difficulty (Easy, Medium, Hard)
   - Custom tags (from ^labels)
   - Points
3. **Section configuration:**
   - Select count (pull X from Y)
   - Shuffle (yes/no)
4. **Labels choice** (NEW):
   - Export with labels (for question banks)
   - Export without labels (for final exams)
5. **Preview** before export

---

## Filter Logic

**From QTI-Generator (preserve this):**

```
Within a category: OR logic
Between categories: AND logic

Example: (Remember OR Understand) AND Easy AND Cellbiologi
```

```python
# If user selects:
bloom: ["Remember", "Understand"]
difficulty: ["Easy"]
custom: ["Cellbiologi"]

# Question matches if:
# (has Remember OR has Understand) 
# AND (has Easy)
# AND (has Cellbiologi)
```

---

## Tool Design

### Input Schema

```python
Tool(
    name="step3_question_set",
    description="Create Question Set with sections and filtering. Use after validation.",
    inputSchema={
        "type": "object",
        "properties": {
            "set_name": {
                "type": "string",
                "description": "Name for the Question Set"
            },
            "include_labels": {
                "type": "boolean",
                "description": "Include ^labels in export (false = strip labels)",
                "default": True
            },
            "sections": {
                "type": "array",
                "description": "Section configurations",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "filter_bloom": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Bloom levels (OR logic)"
                        },
                        "filter_difficulty": {
                            "type": "array", 
                            "items": {"type": "string"},
                            "description": "Difficulty levels (OR logic)"
                        },
                        "filter_custom": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Custom tags (OR logic)"
                        },
                        "filter_points": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Point values (OR logic)"
                        },
                        "select": {
                            "type": "integer",
                            "description": "Random select X questions (null = all)"
                        },
                        "shuffle": {
                            "type": "boolean",
                            "default": True
                        }
                    },
                    "required": ["name"]
                }
            }
        },
        "required": ["set_name", "sections"]
    }
)
```

### Output

```python
{
    "success": bool,
    "set_name": str,
    "include_labels": bool,
    "sections": [
        {
            "name": str,
            "matched_questions": int,
            "selected_questions": int,  # After random selection
            "shuffle": bool
        }
    ],
    "total_questions": int,
    "preview": str,  # Human-readable preview
    "ready_for_export": bool
}
```

---

## Implementation

### Wrapper: Reuse QTI-Generator's `AssessmentTestGenerator`

```python
# wrappers/question_set.py

from ..wrappers import QTI_GENERATOR_PATH
sys.path.insert(0, str(QTI_GENERATOR_PATH))

from src.generator.assessment_test_generator import (
    AssessmentTestGenerator,
    SectionConfig,
)

def build_question_set(
    questions: List[dict],
    set_name: str,
    sections: List[dict],
    include_labels: bool = True,
    language: str = "sv"
) -> dict:
    """Build Question Set configuration.
    
    Args:
        questions: Parsed questions from markdown
        set_name: Name for the Question Set
        sections: Section configurations
        include_labels: If False, strip ^labels before export
        language: Language code
    
    Returns:
        Configuration ready for export
    """
    generator = AssessmentTestGenerator()
    
    # Convert section dicts to SectionConfig
    section_configs = []
    section_results = []
    
    for s in sections:
        config = SectionConfig(
            name=s["name"],
            filter_bloom=s.get("filter_bloom"),
            filter_difficulty=s.get("filter_difficulty"),
            filter_custom=s.get("filter_custom"),
            filter_points=s.get("filter_points"),
            select=s.get("select"),
            shuffle=s.get("shuffle", True)
        )
        section_configs.append(config)
        
        # Filter questions to get count
        filtered = generator._filter_questions(questions, config)
        section_results.append({
            "name": config.name,
            "matched_questions": len(filtered),
            "selected_questions": min(config.select or len(filtered), len(filtered)),
            "shuffle": config.shuffle
        })
    
    # Strip labels if requested
    if not include_labels:
        questions = strip_labels(questions)
    
    return {
        "success": True,
        "set_name": set_name,
        "include_labels": include_labels,
        "sections": section_results,
        "section_configs": section_configs,  # For export step
        "questions": questions,
        "total_questions": sum(s["selected_questions"] for s in section_results),
        "language": language
    }


def strip_labels(questions: List[dict]) -> List[dict]:
    """Remove ^labels from questions."""
    stripped = []
    for q in questions:
        q_copy = q.copy()
        q_copy.pop("labels", None)
        q_copy.pop("tags", None)
        stripped.append(q_copy)
    return stripped
```

### Server Handler

```python
async def handle_step3_question_set(arguments: dict) -> List[TextContent]:
    """Handle step3_question_set - build Question Set."""
    session = get_current_session()
    
    if not session:
        return [TextContent(
            type="text",
            text="No active session. Run step0_start first."
        )]
    
    # Parse questions from working file
    data = parse_file(str(session.working_file))
    questions = data.get("questions", [])
    
    if not questions:
        return [TextContent(type="text", text="No questions found.")]
    
    # Build Question Set
    from .wrappers.question_set import build_question_set
    
    result = build_question_set(
        questions=questions,
        set_name=arguments["set_name"],
        sections=arguments["sections"],
        include_labels=arguments.get("include_labels", True),
        language=arguments.get("language", "sv")
    )
    
    # Store in session for step4_export
    session.question_set_config = result
    
    # Build preview
    preview_lines = [
        f"Question Set: {result['set_name']}",
        f"Labels: {'Included' if result['include_labels'] else 'Removed'}",
        "",
        "Sections:"
    ]
    
    for s in result["sections"]:
        preview_lines.append(
            f"  • {s['name']}: {s['selected_questions']} questions "
            f"(of {s['matched_questions']} matching)"
            f"{' [shuffle]' if s['shuffle'] else ''}"
        )
    
    preview_lines.extend([
        "",
        f"Total: {result['total_questions']} questions",
        "",
        "Next step: step4_export to create QTI package"
    ])
    
    return [TextContent(type="text", text="\n".join(preview_lines))]
```

---

## Dialogue Example

```
Teacher: "Create a Question Set for my biology exam"

Claude: "I'll help you create a Question Set. First I need to know:

1. What should the set be called?
2. Should labels (Bloom, difficulty) be included in the export?
   - Yes: Good for question banks, teachers can see categorisation
   - No: Cleaner for final exams, students don't see categories

3. How many sections do you want?"

Teacher: "Call it 'Cell Biology Exam Spring 26'. Remove labels.
          Two sections: one with easy questions, one with hard."

Claude: "Good! Let me configure:

Section 1: Easy questions
- Filtering on: Difficulty = Easy
- How many questions should be randomly selected? (of 12 easy questions available)"

Teacher: "8"

Claude: "Section 2: Hard questions
- Filtering on: Difficulty = Hard
- How many questions should be randomly selected? (of 7 hard questions available)"

Teacher: "5"

Claude: [Calls step3_question_set with config]

"Question Set configured!

Cell Biology Exam Spring 26
Labels: Removed

Sections:
  • Easy questions: 8 questions (of 12 matching) [shuffle]
  • Hard questions: 5 questions (of 7 matching) [shuffle]

Total: 13 questions

Would you like to export now? (step4_export)"
```

---

## Labels: With vs Without

### With Labels (include_labels: true)

Questions keep their `^labels` field:
```markdown
^labels #Easy #Remember #Cellbiologi #Biog001x
```

**Use case:** Question banks where teachers need to see categorization

### Without Labels (include_labels: false)  

Labels stripped before export:
```markdown
# No ^labels field in export
```

**Use case:** Final exams where students shouldn't see difficulty/Bloom categorization

**Implementation:** Strip labels AFTER filtering but BEFORE XML generation

---

## Modified Export Flow

```
step3_question_set
       │
       ├── Filter questions per section
       ├── Apply random selection
       ├── Strip labels (if include_labels=false)
       ├── Store config in session
       │
       ▼
step4_export
       │
       ├── Check: session.question_set_config exists?
       │   ├── YES: Generate assessmentTest XML
       │   └── NO: Generate individual QTI items (Path A)
       │
       ▼
QTI Package
```

---

## Consequences

### Positive
- Teachers can create dynamic tests without YAML
- Labels choice enables both question banks and clean exams
- Reuses proven QTI-Generator code
- Clear preview before export

### Negative
- More complex than direct export
- Session state needed between step3 and step4
- Multiple tool calls for full workflow

### Neutral
- Filtering logic matches QTI-Generator exactly
- Optional feature (Path A still works)

---

## Testing

```python
def test_filter_bloom_or_logic():
    """Bloom filters should use OR logic."""
    questions = [
        {"id": "Q1", "tags": ["Remember", "Easy"]},
        {"id": "Q2", "tags": ["Understand", "Easy"]},
        {"id": "Q3", "tags": ["Apply", "Easy"]},
    ]
    config = SectionConfig(
        name="Test",
        filter_bloom=["Remember", "Understand"]
    )
    # Should match Q1 and Q2, not Q3
    
def test_filter_between_categories_and_logic():
    """Different categories should use AND logic."""
    questions = [
        {"id": "Q1", "tags": ["Remember", "Easy"]},
        {"id": "Q2", "tags": ["Remember", "Hard"]},
    ]
    config = SectionConfig(
        name="Test",
        filter_bloom=["Remember"],
        filter_difficulty=["Easy"]
    )
    # Should match only Q1

def test_strip_labels():
    """Labels should be removed when include_labels=False."""
    questions = [{"id": "Q1", "labels": "#Easy #Remember", "tags": ["Easy"]}]
    stripped = strip_labels(questions)
    assert "labels" not in stripped[0]
    assert "tags" not in stripped[0]
```

---

## References

- QTI-Generator: `src/generator/assessment_test_generator.py`
- SectionConfig dataclass
- Filter logic documentation
- ADR-010: Step 3 Decision Architecture

---

*ADR-011 | QuestionForge | 2026-01-06*
