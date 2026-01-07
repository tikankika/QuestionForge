# Markdown Specification for QTI Question Input

## Overview

This document defines the markdown format used for creating assessment questions that will be converted to QTI 2.2 packages for Inspera. The format is designed to be human-readable, easy to create with Claude Desktop, and structurally complete for automated conversion.

---

## Document Structure

A question bank markdown file consists of:

1. **Metadata Header** (YAML frontmatter)
2. **One or more questions** (markdown sections)

### Basic Template

```markdown
---
test_metadata:
  title: "Test Title"
  identifier: "TEST_001"
  language: "en"
  description: "Brief description of the test"
  subject: "Subject area"
  author: "Author name"
  created_date: "2025-10-30"

assessment_configuration:
  type: "formative"  # or "summative"
  time_limit: 60  # minutes (optional)
  shuffle_questions: true
  shuffle_choices: true

learning_objectives:
  - id: "LO1"
    description: "Students will be able to..."
  - id: "LO2"
    description: "Students will be able to..."
---

# Question 1: [Brief title]

[Question content here...]

---

# Question 2: [Brief title]

[Question content here...]
```

---

## Metadata Header

### Required Fields

```yaml
test_metadata:
  title: "string"           # Display name of the test
  identifier: "string"      # Unique ID (alphanumeric, underscores)
  language: "string"        # ISO 639-1 code (e.g., "en", "sv", "no")
```

### Optional Fields

```yaml
test_metadata:
  description: "string"     # Purpose/description of the test
  subject: "string"         # Subject area/course code
  author: "string"          # Creator name
  created_date: "YYYY-MM-DD"

assessment_configuration:
  type: "formative|summative"
  time_limit: integer       # minutes
  shuffle_questions: boolean
  shuffle_choices: boolean
  feedback_mode: "immediate|deferred|none"
  attempts_allowed: integer

learning_objectives:
  - id: "string"           # Unique objective identifier
    description: "string"   # What students should know/do
  - id: "string"
    description: "string"
```

---

## Supported Question Types

### Implementation Status Overview (v0.2.3)

The table below shows all question types with XML templates available in this repository, along with their current implementation status in the markdown-to-QTI converter.

#### Status Legend

- **[PRODUCTION READY]**: Fully implemented in converter, validated against Inspera exports, ready for production use
- **[BETA]**: Functional with documented limitations; suitable for testing environments
- **[PLANNED v0.3.0]**: XML template in development or converter implementation scheduled for next minor release
- **[PLANNED v0.4.0]**: XML template complete and validated; converter implementation in development

### Complete Question Type Inventory

| Type Code | Description | Auto/Manual Grading | Status | Implementation Notes |
|-----------|-------------|-------------------|--------|---------------------|
| **Production Ready (3 types)** |
| `extended_text` | Essay with rich text editor | Manual | [PRODUCTION READY] | Complete implementation with rubric support |
| `multiple_choice_single` | Single correct answer | Auto | [PRODUCTION READY] | Fully functional with option-specific feedback |
| `text_area` | Short plain text response | Manual | [PRODUCTION READY] | Complete implementation for plain text |
| **Beta (1 type)** |
| `multiple_response` | Select all that apply | Auto | [BETA] | Basic scoring implemented; advanced partial credit mapping planned for v0.3.0 |
| **Planned for v0.3.0 (3 types)** |
| `true_false` | Boolean response (True/False) | Auto | [PLANNED v0.3.0] | XML template in development |
| `fill_blank` | Single fill-in-the-blank | Auto | [PLANNED v0.3.0] | XML template in development; differs from text_entry |
| `matching` | Associate pairs (two columns) | Auto | [PLANNED v0.3.0] | XML template complete (`match.xml`); converter implementation in progress |
| **Advanced Types - Planned for v0.4.0 (9 types)** |
| `inline_choice` | Dropdown selections in text | Auto | [PLANNED v0.4.0] | XML template ready; requires multi-field dropdown logic |
| `text_entry` | Multiple fill-in-the-blank fields | Auto | [PLANNED v0.4.0] | XML template ready; requires string matching for multiple fields |
| `gapmatch` | Drag text/images into gaps | Auto | [PLANNED v0.4.0] | XML template ready; requires directed pair mapping |
| `hotspot` | Click on image regions | Auto | [PLANNED v0.4.0] | XML template ready; requires coordinate-based interaction |
| `graphicgapmatch` | Drag onto image hotspots | Auto | [PLANNED v0.4.0] | XML template ready (`graphicgapmatch_v2.xml`); requires image hotspot mapping |
| `text_entry_graphic` | Fill-in text fields on image | Auto | [PLANNED v0.4.0] | XML template ready; requires positioned text fields |
| `audio_record` | Audio recording response | Manual | [PLANNED v0.4.0] | XML template ready; requires file upload handling |
| `composite_editor` | Mixed interaction types | Hybrid | [PLANNED v0.4.0] | XML template ready; requires multi-interaction aggregation |
| `nativehtml` | Informational content (non-scored) | N/A | [PLANNED v0.4.0] | XML template ready; displays content without interaction |

