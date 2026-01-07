#!/usr/bin/env python3
"""
Validate markdown question bank for common issues.

Usage:
    python3 scripts/validate_markdown.py path/to/file.md
    python3 scripts/validate_markdown.py path/to/file.md --fix

This script checks for:
- Match questions with incorrect point values (points should equal number of premises)
- Points stored as floats instead of integers (1.0 vs 1)

The validation is also performed automatically during QTI generation,
but this script allows standalone checking and fixing of markdown files.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.parser.markdown_parser import MarkdownQuizParser


def validate_markdown(file_path: Path, fix: bool = False, verbose: bool = False):
    """
    Validate markdown file and optionally fix issues.

    Args:
        file_path: Path to markdown file
        fix: If True, write corrections back to file
        verbose: If True, show detailed output for each question

    Returns:
        Exit code (0 = success, 1 = issues found)
    """
    print(f"📋 Validating: {file_path}")
    print()

    # Read and parse markdown
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        parser = MarkdownQuizParser(content)
        quiz_data = parser.parse()
        questions = quiz_data.get('questions', [])

        if not questions:
            print("⚠️  No questions found in markdown file")
            return 1

    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return 1
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return 1

    # Track issues
    match_issues = []
    float_issues = []
    all_ok = []

    # Check each question
    for q in questions:
        q_id = q.get('identifier', 'UNKNOWN')
        q_type = q.get('question_type', 'unknown')

        if verbose:
            print(f"Checking {q_id} ({q_type})...", end=" ")

        # Validation 1: Match questions points vs premises
        if q_type == 'match':
            premise_count = len(q.get('premises', []))
            declared_points = q.get('points', 1)

            if premise_count != declared_points:
                issue = {
                    'id': q_id,
                    'premises': premise_count,
                    'points': declared_points
                }
                match_issues.append(issue)
                if verbose:
                    print(f"❌ {premise_count} premises but Points: {declared_points}")
            else:
                if verbose:
                    print(f"✓ OK (Points: {declared_points} matches {premise_count} premises)")
                all_ok.append(q_id)
        else:
            # Validation 2: Point format (int vs float) - only for non-match questions
            points = q.get('points')
            if isinstance(points, float) and points == int(points):
                float_issues.append({
                    'id': q_id,
                    'points': points
                })
                if verbose:
                    print(f"⚠️  Points: {points} is float")
            else:
                if verbose:
                    print("✓ OK")
                all_ok.append(q_id)

    # Report results
    total_issues = len(match_issues) + len(float_issues)

    if total_issues == 0:
        print(f"✅ All {len(questions)} questions validated successfully!")
        print()
        return 0

    # Show summary
    print(f"Found {total_issues} issue(s) in {len(questions)} questions:\n")

    if match_issues:
        print(f"❌ Match Question Point Mismatches ({len(match_issues)}):")
        for issue in match_issues:
            print(f"   {issue['id']}: {issue['premises']} premises but Points: {issue['points']}")
            print(f"      → Should be: Points: {issue['premises']}")
        print()

    if float_issues:
        print(f"⚠️  Float Point Values ({len(float_issues)}):")
        for issue in float_issues:
            print(f"   {issue['id']}: Points: {issue['points']}")
            print(f"      → Should be: Points: {int(issue['points'])}")
        print()

    # Provide recommendations
    if fix:
        print("🔧 FIX MODE NOT YET IMPLEMENTED")
        print("   The markdown parser auto-corrects these issues during generation.")
        print("   Run interactive_qti.py to generate with auto-corrections.")
        print()
        return 1
    else:
        print("💡 HOW TO FIX:")
        print("   Option 1: Run interactive_qti.py - issues will be auto-corrected during parsing")
        print("   Option 2: Manually edit the markdown file:")
        if match_issues:
            print(f"      - Update match question Points to match premise count")
        if float_issues:
            print(f"      - Change Points: X.0 to Points: X (remove .0)")
        print()
        print("   Note: Auto-correction happens automatically when generating QTI,")
        print("         so you may not need to manually fix the markdown.")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Validate markdown question bank for common issues"
    )
    parser.add_argument(
        'file',
        type=Path,
        help="Path to markdown file"
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help="Auto-fix issues in markdown (not yet implemented)"
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Show detailed output for each question"
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"❌ File not found: {args.file}")
        return 1

    return validate_markdown(args.file, fix=args.fix, verbose=args.verbose)


if __name__ == '__main__':
    sys.exit(main())
