# QTI 2.2 Analysis for Inspera Platform

**Date**: 2025-10-30
**Analyst**: Development Team
**Source**: Inspera QTI exports in `QTI_test1/` folder
**Purpose**: Reverse-engineer Inspera's QTI 2.2 implementation to create accurate XML templates

---

## Executive Summary

Analyzed 50+ QTI 2.2 XML files exported from Inspera Assessment Platform to identify:
- 6 distinct question types with working examples
- Inspera-specific namespace requirements and attributes
- Complete XML structure patterns for template creation
- Manifest and assessment-level structures

**Key Finding**: Inspera implements QTI 2.2 with proprietary extensions via `xmlns:inspera` namespace. Standard QTI tools will not work; custom templates are required.

---

## Question Types Identified

### 1. Multiple Choice (Single Answer)
**Type**: `content_question_qti2_multiple_choice`
**Example**: `QTI_test1/InsperaAssessmentExport_765625288_422217867/ID_421824589-item.xml`
**Frequency**: 30+ instances across exports

**Structure**:
```xml
<responseDeclaration baseType="identifier" cardinality="single" identifier="RESPONSE">
    <correctResponse>
        <value>rId1</value>
    </correctResponse>
    <mapping defaultValue="0">
        <mapEntry mapKey="rId1" mappedValue="1"/>
    </mapping>
</responseDeclaration>

<itemBody inspera:defaultLanguage="sv_se" inspera:supportedLanguages="sv_se">
    <choiceInteraction maxChoices="1" responseIdentifier="RESPONSE" shuffle="true">
        <prompt/>
        <simpleChoice identifier="rId0"><p>Option A</p></simpleChoice>
        <simpleChoice identifier="rId1"><p>Option B</p></simpleChoice>
    </choiceInteraction>
</itemBody>
```

**Scoring**: Simple mapping (1 point for correct, 0 for wrong)
**Feedback Types**: unanswered | correct | wrong | partially_correct

---

### 2. Text Area (Plain Text Essay)
**Type**: `content_question_qti2_text_area`
**Example**: `QTI_test1/InsperaAssessmentExport_968954738_359001188/ID_359000964-item.xml`
**Frequency**: 4+ instances

**Structure**:
```xml
<responseDeclaration baseType="string" cardinality="single" identifier="RESPONSE">
</responseDeclaration>

<itemBody>
    <extendedTextInteraction
        autoExpand="true"
        inspera:variant="textarea"
        usePlainText="true"
        initialNumberOfLines="3"
        responseIdentifier="RESPONSE">
    </extendedTextInteraction>
</itemBody>
```

**Scoring**: Manual grading (no automatic scoring)
**Features**: Multiple response fields possible, line count configurable

---

### 3. Extended Text (Rich Text Editor)
**Type**: `content_question_qti2_extendedtext`
**Example**: `QTI_test1/InsperaAssessmentExport_968954738_359001188/ID_358994507-item.xml`
**Frequency**: 3+ instances

**Structure**:
```xml
<extendedTextInteraction
    usePlainText="false"
    inspera:editorToolbar="default"
    inspera:showWordCount="true"
    expectedLength="0">
</extendedTextInteraction>
```

**Features**:
- Rich text formatting toolbar
- Embedded media support
- Word count tracking
- `inspera:maxWords` attribute for limits

---

### 4. Graphic Gap Match (Drag-and-Drop on Image)
**Type**: `content_question_qti2_graphicgapmatch_v2`
**Example**: `QTI_test1/InsperaAssessmentExport_968954738_359001188/ID_357901008-item.xml`
**Frequency**: 2+ instances

**Structure**:
```xml
<responseDeclaration baseType="directedPair" cardinality="multiple" identifier="RESPONSE">
    <correctResponse>
        <value>A1 GAP1</value>
        <value>A2 GAP2</value>
    </correctResponse>
</responseDeclaration>

<graphicGapMatchInteraction>
    <object class="background" data="resources/image.png" type="image/png"/>
    <gapText identifier="A1">Label 1</gapText>
    <gapText identifier="A2">Label 2</gapText>
    <associableHotspot coords="x,y,w,h" shape="rect" identifier="GAP1"/>
    <associableHotspot coords="x,y,w,h" shape="rect" identifier="GAP2"/>
</graphicGapMatchInteraction>
```

