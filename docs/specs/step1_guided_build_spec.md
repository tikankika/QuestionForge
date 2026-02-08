# STEP 1: GUIDED BUILD - COMPLETE SPECIFICATION

**Version:** 0.1 DRAFT  
**Date:** 2026-01-07  
**Status:** For review before implementation

---

## OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STEP 1: GUIDED BUILD                             │
│                                                                          │
│  INPUT:  Markdown file with questions (various formats)                 │
│  OUTPUT: Markdown file in QFMD format (ready for Step 2)                │
│                                                                          │
│  PROCESS: Question-by-question walkthrough with teacher verification    │
│  KEY: Clear spec + Claude guides + Human verifies                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 0: INITIALIZATION (Before question loop)

### 0a. Session Management

```python
def step1_start(file_path: str, resume: bool = False) -> Session:
    """
    Start or resume Step 1 session.
    
    Args:
        file_path: Path to markdown file
        resume: True = continue previous session
    
    Returns:
        Session with state
    """
```

**State that is saved:**
```yaml
session:
  id: "uuid"
  file_path: "/path/to/questions.md"
  started: "2026-01-07T10:00:00Z"
  last_updated: "2026-01-07T10:30:00Z"
  
progress:
  total_questions: 40
  current_question: 12
  completed: [Q001, Q002, ..., Q011]
  skipped: [Q005]
  has_warnings: [Q003, Q007]
  
changes:
  - question: Q001
    field: "labels"
    old: null
    new: "^labels #EXAMPLE_COURSE #Remember #Easy"
    timestamp: "2026-01-07T10:05:00Z"
```

### 0b. File Validation

```python
def validate_input_file(file_path: str) -> FileValidation:
    """
    Check that the file is a valid question file.
    
    Checks:
    - File exists
    - Is markdown (.md)
    - Contains at least one question
    - Not empty
    - Encoding OK (UTF-8)
    """
```

**Result:**
```yaml
file_validation:
  exists: true
  is_markdown: true
  encoding: "utf-8"
  has_questions: true
  question_count: 40
  has_header: true  # Content before ===QUESTIONS===
  errors: []
```

### 0c. Format Detection

```python
def detect_format(content: str) -> FormatLevel:
    """
    Identify which input level the file has.
    
    Returns:
        FormatLevel.UNSTRUCTURED - needs qf-scaffolding
        FormatLevel.SEMI_STRUCTURED - **Type**: format
        FormatLevel.LEGACY_SYNTAX - @question: format
        FormatLevel.QFMD - already correct
    """
```

**Detection logic:**
```python
if "^question" in content and "@field:" in content and "@end_field" in content:
    return FormatLevel.QFMD
elif "@question:" in content or "@type:" in content:
    return FormatLevel.LEGACY_SYNTAX
elif "**Type**:" in content or "## Question Text" in content:
    return FormatLevel.SEMI_STRUCTURED
elif "**QUESTION:**" in content or "**CORRECT ANSWER:**" in content:
    return FormatLevel.UNSTRUCTURED
else:
    return FormatLevel.UNKNOWN
```

**Action per level:**
```
UNSTRUCTURED:       → Reject, recommend M3 or qf-scaffolding
SEMI_STRUCTURED:    → Accept, larger transformation needed
LEGACY_SYNTAX:      → Accept, syntax upgrade to QFMD
QFMD:               → Skip Step 1, go directly to Step 2
UNKNOWN:            → Ask user
```

### 0d. Question Parsing

```python
def parse_questions(content: str, format_level: FormatLevel) -> List[Question]:
    """
    Split file into individual questions.
    
    Delimiters (depending on format):
    - SEMI_STRUCTURED: "# Question N:" or "## QN"
    - LEGACY_SYNTAX: "# Q001" + @question:
    - QFMD: "# Q001" + ^question
    """
```

**Output:**
```yaml
questions:
  - id: "Q001"
    title: "Muscle movement in the gastrointestinal tract"
    raw_content: "# Q001 Muscle movement...\n@question: Q001\n..."
    line_start: 145
    line_end: 198
    detected_type: "text_entry"  # or null if unknown
    
  - id: "Q002"
    title: "Where is bile produced"
    raw_content: "..."
    line_start: 200
    line_end: 265
    detected_type: "inline_choice"
```

### 0e. Resource Check

```python
def check_resources(questions: List[Question], base_path: str) -> ResourceReport:
    """
    Check that all referenced resources exist.
    
    Searches for:
    - Image references: ![alt](image.png), @image: file.png
    - Audio files: @audio: recording.mp3
    - Other files: @resource: data.csv
    """
```

