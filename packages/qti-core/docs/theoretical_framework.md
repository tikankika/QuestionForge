# Theoretical Framework

## Introduction

This document establishes the pedagogical foundation for the QTI Generator for Inspera project. The tool integrates three complementary theoretical frameworks to ensure that generated assessments are pedagogically sound, evidence-based, and effectively support student learning.

### The Three Frameworks

1. **Bloom's Taxonomy** (Anderson & Krathwohl, 2001) - Provides cognitive level classification
2. **Test-Based Learning** (Roediger & Karpicke, 2006) - Leverages retrieval practice principles
3. **Constructive Alignment** (Biggs & Tang, 2011) - Ensures coherence between objectives and assessment

### Purpose

This framework guides:
- Test planning and question distribution
- Question generation with appropriate cognitive demand
- Validation of assessment quality and alignment
- Metadata structure for all generated questions

---

## Bloom's Taxonomy

### Overview

Bloom's Taxonomy classifies learning objectives and assessment items according to cognitive complexity. The revised taxonomy (Anderson & Krathwohl, 2001) consists of six hierarchical levels, from lower-order to higher-order thinking skills.

### The Six Cognitive Levels

#### 1. Remember
**Definition**: Retrieve relevant knowledge from long-term memory.

**Action Verbs**: Define, list, recall, recognize, identify, name, state

**Question Types**:
- Multiple choice with factual recall
- True/false statements
- Fill-in-the-blank with terminology

**Example**:
```
Question: What is the capital of Sweden?
Bloom's Level: Remember
```

#### 2. Understand
**Definition**: Construct meaning from instructional messages, including oral, written, and graphic communication.

**Action Verbs**: Explain, summarize, paraphrase, classify, compare, interpret, describe

**Question Types**:
- Explain concepts in own words
- Classify examples into categories
- Compare and contrast items

**Example**:
```
Question: Explain the difference between formative and summative assessment.
Bloom's Level: Understand
```

#### 3. Apply
**Definition**: Carry out or use a procedure in a given situation.

**Action Verbs**: Execute, implement, use, demonstrate, solve, calculate, apply

**Question Types**:
- Problem-solving with known procedures
- Calculations using formulas
- Application of rules to new situations

**Example**:
```
Question: Calculate the standard deviation for the following dataset: [2, 4, 6, 8, 10]
Bloom's Level: Apply
```

#### 4. Analyze
**Definition**: Break material into constituent parts and determine how parts relate to one another and to an overall structure.

**Action Verbs**: Differentiate, organize, attribute, compare, deconstruct, examine, investigate

**Question Types**:
- Identify relationships between components
- Distinguish relevant from irrelevant information
- Determine underlying structure or patterns

**Example**:
```
Question: Analyze the research design and identify potential confounding variables.
Bloom's Level: Analyze
```

#### 5. Evaluate
**Definition**: Make judgments based on criteria and standards.

**Action Verbs**: Check, critique, judge, assess, defend, justify, argue, support

**Question Types**:
- Critique arguments or solutions
- Justify decisions with evidence
- Assess quality using explicit criteria

**Example**:
```
Question: Evaluate the validity of this experimental design and justify your assessment.
Bloom's Level: Evaluate
```

#### 6. Create
**Definition**: Put elements together to form a coherent or functional whole; reorganize elements into a new pattern or structure.

**Action Verbs**: Design, construct, plan, produce, generate, develop, formulate

**Question Types**:
- Design solutions to complex problems
- Generate hypotheses
- Create original products or plans

**Example**:
```
Question: Design an experiment to test the hypothesis that sleep deprivation affects memory retention.
Bloom's Level: Create
```

### Distribution Guidelines

A well-balanced assessment typically includes:

- **Remember & Understand** (30-40%): Foundation knowledge
- **Apply & Analyze** (40-50%): Application and critical thinking
- **Evaluate & Create** (10-20%): Higher-order synthesis

**Note**: Distribution should align with learning objectives and course level (introductory courses may emphasize lower levels; advanced courses emphasize higher levels).

### Implementation in QTI Generator

Each question includes Bloom's level metadata:
```yaml
bloom_level: Apply
```

The validation module checks:
- Distribution across cognitive levels
- Alignment with stated course objectives
- Appropriate balance for assessment type (formative vs. summative)

---

## Test-Based Learning

### Overview

Test-Based Learning (TBL) research demonstrates that retrieval practice—actively recalling information—enhances long-term retention more effectively than passive review. The "testing effect" (Roediger & Karpicke, 2006) shows that tests are not merely assessment tools but powerful learning interventions.

### Key Principles

#### 1. The Testing Effect
**Research Finding**: Retrieving information from memory strengthens that memory trace more than repeated studying.

**Implication**: Frequent low-stakes testing supports learning, not just assessment.

**Implementation**:
- Design formative assessments with immediate feedback
- Use retrieval practice throughout the learning process
- Multiple attempts allowed for practice questions

#### 2. Retrieval Practice
**Research Finding**: Effortful retrieval produces better retention than easy retrieval.