**Scoring**:
- `SCORE_EACH_CORRECT`: Points per correct pair (e.g., 2 points)
- `SCORE_EACH_WRONG`: Penalty for wrong pairs (e.g., -1 points)
- `SCORE_MINIMUM`: Floor (e.g., 0)

**Features**:
- Reusable labels: `inspera:reuseAlternatives="true"`
- Position tokens: `inspera:tokenPosition="right"`

---

### 5. Text Entry Graphic (Fill-in-Blank on Image)
**Type**: `content_question_qti2_text_entry_graphic`
**Example**: `QTI_test1/InsperaAssessmentExport_968954738_359001188/ID_139280211-item.xml`
**Frequency**: 2+ instances

**Structure**:
```xml
<responseDeclaration baseType="string" cardinality="single" identifier="RESPONSE-1">
</responseDeclaration>

<div class="overlayContainer" inspera:style="position:absolute;top:100px;left:50px;">
    <textEntryInteraction
        expectedLength="17"
        inspera:expandAutomatically="true"
        responseIdentifier="RESPONSE-1">
    </textEntryInteraction>
</div>
<img src="resources/image.png"/>
```

**Answer Matching**:
```xml
<stringMatch caseSensitive="false" inspera:ignoredCharacters=" ">
    <variable identifier="RESPONSE-1"/>
    <baseValue baseType="string">correct answer</baseValue>
</stringMatch>
```

**Features**:
- Multiple correct answer variants (OR logic)
- Case-insensitive matching
- Character ignoring (spaces, punctuation)
- Absolute positioning on image

---

### 6. Composite Editor (Mixed Question Types)
**Type**: `content_question_qti2_composite_editor`
**Example**: `QTI_test1/InsperaAssessmentExport_968954738_359001188/ID_139828593-item.xml`
**Frequency**: 2+ instances

**Structure**: Combines multiple interaction types in single item
- Text entry fields (fill-in-blank)
- Choice interactions (multiple choice)
- Mixed response declarations

**Scoring**: Aggregate scoring across all components

---

## Inspera-Specific Namespace Requirements

### Required Namespace Declaration
```xml
<assessmentItem
    xmlns="http://www.imsglobal.org/xsd/imsqti_v2p2"
    xmlns:inspera="http://www.inspera.no/qti"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.imsglobal.org/xsd/imsqti_v2p2
                        http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_v2p2.xsd">
```

### Critical Inspera Attributes

| Attribute | Purpose | Example Values |
|-----------|---------|----------------|
| `inspera:objectType` | Question type identifier | `content_question_qti2_multiple_choice` |
| `inspera:defaultLanguage` | Default UI language | `sv_se`, `en`, `no` |
| `inspera:supportedLanguages` | Available languages | `sv_se`, `en` |
| `inspera:variant` | UI variant | `textarea`, `text` |
| `inspera:fieldWidth` | Field width | `100%`, `50%` |
| `inspera:showWordCount` | Display word count | `true`, `false` |
| `inspera:expandAutomatically` | Auto-expand fields | `true`, `false` |
| `inspera:editorToolbar` | Toolbar configuration | `default`, `minimal` |
| `inspera:ignoredCharacters` | Characters to ignore in matching | `" "`, `".,!?"` |
| `inspera:style` | CSS styling | `position:absolute;top:100px;left:50px;` |
| `inspera:type` | Special processing type | `max_score_upper_bound`, `min_score_lower_bound` |
| `inspera:tokenPosition` | Token placement | `right`, `left`, `top`, `bottom` |
| `inspera:reuseAlternatives` | Allow label reuse | `true`, `false` |
| `inspera:gapSize` | Gap sizing mode | `individualSize`, `uniform` |

---

## Standard Structure Pattern

All question items follow this structure:

