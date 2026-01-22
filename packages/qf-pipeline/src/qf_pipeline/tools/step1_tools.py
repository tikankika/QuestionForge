"""
MCP Tool implementations for Step 1: Guided Build.
Convert questions to QFMD (QuestionForge Markdown) format.
"""

from pathlib import Path
from typing import Optional, Dict, Any

from ..step1.session import Session, QuestionStatus
from ..step1.parser import parse_file, ParsedQuestion, get_question_by_id
from ..step1.detector import detect_format, FormatLevel, get_format_description, is_transformable
from ..step1.analyzer import analyze_question, get_auto_fixable_issues, count_issues_by_severity
from ..step1.transformer import transformer
from ..step1.prompts import format_issue_summary, format_progress, get_prompt, BLOOM_LEVELS, DIFFICULTY_LEVELS
from .session import get_current_session  # Step 0 session
import re
from typing import List


# Global session state
_step1_session: Optional[Session] = None
_parsed_questions: list = []


def get_step1_session() -> Optional[Session]:
    """Get current Step 1 session."""
    return _step1_session


def set_step1_session(session: Optional[Session]) -> None:
    """Set current Step 1 session."""
    global _step1_session
    _step1_session = session


# ════════════════════════════════════════════════════════════════════
# MCP TOOLS
# ════════════════════════════════════════════════════════════════════

