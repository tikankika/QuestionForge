#!/usr/bin/env python3
"""
Preprocessing utilities for markdown quiz files.

This module consolidates functionality from standalone helper scripts:
- add_unified_feedback_v2.py: Add unified feedback subsections
- filter_hotspot_questions.py: Filter questions by type
"""

from typing import List, Set


# Question types that require partial credit feedback
PARTIAL_CREDIT_TYPES = {
    'multiple_response', 'text_entry', 'inline_choice', 'match',
    'graphicgapmatch_v2', 'text_entry_graphic'
}


def add_unified_feedback(content: str) -> tuple[str, int]:
    """
    Add unified feedback subsections to questions that only have General Feedback.

    Converts:
        ### General Feedback
        Feedback text...
        ---

    To:
        ### General Feedback
        Feedback text...

        ### Correct Response Feedback
        Feedback text...

        ### Incorrect Response Feedback
        Feedback text...

        ### Partially Correct Response Feedback  (if applicable)
        Feedback text...

        ### Unanswered Feedback
        Feedback text...
        ---

    Args:
        content: Markdown file content

    Returns:
        Tuple of (modified content, number of questions fixed)
    """
    lines = content.splitlines(keepends=True)
    output_lines = []
    current_question_type = None
    in_general_feedback = False
    general_feedback_lines = []
    questions_fixed = 0
    seen_type_for_question = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Reset type tracking at new question
        if line.startswith('# Question'):
            seen_type_for_question = False

        # Track question type (ONLY the first Type field per question!)
        if line.startswith('**Type**:') and not seen_type_for_question:
            # Extract type, remove trailing spaces and any extra characters
            type_part = line.split(':')[1].strip()
            # Remove any trailing whitespace or markdown formatting
            current_question_type = type_part.split()[0] if type_part else None
            seen_type_for_question = True

        # Detect start of General Feedback
        if line.strip() == '### General Feedback':
            in_general_feedback = True
            general_feedback_lines = []
            i += 1
            continue

        # Collect feedback content until ---
        if in_general_feedback:
            if line.strip() == '---':
                # End of feedback - now output unified subsections
                feedback_content = ''.join(general_feedback_lines).strip()

                # Output all subsections
                output_lines.append('### General Feedback\n')
                output_lines.append(feedback_content + '\n')
                output_lines.append('\n')
                output_lines.append('### Correct Response Feedback\n')
                output_lines.append(feedback_content + '\n')
                output_lines.append('\n')
                output_lines.append('### Incorrect Response Feedback\n')
                output_lines.append(feedback_content + '\n')
                output_lines.append('\n')

                # Add Partially Correct if needed
                if current_question_type in PARTIAL_CREDIT_TYPES:
                    output_lines.append('### Partially Correct Response Feedback\n')
                    output_lines.append(feedback_content + '\n')
                    output_lines.append('\n')

                output_lines.append('### Unanswered Feedback\n')
                output_lines.append(feedback_content + '\n')
                output_lines.append('\n')
                output_lines.append(line)  # Add the --- separator

                in_general_feedback = False
                questions_fixed += 1
                i += 1
                continue
            else:
                general_feedback_lines.append(line)
                i += 1
                continue

        # Normal line - just copy
        output_lines.append(line)
        i += 1

    return ''.join(output_lines), questions_fixed


def filter_questions_by_type(content: str, exclude_types: Set[str]) -> tuple[str, int]:
    """
    Remove questions of specified types from markdown content.

    Args:
        content: Markdown file content
        exclude_types: Set of question type identifiers to exclude
                      (e.g., {'hotspot', 'graphicgapmatch_v2'})

    Returns:
        Tuple of (filtered content, number of questions removed)
    """
    lines = content.splitlines(keepends=True)
    output_lines = []
    in_excluded_question = False
    questions_removed = 0
    current_question_type = None
    question_start_index = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect start of question
        if line.startswith('# Question'):
            question_start_index = len(output_lines)
            current_question_type = None
            in_excluded_question = False

        # Track question type
        if line.startswith('**Type**:'):
            type_part = line.split(':')[1].strip()
            current_question_type = type_part.split()[0] if type_part else None

            # Check if this type should be excluded
            if current_question_type in exclude_types:
                in_excluded_question = True
                # Remove question header we already added
                if question_start_index is not None:
                    output_lines = output_lines[:question_start_index]
                questions_removed += 1

        # Only add line if not in excluded question
        if not in_excluded_question:
            output_lines.append(line)

        # Reset at end of question (separator)
        if line.strip() == '---' and in_excluded_question:
            in_excluded_question = False

        i += 1

    return ''.join(output_lines), questions_removed


def preprocess_markdown(
    content: str,
    add_feedback: bool = False,
    exclude_types: Set[str] = None
) -> tuple[str, dict]:
    """
    Apply preprocessing operations to markdown content.

    Args:
        content: Original markdown content
        add_feedback: If True, add unified feedback subsections
        exclude_types: Set of question types to exclude (e.g., {'hotspot'})

    Returns:
        Tuple of (processed content, stats dict)
    """
    stats = {
        'feedback_added': 0,
        'questions_removed': 0,
        'operations': []
    }

    processed_content = content

    # Add unified feedback if requested
    if add_feedback:
        processed_content, count = add_unified_feedback(processed_content)
        stats['feedback_added'] = count
        stats['operations'].append(f'Added unified feedback to {count} questions')

    # Filter question types if requested
    if exclude_types:
        processed_content, count = filter_questions_by_type(processed_content, exclude_types)
        stats['questions_removed'] = count
        types_str = ', '.join(exclude_types)
        stats['operations'].append(f'Removed {count} questions of types: {types_str}')

    return processed_content, stats
