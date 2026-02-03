# Universal QTI Generator Input Specification

**Purpose**: This is THE MASTER TEMPLATE showing the EXACT markdown format required for the Python QTI Generator to create valid QTI 2.2 XML files for Inspera import.

**Universality**: This specification works for:
- ✅ **All subjects**: Mathematics, Science, History, Languages, Arts, Engineering, Medicine, etc.
- ✅ **All educational levels**: Gymnasium (Gy11/GY25), Högskola, Universitet (Bachelor, Master, PhD)
- ✅ **All assessment types**: Formative, Summative, Diagnostic, Practice

**What determines complexity**: NOT the format (which stays identical), but YOUR content:
- Question difficulty and depth
- Bloom's Taxonomy level (Remember → Create)
- Learning objectives aligned to your curriculum
- Points assigned per question

---

## 📐 THE FORMAT IS UNIVERSAL - THE CONTENT IS YOURS

**Same Format Example:**

**Gymnasium (Simple):**
```markdown
# Question 1: Basic Photosynthesis

**Type**: multiple_choice_single
**Identifier**: GYM_Q001
**Points**: 1
**Bloom's Level**: Remember

## Question Text
What happens during photosynthesis?
```

**University (Advanced):**
```markdown
# Question 1: Photosystem II Electron Transport

**Type**: multiple_choice_single
**Identifier**: UNI_Q001
**Points**: 3
**Bloom's Level**: Analyze

## Question Text
During quantitative analysis of Photosystem II in *Arabidopsis*, P680+ reduction rate decreases at pH 6.2 vs pH 7.4. What is the most likely molecular explanation?
```

**→ SAME FORMAT, DIFFERENT CONTENT COMPLEXITY!**

---

## ✅ EXACT FORMAT SPECIFICATION

### 1. File Header - YAML Frontmatter (REQUIRED)

**Location**: Top of file
**Delimiters**: Three dashes `---` on separate lines

```yaml
---
test_metadata:
  title: "[Your Assessment Title]"
  identifier: "[UNIQUE_TEST_ID]"  # Examples: MATH101_EXAM, BIOG_QUIZ_2025
  language: "[ISO-CODE]"  # sv, en, no, da, fi, etc.
  description: "[Brief description of assessment purpose and coverage]"
  subject: "[Course Code or Subject Area]"
  author: "[Your Name]"
  created_date: "[YYYY-MM-DD]"

assessment_configuration:
  type: "[formative or summative]"
  time_limit: [minutes]  # Optional, use null if no limit
  shuffle_questions: [true or false]
  shuffle_choices: [true or false]
  feedback_mode: "[immediate, deferred, or none]"
  attempts_allowed: [number or unlimited]

learning_objectives:
  - id: "LO1"
    description: "[Students will be able to... / Eleven ska kunna...]"
  - id: "LO2"
    description: "[Students will be able to... / Studenten ska kunna...]"
  - id: "LO3"
    description: "[Your learning objective description]"
  # Add as many as needed (typically 5-15 for a complete assessment)
---
```

**Examples for Different Subjects:**

**Mathematics:**
```yaml
learning_objectives:
  - id: "LO1"
    description: "Calculate derivatives of polynomial functions"
  - id: "LO2"
    description: "Apply chain rule to composite functions"
```

**History:**
```yaml
learning_objectives:
  - id: "LO1"
    description: "Analyze causes of the French Revolution"
  - id: "LO2"
    description: "Evaluate impact of Enlightenment on modern democracy"
```

**Language (Swedish):**
```yaml
learning_objectives:
  - id: "LO1"
    description: "Konjugera oregelbundna verb i presens och preteritum"
  - id: "LO2"
    description: "Analysera grammatiska strukturer i autentiska texter"
```

---

## 📋 REQUIRED vs OPTIONAL FIELDS

### Required Fields (BB6 v3.0 Strict):

**Per Question:**
- `**Type**:` - Question type (must be exact spelling)
- `**Identifier**:` - Unique ID for the question
- `**Points**:` - Point value
- `**Tags**:` - Comma-separated metadata (see BB6 specification below)

**Per File (YAML frontmatter):**
- `title` - Assessment title
- `identifier` - Unique test ID
- `language` - ISO language code

### BB6 v3.0 Tags Field Specification (REQUIRED)

**Format:** `**Tags**: CourseCode, LearningContentWords, BloomLevel, Difficulty, [Keywords]`

