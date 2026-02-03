# STEP 1: GUIDED BUILD - IMPLEMENTATION INSTRUCTIONS

**För:** Code/Developer  
**Version:** 1.0  
**Datum:** 2026-01-07  
**Språk:** Python 3.11+  
**Location:** `/packages/qf-pipeline/src/qf_pipeline/step1/`

---

## OVERVIEW

Bygg ett MCP-verktyg som hjälper lärare transformera quiz-frågor från olika input-format till valid v6.5 markdown-format genom interaktiv dialog.

```
INPUT:  Markdown-fil med frågor (varierade format)
OUTPUT: Markdown-fil i valid v6.5 format
METHOD: Fråga-för-fråga genomgång med lärar-verifikation
```

---

## ARCHITECTURE

```
qf-pipeline/src/qf_pipeline/
├── step1/
│   ├── __init__.py
│   ├── session.py        # Session state management
│   ├── parser.py         # Parse markdown to questions
│   ├── detector.py       # Detect format level and question type
│   ├── analyzer.py       # Find issues by comparing to requirements
│   ├── transformer.py    # Apply fixes (regex + structure)
│   └── prompts.py        # User interaction prompts
│
└── tools/
    └── step1_tools.py    # MCP tool definitions
```

---

## FILE 1: session.py

```python
"""
Session management for Step 1 Guided Build.
Tracks progress, changes, and allows resume.
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

@dataclass
class Change:
    """Record of a single change made."""
    timestamp: str
    question_id: str
    field: str
    old_value: Optional[str]
    new_value: str
    change_type: str  # 'auto', 'user_input', 'batch'

@dataclass
class QuestionStatus:
    """Status of a single question."""
    question_id: str
    status: str  # 'pending', 'completed', 'skipped', 'has_warnings'
    issues_found: int = 0
    issues_fixed: int = 0
    issues_skipped: int = 0

@dataclass
class Session:
    """Step 1 session state."""
    session_id: str
    source_file: str
    working_file: str
    output_folder: str
    created_at: str
    updated_at: str
    
    # Progress
    total_questions: int = 0
    current_index: int = 0
    questions: List[QuestionStatus] = field(default_factory=list)
    
    # Changes log
    changes: List[Change] = field(default_factory=list)
    
    # Format info
    detected_format: str = ""  # 'v63', 'semi_structured', 'raw'
    
    def save(self, path: Path):
        """Save session to JSON file."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, path: Path) -> 'Session':
        """Load session from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Reconstruct dataclasses
        data['questions'] = [QuestionStatus(**q) for q in data['questions']]
        data['changes'] = [Change(**c) for c in data['changes']]
        return cls(**data)
    
    @classmethod
    def create_new(cls, source_file: str, output_folder: str) -> 'Session':
        """Create a new session."""
        now = datetime.now().isoformat()
        session_id = str(uuid.uuid4())[:8]
        
        # Create working file path
        source_path = Path(source_file)
        working_file = str(Path(output_folder) / f"{source_path.stem}_working.md")
        
        return cls(
            session_id=session_id,
            source_file=source_file,
            working_file=working_file,
            output_folder=output_folder,
            created_at=now,
            updated_at=now
        )
    
    def get_current_question(self) -> Optional[QuestionStatus]:
        """Get current question being processed."""
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None
    
    def add_change(self, question_id: str, field: str, 
                   old_value: str, new_value: str, change_type: str):
        """Record a change."""
        self.changes.append(Change(
            timestamp=datetime.now().isoformat(),
            question_id=question_id,
            field=field,
            old_value=old_value,
            new_value=new_value,
            change_type=change_type
        ))
        self.updated_at = datetime.now().isoformat()
    
    def get_progress(self) -> Dict:
        """Get progress summary."""
        completed = sum(1 for q in self.questions if q.status == 'completed')
        skipped = sum(1 for q in self.questions if q.status == 'skipped')
        return {
            'total': self.total_questions,
            'current': self.current_index + 1,
            'completed': completed,
            'skipped': skipped,
            'remaining': self.total_questions - completed - skipped,
            'percent': int((completed / self.total_questions) * 100) if self.total_questions > 0 else 0
        }
```

---

## FILE 2: parser.py

