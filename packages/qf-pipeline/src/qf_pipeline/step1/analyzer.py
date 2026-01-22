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
# Patterns accept both "^field value" and "^field: value" formats
# Also accepts ^labels as alias for ^tags (both are valid)
REQUIRED_METADATA = [
    ('^question', r'^\^question:?\s+Q\d{3}', 'Fråge-ID (Q001, Q002, etc.)'),
    ('^type', r'\^type:?\s+\w+', 'Frågetyp'),
    ('^identifier', r'\^identifier:?\s+\w+', 'Unik identifierare'),
    ('^points', r'\^points:?\s+\d+', 'Poäng'),
    ('^tags', r'\^(tags|labels):?\s+.+', 'Etiketter med Bloom och Difficulty'),
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

# Type name aliases that need normalization
TYPE_NAME_ALIASES = {
    'multiple_choice': 'multiple_choice_single',
    'mc': 'multiple_choice_single',
    'mcq': 'multiple_choice_single',
    'mr': 'multiple_response',
    'tf': 'true_false',
}

# Valid type names (QTI-exportable)
VALID_TYPE_NAMES = {
    'multiple_choice_single',
    'multiple_response',
    'true_false',
    'text_entry',
    'text_entry_math',
    'text_entry_numeric',
    'inline_choice',
    'match',
    'hotspot',
    'graphicgapmatch_v2',
    'text_entry_graphic',
    'text_area',
    'essay',
    'audio_record',
    'composite_editor',
    'nativehtml',
}


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

    # 5. Check placeholder syntax
    issues.extend(_check_placeholders(content))

    # 6. Check field structure (@end_field)
    issues.extend(_check_field_structure(content))

    # 7. Check type name validity
    issues.extend(_check_type_name(content))

    # 8. Check type-specific structure requirements
    issues.extend(_check_type_structure(content, question_type))

    return issues


def _check_metadata(content: str) -> List[Issue]:
    """Check for required metadata."""
    issues = []

    for field, pattern, description in REQUIRED_METADATA:
        if not re.search(pattern, content, re.MULTILINE):
            # Check if old syntax exists (@key:)
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
                elif field == '^tags':
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
    """Check for Legacy Syntax patterns."""
    issues = []

    # Old metadata patterns (@ with colon instead of ^ with space)
    old_patterns = [
        (r'^@question:', '^question', 'metadata_syntax'),
        (r'^@type:', '^type', 'metadata_syntax'),
        (r'^@identifier:', '^identifier', 'metadata_syntax'),
        (r'^@title:', '^title', 'metadata_syntax'),
        (r'^@points:', '^points', 'metadata_syntax'),
        (r'^@tags:', '^tags', 'metadata_syntax'),
        (r'^@labels:', '^tags', 'metadata_syntax'),
        (r'^@shuffle:', '^shuffle', 'metadata_syntax'),
        (r'^@language:', '^language', 'metadata_syntax'),
    ]

    found_transforms = set()
    for old_pattern, new_syntax, transform_id in old_patterns:
        if re.search(old_pattern, content, re.MULTILINE):
            if transform_id not in found_transforms:
                issues.append(Issue(
                    severity=Severity.CRITICAL,
                    category='old_syntax',
                    field='metadata',
                    message=f"Legacy Syntax needs conversion to QFMD",
                    auto_fixable=True,
                    transform_id=transform_id
                ))
                found_transforms.add(transform_id)

    # Check for missing @end_field markers
    field_starts = len(re.findall(r'^@field:', content, re.MULTILINE))
    field_ends = len(re.findall(r'^@end_field', content, re.MULTILINE))

    if field_starts > 0 and field_ends == 0:
        issues.append(Issue(
            severity=Severity.CRITICAL,
            category='old_syntax',
            field='structure',
            message=f"Saknar @end_field markerare ({field_starts} @field: utan motsvarande @end_field)",
            auto_fixable=True,
            transform_id='add_end_fields'
        ))

    # Check for ## headers that should be ### in QFMD
    if re.search(r'^##\s+(Question Text|Options|Answer|Feedback|Blanks|Scoring|Pairs)', content, re.MULTILINE):
        issues.append(Issue(
            severity=Severity.WARNING,
            category='old_syntax',
            field='headers',
            message="## headers → ### headers (QFMD format)",
            auto_fixable=True,
            transform_id='upgrade_headers'
        ))

    return issues


def _check_labels(content: str) -> List[Issue]:
    """Check that labels/tags contain Bloom and Difficulty."""
    issues = []

    # Match both ^tags and @tags:
    labels_match = re.search(r'(?:\^tags|@tags:)\s+(.+)$', content, re.MULTILINE)
    if labels_match:
        labels = labels_match.group(1)

        has_bloom = any(level in labels for level in BLOOM_LEVELS)
        has_difficulty = any(level in labels for level in DIFFICULTY_LEVELS)

        if not has_bloom:
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category='incomplete_labels',
                field='^tags',
                message="Tags saknar Bloom-nivå (Remember/Understand/Apply/Analyze)",
                current_value=labels,
                prompt_key='select_bloom'
            ))

        if not has_difficulty:
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category='incomplete_labels',
                field='^tags',
                message="Tags saknar svårighetsgrad (Easy/Medium/Hard)",
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
            issues.append(Issue(
                severity=Severity.WARNING,
                category='missing_field',
                field=field_name,
                message=f"Saknar @field: {field_name}"
            ))

    return issues