**Template Coverage**: 16 question types (15 interactive + 1 informational)
**Production Ready**: 3 types (18.75% of templates)
**Beta**: 1 type (6.25% of templates)
**In Development**: 12 types (75% of templates)

### Coverage Analysis

Based on analysis of Inspera QTI exports, the production-ready question types cover the most frequently used interactions:

- **extended_text**: 24.2% of analyzed questions
- **multiple_choice_single**: 16.0% of analyzed questions
- **text_area**: 9.3% of analyzed questions
- **multiple_response**: 3.1% of analyzed questions

**Current Production Coverage**: ~52.6% of common question types
**Projected v0.3.0 Coverage**: ~65% (with true_false, fill_blank, matching)
**Projected v0.4.0 Coverage**: ~87% (with all advanced types)

### Implementation Roadmap

**v0.3.0 Goals**:
- Complete true_false XML template and converter implementation
- Complete fill_blank XML template and converter implementation
- Implement match.xml converter logic (XML template already complete)
- Enhance multiple_response with advanced partial credit mapping

**v0.4.0 Goals**:
- Implement converters for all 9 advanced question types with complete XML templates
- Add multi-field interaction support (inline_choice, text_entry)
- Add image-based interaction support (hotspot, graphicgapmatch, text_entry_graphic)
- Add drag-and-drop interaction support (gapmatch, graphicgapmatch)
- Add file upload support (audio_record)
- Add composite interaction aggregation (composite_editor)

---

## Question Format

Each question is separated by `---` (horizontal rule) and begins with a markdown heading.

### General Structure

```markdown
# Question [N]: [Title]

**Type**: [question_type]
**Identifier**: [UNIQUE_ID]
**Points**: [number]
**Learning Objectives**: [LO1, LO2, ...]
**Bloom's Level**: [Remember|Understand|Apply|Analyze|Evaluate|Create]

## Question Text

[The actual question prompt, can include:]
- Regular text
- **Bold** and *italic* formatting
- Images: ![alt text](path/to/image.png)
- Code blocks
- Mathematical notation (LaTeX)

## Options

[Format varies by question type - see below]

## Answer

[Correct answer specification - varies by type]

## Feedback

### General Feedback
[Feedback shown to all students]

### Correct Response Feedback
[Shown when answer is correct]

### Incorrect Response Feedback
[Shown when answer is incorrect]

### Option-Specific Feedback (optional)
- **A**: [Feedback for choosing option A]
- **B**: [Feedback for choosing option B]
- **C**: [Feedback for choosing option C]
```

---

## Question Types

### 1. Multiple Choice (Single Response)

**Type Code**: `multiple_choice_single`

```markdown
# Question 1: Capital of Sweden

**Type**: multiple_choice_single
**Identifier**: MC_001
**Points**: 1
**Learning Objectives**: LO1
**Bloom's Level**: Remember

## Question Text

What is the capital of Sweden?

## Options

A. Oslo
B. Stockholm
C. Copenhagen
D. Helsinki

## Answer

B

## Feedback

### General Feedback
This question tests your knowledge of European capitals.

### Correct Response Feedback
Correct! Stockholm is the capital and largest city of Sweden.

### Incorrect Response Feedback
Not quite. Remember that Stockholm is located on Sweden's east coast.

### Partially Correct Feedback (optional)
You're on the right track, but please review the answer.

### Unanswered Feedback
Please select an answer before submitting.

### Option-Specific Feedback
- **A**: Oslo is the capital of Norway, not Sweden.
- **B**: Correct! Stockholm has been Sweden's capital since 1634.
- **C**: Copenhagen is the capital of Denmark.
- **D**: Helsinki is the capital of Finland.
```

