"""
MCP Tool implementations for Step 1: Interactive Guided Build.

RFC-013 Architecture:
- Step 1 is a SAFETY NET for structural issues
- M5 should generate structurally correct output
- Step 1 catches: M5 bugs, file corruption, older formats, edge cases
- If M5 is perfect → Step 1 finds 0 issues

Key Features:
- YAML progress frontmatter in working file
- Question-by-question workflow with teacher approval
- Self-learning pattern system
- Decision logging for analytics
"""

import uuid
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from ..step1.session import Session, QuestionStatus
from ..step1.parser import parse_file, ParsedQuestion, get_question_by_id
from ..step1.detector import detect_format, FormatLevel, get_format_description
from ..step1.analyzer import analyze_question, get_auto_fixable_issues
from ..step1.transformer import transformer
from ..step1.prompts import format_issue_summary, get_prompt

# RFC-013 new modules
from ..step1.frontmatter import (
    add_frontmatter,
    update_frontmatter,
    remove_frontmatter,
    parse_frontmatter,
    has_frontmatter,
    create_progress_dict,
    update_progress,
)
from ..step1.patterns import (
    Pattern,
    load_patterns,
    save_patterns,
    find_pattern_for_issue,
    find_or_create_pattern,
    update_pattern_from_teacher_fix,
)
from ..step1.structural_issues import (
    StructuralIssue,
    detect_structural_issues,
    detect_separator_issues,
    categorize_issues,
)
from ..step1.decision_logger import (
    log_decision,
    log_session_start,
    log_session_complete,
    log_navigation,
)
from .session import get_current_session  # Step 0 session


# ════════════════════════════════════════════════════════════════════
# GLOBAL STATE
# ════════════════════════════════════════════════════════════════════

_step1_session: Optional[Session] = None
_parsed_questions: List[ParsedQuestion] = []
_patterns: List[Pattern] = []
_project_path: Optional[Path] = None


def get_step1_session() -> Optional[Session]:
    """Get current Step 1 session."""
    return _step1_session


def set_step1_session(session: Optional[Session]) -> None:
    """Set current Step 1 session."""
    global _step1_session
    _step1_session = session


# ════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════

def _get_working_file_path(project_path: Path) -> Path:
    """Get path to Step 1 working file in pipeline/ folder."""
    return project_path / "pipeline" / "step1_working.md"


def _ensure_pipeline_folder(project_path: Path) -> Path:
    """Ensure pipeline/ folder exists."""
    pipeline_dir = project_path / "pipeline"
    pipeline_dir.mkdir(parents=True, exist_ok=True)
    return pipeline_dir


def _get_question_display(question: ParsedQuestion, issues: List[StructuralIssue]) -> Dict[str, Any]:
    """Format question for display with issues."""
    return {
        "question_id": question.question_id,
        "title": question.title,
        "type": question.detected_type,
        "line_start": question.line_start,
        "line_end": question.line_end,
        "preview": question.raw_content[:500] + "..." if len(question.raw_content) > 500 else question.raw_content,
        "issues_count": len(issues),
        "issues": [
            {
                "type": i.issue_type,
                "severity": i.severity.value,
                "message": i.message,
                "line": i.line_number,
                "fix_suggestion": i.fix_suggestion,
                "auto_fixable": i.auto_fixable
            }
            for i in issues
        ]
    }


def _get_ai_suggestions(
    issues: List[StructuralIssue],
    patterns: List[Pattern],
    question_type: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], List[Pattern]]:
    """
    Get AI suggestions for issues based on learned patterns.

    Uses dynamic pattern creation: if no pattern exists for an issue,
    a new tentative pattern is created with low confidence.

    Args:
        issues: List of structural issues
        patterns: List of existing patterns
        question_type: Type of question (for pattern creation)

    Returns:
        Tuple of (suggestions, new_patterns_created)
    """
    suggestions = []
    new_patterns = []

    for issue in issues:
        # Try to find existing pattern, or create new one
        pattern, is_new = find_or_create_pattern(
            patterns=patterns,
            error_message=issue.message,
            error_field=getattr(issue, 'field', None),
            question_type=question_type
        )

        if is_new:
            new_patterns.append(pattern)
            # Add to patterns list for future lookups in this session
            patterns.append(pattern)

        suggestion = {
            "issue_type": issue.issue_type,
            "message": issue.message,
            "fix_suggestion": pattern.fix_suggestion if pattern else issue.fix_suggestion,
            "auto_fixable": issue.auto_fixable,
            "pattern_id": pattern.pattern_id if pattern else None,
            "confidence": pattern.confidence if pattern else 0.3,
            "learned_from": pattern.learned_from if pattern else 0,
            "is_new_pattern": is_new
        }
        suggestions.append(suggestion)

    return suggestions, new_patterns