```python
"""
Parse markdown file into individual questions.
Handles multiple input formats.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass
class ParsedQuestion:
    """A parsed question from the source file."""
    question_id: str           # Q001, Q002, etc.
    title: Optional[str]       # Title if present
    raw_content: str           # Original content
    line_start: int            # Starting line in file
    line_end: int              # Ending line in file
    detected_type: Optional[str]  # Detected question type

# Question delimiters for different formats
QUESTION_PATTERNS = [
    # v6.5/v6.3: # Q001 Title
    r'^#\s*(Q\d{3}[A-Z]?)\s*(.*?)$',
    
    # Semi-structured: # Question 1: Title
    r'^#\s*Question\s*(\d+):?\s*(.*?)$',
    
    # Alternative: ## Q001
    r'^##\s*(Q\d{3}[A-Z]?)\s*(.*?)$',
]

def parse_file(content: str) -> List[ParsedQuestion]:
    """
    Parse markdown content into list of questions.
    
    Args:
        content: Full markdown file content
        
    Returns:
        List of ParsedQuestion objects
    """
    lines = content.split('\n')
    questions = []
    
    # Find all question boundaries
    boundaries = []  # [(line_num, question_id, title), ...]
    
    for i, line in enumerate(lines):
        for pattern in QUESTION_PATTERNS:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                q_id = match.group(1)
                title = match.group(2).strip() if match.group(2) else None
                
                # Normalize question ID
                if q_id.isdigit():
                    q_id = f"Q{int(q_id):03d}"
                
                boundaries.append((i, q_id, title))
                break
    
    # Extract content between boundaries
    for idx, (line_num, q_id, title) in enumerate(boundaries):
        # End is either next question or end of file
        if idx + 1 < len(boundaries):
            end_line = boundaries[idx + 1][0]
        else:
            end_line = len(lines)
        
        # Extract raw content
        raw_content = '\n'.join(lines[line_num:end_line])
        
        # Detect question type
        detected_type = detect_question_type(raw_content)
        
        questions.append(ParsedQuestion(
            question_id=q_id,
            title=title,
            raw_content=raw_content,
            line_start=line_num + 1,  # 1-indexed
            line_end=end_line,
            detected_type=detected_type
        ))
    
    return questions

def detect_question_type(content: str) -> Optional[str]:
    """
    Detect question type from content.
    
    Returns:
        Question type string or None if unclear
    """
    content_lower = content.lower()
    
    # Explicit type declaration
    type_match = re.search(r'(?:\^type|@type:|type:)\s*(\w+)', content, re.IGNORECASE)
    if type_match:
        return normalize_type(type_match.group(1))
    
    # Infer from content patterns
    if '{{blank' in content_lower or '{{blank-' in content_lower:
        return 'text_entry'
    
    if '{{dropdown' in content_lower or '{{dropdown-' in content_lower:
        return 'inline_choice'
    
    if re.search(r'\|\s*\w+\s*\|', content):  # Table pattern
        if 'pair' in content_lower or 'match' in content_lower:
            return 'match'
    
    # Check for options/choices
    if re.search(r'^[A-F][.)]\s', content, re.MULTILINE) or \
       re.search(r'^\d+[.)]\s', content, re.MULTILINE):
        # Has options - but single or multiple?
        answer_match = re.search(r'(?:answer|svar|rätt).*?([A-F](?:\s*,\s*[A-F])*)', content, re.IGNORECASE)
        if answer_match:
            answer = answer_match.group(1)
            if ',' in answer:
                return 'multiple_response'
        return 'multiple_choice_single'
    
    # Essay/text area indicators
    if 'rubric' in content_lower or 'scoring rubric' in content_lower:
        return 'text_area'
    
    if 'short_response' in content_lower or 'essay' in content_lower:
        return 'text_area'
    
    return None

def normalize_type(type_str: str) -> str:
    """Normalize type string to standard format."""
    type_map = {
        'mc': 'multiple_choice_single',
        'mcq': 'multiple_choice_single',
        'multiple_choice': 'multiple_choice_single',
        'multiplechoice': 'multiple_choice_single',
        'mr': 'multiple_response',
        'multipleresponse': 'multiple_response',
        'fib': 'text_entry',
        'fill_in_blank': 'text_entry',
        'fillinblank': 'text_entry',
        'fillblank': 'text_entry',
        'dropdown': 'inline_choice',
        'inlinechoice': 'inline_choice',
        'matching': 'match',
        'essay': 'text_area',
        'short_response': 'text_area',
        'shortresponse': 'text_area',
        'textarea': 'text_area',
    }
    normalized = type_str.lower().replace(' ', '_').replace('-', '_')
    return type_map.get(normalized, normalized)
```

---

## FILE 3: detector.py

```python
"""
Detect input format level.
"""

import re
from enum import Enum

class FormatLevel(Enum):
    """Input format levels."""
    VALID_V65 = 'v65'           # Already valid, skip Step 1
    OLD_SYNTAX_V63 = 'v63'      # Has @field: but old syntax
    SEMI_STRUCTURED = 'semi'    # Has ## headers, **Type**: etc
    RAW = 'raw'                 # Unstructured, needs scaffolding
    UNKNOWN = 'unknown'

def detect_format(content: str) -> FormatLevel:
    """
    Detect the format level of input content.
    
    Args:
        content: Full file content
        
    Returns:
        FormatLevel enum value
    """
    # Check for v6.5 markers
    has_caret_metadata = bool(re.search(r'^\^(question|type|identifier)', content, re.MULTILINE))
    has_field_markers = bool(re.search(r'^@field:', content, re.MULTILINE))
    has_end_field = bool(re.search(r'^@end_field', content, re.MULTILINE))
    
    if has_caret_metadata and has_field_markers and has_end_field:
        return FormatLevel.VALID_V65
    
    # Check for v6.3 markers (old syntax)
    has_at_metadata = bool(re.search(r'^@(question|type|identifier):', content, re.MULTILINE))
    
    if has_at_metadata and has_field_markers:
        return FormatLevel.OLD_SYNTAX_V63
    
    # Check for semi-structured markers
    has_bold_type = bool(re.search(r'\*\*Type\*\*:', content, re.IGNORECASE))
    has_markdown_headers = bool(re.search(r'^##\s+(Question Text|Options|Answer|Feedback)', content, re.MULTILINE | re.IGNORECASE))
    
    if has_bold_type or has_markdown_headers:
        return FormatLevel.SEMI_STRUCTURED
    
    # Check for raw Swedish format
    has_raw_swedish = bool(re.search(r'\*\*(FRÅGA|RÄTT SVAR|FELAKTIGA):', content, re.IGNORECASE))
    
    if has_raw_swedish:
        return FormatLevel.RAW
    
    # If has any question-like structure
    has_questions = bool(re.search(r'^#.*Q\d{3}|^#\s*Question\s*\d+', content, re.MULTILINE | re.IGNORECASE))
    
    if has_questions:
        return FormatLevel.SEMI_STRUCTURED
    
    return FormatLevel.UNKNOWN

def get_format_description(level: FormatLevel) -> str:
    """Get human-readable description of format level."""
    descriptions = {
        FormatLevel.VALID_V65: "Valid v6.5 format - redo för Step 2",
        FormatLevel.OLD_SYNTAX_V63: "Gammal syntax (v6.3) - behöver syntax-uppgradering",
        FormatLevel.SEMI_STRUCTURED: "Semi-strukturerat - behöver omformatering",
        FormatLevel.RAW: "Ostrukturerat - behöver qf-scaffolding först",
        FormatLevel.UNKNOWN: "Okänt format - behöver manuell granskning"
    }
    return descriptions.get(level, "Okänt")
```

---

## FILE 4: analyzer.py