**MUST include:**
1. **Course Code** (e.g., EXAMPLE_COURSE, TRA265)
2. **Learning Content Words** (e.g., Celltyper, Prokaryot, Eukaryot)
3. **Bloom's Level** - ONE of: Remember, Understand, Apply, Analyze, Evaluate, Create
4. **Difficulty** - ONE of: Easy, Medium, Hard

**Example:**
```markdown
**Tags**: EXAMPLE_COURSE, Celltyper, Prokaryot, Eukaryot, Cellkärna, Understand, Easy
```

**How it works:**
✅ Each tag becomes a **searchable label** in Inspera question bank
✅ Enables filtering by course, topic, Bloom's level, difficulty
✅ Supports curriculum alignment and reporting
✅ Single source of truth for all question metadata

**IMPORTANT:**
❌ Do NOT use separate `**Learning Objectives**:` or `**Bloom's Level**:` fields
❌ These are NO LONGER supported in BB6 v3.0
✅ Put everything in the `**Tags**:` field

See `docs/BB6_STRICT_METADATA_SPEC.md` for complete specification.

---

## 📝 FEEDBACK FORMAT: Two Acceptable Approaches

### IMPORTANT: Inspera Platform Behavior

Inspera displays the **SAME feedback text** to all students regardless of their response (correct, incorrect, partial, or unanswered). This is an Inspera-specific requirement, not part of the QTI 2.2 standard.

The QTI Generator ensures Inspera compatibility by using **identical feedback content** for all response states, regardless of which format you use in your markdown.

### Option 1: Simple Format ✅ (Recommended)

Write only **General Feedback** - the generator automatically duplicates it for all states:

```markdown
## Feedback

### General Feedback
Your comprehensive feedback that works for all students.
```

**Advantages:**
- ✅ Less writing (no duplication needed)
- ✅ Faster authoring workflow
- ✅ Generator handles duplication automatically
- ✅ Works perfectly with Inspera
- ✅ Passes BB6 v3.0 validation

**How it works:** The generator uses this fallback chain:
1. If `### Correct Response Feedback` exists → use it for ALL states
2. Otherwise, if `### General Feedback` exists → use it for ALL states
3. Otherwise → use default text ('Correct!', 'Incorrect.', etc.)

### Option 2: Unified Format ✅ (Explicit Control)

Write all subsections (content typically identical due to Inspera requirement):

```markdown
## Feedback

### General Feedback
Your comprehensive feedback that works for all students.

### Correct Response Feedback
Your comprehensive feedback that works for all students.

### Incorrect Response Feedback
Your comprehensive feedback that works for all students.

### Partially Correct Response Feedback
Your comprehensive feedback that works for all students.

### Unanswered Feedback
Your comprehensive feedback that works for all students.
```

**Advantages:**
- ✅ Explicit control over each state
- ✅ Can use different wording if desired (though Inspera shows same text)
- ✅ Passes BB6 v3.0 validation

**Note:** For question types that support partial credit (`multiple_response`, `text_entry`, `inline_choice`, `match`, `graphicgapmatch_v2`, `text_entry_graphic`), include the `### Partially Correct Response Feedback` subsection.

### Preprocessing Option (Optional)

If you prefer to write simple format and convert to unified format:

```bash
python3 main.py input.md output.zip --add-feedback --language sv
```

The `--add-feedback` flag automatically expands simple feedback to unified format by duplicating the General Feedback content to all required subsections.

### Why Both Formats Work

1. **Inspera Requirement:** Platform requires identical feedback across all response states
2. **Generator Behavior:** Uses fallback chain (`correct` → `general` → default)
3. **QTI Output:** All four `<modalFeedback>` XML elements get the same content
4. **Validation:** Both formats pass BB6 v3.0 validation

**Example - Simple Format Input:**
```markdown
## Feedback

### General Feedback
The answer is 4 because 2 + 2 = 4.
```

**Generator Output (All States):**
- Correct Response: "The answer is 4 because 2 + 2 = 4."
- Incorrect Response: "The answer is 4 because 2 + 2 = 4."
- Partially Correct: "The answer is 4 because 2 + 2 = 4."
- Unanswered: "The answer is 4 because 2 + 2 = 4."

**Result:** Works perfectly with Inspera! ✅

---

### 2. Question Structure - Multiple Choice Single

**Question Heading**: Single `#` (H1 level)
**Format**: `# Question [N]: [Descriptive Title]`

