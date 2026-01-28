"""Step 1: Minimal Safety Net

Vision A Implementation (2026-01-28):
- Step 1 is used ONLY when Step 3 auto-fix fails
- Most files go: M5 → Step 2 → Step 3 → Step 4 (Step 1 skipped)
- Step 1 handles: unknown errors, Step 3 failures, structural issues

Archived modules (3200+ lines) → step1/_archived/
Kept modules (~520 lines): frontmatter, parser, decision_logger
"""

# Kept: Frontmatter management
from .frontmatter import (
    add_frontmatter,
    update_frontmatter,
    remove_frontmatter,
    parse_frontmatter,
    has_frontmatter,
    create_progress_dict,
    update_progress,
)

# Kept: Question parsing
from .parser import (
    parse_file,
    ParsedQuestion,
)

# Kept: Decision logging
from .decision_logger import (
    log_decision,
    log_session_start,
    log_session_complete,
    log_navigation,
)

__all__ = [
    # Frontmatter
    'add_frontmatter',
    'update_frontmatter',
    'remove_frontmatter',
    'parse_frontmatter',
    'has_frontmatter',
    'create_progress_dict',
    'update_progress',
    # Parsing
    'parse_file',
    'ParsedQuestion',
    # Decision logging
    'log_decision',
    'log_session_start',
    'log_session_complete',
    'log_navigation',
]

# =============================================================================
# ARCHIVED: The following were moved to step1/_archived/ on 2026-01-28
# =============================================================================
# - analyzer.py (458 lines) → Replaced by Step 2 validator
# - detector.py (78 lines) → Not needed
# - patterns.py (465 lines) → Step 3 has its own patterns
# - prompts.py (189 lines) → Simplified
# - session.py (136 lines) → SessionManager used instead
# - structural_issues.py (367 lines) → Replaced by pipeline_router
# - transformer.py (487 lines) → Replaced by Step 3 auto-fix
# - step1_tools.py (947 lines) → Replaced by minimal step1_tools.py
# =============================================================================
