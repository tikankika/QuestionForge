# Question Set Debugging Guide

This guide helps you debug and validate Question Sets (assessmentTest) before importing to Inspera.

## Quick Validation Checklist

Before importing your Question Set ZIP to Inspera, verify:

- [ ] `inspera:maximumScore` attribute exists in assessmentTest XML
- [ ] `<outcomeDeclaration>` block exists with SCORE identifier
- [ ] `<outcomeProcessing>` block exists
- [ ] Max score matches expected value (section selections × points)
- [ ] All section names are descriptive and unique
- [ ] Selection rules (select="X") are present for randomized sections

## Common Issues and Solutions

### Issue 1: Wrong Maximum Score in Inspera

**Symptoms:**
- Inspera shows decimal scores like 10.394 instead of 10
- Total score doesn't match expected value
- Section scores look like weighted averages

**Root Cause:**
The assessmentTest XML is missing score declarations. Inspera calculates its own scores using unknown heuristics.

**Solution:**
Ensure your generated XML includes:

```xml
<assessmentTest ... inspera:maximumScore="31.0">
  <outcomeDeclaration identifier="SCORE" cardinality="single" baseType="float">
    <defaultValue>
      <value>0</value>
    </defaultValue>
  </outcomeDeclaration>
  ...
  <outcomeProcessing>
    <setOutcomeValue identifier="SCORE">
      <sum>
        <testVariables variableIdentifier="SCORE"/>
      </sum>
    </setOutcomeValue>
  </outcomeProcessing>
</assessmentTest>
```

**Verification:**
```bash
# Check if maximumScore exists
grep "maximumScore" output/*/ID_*-assessment.xml

# Check if outcomeDeclaration exists
grep -A 5 "outcomeDeclaration" output/*/ID_*-assessment.xml
```

### Issue 2: Section Shows Wrong Number of Questions

**Symptoms:**
- Preview shows X questions but different number appear in Inspera
- "Y frågor matchar" in terminal differs from actual selection

**Root Cause:**
Filter logic may have changed, or duplicate prevention is active.

**Solution:**
1. Check the logs during generation:
```bash
python3 scripts/interactive_qti.py 2>&1 | grep "Section"
```

2. Look for lines like:
```
INFO: Section 'remember': 51 questions, select=10, max_score=10.0
```

3. Verify filter logic manually:
```python
# In Python REPL
from src.parser.markdown_parser import MarkdownQuizParser
from pathlib import Path

md_file = Path("your_file.md")
content = md_file.read_text(encoding='utf-8')
parser = MarkdownQuizParser(content)
quiz_data = parser.parse()

# Count questions matching your filters
questions = quiz_data.get('questions', [])
# Apply your filter logic here
```

### Issue 3: Duplicate Questions Across Sections

**Symptoms:**
- Same question appears in multiple sections
- Student sees repeated content

**Root Cause:**
Overlapping filters between sections.

**Solution:**
1. Review your section filters - ensure they're mutually exclusive
2. Use the duplicate prevention feature (enabled by default in interactive mode)
3. Check generation logs for warnings about overlapping pools

### Issue 4: Max Score Calculation Mismatch

**Symptoms:**
- Expected score: 31.0
- Actual score in XML: 61.0
- Sections show more questions than expected

**Root Cause:**
This is usually NOT a bug - the filters match more questions than you think!

**Solution:**
1. Check the generation logs:
```
INFO: Section 'section_name': X questions, select=Y, max_score=Z
```

2. Verify your filter combinations:
   - Remember that OR logic within categories is expansive
   - AND logic between categories is restrictive

3. Common mistake:
   - Filter: `(Understand OR Remember) AND (Medium OR Hard)`
   - This matches ALL Understand OR Remember questions that are Medium OR Hard
   - May be more questions than you expect!

4. If the count is correct but unexpected:
   - Your filters are working correctly
   - Adjust filters to be more restrictive
   - Or accept the actual match count

## Validation Commands

### Check Generated Assessment XML

```bash
# Navigate to your output directory
cd output/YOUR_QUIZ_NAME/

# Check if assessment file exists
ls -l ID_*-assessment.xml

# View the file
cat ID_*-assessment.xml

# Check max score
grep "maximumScore" ID_*-assessment.xml

# Count sections
grep "<assessmentSection" ID_*-assessment.xml | wc -l

# Count question references
grep "<assessmentItemRef" ID_*-assessment.xml | wc -l
```

### Verify Individual Question Scores

```bash
# Check point values in individual question XML files
grep "mappedValue" output/YOUR_QUIZ_NAME/*.xml | grep -v assessment.xml

# Count by point value
grep "mappedValue" output/YOUR_QUIZ_NAME/*-item.xml | grep -o 'mappedValue="[0-9]*"' | sort | uniq -c
```

### Manual Score Calculation

```python
import xml.etree.ElementTree as ET

# Parse the assessment XML
tree = ET.parse('output/YOUR_QUIZ_NAME/ID_XXX-assessment.xml')
root = tree.getroot()

# Extract max score
ns = {'inspera': 'http://ns.inspera.no'}
max_score = root.get('{http://ns.inspera.no}maximumScore')
print(f"Declared max score: {max_score}")

# Count sections and selections
sections = root.findall('.//assessmentSection', {'': 'http://www.imsglobal.org/xsd/imsqti_v2p2'})
print(f"Number of sections: {len(sections)}")

for i, section in enumerate(sections, 1):
    title = section.get('title', f'Section {i}')
    selection = section.find('selection')
    select_count = selection.get('select') if selection is not None else 'all'
    item_refs = section.findall('assessmentItemRef')
    total_items = len(item_refs)

    print(f"Section {i} '{title}': {select_count} from {total_items} questions")
```

## Best Practices

1. **Always check logs during generation**
   - Look for INFO messages about section scores
   - Verify counts match your expectations

2. **Test import with small Question Set first**
   - Create a 5-question test set
   - Verify scoring works correctly
   - Then scale up to full quiz

3. **Document your section filters**
   - Keep notes on what each section should contain
   - Expected question counts
   - Expected max scores

4. **Use descriptive section names**
   - "Enkla frågor om cellbiologi" (good)
   - "Section 1" (bad)

5. **Review generated XML before import**
   - Check that `maximumScore` is correct
   - Verify section structure makes sense
   - Ensure no syntax errors

## Getting Help

If you encounter issues not covered here:

1. Check the main CHANGELOG.md for recent fixes
2. Review `docs/troubleshooting/inspera-import-issues.md`
3. Run the validation script: `python3 scripts/validate_question_set.py`
4. Open an issue on GitHub with:
   - Generation logs
   - Expected vs actual scores
   - Filter configuration used
   - Generated assessment XML (sanitized if needed)
