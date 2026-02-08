# STEP 1 IMPLEMENTATION SPEC (Simplified)

**Version:** 2.0  
**Date:** 2026-01-07  
**Approach:** XML templates + general fix logic

---

## ARCHITECTURE

```
qf-pipeline/src/qf_pipeline/
├── step1/
│   ├── __init__.py
│   ├── session.py          # Session management
│   ├── parser.py           # Parse markdown to questions
│   ├── detector.py         # Identify format/type
│   ├── analyzer.py         # Compare against requirements (uses XML templates)
│   ├── fixer.py            # Apply fixes
│   └── transforms.py       # GENERAL syntax transformations
│
├── shared/
│   ├── field_map.py        # Map XML placeholder → markdown field
│   └── user_prompts.py     # Questions to ask the user
│
└── tools/
    └── step1_tools.py      # MCP tool definitions
```

---

## FILE 1: transforms.py (General fixes)

```python
"""
General syntax transformations.
Applies to ALL question types.
"""

import re
from typing import Tuple, List, Callable

# ════════════════════════════════════════════════════════════════════
# METADATA SYNTAX (v6.3 → v6.5)
# ════════════════════════════════════════════════════════════════════

METADATA_TRANSFORMS = [
    # @key: value → ^key value
    (r'^@question:\s*(.+)$', r'^question \1'),
    (r'^@type:\s*(.+)$', r'^type \1'),
    (r'^@identifier:\s*(.+)$', r'^identifier \1'),
    (r'^@title:\s*(.+)$', r'^title \1'),
    (r'^@points:\s*(.+)$', r'^points \1'),
    (r'^@tags:\s*(.+)$', r'^labels \1'),
    (r'^@labels:\s*(.+)$', r'^labels \1'),
]

# ════════════════════════════════════════════════════════════════════
# IN-FIELD METADATA (Bold → Caret)
# ════════════════════════════════════════════════════════════════════

INFIELD_TRANSFORMS = [
    (r'\*\*Correct Answers?:\*\*', '^Correct_Answers'),
    (r'\*\*Case Sensitive:\*\*\s*(.+)', r'^Case_Sensitive \1'),
    (r'\*\*Type:\*\*\s*(.+)', r'^Type \1'),
    (r'\*\*Points:\*\*\s*(.+)', r'^Points \1'),
    (r'\*\*Options:\*\*', '^Options'),
    (r'\*\*Correct Answer:\*\*\s*(.+)', r'^Correct \1'),
    (r'\*\*Correct:\*\*\s*(.+)', r'^Correct \1'),
]

# ════════════════════════════════════════════════════════════════════
# PLACEHOLDER SYNTAX
# ════════════════════════════════════════════════════════════════════

PLACEHOLDER_TRANSFORMS = [
    # {{BLANK-N}} → {{blank_N}}
    (r'\{\{BLANK-(\d+)\}\}', r'{{blank_\1}}'),
    (r'\{\{DROPDOWN-(\d+)\}\}', r'{{dropdown_\1}}'),
    (r'\{\{BLANK(\d+)\}\}', r'{{blank_\1}}'),
    (r'\{\{DROPDOWN(\d+)\}\}', r'{{dropdown_\1}}'),
]

# ════════════════════════════════════════════════════════════════════
# OPTIONS FORMAT
# ════════════════════════════════════════════════════════════════════

def transform_numbered_options(text: str) -> str:
    """Convert 1. 2. 3. to A. B. C."""
    lines = text.split('\n')
    result = []
    number_to_letter = {
        '1': 'A', '2': 'B', '3': 'C', '4': 'D', 
        '5': 'E', '6': 'F', '7': 'G', '8': 'H'
    }
    for line in lines:
        # Match "1." or "1)" at start of line
        match = re.match(r'^(\d+)[.)\s]\s*(.+)$', line.strip())
        if match:
            num, content = match.groups()
            if num in number_to_letter:
                line = f"{number_to_letter[num]}. {content}"
        result.append(line)
    return '\n'.join(result)

def transform_lowercase_options(text: str) -> str:
    """Convert a. b. c. to A. B. C."""
    lines = text.split('\n')
    result = []
    for line in lines:
        match = re.match(r'^([a-f])[.)\s]\s*(.+)$', line.strip())
        if match:
            letter, content = match.groups()
            line = f"{letter.upper()}. {content}"
        result.append(line)
    return '\n'.join(result)

# ════════════════════════════════════════════════════════════════════
# FIELD STRUCTURE
# ════════════════════════════════════════════════════════════════════

def ensure_end_fields(text: str) -> str:
    """Add @end_field where missing."""
    # Complex logic - needs to parse field structure
    # TODO: Implement
    pass

def convert_nested_fields(text: str) -> str:
    """Convert @field: inside @field: to @@field:"""
    # TODO: Implement
    pass

# ════════════════════════════════════════════════════════════════════
# APPLY ALL TRANSFORMS
# ════════════════════════════════════════════════════════════════════

def apply_regex_transforms(text: str, transforms: List[Tuple[str, str]]) -> str:
    """Apply list of regex transformations."""
    for pattern, replacement in transforms:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
    return text

def apply_all_transforms(text: str) -> Tuple[str, List[str]]:
    """
    Apply all general transformations.
    
    Returns:
        (transformed_text, list_of_changes_made)
    """
    changes = []
    original = text
    
    # Metadata
    text = apply_regex_transforms(text, METADATA_TRANSFORMS)
    if text != original:
        changes.append("Converted metadata syntax (@key: → ^key)")
        original = text
    
    # In-field metadata
    text = apply_regex_transforms(text, INFIELD_TRANSFORMS)
    if text != original:
        changes.append("Converted in-field metadata (**Key:** → ^Key)")
        original = text
    
    # Placeholders
    text = apply_regex_transforms(text, PLACEHOLDER_TRANSFORMS)
    if text != original:
        changes.append("Converted placeholder syntax ({{BLANK-1}} → {{blank_1}})")
        original = text
    
    # Options (needs context-aware transform)
    # Applied only within @field: options
    
    return text, changes
```