1. **Header**: `<assessmentItem>` with namespaces and attributes
2. **Response Declaration(s)**: Define answer capture and correct responses
3. **Outcome Declarations**: Define SCORE and FEEDBACK outcomes
4. **Template Declarations**: Define scoring configuration variables
5. **Item Body**: Question content and interactions
6. **Response Processing**: Scoring and feedback logic
7. **Modal Feedback**: Feedback messages

### Template Declarations (Common to All)

```xml
<templateDeclaration baseType="float" cardinality="single" identifier="SCORE_EACH_CORRECT">
    <defaultValue><value>1</value></defaultValue>
</templateDeclaration>

<templateDeclaration baseType="float" cardinality="single" identifier="SCORE_EACH_WRONG">
    <defaultValue><value>0</value></defaultValue>
</templateDeclaration>

<templateDeclaration baseType="float" cardinality="single" identifier="SCORE_ALL_CORRECT">
    <defaultValue><value/></defaultValue>
</templateDeclaration>

<templateDeclaration baseType="float" cardinality="single" identifier="SCORE_MINIMUM">
    <defaultValue><value/></defaultValue>
</templateDeclaration>

<templateDeclaration baseType="float" cardinality="single" identifier="SCORE_UNANSWERED">
    <defaultValue><value>0</value></defaultValue>
</templateDeclaration>
```

---

## Response Processing Patterns

### Pattern 1: Check for Unanswered
```xml
<responseCondition>
    <responseIf>
        <and>
            <isNull><variable identifier="RESPONSE"/></isNull>
        </and>
        <setOutcomeValue identifier="SCORE">
            <variable identifier="SCORE_UNANSWERED"/>
        </setOutcomeValue>
    </responseIf>
    <responseElse>
        <!-- Scoring logic -->
    </responseElse>
</responseCondition>
```

### Pattern 2: Score Bounds Enforcement
```xml
<responseCondition inspera:type="max_score_upper_bound">
    <responseIf>
        <and>
            <gte>
                <variable identifier="SCORE"/>
                <baseValue baseType="float">1.0</baseValue>
            </gte>
        </and>
        <setOutcomeValue identifier="SCORE">
            <baseValue baseType="float">1.0</baseValue>
        </setOutcomeValue>
    </responseIf>
</responseCondition>
```

---

## Manifest Structure

**File**: `imsmanifest.xml`

```xml
<manifest version="1.1" identifier="MANIFEST">
  <metadata>
    <imsmd:lom>
      <imsmd:lifecycle>
        <imsmd:status>Draft</imsmd:status>
      </imsmd:lifecycle>
      <imsmd:classification>
        <imsmd:taxonpath>
          <imsmd:taxon>
            <imsmd:id>deployEnv</imsmd:id>
            <imsmd:entry>prod</imsmd:entry>
          </imsmd:taxon>
        </imsmd:taxonpath>
      </imsmd:classification>
    </imsmd:lom>
  </metadata>
  <resources>
    <resource identifier="ID_XXX" type="imsqti_item_xmlv2p2" href="ID_XXX-item.xml">
      <metadata>
        <imsmd:classification>
          <imsmd:taxonpath>
            <imsmd:taxon>
              <imsmd:id>objectType</imsmd:id>
              <imsmd:entry>content_question_qti2_[TYPE]</imsmd:entry>
            </imsmd:taxon>
          </imsmd:taxonpath>
        </imsmd:classification>
      </metadata>
      <file href="ID_XXX-item.xml"/>
    </resource>
  </resources>
</manifest>
```

---

## Assessment Structure

**File**: `ID_XXX-assessment.xml`

```xml
<assessmentTest identifier="ID_XXX" title="Test Title">
  <testPart identifier="test-part-XXX" navigationMode="nonlinear" submissionMode="simultaneous">
    <assessmentSection identifier="section-1" title="Section 1">
      <assessmentItemRef href="ID_ITEM1-item.xml" identifier="ID_ITEM1"/>
      <assessmentItemRef href="ID_ITEM2-item.xml" identifier="ID_ITEM2"/>
    </assessmentSection>
  </testPart>
</assessmentTest>
```

**Navigation Modes**:
- `nonlinear`: Students can jump between questions
- `linear`: Must answer sequentially