**Output:**
```yaml
resource_check:
  total_references: 5
  found: 3
  missing: 2
  missing_details:
    - question: Q005
      resource: "bacteria_structure.png"
      type: "image"
      referenced_at: "line 234"
    - question: Q014
      resource: "virus_diagram.svg"
      type: "image"
      referenced_at: "line 456"
```

---

## PHASE 1: QUESTION LOOP (Main process)

### 1. READ Question

```python
def get_current_question(session: Session) -> QuestionContext:
    """
    Get current question with context.
    
    Returns:
        QuestionContext with:
        - question: Question object
        - position: "12 of 40"
        - previous_fixes: relevant previous fixes
    """
```

### 2. IDENTIFY Question Type

```python
def identify_type(question: Question) -> TypeIdentification:
    """
    Identify question type.
    
    Strategy:
    1. Explicit type field (^type, @type:, **Type**:)
    2. Infer from content (options → MC, blanks → text_entry)
    3. Ask user if unclear
    """
```

**Output:**
```yaml
type_identification:
  source: "explicit"  # or "inferred" or "user_provided"
  type: "multiple_choice_single"
  confidence: "high"  # high/medium/low
  alternatives: []    # if low confidence
  issues:
    - "Type specified as 'MCQ', normalised to 'multiple_choice_single'"
```

**Type inference rules:**
```python
TYPE_INFERENCE = {
    # Pattern → Type
    r"## Options\n.*\n[A-F][.)]": "multiple_choice_*",  # MC or MR
    r"\{\{blank_?\d+\}\}": "text_entry",
    r"\{\{dropdown_?\d+\}\}": "inline_choice",
    r"## Pairs|Match": "match",
    r"True.*False|True.*False": "true_false",
    r"## Scoring Rubric": "text_area",  # essay
}

# MC vs MR: check answer field
# "A" = single, "A, B, C" = multiple
```

### 3. LOAD Specification

```python
def load_type_spec(question_type: str) -> TypeSpecification:
    """
    Load specification for the question type.
    
    Location: /packages/qf-pipeline/src/qf_pipeline/specs/
    """
```

**Spec structure (see separate document for all types):**
```yaml
# specs/multiple_choice_single.yaml
name: "Multiple Choice (Single Answer)"
code: "multiple_choice_single"
inspera_type: "multipleChoice"

required_metadata:
  - field: "^question"
    pattern: "Q\\d{3}[A-Z]?"
    required: true
  - field: "^type"
    value: "multiple_choice_single"
    required: true
  - field: "^identifier"
    pattern: "[A-Z_]+_Q\\d+"
    required: true
  - field: "^points"
    type: "integer"
    min: 1
    max: 10
    required: true
  - field: "^labels"
    must_contain: ["#Bloom", "#Difficulty"]
    required: true

required_fields:
  - name: "question_text"
    required: true
  - name: "options"
    required: true
    constraints:
      min_items: 3
      max_items: 6
      format: "A. text"
  - name: "answer"
    required: true
    constraints:
      format: "single_letter"
      values: ["A", "B", "C", "D", "E", "F"]
  - name: "feedback"
    required: true
    subfields:
      - "general_feedback"
      - "correct_feedback"
      - "incorrect_feedback"
      - "unanswered_feedback"
```

### 4. COMPARE Question to Specification

```python
def compare_to_spec(question: Question, spec: TypeSpecification) -> ComparisonResult:
    """
    Compare question against specification.
    
    Returns:
        List of issues with severity and suggested fix
    """
```

**Output:**
```yaml
comparison_result:
  question_id: "Q001"
  question_type: "multiple_choice_single"
  
  issues:
    - severity: "critical"  # critical = cannot export
      category: "missing_metadata"
      field: "^labels"
      message: "Missing ^labels metadata"
      current: null
      suggestion: "^labels #EXAMPLE_COURSE #Remember #Easy"
      auto_fixable: false  # needs user input for Bloom/Difficulty
      
    - severity: "critical"
      category: "wrong_format"
      field: "options"
      message: "Options numbered 1-4 instead of A-D"
      current: "1. Option one\n2. Option two"
      suggestion: "A. Option one\nB. Option two"
      auto_fixable: true
      
    - severity: "warning"  # warning = can export but suboptimal
      category: "missing_field"
      field: "feedback.unanswered_feedback"
      message: "Missing unanswered_feedback"
      current: null
      suggestion: "Answer the question to receive feedback."
      auto_fixable: true
      
    - severity: "info"  # info = observation
      category: "style"
      field: "question_text"
      message: "Question text does not end with question mark"
      current: "What is the mitochondrion"
      suggestion: "What is the mitochondrion?"
      auto_fixable: true
      
  summary:
    critical: 2
    warning: 1
    info: 1
    can_export: false  # critical > 0
```

