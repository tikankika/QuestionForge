# QTI Question Types - Complete Inventory

**Generated**: 2025-10-30
**Source**: All QTI export folders
**Total Question Files Analyzed**: 194

---

## Executive Summary

**Folders Analyzed:**
- `QTI_test1/`: 77 question files
- `QTI_downloads_Questions_download_20251030/`: 15 question files
- `QTI_downloads_Question Sets_download_20251030/`: 102 question files

**Unique Question Types Found**: 14

**Coverage**: The analyzed exports provide working examples for 14 of Inspera's question types, covering automatically marked, manually marked, and special-purpose questions.

---

## Complete Question Type Inventory

| # | inspera:objectType | Count | % | Category | Example File | Priority |
|---|-------------------|-------|---|----------|--------------|----------|
| 1 | `content_question_qti2_extendedtext` | 47 | 24.2% | Manual | `QTI_test1/.../ID_358994507-item.xml` | P1 |
| 2 | `content_question_qti2_multiple_choice` | 31 | 16.0% | Auto | `QTI_test1/.../ID_421824591-item.xml` | P1 |
| 3 | `content_question_qti2_text_area` | 18 | 9.3% | Manual | `QTI_test1/.../ID_358999663-item.xml` | P1 |
| 4 | `content_nativehtml` | 14 | 7.2% | Special | `QTI_downloads_Questions.../ID_422659848-item.xml` | P3 |
| 5 | `content_question_qti2_gapmatch` | 13 | 6.7% | Auto | `QTI_downloads_Questions.../ID_422658140-item.xml` | P2 |
| 6 | `content_question_qti2_graphicgapmatch_v2` | 9 | 4.6% | Auto | `QTI_test1/.../ID_139826268-item.xml` | P2 |
| 7 | `content_question_qti2_text_entry_graphic` | 6 | 3.1% | Auto | `QTI_test1/.../ID_139280211-item.xml` | P2 |
| 8 | `content_question_qti2_multiple_response` | 6 | 3.1% | Auto | `QTI_downloads_Question Sets.../ID_182278928-item.xml` | P1 |
| 9 | `content_question_qti2_composite_editor` | 5 | 2.6% | Auto | `QTI_test1/.../ID_139837287-item.xml` | P3 |
| 10 | `content_question_qti2_inline_choice` | 4 | 2.1% | Auto | `QTI_downloads_Questions.../ID_422657539-item.xml` | P2 |
| 11 | `content_question_qti2_hotspot` | 4 | 2.1% | Auto | `QTI_downloads_Questions.../ID_422657904-item.xml` | P2 |
| 12 | `content_question_qti2_text_entry` | 3 | 1.5% | Auto | `QTI_downloads_Question Sets.../ID_196095378-item.xml` | P2 |
| 13 | `content_question_qti2_match` | 3 | 1.5% | Auto | `QTI_downloads_Questions.../ID_422659389-item.xml` | P2 |
| 14 | `content_question_qti2_audio_record` | 1 | 0.5% | Manual | `QTI_downloads_Questions.../ID_422653357-item.xml` | P3 |

**Total**: 194 questions across 14 types

---

## Category Classification

### Automatically Marked (Auto-Scoring)
Questions with automated scoring logic.

| Type | Common Name | Description | Count |
|------|-------------|-------------|-------|
| `multiple_choice` | Multiple Choice (Single) | Select one correct answer | 31 |
| `multiple_response` | Multiple Choice (Multiple) | Select multiple correct answers | 6 |
| `gapmatch` | Gap Match / Drag-Drop Text | Drag text labels into gaps | 13 |
| `graphicgapmatch_v2` | Graphic Gap Match | Drag labels onto image hotspots | 9 |
| `text_entry` | Text Entry (Inline) | Fill-in-the-blank inline | 3 |
| `text_entry_graphic` | Text Entry on Graphic | Fill-in text boxes on image | 6 |
| `inline_choice` | Inline Choice (Dropdown) | Select from dropdown menus | 4 |
| `hotspot` | Hotspot | Click areas on an image | 4 |
| `match` | Matching | Match items between two lists | 3 |
| `composite_editor` | Composite | Mixed question types in one item | 5 |

**Subtotal**: 84 questions (43.3%)

### Manually Marked (Requires Grading)
Questions requiring instructor evaluation.

| Type | Common Name | Description | Count |
|------|-------------|-------------|-------|
| `extendedtext` | Extended Text / Essay | Rich text editor, long-form response | 47 |
| `text_area` | Text Area | Plain text, short-form response | 18 |
| `audio_record` | Audio Record | Voice recording response | 1 |

**Subtotal**: 66 questions (34.0%)

### Special Purpose
Questions with unique characteristics.

| Type | Common Name | Description | Count |
|------|-------------|-------------|-------|
| `nativehtml` | Native HTML | Custom HTML content | 14 |

**Subtotal**: 14 questions (7.2%)

---

## Priority Implementation Ranking

### Priority 1 (Essential - 55.7% of questions)
**Implement First** - Cover majority of use cases

1. **Extended Text** (47 questions, 24.2%)
   - Rich text editor
   - Manual grading
   - Example: `QTI_test1/InsperaAssessmentExport_968954738_359001188/ID_358994507-item.xml`

2. **Multiple Choice - Single** (31 questions, 16.0%)
   - Single correct answer
   - Automatic scoring
   - Example: `QTI_test1/InsperaAssessmentExport_2061233917_422217867/ID_421824591-item.xml`

3. **Text Area** (18 questions, 9.3%)
   - Plain text
   - Manual grading
   - Example: `QTI_test1/InsperaAssessmentExport_968954738_359001188/ID_358999663-item.xml`

