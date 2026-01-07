#!/usr/bin/env python3
"""
Convert Evolution markdown file from dual-structure format to QTI Generator format.

This script transforms the Evolution file that has separate Metadata and Question Content
sections into the format expected by the QTI Generator (inline metadata with labels).
"""

import re
import sys
from pathlib import Path
from datetime import datetime


def extract_labels_from_metadata(metadata_section):
    """Extract labels from the metadata section's label list."""
    labels = []
    in_labels = False

    for line in metadata_section.split('\n'):
        line = line.strip()

        if '**Labels**:' in line:
            in_labels = True
            continue

        if in_labels:
            # Extract label from backticks
            match = re.match(r'-\s+`([^`]+)`', line)
            if match:
                labels.append(match.group(1))
            elif line.startswith('###') or line.startswith('**'):
                # End of labels section
                break

    return labels


def convert_question(question_block):
    """Convert a single question from dual format to inline format."""
    # Split into Metadata and Question Content sections
    sections = re.split(r'### (Metadata|Question Content)', question_block)

    if len(sections) < 4:
        # Not a valid question block
        return None

    metadata_section = sections[2]  # Content after "### Metadata"
    question_content = sections[4]  # Content after "### Question Content"

    # Extract labels from metadata
    labels = extract_labels_from_metadata(metadata_section)
    labels_line = ', '.join(labels)

    # Process question content
    lines = question_content.split('\n')
    converted_lines = []

    for i, line in enumerate(lines):
        # Skip the initial "# Fråga X:" line - we'll keep it as is
        # Add Labels field after Difficulty field
        if line.startswith('**Difficulty**:'):
            converted_lines.append(line)
            converted_lines.append('')
            converted_lines.append(f'**Labels**: {labels_line}')
            continue

        # Replace "## Correct Answer" with "## Answer"
        if line.strip() == '## Correct Answer':
            converted_lines.append('## Answer')
            continue

        converted_lines.append(line)

    return '\n'.join(converted_lines).strip()


def create_yaml_frontmatter():
    """Create YAML frontmatter for the Evolution test."""
    today = datetime.now().strftime('%Y-%m-%d')

    frontmatter = f"""---
test_metadata:
  title: "BIOG001X Evolution - Question Bank"
  identifier: "BIOG001X_EVOLUTION"
  language: "sv"
  description: "Evolution question bank for BIOG001X - Biologi nivå 1 (GY25)"
  subject: "Biology - Evolution"
  author: "BIOG001X Course Team"
  created_date: "{today}"

assessment_configuration:
  type: "formative"
  time_limit: 90
  shuffle_questions: true
  shuffle_choices: true

learning_objectives:
  - id: "LO1"
    description: "Förstå och förklara evolutionens grundläggande definition"
  - id: "LO2"
    description: "Känna till och använda evolutionsbiologiska grundbegrepp"
  - id: "LO3"
    description: "Förstå naturligt urval och dess mekanismer"
  - id: "LO4"
    description: "Tillämpa evolutionära koncept på exempel"
  - id: "LO5"
    description: "Analysera och utvärdera evolutionära scenarier"
---
"""
    return frontmatter


def convert_file(input_path, output_path):
    """Convert the entire Evolution file."""
    print(f"Reading input file: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by question delimiters (## \d+:)
    # First, remove the header section before the first question
    parts = re.split(r'(^|\n)(## \d+:)', content)

    # Find where questions start
    questions_start_idx = None
    for i, part in enumerate(parts):
        if re.match(r'## \d+:', part):
            questions_start_idx = i
            break

    if questions_start_idx is None:
        print("Error: Could not find questions in the file")
        return False

    # Reconstruct question blocks
    question_blocks = []
    i = questions_start_idx
    while i < len(parts):
        if re.match(r'## \d+:', parts[i]):
            # Start of a question
            question_header = parts[i]
            question_content = parts[i + 1] if i + 1 < len(parts) else ''

            # Split by --- to get just this question
            question_full = question_header + question_content
            question_full = question_full.split('\n---\n')[0]

            question_blocks.append(question_full)
            i += 2
        else:
            i += 1

    print(f"Found {len(question_blocks)} questions")

    # Convert each question
    converted_questions = []
    skipped = 0

    for i, block in enumerate(question_blocks, 1):
        try:
            converted = convert_question(block)
            if converted:
                converted_questions.append(converted)
            else:
                print(f"Warning: Skipped question {i} (could not parse)")
                skipped += 1
        except Exception as e:
            print(f"Warning: Error converting question {i}: {e}")
            skipped += 1

    print(f"Successfully converted {len(converted_questions)} questions")
    if skipped > 0:
        print(f"Skipped {skipped} questions due to parsing errors")

    # Create final output
    output_content = create_yaml_frontmatter()
    output_content += '\n\n'
    output_content += '\n\n---\n\n'.join(converted_questions)

    # Write to output file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Writing output file: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)

    print(f"✓ Conversion complete!")
    print(f"  Input:  {input_path}")
    print(f"  Output: {output_path}")
    print(f"  Questions: {len(converted_questions)}")

    return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python convert_evolution_format.py <input_file> [output_file]")
        print("\nExample:")
        print("  python convert_evolution_format.py Evolution_Fragebank_68_fragor_LABELED.md Evolution_CONVERTED.md")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        # Default output path
        output_path = input_path.parent / f"{input_path.stem}_CONVERTED.md"

    success = convert_file(input_path, output_path)

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