# ════════════════════════════════════════════════════════════════════
# MCP TOOLS - RFC-013 SPEC
# ════════════════════════════════════════════════════════════════════

async def step1_start(
    project_path: Optional[str] = None,
    source_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Initialize Step 1 session.

    RFC-013 Flow:
    1. Load source (default: questions/m5_output.md or working_file from Step 0)
    2. Add YAML frontmatter for progress tracking
    3. Copy to pipeline/step1_working.md
    4. Parse questions, detect structural issues
    5. Return session info + first question

    Args:
        project_path: Path to project (uses Step 0 session if not provided)
        source_file: Override source file path

    Returns:
        Session info with first question and structural issues
    """
    global _step1_session, _parsed_questions, _patterns, _project_path

    # Get project path from Step 0 session or argument
    step0_session = get_current_session()

    if step0_session and not project_path:
        status = step0_session.get_status()
        project_path = status.get('project_path')
        if not source_file:
            source_file = status.get('working_file')

    if not project_path:
        return {
            "error": "Ingen projekt-sökväg angiven",
            "recommendation": "Kör step0_start först, eller ange project_path"
        }

    _project_path = Path(project_path)

    # Determine source file
    if not source_file:
        # Try common locations
        m5_output = _project_path / "questions" / "m5_output.md"
        questions_md = _project_path / "questions" / "questions.md"

        if m5_output.exists():
            source_file = str(m5_output)
        elif questions_md.exists():
            source_file = str(questions_md)
        else:
            return {
                "error": "Ingen källfil hittad",
                "tried": [str(m5_output), str(questions_md)],
                "recommendation": "Ange source_file eller kör M5 först"
            }

    source_path = Path(source_file)
    if not source_path.exists():
        return {"error": f"Fil ej hittad: {source_file}"}

    # Read source content
    content = source_path.read_text(encoding='utf-8')

    # Detect format
    format_level = detect_format(content)

    # Parse questions
    questions = parse_file(content)

    if not questions:
        return {
            "error": "Inga frågor hittades",
            "format": format_level.value,
            "recommendation": "Kontrollera att filen innehåller frågor med # Q001 headers"
        }

    _parsed_questions = questions

    # Create session
    session_id = str(uuid.uuid4())[:8]
    _step1_session = Session.create_new(source_file, str(_project_path / "pipeline"))
    _step1_session.session_id = session_id
    _step1_session.total_questions = len(questions)
    _step1_session.detected_format = format_level.value

    # Initialize question status
    _step1_session.questions = [
        QuestionStatus(question_id=q.question_id, status='pending')
        for q in questions
    ]

    # Load patterns for self-learning
    _patterns = load_patterns(_project_path)

    # Create progress frontmatter
    progress = create_progress_dict(
        session_id=session_id,
        total_questions=len(questions),
        current_question=1,
        current_question_id=questions[0].question_id
    )

    # Add frontmatter to content
    content_with_fm = add_frontmatter(content, progress)

    # Ensure pipeline/ folder exists
    _ensure_pipeline_folder(_project_path)

    # Save to working file
    working_file = _get_working_file_path(_project_path)
    working_file.write_text(content_with_fm, encoding='utf-8')
    _step1_session.working_file = str(working_file)

    # Log session start
    log_session_start(
        project_path=_project_path,
        session_id=session_id,
        source_file=source_file,
        total_questions=len(questions),
        detected_format=format_level.value
    )

    # Analyze first question for structural issues
    first_q = questions[0]
    structural_issues = detect_structural_issues(first_q.raw_content, first_q.question_id)

    # Also check separators (needs full content)
    separator_issues = detect_separator_issues(content, questions)
    first_q_sep_issues = [i for i in separator_issues if first_q.question_id in i.message]

    all_issues = structural_issues + first_q_sep_issues
    ai_suggestions, new_patterns = _get_ai_suggestions(
        all_issues, _patterns, question_type=first_q.detected_type
    )

    # Save new patterns immediately (they'll have low confidence until teacher confirms)
    if new_patterns:
        save_patterns(_project_path, _patterns)

    return {
        "session_id": session_id,
        "source_file": source_file,
        "working_file": str(working_file),
        "format": format_level.value,
        "format_description": get_format_description(format_level),
        "total_questions": len(questions),
        "current_question": _get_question_display(first_q, all_issues),
        "ai_suggestions": ai_suggestions,
        "patterns_loaded": len(_patterns),
        "new_patterns_created": len(new_patterns),
        "message": f"Session startad! {len(questions)} frågor, {len(all_issues)} strukturella problem i första frågan.",
        "next_action": "step1_apply_fix" if all_issues else "step1_next"
    }


async def step1_status() -> Dict[str, Any]:
    """
    Get current session status.

    Returns progress from frontmatter in working file.
    """
    if not _step1_session or not _project_path:
        return {"error": "Ingen aktiv session. Kör step1_start först."}

    working_file = _get_working_file_path(_project_path)

    if not working_file.exists():
        return {"error": "Working file saknas"}

    content = working_file.read_text(encoding='utf-8')
    frontmatter = parse_frontmatter(content)

    if not frontmatter or "step1_progress" not in frontmatter:
        return {"error": "Frontmatter saknas i working file"}

    progress = frontmatter["step1_progress"]

    return {
        "session_id": progress.get("session_id"),
        "status": progress.get("status"),
        "total_questions": progress.get("total_questions"),
        "current_question": progress.get("current_question"),
        "current_question_id": progress.get("current_question_id"),
        "questions_completed": progress.get("questions_completed", 0),
        "questions_skipped": progress.get("questions_skipped", 0),
        "questions_deleted": progress.get("questions_deleted", 0),
        "issues_fixed": progress.get("issues_fixed", 0),
        "started_at": progress.get("started_at"),
        "last_updated": progress.get("last_updated"),
        "progress_percent": round(
            (progress.get("questions_completed", 0) / progress.get("total_questions", 1)) * 100, 1
        ),
        "working_file": str(working_file)
    }


async def step1_navigate(direction: str = "next") -> Dict[str, Any]:
    """
    Navigate between questions.

    Args:
        direction: "next", "previous", or question_id (e.g., "Q007")

    Returns:
        Current question with structural issues and AI suggestions
    """
    if not _step1_session or not _project_path:
        return {"error": "Ingen aktiv session"}

    working_file = _get_working_file_path(_project_path)
    content = working_file.read_text(encoding='utf-8')

    # Parse frontmatter
    frontmatter = parse_frontmatter(content)
    if not frontmatter:
        return {"error": "Frontmatter saknas"}

    progress = frontmatter.get("step1_progress", {})
    current_idx = progress.get("current_question", 1) - 1  # 0-indexed

    # Re-parse questions from content without frontmatter
    content_body = remove_frontmatter(content) if has_frontmatter(content) else content
    questions = parse_file(content_body)

    if not questions:
        return {"error": "Inga frågor hittade i working file"}

    # Calculate new index
    old_idx = current_idx
    old_question_id = progress.get("current_question_id", "Q001")

    if direction == "next":
        new_idx = min(current_idx + 1, len(questions) - 1)
    elif direction == "previous":
        new_idx = max(current_idx - 1, 0)
    else:
        # Assume it's a question_id
        new_idx = next(
            (i for i, q in enumerate(questions) if q.question_id == direction),
            current_idx
        )

    new_question = questions[new_idx]

    # Update frontmatter
    content = update_progress(
        content,
        current_question=new_idx + 1,
        current_question_id=new_question.question_id
    )
    working_file.write_text(content, encoding='utf-8')

    # Log navigation
    log_navigation(
        project_path=_project_path,
        session_id=progress.get("session_id", "unknown"),
        from_question=old_question_id,
        to_question=new_question.question_id,
        direction=direction
    )

    # Analyze new question
    structural_issues = detect_structural_issues(new_question.raw_content, new_question.question_id)
    separator_issues = detect_separator_issues(content_body, questions)
    q_sep_issues = [i for i in separator_issues if new_question.question_id in i.message]

    all_issues = structural_issues + q_sep_issues
    ai_suggestions, new_patterns = _get_ai_suggestions(
        all_issues, _patterns, question_type=new_question.detected_type
    )

    # Save new patterns immediately
    if new_patterns:
        save_patterns(_project_path, _patterns)

    return {
        "navigated_from": old_question_id,
        "navigated_to": new_question.question_id,
        "position": f"{new_idx + 1} av {len(questions)}",
        "current_question": _get_question_display(new_question, all_issues),
        "ai_suggestions": ai_suggestions,
        "new_patterns_created": len(new_patterns),
        "next_action": "step1_apply_fix" if all_issues else "step1_next"
    }


# Aliases for RFC-013 tool names
async def step1_next() -> Dict[str, Any]:
    """Move to next question."""
    return await step1_navigate("next")


async def step1_previous() -> Dict[str, Any]:
    """Move to previous question."""
    return await step1_navigate("previous")


async def step1_jump(question_id: str) -> Dict[str, Any]:
    """Jump to specific question."""
    return await step1_navigate(question_id)


async def step1_analyze_question(question_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze current or specified question for STRUCTURAL issues.

    Only detects structural issues that Step 1 should fix.
    Pedagogical issues are reported but should go to M5.

    Args:
        question_id: Question to analyze (default: current)

    Returns:
        Structural issues with AI suggestions
    """
    if not _step1_session or not _project_path:
        return {"error": "Ingen aktiv session"}

    working_file = _get_working_file_path(_project_path)
    content = working_file.read_text(encoding='utf-8')

    # Get current question from frontmatter
    frontmatter = parse_frontmatter(content)
    progress = frontmatter.get("step1_progress", {}) if frontmatter else {}

    # Parse questions
    content_body = remove_frontmatter(content) if has_frontmatter(content) else content
    questions = parse_file(content_body)

    # Find target question
    target_id = question_id or progress.get("current_question_id", "Q001")
    question = get_question_by_id(questions, target_id)

    if not question:
        return {"error": f"Fråga ej hittad: {target_id}"}

    # Detect structural issues
    structural_issues = detect_structural_issues(question.raw_content, question.question_id)

    # Detect separator issues
    separator_issues = detect_separator_issues(content_body, questions)
    q_sep_issues = [i for i in separator_issues if question.question_id in i.message]

    all_structural = structural_issues + q_sep_issues

    # Also run legacy analyzer to catch pedagogical issues
    legacy_issues = analyze_question(question.raw_content, question.detected_type)
    structural_legacy, pedagogical, mechanical = categorize_issues(legacy_issues)

    # Get AI suggestions for structural issues (with dynamic pattern creation)
    ai_suggestions, new_patterns = _get_ai_suggestions(
        all_structural, _patterns, question_type=question.detected_type
    )

    # Save new patterns immediately
    if new_patterns:
        save_patterns(_project_path, _patterns)

    return {
        "question_id": target_id,
        "question_type": question.detected_type,
        "structural_issues": [
            {
                "type": i.issue_type,
                "severity": i.severity.value,
                "message": i.message,
                "line": i.line_number,
                "fix_suggestion": i.fix_suggestion,
                "auto_fixable": i.auto_fixable
            }
            for i in all_structural
        ],
        "structural_count": len(all_structural),
        "pedagogical_issues": [
            {
                "message": getattr(i, 'message', str(i)),
                "field": getattr(i, 'field', None)
            }
            for i in pedagogical
        ],
        "pedagogical_count": len(pedagogical),
        "ai_suggestions": ai_suggestions,
        "instruction": (
            f"{len(all_structural)} strukturella problem (Step 1 fixar), "
            f"{len(pedagogical)} pedagogiska (M5 fixar)"
        ),
        "next_action": (
            "step1_apply_fix" if all_structural else
            ("route_to_m5" if pedagogical else "step1_next")
        )
    }


async def step1_apply_fix(
    question_id: str,
    issue_type: str,
    action: str,
    fix_content: Optional[str] = None,
    teacher_note: Optional[str] = None
) -> Dict[str, Any]:
    """
    Apply a teacher-approved fix.

    RFC-013 Workflow:
    1. Apply fix to working file
    2. Update frontmatter (issues_fixed counter)
    3. Log decision to step1_decisions.jsonl
    4. Update pattern confidence
    5. Save updated patterns

    Args:
        question_id: Question being fixed
        issue_type: Type of structural issue
        action: "accept_ai", "modify", "manual", "skip"
        fix_content: Content for "modify" or "manual" actions
        teacher_note: Optional teacher reasoning

    Returns:
        Confirmation with updated question
    """
    global _patterns

    if not _step1_session or not _project_path:
        return {"error": "Ingen aktiv session"}

    working_file = _get_working_file_path(_project_path)
    content = working_file.read_text(encoding='utf-8')

    # Get session info from frontmatter
    frontmatter = parse_frontmatter(content)
    progress = frontmatter.get("step1_progress", {}) if frontmatter else {}
    session_id = progress.get("session_id", "unknown")

    # Parse questions
    content_body = remove_frontmatter(content) if has_frontmatter(content) else content
    questions = parse_file(content_body)

    question = get_question_by_id(questions, question_id)
    if not question:
        return {"error": f"Fråga ej hittad: {question_id}"}

    # Find the pattern for this issue
    pattern = find_pattern_for_issue(_patterns, issue_type)

    # Build AI suggestion for logging
    ai_suggestion = {
        "issue_type": issue_type,
        "fix_suggestion": pattern.fix_suggestion if pattern else "Ingen AI-förslag",
        "confidence": pattern.confidence if pattern else 0.5
    }

    # Apply fix based on action
    applied_fix = None
    fix_success = False

    if action == "accept_ai":
        # Apply auto-fix using transformer
        new_content, changes = transformer.apply_all_auto(question.raw_content)
        if changes:
            content_body = content_body.replace(question.raw_content, new_content)
            applied_fix = {"action": "auto_transform", "changes": changes}
            fix_success = True

    elif action == "modify" and fix_content:
        # Apply modified content from teacher
        content_body = content_body.replace(question.raw_content, fix_content)
        applied_fix = {"action": "teacher_modified", "content": fix_content[:100]}
        fix_success = True

    elif action == "manual" and fix_content:
        # Apply teacher's manual fix
        content_body = content_body.replace(question.raw_content, fix_content)
        applied_fix = {"action": "teacher_manual", "content": fix_content[:100]}
        fix_success = True

    elif action == "skip":
        applied_fix = {"action": "skipped"}
        # Don't update issues_fixed for skip

    # Update pattern statistics
    if pattern and action in ["accept_ai", "modify", "manual"]:
        pattern.update_stats(action)

    # Log decision
    log_decision(
        project_path=_project_path,
        session_id=session_id,
        question_id=question_id,
        issue_type=issue_type,
        issue_description=f"Structural issue: {issue_type}",
        line_number=question.line_start,
        ai_suggestion=ai_suggestion,
        teacher_decision=action,
        applied_fix=applied_fix,
        teacher_note=teacher_note,
        pattern_id=pattern.pattern_id if pattern else None
    )

    # Update frontmatter
    issues_fixed = progress.get("issues_fixed", 0)
    if fix_success:
        issues_fixed += 1

    # Rebuild content with updated frontmatter
    content = add_frontmatter(content_body, frontmatter)
    content = update_progress(content, issues_fixed=issues_fixed)

    # Save working file
    working_file.write_text(content, encoding='utf-8')

    # Save updated patterns
    save_patterns(_project_path, _patterns)

    # Re-analyze question
    new_questions = parse_file(content_body)
    new_question = get_question_by_id(new_questions, question_id)
    remaining_issues = detect_structural_issues(new_question.raw_content, question_id) if new_question else []

    return {
        "question_id": question_id,
        "action": action,
        "success": fix_success,
        "applied_fix": applied_fix,
        "pattern_updated": pattern.pattern_id if pattern else None,
        "pattern_confidence": pattern.confidence if pattern else None,
        "remaining_issues": len(remaining_issues),
        "issues_fixed_total": issues_fixed,
        "message": f"Fix applicerad på {question_id}" if fix_success else f"Hoppade över {issue_type}",
        "next_action": "step1_apply_fix" if remaining_issues else "step1_next"
    }


async def step1_skip(
    question_id: Optional[str] = None,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Skip current question entirely.

    Args:
        question_id: Question to skip (default: current)
        reason: Reason for skipping

    Returns:
        Confirmation and next question
    """
    if not _step1_session or not _project_path:
        return {"error": "Ingen aktiv session"}

    working_file = _get_working_file_path(_project_path)
    content = working_file.read_text(encoding='utf-8')

    frontmatter = parse_frontmatter(content)
    progress = frontmatter.get("step1_progress", {}) if frontmatter else {}

    target_id = question_id or progress.get("current_question_id", "Q001")

    # Update skip count
    skipped = progress.get("questions_skipped", 0) + 1

    content = update_progress(content, questions_skipped=skipped)
    working_file.write_text(content, encoding='utf-8')

    # Log decision
    log_decision(
        project_path=_project_path,
        session_id=progress.get("session_id", "unknown"),
        question_id=target_id,
        issue_type="skip_question",
        issue_description=f"Hoppade över hela frågan: {reason or 'Ingen anledning'}",
        line_number=None,
        ai_suggestion={},
        teacher_decision="skip",
        applied_fix={"action": "skipped_question"},
        teacher_note=reason
    )

    # Move to next
    result = await step1_navigate("next")
    result["skipped_question"] = target_id
    result["skip_reason"] = reason

    return result


async def step1_finish() -> Dict[str, Any]:
    """
    Complete Step 1 session.

    RFC-013 Flow:
    1. Remove frontmatter from working file
    2. Save final content to output/step1_complete.md
    3. Generate summary report
    4. Archive working files to pipeline/history/
    5. Save updated patterns
    """
    global _patterns

    if not _step1_session or not _project_path:
        return {"error": "Ingen aktiv session"}

    working_file = _get_working_file_path(_project_path)

    if not working_file.exists():
        return {"error": "Working file saknas"}

    content = working_file.read_text(encoding='utf-8')

    # Parse final frontmatter for stats
    frontmatter = parse_frontmatter(content)
    progress = frontmatter.get("step1_progress", {}) if frontmatter else {}

    # Remove frontmatter
    content_clean = remove_frontmatter(content)

    # Save to output/step1_complete.md
    output_dir = _project_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "step1_complete.md"
    output_file.write_text(content_clean, encoding='utf-8')

    # Archive working file
    history_dir = _project_path / "pipeline" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    archive_name = f"step1_working_{progress.get('session_id', 'unknown')}.md"
    shutil.copy(working_file, history_dir / archive_name)

    # Save patterns
    save_patterns(_project_path, _patterns)

    # Log completion
    log_session_complete(
        project_path=_project_path,
        session_id=progress.get("session_id", "unknown"),
        status="completed",
        questions_completed=progress.get("questions_completed", 0),
        questions_skipped=progress.get("questions_skipped", 0),
        questions_deleted=progress.get("questions_deleted", 0),
        issues_fixed=progress.get("issues_fixed", 0),
        patterns_updated=len([p for p in _patterns if p.learned_from > 0])
    )

    # Parse final questions for count
    final_questions = parse_file(content_clean)

    return {
        "session_id": progress.get("session_id"),
        "status": "completed",
        "output_file": str(output_file),
        "archived_to": str(history_dir / archive_name),
        "summary": {
            "total_questions": progress.get("total_questions", 0),
            "questions_completed": progress.get("questions_completed", 0),
            "questions_skipped": progress.get("questions_skipped", 0),
            "questions_deleted": progress.get("questions_deleted", 0),
            "issues_fixed": progress.get("issues_fixed", 0),
            "final_question_count": len(final_questions)
        },
        "patterns_learned": len([p for p in _patterns if p.learned_from > 0]),
        "message": "Step 1 klar! Kör step2_validate för validering.",
        "next_step": "step2_validate"
    }


# ════════════════════════════════════════════════════════════════════
# LEGACY TOOLS (kept for backwards compatibility)
# ════════════════════════════════════════════════════════════════════

async def step1_transform(question_id: Optional[str] = None) -> Dict[str, Any]:
    """
    [LEGACY] Apply all auto-fixable transforms at once.

    Use step1_apply_fix for RFC-013 interactive workflow.
    """
    if not _step1_session or not _project_path:
        return {"error": "Ingen aktiv session"}

    working_file = _get_working_file_path(_project_path)
    content = working_file.read_text(encoding='utf-8')

    # Remove frontmatter for transformation
    content_body = remove_frontmatter(content) if has_frontmatter(content) else content

    # Transform
    new_content, changes = transformer.apply_all_auto(content_body)

    if not changes:
        return {"changes": [], "message": "Inga automatiska fixar att applicera"}

    # Re-add frontmatter
    frontmatter = parse_frontmatter(content)
    if frontmatter:
        new_content = add_frontmatter(new_content, frontmatter)

    working_file.write_text(new_content, encoding='utf-8')

    return {
        "changes": changes,
        "message": f"Applicerade {len(changes)} transformationer",
        "next_step": "Kör step2_validate för att verifiera"
    }


async def step1_preview(lines: int = 50) -> Dict[str, Any]:
    """Preview working file content."""
    if not _step1_session or not _project_path:
        return {"error": "Ingen aktiv session"}

    working_file = _get_working_file_path(_project_path)
    content = working_file.read_text(encoding='utf-8')

    all_lines = content.split('\n')
    preview_lines = all_lines[:lines]

    return {
        "file": str(working_file),
        "total_lines": len(all_lines),
        "showing": min(lines, len(all_lines)),
        "content": '\n'.join(preview_lines)
    }


# Keep old function names for backwards compatibility
async def step1_analyze(question_id: Optional[str] = None) -> Dict[str, Any]:
    """[LEGACY] Alias for step1_analyze_question."""
    return await step1_analyze_question(question_id)


async def step1_fix_auto(question_id: Optional[str] = None) -> Dict[str, Any]:
    """[LEGACY] Apply auto-fixes. Use step1_apply_fix(action='accept_ai') instead."""
    if not question_id and _step1_session:
        # Get current question from session
        frontmatter = parse_frontmatter(
            _get_working_file_path(_project_path).read_text(encoding='utf-8')
        ) if _project_path else None
        question_id = frontmatter.get("step1_progress", {}).get("current_question_id") if frontmatter else None

    if not question_id:
        return {"error": "Inget question_id"}

    return await step1_apply_fix(question_id, "auto_transform", "accept_ai")


async def step1_fix_manual(question_id: str, field: str, value: str) -> Dict[str, Any]:
    """[LEGACY] Apply manual fix. Use step1_apply_fix(action='manual') instead."""
    return await step1_apply_fix(question_id, field, "manual", fix_content=value)


async def step1_suggest(question_id: str, field: str) -> Dict[str, Any]:
    """[LEGACY] Get suggestion for field."""
    pattern = find_pattern_for_issue(_patterns, field) if _patterns else None

    return {
        "question_id": question_id,
        "field": field,
        "suggestion": pattern.fix_suggestion if pattern else None,
        "confidence": pattern.confidence if pattern else 0.5,
        "instruction": "Använd step1_apply_fix för att applicera"
    }


async def step1_batch_preview(issue_type: str) -> Dict[str, Any]:
    """[LEGACY] Preview questions with same issue."""
    return {"message": "Batch operations removed in RFC-013. Use question-by-question workflow."}


async def step1_batch_apply(issue_type: str, fix_type: str, question_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """[LEGACY] Batch apply removed in RFC-013."""
    return {"message": "Batch operations removed in RFC-013. Use step1_apply_fix for each question."}
