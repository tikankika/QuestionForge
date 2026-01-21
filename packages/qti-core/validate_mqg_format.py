#!/usr/bin/env python3
"""
MQG Format Validator - v6.5 Format

Validates markdown question files against MQG_bb6 v6.5 Field Requirements
before QTI generation.

v6.5 Format:
    # Q001 Title
    ^question Q001
    ^type multiple_choice_single
    ^identifier MC_Q001
    ^points 1
    ^labels #label1 #label2

    ### Question Text
    @field: question_text
    Content with {{blank_1}} or {{dropdown_1}} placeholders...
    @end_field

    ### Feedback
    @field: feedback
    @@field: general_feedback
    Content...
    @@end_field
    @end_field

Usage:
    python validate_mqg_format.py input.md
    python validate_mqg_format.py input.md --verbose

Exit codes:
    0 = Valid (ready for QTI generation)
    1 = Errors found (fix before QTI generation)
    2 = File not found or other error
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, field

# Valid question type codes according to MQG specs
VALID_TYPES = {
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
    'nativehtml'
}

# Types that require specific sections (using @field: identifiers)
REQUIRES_OPTIONS = {'multiple_choice_single', 'multiple_response', 'true_false'}
REQUIRES_ANSWER = {'multiple_choice_single', 'true_false'}
REQUIRES_CORRECT_ANSWERS = {'multiple_response'}
REQUIRES_BLANKS = {'text_entry', 'text_entry_math', 'text_entry_numeric'}
REQUIRES_DROPDOWNS = {'inline_choice'}
REQUIRES_IMAGE = {'hotspot', 'graphicgapmatch_v2', 'text_entry_graphic'}
REQUIRES_SCORING = {'multiple_response', 'text_entry', 'text_entry_math', 'text_entry_numeric', 'inline_choice', 'match', 'graphicgapmatch_v2', 'text_entry_graphic'}
REQUIRES_RUBRIC = {'text_area', 'essay', 'audio_record'}
REQUIRES_PAIRS = {'match'}

# Types that need partially correct feedback
REQUIRES_PARTIAL_FEEDBACK = {'multiple_response', 'text_entry', 'text_entry_math', 'text_entry_numeric', 'inline_choice', 'match', 'graphicgapmatch_v2', 'text_entry_graphic', 'composite_editor'}

# Bloom's levels and difficulty
BLOOM_LEVELS = {'Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create'}
DIFFICULTY_LEVELS = {'Easy', 'Medium', 'Hard'}


@dataclass
class ValidationIssue:
    """Represents a validation error or warning"""
    level: str  # 'ERROR' or 'WARNING'
    question_num: int
    question_id: str
    message: str
    line_num: int = 0


@dataclass
class ValidationReport:
    """Validation results for a markdown file"""
    errors: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    total_questions: int = 0
    valid_questions: int = 0

    def add_error(self, q_num: int, q_id: str, message: str, line: int = 0):
        self.errors.append(ValidationIssue('ERROR', q_num, q_id, message, line))

    def add_warning(self, q_num: int, q_id: str, message: str, line: int = 0):
        self.warnings.append(ValidationIssue('WARNING', q_num, q_id, message, line))

    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def print_report(self):
        """Print formatted validation report"""
        print("=" * 80)
        print("MQG FORMAT VALIDATION REPORT (v6.5)")
        print("=" * 80)
        print()

        if self.errors:
            print("❌ ERRORS FOUND:\n")
            for issue in self.errors:
                print(f"Question {issue.question_num} ({issue.question_id}):")
                if issue.line_num:
                    print(f"  Line {issue.line_num}: {issue.message}")
                else:
                    print(f"  {issue.message}")
                print()

        if self.warnings:
            print("⚠️  WARNINGS:\n")
            for issue in self.warnings:
                print(f"Question {issue.question_num} ({issue.question_id}):")
                print(f"  {issue.message}")
                print()

        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total Questions: {self.total_questions}")
        print(f"✅ Valid: {self.valid_questions}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print()

        if self.is_valid():
            print("STATUS: ✅ READY FOR QTI GENERATION")
        else:
            print(f"STATUS: ❌ NOT READY - Fix {len(self.errors)} error(s) before QTI generation")
            print()
            print("→ Go back to Claude Desktop and fix the errors listed above")


def split_questions(content: str) -> List[str]:
    """
    Split content into question blocks.

    Uses:
    - ===QUESTIONS=== marker to separate header from questions
    - # Q001 headers to mark question starts
    """
    # Find ===QUESTIONS=== marker
    questions_marker = '===QUESTIONS==='
    if questions_marker in content:
        # Split at marker, take everything after
        content = content.split(questions_marker, 1)[1]

    # Split by question headers: # Q001, # Q002, etc.
    # Pattern matches: # Q001 Title
    question_pattern = r'\n(?=# Q\d+[A-Z]?\s)'

    blocks = re.split(question_pattern, content)

    # Filter out empty blocks and non-question content
    question_blocks = []
    for block in blocks:
        block = block.strip()
        if block and re.match(r'^# Q\d+[A-Z]?\s', block):
            question_blocks.append(block)

    return question_blocks


def extract_field_sections(block: str) -> Dict[str, str]:
    """
    Extract sections using v6.5 field boundaries.

    v6.5 format:
    - @field: / @end_field for top-level fields
    - @@field: / @@end_field for subfields (nested)

    Uses stack-based parsing to handle nested fields.
    Returns dict mapping field_id -> content
    """
    sections = {}
    lines = block.split('\n')
    field_stack = []

    for line in lines:
        # Skip header lines (###, ####) - they're for human readability only
        if re.match(r'^#{2,4}\s+', line):
            continue

        # Check for @@field: or @subfield: start (subfield, v6.5)
        # Accepts both @@field: and @subfield: formats
        subfield_match = re.match(r'^(?:@@field|@subfield):\s*(\w+)\s*(.*)', line)
        if subfield_match:
            field_id = subfield_match.group(1)
            same_line_content = subfield_match.group(2).strip()
            field_stack.append({'id': field_id, 'content': []})
            # Handle content on same line as @subfield:
            if same_line_content:
                field_stack[-1]['content'].append(same_line_content)
            continue

        # Check for @field: start (top-level)
        # Also captures any content on the same line
        field_match = re.match(r'^@field:\s*(\w+)\s*(.*)', line)
        if field_match:
            field_id = field_match.group(1)
            same_line_content = field_match.group(2).strip()
            field_stack.append({'id': field_id, 'content': []})
            # Handle content on same line as @field:
            if same_line_content:
                field_stack[-1]['content'].append(same_line_content)
            continue

        # Check for @@end_field or @end_subfield (subfield end, v6.5)
        if line.strip() in ('@@end_field', '@end_subfield'):
            if field_stack:
                completed = field_stack.pop()
                sections[completed['id']] = '\n'.join(completed['content']).strip()
            continue

        # Check for @end_field (top-level end)
        if line.strip() == '@end_field':
            if field_stack:
                completed = field_stack.pop()
                sections[completed['id']] = '\n'.join(completed['content']).strip()
            continue

        # Add content to current field
        if field_stack:
            field_stack[-1]['content'].append(line)

    return sections


# Note: Feedback subsections are extracted by extract_field_sections() via stack-based parsing.
# v6.5 uses @@field: for subfields. Feedback subsections (general_feedback, correct_feedback, etc.)
# appear directly in the sections dict alongside other fields.


def validate_content(content: str, verbose: bool = False) -> Tuple[bool, List[ValidationIssue]]:
    """
    Validate markdown content string against MQG v6.5 specs.
    """
    report = ValidationReport()

    # Split into questions
    question_blocks = split_questions(content)
    report.total_questions = len(question_blocks)

    if report.total_questions == 0:
        report.add_error(0, 'FILE', 'No questions found. Check for ===QUESTIONS=== marker and # Q001 headers.')
        return report.is_valid(), report.errors + report.warnings

    identifiers_seen: Set[str] = set()

    for q_num, block in enumerate(question_blocks, 1):
        issues = validate_question_block(block, q_num, identifiers_seen, verbose)

        # Count valid questions
        has_critical_error = any(
            'Missing ^type' in issue.message or
            'Missing ^identifier' in issue.message or
            'Invalid question type' in issue.message
            for issue in issues if issue.level == 'ERROR'
        )

        if not has_critical_error:
            report.valid_questions += 1

        for issue in issues:
            if issue.level == 'ERROR':
                report.errors.append(issue)
            else:
                report.warnings.append(issue)

    return report.is_valid(), report.errors + report.warnings


def validate_markdown_file(file_path: Path, verbose: bool = False) -> ValidationReport:
    """Validate a markdown file against MQG v6.5 specs"""
    report = ValidationReport()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(2)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(2)

    is_valid, issues = validate_content(content, verbose)

    for issue in issues:
        if issue.level == 'ERROR':
            report.errors.append(issue)
        else:
            report.warnings.append(issue)

    # Count questions
    question_blocks = split_questions(content)
    report.total_questions = len(question_blocks)
    report.valid_questions = report.total_questions - len([i for i in issues if i.level == 'ERROR'])

    return report


def validate_question_block(block: str, q_num: int, identifiers: Set[str], verbose: bool) -> List[ValidationIssue]:
    """Validate a single question block in v6.5 format"""
    issues = []

    # Extract header line: # Q001 Title
    header_match = re.match(r'^# (Q\d+[A-Z]?)\s+(.*)$', block, re.MULTILINE)
    q_code = header_match.group(1) if header_match else f'Q{q_num}'

    # Extract ^ metadata from header section (before first ##)
    header_section = block.split('\n##')[0] if '\n##' in block else block

    # Extract ^type (v6.5 format) - accepts optional colon, anywhere on line
    # Handles both "^type value" and "^type: value" formats
    type_match = re.search(r'\^type:?\s+(\S+)', header_section, re.MULTILINE)
    q_type = type_match.group(1).strip() if type_match else None

    # Extract ^identifier (v6.5 format) - accepts optional colon, anywhere on line
    # Handles multi-field lines like "^type: X ^identifier: Y ^points: Z"
    id_match = re.search(r'\^identifier:?\s+(\S+)', header_section, re.MULTILINE)
    q_id = id_match.group(1).strip() if id_match else q_code

    # Extract ^points (v6.5 format) - accepts optional colon, anywhere on line
    points_match = re.search(r'\^points:?\s+(\d+)', header_section, re.MULTILINE)

    # Extract ^labels (v6.5 format) - Inspera "Labels", accepts optional colon
    labels_match = re.search(r'\^labels:?\s+(.+?)(?=\^|$)', header_section, re.MULTILINE)

    # Extract ^tags (alternative to ^labels) - accepts optional colon
    tags_match = re.search(r'\^tags:?\s+(.+?)(?=\^|$)', header_section, re.MULTILINE)

    # Use ^tags as labels if ^labels not present
    if not labels_match and tags_match:
        labels_match = tags_match

    # Extract ^custom_metadata (v6.5 format) - optional
    custom_metadata_matches = re.findall(r'^\^custom_metadata\s+(.+)$', header_section, re.MULTILINE)

    # Validate required metadata
    if not type_match:
        issues.append(ValidationIssue('ERROR', q_num, q_id, 'Missing ^type field'))
    elif q_type not in VALID_TYPES:
        issues.append(ValidationIssue('ERROR', q_num, q_id, f'Invalid question type: "{q_type}" (check spelling and underscores)'))

    if not id_match:
        issues.append(ValidationIssue('ERROR', q_num, q_id, 'Missing ^identifier field'))
    else:
        if q_id in identifiers:
            issues.append(ValidationIssue('ERROR', q_num, q_id, f'Duplicate identifier: {q_id} (must be unique)'))
        identifiers.add(q_id)

        if not re.match(r'^[A-Z0-9_]+$', q_id):
            issues.append(ValidationIssue('WARNING', q_num, q_id, f'Identifier should be UPPERCASE_UNDERSCORES: {q_id}'))

    if not points_match:
        issues.append(ValidationIssue('ERROR', q_num, q_id, 'Missing ^points field'))

    # Extract sections by @field: identifier
    sections = extract_field_sections(block)

    # Check for question_text section
    if 'question_text' not in sections:
        issues.append(ValidationIssue('ERROR', q_num, q_id, 'Missing "question_text" section (@field: question_text)'))

    # Type-specific validation
    if q_type:
        if q_type in REQUIRES_OPTIONS:
            if 'options' not in sections:
                issues.append(ValidationIssue('ERROR', q_num, q_id, f'Missing "options" section (required for {q_type})'))

        if q_type in REQUIRES_ANSWER:
            if 'answer' not in sections:
                issues.append(ValidationIssue('ERROR', q_num, q_id, f'Missing "answer" section (required for {q_type})'))

        if q_type in REQUIRES_CORRECT_ANSWERS:
            if 'correct_answers' not in sections:
                issues.append(ValidationIssue('ERROR', q_num, q_id, f'Missing "correct_answers" section (required for {q_type})'))

        if q_type in REQUIRES_PAIRS:
            if 'pairs' not in sections:
                issues.append(ValidationIssue('ERROR', q_num, q_id, f'Missing "pairs" section (required for {q_type})'))
            else:
                # Validate pairs format - must be inline format "1. X → Y" or "- X → Y"
                pairs_content = sections.get('pairs', '')
                has_inline_format = re.search(r'(\d+\.|[-•])\s*.+\s*(→|->)\s*.+', pairs_content)
                has_table_format = re.search(r'\|.*\|.*\|', pairs_content)
                if has_table_format and not has_inline_format:
                    issues.append(ValidationIssue('ERROR', q_num, q_id,
                        'Match pairs must use inline format: "1. X → Y" (table format not supported)'))
                elif not has_inline_format:
                    issues.append(ValidationIssue('ERROR', q_num, q_id,
                        'Match pairs format not recognized - use: "1. Premise → Response"'))

        if q_type in REQUIRES_BLANKS:
            # Check for {{blank_N}} placeholders (v6.5 format)
            if '{{blank_' not in block:
                issues.append(ValidationIssue('ERROR', q_num, q_id, 'text_entry requires {{blank_N}} placeholder(s) in question text'))

            # Check for blanks section or blank_N subsections
            has_blanks = 'blanks' in sections or any(k.startswith('blank_') for k in sections)
            if not has_blanks:
                issues.append(ValidationIssue('ERROR', q_num, q_id, 'Missing "blanks" section or blank_N subsections'))

        if q_type in REQUIRES_DROPDOWNS:
            if '{{dropdown_' not in block:
                issues.append(ValidationIssue('WARNING', q_num, q_id, 'No {{dropdown_N}} placeholders found in question text'))

            has_dropdowns = any(k.startswith('dropdown_') for k in sections)
            if not has_dropdowns:
                issues.append(ValidationIssue('ERROR', q_num, q_id, 'Missing "dropdown_N" sections'))

        if q_type in REQUIRES_IMAGE:
            if '![' not in block:
                issues.append(ValidationIssue('WARNING', q_num, q_id, f'No image reference found (expected for {q_type})'))

        if q_type in REQUIRES_SCORING:
            if 'scoring' not in sections:
                issues.append(ValidationIssue('ERROR', q_num, q_id, f'Missing "scoring" section (required for {q_type})'))

        if q_type in REQUIRES_RUBRIC:
            if 'scoring_rubric' not in sections and 'scoring' not in sections:
                issues.append(ValidationIssue('ERROR', q_num, q_id, f'Missing "scoring_rubric" or "scoring" section (required for {q_type})'))

    # Validate feedback (v6.5: @@field: subsections are in sections dict via stack-based parsing)
    if 'feedback' not in sections:
        issues.append(ValidationIssue('ERROR', q_num, q_id, 'Missing "feedback" section (@field: feedback)'))
    else:
        if 'general_feedback' not in sections:
            issues.append(ValidationIssue('ERROR', q_num, q_id, 'Missing "general_feedback" subsection (@@field: general_feedback)'))

        # Auto-graded questions need specific feedback subsections
        if q_type and q_type not in ['text_area', 'essay', 'audio_record', 'nativehtml', 'composite_editor']:
            if 'correct_feedback' not in sections:
                issues.append(ValidationIssue('ERROR', q_num, q_id, 'Missing "correct_feedback" subsection (@@field: correct_feedback)'))
            if 'incorrect_feedback' not in sections:
                issues.append(ValidationIssue('ERROR', q_num, q_id, 'Missing "incorrect_feedback" subsection (@@field: incorrect_feedback)'))
            if 'unanswered_feedback' not in sections:
                issues.append(ValidationIssue('ERROR', q_num, q_id, 'Missing "unanswered_feedback" subsection (@@field: unanswered_feedback)'))

            if q_type in REQUIRES_PARTIAL_FEEDBACK:
                if 'partial_feedback' not in sections:
                    issues.append(ValidationIssue('ERROR', q_num, q_id, f'Missing "partial_feedback" subsection (required for {q_type})'))

    # Validate labels content
    if labels_match:
        labels_content = labels_match.group(1).strip()

        if not labels_content:
            issues.append(ValidationIssue('ERROR', q_num, q_id, '^labels field cannot be empty'))
        else:
            # Check for Bloom's level
            has_bloom = any(bloom.lower() in labels_content.lower() for bloom in BLOOM_LEVELS)
            if not has_bloom:
                issues.append(ValidationIssue('ERROR', q_num, q_id,
                    f"^labels must include Bloom's level (Remember, Understand, Apply, Analyze, Evaluate, or Create)"))

            # Check for Difficulty level
            has_difficulty = any(diff.lower() in labels_content.lower() for diff in DIFFICULTY_LEVELS)
            if not has_difficulty:
                issues.append(ValidationIssue('ERROR', q_num, q_id,
                    '^labels must include Difficulty level (Easy, Medium, or Hard)'))
    else:
        issues.append(ValidationIssue('ERROR', q_num, q_id, 'Missing ^labels field'))

    # Validate custom_metadata format (optional field)
    for cm_line in custom_metadata_matches:
        if ':' not in cm_line:
            issues.append(ValidationIssue('WARNING', q_num, q_id,
                f'Invalid ^custom_metadata format "{cm_line}" - expected "Field name: value"'))

    return issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_mqg_format.py <markdown_file> [--verbose]")
        print()
        print("Validates markdown question files against MQG_bb6 v6.5 specs before QTI generation.")
        sys.exit(2)

    file_path = Path(sys.argv[1])
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    print(f"Validating: {file_path}")
    print()

    report = validate_markdown_file(file_path, verbose)
    report.print_report()

    sys.exit(0 if report.is_valid() else 1)


if __name__ == '__main__':
    main()
