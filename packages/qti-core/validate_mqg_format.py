#!/usr/bin/env python3
"""
MQG Format Validator - v6.5 Format

THIN WRAPPER around markdown_parser.py - the single source of truth for parsing.
This file only handles CLI interface and output formatting.

All parsing logic lives in src/parser/markdown_parser.py.
This guarantees: validate pass → export works (same parser, same rules).

Usage:
    python validate_mqg_format.py input.md
    python validate_mqg_format.py input.md --verbose

Exit codes:
    0 = Valid (ready for QTI generation)
    1 = Errors found (fix before QTI generation)
    2 = File not found or other error
"""

import sys
from pathlib import Path
from typing import List
from dataclasses import dataclass, field

# Import the parser - single source of truth
from src.parser.markdown_parser import MarkdownQuizParser


@dataclass
class ValidationIssue:
    """Represents a validation error or warning"""
    level: str  # 'ERROR' or 'WARNING'
    question_num: int
    question_id: str
    message: str
    suggestion: str = ""


@dataclass
class ValidationReport:
    """Validation results for a markdown file"""
    errors: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    total_questions: int = 0
    valid_questions: int = 0

    def is_valid(self) -> bool:
        """Check if file passed validation (no errors)"""
        return len(self.errors) == 0

    def add_error(self, q_num: int, q_id: str, message: str, suggestion: str = ""):
        """Add an error to the report"""
        self.errors.append(ValidationIssue('ERROR', q_num, q_id, message, suggestion))

    def add_warning(self, q_num: int, q_id: str, message: str, suggestion: str = ""):
        """Add a warning to the report"""
        self.warnings.append(ValidationIssue('WARNING', q_num, q_id, message, suggestion))

    def print_report(self):
        """Print formatted validation report"""
        print("=" * 80)
        print("MQG FORMAT VALIDATION REPORT (v6.5)")
        print("=" * 80)
        print()

        if self.errors:
            print("❌ ERRORS FOUND:\n")
            for issue in self.errors:
                print(f"Question {issue.question_num} ({issue.question_id}):")
                print(f"  {issue.message}")
                if issue.suggestion:
                    print(f"  → Suggestion: {issue.suggestion}")
                print()

        if self.warnings:
            print("⚠️  WARNINGS:\n")
            for issue in self.warnings:
                print(f"Question {issue.question_num} ({issue.question_id}):")
                print(f"  {issue.message}")
                print()

        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total Questions: {self.total_questions}")
        print(f"✅ Valid: {self.valid_questions}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print()

        if self.is_valid():
            print("STATUS: ✅ READY FOR QTI GENERATION")
            print()
            print("NEXT STEP: Run step 2 to create output folder:")
            print(f"  python scripts/step2_create_folder.py <your_file.md>")
        else:
            print(f"STATUS: ❌ NOT READY - Fix {len(self.errors)} error(s) before QTI generation")
            print()
            print("→ Go back to Claude Desktop and fix the errors listed above")


def validate_markdown_file(file_path: Path, verbose: bool = False) -> ValidationReport:
    """
    Validate a markdown file against MQG v6.5 specs.

    Uses markdown_parser.validate() - the SAME parser used by step4_generate_xml.
    This guarantees: if validate passes, export will work.
    """
    report = ValidationReport()

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(2)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(2)

    # Use parser.validate() - single source of truth!
    parser = MarkdownQuizParser(content)
    result = parser.validate()

    # Convert parser result to ValidationReport
    report.total_questions = result['total_questions']
    report.valid_questions = result['parsed_questions']

    for error in result['errors']:
        report.add_error(
            q_num=error.get('question_num', 0),
            q_id=error.get('question_id', 'UNKNOWN'),
            message=error.get('message', 'Unknown error'),
            suggestion=error.get('suggestion', '')
        )

    return report


def validate_content(content: str, verbose: bool = False):
    """
    Validate markdown content string.

    Returns: (is_valid, issues_list)
    """
    parser = MarkdownQuizParser(content)
    result = parser.validate()

    issues = []
    for error in result['errors']:
        issues.append(ValidationIssue(
            level='ERROR',
            question_num=error.get('question_num', 0),
            question_id=error.get('question_id', 'UNKNOWN'),
            message=error.get('message', 'Unknown error'),
            suggestion=error.get('suggestion', '')
        ))

    return result['valid'], issues


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python validate_mqg_format.py <markdown_file> [--verbose]")
        sys.exit(2)

    file_path = Path(sys.argv[1])
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(2)

    report = validate_markdown_file(file_path, verbose)
    report.print_report()

    sys.exit(0 if report.is_valid() else 1)


if __name__ == '__main__':
    main()
