"""Step 1: Guided Build - Convert to QFMD (QuestionForge Markdown) format.

RFC-013 Architecture:
- Step 1 is a SAFETY NET for structural issues
- M5 should generate structurally correct output
- Step 1 catches: M5 bugs, file corruption, older formats, edge cases
"""

from .session import Session, QuestionStatus, Change
from .detector import detect_format, FormatLevel, get_format_description
from .parser import parse_file, ParsedQuestion
from .analyzer import analyze_question, Issue, Severity
from .transformer import Transformer, transformer
from .prompts import get_prompt, format_issue_summary

# RFC-013 new modules
from .frontmatter import (
    add_frontmatter,
    update_frontmatter,
    remove_frontmatter,
    parse_frontmatter,
    has_frontmatter,
    create_progress_dict,
    update_progress,
)
from .patterns import (
    Pattern,
    load_patterns,
    save_patterns,
    find_pattern_for_issue,
    get_pattern_by_id,
    DEFAULT_PATTERNS,
)
from .structural_issues import (
    StructuralIssue,
    IssueSeverity,
    IssueCategory,
    detect_structural_issues,
    detect_separator_issues,
    categorize_issues,
    is_structural_issue,
    is_pedagogical_issue,
)
from .decision_logger import (
    log_decision,
    log_session_start,
    log_session_complete,
    log_navigation,
)

__all__ = [
    # Session management
    'Session',
    'QuestionStatus',
    'Change',
    # Format detection
    'detect_format',
    'FormatLevel',
    'get_format_description',
    # Parsing
    'parse_file',
    'ParsedQuestion',
    # Analysis (legacy)
    'analyze_question',
    'Issue',
    'Severity',
    # Transformation
    'Transformer',
    'transformer',
    # Prompts
    'get_prompt',
    'format_issue_summary',
    # RFC-013: Frontmatter
    'add_frontmatter',
    'update_frontmatter',
    'remove_frontmatter',
    'parse_frontmatter',
    'has_frontmatter',
    'create_progress_dict',
    'update_progress',
    # RFC-013: Self-learning patterns
    'Pattern',
    'load_patterns',
    'save_patterns',
    'find_pattern_for_issue',
    'get_pattern_by_id',
    'DEFAULT_PATTERNS',
    # RFC-013: Structural issues
    'StructuralIssue',
    'IssueSeverity',
    'IssueCategory',
    'detect_structural_issues',
    'detect_separator_issues',
    'categorize_issues',
    'is_structural_issue',
    'is_pedagogical_issue',
    # RFC-013: Decision logging
    'log_decision',
    'log_session_start',
    'log_session_complete',
    'log_navigation',
]
