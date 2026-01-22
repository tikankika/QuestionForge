# STEP 1: GUIDED BUILD - KOMPLETT SPECIFIKATION

**Version:** 0.1 DRAFT  
**Datum:** 2026-01-07  
**Status:** För granskning innan implementation

---

## ÖVERSIKT

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STEP 1: GUIDED BUILD                             │
│                                                                          │
│  INPUT:  Markdown-fil med frågor (various formats)                      │
│  OUTPUT: Markdown-fil i QFMD format (redo för Step 2)                   │
│                                                                          │
│  PROCESS: Fråga-för-fråga genomgång med lärar-verifikation              │
│  KEY: Tydlig spec + Claude guidar + Human verifierar                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 0: INITIALIZATION (Före fråge-loop)

### 0a. Session Management

```python
def step1_start(file_path: str, resume: bool = False) -> Session:
    """
    Starta eller återuppta Step 1 session.
    
    Args:
        file_path: Sökväg till markdown-fil
        resume: True = fortsätt tidigare session
    
    Returns:
        Session med state
    """
```

**State som sparas:**
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
    new: "^labels #BIOG001X #Remember #Easy"
    timestamp: "2026-01-07T10:05:00Z"
```

### 0b. File Validation

```python
def validate_input_file(file_path: str) -> FileValidation:
    """
    Kontrollera att filen är en giltig fråge-fil.
    
    Checks:
    - Fil existerar
    - Är markdown (.md)
    - Innehåller minst en fråga
    - Inte tom
    - Encoding OK (UTF-8)
    """
```

**Resultat:**
```yaml
file_validation:
  exists: true
  is_markdown: true
  encoding: "utf-8"
  has_questions: true
  question_count: 40
  has_header: true  # Innehåll före ===QUESTIONS===
  errors: []
```

### 0c. Format Detection

```python
def detect_format(content: str) -> FormatLevel:
    """
    Identifiera vilken input-nivå filen har.
    
    Returns:
        FormatLevel.UNSTRUCTURED - behöver qf-scaffolding
        FormatLevel.SEMI_STRUCTURED - **Type**: format
        FormatLevel.LEGACY_SYNTAX - @question: format
        FormatLevel.QFMD - redan korrekt
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
elif "**FRÅGA:**" in content or "**RÄTT SVAR:**" in content:
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
    Splitta fil till individuella frågor.
    
    Delimiters (beroende på format):
    - SEMI_STRUCTURED: "# Question N:" eller "## QN"
    - LEGACY_SYNTAX: "# Q001" + @question:
    - QFMD: "# Q001" + ^question
    """
```

**Output:**
```yaml
questions:
  - id: "Q001"
    title: "Muskelrörelse i mag-tarmkanalen"
    raw_content: "# Q001 Muskelrörelse...\n@question: Q001\n..."
    line_start: 145
    line_end: 198
    detected_type: "text_entry"  # eller null om okänt
    
  - id: "Q002"
    title: "Var produceras galla"
    raw_content: "..."
    line_start: 200
    line_end: 265
    detected_type: "inline_choice"
```

### 0e. Resource Check

```python
def check_resources(questions: List[Question], base_path: str) -> ResourceReport:
    """
    Kontrollera att alla refererade resurser finns.
    
    Söker efter:
    - Bildreferenser: ![alt](image.png), @image: file.png
    - Ljudfiler: @audio: recording.mp3
    - Andra filer: @resource: data.csv
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
      resource: "bakterie_struktur.png"
      type: "image"
      referenced_at: "line 234"
    - question: Q014
      resource: "virus_diagram.svg"
      type: "image"
      referenced_at: "line 456"
```

---

## PHASE 1: QUESTION LOOP (Huvudprocess)

### 1. READ Question

```python
def get_current_question(session: Session) -> QuestionContext:
    """
    Hämta aktuell fråga med kontext.
    
    Returns:
        QuestionContext med:
        - question: Question object
        - position: "12 av 40"
        - previous_fixes: relevanta tidigare fixar
    """
```

### 2. IDENTIFY Question Type

```python
def identify_type(question: Question) -> TypeIdentification:
    """
    Identifiera frågetyp.
    
    Strategy:
    1. Explicit type field (^type, @type:, **Type**:)
    2. Infer from content (options → MC, blanks → text_entry)
    3. Ask user if unclear
    """
```

**Output:**
```yaml
type_identification:
  source: "explicit"  # eller "inferred" eller "user_provided"
  type: "multiple_choice_single"
  confidence: "high"  # high/medium/low
  alternatives: []    # om low confidence
  issues:
    - "Type specified as 'MCQ', normalized to 'multiple_choice_single'"
```

**Type inference rules:**
```python
TYPE_INFERENCE = {
    # Pattern → Type
    r"## Options\n.*\n[A-F][.)]": "multiple_choice_*",  # MC eller MR
    r"\{\{blank_?\d+\}\}": "text_entry",
    r"\{\{dropdown_?\d+\}\}": "inline_choice",
    r"## Pairs|Matcha": "match",
    r"Sant.*Falskt|True.*False": "true_false",
    r"## Scoring Rubric": "text_area",  # essay
}

# MC vs MR: kolla answer field
# "A" = single, "A, B, C" = multiple
```

### 3. LOAD Specification

```python
def load_type_spec(question_type: str) -> TypeSpecification:
    """
    Ladda specifikation för frågetypen.
    
    Location: /packages/qf-pipeline/src/qf_pipeline/specs/
    """
```

**Spec structure (se separat dokument för alla typer):**
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
    Jämför fråga mot specifikation.
    
    Returns:
        Lista av issues med severity och suggested fix
    """
