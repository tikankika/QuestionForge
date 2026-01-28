"""MCP tools for qf-pipeline."""

from .session import (
    start_session_tool,
    get_session_status_tool,
    end_session_tool,
    load_session_tool,
    get_current_session,
    set_current_session,
)

from .step1_tools import (
    # RFC-013 core tools
    step1_start,
    step1_status,
    step1_navigate,
    step1_next,
    step1_previous,
    step1_jump,
    step1_analyze_question,
    step1_apply_fix,
    step1_skip,
    step1_finish,
    # Legacy tools (backwards compatibility)
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
    # Step 1 tools - RFC-013 core
    "step1_start",
    "step1_status",
    "step1_navigate",
    "step1_next",
    "step1_previous",
    "step1_jump",
    "step1_analyze_question",
    "step1_apply_fix",
    "step1_skip",
    "step1_finish",
    # Step 1 tools - Legacy (backwards compatibility)
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