```python
"""
Analyze questions and find issues.
"""

import re
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class Severity(Enum):
    CRITICAL = 'critical'  # Must fix to export
    WARNING = 'warning'    # Should fix for quality
    INFO = 'info'          # Nice to fix

@dataclass
class Issue:
    """An issue found in a question."""
    severity: Severity
    category: str
    field: str
    message: str
    current_value: Optional[str] = None
    suggested_value: Optional[str] = None
    auto_fixable: bool = False
    prompt_key: Optional[str] = None  # Key for user prompt if needed
    transform_id: Optional[str] = None  # ID for transformer

# Required metadata for ALL question types
REQUIRED_METADATA = [
    ('^question', r'^\^question\s+Q\d{3}', 'Fråge-ID (Q001, Q002, etc.)'),
    ('^type', r'^\^type\s+\w+', 'Frågetyp'),
    ('^identifier', r'^\^identifier\s+\w+', 'Unik identifierare'),
    ('^points', r'^\^points\s+\d+', 'Poäng'),
    ('^labels', r'^\^labels\s+.+', 'Etiketter med Bloom och Difficulty'),
]

# Required fields per question type
TYPE_REQUIRED_FIELDS = {
    'multiple_choice_single': ['question_text', 'options', 'answer', 'feedback'],
    'multiple_response': ['question_text', 'options', 'answer', 'scoring', 'feedback'],
    'text_entry': ['question_text', 'blanks', 'feedback'],
    'inline_choice': ['question_text', 'feedback'],  # dropdown_N fields detected separately
    'match': ['question_text', 'pairs', 'feedback'],
    'text_area': ['question_text', 'feedback'],
    'true_false': ['question_text', 'answer', 'feedback'],
}

# Bloom levels and difficulty values
BLOOM_LEVELS = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
DIFFICULTY_LEVELS = ['Easy', 'Medium', 'Hard']

def analyze_question(content: str, question_type: Optional[str] = None) -> List[Issue]:
    """
    Analyze a question and return list of issues.
    
    Args:
        content: Question content (single question)
        question_type: Detected or specified question type
        
    Returns:
        List of Issue objects
    """
    issues = []
    
    # 1. Check required metadata
    issues.extend(_check_metadata(content))
    
    # 2. Check old syntax that needs transformation
    issues.extend(_check_old_syntax(content))
    
    # 3. Check labels for Bloom and Difficulty
    issues.extend(_check_labels(content))
    
    # 4. Check type-specific required fields
    if question_type:
        issues.extend(_check_required_fields(content, question_type))
    
    # 5. Check options format
    issues.extend(_check_options_format(content))
    
    # 6. Check placeholder syntax
    issues.extend(_check_placeholders(content))
    
    # 7. Check field structure (@end_field)
    issues.extend(_check_field_structure(content))
    
    # 8. Check feedback completeness
    issues.extend(_check_feedback(content))
    
    return issues

def _check_metadata(content: str) -> List[Issue]:
    """Check for required metadata."""
    issues = []
    
    for field, pattern, description in REQUIRED_METADATA:
        if not re.search(pattern, content, re.MULTILINE):
            # Check if old syntax exists
            old_field = field.replace('^', '@') + ':'
            if re.search(f'^{re.escape(old_field)}', content, re.MULTILINE):
                issues.append(Issue(
                    severity=Severity.CRITICAL,
                    category='old_syntax',
                    field=field,
                    message=f"Gammal syntax '{old_field}' → '{field}'",
                    auto_fixable=True,
                    transform_id='metadata_syntax'
                ))
            else:
                prompt_key = None
                auto_fix = False
                
                if field == '^identifier':
                    auto_fix = True
                    prompt_key = 'confirm_identifier'
                elif field == '^labels':
                    prompt_key = 'missing_labels'
                elif field == '^points':
                    auto_fix = True
                    
                issues.append(Issue(
                    severity=Severity.CRITICAL,
                    category='missing_metadata',
                    field=field,
                    message=f"Saknar {field} ({description})",
                    auto_fixable=auto_fix,
                    prompt_key=prompt_key
                ))
    
    return issues

def _check_old_syntax(content: str) -> List[Issue]:
    """Check for old syntax patterns."""
    issues = []
    
    # Old metadata patterns
    old_patterns = [
        (r'^@question:', '^question', 'metadata_syntax'),
        (r'^@type:', '^type', 'metadata_syntax'),
        (r'^@identifier:', '^identifier', 'metadata_syntax'),
        (r'^@title:', '^title', 'metadata_syntax'),
        (r'^@points:', '^points', 'metadata_syntax'),
        (r'^@tags:', '^labels', 'metadata_syntax'),
        (r'^@labels:', '^labels', 'metadata_syntax'),
    ]
    
    for old_pattern, new_syntax, transform_id in old_patterns:
        if re.search(old_pattern, content, re.MULTILINE):
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category='old_syntax',
                field=new_syntax,
                message=f"Gammal syntax: {old_pattern.replace('^', '').replace(':', '')} → {new_syntax}",
                auto_fixable=True,
                transform_id=transform_id
            ))
    
    # Old in-field patterns
    infield_patterns = [
        (r'\*\*Correct Answers?:\*\*', '^Correct_Answers', 'infield_syntax'),
        (r'\*\*Case Sensitive:\*\*', '^Case_Sensitive', 'infield_syntax'),
        (r'\*\*Options:\*\*', '^Options', 'infield_syntax'),
        (r'\*\*Correct:\*\*', '^Correct', 'infield_syntax'),
    ]
    
    for old_pattern, new_syntax, transform_id in infield_patterns:
        if re.search(old_pattern, content):
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category='old_syntax',
                field=new_syntax,
                message=f"Gammal in-field syntax → {new_syntax}",
                auto_fixable=True,
                transform_id=transform_id
            ))
    
    return issues

def _check_labels(content: str) -> List[Issue]:
    """Check that labels contain Bloom and Difficulty."""
    issues = []
    
    labels_match = re.search(r'(?:\^labels|@tags:)\s+(.+)$', content, re.MULTILINE)
    if labels_match:
        labels = labels_match.group(1)
        
        has_bloom = any(level in labels for level in BLOOM_LEVELS)
        has_difficulty = any(level in labels for level in DIFFICULTY_LEVELS)
        
        if not has_bloom:
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category='incomplete_labels',
                field='^labels',
                message="Labels saknar Bloom-nivå (Remember/Understand/Apply/Analyze)",
                current_value=labels,
                prompt_key='select_bloom'
            ))
        
        if not has_difficulty:
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category='incomplete_labels',
                field='^labels',
                message="Labels saknar svårighetsgrad (Easy/Medium/Hard)",
                current_value=labels,
                prompt_key='select_difficulty'
            ))
    
    return issues

def _check_required_fields(content: str, question_type: str) -> List[Issue]:
    """Check that required fields exist for the question type."""
    issues = []
    
    required = TYPE_REQUIRED_FIELDS.get(question_type, [])
    
    for field_name in required:
        # Check for @field: field_name
        if not re.search(f'@field:\\s*{field_name}', content, re.IGNORECASE):
            # Maybe it exists in old format (## Field Name)
            header_pattern = f'##\\s*{field_name.replace("_", " ")}'
            if re.search(header_pattern, content, re.IGNORECASE):
                issues.append(Issue(
                    severity=Severity.CRITICAL,
                    category='wrong_format',
                    field=field_name,
                    message=f"Field '{field_name}' har fel format (## header → @field:)",
                    auto_fixable=True,
                    transform_id='header_to_field'
                ))
            else:
                issues.append(Issue(
                    severity=Severity.CRITICAL,
                    category='missing_field',
                    field=field_name,
                    message=f"Saknar @field: {field_name}",
                    prompt_key=f'add_{field_name}'
                ))
    
    return issues

def _check_options_format(content: str) -> List[Issue]:
    """Check options are formatted correctly (A. B. C. not 1. 2. 3.)."""
    issues = []
    
    # Look for numbered options
    if re.search(r'^\d+[.)]\s+\w', content, re.MULTILINE):
        # Check if this is within options section
        options_section = _extract_section(content, 'options')
        if options_section and re.search(r'^\d+[.)]\s', options_section, re.MULTILINE):
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category='wrong_format',
                field='options',
                message="Alternativ numrerade (1. 2. 3.) → ska vara bokstäver (A. B. C.)",
                auto_fixable=True,
                transform_id='numbered_to_letter_options'
            ))
    
    # Look for lowercase options
    if re.search(r'^[a-f][.)]\s+\w', content, re.MULTILINE):
        options_section = _extract_section(content, 'options')
        if options_section and re.search(r'^[a-f][.)]\s', options_section, re.MULTILINE):
            issues.append(Issue(
                severity=Severity.WARNING,
                category='wrong_format',
                field='options',
                message="Alternativ med små bokstäver (a. b. c.) → stora (A. B. C.)",
                auto_fixable=True,
                transform_id='lowercase_to_upper_options'
            ))
    
    return issues

def _check_placeholders(content: str) -> List[Issue]:
    """Check placeholder syntax."""
    issues = []
    
    # Old blank syntax
    if re.search(r'\{\{BLANK-\d+\}\}', content):
        issues.append(Issue(
            severity=Severity.CRITICAL,
            category='old_syntax',
            field='placeholders',
            message="Gammal syntax {{BLANK-1}} → {{blank_1}}",
            auto_fixable=True,
            transform_id='placeholder_syntax'
        ))
    
    # Old dropdown syntax
    if re.search(r'\{\{DROPDOWN-\d+\}\}', content):
        issues.append(Issue(
            severity=Severity.CRITICAL,
            category='old_syntax',
            field='placeholders',
            message="Gammal syntax {{DROPDOWN-1}} → {{dropdown_1}}",
            auto_fixable=True,
            transform_id='placeholder_syntax'
        ))
    
    return issues

def _check_field_structure(content: str) -> List[Issue]:
    """Check @field: and @end_field balance."""
    issues = []
    
    field_starts = len(re.findall(r'^@field:', content, re.MULTILINE))
    field_ends = len(re.findall(r'^@end_field', content, re.MULTILINE))
    
    if field_starts > field_ends:
        issues.append(Issue(
            severity=Severity.CRITICAL,
            category='structure',
            field='@end_field',
            message=f"Saknar {field_starts - field_ends} st @end_field",
            auto_fixable=True,
            transform_id='add_end_fields'
        ))
    
    # Check for nested fields using @field: instead of @@field:
    # This is tricky to detect automatically
    
    return issues

def _check_feedback(content: str) -> List[Issue]:
    """Check feedback completeness."""
    issues = []
    
    # Required feedback subfields for auto-graded
    required_feedback = [
        'general_feedback',
        'correct_feedback', 
        'incorrect_feedback',
        'unanswered_feedback'
    ]
    
    feedback_section = _extract_section(content, 'feedback')
    if feedback_section:
        for subfield in required_feedback:
            if subfield not in feedback_section.lower():
                issues.append(Issue(
                    severity=Severity.WARNING,
                    category='missing_feedback',
                    field=subfield,
                    message=f"Saknar {subfield}",
                    prompt_key='suggest_feedback'
                ))
    
    return issues

def _extract_section(content: str, section_name: str) -> Optional[str]:
    """Extract content of a section/field."""
    # Try @field: format
    pattern = f'@field:\\s*{section_name}\\s*\\n(.*?)(?=@end_field|@field:|$)'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Try ## header format
    pattern = f'##\\s*{section_name.replace("_", " ")}\\s*\\n(.*?)(?=^##|^#|$)'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE | re.MULTILINE)
    if match:
        return match.group(1)
    
    return None
```