```markdown
# Question 1: [Brief Descriptive Title]

## REQUIRED FIELDS:
**Type**: multiple_choice_single
**Identifier**: [Q001, MC_001, YOUR_ID_FORMAT]
**Points**: [1-5 typically]
**Tags**: [CourseCode], [Content], [Content], [BloomLevel], [Difficulty]

## Question Text

[Your question prompt here. Can include:]
- Regular text with **bold** and *italic*
- Mathematical notation: $f(x) = x^2 + 3x - 5$
- Images: ![description](path/to/image.png)
- Code blocks for programming questions
- Tables, lists, and other markdown formatting

## Options

A. [First option text]
B. [Second option text]
C. [Third option text]
D. [Fourth option text]
[E. Fifth option if needed]

## Answer

[Single letter - e.g., B]

## Feedback

### General Feedback
[Your comprehensive feedback that works for all students.
Include context, explanation, and guidance here.]

**OR use Unified Format (optional):**

### General Feedback
[Context or background information]

### Correct Response Feedback
[Positive reinforcement and explanation]

### Incorrect Response Feedback
[Guidance toward correct understanding]

### Unanswered Feedback
[Reminder to answer the question]

**Optional - Option-Specific Feedback:**

### Option-Specific Feedback
- **A**: [Explanation of why this option is incorrect / what misconception it represents]
- **B**: [Confirmation that this is correct and additional explanation]
- **C**: [Explanation of why this option is incorrect]
- **D**: [Explanation of why this option is incorrect]

---
```

**Question Separator**: Always use `---` on its own line between questions

---

### 3. Question Structure - Multiple Response (Select All)

```markdown
# Question [N]: [Title]

## REQUIRED:
**Type**: multiple_response
**Identifier**: [YOUR_ID]
**Points**: [Total points]

## OPTIONAL (Inspera labels):
**Learning Objectives**: [LO1, LO2]
**Bloom's Level**: [Level]

## Question Text

[Question prompt - do NOT include "Select all that apply" here]

## Prompt

[Select all that apply. / Välj alla korrekta påståenden. / Choose all correct options.]

## Options

A. [Option text]
B. [Option text]
C. [Option text]
D. [Option text]
E. [Option text]

## Answer

[Comma-separated letters - e.g., A, C, E]

## Scoring

**Points per correct choice**: [e.g., 0.67 or 1]
**Points per incorrect choice**: [e.g., 0 or -0.5]
**Maximum score**: [Total points]
**Minimum score**: [Usually 0]

## Feedback

### General Feedback
[Your comprehensive feedback that works for all students.]

**OR use Unified Format (recommended for partial credit types):**

### General Feedback
[General information]

### Correct Response Feedback
[All correct - excellent work]

### Incorrect Response Feedback
[None or some wrong - guidance]

### Partially Correct Response Feedback
[Some correct - encouragement and direction]

### Unanswered Feedback
[Prompt to answer]

**Optional - Option-Specific Feedback:**

### Option-Specific Feedback
- **A**: [Why this is correct/incorrect]
- **B**: [Why this is correct/incorrect]
- **C**: [Why this is correct/incorrect]
- **D**: [Why this is correct/incorrect]
- **E**: [Why this is correct/incorrect]

---
```

---

### 4. Question Structure - True/False

```markdown
# Question [N]: [Title]

## REQUIRED:
**Type**: true_false
**Identifier**: [YOUR_ID]
**Points**: [Usually 1]

## OPTIONAL (Inspera labels):
**Learning Objectives**: [LO1]
**Bloom's Level**: [Level]

## Question Text

[True or false: Statement to evaluate]
[Sant eller falskt: Påstående att bedöma]

## Options

A. [True / Sant]
B. [False / Falskt]

## Answer

[A or B]

## Feedback

### General Feedback
[Your comprehensive feedback that works for all students.
Include context, explanation, and correction if needed.]

**OR use Unified Format (optional):**

### General Feedback
[Context about the concept]

### Correct Response Feedback
[Confirmation and explanation]

### Incorrect Response Feedback
[Correction and guidance]

### Unanswered Feedback
[Reminder to answer]

---
```

---

### 5. Question Structure - Fill-in-the-Blank