### 2. Multiple Response (Select All That Apply)

**Type Code**: `multiple_response`

```markdown
# Question 2: Bloom's Taxonomy Levels

**Type**: multiple_response
**Identifier**: MR_002
**Points**: 3
**Learning Objectives**: LO3
**Bloom's Level**: Understand

## Question Text

Which of the following are levels in Bloom's Revised Taxonomy?

## Prompt

Select all that apply.

## Options

A. Remember
B. Memorize
C. Apply
D. Synthesize
E. Evaluate
F. Compute

## Answer

A, C, E

## Scoring

**Points per correct choice**: 1
**Points per incorrect choice**: -0.5
**Maximum score**: 3
**Minimum score**: 0

## Feedback

### General Feedback
Bloom's Revised Taxonomy has six levels: Remember, Understand, Apply, Analyze, Evaluate, Create.

### Correct Response Feedback
Excellent! You correctly identified all the levels from Bloom's Revised Taxonomy.

### Incorrect Response Feedback
Review the six levels of Bloom's Revised Taxonomy. "Memorize," "Synthesize," and "Compute" are not official taxonomy levels.

### Option-Specific Feedback
- **A**: Correct! "Remember" is the foundational level.
- **B**: "Memorize" is not a Bloom's level; the correct term is "Remember."
- **C**: Correct! "Apply" is the third level.
- **D**: "Synthesize" was in the original taxonomy but was replaced by "Create."
- **E**: Correct! "Evaluate" is the fifth level.
- **F**: "Compute" is not a distinct Bloom's level; it's an action verb under "Apply."
```

### 3. True/False

**Type Code**: `true_false`

```markdown
# Question 3: Correlation and Causation

**Type**: true_false
**Identifier**: TF_001
**Points**: 1
**Learning Objectives**: LO4
**Bloom's Level**: Evaluate

## Question Text

True or False: A strong correlation between two variables proves that one causes the other.

## Answer

False

## Feedback

### General Feedback
Understanding the distinction between correlation and causation is fundamental to research interpretation.

### Correct Response Feedback
Correct! Correlation does not imply causation. A third variable or reverse causation may explain the relationship.

### Incorrect Response Feedback
This is false. Correlation indicates association, but does not prove causation. Consider confounding variables and alternative explanations.
```

### 4. Fill-in-the-Blank

**Type Code**: `fill_blank`

```markdown
# Question 4: Statistical Term

**Type**: fill_blank
**Identifier**: FB_001
**Points**: 1
**Learning Objectives**: LO2
**Bloom's Level**: Remember

## Question Text

The ________ is a measure of central tendency calculated by summing all values and dividing by the number of values.

## Answer

mean

## Accepted Alternatives

- average
- arithmetic mean
- arithmetic average

## Matching

**Case sensitive**: false
**Exact match**: false
**Allow spaces**: true

## Feedback

### General Feedback
Measures of central tendency describe the center of a distribution.

### Correct Response Feedback
Correct! The mean (or average) is the sum of values divided by the count.

### Incorrect Response Feedback
The correct answer is "mean" or "average." This is calculated as: (sum of all values) / (number of values).
```

### 5. Text Area (Short Response)

**Type Code**: `text_area`

```markdown
# Question 5: Statistical Definition

**Type**: text_area
**Identifier**: TA_001
**Points**: 2
**Learning Objectives**: LO2
**Bloom's Level**: Understand

## Question Text

In your own words, explain what the standard deviation measures and why it is useful in data analysis.

## Editor Configuration

**Initial lines**: 5
**Field width**: 100%
**Show word count**: true
**Editor prompt**: Type your answer here...

## Feedback

### General Feedback
Standard deviation is a key measure of variability that describes how spread out data values are from the mean.

### Answered Feedback
Thank you for your response. Your answer will be reviewed and graded by the instructor.

### Unanswered Feedback
Please provide an answer to this question.

### Grading Notes for Instructor
Look for:
- Understanding that SD measures variability/spread
- Mention of relationship to the mean
- Recognition that larger SD = more spread out data
- Practical application (e.g., comparing consistency between datasets)

Award full points (2) for complete explanation including all elements.
Award partial credit (1) for basic understanding without full explanation.
```