---

## FILE 2: field_map.py (XML placeholder → Markdown field)

```python
"""
Map XML template placeholders to markdown fields.
Derived from qti-core/templates/xml/*.xml
"""

# Generated from XML templates
PLACEHOLDER_TO_FIELD = {
    # Metadata
    '{{IDENTIFIER}}': '^identifier',
    '{{TITLE}}': '^title',
    '{{MAX_SCORE}}': '^points',
    '{{LANGUAGE}}': '^language',
    
    # Content
    '{{QUESTION_TEXT}}': '@field: question_text',
    '{{CHOICES}}': '@field: options',
    '{{CORRECT_CHOICE_ID}}': '@field: answer',
    '{{SHUFFLE}}': '^shuffle',
    
    # Feedback
    '{{FEEDBACK_CORRECT}}': '@@field: correct_feedback',
    '{{FEEDBACK_INCORRECT}}': '@@field: incorrect_feedback',
    '{{FEEDBACK_UNANSWERED}}': '@@field: unanswered_feedback',
    '{{FEEDBACK_PARTIALLY_CORRECT}}': '@@field: partial_feedback',
}

# Type-specific fields (derived from XML templates)
TYPE_REQUIRED_FIELDS = {
    'multiple_choice_single': [
        'question_text', 'options', 'answer', 'feedback'
    ],
    'multiple_response': [
        'question_text', 'options', 'answer', 'scoring', 'feedback'
    ],
    'text_entry': [
        'question_text', 'blanks', 'feedback'
    ],
    'inline_choice': [
        'question_text', 'dropdown_*', 'feedback'  # * = 1, 2, 3...
    ],
    'match': [
        'question_text', 'pairs', 'feedback'
    ],
    'text_area': [
        'question_text', 'scoring_rubric', 'feedback'
    ],
    # ... rest derived from XML templates
}

# Required metadata (same for ALL types)
REQUIRED_METADATA = [
    '^question',
    '^type', 
    '^identifier',
    '^points',
    '^labels',  # must contain Bloom + Difficulty
]

# Feedback subfields per category
FEEDBACK_SUBFIELDS = {
    'auto_graded': [
        'general_feedback',
        'correct_feedback', 
        'incorrect_feedback',
        'unanswered_feedback'
    ],
    'partial_credit': [
        'general_feedback',
        'correct_feedback',
        'incorrect_feedback', 
        'partial_feedback',
        'unanswered_feedback'
    ],
    'manual_graded': [
        'general_feedback',
        'answered_feedback',
        'unanswered_feedback'
    ]
}
```