---

## FILE 5: transformer.py

```python
"""
Apply transformations to fix issues.
"""

import re
from typing import Tuple, List, Dict, Callable

# ════════════════════════════════════════════════════════════════════
# TRANSFORM REGISTRY
# ════════════════════════════════════════════════════════════════════

class Transformer:
    """Registry of all transforms."""
    
    def __init__(self):
        self._transforms: Dict[str, Callable] = {}
        self._register_all()
    
    def _register_all(self):
        """Register all transform functions."""
        self._transforms = {
            'metadata_syntax': self._transform_metadata_syntax,
            'infield_syntax': self._transform_infield_syntax,
            'placeholder_syntax': self._transform_placeholder_syntax,
            'numbered_to_letter_options': self._transform_numbered_options,
            'lowercase_to_upper_options': self._transform_lowercase_options,
            'header_to_field': self._transform_header_to_field,
            'add_end_fields': self._transform_add_end_fields,
        }
    
    def apply(self, transform_id: str, content: str) -> Tuple[str, bool, str]:
        """
        Apply a transform.
        
        Returns:
            (transformed_content, success, description)
        """
        if transform_id not in self._transforms:
            return content, False, f"Unknown transform: {transform_id}"
        
        try:
            result, description = self._transforms[transform_id](content)
            return result, True, description
        except Exception as e:
            return content, False, f"Transform failed: {str(e)}"
    
    def apply_all_auto(self, content: str) -> Tuple[str, List[str]]:
        """
        Apply all auto-fixable transforms.
        
        Returns:
            (transformed_content, list_of_descriptions)
        """
        changes = []
        
        # Order matters - do metadata first, then content
        transform_order = [
            'metadata_syntax',
            'infield_syntax', 
            'placeholder_syntax',
            'numbered_to_letter_options',
            'lowercase_to_upper_options',
            'add_end_fields',
        ]
        
        for transform_id in transform_order:
            new_content, success, description = self.apply(transform_id, content)
            if success and new_content != content:
                content = new_content
                changes.append(description)
        
        return content, changes
    
    # ════════════════════════════════════════════════════════════════
    # TRANSFORM IMPLEMENTATIONS
    # ════════════════════════════════════════════════════════════════
    
    def _transform_metadata_syntax(self, content: str) -> Tuple[str, str]:
        """Transform @key: value → ^key value"""
        transforms = [
            (r'^@question:\s*(.+)$', r'^question \1'),
            (r'^@type:\s*(.+)$', r'^type \1'),
            (r'^@identifier:\s*(.+)$', r'^identifier \1'),
            (r'^@title:\s*(.+)$', r'^title \1'),
            (r'^@points:\s*(.+)$', r'^points \1'),
            (r'^@tags:\s*(.+)$', r'^labels \1'),
            (r'^@labels:\s*(.+)$', r'^labels \1'),
            (r'^@shuffle:\s*(.+)$', r'^shuffle \1'),
            (r'^@language:\s*(.+)$', r'^language \1'),
        ]
        
        original = content
        for pattern, replacement in transforms:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        if content != original:
            return content, "Konverterade metadata-syntax (@key: → ^key)"
        return content, ""
    
    def _transform_infield_syntax(self, content: str) -> Tuple[str, str]:
        """Transform **Key:** → ^Key"""
        transforms = [
            (r'\*\*Correct Answers?:\*\*', '^Correct_Answers'),
            (r'\*\*Case Sensitive:\*\*\s*(Yes|No|True|False)', r'^Case_Sensitive \1'),
            (r'\*\*Options:\*\*', '^Options'),
            (r'\*\*Correct:\*\*\s*(.+)', r'^Correct \1'),
            (r'\*\*Type:\*\*\s*(.+)', r'^Type \1'),
            (r'\*\*Points:\*\*\s*(.+)', r'^Points \1'),
        ]
        
        original = content
        for pattern, replacement in transforms:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        if content != original:
            return content, "Konverterade in-field syntax (**Key:** → ^Key)"
        return content, ""
    
    def _transform_placeholder_syntax(self, content: str) -> Tuple[str, str]:
        """Transform {{BLANK-1}} → {{blank_1}}"""
        transforms = [
            (r'\{\{BLANK-(\d+)\}\}', r'{{blank_\1}}'),
            (r'\{\{BLANK(\d+)\}\}', r'{{blank_\1}}'),
            (r'\{\{DROPDOWN-(\d+)\}\}', r'{{dropdown_\1}}'),
            (r'\{\{DROPDOWN(\d+)\}\}', r'{{dropdown_\1}}'),
        ]
        
        original = content
        for pattern, replacement in transforms:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        if content != original:
            return content, "Konverterade placeholder-syntax"
        return content, ""
    
    def _transform_numbered_options(self, content: str) -> Tuple[str, str]:
        """Transform 1. 2. 3. → A. B. C. in options section."""
        
        def replace_in_options(match):
            options_content = match.group(1)
            number_map = {'1': 'A', '2': 'B', '3': 'C', '4': 'D', '5': 'E', '6': 'F'}
            
            for num, letter in number_map.items():
                options_content = re.sub(
                    f'^{num}[.)\\s]\\s*',
                    f'{letter}. ',
                    options_content,
                    flags=re.MULTILINE
                )
            
            return f'@field: options\n{options_content}'
        
        # Try to find options section
        original = content
        content = re.sub(
            r'@field:\s*options\s*\n(.*?)(?=@end_field|@field:|$)',
            replace_in_options,
            content,
            flags=re.DOTALL
        )
        
        if content != original:
            return content, "Konverterade numrerade alternativ till bokstäver"
        return content, ""
    
    def _transform_lowercase_options(self, content: str) -> Tuple[str, str]:
        """Transform a. b. c. → A. B. C."""
        
        def replace_in_options(match):
            options_content = match.group(1)
            
            for letter in 'abcdef':
                options_content = re.sub(
                    f'^{letter}[.)\\s]\\s*',
                    f'{letter.upper()}. ',
                    options_content,
                    flags=re.MULTILINE
                )
            
            return f'@field: options\n{options_content}'
        
        original = content
        content = re.sub(
            r'@field:\s*options\s*\n(.*?)(?=@end_field|@field:|$)',
            replace_in_options,
            content,
            flags=re.DOTALL
        )
        
        if content != original:
            return content, "Konverterade små bokstäver till stora i alternativ"
        return content, ""
    
    def _transform_header_to_field(self, content: str) -> Tuple[str, str]:
        """Transform ## Header to @field: header format."""
        # This is complex and context-dependent
        # Basic implementation for common headers
        
        header_map = {
            'Question Text': 'question_text',
            'Options': 'options',
            'Answer': 'answer',
            'Feedback': 'feedback',
            'Scoring': 'scoring',
            'Pairs': 'pairs',
            'Blanks': 'blanks',
        }
        
        original = content
        for header, field_name in header_map.items():
            pattern = f'^##\\s*{header}\\s*$'
            replacement = f'@field: {field_name}'
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.IGNORECASE)
        
        if content != original:
            return content, "Konverterade markdown headers till @field: format"
        return content, ""
    
    def _transform_add_end_fields(self, content: str) -> Tuple[str, str]:
        """Add missing @end_field markers."""
        # This is complex - need to track field nesting
        # Simple heuristic: add @end_field before next @field: or ## or # at same/higher level
        
        lines = content.split('\n')
        result = []
        in_field = False
        field_depth = 0
        
        for i, line in enumerate(lines):
            # Check if starting a new field
            if line.strip().startswith('@field:'):
                if in_field:
                    result.append('@end_field')
                result.append(line)
                in_field = True
                field_depth = 1
            elif line.strip().startswith('@@field:'):
                result.append(line)
                field_depth += 1
            elif line.strip() == '@end_field':
                result.append(line)
                field_depth -= 1
                if field_depth <= 0:
                    in_field = False
            elif line.strip() == '@@end_field':
                result.append(line)
                field_depth -= 1
            elif line.startswith('# ') and in_field:
                # New question starting - close any open fields
                result.append('@end_field')
                in_field = False
                result.append(line)
            else:
                result.append(line)
        
        # Close any remaining open field
        if in_field:
            result.append('@end_field')
        
        new_content = '\n'.join(result)
        if new_content != content:
            return new_content, "La till saknade @end_field"
        return content, ""

# Global transformer instance
transformer = Transformer()
```