**Note**: `text_area` is for shorter, plain-text responses without rich formatting. For longer essays with formatting options, use `extended_text` instead.

### 6. Extended Text (Essay / Long Response)

**Type Code**: `extended_text`

```markdown
# Question 5: Research Design Analysis

**Type**: extended_text
**Identifier**: EXT_001
**Points**: 10
**Learning Objectives**: LO5, LO6
**Bloom's Level**: Evaluate

## Question Text

Read the following research scenario:

> A researcher wants to investigate whether meditation improves academic performance.
> She recruits 100 university students and randomly assigns 50 to a meditation group
> (20 minutes daily for 8 weeks) and 50 to a control group. At the end of the study,
> she compares the groups' GPA.

Evaluate this research design by addressing:
1. What type of research design is this?
2. What are the strengths of this design?
3. What are potential limitations or threats to validity?
4. How would you improve the design?

## Editor Configuration

**Initial lines**: 15
**Field width**: 100%
**Show word count**: true
**Maximum words**: 600
**Editor prompt**: Enter your response here...

## Scoring Rubric

### Excellent (9-10 points)
- Correctly identifies experimental design
- Discusses randomization and control group strengths
- Identifies multiple threats (e.g., placebo effect, dropout, measurement)
- Proposes specific, feasible improvements
- Well-organized with clear argumentation

### Good (7-8 points)
- Correctly identifies design type
- Discusses some strengths
- Identifies at least 2 threats to validity
- Proposes improvements
- Generally well-organized

### Satisfactory (5-6 points)
- Identifies design type (may have minor errors)
- Mentions some strengths or limitations
- Proposes at least one improvement
- Basic organization

### Needs Improvement (0-4 points)
- Incorrect or missing design identification
- Limited discussion of strengths/limitations
- No improvements proposed
- Poor organization

## Feedback

### General Feedback
This question assesses your ability to critically evaluate research designs and propose methodological improvements.

### Answered Feedback
Thank you for your response. Your submission has been recorded and will be graded by the instructor.

### Unanswered Feedback
Please provide a response to this question before submitting the assessment.

### Grading Notes for Instructor
Look for:
- Recognition of true experimental design with randomization
- Discussion of internal validity (control group, randomization)
- Threats: placebo effect, expectancy effects, attrition, GPA measurement limitations
- Improvements: blinding, active control group, multiple outcome measures, longer follow-up
```

### 7. Matching

**Type Code**: `matching`

```markdown
# Question 7: Statistical Tests

**Type**: matching
**Identifier**: MATCH_001
**Points**: 3
**Learning Objectives**: LO7
**Bloom's Level**: Understand

## Question Text

Match each research scenario to the appropriate statistical test.

## Premises (Left Column)

1. Comparing mean test scores between two independent groups
2. Examining the relationship between two continuous variables
3. Comparing proportions across three or more categories

## Choices (Right Column)

A. Chi-square test
B. Pearson correlation
C. Independent samples t-test
D. ANOVA
E. Paired samples t-test

## Answer

1 → C
2 → B
3 → A

## Scoring

**Type**: partial_credit
**Points per correct match**: 1
**Minimum score**: 0

## Feedback

### General Feedback
Selecting the appropriate statistical test depends on the type of data and research question.

### Correct Response Feedback
Excellent! You correctly matched all scenarios to their appropriate statistical tests.

### Incorrect Response Feedback
Review the conditions for each test:
- t-test: Compare means between 2 groups
- Correlation: Relationship between 2 continuous variables
- Chi-square: Categorical data, frequency distributions

### Match-Specific Feedback
- **1 → C**: Correct. Independent samples t-test compares means between two independent groups.
- **2 → B**: Correct. Pearson correlation measures linear relationships between continuous variables.
- **3 → A**: Correct. Chi-square tests analyze categorical data across multiple groups.
```