---

## FILE 3: user_prompts.py (What to ask the user)

```python
"""
Prompts for interactive dialogue with the user.
"""

PROMPTS = {
    'missing_bloom': {
        'question': "Which Bloom level does the question have?",
        'options': ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create'],
        'help': "Remember=factual knowledge, Understand=explain, Apply=apply..."
    },
    
    'missing_difficulty': {
        'question': "Which difficulty level does the question have?",
        'options': ['Easy', 'Medium', 'Hard'],
        'help': "Easy=basic, Medium=requires understanding, Hard=complex"
    },
    
    'missing_identifier': {
        'question': "Generate identifier automatically?",
        'auto_value': "{COURSE}_{TYPE}_{QNUM}",
        'example': "BIOG_MC_Q001"
    },
    
    'missing_feedback': {
        'question': "Missing feedback. Would you like me to suggest?",
        'options': ['Yes, suggest', 'No, I will write myself', 'Skip'],
    },
    
    'ambiguous_type': {
        'question': "Cannot determine question type. Which is it?",
        'options': ['multiple_choice_single', 'multiple_response', 'text_entry', 'inline_choice', 'match', 'Other'],
    },
    
    'image_missing': {
        'question': "Image file '{filename}' not found. Where is it?",
        'allow_path_input': True,
        'allow_skip': True,
    },
    
    'batch_apply': {
        'question': "Same fix can be applied to {count} similar questions. Apply to all?",
        'options': ['Yes, all', 'Let me choose', 'No, this one only'],
        'show_preview': True,
    }
}

def get_prompt(prompt_id: str, **kwargs) -> dict:
    """Get prompt with interpolated values."""
    prompt = PROMPTS[prompt_id].copy()
    prompt['question'] = prompt['question'].format(**kwargs)
    return prompt
```

---

## FILE 4: analyzer.py (Find problems)