**Implication**: Questions should require genuine recall, not recognition alone.

**Implementation**:
- Minimize cueing in question stems
- Use constructed response when possible
- Avoid verbatim repetition of course materials

#### 3. Spacing and Distribution
**Research Finding**: Spaced practice produces better retention than massed practice.

**Implication**: Tests should be distributed over time, with repeated retrieval opportunities.

**Implementation**:
- Plan multiple assessments throughout course
- Include cumulative questions in later assessments
- Interleave topics rather than blocking by topic

#### 4. Feedback Mechanisms
**Research Finding**: Immediate corrective feedback enhances the testing effect.

**Implication**: All questions should provide meaningful feedback.

**Implementation**:
- Provide explanatory feedback for correct and incorrect responses
- Reference learning materials for further study
- Explain why incorrect options are wrong

### Feedback Design Guidelines

**For Correct Responses**:
- Confirm correctness
- Reinforce key concepts
- Extend learning with additional context

**For Incorrect Responses**:
- Explain why the response is incorrect
- Provide correct answer with explanation
- Direct to relevant learning resources
- Address common misconceptions

**Example Feedback Structure**:
```xml
<modalFeedback outcomeIdentifier="FEEDBACK" identifier="correct">
    Correct! The standard deviation measures the spread of data around the mean.
    Your calculation demonstrates understanding of this fundamental statistical concept.
</modalFeedback>

<modalFeedback outcomeIdentifier="FEEDBACK" identifier="incorrect">
    Not quite. The standard deviation requires calculating variance first (mean of squared deviations),
    then taking the square root. Review Chapter 3, Section 2 for step-by-step guidance.
</modalFeedback>
```

### Implementation in QTI Generator

- All questions include feedback fields in markdown input
- XML generator creates appropriate QTI feedback elements
- Feedback is displayed immediately in Inspera platform
- Formative assessments allow multiple attempts to support learning

---

## Constructive Alignment

### Overview

Constructive Alignment (Biggs & Tang, 2011) ensures coherence across three dimensions:

1. **Intended Learning Outcomes (ILOs)**: What students should know/do
2. **Teaching/Learning Activities**: How students learn
3. **Assessment Tasks**: How learning is measured

In this project, we focus on the alignment between ILOs and assessment tasks.

### The Alignment Framework

```
Learning Objectives ←→ Assessment Questions ←→ Cognitive Levels
```

**Principle**: Assessment tasks should directly measure stated learning objectives at the appropriate cognitive level.

### Mapping Objectives to Questions

#### Step 1: Identify Learning Objectives
Each course or test should have explicit learning objectives.

**Example Objective**:
```
Students will be able to apply statistical methods to analyze research data.
```