---

## FILE 6: prompts.py

```python
"""
User interaction prompts for Step 1.
"""

from typing import Dict, List, Any, Optional

# Bloom taxonomy levels with descriptions
BLOOM_LEVELS = [
    ('Remember', 'Minnas fakta, definitioner, termer'),
    ('Understand', 'Förklara, sammanfatta, tolka'),
    ('Apply', 'Använda kunskap i ny situation'),
    ('Analyze', 'Bryta ner, jämföra, identifiera mönster'),
    ('Evaluate', 'Bedöma, kritisera, motivera'),
    ('Create', 'Skapa, designa, konstruera'),
]

DIFFICULTY_LEVELS = [
    ('Easy', 'Grundläggande - de flesta klarar'),
    ('Medium', 'Medel - kräver god förståelse'),
    ('Hard', 'Svår - kräver djup förståelse'),
]

PROMPTS = {
    'select_bloom': {
        'type': 'single_choice',
        'question': 'Vilken Bloom-nivå har denna fråga?',
        'options': BLOOM_LEVELS,
        'help': 'Välj den kognitiva nivå som bäst beskriver vad frågan testar.'
    },
    
    'select_difficulty': {
        'type': 'single_choice',
        'question': 'Vilken svårighetsgrad har denna fråga?',
        'options': DIFFICULTY_LEVELS,
        'help': 'Uppskatta hur svår frågan är för en typisk student.'
    },
    
    'confirm_identifier': {
        'type': 'confirm_or_edit',
        'question': 'Genererad identifier: {identifier}. Godkänn eller ändra:',
        'default': '{identifier}',
        'help': 'Identifier måste vara unik. Format: KURS_TYP_NUMMER'
    },
    
    'missing_labels': {
        'type': 'text_input',
        'question': 'Ange labels för frågan:',
        'placeholder': '#KURS #Ämne #Bloom #Difficulty',
        'help': 'Labels måste innehålla minst Bloom-nivå och svårighetsgrad.'
    },
    
    'suggest_feedback': {
        'type': 'confirm_suggestion',
        'question': 'Saknar {field}. Vill du att jag föreslår?',
        'options': [
            ('yes', 'Ja, föreslå'),
            ('manual', 'Nej, jag skriver själv'),
            ('skip', 'Hoppa över')
        ]
    },
    
    'ambiguous_type': {
        'type': 'single_choice',
        'question': 'Kan inte avgöra frågetyp. Vilken är det?',
        'options': [
            ('multiple_choice_single', 'Flerval (ett svar)'),
            ('multiple_response', 'Flerval (flera svar)'),
            ('text_entry', 'Fyll i lucka'),
            ('inline_choice', 'Dropdown'),
            ('match', 'Matchning'),
            ('text_area', 'Fritext/Essä'),
        ]
    },
    
    'batch_apply': {
        'type': 'batch_confirm',
        'question': 'Samma fix kan appliceras på {count} liknande frågor:',
        'preview_count': 3,  # Show first 3 as preview
        'options': [
            ('all', 'Applicera på alla {count}'),
            ('select', 'Låt mig välja'),
            ('skip', 'Bara denna fråga')
        ]
    },
    
    'image_missing': {
        'type': 'path_input',
        'question': 'Bildfil "{filename}" hittades inte. Var finns den?',
        'allow_skip': True,
        'skip_warning': 'Frågan exporteras utan bild.'
    },
    
    'confirm_changes': {
        'type': 'confirm',
        'question': 'Applicera dessa ändringar?',
        'show_diff': True
    }
}

def get_prompt(prompt_key: str, **kwargs) -> Dict[str, Any]:
    """
    Get a prompt configuration with interpolated values.
    
    Args:
        prompt_key: Key from PROMPTS dict
        **kwargs: Values to interpolate
        
    Returns:
        Prompt configuration dict
    """
    if prompt_key not in PROMPTS:
        raise ValueError(f"Unknown prompt: {prompt_key}")
    
    prompt = PROMPTS[prompt_key].copy()
    
    # Interpolate question text
    if 'question' in prompt:
        prompt['question'] = prompt['question'].format(**kwargs)
    
    # Interpolate options if present
    if 'options' in prompt and isinstance(prompt['options'], list):
        new_options = []
        for opt in prompt['options']:
            if isinstance(opt, tuple):
                new_options.append((opt[0].format(**kwargs), opt[1].format(**kwargs)))
            else:
                new_options.append(opt.format(**kwargs))
        prompt['options'] = new_options
    
    return prompt

def format_issue_summary(issues: List[Any]) -> str:
    """Format issues for display to user."""
    lines = []
    
    critical = [i for i in issues if i.severity.value == 'critical']
    warning = [i for i in issues if i.severity.value == 'warning']
    info = [i for i in issues if i.severity.value == 'info']
    
    if critical:
        lines.append(f"❌ **{len(critical)} kritiska problem** (måste fixas):")
        for issue in critical:
            auto = " [AUTO]" if issue.auto_fixable else ""
            lines.append(f"   - {issue.message}{auto}")
    
    if warning:
        lines.append(f"⚠️ **{len(warning)} varningar** (rekommenderas):")
        for issue in warning:
            auto = " [AUTO]" if issue.auto_fixable else ""
            lines.append(f"   - {issue.message}{auto}")
    
    if info:
        lines.append(f"ℹ️ **{len(info)} förslag:**")
        for issue in info:
            lines.append(f"   - {issue.message}")
    
    return '\n'.join(lines)
```