```markdown
# Question [N]: [Title]

## REQUIRED:
**Type**: fill_in_the_blank
**Identifier**: [YOUR_ID]
**Points**: [Usually 1-2]

## OPTIONAL (Inspera labels):
**Learning Objectives**: [LO1]
**Bloom's Level**: [Remember or Understand typically]

## Question Text

[Text with blank marked as **________** or __________]
Example: The derivative of $x^2$ is **________**.

## Correct Answer

[primary answer]

## Accepted Alternatives

[answer1, answer2, answer3]  # Comma-separated, no bullets

## Case Sensitive

[true or false]

## Expected Length

[Number - approximate character length for UI field sizing]

## Feedback

### General Feedback
[Your comprehensive feedback including the correct answer and explanation.]

**OR use Unified Format (optional):**

### General Feedback
[Context about the concept]

### Correct Response Feedback
[Confirmation and explanation]

### Incorrect Response Feedback
[Guidance without revealing answer]

### Unanswered Feedback
[Prompt to fill in the blank]

---
```

---

### 6. Question Structure - Matching (Associate Pairs)

```markdown
# Question [N]: [Title]

## REQUIRED:
**Type**: match
**Identifier**: [YOUR_ID]
**Points**: [Total points]

## OPTIONAL (Inspera labels):
**Learning Objectives**: [LO1, LO2]
**Bloom's Level**: [Understand or Apply typically]

## Question Text

[Instructions for matching task]
Example: Match each [concept] with its [definition/example/application].

## Premises (Left Column)

1. [First item to match]
2. [Second item to match]
3. [Third item to match]

## Choices (Right Column)

A. [First choice]
B. [Second choice]
C. [Third choice]
D. [Optional fourth choice - distractor]

## Answer

1 → [A, B, or C]
2 → [A, B, or C]
3 → [A, B, or C]

## Scoring

**Type**: partial_credit
**Points per correct match**: [e.g., 1]
**Minimum score**: [Usually 0]

## Feedback

### General Feedback
[Your comprehensive feedback including correct matches and explanations.]

**OR use Unified Format (recommended for partial credit types):**

### General Feedback
[Context about the concepts being matched]

### Correct Response Feedback
[All correct - excellent]

### Incorrect Response Feedback
[Guidance for wrong matches]

### Partially Correct Response Feedback
[Some correct - encouragement]

### Unanswered Feedback
[Prompt to complete matching]

---
```

---

### 7. Question Structure - Text Area (Short Response)

**Note**: This type requires manual grading

```markdown
# Question [N]: [Title]

## REQUIRED:
**Type**: text_area
**Identifier**: [YOUR_ID]
**Points**: [Usually 2-5]

## OPTIONAL (Inspera labels):
**Learning Objectives**: [LO1, LO2]
**Bloom's Level**: [Apply, Analyze, or Evaluate typically]

## Question Text

[Open-ended question requiring written response]
[Specify expected length: 50-100 words, 3-5 sentences, etc.]

## Rubric

[Scoring criteria - what constitutes full, partial, and no credit]

## Sample Answer

[Example of a complete, correct response]

## Feedback

### General Feedback
[Your comprehensive feedback about expectations and key points.]

**OR use Unified Format (optional):**

### General Feedback
[Context about the question]

### Unanswered Feedback
[Prompt to provide answer]

---
```

---

### 8. Question Structure - Extended Text (Essay)

**Note**: This type requires manual grading

```markdown
# Question [N]: [Title]

## REQUIRED:
**Type**: extended_text
**Identifier**: [YOUR_ID]
**Points**: [Usually 5-15]

## OPTIONAL (Inspera labels):
**Learning Objectives**: [LO1, LO2, LO3]
**Bloom's Level**: [Analyze, Evaluate, or Create]

## Question Text

[Essay prompt with clear expectations]
[Specify length: 300-500 words, 2-3 paragraphs, etc.]

## Rubric

[Detailed scoring criteria]
[Consider: argument quality, evidence use, organization, writing quality]

## Sample Answer

[Example of high-quality response]

## Feedback

### General Feedback
[Your comprehensive feedback about expectations, key points, and evaluation criteria.]

**OR use Unified Format (optional):**

### General Feedback
[Context and expectations]

### Unanswered Feedback
[Prompt to write essay]

---
```

---

## ⚠️ CRITICAL FORMAT RULES (UNIVERSAL - NEVER CHANGE)

### Question Header Fields

**REQUIRED Fields (Parser fails without these):**

