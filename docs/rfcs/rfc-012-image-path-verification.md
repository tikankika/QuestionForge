# RFC-012 Image Path Verification

**Datum:** 2026-01-24
**Testat av:** Claude Code (Opus 4.5)
**Status:** ✅ VERIFIED - Scripts löser RFC-012 buggen

---

## Syfte

Verifiera att manuella scripts (`qti-core/scripts/`) korrekt tillämpar `apply_resource_mapping()` för att lösa den kritiska buggen i RFC-012.

---

## Test Setup

**Testfil:** `tests/fixtures/v65/image_test.md`

```markdown
@field: question_text
Look at the diagram below and answer the question.

![Test Diagram](test_image.png)

What color is the pixel?
@end_field
```

**Bilder:**
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

### XML Content (rad 35 i IMG_TEST_Q001-item.xml)

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

### ✅ VERIFIED: Scripts löser RFC-012 buggen

**Vad scripts gör korrekt:**
1. `step3_copy_resources.py` - Kopierar och döper om bilder med question ID prefix
2. `step4_generate_xml.py` - Kör `apply_resource_mapping()` som uppdaterar alla bildpaths i XML

**Vad MCP pipeline saknar (buggen):**
- Pipeline anropar ALDRIG `apply_resource_mapping()` efter `copy_resources()`
- Därför har XML fortfarande gamla paths (`test_image.png` istället för `resources/IMG_TEST_Q001_test_image.png`)

### Recommendation

**Implementera RFC-012 Phase 1:** Låt MCP pipeline köra scripts via subprocess.
- Detta garanterar att `apply_resource_mapping()` körs
- Inga kodändringar i scripts krävs
- Output blir identisk med manuell körning

---

## Files Created During Test

- `tests/fixtures/v65/image_test.md` - Testfil med bildref
- `tests/fixtures/v65/test_image.png` - Test PNG
- `tests/fixtures/v65/feedback_image.png` - Test PNG
- `output/image_test/` - Generated output (can be deleted)
- `output/image_test.zip` - Final package (can be deleted)

---

*RFC-012 Image Path Verification | 2026-01-24*
