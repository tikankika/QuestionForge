#!/usr/bin/env python3
"""
Test script for parse_selection_input() function.
"""

import sys
sys.path.insert(0, '/path/to/qti-generator')

# Import the function
import re
from typing import List

def parse_selection_input(input_str: str) -> List[int]:
    """
    Parse user selection input supporting both comma and 'or' separators.
    """
    if not input_str:
        return []

    normalized = input_str.lower().strip()
    parts = re.split(r'\s*or\s*', normalized)

    if len(parts) == 1:
        parts = [p.strip() for p in normalized.split(',')]

    selected = []
    for part in parts:
        part = part.strip()
        if part.isdigit():
            selected.append(int(part))

    return selected


def test_parse_selection_input():
    """Test the parse_selection_input function."""

    print("=" * 60)
    print("Testing parse_selection_input()")
    print("=" * 60)
    print()

    tests = [
        # (input, expected_output, description)
        ("1 or 2", [1, 2], "New format with 'or'"),
        ("1,2", [1, 2], "Old format with comma"),
        ("1 OR 2", [1, 2], "Case-insensitive OR"),
        ("1or2", [1, 2], "No spaces around 'or'"),
        ("1 or 2 or 3", [1, 2, 3], "Multiple values with 'or'"),
        ("1,2,3", [1, 2, 3], "Multiple values with comma"),
        ("", [], "Empty input"),
        ("xyz", [], "Invalid input"),
        ("1", [1], "Single value"),
        ("  1 or 2  ", [1, 2], "Extra whitespace"),
    ]

    all_passed = True

    for input_str, expected, description in tests:
        result = parse_selection_input(input_str)
        passed = result == expected

        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {description}")
        print(f"  Input:    \"{input_str}\"")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")

        if not passed:
            all_passed = False

        print()

    print("=" * 60)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 60)

    return all_passed


if __name__ == '__main__':
    success = test_parse_selection_input()
    sys.exit(0 if success else 1)