---

## Question Type: Hotspot (Click on Image)

**Type identifier**: `hotspot`

Hotspot questions require students to click on specific areas of an image. Ideal for:
- Anatomy identification (organs, structures)
- Geography (locations on maps)
- Diagram labeling (parts of systems, processes)
- Visual identification tasks

### Required Sections

1. **Type**: `hotspot`
2. **Image**: Image metadata (file path, dimensions, title)
3. **Question Text**: Instructions for the student
4. **Hotspots**: Clickable areas with coordinates and shapes
5. **Feedback**: Standard feedback sections

### Hotspot Format

Each hotspot must specify:
- **Shape**: `rect` (rectangle) or `circle`
- **Coordinates**:
  - Rectangle: `x1,y1,x2,y2` (top-left and bottom-right corners)
  - Circle: `x,y,radius` (center point and radius in pixels)
- **Label**: Descriptive text for the hotspot
- **Correct**: `true` or `false` (only one hotspot should be correct)

### Example: Hotspot Question

```markdown
# Question 7: Identify the Heart

**Type**: hotspot
**Identifier**: HS001
**Points**: 2
**Learning Objectives**: LO1
**Bloom's Level**: Remember

## Question Text

Click on the location of the **heart** in the anatomical diagram below.

## Image

**File**: resources/anatomy_diagram.png
**Canvas Height**: 500
**Title**: Human Anatomy Diagram

## Hotspots

### Hotspot 1
**Shape**: circle
**Coordinates**: 180,200,35
**Label**: Heart
**Correct**: true

### Hotspot 2
**Shape**: rect
**Coordinates**: 250,150,320,220
**Label**: Lungs
**Correct**: false

### Hotspot 3
**Shape**: rect
**Coordinates**: 140,280,200,360
**Label**: Stomach
**Correct**: false

## Feedback

### General Feedback
The heart is a muscular organ located slightly left of center in the chest cavity.

### Correct Response Feedback
Excellent! You correctly identified the heart's location.

### Incorrect Response Feedback
Not quite. The heart is located in the center-left of the chest, between the lungs.

### Unanswered Feedback
Please click on the diagram to select your answer.
```

### Image Configuration Options

- **File**: Relative path to image file (required)
- **Canvas Height**: Height of the interactive canvas in pixels (default: 400)
- **Title**: Descriptive title for accessibility (optional)
- **Logical Name**: Internal identifier (auto-generated from filename if not provided)

---

## Question Type: Match (Two-Column Matching)

**Type identifier**: `match`

Match questions require students to associate items from a left column (premises) with items from a right column (responses). Ideal for:
- Matching terms to definitions
- Pairing concepts with examples
- Associating causes with effects
- Matching statistical tests to scenarios

### Required Sections

1. **Type**: `match`
2. **Question Text**: Instructions for the student
3. **Premises (Left Column)**: Numbered items (1, 2, 3, ...)
4. **Choices (Right Column)**: Lettered items (A, B, C, ...)
5. **Answer**: Correct pairings using → or ->
6. **Scoring**: Partial credit configuration
7. **Feedback**: Standard feedback sections

### Match Format

- **Premises** are numbered: `1.`, `2.`, `3.`, etc.
- **Choices/Responses** are lettered: `A.`, `B.`, `C.`, etc.
- You can have **more choices than premises** (distractor options)
- **Answer format**: `1 → A` or `1 -> A` (one pairing per line)

### Scoring Options

- **Points per correct match**: Points awarded for each correct pairing
- **Points per incorrect match**: Typically 0 or negative
- **Minimum score**: Floor value (typically 0)
- **Maximum score**: Total points when all correct (optional, defaults to num_pairs × points_per_correct)

### Example: Match Question