```python
"""
Analyse question and find what is missing/wrong.
"""

from .field_map import REQUIRED_METADATA, TYPE_REQUIRED_FIELDS, FEEDBACK_SUBFIELDS
from .transforms import METADATA_TRANSFORMS, INFIELD_TRANSFORMS
import re

class Issue:
    def __init__(self, severity, category, field, message, 
                 current=None, suggestion=None, auto_fixable=False, prompt_id=None):
        self.severity = severity  # 'critical', 'warning', 'info'
        self.category = category
        self.field = field
        self.message = message
        self.current = current
        self.suggestion = suggestion
        self.auto_fixable = auto_fixable
        self.prompt_id = prompt_id  # for user_prompts

def analyse_question(question_text: str, question_type: str = None) -> List[Issue]:
    """
    Analyse a question and return list of issues.
    """
    issues = []
    
    # 1. Check metadata
    for meta in REQUIRED_METADATA:
        pattern = f"^\\{meta}\\s+" if meta.startswith('^') else f"^{meta}\\s+"
        if not re.search(pattern, question_text, re.MULTILINE):
            # Check if old syntax exists
            old_pattern = meta.replace('^', '@') + ':'
            if re.search(old_pattern, question_text):
                issues.append(Issue(
                    severity='critical',
                    category='old_syntax',
                    field=meta,
                    message=f"Old syntax '{old_pattern}' should be '{meta}'",
                    auto_fixable=True
                ))
            else:
                prompt_id = None
                if meta == '^labels':
                    prompt_id = 'missing_bloom'  # trigger user prompt
                elif meta == '^identifier':
                    prompt_id = 'missing_identifier'
                    
                issues.append(Issue(
                    severity='critical',
                    category='missing_metadata',
                    field=meta,
                    message=f"Missing {meta}",
                    auto_fixable=(meta == '^identifier'),
                    prompt_id=prompt_id
                ))
    
    # 2. Check Bloom + Difficulty in labels
    labels_match = re.search(r'\^labels\s+(.+)$', question_text, re.MULTILINE)
    if labels_match:
        labels = labels_match.group(1)
        bloom_levels = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
        difficulties = ['Easy', 'Medium', 'Hard']
        
        has_bloom = any(b in labels for b in bloom_levels)
        has_diff = any(d in labels for d in difficulties)
        
        if not has_bloom:
            issues.append(Issue(
                severity='critical',
                category='incomplete_labels',
                field='^labels',
                message="Labels missing Bloom level",
                prompt_id='missing_bloom'
            ))
        if not has_diff:
            issues.append(Issue(
                severity='critical',
                category='incomplete_labels', 
                field='^labels',
                message="Labels missing difficulty",
                prompt_id='missing_difficulty'
            ))
    
    # 3. Check type-specific fields
    if question_type and question_type in TYPE_REQUIRED_FIELDS:
        for field in TYPE_REQUIRED_FIELDS[question_type]:
            if not re.search(f"@field:\\s*{field}", question_text):
                issues.append(Issue(
                    severity='critical',
                    category='missing_field',
                    field=field,
                    message=f"Missing @field: {field}"
                ))
    
    # 4. Check options format (numbered instead of letters)
    if re.search(r'@field:\s*options', question_text):
        options_section = extract_field(question_text, 'options')
        if options_section and re.search(r'^\d+[.)]\s', options_section, re.MULTILINE):
            issues.append(Issue(
                severity='critical',
                category='wrong_format',
                field='options',
                message="Options numbered (1,2,3) instead of letters (A,B,C)",
                auto_fixable=True
            ))
    
    # 5. Check @end_field
    field_starts = len(re.findall(r'@field:', question_text))
    field_ends = len(re.findall(r'@end_field', question_text))
    if field_starts > field_ends:
        issues.append(Issue(
            severity='critical',
            category='structure',
            field='@end_field',
            message=f"Missing {field_starts - field_ends} @end_field marker(s)",
            auto_fixable=True
        ))
    
    return issues

def extract_field(text: str, field_name: str) -> str:
    """Extract content of a field."""
    pattern = f"@field:\\s*{field_name}\\s*\\n(.*?)(?=@end_field|@field:|$)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1) if match else None
```

---

## SUMMARY: Less code, same functionality

| Previously (TYPE REQUIREMENTS) | Now (Simplified) |
|--------------------------------|------------------|
| 5 large YAML files (500+ lines each) | 4 Python files (~150 lines each) |
| Duplicates info from XML | Uses XML as source |
| Difficult to maintain | One place for each thing |
| Complete examples in YAML | Examples in XML templates |

**Total code: ~600 lines instead of ~3000 lines**

---

## NEXT STEPS

1. ✅ Design complete (this document)
2. ⏳ Implement transforms.py
3. ⏳ Implement analyzer.py  
4. ⏳ Implement MCP tools
5. ⏳ Test on EXAMPLE_COURSE_Fys_v63.md

---

*Step 1 Implementation Spec v2.0 | 2026-01-07*