---

## FILE 7: step1_tools.py (MCP Tools)

```python
"""
MCP Tool definitions for Step 1: Guided Build.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import json

# Import step1 modules
from ..step1.session import Session
from ..step1.parser import parse_file, ParsedQuestion
from ..step1.detector import detect_format, FormatLevel, get_format_description
from ..step1.analyzer import analyze_question, Issue
from ..step1.transformer import transformer
from ..step1.prompts import get_prompt, format_issue_summary

# Global session state (in production, use proper state management)
_current_session: Optional[Session] = None

# ════════════════════════════════════════════════════════════════════
# MCP TOOLS
# ════════════════════════════════════════════════════════════════════

def step1_start(
    source_file: str,
    output_folder: str,
    project_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Start a new Step 1 session.
    
    Args:
        source_file: Path to markdown file with questions
        output_folder: Directory for output files
        project_name: Optional project name
        
    Returns:
        Session info and initial analysis
    """
    global _current_session
    
    # Validate source file
    source_path = Path(source_file)
    if not source_path.exists():
        return {"error": f"File not found: {source_file}"}
    
    if not source_path.suffix.lower() == '.md':
        return {"error": f"Not a markdown file: {source_file}"}
    
    # Create output folder
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Read file
    content = source_path.read_text(encoding='utf-8')
    
    # Detect format
    format_level = detect_format(content)
    
    if format_level == FormatLevel.RAW:
        return {
            "error": "Filen är för ostrukturerad för Step 1",
            "recommendation": "Använd qf-scaffolding först",
            "format": format_level.value,
            "format_description": get_format_description(format_level)
        }
    
    if format_level == FormatLevel.VALID_V65:
        return {
            "message": "Filen är redan i valid v6.5 format",
            "recommendation": "Gå direkt till Step 2 (validate)",
            "format": format_level.value
        }
    
    # Parse questions
    questions = parse_file(content)
    
    if not questions:
        return {"error": "Inga frågor hittades i filen"}
    
    # Create session
    _current_session = Session.create_new(source_file, output_folder)
    _current_session.total_questions = len(questions)
    _current_session.detected_format = format_level.value
    
    # Initialize question status
    from ..step1.session import QuestionStatus
    _current_session.questions = [
        QuestionStatus(question_id=q.question_id, status='pending')
        for q in questions
    ]
    
    # Copy source to working file
    working_path = Path(_current_session.working_file)
    working_path.write_text(content, encoding='utf-8')
    
    # Save session
    session_file = output_path / f"session_{_current_session.session_id}.json"
    _current_session.save(session_file)
    
    # Analyze first question
    first_question = questions[0]
    issues = analyze_question(first_question.raw_content, first_question.detected_type)
    
    return {
        "session_id": _current_session.session_id,
        "source_file": source_file,
        "working_file": _current_session.working_file,
        "format": format_level.value,
        "format_description": get_format_description(format_level),
        "total_questions": len(questions),
        "first_question": {
            "id": first_question.question_id,
            "title": first_question.title,
            "type": first_question.detected_type,
            "line_start": first_question.line_start,
            "issues_count": len(issues),
            "issues_summary": format_issue_summary(issues)
        }
    }

def step1_status() -> Dict[str, Any]:
    """
    Get current session status.
    
    Returns:
        Session progress and statistics
    """
    if not _current_session:
        return {"error": "No active session. Use step1_start first."}
    
    progress = _current_session.get_progress()
    current = _current_session.get_current_question()
    
    return {
        "session_id": _current_session.session_id,
        "progress": progress,
        "current_question": current.question_id if current else None,
        "format": _current_session.detected_format,
        "changes_made": len(_current_session.changes)
    }

def step1_analyze(question_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a question and return issues.
    
    Args:
        question_id: Question to analyze (default: current)
        
    Returns:
        List of issues with suggested fixes
    """
    if not _current_session:
        return {"error": "No active session"}
    
    # Read working file
    working_path = Path(_current_session.working_file)
    content = working_path.read_text(encoding='utf-8')
    
    # Parse and find question
    questions = parse_file(content)
    
    target_id = question_id or _current_session.questions[_current_session.current_index].question_id
    question = next((q for q in questions if q.question_id == target_id), None)
    
    if not question:
        return {"error": f"Question not found: {target_id}"}
    
    # Analyze
    issues = analyze_question(question.raw_content, question.detected_type)
    
    # Separate auto-fixable and manual
    auto_fixable = [i for i in issues if i.auto_fixable]
    needs_input = [i for i in issues if not i.auto_fixable and i.prompt_key]
    other = [i for i in issues if not i.auto_fixable and not i.prompt_key]
    
    return {
        "question_id": target_id,
        "question_type": question.detected_type,
        "total_issues": len(issues),
        "auto_fixable": len(auto_fixable),
        "needs_input": len(needs_input),
        "issues_summary": format_issue_summary(issues),
        "issues": [
            {
                "severity": i.severity.value,
                "category": i.category,
                "field": i.field,
                "message": i.message,
                "auto_fixable": i.auto_fixable,
                "prompt_key": i.prompt_key,
                "transform_id": i.transform_id
            }
            for i in issues
        ]
    }

def step1_fix_auto(question_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Apply all auto-fixable transforms to a question.
    
    Args:
        question_id: Question to fix (default: current)
        
    Returns:
        List of changes made
    """
    if not _current_session:
        return {"error": "No active session"}
    
    # Read working file
    working_path = Path(_current_session.working_file)
    content = working_path.read_text(encoding='utf-8')
    
    # Parse and find question
    questions = parse_file(content)
    
    target_id = question_id or _current_session.questions[_current_session.current_index].question_id
    question = next((q for q in questions if q.question_id == target_id), None)
    
    if not question:
        return {"error": f"Question not found: {target_id}"}
    
    # Apply transforms
    new_content, changes = transformer.apply_all_auto(question.raw_content)
    
    if not changes:
        return {
            "question_id": target_id,
            "changes": [],
            "message": "Inga automatiska fixar att applicera"
        }
    
    # Update file
    full_content = content.replace(question.raw_content, new_content)
    working_path.write_text(full_content, encoding='utf-8')
    
    # Log changes
    for change_desc in changes:
        _current_session.add_change(
            question_id=target_id,
            field='auto',
            old_value=None,
            new_value=change_desc,
            change_type='auto'
        )
    
    return {
        "question_id": target_id,
        "changes": changes,
        "message": f"Applicerade {len(changes)} automatiska fixar"
    }

def step1_fix_manual(
    question_id: str,
    field: str,
    value: str
) -> Dict[str, Any]:
    """
    Apply a manual fix from user input.
    
    Args:
        question_id: Question to fix
        field: Field to update
        value: New value
        
    Returns:
        Confirmation of change
    """
    if not _current_session:
        return {"error": "No active session"}
    
    # Implementation depends on field type
    # This is a simplified version
    
    working_path = Path(_current_session.working_file)
    content = working_path.read_text(encoding='utf-8')
    
    # Find question and update field
    # ... implementation ...
    
    _current_session.add_change(
        question_id=question_id,
        field=field,
        old_value=None,
        new_value=value,
        change_type='user_input'
    )
    
    return {
        "question_id": question_id,
        "field": field,
        "new_value": value,
        "message": f"Uppdaterade {field}"
    }

def step1_next(direction: str = "forward") -> Dict[str, Any]:
    """
    Move to next/previous question.
    
    Args:
        direction: "forward", "back", or question_id
        
    Returns:
        New current question info
    """
    if not _current_session:
        return {"error": "No active session"}
    
    if direction == "forward":
        if _current_session.current_index < len(_current_session.questions) - 1:
            _current_session.current_index += 1
    elif direction == "back":
        if _current_session.current_index > 0:
            _current_session.current_index -= 1
    else:
        # Assume it's a question_id
        for i, q in enumerate(_current_session.questions):
            if q.question_id == direction:
                _current_session.current_index = i
                break
    
    current = _current_session.get_current_question()
    progress = _current_session.get_progress()
    
    return {
        "current_question": current.question_id,
        "position": f"{progress['current']} av {progress['total']}",
        "progress": progress
    }

def step1_skip(reason: Optional[str] = None) -> Dict[str, Any]:
    """
    Skip current question.
    
    Args:
        reason: Optional reason for skipping
        
    Returns:
        Confirmation and next question
    """
    if not _current_session:
        return {"error": "No active session"}
    
    current = _current_session.get_current_question()
    current.status = 'skipped'
    
    if reason:
        _current_session.add_change(
            question_id=current.question_id,
            field='skip_reason',
            old_value=None,
            new_value=reason,
            change_type='skip'
        )
    
    # Move to next
    return step1_next("forward")

def step1_finish() -> Dict[str, Any]:
    """
    Finish Step 1 and generate report.
    
    Returns:
        Summary report
    """
    if not _current_session:
        return {"error": "No active session"}
    
    progress = _current_session.get_progress()
    
    # Count issues by type
    completed = [q for q in _current_session.questions if q.status == 'completed']
    skipped = [q for q in _current_session.questions if q.status == 'skipped']
    warnings = [q for q in _current_session.questions if q.status == 'has_warnings']
    
    # Save final session state
    output_path = Path(_current_session.output_folder)
    session_file = output_path / f"session_{_current_session.session_id}_final.json"
    _current_session.save(session_file)
    
    return {
        "session_id": _current_session.session_id,
        "working_file": _current_session.working_file,
        "summary": {
            "total_questions": _current_session.total_questions,
            "completed": len(completed),
            "skipped": len(skipped),
            "with_warnings": len(warnings),
            "total_changes": len(_current_session.changes)
        },
        "skipped_questions": [q.question_id for q in skipped],
        "warning_questions": [q.question_id for q in warnings],
        "ready_for_step2": len(skipped) == 0 and len(warnings) == 0,
        "next_action": "Kör step2_validate på working_file" if len(skipped) == 0 else "Fixa skippade frågor först"
    }

# ════════════════════════════════════════════════════════════════════
# TOOL REGISTRATION (for MCP)
# ════════════════════════════════════════════════════════════════════

TOOLS = [
    {
        "name": "step1_start",
        "description": "Starta Step 1 Guided Build session. Analyserar fil och förbereder för fråga-för-fråga genomgång.",
        "parameters": {
            "source_file": {"type": "string", "description": "Sökväg till markdown-fil"},
            "output_folder": {"type": "string", "description": "Mapp för output"},
            "project_name": {"type": "string", "description": "Valfritt projektnamn"}
        }
    },
    {
        "name": "step1_status",
        "description": "Visa status för aktiv session.",
        "parameters": {}
    },
    {
        "name": "step1_analyze",
        "description": "Analysera en fråga och visa problem som behöver fixas.",
        "parameters": {
            "question_id": {"type": "string", "description": "Fråge-ID (default: aktuell)"}
        }
    },
    {
        "name": "step1_fix_auto",
        "description": "Applicera alla automatiska fixar på en fråga.",
        "parameters": {
            "question_id": {"type": "string", "description": "Fråge-ID (default: aktuell)"}
        }
    },
    {
        "name": "step1_fix_manual",
        "description": "Applicera manuell fix från användarinput.",
        "parameters": {
            "question_id": {"type": "string", "description": "Fråge-ID"},
            "field": {"type": "string", "description": "Fält att uppdatera"},
            "value": {"type": "string", "description": "Nytt värde"}
        }
    },
    {
        "name": "step1_next",
        "description": "Gå till nästa/föregående fråga.",
        "parameters": {
            "direction": {"type": "string", "description": "'forward', 'back', eller fråge-ID"}
        }
    },
    {
        "name": "step1_skip",
        "description": "Hoppa över aktuell fråga.",
        "parameters": {
            "reason": {"type": "string", "description": "Anledning (valfritt)"}
        }
    },
    {
        "name": "step1_finish",
        "description": "Avsluta Step 1 och generera rapport.",
        "parameters": {}
    }
]
```