```markdown
# Question 8: Statistical Tests

**Type**: match
**Identifier**: MATCH001
**Points**: 3
**Learning Objectives**: LO1
**Bloom's Level**: Understand

## Question Text

Match each research scenario to the appropriate statistical test.

## Premises (Left Column)

1. Comparing mean test scores between two independent groups
2. Examining the relationship between two continuous variables
3. Comparing proportions across three or more categories

## Choices (Right Column)

A. Chi-square test
B. Pearson correlation
C. Independent samples t-test
D. ANOVA
E. Paired samples t-test

## Answer

1 → C
2 → B
3 → A

## Scoring

**Type**: partial_credit
**Points per correct match**: 1
**Minimum score**: 0

## Feedback

### General Feedback
Selecting the appropriate statistical test depends on the type of data and research question.

### Correct Response Feedback
Excellent! You correctly matched all scenarios to their appropriate statistical tests.

### Incorrect Response Feedback
Review the conditions for each test:
- t-test: Compare means between 2 groups
- Correlation: Relationship between 2 continuous variables
- Chi-square: Categorical data

### Partially Correct Response Feedback
You got some matches correct. Review the test selection criteria.

### Unanswered Feedback
Please match each scenario to the appropriate statistical test.
```

### Key Features

- **Partial Credit**: Students earn points for each correct match
- **Distractor Options**: Include more choices than premises
- **Flexible Pairing**: Each premise matches to exactly one response
- **Negative Scoring**: Optional penalties for incorrect matches

---

## Question Type: Text Entry (Fill-in-the-Blank)

**Type identifier**: `text_entry`

Text entry questions require students to fill in blanks within the question text. Ideal for:
- Completing formulas or equations
- Filling in key terms or definitions
- Recalling specific facts or values
- Multi-part questions with short answers

### Required Sections

1. **Type**: `text_entry`
2. **Question Text**: Text with `{{BLANK-N}}` markers where N is the blank number
3. **Blanks**: Definition of each blank with correct answer and alternatives
4. **Scoring**: Partial credit configuration
5. **Feedback**: Standard feedback sections

### Blank Format

Each blank must specify:
- **Correct Answer**: The primary correct answer
- **Accepted Alternatives**: Comma-separated list of alternative correct answers (optional)
- **Case Sensitive**: `true` or `false` (default: false)
- **Expected Length**: Number of characters for the input field (default: 15)

### Blank Markers in Question Text

Use `{{BLANK-N}}` markers in the question text where N corresponds to the blank number:
- `{{BLANK-1}}` for the first blank
- `{{BLANK-2}}` for the second blank
- etc.

### Example: Text Entry Question

```markdown
# Question 9: Statistical Formula

**Type**: text_entry
**Identifier**: TE001
**Points**: 3
**Learning Objectives**: LO1
**Bloom's Level**: Remember

## Question Text

Complete the formula for calculating the mean:

The {{BLANK-1}} is calculated by summing all values and dividing by the {{BLANK-2}}. The formula is: x̄ = Σx / {{BLANK-3}}

## Blanks

### Blank 1
**Correct Answer**: mean
**Accepted Alternatives**: average, arithmetic mean
**Case Sensitive**: false
**Expected Length**: 20

### Blank 2
**Correct Answer**: number of observations
**Accepted Alternatives**: sample size, n, N
**Case Sensitive**: false
**Expected Length**: 25

### Blank 3
**Correct Answer**: n
**Accepted Alternatives**: N
**Case Sensitive**: false
**Expected Length**: 5

## Scoring

**Points per correct blank**: 1
**Points per incorrect blank**: 0
**Minimum score**: 0

## Feedback

### General Feedback
The mean (or average) is a measure of central tendency.

### Correct Response Feedback
Excellent! You correctly completed the formula.

### Incorrect Response Feedback
Review the formula for calculating the mean: x̄ = Σx / n

### Partially Correct Response Feedback
You got some blanks correct. Review the definition of mean.

### Unanswered Feedback
Please fill in all blanks to complete the formula.
```

### Key Features

- **Multiple Blanks**: Support for multiple fill-in fields per question
- **Alternative Answers**: Accept multiple correct variations per blank
- **Case Sensitivity**: Configure per blank
- **Partial Credit**: Points awarded for each correct blank
- **String Matching**: Automatic scoring with exact match (or case-insensitive)

### Tips for Creating Text Entry Questions

1. **Keep answers concise**: Single words or short phrases work best
2. **Provide alternatives**: Include common variations (e.g., "mean" and "average")
3. **Use case-insensitive**: Unless capitalization matters (e.g., proper nouns)
4. **Set appropriate field length**: Match the expected answer length