1. **Type** - EXACT spelling required (lowercase, underscores):
   - `multiple_choice_single`
   - `multiple_response`
   - `true_false`
   - `fill_in_the_blank`
   - `match`
   - `text_area`
   - `extended_text`
   - `audio_record`
   - `nativehtml`

2. **Identifier** - Unique question ID:
   - UPPERCASE letters, numbers, underscores only
   - No spaces, no special characters
   - Examples: `Q001`, `MC_001`, `MATH_Q15`, `HIST_ESSAY_1`

3. **Points** - Point value (number)

**OPTIONAL Fields (Become Inspera searchable labels if included):**
- **Learning Objectives**: References to LO IDs from YAML (e.g., `LO1, LO2`)
- **Bloom's Level**: Cognitive level (Remember, Understand, Apply, Analyze, Evaluate, Create)

**Section Headers** (must be EXACT, H2 level with `##`):
- `## Question Text` (NOT "### Question" or "## Frågetext")
- `## Options` (NOT "## Choices" or "## Alternativ")
- `## Answer` (NOT "## Correct Answer" or "## Svar")
- `## Feedback` (NOT "## Återkoppling")
- `## Prompt` (for multiple_response only)
- `## Premises (Left Column)` (for match)
- `## Choices (Right Column)` (for match)
- `## Correct Answer` (for fill_in_the_blank)
- `## Accepted Alternatives` (for fill_in_the_blank)
- `## Case Sensitive` (for fill_in_the_blank)
- `## Expected Length` (for fill_in_the_blank)
- `## Scoring` (for multiple_response and match)

**Feedback Subsections** (must be EXACT, H3 level with `###`):

**Simple Format (Recommended - BB6 v3.0 compliant):**
- `### General Feedback` (REQUIRED - generator duplicates for all states)

**Unified Format (Optional - BB6 v3.0 compliant):**
- `### General Feedback`
- `### Correct Response Feedback`
- `### Incorrect Response Feedback`
- `### Partially Correct Response Feedback` (for partial credit types: MR, Match, Text Entry, etc.)
- `### Unanswered Feedback`

**Optional (both formats):**
- `### Option-Specific Feedback` (for MC and MR)

**Answer Format**:
- Multiple Choice Single: Single letter `B` (no bold, no period, no quotes)
- Multiple Response: Comma-separated `A, C, E`
- True/False: `A` (where A=True/Sant, B=False/Falskt)
- Match: One pairing per line `1 → A` or `1 -> A`
- Fill-in-the-blank: Plain text under `## Correct Answer`

**Question Separator**:
- Three dashes `---` on its own line
- One blank line before and after recommended

---

## 🎯 ADAPTING FOR YOUR COURSE

### Step 1: Customize YAML Frontmatter

**Choose appropriate:**
- `title`: Your assessment name
- `identifier`: Unique ID with your course code
- `language`: Your language code (sv, en, no, etc.)
- `subject`: Your course code or subject area
- `type`: formative (practice, low stakes) vs summative (graded, high stakes)

**Write Learning Objectives aligned to:**
- **Gymnasium**: Gy11/GY25 centralt innehåll and kunskapskrav
- **Högskola/Universitet**: Course syllabus learning outcomes
- **International**: Your curriculum standards

### Step 2: Write Questions at Appropriate Level

**Gymnasium Questions** typically:
- Use Bloom's levels: Remember, Understand, Apply
- Award 1-2 points per question
- Use clear, direct language
- Test foundational knowledge
- Refer to textbook sections

**University Questions** typically:
- Use Bloom's levels: Apply, Analyze, Evaluate, Create
- Award 2-5 points per question
- Use discipline-specific terminology
- Test critical thinking and synthesis
- Reference research articles or case studies

### Step 3: Choose Appropriate Question Types

| Learning Goal | Best Question Type | Example |
|---------------|-------------------|---------|
| Recall facts/definitions | Fill-in-the-blank, MC Single | "The capital of Sweden is ________" |
| Understand concepts | MC Single, True/False | "Explain why photosynthesis requires..." |
| Apply procedures | MC Single, Multiple Response | "Calculate the derivative of..." |
| Analyze relationships | Match, Multiple Response | "Match each cause with its effect" |
| Evaluate arguments | MC Single, Text Area | "Which interpretation is best supported..." |
| Create solutions | Extended Text, Text Area | "Design an experiment to test..." |

---

## 📊 EXAMPLE: SAME QUESTION ACROSS LEVELS

### Gymnasium Level (Basic)