async def step1_start(
    source_file: Optional[str] = None,
    output_folder: Optional[str] = None,
    project_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Start a new Step 1 session.

    Uses Step 0 session if available, otherwise requires source_file and output_folder.

    Args:
        source_file: Path to markdown file (optional if Step 0 session exists)
        output_folder: Directory for output files (optional if Step 0 session exists)
        project_name: Optional project name

    Returns:
        Session info and initial analysis
    """
    global _step1_session, _parsed_questions

    # Check for Step 0 session first
    step0_session = get_current_session()

    if step0_session:
        # Use Step 0 session paths
        status = step0_session.get_status()
        source_file = status.get('working_file')  # Use working copy from Step 0
        project_path = status.get('project_path')

        if not source_file or not project_path:
            return {"error": "Step 0 session saknar nödvändiga sökvägar"}

        # Output folder is 03_output within project structure
        output_folder = str(Path(project_path) / "03_output")
    else:
        # No Step 0 session - require explicit paths
        if not source_file or not output_folder:
            return {
                "error": "Ingen aktiv Step 0 session",
                "recommendation": "Kör step0_start först, eller ange source_file och output_folder"
            }

    # Validate source file
    source_path = Path(source_file)
    if not source_path.exists():
        return {"error": f"File not found: {source_file}"}

    if not source_path.suffix.lower() == '.md':
        return {"error": f"Not a markdown file: {source_file}"}

    # Create output folder
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    # Read file
    content = source_path.read_text(encoding='utf-8')

    # Detect format
    format_level = detect_format(content)
    format_warning = None

    # Accept ALL formats - only warn, don't reject
    if format_level == FormatLevel.UNSTRUCTURED:
        format_warning = {
            "level": "severe",
            "message": "Filen saknar tydlig struktur. Step 1 försöker ändå.",
            "recommendation": "Om många fel uppstår, överväg M1-M4 för att strukturera innehållet först."
        }
    elif format_level == FormatLevel.QFMD:
        # Already QFMD - still allow step1 to run for any remaining fixes
        format_warning = {
            "level": "info",
            "message": "Filen är redan i QFMD-format.",
            "recommendation": "Kör step2_validate direkt, eller fortsätt här för eventuella justeringar."
        }
    elif format_level == FormatLevel.SEMI_STRUCTURED:
        format_warning = {
            "level": "moderate",
            "message": "Filen är semi-strukturerad. Step 1 försöker fixa.",
            "recommendation": "Om många strukturella fel, överväg M3 för omgenerering."
        }

    # Parse questions
    questions = parse_file(content)

    if not questions:
        # If no questions found and format is problematic, give helpful guidance
        if format_level in [FormatLevel.UNSTRUCTURED, FormatLevel.UNKNOWN]:
            return {
                "error": "Inga frågor hittades i filen",
                "format": format_level.value,
                "recommendation": "Filen verkar sakna frågestruktur. Använd M3 (Question Generation) för att skapa frågor från ditt material.",
                "format_warning": format_warning
            }
        return {
            "error": "Inga frågor hittades i filen",
            "format": format_level.value,
            "recommendation": "Kontrollera att filen innehåller frågor med # Q001 eller liknande headers."
        }

    _parsed_questions = questions

    # Create session
    _step1_session = Session.create_new(source_file, output_folder)
    _step1_session.total_questions = len(questions)
    _step1_session.detected_format = format_level.value

    # Initialize question status
    _step1_session.questions = [
        QuestionStatus(question_id=q.question_id, status='pending')
        for q in questions
    ]

    # Copy source to working file
    working_path = Path(_step1_session.working_file)
    working_path.write_text(content, encoding='utf-8')

    # Save session
    session_file = output_path / f"step1_session_{_step1_session.session_id}.json"
    _step1_session.save(session_file)

    # Analyze first question
    first_question = questions[0]
    issues = analyze_question(first_question.raw_content, first_question.detected_type)
    _step1_session.questions[0].issues_found = len(issues)

    # Count total issues across all questions for severity assessment
    total_issues = 0
    severe_issues = 0
    for q in questions:
        q_issues = analyze_question(q.raw_content, q.detected_type)
        total_issues += len(q_issues)
        # Count severe issues (missing required fields)
        severe_issues += sum(1 for i in q_issues if hasattr(i, 'severity') and i.severity.value == 'error')

    # Build recommendation based on issue count
    if severe_issues > len(questions) * 3:  # More than 3 severe issues per question on average
        m1m4_recommendation = f"Filen har {severe_issues} allvarliga problem. Överväg M1-M4 för bättre struktur."
    else:
        m1m4_recommendation = None

    return {
        "session_id": _step1_session.session_id,
        "source_file": source_file,
        "working_file": _step1_session.working_file,
        "format": format_level.value,
        "format_description": get_format_description(format_level),
        "format_warning": format_warning,
        "total_questions": len(questions),
        "total_issues": total_issues,
        "severe_issues": severe_issues,
        "m1m4_recommendation": m1m4_recommendation,
        "first_question": {
            "id": first_question.question_id,
            "title": first_question.title,
            "type": first_question.detected_type,
            "line_start": first_question.line_start,
            "issues_count": len(issues),
            "auto_fixable": len(get_auto_fixable_issues(issues)),
            "issues_summary": format_issue_summary(issues)
        },
        "message": f"Session started! {len(questions)} frågor hittades. Kör step1_analyze eller step1_transform för att fixa."
    }


async def step1_status() -> Dict[str, Any]:
    """
    Get current session status.

    Returns:
        Session progress and statistics
    """
    if not _step1_session:
        return {"error": "No active session. Use step1_start first."}

    progress = _step1_session.get_progress()
    current = _step1_session.get_current_question()

    return {
        "session_id": _step1_session.session_id,
        "progress": progress,
        "progress_display": format_progress(progress),
        "current_question": current.question_id if current else None,
        "format": _step1_session.detected_format,
        "changes_made": len(_step1_session.changes),
        "working_file": _step1_session.working_file
    }


async def step1_analyze(question_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a question and return categorized issues.

    Args:
        question_id: Question to analyze (default: current)

    Returns:
        Categorized issues: auto_fixable and needs_input
    """
    if not _step1_session:
        return {"error": "No active session"}

    # Read working file
    working_path = Path(_step1_session.working_file)
    content = working_path.read_text(encoding='utf-8')

    # Parse and find question
    questions = parse_file(content)

    target_id = question_id or _step1_session.questions[_step1_session.current_index].question_id
    question = get_question_by_id(questions, target_id)

    if not question:
        return {"error": f"Question not found: {target_id}"}

    # Analyze
    issues = analyze_question(question.raw_content, question.detected_type)
    counts = count_issues_by_severity(issues)

    # Categorize issues
    auto_fixable = [i for i in issues if i.auto_fixable]
    needs_input = [i for i in issues if not i.auto_fixable and i.prompt_key]
    other = [i for i in issues if not i.auto_fixable and not i.prompt_key]

    return {
        "question_id": target_id,
        "question_type": question.detected_type,
        "question_title": question.title,
        "question_preview": question.raw_content[:300] + "..." if len(question.raw_content) > 300 else question.raw_content,
        "total_issues": len(issues),
        "by_severity": counts,

        # Categorized issues
        "auto_fixable": [
            {
                "id": idx,
                "field": i.field,
                "message": i.message,
                "transform_id": i.transform_id
            }
            for idx, i in enumerate(auto_fixable)
        ],
        "auto_fixable_count": len(auto_fixable),

        "needs_input": [
            {
                "id": idx,
                "field": i.field,
                "message": i.message,
                "prompt_key": i.prompt_key,
                "current_value": i.current_value,
                "prompt": get_prompt(i.prompt_key) if i.prompt_key else None
            }
            for idx, i in enumerate(needs_input)
        ],
        "needs_input_count": len(needs_input),

        "other_issues": [
            {
                "id": idx,
                "field": i.field,
                "message": i.message,
                "severity": i.severity.value
            }
            for idx, i in enumerate(other)
        ],

        # Instructions for Claude
        "instruction": (
            f"{len(auto_fixable)} auto-fixable (kör step1_fix_auto), "
            f"{len(needs_input)} kräver input (fråga användaren), "
            f"{len(other)} övriga"
        ) if issues else "Inga problem hittades!",

        "next_action": "step1_fix_auto" if auto_fixable else ("ask_user" if needs_input else "step1_next")
    }


async def step1_transform(question_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Apply all auto-fixable transforms to a question or all questions.

    Args:
        question_id: Question to fix (default: all questions)

    Returns:
        List of changes made
    """
    if not _step1_session:
        return {"error": "No active session"}

    # Read working file
    working_path = Path(_step1_session.working_file)
    content = working_path.read_text(encoding='utf-8')

    if question_id:
        # Transform single question
        questions = parse_file(content)
        question = get_question_by_id(questions, question_id)

        if not question:
            return {"error": f"Question not found: {question_id}"}

        new_content, changes = transformer.apply_all_auto(question.raw_content)

        if not changes:
            return {
                "question_id": question_id,
                "changes": [],
                "message": "Inga automatiska fixar att applicera"
            }

        # Update file
        full_content = content.replace(question.raw_content, new_content)
        working_path.write_text(full_content, encoding='utf-8')

        # Log changes
        for change_desc in changes:
            _step1_session.add_change(
                question_id=question_id,
                field='auto',
                old_value=None,
                new_value=change_desc,
                change_type='auto'
            )

        return {
            "question_id": question_id,
            "changes": changes,
            "message": f"Applicerade {len(changes)} automatiska fixar på {question_id}"
        }
    else:
        # Transform entire file
        new_content, changes = transformer.apply_all_auto(content)

        if not changes:
            return {
                "changes": [],
                "message": "Inga automatiska fixar att applicera"
            }

        # Write transformed content
        working_path.write_text(new_content, encoding='utf-8')

        # Log changes
        for change_desc in changes:
            _step1_session.add_change(
                question_id='ALL',
                field='auto',
                old_value=None,
                new_value=change_desc,
                change_type='auto'
            )

        # Mark all questions as completed
        for q in _step1_session.questions:
            q.status = 'completed'

        return {
            "changes": changes,
            "questions_processed": len(_step1_session.questions),
            "message": f"Applicerade {len(changes)} transformationer på hela filen",
            "next_step": "Kör step2_validate för att verifiera resultatet"
        }


async def step1_next(direction: str = "forward") -> Dict[str, Any]:
    """
    Move to next/previous question.

    Args:
        direction: "forward", "back", or question_id

    Returns:
        New current question info with analysis
    """
    if not _step1_session:
        return {"error": "No active session"}

    if direction == "forward":
        if _step1_session.current_index < len(_step1_session.questions) - 1:
            _step1_session.current_index += 1
    elif direction == "back":
        if _step1_session.current_index > 0:
            _step1_session.current_index -= 1
    else:
        # Assume it's a question_id
        for i, q in enumerate(_step1_session.questions):
            if q.question_id == direction:
                _step1_session.current_index = i
                break

    current = _step1_session.get_current_question()
    progress = _step1_session.get_progress()

    # Analyze current question (like step1_start does for first question)
    issues = analyze_question(current.raw_content, current.detected_type)
    auto_fixable = get_auto_fixable_issues(issues)

    return {
        "current_question": current.question_id,
        "current_index": _step1_session.current_index,
        "total_questions": len(_step1_session.questions),
        "question_type": current.detected_type,
        "question_title": current.title,
        "issues_count": len(issues),
        "auto_fixable": len(auto_fixable),
        "issues_summary": format_issue_summary(issues),
        "position": f"{progress['current']} av {progress['total']}",
        "progress": progress
    }


async def step1_preview(lines: int = 50) -> Dict[str, Any]:
    """
    Preview the working file content.

    Args:
        lines: Number of lines to show (default: 50)

    Returns:
        File content preview
    """
    if not _step1_session:
        return {"error": "No active session"}

    working_path = Path(_step1_session.working_file)
    content = working_path.read_text(encoding='utf-8')

    all_lines = content.split('\n')
    preview_lines = all_lines[:lines]

    return {
        "file": _step1_session.working_file,
        "total_lines": len(all_lines),
        "showing": min(lines, len(all_lines)),
        "content": '\n'.join(preview_lines)
    }


async def step1_finish() -> Dict[str, Any]:
    """
    Finish Step 1 and generate report.

    Returns:
        Summary report
    """
    if not _step1_session:
        return {"error": "No active session"}

    progress = _step1_session.get_progress()

    # Count questions by status
    completed = [q for q in _step1_session.questions if q.status == 'completed']
    skipped = [q for q in _step1_session.questions if q.status == 'skipped']
    pending = [q for q in _step1_session.questions if q.status == 'pending']
    warnings = [q for q in _step1_session.questions if q.status == 'has_warnings']

    # Save final session state
    output_path = Path(_step1_session.output_folder)
    session_file = output_path / f"step1_session_{_step1_session.session_id}_final.json"
    _step1_session.save(session_file)

    ready = len(pending) == 0 and len(skipped) == 0

    return {
        "session_id": _step1_session.session_id,
        "working_file": _step1_session.working_file,
        "summary": {
            "total_questions": _step1_session.total_questions,
            "completed": len(completed),
            "skipped": len(skipped),
            "pending": len(pending),
            "with_warnings": len(warnings),
            "total_changes": len(_step1_session.changes)
        },
        "changes": [
            {"question": c.question_id, "description": c.new_value}
            for c in _step1_session.changes[:10]  # Show first 10
        ],
        "skipped_questions": [q.question_id for q in skipped],
        "ready_for_step2": ready,
        "next_action": "Kör step2_validate på working_file" if ready else f"Fixa {len(pending)} väntande frågor först"
    }


# ════════════════════════════════════════════════════════════════════
# INTERACTIVE TOOLS (NEW)
# ════════════════════════════════════════════════════════════════════

async def step1_fix_auto(question_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Apply ONLY auto-fixable transforms to a question.
    Returns remaining issues that need user input.

    Args:
        question_id: Question to fix (default: current)

    Returns:
        What was fixed and what remains
    """
    if not _step1_session:
        return {"error": "No active session"}

    # Read working file
    working_path = Path(_step1_session.working_file)
    content = working_path.read_text(encoding='utf-8')

    # Parse and find question
    questions = parse_file(content)

    target_id = question_id or _step1_session.questions[_step1_session.current_index].question_id
    question = get_question_by_id(questions, target_id)

    if not question:
        return {"error": f"Question not found: {target_id}"}

    # Apply auto transforms
    new_content, changes = transformer.apply_all_auto(question.raw_content)

    if changes:
        # Update file
        full_content = content.replace(question.raw_content, new_content)
        working_path.write_text(full_content, encoding='utf-8')

        # Log changes
        for change_desc in changes:
            _step1_session.add_change(
                question_id=target_id,
                field='auto',
                old_value=None,
                new_value=change_desc,
                change_type='auto'
            )

    # Re-analyze to see what remains
    updated_content = working_path.read_text(encoding='utf-8')
    updated_questions = parse_file(updated_content)
    updated_question = get_question_by_id(updated_questions, target_id)

    remaining_issues = analyze_question(updated_question.raw_content, updated_question.detected_type) if updated_question else []
    needs_input = [i for i in remaining_issues if not i.auto_fixable and i.prompt_key]

    return {
        "question_id": target_id,
        "fixed": changes,
        "fixed_count": len(changes),

        # What remains and needs input
        "remaining": [
            {
                "field": i.field,
                "message": i.message,
                "prompt_key": i.prompt_key,
                "prompt": get_prompt(i.prompt_key) if i.prompt_key else None
            }
            for i in needs_input
        ],
        "remaining_count": len(needs_input),

        # Instruction for Claude
        "instruction": (
            f"Fixade {len(changes)} auto-issues. "
            f"{len(needs_input)} kräver användarinput."
            if needs_input else
            "Alla issues fixade! Kör step1_next() för nästa fråga."
        ),
        "next_action": "ask_user" if needs_input else "step1_next"
    }


async def step1_fix_manual(
    question_id: str,
    field: str,
    value: str
) -> Dict[str, Any]:
    """
    Apply a single manual fix based on user input.

    Args:
        question_id: Question ID
        field: Field to update (bloom, difficulty, partial_feedback, etc.)
        value: Value from user

    Returns:
        Confirmation of change
    """
    if not _step1_session:
        return {"error": "No active session"}

    working_path = Path(_step1_session.working_file)
    content = working_path.read_text(encoding='utf-8')
    questions = parse_file(content)

    question = get_question_by_id(questions, question_id)
    if not question:
        return {"error": f"Question not found: {question_id}"}

    new_content = question.raw_content
    success = False

    # Handle different field types
    if field == "bloom":
        # Add Bloom level to ^tags
        new_content = _add_to_tags(new_content, f"#Bloom:{value}")
        success = True

    elif field == "difficulty":
        # Add difficulty to ^tags
        new_content = _add_to_tags(new_content, f"#{value}")
        success = True

    elif field == "partial_feedback":
        # Add partial_feedback subfield
        new_content = _add_feedback_subfield(new_content, "partial_feedback", value)
        success = True

    elif field == "correct_answers":
        # Add correct_answers for multiple_response
        new_content = _add_correct_answers(new_content, value)
        success = True

    elif field == "identifier":
        # Update ^identifier
        new_content = re.sub(
            r'\^identifier\s+\w+',
            f'^identifier {value}',
            new_content
        )
        success = True

    else:
        return {"error": f"Unknown field: {field}"}

    if success and new_content != question.raw_content:
        # Update file
        full_content = content.replace(question.raw_content, new_content)
        working_path.write_text(full_content, encoding='utf-8')

        # Log change
        _step1_session.add_change(
            question_id=question_id,
            field=field,
            old_value=None,
            new_value=value,
            change_type='user_input'
        )

        return {
            "question_id": question_id,
            "field": field,
            "value": value,
            "success": True,
            "message": f"Uppdaterade {field} för {question_id}"
        }

    return {
        "question_id": question_id,
        "field": field,
        "success": False,
        "message": "Ingen ändring gjordes"
    }


async def step1_suggest(
    question_id: str,
    field: str
) -> Dict[str, Any]:
    """
    Generate a suggestion for a field based on context.

    Args:
        question_id: Question ID
        field: Field to suggest value for

    Returns:
        Suggestion that user can accept/modify
    """
    if not _step1_session:
        return {"error": "No active session"}

    working_path = Path(_step1_session.working_file)
    content = working_path.read_text(encoding='utf-8')
    questions = parse_file(content)

    question = get_question_by_id(questions, question_id)
    if not question:
        return {"error": f"Question not found: {question_id}"}

    suggestion = None
    options = []

    if field == "partial_feedback":
        # Copy from correct_feedback
        match = re.search(
            r'@@field:\s*correct_feedback\s*\n(.*?)@@end_field',
            question.raw_content,
            re.DOTALL
        )
        if match:
            suggestion = match.group(1).strip()

    elif field == "bloom":
        # Suggest based on question type
        if question.detected_type == 'text_entry':
            suggestion = "Remember"
        elif question.detected_type in ['multiple_response', 'multiple_choice_single']:
            suggestion = "Understand"
        elif question.detected_type == 'match':
            suggestion = "Analyze"
        else:
            suggestion = "Understand"
        options = [level[0] for level in BLOOM_LEVELS]

    elif field == "difficulty":
        suggestion = "Medium"
        options = [level[0] for level in DIFFICULTY_LEVELS]

    return {
        "question_id": question_id,
        "field": field,
        "suggestion": suggestion,
        "options": options if options else None,
        "instruction": (
            f"Förslag för {field}: '{suggestion}'. "
            "Acceptera, modifiera, eller hoppa över?"
        ) if suggestion else f"Inget förslag för {field}. Ange värde."
    }


async def step1_batch_preview(issue_type: str) -> Dict[str, Any]:
    """
    Show all questions with the same type of issue.

    Args:
        issue_type: E.g. "missing_partial_feedback", "missing_bloom"

    Returns:
        List of affected questions
    """
    if not _step1_session:
        return {"error": "No active session"}

    working_path = Path(_step1_session.working_file)
    content = working_path.read_text(encoding='utf-8')
    questions = parse_file(content)

    affected = []

    for q in questions:
        issues = analyze_question(q.raw_content, q.detected_type)
        for issue in issues:
            if _matches_issue_type(issue, issue_type):
                affected.append({
                    "question_id": q.question_id,
                    "title": q.title,
                    "type": q.detected_type,
                    "preview": q.raw_content[:100] + "..."
                })
                break

    return {
        "issue_type": issue_type,
        "count": len(affected),
        "questions": affected[:5],  # Show max 5 as preview
        "all_ids": [a["question_id"] for a in affected],
        "instruction": (
            f"{len(affected)} frågor har samma problem ({issue_type}). "
            "Vill du applicera samma fix på alla?"
        ),
        "options": [
            ("all", f"Applicera på alla {len(affected)}"),
            ("select", "Låt mig välja vilka"),
            ("one", "Bara nuvarande fråga")
        ] if affected else []
    }


async def step1_batch_apply(
    issue_type: str,
    fix_type: str,
    question_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Apply the same fix to multiple questions.

    Args:
        issue_type: E.g. "missing_partial_feedback"
        fix_type: How to fix (e.g. "copy_from_correct", "add_bloom_remember")
        question_ids: Specific questions, or None for all

    Returns:
        Result of batch operation
    """
    if not _step1_session:
        return {"error": "No active session"}

    # Find affected questions if not specified
    if question_ids is None:
        preview = await step1_batch_preview(issue_type)
        question_ids = preview.get("all_ids", [])

    if not question_ids:
        return {"error": "No questions to fix", "issue_type": issue_type}

    success = []
    failed = []

    for qid in question_ids:
        try:
            if issue_type == "missing_partial_feedback" and fix_type == "copy_from_correct":
                result = await step1_suggest(qid, "partial_feedback")
                if result.get("suggestion"):
                    fix_result = await step1_fix_manual(qid, "partial_feedback", result["suggestion"])
                    if fix_result.get("success"):
                        success.append(qid)
                    else:
                        failed.append(qid)
                else:
                    failed.append(qid)

            elif issue_type == "missing_bloom":
                bloom_level = fix_type.replace("add_bloom_", "").capitalize()
                fix_result = await step1_fix_manual(qid, "bloom", bloom_level)
                if fix_result.get("success"):
                    success.append(qid)
                else:
                    failed.append(qid)

            elif issue_type == "missing_difficulty":
                difficulty = fix_type.replace("add_difficulty_", "").capitalize()
                fix_result = await step1_fix_manual(qid, "difficulty", difficulty)
                if fix_result.get("success"):
                    success.append(qid)
                else:
                    failed.append(qid)

            else:
                failed.append(qid)

        except Exception as e:
            failed.append(qid)

    # Log batch change
    if success:
        _step1_session.add_change(
            question_id="BATCH",
            field=issue_type,
            old_value=None,
            new_value=f"Fixed {len(success)} questions with {fix_type}",
            change_type="batch"
        )

    return {
        "issue_type": issue_type,
        "fix_type": fix_type,
        "success": success,
        "success_count": len(success),
        "failed": failed,
        "failed_count": len(failed),
        "message": f"Fixade {len(success)} av {len(question_ids)} frågor"
    }


async def step1_skip(
    question_id: Optional[str] = None,
    issue_field: Optional[str] = None,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Skip an issue or entire question.

    Args:
        question_id: Question ID (default: current)
        issue_field: Specific field to skip (None = skip whole question)
        reason: Reason for skipping

    Returns:
        Confirmation
    """
    if not _step1_session:
        return {"error": "No active session"}

    target_id = question_id or _step1_session.questions[_step1_session.current_index].question_id

    if issue_field:
        # Skip specific issue
        _step1_session.add_change(
            question_id=target_id,
            field=f"skip_{issue_field}",
            old_value=None,
            new_value=reason or "User skipped",
            change_type="skip"
        )

        return {
            "question_id": target_id,
            "skipped_field": issue_field,
            "reason": reason,
            "message": f"Hoppade över {issue_field} för {target_id}",
            "next_action": "step1_analyze"  # Re-check for more issues
        }
    else:
        # Skip entire question
        q_status = next((q for q in _step1_session.questions if q.question_id == target_id), None)
        if q_status:
            q_status.status = 'skipped'

        _step1_session.add_change(
            question_id=target_id,
            field="skip_question",
            old_value=None,
            new_value=reason or "User skipped entire question",
            change_type="skip"
        )

        return {
            "question_id": target_id,
            "skipped": True,
            "reason": reason,
            "message": f"Hoppade över hela {target_id}",
            "next_action": "step1_next"
        }


# ════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════

def _add_to_tags(content: str, tag: str) -> str:
    """Add a tag to ^tags line."""
    match = re.search(r'(\^tags\s+.+)', content, re.MULTILINE)
    if match:
        old_tags = match.group(1)
        new_tags = f"{old_tags} {tag}"
        return content.replace(old_tags, new_tags)
    return content


def _add_feedback_subfield(content: str, subfield_name: str, value: str) -> str:
    """Add a feedback subfield before @end_field of feedback section."""
    # Find the feedback section and add before its @end_field
    pattern = r'(@field:\s*feedback\s*\n.*?)(@@end_field\s*\n@end_field)'

    def replacement(m):
        return f"{m.group(1)}@@end_field\n\n#### Partial Feedback\n@@field: {subfield_name}\n{value}\n\n{m.group(2)}"

    result = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # If no match, try simpler pattern
    if result == content:
        pattern = r'(@@field:\s*\w+_feedback\s*\n.*?@@end_field)\s*\n(@end_field)'

        def replacement2(m):
            return f"{m.group(1)}\n\n#### Partial Feedback\n@@field: {subfield_name}\n{value}\n\n@@end_field\n{m.group(2)}"

        result = re.sub(pattern, replacement2, content, flags=re.DOTALL)

    return result


def _add_correct_answers(content: str, answers: str) -> str:
    """Add correct_answers section for multiple_response."""
    # Add after options section
    pattern = r'(@field:\s*options\s*\n.*?@end_field)'

    def replacement(m):
        return f"{m.group(1)}\n\n### Correct Answers\n@field: correct_answers\n{answers}\n@end_field"

    return re.sub(pattern, replacement, content, flags=re.DOTALL)


def _matches_issue_type(issue, issue_type: str) -> bool:
    """Check if issue matches type."""
    type_mapping = {
        "missing_partial_feedback": lambda i: "partial_feedback" in i.message.lower() or "partial feedback" in i.message.lower(),
        "missing_bloom": lambda i: "bloom" in i.message.lower(),
        "missing_difficulty": lambda i: "svårighetsgrad" in i.message.lower() or "difficulty" in i.message.lower(),
        "missing_correct_answers": lambda i: "correct_answers" in i.message.lower(),
        "missing_labels": lambda i: "labels" in i.message.lower() or "tags" in i.message.lower(),
    }
    check = type_mapping.get(issue_type)
    return check(issue) if check else False


# ════════════════════════════════════════════════════════════════════
# TOOL REGISTRATION INFO
# ════════════════════════════════════════════════════════════════════

STEP1_TOOLS = [
    {
        "name": "step1_start",
        "description": "Starta Step 1 interaktiv session. Använder Step 0 session om aktiv.",
        "parameters": {
            "source_file": {"type": "string", "description": "Sökväg till markdown-fil (optional om Step 0 session finns)", "optional": True},
            "output_folder": {"type": "string", "description": "Mapp för output (optional om Step 0 session finns)", "optional": True},
            "project_name": {"type": "string", "description": "Valfritt projektnamn", "optional": True}
        }
    },
    {
        "name": "step1_status",
        "description": "Visa status för aktiv Step 1 session.",
        "parameters": {}
    },
    {
        "name": "step1_analyze",
        "description": "Analysera en fråga. Returnerar auto_fixable och needs_input kategorier.",
        "parameters": {
            "question_id": {"type": "string", "description": "Fråge-ID (default: aktuell)", "optional": True}
        }
    },
    {
        "name": "step1_fix_auto",
        "description": "Applicera ENDAST automatiska transforms. Returnerar remaining issues som kräver input.",
        "parameters": {
            "question_id": {"type": "string", "description": "Fråge-ID (default: aktuell)", "optional": True}
        }
    },
    {
        "name": "step1_fix_manual",
        "description": "Applicera EN manuell fix baserat på användarinput.",
        "parameters": {
            "question_id": {"type": "string", "description": "Fråge-ID"},
            "field": {"type": "string", "description": "Fält (bloom, difficulty, partial_feedback, etc.)"},
            "value": {"type": "string", "description": "Värde från användaren"}
        }
    },
    {
        "name": "step1_suggest",
        "description": "Generera förslag för ett fält. Användaren kan acceptera/modifiera.",
        "parameters": {
            "question_id": {"type": "string", "description": "Fråge-ID"},
            "field": {"type": "string", "description": "Fält att föreslå för"}
        }
    },
    {
        "name": "step1_batch_preview",
        "description": "Visa alla frågor med samma issue-typ.",
        "parameters": {
            "issue_type": {"type": "string", "description": "T.ex. missing_partial_feedback, missing_bloom"}
        }
    },
    {
        "name": "step1_batch_apply",
        "description": "Applicera samma fix på flera frågor.",
        "parameters": {
            "issue_type": {"type": "string", "description": "Issue-typ"},
            "fix_type": {"type": "string", "description": "Hur fixas (copy_from_correct, add_bloom_remember, etc.)"},
            "question_ids": {"type": "array", "description": "Lista av fråge-ID (optional, None = alla)", "optional": True}
        }
    },
    {
        "name": "step1_skip",
        "description": "Hoppa över issue eller hel fråga.",
        "parameters": {
            "question_id": {"type": "string", "description": "Fråge-ID (optional)", "optional": True},
            "issue_field": {"type": "string", "description": "Specifikt fält, eller None för hel fråga", "optional": True},
            "reason": {"type": "string", "description": "Anledning (optional)", "optional": True}
        }
    },
    {
        "name": "step1_transform",
        "description": "[LEGACY] Applicera ALLA transforms på en gång. Använd step1_fix_auto för interaktivt flöde.",
        "parameters": {
            "question_id": {"type": "string", "description": "Fråge-ID (default: alla)", "optional": True}
        }
    },
    {
        "name": "step1_next",
        "description": "Gå till nästa/föregående fråga.",
        "parameters": {
            "direction": {"type": "string", "description": "'forward', 'back', eller fråge-ID", "optional": True}
        }
    },
    {
        "name": "step1_preview",
        "description": "Förhandsgranska working file.",
        "parameters": {
            "lines": {"type": "integer", "description": "Antal rader (default: 50)", "optional": True}
        }
    },
    {
        "name": "step1_finish",
        "description": "Avsluta Step 1 och generera rapport.",
        "parameters": {}
    }
]