**Submission Modes**:
- `simultaneous`: All answers submitted together
- `individual`: Each question submitted separately

---

## Complete Question Types from UI Screenshots

From Inspera interface, additional types available (not all in exports):

### Automatically Marked
1. ✅ Multiple Choice (single) - HAVE EXAMPLE
2. ⚠️ Multiple Response (multiple) - NEED TO CREATE
3. ⚠️ Text Entry (inline fill-in) - SIMILAR TO TEXT_ENTRY_GRAPHIC
4. ⚠️ Numeric Entry - NOT IN EXPORTS
5. ⚠️ Math Entry - NOT IN EXPORTS
6. ⚠️ Inline Choice (dropdown) - NOT IN EXPORTS
7. ⚠️ True/False - SIMPLE MC VARIANT
8. ⚠️ Matching/Pairing - NOT IN EXPORTS
9. ✅ Composite - HAVE EXAMPLE
10. ⚠️ Drag and Drop - SIMILAR TO GRAPHIC_GAP_MATCH
11. ⚠️ Hotspot - NOT IN EXPORTS
12. ✅ Graphic Gap Match - HAVE EXAMPLE
13. ⚠️ Inline Gap Match - NOT IN EXPORTS
14. ⚠️ Graphic Text Entry - HAVE EXAMPLE
15. ⚠️ Numerical Simulation - NOT IN EXPORTS

### Manually Marked
16. ✅ Essay - HAVE AS EXTENDED_TEXT
17. ✅ Text Area - HAVE EXAMPLE
18. ⚠️ Upload Assignment - NOT IN EXPORTS
19. ⚠️ Programming - NOT IN EXPORTS
20. ⚠️ Math Working - NOT IN EXPORTS
21. ⚠️ Audio Record - NOT IN EXPORTS

### Oral
22. ⚠️ Oral - NOT IN EXPORTS

### Not Marked
23. ⚠️ Document - NOT IN EXPORTS
24. ⚠️ Form - NOT IN EXPORTS

---

## Recommendations

### Priority 1: Create Templates for Verified Types
- Multiple Choice (single) ✅
- Text Area ✅
- Extended Text ✅
- Graphic Gap Match (if needed)
- Text Entry Graphic (if needed)

### Priority 2: Infer Templates from Specification
For types not in exports but visible in UI:
- Multiple Response (likely similar to MC with `cardinality="multiple"`)
- True/False (likely MC variant with 2 choices)
- Numeric Entry (likely `baseType="float"`)

### Priority 3: Request Additional Exports
- Contact Inspera support for example exports of missing types
- Export sample questions from Inspera UI for each type

---

## Validation Strategy

1. **Structural Validation**: Validate against QTI 2.2 XSD schema
2. **Namespace Validation**: Ensure all Inspera attributes are present
3. **Export Comparison**: Diff generated XML against real exports
4. **Import Testing**: Test import into Inspera platform

---

## Files Analyzed

**Total**: 50+ XML files across 3 assessment exports

**Export 1**: `/QTI_test1/InsperaAssessmentExport_968954738_359001188/`
- 16 question items
- 1 assessment file
- 1 manifest file
- Types: text_area, extendedtext, graphicgapmatch_v2, text_entry_graphic, composite_editor

**Export 2**: `/QTI_test1/InsperaAssessmentExport_765625288_422217867/`
- 26 question items
- 1 assessment file
- 1 manifest file
- Types: primarily multiple_choice

**Export 3**: `/QTI_test1/InsperaAssessmentExport_2061233917_422217867/`
- Similar to Export 2

---

## Next Steps

1. Create XML templates for verified question types
2. Document template structure in `templates/xml/README.md`
3. Build Python generator to populate templates
4. Implement validation against QTI 2.2 schema
5. Test round-trip: markdown → XML → Inspera import

---

## References

- QTI 2.2 Specification: https://www.imsglobal.org/question/qtiv2p2/imsqti_v2p2.html
- Inspera Platform: https://www.inspera.com/
- Export Location: `/path/to/qti-generator/QTI_test1/`

---

**Document Version**: 1.0
**Last Updated**: 2025-10-30
**Status**: Complete - ready for template creation
