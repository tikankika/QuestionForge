"""MCP tools for qf-pipeline."""

from .session import (
    start_session_tool,
    get_session_status_tool,
    end_session_tool,
    load_session_tool,
    get_current_session,
    set_current_session,
)

from .step0_tools import (
    step0_add_file,
    step0_analyze,
)

from .step1_tools import (
    # NEW: Minimal Step 1 (Vision A)
    step1_review,
    step1_manual_fix,
    step1_delete,
    step1_skip,
    # DEPRECATED: Old tools (stubs for backwards compatibility)
    step1_start,
    step1_status,
    step1_navigate,
    step1_next,
    step1_previous,
    step1_jump,
    step1_analyze_question,
    step1_apply_fix,
    step1_finish,
    step1_analyze,
    step1_fix_auto,
    step1_fix_manual,
    step1_suggest,
    step1_batch_preview,
    step1_batch_apply,
    step1_transform,
    step1_preview,
    get_step1_session,
)

from .project_files import (
    read_project_file,
    write_project_file,
)

from .pipeline_router import (
    route_errors,
    RouteDecision,
    CategorizedError,
    ErrorCategory,
    format_route_decision,
)

__all__ = [
    # Session tools (Step 0)
    "start_session_tool",
    "get_session_status_tool",
    "end_session_tool",
    "load_session_tool",
    "get_current_session",
    "set_current_session",
    # Step 0 tools - ADR-015 Flexible Project Initialization
    "step0_add_file",
    "step0_analyze",
    # Step 1 tools - NEW MINIMAL (Vision A)
    "step1_review",
    "step1_manual_fix",
    "step1_delete",
    "step1_skip",
    # Step 1 tools - DEPRECATED (stubs)
    "step1_start",
    "step1_status",
    "step1_navigate",
    "step1_next",
    "step1_previous",
    "step1_jump",
    "step1_analyze_question",
    "step1_apply_fix",
    "step1_finish",
    "step1_analyze",
    "step1_fix_auto",
    "step1_fix_manual",
    "step1_suggest",
    "step1_batch_preview",
    "step1_batch_apply",
    "step1_transform",
    "step1_preview",
    "get_step1_session",
    # Project file tools
    "read_project_file",
    "write_project_file",
    # Pipeline router
    "route_errors",
    "RouteDecision",
    "CategorizedError",
    "ErrorCategory",
    "format_route_decision",
]
