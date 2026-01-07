#!/usr/bin/env python3
"""
Question Set Validation Script

Validates generated assessmentTest XML for correct scoring and structure.

Usage:
    python3 scripts/validate_question_set.py output/QUIZ_NAME/
    python3 scripts/validate_question_set.py output/QUIZ_NAME/ID_ASSESSMENT_001-assessment.xml

This script:
- Reads assessmentTest XML
- Calculates expected max scores from sections and question references
- Compares with declared inspera:maximumScore
- Reports any discrepancies
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple


def parse_assessment_xml(xml_path: Path) -> Tuple[float, List[Dict]]:
    """
    Parse assessmentTest XML and extract score information.

    Returns:
        (declared_max_score, sections_info)
        where sections_info is a list of dicts with section details
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Define namespaces
    ns = {
        'qti': 'http://www.imsglobal.org/xsd/imsqti_v2p2',
        'inspera': 'http://ns.inspera.no'
    }

    # Get declared max score
    declared_max_score = root.get('{http://ns.inspera.no}maximumScore')
    if declared_max_score:
        declared_max_score = float(declared_max_score)
    else:
        declared_max_score = None

    # Parse sections
    sections = []
    for section in root.findall('.//{http://www.imsglobal.org/xsd/imsqti_v2p2}assessmentSection'):
        section_info = {
            'id': section.get('identifier'),
            'title': section.get('title'),
            'visible': section.get('visible', 'true')
        }

        # Check for selection element
        selection = section.find('{http://www.imsglobal.org/xsd/imsqti_v2p2}selection')
        if selection is not None:
            section_info['select'] = int(selection.get('select'))
        else:
            section_info['select'] = None

        # Check for ordering/shuffle
        ordering = section.find('{http://www.imsglobal.org/xsd/imsqti_v2p2}ordering')
        if ordering is not None:
            section_info['shuffle'] = ordering.get('shuffle', 'false') == 'true'
        else:
            section_info['shuffle'] = False

        # Count question references
        item_refs = section.findall('{http://www.imsglobal.org/xsd/imsqti_v2p2}assessmentItemRef')
        section_info['total_questions'] = len(item_refs)
        section_info['item_hrefs'] = [ref.get('href') for ref in item_refs]

        sections.append(section_info)

    return declared_max_score, sections


def get_question_score(quiz_dir: Path, item_href: str) -> int:
    """
    Read individual question XML and extract its score (mapped value).

    Args:
        quiz_dir: Directory containing question XML files
        item_href: Filename of the question (e.g., "QUESTION_001-item.xml")

    Returns:
        Point value of the question (default 1 if not found)
    """
    item_path = quiz_dir / item_href
    if not item_path.exists():
        print(f"  ⚠ Warning: Question file not found: {item_href}")
        return 1

    try:
        tree = ET.parse(item_path)
        root = tree.getroot()

        # Look for responseDeclaration with SCORE identifier
        ns = {'qti': 'http://www.imsglobal.org/xsd/imsqti_v2p2'}
        response_decl = root.find(".//qti:responseDeclaration[@identifier='RESPONSE']", ns)

        if response_decl is not None:
            # Find mapping with correct answer
            mapping = response_decl.find('.//qti:mapping', ns)
            if mapping is not None:
                map_entries = mapping.findall('.//qti:mapEntry', ns)
                if map_entries:
                    # Get the mapped value (assuming all correct answers have same value)
                    mapped_value = map_entries[0].get('mappedValue')
                    if mapped_value:
                        return int(float(mapped_value))

        return 1  # Default if not found

    except Exception as e:
        print(f"  ⚠ Warning: Could not parse {item_href}: {e}")
        return 1


def calculate_expected_score(quiz_dir: Path, sections: List[Dict]) -> float:
    """
    Calculate expected maximum score based on section configuration.

    Args:
        quiz_dir: Directory containing question XML files
        sections: List of section info dicts

    Returns:
        Expected total max score
    """
    total_score = 0.0

    for section in sections:
        # Get point value from first question in section (assume all same points)
        if section['item_hrefs']:
            first_item = section['item_hrefs'][0]
            points_per_question = get_question_score(quiz_dir, first_item)
        else:
            points_per_question = 1

        # Calculate section max score
        if section['select'] is not None:
            # Random selection: select X from Y
            num_questions = section['select']
        else:
            # All questions
            num_questions = section['total_questions']

        section_max = num_questions * points_per_question
        section['calculated_max'] = section_max
        section['points_per_question'] = points_per_question

        total_score += section_max

    return total_score


def validate_question_set(quiz_dir: Path, assessment_xml: Path):
    """
    Validate Question Set XML for correct scoring.

    Args:
        quiz_dir: Directory containing all question XML files
        assessment_xml: Path to assessmentTest XML file
    """
    print(f"Validating: {assessment_xml}")
    print("=" * 70)

    # Parse assessment XML
    declared_max, sections = parse_assessment_xml(assessment_xml)

    print(f"\nDeclared maximum score: {declared_max}")
    print(f"Number of sections: {len(sections)}\n")

    # Calculate expected score
    expected_max = calculate_expected_score(quiz_dir, sections)

    # Display section breakdown
    print("Section Breakdown:")
    print("-" * 70)
    for i, section in enumerate(sections, 1):
        select_info = f"{section['select']} from {section['total_questions']}" if section['select'] else f"all {section['total_questions']}"
        shuffle_info = "shuffle" if section['shuffle'] else "fixed order"

        print(f"  {i}. {section['title']}")
        print(f"     Questions: {select_info} ({shuffle_info})")
        print(f"     Points: {section['points_per_question']}p per question")
        print(f"     Max score: {section['calculated_max']}")
        print()

    print("=" * 70)
    print(f"Calculated total max score: {expected_max}")
    print(f"Declared total max score:   {declared_max}")

    # Validation result
    if declared_max is None:
        print("\n❌ FAIL: inspera:maximumScore attribute is missing!")
        print("   This will cause incorrect scoring in Inspera.")
        return False
    elif abs(declared_max - expected_max) < 0.01:  # Allow tiny floating point differences
        print(f"\n✅ SUCCESS: Scores match! ({expected_max})")
        return True
    else:
        difference = declared_max - expected_max
        print(f"\n❌ FAIL: Score mismatch!")
        print(f"   Difference: {difference:+.1f}")
        print(f"   This may indicate a calculation error or unexpected question pool.")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/validate_question_set.py output/QUIZ_NAME/")
        print("   or: python3 scripts/validate_question_set.py output/QUIZ_NAME/ID_XXX-assessment.xml")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if input_path.is_dir():
        # Find assessment XML in directory
        quiz_dir = input_path
        assessment_files = list(quiz_dir.glob("ID_*-assessment.xml"))

        if not assessment_files:
            print(f"Error: No assessment XML found in {quiz_dir}")
            sys.exit(1)

        if len(assessment_files) > 1:
            print(f"Warning: Multiple assessment files found, using first one")

        assessment_xml = assessment_files[0]
    else:
        # Direct path to assessment XML
        assessment_xml = input_path
        quiz_dir = assessment_xml.parent

    if not assessment_xml.exists():
        print(f"Error: File not found: {assessment_xml}")
        sys.exit(1)

    # Validate
    success = validate_question_set(quiz_dir, assessment_xml)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