---

## TESTING

### Test File: EXAMPLE_COURSE_Fys_v63.md (verklig fil)

```bash
# Kör test
cd /packages/qf-pipeline
python -m pytest tests/test_step1.py -v

# Eller manuellt
python -c "
from qf_pipeline.step1.detector import detect_format
from qf_pipeline.step1.parser import parse_file
from pathlib import Path

content = Path('test_data/EXAMPLE_COURSE_Fys_v63.md').read_text()
print(f'Format: {detect_format(content)}')
questions = parse_file(content)
print(f'Questions: {len(questions)}')
for q in questions[:3]:
    print(f'  {q.question_id}: {q.detected_type}')
"
```

---

## KNOWN LIMITATIONS

1. **Batch apply** - Förenklad implementation, behöver mer testning
2. **Nested fields** - @@field: detektion är komplex
3. **Semi-structured** - ## Header → @field: konvertering behöver mer arbete
4. **Image handling** - Inte implementerat i denna version
5. **Feedback generation** - Kräver AI, inte inkluderat

---

## NEXT STEPS FOR CODE

1. ✅ Skapa filstruktur
2. ⏳ Implementera session.py
3. ⏳ Implementera parser.py
4. ⏳ Implementera detector.py
5. ⏳ Implementera analyzer.py
6. ⏳ Implementera transformer.py
7. ⏳ Implementera prompts.py
8. ⏳ Implementera step1_tools.py
9. ⏳ Skriva tester
10. ⏳ Testa på verklig fil

---

*Step 1 Implementation Instructions v1.0 | 2026-01-07*
