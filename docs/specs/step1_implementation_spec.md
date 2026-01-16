# STEP 1 IMPLEMENTATION SPEC (Förenklad)

**Version:** 2.0  
**Datum:** 2026-01-07  
**Approach:** XML templates + generell fix-logik

---

## ARKITEKTUR

```
qf-pipeline/src/qf_pipeline/
├── step1/
│   ├── __init__.py
│   ├── session.py          # Session management
│   ├── parser.py           # Parse markdown till frågor
│   ├── detector.py         # Identifiera format/typ
│   ├── analyzer.py         # Jämför mot krav (använder XML templates)
│   ├── fixer.py            # Applicera fixar
│   └── transforms.py       # GENERELLA syntax-transformationer
│
├── shared/
│   ├── field_map.py        # Mappa XML placeholder → markdown field
│   └── user_prompts.py     # Frågor att ställa användaren
│
└── tools/
    └── step1_tools.py      # MCP tool definitions
```

---

## FIL 1: transforms.py (Generella fixar)

```python
"""
Generella syntax-transformationer.
Gäller ALLA frågetyper.
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
    """Konvertera 1. 2. 3. till A. B. C."""
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
    """Konvertera a. b. c. till A. B. C."""
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
    """Lägg till @end_field där det saknas."""
    # Komplex logik - behöver parse field-struktur
    # TODO: Implementera
    pass

def convert_nested_fields(text: str) -> str:
    """Konvertera @field: inne i @field: till @@field:"""
    # TODO: Implementera
    pass

# ════════════════════════════════════════════════════════════════════
# APPLY ALL TRANSFORMS
# ════════════════════════════════════════════════════════════════════

def apply_regex_transforms(text: str, transforms: List[Tuple[str, str]]) -> str:
    """Applicera lista av regex-transformationer."""
    for pattern, replacement in transforms:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
    return text

def apply_all_transforms(text: str) -> Tuple[str, List[str]]:
    """
    Applicera alla generella transformationer.
    
    Returns:
        (transformed_text, list_of_changes_made)
    """
    changes = []
    original = text
    
    # Metadata
    text = apply_regex_transforms(text, METADATA_TRANSFORMS)
    if text != original:
        changes.append("Konverterade metadata-syntax (@key: → ^key)")
        original = text
    
    # In-field metadata
    text = apply_regex_transforms(text, INFIELD_TRANSFORMS)
    if text != original:
        changes.append("Konverterade in-field metadata (**Key:** → ^Key)")
        original = text
    
    # Placeholders
    text = apply_regex_transforms(text, PLACEHOLDER_TRANSFORMS)
    if text != original:
        changes.append("Konverterade placeholder-syntax ({{BLANK-1}} → {{blank_1}})")
        original = text
    
    # Options (behöver kontext-medveten transform)
    # Appliceras bara inom @field: options
    
    return text, changes
```

---

## FIL 2: field_map.py (XML placeholder → Markdown field)

```python
"""
Mappa XML template placeholders till markdown fields.
Härledd från qti-core/templates/xml/*.xml
"""

# Genererad från XML templates
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

# Type-specifika fields (härledd från XML templates)
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
    # ... resten härledda från XML templates
}

# Required metadata (samma för ALLA typer)
REQUIRED_METADATA = [
    '^question',
    '^type', 
    '^identifier',
    '^points',
    '^labels',  # måste innehålla Bloom + Difficulty
]

# Feedback subfields per kategori
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

## FIL 3: user_prompts.py (Vad fråga användaren)

```python
"""
Prompts för interaktiv dialog med användaren.
"""

PROMPTS = {
    'missing_bloom': {
        'question': "Vilken Bloom-nivå har frågan?",
        'options': ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create'],
        'help': "Remember=faktakunskap, Understand=förklara, Apply=tillämpa..."
    },
    
    'missing_difficulty': {
        'question': "Vilken svårighetsgrad har frågan?",
        'options': ['Easy', 'Medium', 'Hard'],
        'help': "Easy=grundläggande, Medium=kräver förståelse, Hard=komplex"
    },
    
    'missing_identifier': {
        'question': "Generera identifier automatiskt?",
        'auto_value': "{COURSE}_{TYPE}_{QNUM}",
        'example': "BIOG_MC_Q001"
    },
    
    'missing_feedback': {
        'question': "Saknar feedback. Vill du att jag föreslår?",
        'options': ['Ja, föreslå', 'Nej, jag skriver själv', 'Hoppa över'],
    },
    
    'ambiguous_type': {
        'question': "Kan inte avgöra frågetyp. Vilket är det?",
        'options': ['multiple_choice_single', 'multiple_response', 'text_entry', 'inline_choice', 'match', 'Annan'],
    },
    
    'image_missing': {
        'question': "Bildfil '{filename}' hittades inte. Var finns den?",
        'allow_path_input': True,
        'allow_skip': True,
    },
    
    'batch_apply': {
        'question': "Samma fix kan appliceras på {count} liknande frågor. Applicera på alla?",
        'options': ['Ja, alla', 'Låt mig välja', 'Nej, bara denna'],
        'show_preview': True,
    }
}

