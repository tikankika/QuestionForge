"""
Structural Issue Detection for Step 1.

Focuses ONLY on structural/syntax issues that Step 1 should fix.
Pedagogical issues (missing content) go to M5, not Step 1.

RFC-013 Beslut 5-6:
- M5 ansvar: Generera strukturellt korrekt output
- Step 1 ansvar: Säkerhetsnät för M5-buggar, file corruption, äldre format
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class IssueSeverity(Enum):
    """Severity levels for structural issues."""
    ERROR = "error"       # Must fix - blocks export
    WARNING = "warning"   # Should fix - may cause problems
    INFO = "info"         # Nice to fix - style/consistency


class IssueCategory(Enum):
    """Issue categories for routing."""
    STRUCTURAL = "structural"       # Step 1 fixes these
    PEDAGOGICAL = "pedagogical"     # M5 fixes these (missing content)
    MECHANICAL = "mechanical"       # Step 3 auto-fixes these


@dataclass
class StructuralIssue:
    """A structural issue detected in a question."""

    issue_type: str               # e.g., "missing_separator_after"
    severity: IssueSeverity
    category: IssueCategory
    message: str                  # Swedish user-facing message
    line_number: Optional[int]    # Where in the question
    fix_suggestion: str           # What to do
    auto_fixable: bool           # Can be auto-fixed by transformer


# Structural issue types that Step 1 handles
STRUCTURAL_ISSUE_TYPES = [
    "missing_separator_before",
    "missing_separator_after",
    "metadata_colon",
    "unclosed_field_block",
    "malformed_field_start",
    "malformed_field_end",
    "legacy_at_syntax",
    "junk_content_between_questions",
    "missing_question_header",
    "duplicate_field",
]

# Pedagogical issues - route to M5, not Step 1
PEDAGOGICAL_ISSUE_TYPES = [
    "missing_question_text",
    "missing_options",
    "missing_correct_answer",
    "missing_feedback",
    "missing_bloom_level",
    "missing_difficulty",
    "missing_type",
    "incomplete_content",
]


def detect_structural_issues(question_content: str, question_id: str = "Q???") -> List[StructuralIssue]:
    """
    Detect structural issues in a single question.

    Only detects STRUCTURAL issues that Step 1 should fix.
    Pedagogical issues are detected separately.

    Args:
        question_content: Raw markdown content of one question
        question_id: Question identifier for error messages

    Returns:
        List of StructuralIssue objects
    """
    issues = []

    # Check for metadata colon (^type: instead of ^type)
    issues.extend(_check_metadata_colon(question_content))

    # Check for unclosed field blocks
    issues.extend(_check_unclosed_fields(question_content))

    # Check for malformed field syntax
    issues.extend(_check_malformed_fields(question_content))

    # Check for legacy @ syntax
    issues.extend(_check_legacy_syntax(question_content))

    # Check for junk content
    issues.extend(_check_junk_content(question_content))

    return issues


def detect_separator_issues(content: str, questions: list) -> List[StructuralIssue]:
    """
    Detect separator issues between questions.

    Must be called with full file content and parsed questions.

    Args:
        content: Full markdown file content
        questions: List of parsed questions with line_start/line_end

    Returns:
        List of separator-related StructuralIssue objects
    """
    issues = []
    lines = content.split('\n')

    for i, q in enumerate(questions):
        # Check for separator before (except first question)
        if i > 0:
            # Look for --- before question header
            prev_line_idx = q.line_start - 2  # Line before header (0-indexed)
            if prev_line_idx >= 0:
                prev_line = lines[prev_line_idx].strip()
                if prev_line != '---' and prev_line != '':
                    issues.append(StructuralIssue(
                        issue_type="missing_separator_before",
                        severity=IssueSeverity.ERROR,
                        category=IssueCategory.STRUCTURAL,
                        message=f"Saknar separator (---) före {q.question_id}",
                        line_number=q.line_start,
                        fix_suggestion="Lägg till '---' före frågeheadern",
                        auto_fixable=True
                    ))

        # Check for separator after (except last question)
        if i < len(questions) - 1:
            # Look for --- after question ends
            next_line_idx = q.line_end  # Line after question (0-indexed)
            if next_line_idx < len(lines):
                next_line = lines[next_line_idx].strip()
                if next_line != '---' and not next_line.startswith('#'):
                    issues.append(StructuralIssue(
                        issue_type="missing_separator_after",
                        severity=IssueSeverity.ERROR,
                        category=IssueCategory.STRUCTURAL,
                        message=f"Saknar separator (---) efter {q.question_id}",
                        line_number=q.line_end,
                        fix_suggestion="Lägg till '---' efter @end_field",
                        auto_fixable=True
                    ))

    return issues


def _check_metadata_colon(content: str) -> List[StructuralIssue]:
    """Check for colons in metadata fields (^type: instead of ^type)."""
    issues = []

    # Patterns for metadata with colon
    metadata_patterns = [
        (r'^\^type:', 'type'),
        (r'^\^identifier:', 'identifier'),
        (r'^\^points:', 'points'),
        (r'^\^tags:', 'tags'),
        (r'^\^labels:', 'labels'),
    ]

    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        for pattern, field_name in metadata_patterns:
            if re.match(pattern, line.strip()):
                issues.append(StructuralIssue(
                    issue_type="metadata_colon",
                    severity=IssueSeverity.ERROR,
                    category=IssueCategory.STRUCTURAL,
                    message=f"Metadata ^{field_name} har kolon - ska vara utan",
                    line_number=line_num,
                    fix_suggestion=f"Ändra ^{field_name}: till ^{field_name}",
                    auto_fixable=True
                ))

    return issues


def _check_unclosed_fields(content: str) -> List[StructuralIssue]:
    """Check for fields without @end_field."""
    issues = []

    # Count @field: and @end_field
    field_starts = re.findall(r'^@field:\s*\w+', content, re.MULTILINE)
    field_ends = re.findall(r'^@end_field', content, re.MULTILINE)

    if len(field_starts) > len(field_ends):
        diff = len(field_starts) - len(field_ends)
        issues.append(StructuralIssue(
            issue_type="unclosed_field_block",
            severity=IssueSeverity.ERROR,
            category=IssueCategory.STRUCTURAL,
            message=f"{diff} fält saknar @end_field",
            line_number=None,
            fix_suggestion="Lägg till @end_field efter varje fältinnehåll",
            auto_fixable=True
        ))

    # Also check nested fields (@@field: / @@end_field)
    nested_starts = re.findall(r'^@@field:\s*\w+', content, re.MULTILINE)
    nested_ends = re.findall(r'^@@end_field', content, re.MULTILINE)

    if len(nested_starts) > len(nested_ends):
        diff = len(nested_starts) - len(nested_ends)
        issues.append(StructuralIssue(
            issue_type="unclosed_field_block",
            severity=IssueSeverity.ERROR,
            category=IssueCategory.STRUCTURAL,
            message=f"{diff} nästlade fält saknar @@end_field",
            line_number=None,
            fix_suggestion="Lägg till @@end_field efter varje nästlat fält",
            auto_fixable=True
        ))

    return issues


def _check_malformed_fields(content: str) -> List[StructuralIssue]:
    """Check for malformed field syntax."""
    issues = []
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        # Check for @field without colon
        if re.match(r'^@field\s+\w+', stripped):
            issues.append(StructuralIssue(
                issue_type="malformed_field_start",
                severity=IssueSeverity.ERROR,
                category=IssueCategory.STRUCTURAL,
                message=f"@field saknar kolon på rad {line_num}",
                line_number=line_num,
                fix_suggestion="Ändra @field till @field:",
                auto_fixable=True
            ))

        # Check for @end_field: (should be without colon)
        if re.match(r'^@end_field:', stripped):
            issues.append(StructuralIssue(
                issue_type="malformed_field_end",
                severity=IssueSeverity.WARNING,
                category=IssueCategory.STRUCTURAL,
                message=f"@end_field har kolon på rad {line_num}",
                line_number=line_num,
                fix_suggestion="Ändra @end_field: till @end_field",
                auto_fixable=True
            ))

    return issues


def _check_legacy_syntax(content: str) -> List[StructuralIssue]:
    """Check for legacy @ metadata syntax (should be ^)."""
    issues = []

    # Legacy patterns that should use ^ instead of @
    legacy_patterns = [
        (r'^@type:', 'type'),
        (r'^@identifier:', 'identifier'),
        (r'^@points:', 'points'),
        (r'^@tags:', 'tags'),
        (r'^@question:', 'question'),
    ]

    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        for pattern, field_name in legacy_patterns:
            if re.match(pattern, line.strip()):
                issues.append(StructuralIssue(
                    issue_type="legacy_at_syntax",
                    severity=IssueSeverity.ERROR,
                    category=IssueCategory.STRUCTURAL,
                    message=f"Gammal @{field_name} syntax - ska vara ^{field_name}",
                    line_number=line_num,
                    fix_suggestion=f"Ändra @{field_name}: till ^{field_name}",
                    auto_fixable=True
                ))

    return issues


def _check_junk_content(content: str) -> List[StructuralIssue]:
    """Check for junk content outside field blocks."""
    issues = []

    # This is complex - for now just check for common patterns
    # that indicate content outside proper fields

    # Text after @end_field that isn't a new section
    pattern = r'@end_field\n+([^#@\-\n].+)'
    matches = re.findall(pattern, content)

    for match in matches:
        if match.strip() and not match.strip().startswith('---'):
            issues.append(StructuralIssue(
                issue_type="junk_content_between_questions",
                severity=IssueSeverity.WARNING,
                category=IssueCategory.STRUCTURAL,
                message="Text utanför fältblock - kan orsaka parserproblem",
                line_number=None,
                fix_suggestion="Ta bort eller flytta text till ett fält",
                auto_fixable=False
            ))
            break  # Only report once

    return issues


def categorize_issues(issues: list) -> Tuple[List, List, List]:
    """
    Categorize issues into structural, pedagogical, and mechanical.

    Args:
        issues: List of issues (can be StructuralIssue or other)

    Returns:
        Tuple of (structural, pedagogical, mechanical) issue lists
    """
    structural = []
    pedagogical = []
    mechanical = []

    for issue in issues:
        if hasattr(issue, 'category'):
            if issue.category == IssueCategory.STRUCTURAL:
                structural.append(issue)
            elif issue.category == IssueCategory.PEDAGOGICAL:
                pedagogical.append(issue)
            elif issue.category == IssueCategory.MECHANICAL:
                mechanical.append(issue)
        elif hasattr(issue, 'issue_type') or hasattr(issue, 'message'):
            # Legacy issue format - categorize by message/type
            issue_str = str(getattr(issue, 'issue_type', '')) + str(getattr(issue, 'message', '')).lower()

            if any(pt in issue_str for pt in ['separator', 'colon', 'field', 'syntax', 'unclosed']):
                structural.append(issue)
            elif any(pt in issue_str for pt in ['missing', 'saknar', 'content']):
                pedagogical.append(issue)
            else:
                mechanical.append(issue)
        else:
            # Unknown format - default to structural
            structural.append(issue)

    return structural, pedagogical, mechanical


def is_structural_issue(issue_type: str) -> bool:
    """Check if an issue type is structural (Step 1's responsibility)."""
    return issue_type in STRUCTURAL_ISSUE_TYPES


def is_pedagogical_issue(issue_type: str) -> bool:
    """Check if an issue type is pedagogical (M5's responsibility)."""
    return issue_type in PEDAGOGICAL_ISSUE_TYPES
