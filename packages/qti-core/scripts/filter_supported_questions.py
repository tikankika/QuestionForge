#!/usr/bin/env python3
"""
Filter markdown file to only include supported question types.

This script reads a converted markdown file and removes questions with
unsupported question types, keeping only the ones that can be processed
by the QTI Generator.
"""

import re
import sys
from pathlib import Path


SUPPORTED_TYPES = {
    'multiple_choice_single',
    'text_area',
    'essay'
}


def filter_questions(input_path, output_path, supported_types=None):
    """Filter questions to only include supported types."""
    if supported_types is None:
        supported_types = SUPPORTED_TYPES

    print(f"Reading input file: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into frontmatter and questions using regex
    # Frontmatter is between first two --- markers
    frontmatter_match = re.match(r'(---\n.*?\n---\n)', content, re.DOTALL)

    if not frontmatter_match:
        print("Error: Could not find YAML frontmatter")
        return False

    frontmatter = frontmatter_match.group(1)
    questions_section = content[len(frontmatter):]

    # Split questions by delimiter (---), but filter out empty blocks
    question_blocks = [q.strip() for q in re.split(r'\n---\n', questions_section) if q.strip()]

    # Filter questions
    kept_questions = []
    skipped_questions = []

    for i, block in enumerate(question_blocks, 1):
        if not block.strip():
            continue

        # Extract question type
        type_match = re.search(r'\*\*Type\*\*:\s*(\w+)', block)

        if not type_match:
            print(f"Warning: Question {i} has no type field, skipping")
            skipped_questions.append((i, 'unknown'))
            continue

        question_type = type_match.group(1)

        if question_type in supported_types:
            kept_questions.append(block)
        else:
            # Extract identifier for logging
            id_match = re.search(r'\*\*Identifier\*\*:\s*(\S+)', block)
            identifier = id_match.group(1) if id_match else f'Q{i:03d}'
            skipped_questions.append((i, question_type, identifier))

    print(f"\nFiltering results:")
    print(f"  Total questions: {len(question_blocks)}")
    print(f"  Kept (supported): {len(kept_questions)}")
    print(f"  Skipped (unsupported): {len(skipped_questions)}")

    if skipped_questions:
        print(f"\nSkipped questions:")
        type_counts = {}
        for item in skipped_questions:
            if len(item) == 2:
                q_num, q_type = item
                identifier = f'Q{q_num:03d}'
            else:
                q_num, q_type, identifier = item

            type_counts[q_type] = type_counts.get(q_type, 0) + 1
            print(f"  - Question {q_num} ({identifier}): {q_type}")

        print(f"\nSkipped by type:")
        for q_type, count in sorted(type_counts.items()):
            print(f"  - {q_type}: {count}")

    # Create output content
    output_content = frontmatter + '\n\n\n' + '\n\n---\n\n'.join(kept_questions)

    # Write to output file
    print(f"\nWriting output file: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)

    print(f"✓ Filtering complete!")
    print(f"  Input:  {input_path}")
    print(f"  Output: {output_path}")
    print(f"  Questions: {len(kept_questions)}")

    return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python filter_supported_questions.py <input_file> [output_file]")
        print("\nExample:")
        print("  python filter_supported_questions.py Evolution_CONVERTED.md Evolution_FILTERED.md")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        # Default output path
        output_path = input_path.parent / f"{input_path.stem}_FILTERED.md"

    success = filter_questions(input_path, output_path)

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