def _check_placeholders(content: str) -> List[Issue]:
    """Check placeholder syntax."""
    issues = []

    # Old blank syntax: {{BLANK-1}} should be {{blank_1}}
    if re.search(r'\{\{BLANK-\d+\}\}', content, re.IGNORECASE):
        issues.append(Issue(
            severity=Severity.CRITICAL,
            category='old_syntax',
            field='placeholders',
            message="Gammal syntax {{BLANK-1}} → {{blank_1}}",
            auto_fixable=True,
            transform_id='placeholder_syntax'
        ))

    # Old dropdown syntax: {{DROPDOWN-1}} should be {{dropdown_1}}
    if re.search(r'\{\{DROPDOWN-\d+\}\}', content, re.IGNORECASE):
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
    subfield_starts = len(re.findall(r'^@@field:', content, re.MULTILINE))
    subfield_ends = len(re.findall(r'^@@end_field', content, re.MULTILINE))

    # For QFMD, we need matching pairs
    if field_starts > field_ends:
        issues.append(Issue(
            severity=Severity.CRITICAL,
            category='structure',
            field='@end_field',
            message=f"Saknar {field_starts - field_ends} st @end_field",
            auto_fixable=True,
            transform_id='add_end_fields'
        ))

    # Check nested fields - in Legacy Syntax nested fields use @field: instead of @@field:
    # This is detected by the header pattern ### within an @field: block
    if re.search(r'^###\s+\w+.*\n@field:', content, re.MULTILINE):
        issues.append(Issue(
            severity=Severity.CRITICAL,
            category='old_syntax',
            field='nested_fields',
            message="Nested fields use @field: → @@field: (QFMD)",
            auto_fixable=True,
            transform_id='nested_field_syntax'
        ))

    return issues


def _check_type_name(content: str) -> List[Issue]:
    """Check that ^type uses valid QTI-exportable type name."""
    issues = []

    # Extract type value
    type_match = re.search(r'\^type:?\s+(\S+)', content, re.MULTILINE)
    if type_match:
        type_value = type_match.group(1)

        # Check if it's an alias that needs normalization
        if type_value.lower() in TYPE_NAME_ALIASES:
            correct_type = TYPE_NAME_ALIASES[type_value.lower()]
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category='invalid_type',
                field='^type',
                message=f"Typnamn '{type_value}' → '{correct_type}'",
                current_value=type_value,
                suggested_value=correct_type,
                auto_fixable=True,
                transform_id='normalize_type_names'
            ))
        elif type_value not in VALID_TYPE_NAMES:
            # Unknown type - might need manual review
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category='invalid_type',
                field='^type',
                message=f"Okänd frågetyp '{type_value}' - kontrollera manuellt",
                current_value=type_value,
                prompt_key='unknown_type'
            ))

    return issues


def _check_type_structure(content: str, question_type: Optional[str]) -> List[Issue]:
    """Check type-specific structure requirements."""
    issues = []

    if not question_type:
        # Try to detect from content
        type_match = re.search(r'\^type:?\s+(\S+)', content, re.MULTILINE)
        if type_match:
            question_type = type_match.group(1)
            # Normalize if alias
            question_type = TYPE_NAME_ALIASES.get(question_type.lower(), question_type)

    if not question_type:
        return issues

    # Multiple response needs correct_answers section
    if question_type == 'multiple_response':
        has_correct_answers = bool(re.search(
            r'@field:\s*correct_answers|###\s*Correct\s*Answers',
            content, re.IGNORECASE
        ))
        # Check if [correct] markers exist in options (can be extracted)
        has_correct_markers = bool(re.search(r'\[correct\]', content, re.IGNORECASE))

        if not has_correct_answers and has_correct_markers:
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category='missing_structure',
                field='correct_answers',
                message="multiple_response: [correct] markerare → @field: correct_answers",
                auto_fixable=True,
                transform_id='extract_correct_answers'
            ))
        elif not has_correct_answers and not has_correct_markers:
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category='missing_structure',
                field='correct_answers',
                message="multiple_response: Saknar correct_answers sektion",
                prompt_key='add_correct_answers'
            ))

    # Text entry needs blank placeholder and blanks section
    if question_type in ('text_entry', 'text_entry_math', 'text_entry_numeric'):
        has_placeholder = bool(re.search(r'\{\{blank_\d+\}\}', content, re.IGNORECASE))
        has_blanks_field = bool(re.search(r'@field:\s*blanks', content, re.IGNORECASE))

        if not has_placeholder or not has_blanks_field:
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category='missing_structure',
                field='blanks',
                message="text_entry: Saknar {{blank_1}} placeholder och/eller @field: blanks",
                auto_fixable=True,
                transform_id='restructure_text_entry'
            ))

    return issues


def get_auto_fixable_issues(issues: List[Issue]) -> List[Issue]:
    """Get only auto-fixable issues."""
    return [i for i in issues if i.auto_fixable]


def get_issues_needing_input(issues: List[Issue]) -> List[Issue]:
    """Get issues that need user input."""
    return [i for i in issues if not i.auto_fixable and i.prompt_key]


def count_issues_by_severity(issues: List[Issue]) -> dict:
    """Count issues by severity level."""
    return {
        'critical': sum(1 for i in issues if i.severity == Severity.CRITICAL),
        'warning': sum(1 for i in issues if i.severity == Severity.WARNING),
        'info': sum(1 for i in issues if i.severity == Severity.INFO),
    }