---

## Advanced Features

### Mathematical Notation

Use LaTeX syntax enclosed in `$...$` for inline math or `$$...$$` for display math:

```markdown
## Question Text

Calculate the mean of the following dataset: {2, 4, 6, 8, 10}

The formula for the mean is: $$\bar{x} = \frac{\sum_{i=1}^{n} x_i}{n}$$
```

### Images

Include images using markdown syntax:

```markdown
## Question Text

Examine the graph below:

![Scatterplot showing correlation](images/scatterplot_001.png)

What type of correlation is displayed?
```

**Image Guidelines**:
- Place images in an `images/` folder relative to the markdown file
- Supported formats: PNG, JPG, GIF, SVG
- Include descriptive alt text for accessibility
- Keep file sizes reasonable (<500KB per image)

### Code Blocks

Use fenced code blocks with language specification:

```markdown
## Question Text

What is the output of the following Python code?

\```python
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)

print(factorial(5))
\```
```

### Tables

Use markdown tables for structured data:

```markdown
## Question Text

Based on the data below, calculate the mean for Group A:

| Participant | Group A | Group B |
|-------------|---------|---------|
| P1          | 85      | 78      |
| P2          | 90      | 82      |
| P3          | 78      | 88      |
| P4          | 92      | 85      |
```

---

## Metadata Fields Reference

### Question-Level Metadata

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Type | string | Yes | Question type code (see question types) |
| Identifier | string | Yes | Unique ID (alphanumeric + underscores) |
| Points | number | Yes | Maximum points for question |
| Learning Objectives | list | Yes | One or more LO identifiers |
| Bloom's Level | enum | Yes | One of six taxonomy levels |
| Difficulty | string | No | easy \| medium \| hard |
| Tags | list | No | Custom categorization tags |
| Time Estimate | number | No | Expected time to complete (minutes) |

### Bloom's Level Values

Must be one of:
- `Remember`
- `Understand`
- `Apply`
- `Analyze`
- `Evaluate`
- `Create`

### Assessment Type Values

- `formative`: Practice, learning-focused, low stakes
- `summative`: Grading-focused, evaluative

---

## Validation Rules

The Python parser will validate:

1. **Required fields present**: Type, Identifier, Points, Learning Objectives, Bloom's Level
2. **Unique identifiers**: No duplicate question or option IDs
3. **Valid Bloom's level**: Must match one of six taxonomy levels
4. **Learning objectives exist**: Referenced LOs must be defined in header
5. **Answer format matches type**: Correct answer specification for question type
6. **Points are positive**: Points > 0
7. **Feedback sections present**: At minimum, general feedback required

### Common Validation Errors

**Error**: "Question identifier 'MC_001' is not unique"
**Fix**: Ensure every question has a unique identifier

**Error**: "Learning objective 'LO5' not defined in header"
**Fix**: Add LO5 to the `learning_objectives` section in YAML frontmatter

**Error**: "Invalid Bloom's level 'application'"
**Fix**: Use exact taxonomy term: "Apply" (not "application")

**Error**: "Multiple choice answer must be single letter (A-Z)"
**Fix**: Specify answer as "B" not "b" or "Option B"

---

## Best Practices

### Writing Clear Questions

1. **Be specific**: Avoid ambiguous language
2. **One concept per question**: Don't combine multiple objectives
3. **Avoid negatives**: Don't use "which is NOT..." (confusing)
4. **Use clear language**: Appropriate for student level
5. **Proofread**: Check grammar and spelling

### Creating Good Distractors (Multiple Choice)

1. **Plausible**: Should seem correct to students who don't know the answer
2. **Common errors**: Based on typical misconceptions
3. **Homogeneous**: All options similar length and complexity
4. **No clues**: Avoid "all of the above" or overlapping options

### Writing Effective Feedback

1. **Explain why**: Don't just confirm right/wrong
2. **Reference concepts**: Connect to learning materials
3. **Address misconceptions**: Explain why wrong answers are wrong
4. **Encourage learning**: Provide next steps or resources

### Alignment Check

Before finalizing, verify:

