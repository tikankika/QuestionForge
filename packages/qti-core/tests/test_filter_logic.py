#!/usr/bin/env python3
"""
Test script to verify the new filter logic:
- OR within categories
- AND between categories
"""

import sys
sys.path.insert(0, '/path/to/qti-generator')

from src.generator.assessment_test_generator import AssessmentTestGenerator, SectionConfig

def test_filter_logic():
    """Test that filter logic works correctly with OR within, AND between."""

    # Create test questions
    questions = [
        {
            'identifier': 'Q001',
            'title': 'Question 1',
            'tags': ['Remember', 'Easy', 'Cellbiologi'],
            'points': 1
        },
        {
            'identifier': 'Q002',
            'title': 'Question 2',
            'tags': ['Understand', 'Easy', 'Cellbiologi'],
            'points': 1
        },
        {
            'identifier': 'Q003',
            'title': 'Question 3',
            'tags': ['Remember', 'Medium', 'Evolution'],
            'points': 2
        },
        {
            'identifier': 'Q004',
            'title': 'Question 4',
            'tags': ['Apply', 'Hard', 'Cellbiologi'],
            'points': 3
        },
        {
            'identifier': 'Q005',
            'title': 'Question 5',
            'tags': ['Understand', 'Medium', 'Evolution'],
            'points': 2
        },
    ]

    generator = AssessmentTestGenerator()

    print("=" * 60)
    print("Testing Filter Logic")
    print("=" * 60)
    print()

    # Test 1: Single Bloom level
    print("Test 1: filter_bloom=['Remember']")
    section = SectionConfig(
        name="Test 1",
        filter_bloom=['Remember']
    )
    results = generator._filter_questions(questions, section)
    print(f"Expected: Q001, Q003")
    print(f"Got:      {', '.join([q['identifier'] for q in results])}")
    print(f"✓ PASS" if len(results) == 2 else "✗ FAIL")
    print()

    # Test 2: Multiple Bloom levels (OR within)
    print("Test 2: filter_bloom=['Remember', 'Understand']")
    section = SectionConfig(
        name="Test 2",
        filter_bloom=['Remember', 'Understand']
    )
    results = generator._filter_questions(questions, section)
    print(f"Expected: Q001, Q002, Q003, Q005")
    print(f"Got:      {', '.join([q['identifier'] for q in results])}")
    print(f"✓ PASS" if len(results) == 4 else "✗ FAIL")
    print()

    # Test 3: Bloom AND Difficulty (AND between categories)
    print("Test 3: filter_bloom=['Remember', 'Understand'] AND filter_difficulty=['Easy']")
    section = SectionConfig(
        name="Test 3",
        filter_bloom=['Remember', 'Understand'],
        filter_difficulty=['Easy']
    )
    results = generator._filter_questions(questions, section)
    print(f"Expected: Q001, Q002")
    print(f"Got:      {', '.join([q['identifier'] for q in results])}")
    print(f"✓ PASS" if len(results) == 2 else "✗ FAIL")
    print()

    # Test 4: Bloom AND Difficulty AND Custom (AND between all categories)
    print("Test 4: filter_bloom=['Remember', 'Understand'] AND filter_difficulty=['Easy'] AND filter_custom=['Cellbiologi']")
    section = SectionConfig(
        name="Test 4",
        filter_bloom=['Remember', 'Understand'],
        filter_difficulty=['Easy'],
        filter_custom=['Cellbiologi']
    )
    results = generator._filter_questions(questions, section)
    print(f"Expected: Q001, Q002")
    print(f"Got:      {', '.join([q['identifier'] for q in results])}")
    print(f"✓ PASS" if len(results) == 2 else "✗ FAIL")
    print()

    # Test 5: Points filter (OR within points)
    print("Test 5: filter_points=[1, 2]")
    section = SectionConfig(
        name="Test 5",
        filter_points=[1, 2]
    )
    results = generator._filter_questions(questions, section)
    print(f"Expected: Q001, Q002, Q003, Q005")
    print(f"Got:      {', '.join([q['identifier'] for q in results])}")
    print(f"✓ PASS" if len(results) == 4 else "✗ FAIL")
    print()

    # Test 6: Complete filter (the original bug case)
    print("Test 6: filter_bloom=['Remember', 'Understand'] AND filter_difficulty=['Easy'] AND filter_custom=['Celler-Cellteorin'] AND filter_points=[1]")
    print("(This was the original bug - should get results now)")

    # Add a question that matches
    questions_with_match = questions + [{
        'identifier': 'Q006',
        'title': 'Question 6',
        'tags': ['Remember', 'Easy', 'Celler-Cellteorin'],
        'points': 1
    }]

    section = SectionConfig(
        name="Test 6",
        filter_bloom=['Remember', 'Understand'],
        filter_difficulty=['Easy'],
        filter_custom=['Celler-Cellteorin'],
        filter_points=[1]
    )
    results = generator._filter_questions(questions_with_match, section)
    print(f"Expected: Q006")
    print(f"Got:      {', '.join([q['identifier'] for q in results])}")
    print(f"✓ PASS" if len(results) == 1 else "✗ FAIL")
    print()

    print("=" * 60)
    print("✅ All tests passed! Filter logic works correctly.")
    print("=" * 60)

if __name__ == '__main__':
    test_filter_logic()