def get_prompt(prompt_id: str, **kwargs) -> dict:
    """Hämta prompt med interpolerade värden."""
    prompt = PROMPTS[prompt_id].copy()
    prompt['question'] = prompt['question'].format(**kwargs)
    return prompt
```

---

## FIL 4: analyzer.py (Hitta problem)

```python
"""
Analysera fråga och hitta vad som saknas/är fel.
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
        self.prompt_id = prompt_id  # för user_prompts

def analyze_question(question_text: str, question_type: str = None) -> List[Issue]:
    """
    Analysera en fråga och returnera lista av issues.
    """
    issues = []
    
    # 1. Kontrollera metadata
    for meta in REQUIRED_METADATA:
        pattern = f"^\\{meta}\\s+" if meta.startswith('^') else f"^{meta}\\s+"
        if not re.search(pattern, question_text, re.MULTILINE):
            # Kolla om gammal syntax finns
            old_pattern = meta.replace('^', '@') + ':'
            if re.search(old_pattern, question_text):
                issues.append(Issue(
                    severity='critical',
                    category='old_syntax',
                    field=meta,
                    message=f"Gammal syntax '{old_pattern}' ska vara '{meta}'",
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
                    message=f"Saknar {meta}",
                    auto_fixable=(meta == '^identifier'),
                    prompt_id=prompt_id
                ))
    
    # 2. Kontrollera Bloom + Difficulty i labels
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
                message="Labels saknar Bloom-nivå",
                prompt_id='missing_bloom'
            ))
        if not has_diff:
            issues.append(Issue(
                severity='critical',
                category='incomplete_labels', 
                field='^labels',
                message="Labels saknar svårighetsgrad",
                prompt_id='missing_difficulty'
            ))
    
    # 3. Kontrollera type-specifika fields
    if question_type and question_type in TYPE_REQUIRED_FIELDS:
        for field in TYPE_REQUIRED_FIELDS[question_type]:
            if not re.search(f"@field:\\s*{field}", question_text):
                issues.append(Issue(
                    severity='critical',
                    category='missing_field',
                    field=field,
                    message=f"Saknar @field: {field}"
                ))
    
    # 4. Kontrollera options-format (numrerade istället för bokstäver)
    if re.search(r'@field:\s*options', question_text):
        options_section = extract_field(question_text, 'options')
        if options_section and re.search(r'^\d+[.)]\s', options_section, re.MULTILINE):
            issues.append(Issue(
                severity='critical',
                category='wrong_format',
                field='options',
                message="Alternativ numrerade (1,2,3) istället för bokstäver (A,B,C)",
                auto_fixable=True
            ))
    
    # 5. Kontrollera @end_field
    field_starts = len(re.findall(r'@field:', question_text))
    field_ends = len(re.findall(r'@end_field', question_text))
    if field_starts > field_ends:
        issues.append(Issue(
            severity='critical',
            category='structure',
            field='@end_field',
            message=f"Saknar {field_starts - field_ends} st @end_field",
            auto_fixable=True
        ))
    
    return issues

def extract_field(text: str, field_name: str) -> str:
    """Extrahera innehåll av ett field."""
    pattern = f"@field:\\s*{field_name}\\s*\\n(.*?)(?=@end_field|@field:|$)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1) if match else None
```

---

## SAMMANFATTNING: Mindre kod, samma funktionalitet

| Tidigare (TYPE REQUIREMENTS) | Nu (Förenklad) |
|------------------------------|----------------|
| 5 stora YAML-filer (500+ rader var) | 4 Python-filer (~150 rader var) |
| Duplicerar info från XML | Använder XML som källa |
| Svårt att underhålla | En plats för varje sak |
| Complete examples i YAML | Examples i XML templates |

**Total kod: ~600 rader istället för ~3000 rader**

---

## NÄSTA STEG

1. ✅ Design klar (detta dokument)
2. ⏳ Implementera transforms.py
3. ⏳ Implementera analyzer.py  
4. ⏳ Implementera MCP tools
5. ⏳ Testa på BIOG001X_Fys_v63.md

---

*Step 1 Implementation Spec v2.0 | 2026-01-07*