- [ ] Bloom's level matches learning objective verb
- [ ] Question actually tests the stated objective
- [ ] Difficulty is appropriate for student level
- [ ] Feedback supports learning, not just evaluation

---

## Example Complete Question Bank

```markdown
---
test_metadata:
  title: "Introduction to Statistics - Module 1 Quiz"
  identifier: "STAT101_M1_QUIZ"
  language: "en"
  description: "Formative assessment covering descriptive statistics"
  subject: "STAT101"
  author: "Dr. Jane Smith"
  created_date: "2025-10-30"

assessment_configuration:
  type: "formative"
  time_limit: 20
  shuffle_questions: true
  shuffle_choices: true
  feedback_mode: "immediate"
  attempts_allowed: 3

learning_objectives:
  - id: "LO1"
    description: "Define and identify measures of central tendency"
  - id: "LO2"
    description: "Calculate mean, median, and mode for datasets"
  - id: "LO3"
    description: "Interpret measures of variability"
---

# Question 1: Defining the Mean

**Type**: multiple_choice_single
**Identifier**: STAT_M1_Q1
**Points**: 1
**Learning Objectives**: LO1
**Bloom's Level**: Remember

## Question Text

Which of the following best defines the mean?

## Options

A. The middle value when data is ordered
B. The most frequently occurring value
C. The sum of all values divided by the number of values
D. The difference between the highest and lowest values

## Answer

C

## Feedback

### General Feedback
The mean is one of three primary measures of central tendency.

### Correct Response Feedback
Correct! The mean is calculated by summing all values and dividing by the count: $\bar{x} = \frac{\sum x}{n}$

### Incorrect Response Feedback
Review the definitions of measures of central tendency. The mean is also called the average.

### Option-Specific Feedback
- **A**: This describes the median, not the mean.
- **B**: This describes the mode, not the mean.
- **C**: Correct! This is the definition of the mean.
- **D**: This describes the range, which is a measure of variability.

---

# Question 2: Calculating the Mean

**Type**: fill_blank
**Identifier**: STAT_M1_Q2
**Points**: 2
**Learning Objectives**: LO2
**Bloom's Level**: Apply

## Question Text

Calculate the mean of the following dataset: {12, 15, 18, 21, 24}

(Enter your answer as a number)

## Answer

18

## Accepted Alternatives

- 18.0
- 18.00

## Matching

**Case sensitive**: false
**Exact match**: true
**Allow spaces**: false

## Feedback

### General Feedback
To find the mean: (1) sum all values, (2) divide by the count.

### Correct Response Feedback
Correct! (12+15+18+21+24) / 5 = 90 / 5 = 18

### Incorrect Response Feedback
The mean is calculated as: (12+15+18+21+24) / 5 = 18. Make sure you sum all values and divide by the total count (5).

---

# Question 3: Comparing Measures

**Type**: true_false
**Identifier**: STAT_M1_Q3
**Points**: 1
**Learning Objectives**: LO3
**Bloom's Level**: Understand

## Question Text

True or False: The standard deviation is always larger than the variance for the same dataset.

## Answer

False

## Feedback

### General Feedback
Understanding the relationship between variance and standard deviation is important for interpreting variability.

### Correct Response Feedback
Correct! The standard deviation is the square root of the variance, so it is always smaller than or equal to the variance (when variance ≥ 1).

### Incorrect Response Feedback
This is false. The standard deviation is calculated as the square root of the variance: $SD = \sqrt{\text{variance}}$. Therefore, SD ≤ variance when variance ≥ 1.
```

---

## Conversion to QTI

The Python generator will convert this markdown format to QTI 2.2 XML:

1. **YAML header** → QTI test manifest metadata
2. **Question text** → `<itemBody>` with XHTML content
3. **Options** → `<choice>` elements
4. **Answer** → `<responseDeclaration>` with correct response
5. **Feedback** → `<modalFeedback>` elements
6. **Metadata** → Inspera-specific namespace fields

The generator preserves:
- Learning objective mappings
- Bloom's level classifications
- All feedback types
- Mathematical notation (converted to MathML or preserved as LaTeX)
- Images (embedded or linked)

---

## Document Version

**Version**: 1.0
**Last Updated**: October 2025
**Status**: Initial specification
