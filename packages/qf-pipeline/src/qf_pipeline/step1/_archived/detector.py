"""
Detect input format level.
"""

import re
from enum import Enum


class FormatLevel(Enum):
    """Input format levels."""
    QFMD = 'qfmd'                    # QuestionForge Markdown (canonical)
    LEGACY_SYNTAX = 'legacy'         # Old @question:/@type: syntax
    SEMI_STRUCTURED = 'semi'         # Has ## headers, **Type**: etc
    UNSTRUCTURED = 'unstructured'    # Unstructured, needs scaffolding
    UNKNOWN = 'unknown'              # Cannot determine format


def detect_format(content: str) -> FormatLevel:
    """
    Detect the format level of input content.

    Args:
        content: Full file content

    Returns:
        FormatLevel enum value
    """
    # Check for QFMD markers (caret metadata + @end_field)
    has_caret_metadata = bool(re.search(r'^\^(question|type|identifier)', content, re.MULTILINE))
    has_field_markers = bool(re.search(r'^@field:', content, re.MULTILINE))
    has_end_field = bool(re.search(r'^@end_field', content, re.MULTILINE))

    if has_caret_metadata and has_field_markers and has_end_field:
        return FormatLevel.QFMD

    # Check for legacy syntax markers (old @ syntax with colon)
    has_at_metadata = bool(re.search(r'^@(question|type|identifier):', content, re.MULTILINE))

    if has_at_metadata and has_field_markers:
        return FormatLevel.LEGACY_SYNTAX

    # Check for semi-structured markers
    has_bold_type = bool(re.search(r'\*\*Type\*\*:', content, re.IGNORECASE))
    has_markdown_headers = bool(re.search(r'^##\s+(Question Text|Options|Answer|Feedback)', content, re.MULTILINE | re.IGNORECASE))

    if has_bold_type or has_markdown_headers:
        return FormatLevel.SEMI_STRUCTURED

    # Check for raw Swedish format
    has_raw_swedish = bool(re.search(r'\*\*(FRÅGA|RÄTT SVAR|FELAKTIGA):', content, re.IGNORECASE))

    if has_raw_swedish:
        return FormatLevel.UNSTRUCTURED

    # If has any question-like structure
    has_questions = bool(re.search(r'^#.*Q\d{3}|^#\s*Question\s*\d+', content, re.MULTILINE | re.IGNORECASE))

    if has_questions:
        return FormatLevel.SEMI_STRUCTURED

    return FormatLevel.UNKNOWN


def get_format_description(level: FormatLevel) -> str:
    """Get human-readable description of format level."""
    descriptions = {
        FormatLevel.QFMD: "QFMD format - ready for validation",
        FormatLevel.LEGACY_SYNTAX: "Legacy syntax - needs conversion to QFMD",
        FormatLevel.SEMI_STRUCTURED: "Semi-structured - needs formatting",
        FormatLevel.UNSTRUCTURED: "Unstructured - recommend M3 (Question Generation)",
        FormatLevel.UNKNOWN: "Unknown format - needs manual review"
    }
    return descriptions.get(level, "Unknown format")


def is_transformable(level: FormatLevel) -> bool:
    """Check if format can be transformed by Step 1."""
    return level == FormatLevel.LEGACY_SYNTAX