4. **Multiple Response** (6 questions, 3.1%)
   - Multiple correct answers
   - Automatic scoring
   - Example: `QTI_downloads_Question Sets_download_20251030/.../ID_182278928-item.xml`

### Priority 2 (Important - 24.2% of questions)
**Implement Second** - Common interactive types

5. **Gap Match** (13 questions, 6.7%)
   - Drag text into gaps
   - Example: `QTI_downloads_Questions_download_20251030/.../ID_422658140-item.xml`

6. **Graphic Gap Match** (9 questions, 4.6%)
   - Drag onto image
   - Example: `QTI_test1/InsperaAssessmentExport_968954738_359001188/ID_139826268-item.xml`

7. **Text Entry Graphic** (6 questions, 3.1%)
   - Fill-in on image
   - Example: `QTI_test1/InsperaAssessmentExport_968954738_359001188/ID_139280211-item.xml`

8. **Inline Choice** (4 questions, 2.1%)
   - Dropdown selections
   - Example: `QTI_downloads_Questions_download_20251030/.../ID_422657539-item.xml`

9. **Hotspot** (4 questions, 2.1%)
   - Click on image
   - Example: `QTI_downloads_Questions_download_20251030/.../ID_422657904-item.xml`

10. **Text Entry** (3 questions, 1.5%)
    - Inline fill-in
    - Example: `QTI_downloads_Question Sets_download_20251030/.../ID_196095378-item.xml`

11. **Match** (3 questions, 1.5%)
    - Match pairs
    - Example: `QTI_downloads_Questions_download_20251030/.../ID_422659389-item.xml`

### Priority 3 (Advanced - 10.3% of questions)
**Implement Last** - Specialized or complex

12. **Native HTML** (14 questions, 7.2%)
    - Custom HTML content
    - Example: `QTI_downloads_Questions_download_20251030/.../ID_422659848-item.xml`

13. **Composite Editor** (5 questions, 2.6%)
    - Mixed question types
    - Example: `QTI_test1/InsperaAssessmentExport_968954738_359001188/ID_139837287-item.xml`

14. **Audio Record** (1 question, 0.5%)
    - Voice response
    - Example: `QTI_downloads_Questions_download_20251030/.../ID_422653357-item.xml`

---

## Mapping to Inspera Official Names

Based on Inspera support documentation structure:

### Automatically Marked
- Multiple Choice → `content_question_qti2_multiple_choice`
- Multiple Response → `content_question_qti2_multiple_response`
- Text Entry → `content_question_qti2_text_entry`
- Inline Choice → `content_question_qti2_inline_choice`
- Matching/Pairing → `content_question_qti2_match`
- Gap Match → `content_question_qti2_gapmatch`
- Drag and Drop → `content_question_qti2_gapmatch`
- Hotspot → `content_question_qti2_hotspot`
- Graphic Gap Match → `content_question_qti2_graphicgapmatch_v2`
- Inline Gap Match → `content_question_qti2_gapmatch` (variant)
- Graphic Text Entry → `content_question_qti2_text_entry_graphic`
- Composite → `content_question_qti2_composite_editor`

### Manually Marked
- Essay → `content_question_qti2_extendedtext`
- Text Area → `content_question_qti2_text_area`
- Audio Record → `content_question_qti2_audio_record`

### Special
- Native HTML → `content_nativehtml`

---

## Missing Types (Not Found in Exports)

Based on Inspera UI screenshots, these types exist but no examples in our exports:

**Automatically Marked:**
- True/False (likely a variant of `multiple_choice` with 2 options)
- Numeric Entry
- Math Entry
- Numerical Simulation

**Manually Marked:**
- Programming
- Math Working
- Upload Assignment

**Oral:**
- Oral

**Not Marked:**
- Document
- Form

**Strategy**: These can be inferred from specification or requested from Inspera support.

---

## Next Steps

### Phase 1: Analysis (Current)
- [x] Inventory all question types
- [ ] Fetch Inspera official documentation
- [ ] Document exact XML structure for each type

### Phase 2: Template Extraction
- [ ] Extract P1 templates (Extended Text, Multiple Choice, Text Area, Multiple Response)
- [ ] Extract P2 templates (Gap Match, Graphic Gap Match, etc.)
- [ ] Extract P3 templates (Native HTML, Composite, Audio Record)
- [ ] Create templates/xml/README.md documenting each template

### Phase 3: Validation
- [ ] Validate templates against QTI 2.2 XSD schema
- [ ] Test round-trip: markdown → XML → Inspera import
- [ ] Document any Inspera-specific quirks

---

## File Locations Reference

### QTI_test1/
**Primary Types**:
- Extended Text (multiple examples)
- Multiple Choice (26 examples in one export)
- Text Area
- Graphic Gap Match v2
- Text Entry Graphic
- Composite Editor

**Path Pattern**: `QTI_test1/InsperaAssessmentExport_*/ID_*-item.xml`

### QTI_downloads_Questions_download_20251030/
**Primary Types**:
- Native HTML
- Gap Match
- Inline Choice
- Hotspot
- Match
- Audio Record
- Graphic Gap Match v2
- Text Entry Graphic

**Path Pattern**: `QTI_downloads_Questions_download_20251030/InsperaAssessmentExport_*/ID_*-item.xml`

### QTI_downloads_Question Sets_download_20251030/
**Primary Types**:
- Extended Text (largest collection)
- Multiple Choice
- Multiple Response
- Text Entry
- Text Area

**Path Pattern**: `QTI_downloads_Question Sets_download_20251030/InsperaAssessmentExport_*/ID_*-item.xml`

---

## Document Version

**Version**: 1.0
**Last Updated**: 2025-10-30
**Status**: Complete inventory - ready for template extraction
