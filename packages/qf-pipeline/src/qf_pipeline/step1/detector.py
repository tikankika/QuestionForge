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
    # Check for v6.5 markers (caret metadata + @end_field)
    has_caret_metadata = bool(re.search(r'^\^(question|type|identifier)', content, re.MULTILINE))
    has_field_markers = bool(re.search(r'^@field:', content, re.MULTILINE))
    has_end_field = bool(re.search(r'^@end_field', content, re.MULTILINE))

    if has_caret_metadata and has_field_markers and has_end_field:
        return FormatLevel.VALID_V65

    # Check for v6.3 markers (old @ syntax with colon)
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


def is_transformable(level: FormatLevel) -> bool:
    """Check if format can be transformed by Step 1."""
    return level == FormatLevel.OLD_SYNTAX_V63