### 5. SUGGEST Corrections

```python
def format_suggestions(comparison: ComparisonResult) -> str:
    """
    Format suggestions for Claude to present.
    
    Returns:
        Markdown-formatted text for presentation
    """
```

**Output format for Claude:**
```markdown
## Q001: Muscle movement in the gastrointestinal tract

**Status:** ❌ Cannot be exported (2 critical problems)

### Critical problems (must be fixed):

1. **Missing ^labels metadata**
   - Current: (missing)
   - Suggestion: `^labels #EXAMPLE_COURSE #[BLOOM] #[DIFFICULTY]`
   - ❓ Which Bloom level? [Remember] [Understand] [Apply] [Analyze]
   - ❓ Which difficulty? [Easy] [Medium] [Hard]

2. **Wrong format on options**
   - Current: `1. Option one`
   - Suggestion: `A. Option one`
   - ✅ Can be fixed automatically

### Warnings (recommended):

3. **Missing unanswered_feedback**
   - Suggestion: "Answer the question to receive feedback."
   - ✅ Can be fixed automatically

---
**Actions:** [Fix all auto] [Skip] [Go back]
```

### 6. TEACHER Decides

```python
def get_teacher_decision(question_id: str, issues: List[Issue]) -> Decision:
    """
    Await teacher's decision.
    
    Decisions:
    - ACCEPT_ALL: Apply all suggestions
    - ACCEPT_AUTO: Apply only auto-fixable
    - MODIFY: Teacher specifies own values
    - SKIP: Skip this question (logged as warning)
    - BACK: Go back to previous question
    """
```

**User input format:**
```yaml
decision:
  action: "modify"
  modifications:
    - field: "^labels"
      value: "^labels #EXAMPLE_COURSE #CellBiology #Remember #Easy"
  accept_auto: true  # apply auto-fixable issues too
```

### 7. APPLY Fix to Current Question

```python
def apply_fixes(
    session: Session, 
    question_id: str, 
    fixes: List[Fix]
) -> ApplyResult:
    """
    Apply fixes to current question.
    
    Process:
    1. Backup current state
    2. Apply each fix
    3. Log changes
    4. Update session state
    """
```

**Change log entry:**
```yaml
change:
  timestamp: "2026-01-07T10:15:23Z"
  question: "Q001"
  fixes_applied:
    - field: "^labels"
      old: null
      new: "^labels #EXAMPLE_COURSE #CellBiology #Remember #Easy"
      source: "user_input"
    - field: "options"
      old: "1. Alt\n2. Alt"
      new: "A. Alt\nB. Alt"
      source: "auto_fix"
```

### 8. APPLY Same Fix to Similar Questions (KEY FEATURE)

```python
def find_similar_questions(
    session: Session,
    fix: Fix,
    question_type: str
) -> List[SimilarQuestion]:
    """
    Find questions where the same fix can be applied.
    
    "Similar" is defined as:
    - Same question type AND
    - Same type of issue (missing_labels, wrong_option_format, etc.)
    """
```

**Dialogue for batch-apply:**
```markdown
## Apply to similar questions?

Fix: **Change option format from 1-4 to A-D**

Found **8 questions** with the same problem:
- Q003: What does bile do... (options 1-4)
- Q008: Type of digestion... (options 1-4)
- Q010: Acidic liquid... (options 1-4)
- ... and 5 more

**Preview Q003:**
```
Current:
1. Breaks down proteins
2. Emulsifies fats
3. Neutralises stomach acid

After fix:
A. Breaks down proteins
B. Emulsifies fats
C. Neutralises stomach acid
```

[Apply to all 8] [Choose which] [Skip batch]
```

```python
def apply_batch_fix(
    session: Session,
    fix: Fix,
    target_questions: List[str]
) -> BatchResult:
    """
    Apply the same fix to multiple questions.
    
    Returns:
        Result per question (success/failure)
    """
```

**Batch result:**
```yaml
batch_result:
  fix_type: "option_format_1234_to_ABCD"
  total: 8
  success: 7
  failed: 1
  details:
    - question: "Q003"
      status: "success"
    - question: "Q012"
      status: "failed"
      reason: "Question already has A-D format"
```

### 9. MOVE to Next Question

```python
def next_question(session: Session, direction: str = "forward") -> QuestionContext:
    """
    Go to next question.
    
    Args:
        direction: "forward", "back", or question_id
    """
```

**Progress update:**
```yaml
progress:
  current: "Q002"
  position: "2 of 40"
  completed: ["Q001"]
  remaining: 39
  estimated_time: "~35 min"  # based on average per question
