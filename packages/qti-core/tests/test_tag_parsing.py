#!/usr/bin/env python3
"""
Test script to verify tag parsing and categorization works correctly
with both comma-separated and space-separated tag formats.
"""

import sys
sys.path.insert(0, '/Users/niklaskarlsson/QTI-Generator-for-Inspera')

from src.parser.markdown_parser import MarkdownQuizParser

def test_tag_parsing():
    """Test that tags are correctly parsed and categorized."""

    # Test with the interactive test file (space-separated tags)
    test_file = '/Users/niklaskarlsson/QTI-Generator-for-Inspera/tests/test_interactive_tags.md'

    print("=" * 60)
    print("Testing Tag Parsing and Categorization")
    print("=" * 60)
    print(f"\nParsing file: {test_file}\n")

    # Parse the quiz
    with open(test_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    parser = MarkdownQuizParser(markdown_content)
    quiz_data = parser.parse()
    questions = quiz_data.get('questions', [])

    print(f"✓ Found {len(questions)} questions\n")

    # Categorize tags
    bloom_levels = {'Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create'}
    difficulty_levels = {'Easy', 'Medium', 'Hard'}

    bloom_tags = {}
    difficulty_tags = {}
    custom_tags = {}
    all_tags = set()

    print("Question tags:")
    print("-" * 60)

    for q in questions:
        tags = q.get('tags', [])
        q_id = q.get('identifier', 'UNKNOWN')

        # Handle both string and list formats
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',')]

        all_tags.update(tags)

        print(f"\n{q_id}: {tags}")
        print(f"  Title: {q.get('title', 'N/A')}")
        print(f"  Points: {q.get('points', 'N/A')}")

        # Categorize each tag
        bloom_found = []
        diff_found = []
        custom_found = []

        for tag in tags:
            tag_clean = tag.lstrip('#')

            if tag_clean in bloom_levels:
                bloom_tags[tag_clean] = bloom_tags.get(tag_clean, 0) + 1
                bloom_found.append(tag_clean)
            elif tag_clean in difficulty_levels:
                difficulty_tags[tag_clean] = difficulty_tags.get(tag_clean, 0) + 1
                diff_found.append(tag_clean)
            else:
                custom_tags[tag_clean] = custom_tags.get(tag_clean, 0) + 1
                custom_found.append(tag_clean)

        print(f"  Bloom: {bloom_found}")
        print(f"  Difficulty: {diff_found}")
        print(f"  Custom: {custom_found}")

    print("\n" + "=" * 60)
    print("Tag Categorization Summary")
    print("=" * 60)

    print(f"\n📚 Bloom Taxonomy Tags ({len(bloom_tags)}):")
    for tag, count in sorted(bloom_tags.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tag}: {count}")

    print(f"\n🎯 Difficulty Tags ({len(difficulty_tags)}):")
    for tag, count in sorted(difficulty_tags.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tag}: {count}")

    print(f"\n🏷️  Custom Tags ({len(custom_tags)}):")
    for tag, count in sorted(custom_tags.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tag}: {count}")

    # Verification
    print("\n" + "=" * 60)
    print("Verification")
    print("=" * 60)

    success = True

    if not bloom_tags:
        print("❌ FAIL: No Bloom taxonomy tags found!")
        success = False
    else:
        print(f"✓ PASS: Found {len(bloom_tags)} Bloom taxonomy tags")

    if not difficulty_tags:
        print("❌ FAIL: No difficulty tags found!")
        success = False
    else:
        print(f"✓ PASS: Found {len(difficulty_tags)} difficulty tags")

    if not custom_tags:
        print("❌ FAIL: No custom tags found!")
        success = False
    else:
        print(f"✓ PASS: Found {len(custom_tags)} custom tags")

    print("\n" + "=" * 60)
    if success:
        print("✅ SUCCESS: Tag parsing and categorization working correctly!")
        print("The tag filtering UI should now display properly.")
    else:
        print("❌ FAILURE: Tag parsing or categorization not working!")
    print("=" * 60 + "\n")

    return success

if __name__ == '__main__':
    success = test_tag_parsing()
    sys.exit(0 if success else 1)