```

**Output:**
```yaml
comparison_result:
  question_id: "Q001"
  question_type: "multiple_choice_single"
  
  issues:
    - severity: "critical"  # critical = kan inte exportera
      category: "missing_metadata"
      field: "^labels"
      message: "Saknar ^labels metadata"
      current: null
      suggestion: "^labels #BIOG001X #Remember #Easy"
      auto_fixable: false  # behöver user input för Bloom/Difficulty
      
    - severity: "critical"
      category: "wrong_format"
      field: "options"
      message: "Alternativ numrerade 1-4 istället för A-D"
      current: "1. Alternativ ett\n2. Alternativ två"
      suggestion: "A. Alternativ ett\nB. Alternativ två"
      auto_fixable: true
      
    - severity: "warning"  # warning = kan exportera men suboptimal
      category: "missing_field"
      field: "feedback.unanswered_feedback"
      message: "Saknar unanswered_feedback"
      current: null
      suggestion: "Besvara frågan för att få feedback."
      auto_fixable: true
      
    - severity: "info"  # info = observation
      category: "style"
      field: "question_text"
      message: "Frågetext slutar inte med frågetecken"
      current: "Vad är mitokondrien"
      suggestion: "Vad är mitokondrien?"
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
    Formatera förslag för Claude att presentera.
    
    Returns:
        Markdown-formaterad text för presentation
    """
```

**Output format för Claude:**
```markdown
## Q001: Muskelrörelse i mag-tarmkanalen

**Status:** ❌ Kan inte exporteras (2 kritiska problem)

### Kritiska problem (måste fixas):

1. **Saknar ^labels metadata**
   - Nuvarande: (saknas)
   - Förslag: `^labels #BIOG001X #[BLOOM] #[DIFFICULTY]`
   - ❓ Vilken Bloom-nivå? [Remember] [Understand] [Apply] [Analyze]
   - ❓ Vilken svårighetsgrad? [Easy] [Medium] [Hard]

2. **Fel format på alternativ**
   - Nuvarande: `1. Alternativ ett`
   - Förslag: `A. Alternativ ett`
   - ✅ Kan fixas automatiskt

### Varningar (rekommenderas):

3. **Saknar unanswered_feedback**
   - Förslag: "Besvara frågan för att få feedback."
   - ✅ Kan fixas automatiskt

---
**Åtgärder:** [Fixa alla auto] [Hoppa över] [Gå tillbaka]
```

### 6. TEACHER Decides

```python
def get_teacher_decision(question_id: str, issues: List[Issue]) -> Decision:
    """
    Invänta lärarens beslut.
    
    Decisions:
    - ACCEPT_ALL: Applicera alla förslag
    - ACCEPT_AUTO: Applicera bara auto-fixable
    - MODIFY: Läraren anger egna värden
    - SKIP: Hoppa över denna fråga (loggas som warning)
    - BACK: Gå tillbaka till föregående fråga
    """
```

**User input format:**
```yaml
decision:
  action: "modify"
  modifications:
    - field: "^labels"
      value: "^labels #BIOG001X #Cellbiologi #Remember #Easy"
  accept_auto: true  # applicera auto-fixable issues också
```

### 7. APPLY Fix to Current Question

```python
def apply_fixes(
    session: Session, 
    question_id: str, 
    fixes: List[Fix]
) -> ApplyResult:
    """
    Applicera fixar på aktuell fråga.
    
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
      new: "^labels #BIOG001X #Cellbiologi #Remember #Easy"
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
    Hitta frågor där samma fix kan appliceras.
    
    "Similar" definieras som:
    - Samma frågetyp OCH
    - Samma typ av issue (missing_labels, wrong_option_format, etc.)
    """
```

**Dialog för batch-apply:**
```markdown
## Applicera på liknande frågor?

Fix: **Ändra alternativ-format från 1-4 till A-D**

Hittade **8 frågor** med samma problem:
- Q003: Vad gör galla... (alternativ 1-4)
- Q008: Typ av nedbrytning... (alternativ 1-4)
- Q010: Sur vätska... (alternativ 1-4)
- ... och 5 till

**Förhandsgranskning Q003:**
```
Nuvarande:
1. Bryter ner proteiner
2. Emulgerar fetter
3. Neutraliserar magsyra

Efter fix:
A. Bryter ner proteiner
B. Emulgerar fetter
C. Neutraliserar magsyra
```

[Applicera på alla 8] [Välj vilka] [Hoppa över batch]
```

```python
def apply_batch_fix(
    session: Session,
    fix: Fix,
    target_questions: List[str]
) -> BatchResult:
    """
    Applicera samma fix på flera frågor.
    
    Returns:
        Resultat per fråga (success/failure)
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
      reason: "Frågan har redan A-D format"