```markdown
# Question 1: Pythagorean Theorem Application

## REQUIRED:
**Type**: multiple_choice_single
**Identifier**: GYM_MATH_Q001
**Points**: 1

## OPTIONAL (Inspera labels):
**Learning Objectives**: LO1
**Bloom's Level**: Apply

## Question Text

En rätrutig triangel har kateterna 3 cm och 4 cm. Hur lång är hypotenusan?

## Options

A. 5 cm
B. 7 cm
C. 12 cm
D. 25 cm

## Answer

A

## Feedback

### General Feedback
Pythagoras sats säger att $a^2 + b^2 = c^2$ där $c$ är hypotenusan. Rätt svar är 5 cm eftersom $3^2 + 4^2 = 9 + 16 = 25 = 5^2$.

---
```

### University Level (Advanced)

```markdown
# Question 1: Generalized Pythagorean Theorem in Banach Spaces

## REQUIRED:
**Type**: multiple_choice_single
**Identifier**: UNI_MATH_Q001
**Points**: 3

## OPTIONAL (Inspera labels):
**Learning Objectives**: LO1, LO2
**Bloom's Level**: Analyze

## Question Text

Let $X$ be a Banach space with norm $\|\cdot\|$ satisfying the parallelogram law. For orthogonal vectors $x, y \in X$, which generalization of the Pythagorean theorem holds?

## Options

A. $\|x + y\|^2 = \|x\|^2 + \|y\|^2$
B. $\|x + y\| = \|x\| + \|y\|$
C. $\|x + y\|^p = \|x\|^p + \|y\|^p$ for all $p \geq 1$
D. $\langle x+y, x+y \rangle = \langle x,x \rangle + \langle y,y \rangle$

## Answer

A

## Feedback

### General Feedback
The parallelogram law characterizes inner product spaces among Banach spaces, enabling geometric concepts like orthogonality. In spaces satisfying the parallelogram law, orthogonal vectors satisfy the Pythagorean identity $\|x + y\|^2 = \|x\|^2 + \|y\|^2$, which follows from $\langle x, y \rangle = 0$. This uses the relationship $\|x + y\|^2 = \langle x+y, x+y \rangle = \|x\|^2 + 2\langle x,y \rangle + \|y\|^2$.

---
```

**→ SAME FORMAT, DRAMATICALLY DIFFERENT COMPLEXITY!**

---

## 📚 SUBJECT-SPECIFIC EXAMPLES

### Mathematics
```markdown
## REQUIRED:
**Type**: multiple_choice_single
**Identifier**: MATH_Q001
**Points**: 1

## OPTIONAL (Inspera labels):
**Learning Objectives**: LO1
**Bloom's Level**: Apply

## Question Text
Solve for $x$: $2x + 5 = 13$
```

### Science (Biology)
```markdown
## REQUIRED:
**Type**: text_area
**Identifier**: BIO_Q001
**Points**: 3

## OPTIONAL (Inspera labels):
**Learning Objectives**: LO2, LO3
**Bloom's Level**: Analyze

## Question Text
Explain how natural selection acts on variation within a population to drive evolutionary change.
```

### History
```markdown
## REQUIRED:
**Type**: extended_text
**Identifier**: HIST_Q001
**Points**: 5

## OPTIONAL (Inspera labels):
**Learning Objectives**: LO1
**Bloom's Level**: Evaluate

## Question Text
To what extent were economic factors the primary cause of the French Revolution?
```

### Language (Swedish Grammar)
```markdown
## REQUIRED:
**Type**: multiple_choice_single
**Identifier**: SV_Q001
**Points**: 1

## OPTIONAL (Inspera labels):
**Learning Objectives**: LO1
**Bloom's Level**: Apply

## Question Text
Välj rätt verbform: "Igår ________ (gå) jag till affären."

## Options
A. går
B. gick
C. gått
D. gående
```

### Programming
```markdown
## REQUIRED:
**Type**: multiple_choice_single
**Identifier**: PROG_Q001
**Points**: 2

## OPTIONAL (Inspera labels):
**Learning Objectives**: LO2
**Bloom's Level**: Apply

## Question Text
What is the output of this Python code?
\`\`\`python
def f(x):
    return x ** 2
print(f(3))
\`\`\`

## Options
A. 6
B. 9
C. 3
D. Error
```

---

## ✅ UNIVERSAL VALIDATION CHECKLIST

Before running QTI generator, verify:

