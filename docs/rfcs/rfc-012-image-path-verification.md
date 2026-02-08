# RFC-012 Image Path Verification

**Date:** 2026-01-24
**Tested by:** Claude Code (Opus 4.5)
**Status:** ✅ VERIFIED - Scripts solve the RFC-012 bug

---

## Purpose

Verify that manual scripts (`qti-core/scripts/`) correctly apply `apply_resource_mapping()` to solve the critical bug in RFC-012.

---

## Test Setup

**Test file:** `tests/fixtures/v65/image_test.md`

```markdown
@field: question_text
Look at the diagram below and answer the question.

![Test Diagram](test_image.png)

What color is the pixel?
@end_field
```

**Images:**
- `test_image.png` (1x1 pixel PNG)
- `feedback_image.png` (1x1 pixel PNG)

---

## Test Execution

```bash
cd ./packages/qti-core

# Step 1: Validate
python3 scripts/step1_validate.py tests/fixtures/v65/image_test.md
# Exit: 0 ✅

# Step 2: Create folder
python3 scripts/step2_create_folder.py tests/fixtures/v65/image_test.md
# Created: output/image_test/.workflow/metadata.json ✅

# Step 3: Copy resources
python3 scripts/step3_copy_resources.py --verbose
# Copied: test_image.png → IMG_TEST_Q001_test_image.png ✅
# Copied: feedback_image.png → IMG_TEST_Q001_feedback_image.png ✅
# Created: .workflow/resource_mapping.json ✅

# Step 4: Generate XML
python3 scripts/step4_generate_xml.py --verbose
# Output: "Loaded resource mapping with 2 entries"
# Output: "Updating image paths in question data..."
# Generated: IMG_TEST_Q001-item.xml ✅

# Step 5: Create ZIP
python3 scripts/step5_create_zip.py
# Created: image_test.zip ✅
```

---

## Critical Verification

### XML Content (line 35 in IMG_TEST_Q001-item.xml)

```xml
<img src="resources/IMG_TEST_Q001_test_image.png" alt="Test Diagram"/>
```

### Transformation

| Stage | Path |
|-------|------|
| Input (markdown) | `test_image.png` |
| After step3 (copy) | File: `resources/IMG_TEST_Q001_test_image.png` |
| After step4 (XML) | Reference: `resources/IMG_TEST_Q001_test_image.png` |
| Final ZIP | ✅ File exists + XML reference matches |

---

## ZIP Contents

```
image_test.zip
├── IMG_TEST_Q001-item.xml
├── imsmanifest.xml
├── .workflow/xml_files.json
└── resources/
    ├── IMG_TEST_Q001_test_image.png
    └── IMG_TEST_Q001_feedback_image.png
```

---

## Conclusion

### ✅ VERIFIED: Scripts solve the RFC-012 bug

**What scripts do correctly:**
1. `step3_copy_resources.py` - Copies and renames images with question ID prefix
2. `step4_generate_xml.py` - Runs `apply_resource_mapping()` which updates all image paths in XML

**What MCP pipeline is missing (the bug):**
- Pipeline NEVER calls `apply_resource_mapping()` after `copy_resources()`
- Therefore XML still has old paths (`test_image.png` instead of `resources/IMG_TEST_Q001_test_image.png`)

### Recommendation

**Implement RFC-012 Phase 1:** Let MCP pipeline run scripts via subprocess.
- This guarantees that `apply_resource_mapping()` runs
- No code changes required in scripts
- Output becomes identical to manual execution

---

## Files Created During Test

- `tests/fixtures/v65/image_test.md` - Test file with image reference
- `tests/fixtures/v65/test_image.png` - Test PNG
- `tests/fixtures/v65/feedback_image.png` - Test PNG
- `output/image_test/` - Generated output (can be deleted)
- `output/image_test.zip` - Final package (can be deleted)

---

*RFC-012 Image Path Verification | 2026-01-24*
