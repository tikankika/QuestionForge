#!/usr/bin/env python3
"""
Test script to verify that simplified packager correctly includes resources.
"""

import sys
import zipfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.packager.qti_packager import QTIPackager

def test_packager_includes_resources():
    """Test that packager creates ZIP with resources from pre-populated directory."""

    # Use existing test_sanitized directory which has resources already
    test_dir = Path("output/test_sanitized")

    if not test_dir.exists():
        print("❌ Test directory not found: output/test_sanitized")
        print("   Run a real test first to create this directory")
        return False

    # Check resources exist in directory
    resources_dir = test_dir / "resources"
    if not resources_dir.exists():
        print("❌ Resources directory not found")
        return False

    resource_files = list(resources_dir.glob("*.png"))
    print(f"Found {len(resource_files)} resource files in {resources_dir}")
    for rf in resource_files:
        print(f"  - {rf.name}")

    # Create simple question XML for testing
    questions_xml = [
        ("TEST_Q001", '<?xml version="1.0"?><assessmentItem/>')
    ]

    metadata = {
        'test_metadata': {'title': 'Test Quiz', 'identifier': 'TEST_001'},
        'questions': [{'identifier': 'TEST_Q001', 'title': 'Test Question'}]
    }

    # Create packager and package the existing directory
    packager = QTIPackager(output_dir="output")

    # IMPORTANT: Use same name as existing directory to test resource preservation
    # In real usage, cli.py uses same quiz_name for both ResourceManager and Packager
    result = packager.create_package(
        questions_xml,
        metadata,
        "test_sanitized.zip",  # Must match existing directory name
        keep_folder=True
    )

    zip_path = Path(result['zip_path'])

    if not zip_path.exists():
        print(f"❌ ZIP file not created: {zip_path}")
        return False

    print(f"\n✓ ZIP created: {zip_path}")

    # Verify ZIP contents
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zip_contents = zipf.namelist()
        print(f"\nZIP contents ({len(zip_contents)} files):")
        for item in sorted(zip_contents):
            print(f"  - {item}")

        # Check for resources
        resource_files_in_zip = [f for f in zip_contents if f.startswith('resources/')]

        if not resource_files_in_zip:
            print("\n❌ FAILED: No resource files found in ZIP!")
            return False

        print(f"\n✓ Found {len(resource_files_in_zip)} resource files in ZIP:")
        for rf in resource_files_in_zip:
            print(f"  - {rf}")

        # Check for manifest
        if 'imsmanifest.xml' not in zip_contents:
            print("\n❌ FAILED: No imsmanifest.xml in ZIP!")
            return False

        print("\n✓ Manifest found in ZIP")

        # Check for item files
        item_files = [f for f in zip_contents if f.endswith('-item.xml')]
        if not item_files:
            print("\n❌ FAILED: No item XML files in ZIP!")
            return False

        print(f"✓ Found {len(item_files)} item XML files in ZIP")

    print("\n" + "="*70)
    print("✓✓✓ SUCCESS: Simplified packager correctly includes resources in ZIP!")
    print("="*70)
    return True

if __name__ == '__main__':
    success = test_packager_includes_resources()
    sys.exit(0 if success else 1)