### Structural
- [ ] YAML frontmatter present and valid (test with yaml parser)
- [ ] All questions use `# Question [N]:` (H1 level, not H2)
- [ ] Questions separated by `---` on its own line
- [ ] No organizational section headers between questions

### Question Headers
- [ ] All questions have REQUIRED fields: Type, Identifier, Points
- [ ] Type field uses EXACT spelling (lowercase_underscore)
- [ ] All Identifiers are unique and valid format (UPPERCASE)
- [ ] OPTIONAL: Learning Objectives (if included) reference IDs defined in YAML
- [ ] OPTIONAL: Bloom's Level (if included) uses correct capitalization

### Section Headers
- [ ] All section headers use `##` (H2 level, not H3)
- [ ] Section headers use EXACT English names
- [ ] No Swedish/Norwegian/Danish headers (`Frågetext`, `Svar`, etc.)

### Content
- [ ] Options format: `A. Text` (uppercase letter, period, space)
- [ ] Answer format matches question type (no bold, no quotes)
- [ ] All required sections present per question type
- [ ] Feedback has proper subsection structure

### Question Type Specific
- [ ] Multiple Response: Has `## Prompt` and `## Scoring`
- [ ] Match: Has `## Premises (Left Column)` and `## Choices (Right Column)` and `## Scoring`
- [ ] Fill-in-the-blank: Has `## Correct Answer`, `## Accepted Alternatives`, `## Case Sensitive`, `## Expected Length`

---

## 🚀 WORKFLOW: FROM TEMPLATE TO INSPERA

### 1. Copy This Template
Save as: `[your_course]_quiz.md`

### 2. Customize YAML Frontmatter
- Fill in your course information
- Write learning objectives for your course
- Configure assessment settings

### 3. Write Questions
- Follow EXACT format for each question type
- Write content at appropriate level for your students
- Create comprehensive feedback

### 4. Validate Format
Use the checklist above

### 5. Generate QTI XML
```bash
python -m src.main [your_course]_quiz.md -o output/
```

### 6. Import to Inspera
- Upload the generated ZIP file
- Review in question bank
- Create test/quiz using questions

---

## 📖 COMPLETE TEMPLATE STRUCTURE

```markdown
---
[YAML FRONTMATTER - Customize for your course]
---

# Question 1: [Your First Question]
[Complete question following type-specific format]

---

# Question 2: [Your Second Question]
[Complete question following type-specific format]

---

# Question 3: [Your Third Question]
[Complete question following type-specific format]

---

[... continue for all questions ...]

---

# Question N: [Your Last Question]
[Complete question following type-specific format]
```

---

## 💡 TIPS FOR SUCCESS

### For Gymnasium
- Use clear, direct language
- Reference textbook sections in General Feedback
- Use concrete, familiar examples
- Focus on Bloom's Remember, Understand, Apply
- Award 1-2 points per question typically

### For University
- Use discipline-specific terminology
- Reference research literature in General Feedback
- Use abstract, theoretical examples
- Focus on Bloom's Apply, Analyze, Evaluate, Create
- Award 2-5 points per question typically
- Include case studies and scenarios

### For All Levels
- ✅ Keep questions focused on one concept
- ✅ Write clear, unambiguous question text
- ✅ Create plausible distractors that reveal misconceptions
- ✅ Provide explanatory feedback, not just "Correct!"/"Wrong!"
- ✅ Align questions to learning objectives
- ✅ Test understanding, not memorization (when possible)

---

## 🔧 TROUBLESHOOTING

### Common Parser Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "No YAML frontmatter" | Missing `---` delimiters | Add `---` before and after YAML |
| "Invalid question type" | Wrong Type spelling | Use exact: `multiple_choice_single` not "Multiple Choice" |
| "Missing required field" | No Identifier or Points | Add to question header |
| "Invalid section header" | Wrong level or name | Use `## Question Text` (H2, English) |
| "Malformed answer" | Extra formatting | Use plain text: `B` not `**B**` |

---

## 📞 SUPPORT

For issues with:
- **This specification**: Check examples and format rules
- **Python QTI generator**: Check project documentation
- **Inspera import**: Consult Inspera support
- **Subject-specific pedagogy**: Consult your curriculum guides

---

**Document Version**: 1.0
**Created**: 2025-11-02
**Purpose**: Universal master template for QTI question generation across all subjects and levels
**Replaces**: Subject-specific templates (but can coexist as examples)
