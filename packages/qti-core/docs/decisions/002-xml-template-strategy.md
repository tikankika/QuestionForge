# ADR 002: QTI XML Template Strategy Based on Actual Exports

## Status

Accepted

## Date

2025-10-30

## Context

The QTI Generator must produce QTI 2.2 XML files that are compatible with Inspera Assessment Platform. Inspera implements QTI 2.2 with proprietary extensions via custom namespaces (`xmlns:inspera="http://www.inspera.no/qti"`).

### Problem

No existing documentation fully specifies Inspera's QTI implementation. The QTI 2.2 specification is generic, but Inspera's specific requirements include:

- Custom namespace attributes (`inspera:objectType`, `inspera:defaultLanguage`, etc.)
- Specific response processing patterns
- Particular feedback structures
- Unique scoring template declarations
- Precise manifest metadata format

### Discovery Process

We obtained actual QTI exports from Inspera (stored in `QTI_test1/`) and analyzed the XML structure to reverse-engineer the exact requirements.

### Alternatives Considered

**Option A: Generate from QTI 2.2 Specification Alone**
- ✅ Standards-compliant
- ❌ Would not work in Inspera (missing proprietary extensions)
- ❌ No validation against real-world requirements

**Option B: Use Existing QTI Libraries** (e.g., `qti-package-maker`)
- ✅ Handles QTI 2.1 for Canvas/Moodle
- ❌ Does not support QTI 2.2
- ❌ Does not support Inspera namespace extensions
- ❌ No Inspera-specific templates

**Option C: Template-Based Generation from Inspera Exports** (Selected)
- ✅ Guaranteed compatibility (based on working examples)
- ✅ Includes all required Inspera extensions
- ✅ Precise control over output structure
- ✅ Can validate against real exports
- ❌ Must maintain templates for each question type

## Decision

We will create **XML templates based on direct analysis of Inspera QTI exports**, with placeholders for dynamic content that will be filled by the Python generator.

### Template Structure

Each question type will have a corresponding template in `templates/xml/`:

```
templates/xml/
├── multiple_choice_single.xml
├── multiple_choice_multiple.xml
├── true_false.xml
├── text_entry.xml
├── essay.xml
├── text_area.xml
├── extended_text.xml
├── graphic_gap_match.xml
├── text_entry_graphic.xml
├── composite_editor.xml
├── imsmanifest.xml
└── assessment.xml
```

### Template Format

Templates use `{{PLACEHOLDER}}` syntax for dynamic content:

```xml
<assessmentItem
    adaptive="false"
    identifier="{{IDENTIFIER}}"
    inspera:objectType="content_question_qti2_multiple_choice"
    timeDependent="false"
    title="{{TITLE}}"
    xmlns="http://www.imsglobal.org/xsd/imsqti_v2p2"
    xmlns:inspera="http://www.inspera.no/qti"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="...">

    <responseDeclaration baseType="identifier" cardinality="single" identifier="RESPONSE">
        <correctResponse>
            <value>{{CORRECT_CHOICE_ID}}</value>
        </correctResponse>
        <mapping defaultValue="0">
            <mapEntry mapKey="{{CORRECT_CHOICE_ID}}" mappedValue="{{MAX_SCORE}}"/>
        </mapping>
    </responseDeclaration>

    <!-- ... rest of template ... -->
</assessmentItem>
```

### Research-Based Template Creation

For each question type:
1. Identify example in `QTI_test1/` exports
2. Extract complete XML structure
3. Identify all Inspera-specific attributes
4. Document required elements
5. Create template with placeholders
6. Validate against original exports

## Consequences

### Positive

- **Guaranteed Compatibility**: Templates derived from working Inspera exports ensure output will import correctly
- **Complete Feature Support**: All Inspera-specific features (feedback types, scoring modes, UI hints) are preserved
- **Validation**: Can diff-test generated XML against real exports
- **Documentation**: Templates serve as reference documentation for Inspera's QTI implementation
- **Maintainability**: Clear separation between structure (templates) and content (generator logic)

### Negative

- **Maintenance Burden**: Must update templates if Inspera changes QTI implementation
- **Template Count**: Need separate template for each question type (currently 10+)
- **Reverse Engineering**: Relies on analyzing exports rather than official specification

### Neutral

- Templates are format-specific (cannot easily port to other platforms)
- Python generator must handle placeholder replacement correctly

## Implementation Notes

### Identified Question Types from Exports

From analysis of `QTI_test1/`, we found these `inspera:objectType` values:

1. `content_question_qti2_multiple_choice` - Single-answer MC
2. `content_question_qti2_text_area` - Plain text essay
3. `content_question_qti2_extendedtext` - Rich text essay
4. `content_question_qti2_graphicgapmatch_v2` - Drag-drop on image
5. `content_question_qti2_text_entry_graphic` - Fill-in on image
6. `content_question_qti2_composite_editor` - Mixed question types

### Critical Inspera-Specific Elements

All templates must include:

- **Namespace declaration**: `xmlns:inspera="http://www.inspera.no/qti"`
- **Object type**: `inspera:objectType="content_question_qti2_[TYPE]"`
- **Language**: `inspera:defaultLanguage` and `inspera:supportedLanguages`
- **Template declarations**: `SCORE_EACH_CORRECT`, `SCORE_EACH_WRONG`, `SCORE_ALL_CORRECT`, `SCORE_MINIMUM`, `SCORE_UNANSWERED`
- **Response processing**: Specific condition patterns for scoring and feedback
- **Modal feedback**: Four types (unanswered, correct, wrong, partially_correct)
- **Score bounds**: `inspera:type="max_score_upper_bound"`

### Template Generation Process

1. Read markdown question
2. Select appropriate XML template
3. Populate placeholders with question data
4. Generate choice/response elements dynamically
5. Write complete QTI XML file
6. Create manifest entry

### Validation Strategy

- **Structural validation**: Check against QTI 2.2 XSD schema
- **Export comparison**: Diff against real Inspera exports
- **Round-trip testing**: Import generated XML into Inspera platform

## References

- QTI 2.2 Specification: https://www.imsglobal.org/question/qtiv2p2/imsqti_v2p2.html
- Inspera exports analyzed: `/QTI_test1/InsperaAssessmentExport_*`
- Template research document: `docs/research/2025-10-30-qti-analysis.md`

## Superseded By

None

## Related Decisions

- ADR 001: Markdown Input Format
- ADR 003: Pedagogical Framework Integration