```

### 9. MOVE to Next Question

```python
def next_question(session: Session, direction: str = "forward") -> QuestionContext:
    """
    Gå till nästa fråga.
    
    Args:
        direction: "forward", "back", or question_id
    """
```

**Progress update:**
```yaml
progress:
  current: "Q002"
  position: "2 av 40"
  completed: ["Q001"]
  remaining: 39
  estimated_time: "~35 min"  # baserat på snitt per fråga
```

---

## PHASE 2: COMPLETION (Efter fråge-loop)

### 2a. Summary Report

```python
def generate_summary(session: Session) -> SummaryReport:
    """
    Generera sammanfattning av Step 1.
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
    missing_labels: 40  # alla frågor
    wrong_option_format: 8
    missing_feedback: 15
    missing_identifier: 40
    
  skipped_questions:
    - id: "Q005"
      reason: "Bild saknas: bakterie.png"
    - id: "Q014"
      reason: "Läraren valde att hoppa över"
      
  warnings:
    - id: "Q003"
      warning: "Feedback identical för correct/incorrect"
    - id: "Q007"
      warning: "Endast 2 alternativ (minimum 3)"
```

### 2b. Ready for Step 2?

```python
def check_ready_for_step2(session: Session) -> ReadinessCheck:
    """
    Kontrollera om filen är redo för validering.
    """
```

**Output:**
```yaml
readiness:
  ready: false
  blocking_issues:
    - "2 frågor har kritiska problem (Q005, Q014)"
  warnings:
    - "3 frågor har varningar som kan påverka kvalitet"
  recommendation: "Fixa Q005 och Q014 innan Step 2"
```

### 2c. Transition to Step 2

```python
def transition_to_step2(session: Session) -> Step2Session:
    """
    Avsluta Step 1 och förbered för Step 2.
    
    Actions:
    - Spara final working file
    - Generera changelog
    - Skapa Step 2 session
    """
```

---

## MCP TOOL INTERFACE

```python
# Tools som exponeras via MCP

@tool
def step1_start(
    source_file: str,
    output_folder: str = None,
    resume_session: str = None
) -> dict:
    """
    Starta eller återuppta Step 1 session.
    
    Args:
        source_file: Sökväg till fråge-fil
        output_folder: Var output ska sparas
        resume_session: Session ID för att återuppta
    """

@tool
def step1_status() -> dict:
    """
    Hämta status för aktiv session.
    
    Returns:
        Progress, current question, statistics
    """

@tool
def step1_get_question(question_id: str = None) -> dict:
    """
    Hämta fråga för granskning.
    
    Args:
        question_id: Specifik fråga eller None för aktuell
    """

@tool
def step1_compare() -> dict:
    """
    Jämför aktuell fråga mot specifikation.
    
    Returns:
        Issues with severity and suggestions
    """

@tool
def step1_apply_fix(
    fixes: List[dict],
    batch_apply: bool = False
) -> dict:
    """
    Applicera fixar.
    
    Args:
        fixes: Lista av fixar att applicera
        batch_apply: Om True, applicera på liknande frågor
    """

@tool
def step1_next(direction: str = "forward") -> dict:
    """
    Gå till nästa fråga.
    
    Args:
        direction: "forward", "back", or question_id
    """

@tool
def step1_skip(reason: str = None) -> dict:
    """
    Hoppa över aktuell fråga.
    """

@tool
def step1_finish() -> dict:
    """
    Avsluta Step 1 och generera rapport.
    """
```

---

## FIL-STRUKTUR FÖR SPECS

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
│   └── ... (alla 17 typer)
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

## ÖPPNA FRÅGOR

1. **Ska Step 1 kunna SKAPA saknade feedback?**
   - Om general_feedback saknas, ska Claude föreslå text?
   - Eller bara markera som "saknas"?

2. **Hur hantera bilder som saknas?**
   - Skip frågan?
   - Fråga var bilden finns?
   - Acceptera utan bild (varning)?

3. **Hur strikt ska batch-apply vara?**
   - Kräva exakt samma pattern?
   - Tillåta "fuzzy" matching?

4. **Session timeout?**
   - Hur länge sparas session state?
   - Auto-save intervall?

5. **Undo-djup?**
   - Hur många steg tillbaka?
   - Per-fråga eller global?

---

*Step 1 Specifikation v0.1 DRAFT | 2026-01-07*