```

---

## PHASE 2: COMPLETION (After question loop)

### 2a. Summary Report

```python
def generate_summary(session: Session) -> SummaryReport:
    """
    Generate summary of Step 1.
    """
```

**Output:**
```yaml
summary:
  session_id: "uuid"
  duration: "45 minutes"
  
  questions:
    total: 40
    completed: 38
    skipped: 2
    with_warnings: 3
    
  changes:
    total_fixes: 156
    auto_fixes: 120
    manual_fixes: 36
    batch_fixes: 84  # 12 batch operations
    
  by_category:
    missing_labels: 40  # all questions
    wrong_option_format: 8
    missing_feedback: 15
    missing_identifier: 40
    
  skipped_questions:
    - id: "Q005"
      reason: "Image missing: bacteria.png"
    - id: "Q014"
      reason: "Teacher chose to skip"
      
  warnings:
    - id: "Q003"
      warning: "Feedback identical for correct/incorrect"
    - id: "Q007"
      warning: "Only 2 options (minimum 3)"
```

### 2b. Ready for Step 2?

```python
def check_ready_for_step2(session: Session) -> ReadinessCheck:
    """
    Check if the file is ready for validation.
    """
```

**Output:**
```yaml
readiness:
  ready: false
  blocking_issues:
    - "2 questions have critical problems (Q005, Q014)"
  warnings:
    - "3 questions have warnings that may affect quality"
  recommendation: "Fix Q005 and Q014 before Step 2"
```

### 2c. Transition to Step 2

```python
def transition_to_step2(session: Session) -> Step2Session:
    """
    End Step 1 and prepare for Step 2.
    
    Actions:
    - Save final working file
    - Generate changelog
    - Create Step 2 session
    """
```

---

## MCP TOOL INTERFACE

```python
# Tools exposed via MCP

@tool
def step1_start(
    source_file: str,
    output_folder: str = None,
    resume_session: str = None
) -> dict:
    """
    Start or resume Step 1 session.
    
    Args:
        source_file: Path to question file
        output_folder: Where output should be saved
        resume_session: Session ID to resume
    """

@tool
def step1_status() -> dict:
    """
    Get status for active session.
    
    Returns:
        Progress, current question, statistics
    """

@tool
def step1_get_question(question_id: str = None) -> dict:
    """
    Get question for review.
    
    Args:
        question_id: Specific question or None for current
    """

@tool
def step1_compare() -> dict:
    """
    Compare current question against specification.
    
    Returns:
        Issues with severity and suggestions
    """

@tool
def step1_apply_fix(
    fixes: List[dict],
    batch_apply: bool = False
) -> dict:
    """
    Apply fixes.
    
    Args:
        fixes: List of fixes to apply
        batch_apply: If True, apply to similar questions
    """

@tool
def step1_next(direction: str = "forward") -> dict:
    """
    Go to next question.
    
    Args:
        direction: "forward", "back", or question_id
    """

@tool
def step1_skip(reason: str = None) -> dict:
    """
    Skip current question.
    """

@tool
def step1_finish() -> dict:
    """
    End Step 1 and generate report.
    """
```

---

## FILE STRUCTURE FOR SPECS

```
/packages/qf-pipeline/src/qf_pipeline/
├── specs/
│   ├── __init__.py
│   ├── base.py              # BaseSpec class
│   ├── multiple_choice_single.yaml
│   ├── multiple_response.yaml
│   ├── text_entry.yaml
│   ├── inline_choice.yaml
│   ├── match.yaml
│   ├── true_false.yaml
│   ├── text_area.yaml       # essay/short_response
│   ├── audio_record.yaml
│   ├── hotspot.yaml
│   └── ... (all 17 types)
│
├── step1/
│   ├── __init__.py
│   ├── session.py           # Session management
│   ├── parser.py            # Question parsing
│   ├── detector.py          # Format detection
│   ├── comparator.py        # Compare to spec
│   ├── fixer.py             # Apply fixes
│   ├── batch.py             # Batch operations
│   └── reporter.py          # Summary reports
│
└── tools/
    └── step1_tools.py       # MCP tool definitions
```

---

## OPEN QUESTIONS

1. **Should Step 1 be able to CREATE missing feedback?**
   - If general_feedback is missing, should Claude suggest text?
   - Or just mark as "missing"?

2. **How to handle missing images?**
   - Skip the question?
   - Ask where the image is?
   - Accept without image (warning)?

3. **How strict should batch-apply be?**
   - Require exact same pattern?
   - Allow "fuzzy" matching?

4. **Session timeout?**
   - How long is session state saved?
   - Auto-save interval?

5. **Undo depth?**
   - How many steps back?
   - Per-question or global?

---

*Step 1 Specification v0.1 DRAFT | 2026-01-07*