#### Step 2: Extract Cognitive Verb
Identify the action verb in the objective (from Bloom's Taxonomy).

**Example**: "apply" → Bloom's level: Apply

#### Step 3: Design Aligned Questions
Create questions that require students to demonstrate the exact skill stated in the objective.

**Aligned Question**:
```
Question: Given the following dataset, apply the t-test to determine whether
the two groups differ significantly.

Learning Objective: Apply statistical methods to analyze research data
Bloom's Level: Apply
Alignment: ✓ Direct match
```

**Misaligned Question**:
```
Question: Define what a t-test is.

Learning Objective: Apply statistical methods to analyze research data
Bloom's Level: Remember
Alignment: ✗ Cognitive level mismatch
```

### Coverage Analysis

**Principle**: All learning objectives should be assessed; no objectives should be over- or under-represented.

**Implementation**:
1. List all course/module learning objectives
2. Tag each question with objective(s) it assesses
3. Validate that all objectives are covered
4. Check distribution to ensure balanced coverage

**Example Coverage Matrix**:

| Objective | Questions | Cognitive Levels |
|-----------|-----------|------------------|
| LO1: Recall key terms | Q1, Q4, Q7 | Remember |
| LO2: Apply statistical tests | Q2, Q5, Q8, Q11 | Apply |
| LO3: Analyze research designs | Q3, Q6, Q9 | Analyze |
| LO4: Evaluate study validity | Q10, Q12 | Evaluate |

### Validation Procedures

The QTI Generator validator checks:

1. **Objective Mapping**: Every question is linked to at least one learning objective
2. **Coverage Completeness**: Every objective is assessed by at least one question
3. **Cognitive Alignment**: Question Bloom's level matches objective verb
4. **Distribution Balance**: No single objective dominates the assessment

### Implementation in QTI Generator

Markdown input includes alignment metadata:
```yaml
learning_objectives:
  - LO2: Apply statistical methods
bloom_level: Apply
```

Validator produces alignment reports:
- Coverage matrix
- Bloom's distribution
- Objective representation percentages
- Alignment warnings for mismatches

---

## Integration Framework

### How the Three Frameworks Complement Each Other

```
┌─────────────────────────────────────────────────────────┐
│ Constructive Alignment                                   │
│ Ensures objectives ←→ questions coherence               │
└────────────┬────────────────────────────────────────────┘
             │
             ├──→ Bloom's Taxonomy
             │    Classifies cognitive demand
             │    Validates appropriate complexity
             │
             └──→ Test-Based Learning
                  Optimizes learning through testing
                  Designs effective feedback
```

### Integrated Quality Framework

A high-quality assessment question should:

1. **Align with Learning Objectives** (Constructive Alignment)
   - Measures what it claims to measure
   - Directly maps to stated ILO

2. **Have Appropriate Cognitive Demand** (Bloom's Taxonomy)
   - Matches objective's cognitive verb
   - Contributes to balanced distribution

3. **Support Learning** (Test-Based Learning)
   - Requires genuine retrieval
   - Includes meaningful feedback
   - Provides learning opportunity

### Example: Integrated Analysis

**Question**:
```
A researcher finds a correlation of r = 0.85 between hours of study and exam scores.
Evaluate whether this finding supports the conclusion that studying causes higher exam scores.

Metadata:
- Learning Objective: LO4 - Evaluate causal claims from correlational data
- Bloom's Level: Evaluate
- Question Type: Multiple choice with justification
- Feedback: Explains correlation ≠ causation with examples
```

**Quality Analysis**:

✓ **Constructive Alignment**:
- Objective requires "evaluate causal claims"
- Question requires evaluating a causal interpretation
- Direct alignment confirmed

✓ **Bloom's Taxonomy**:
- Objective verb: "Evaluate" (Bloom's level 5)
- Question requires judgment using criteria (correlation vs. causation)
- Cognitive levels match

✓ **Test-Based Learning**:
- Requires retrieval of correlation/causation distinction
- Demands application to novel scenario (not verbatim from course)
- Feedback reinforces concept and addresses misconception

**Result**: High-quality question meeting all three framework criteria

---

## Practical Application

### Test Planning Process

1. **Define Assessment Purpose**
   - Formative (learning-focused) or Summative (grading-focused)
   - Stakes level (practice, quiz, exam)

2. **List Learning Objectives**
   - Extract from course syllabus
   - Ensure explicit action verbs (from Bloom's)

3. **Plan Question Distribution**
   - Map each objective to question count
   - Plan Bloom's level distribution
   - Ensure coverage and balance

4. **Design Questions**
   - Use Claude Desktop templates
   - Include all metadata fields
   - Write meaningful feedback

5. **Validate Alignment**
   - Run Python validator
   - Check coverage matrix
   - Review Bloom's distribution

### Question Generation Workflow

When creating questions with Claude Desktop:

1. Reference the learning objective explicitly
2. Identify the Bloom's level from the objective verb
3. Write the question requiring that cognitive level
4. Create feedback that reinforces the concept
5. Add metadata for validation

### Quality Checklist

Before finalizing a question, verify:

- [ ] Linked to specific learning objective(s)
- [ ] Bloom's level matches objective verb
- [ ] Question requires genuine retrieval/thinking
- [ ] Feedback explains correct answer
- [ ] Feedback addresses common errors
- [ ] Metadata fields completed
- [ ] Language is clear and unambiguous

---

## References

### Bloom's Taxonomy
- Anderson, L. W., & Krathwohl, D. R. (Eds.). (2001). *A taxonomy for learning, teaching, and assessing: A revision of Bloom's taxonomy of educational objectives*. New York: Longman.
- Bloom, B. S., Engelhart, M. D., Furst, E. J., Hill, W. H., & Krathwohl, D. R. (1956). *Taxonomy of educational objectives: The classification of educational goals. Handbook I: Cognitive domain*. New York: David McKay.

### Test-Based Learning
- Roediger, H. L., & Karpicke, J. D. (2006). Test-enhanced learning: Taking memory tests improves long-term retention. *Psychological Science, 17*(3), 249-255.
- Karpicke, J. D., & Roediger, H. L. (2008). The critical importance of retrieval for learning. *Science, 319*(5865), 966-968.
- Dunlosky, J., Rawson, K. A., Marsh, E. J., Nathan, M. J., & Willingham, D. T. (2013). Improving students' learning with effective learning techniques: Promising directions from cognitive and educational psychology. *Psychological Science in the Public Interest, 14*(1), 4-58.

### Constructive Alignment
- Biggs, J., & Tang, C. (2011). *Teaching for quality learning at university* (4th ed.). Maidenhead: Open University Press.
- Biggs, J. (1996). Enhancing teaching through constructive alignment. *Higher Education, 32*(3), 347-364.

### QTI and Assessment Standards
- IMS Global Learning Consortium. (2015). *IMS Question & Test Interoperability (QTI) Specification Version 2.2*. Retrieved from https://www.imsglobal.org/question/
- Inspera Assessment. (2024). *QTI 2.2 Implementation Guide*. Retrieved from https://www.inspera.com/

---

## Document Version

**Version**: 1.0
**Last Updated**: October 2025
**Status**: Initial framework documentation
