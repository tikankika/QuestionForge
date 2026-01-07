# ADR 003: Integration of Three Pedagogical Frameworks

## Status

Accepted

## Date

2025-10-30

## Context

The QTI Generator is designed for the AIED (AI in Education) community and educational assessment practitioners. Unlike existing QTI generators that focus purely on technical conversion, this tool should promote pedagogically sound assessment design based on evidence-based frameworks.

### The Problem

Many assessment authoring tools are atheoretical—they allow question creation without guiding users toward best practices. This can result in:

- Assessments dominated by low-level recall questions
- Misalignment between learning objectives and assessment items
- Questions that test recognition rather than genuine understanding
- Ineffective use of testing as a learning tool

### Stakeholder Needs

- **Educators**: Need guidance on creating effective assessments
- **Instructional Designers**: Require alignment validation
- **Researchers** (AIED community): Need theoretically grounded tool for studies
- **Students**: Benefit from better-designed assessments that support learning

## Decision

We will integrate **three complementary pedagogical frameworks** throughout the tool:

### 1. Bloom's Taxonomy (Anderson & Krathwohl, 2001)

**Purpose**: Classify cognitive complexity of learning objectives and questions

**Implementation**:
- Every question must specify Bloom's level (Remember, Understand, Apply, Analyze, Evaluate, Create)
- Validator checks distribution across levels
- Templates guide appropriate question construction for each level
- Reports show cognitive level balance

**Rationale**: Ensures assessments address appropriate cognitive demands and aren't overly focused on recall.

### 2. Test-Based Learning (Roediger & Karpicke, 2006)

**Purpose**: Leverage the testing effect for enhanced learning

**Implementation**:
- Question templates emphasize retrieval practice over recognition
- Feedback mechanisms are mandatory and should explain concepts
- Formative assessment support (multiple attempts, immediate feedback)
- Design guides discourage verbatim recall of course materials

**Rationale**: Tests are learning events, not just measurement tools. Retrieval practice enhances long-term retention.

### 3. Constructive Alignment (Biggs & Tang, 2011)

**Purpose**: Ensure coherence between objectives, teaching, and assessment

**Implementation**:
- Learning objectives explicitly defined in YAML frontmatter
- Each question must reference objective(s) it assesses
- Validator checks:
  - All objectives are assessed
  - No objectives are over/under-represented
  - Bloom's level matches objective's cognitive verb
- Coverage matrix reporting

**Rationale**: Assessment should directly measure stated learning objectives at appropriate cognitive levels.

## Alternatives Considered

**Option A: Purely Technical Tool** (No Pedagogical Framework)
- ✅ Simpler implementation
- ✅ Fewer constraints on users
- ❌ Perpetuates poor assessment practices
- ❌ No differentiation from existing tools
- ❌ Low value for AIED research

**Option B: Single Framework** (e.g., Bloom's only)
- ✅ Simpler to implement
- ✅ Some pedagogical grounding
- ❌ Incomplete guidance (doesn't address alignment or learning through testing)
- ❌ Misses synergies between frameworks

**Option C: Comprehensive Framework Suite** (Many frameworks)
- ✅ Thorough theoretical grounding
- ❌ Overwhelming complexity for users
- ❌ Difficult to validate programmatically
- ❌ May conflict or contradict

**Option D: Three Complementary Frameworks** (Selected)
- ✅ Each framework addresses distinct aspect of quality
- ✅ Frameworks complement rather than conflict
- ✅ Manageable implementation complexity
- ✅ Strong theoretical foundation for publications
- ✅ Practical guidance for practitioners
- ❌ Requires comprehensive documentation

## Integration Strategy

### Phase 1: Documentation (Week 1)
- Theoretical framework document explaining all three frameworks
- Integration guidelines showing how they work together
- Quality checklist incorporating all frameworks

### Phase 2: Metadata Structure (Week 1-2)
- Bloom's level field (required)
- Learning objectives field (required)
- Feedback fields (required for Test-Based Learning)

### Phase 3: Validation Module (Week 3)
- Bloom's distribution analysis
- Objective coverage matrix
- Alignment verification (objective verb ↔ question cognitive demand)
- Feedback quality checks

### Phase 4: Reporting (Week 4)
- Coverage reports showing objective-question mappings
- Bloom's distribution charts
- Alignment warnings (mismatches between stated and actual levels)
- Feedback completeness report

## Consequences

### Positive

1. **Differentiation**: Only QTI tool with pedagogical framework integration
2. **Research Value**: Suitable for AIED studies on assessment quality
3. **Practitioner Guidance**: Helps educators create better assessments
4. **Student Benefit**: Results in more effective learning experiences
5. **Credibility**: Theoretical grounding supports academic publication
6. **Validation**: Programmatic checks prevent common mistakes

### Negative

1. **Complexity**: More metadata required from users
2. **Learning Curve**: Users must understand frameworks
3. **Constraints**: May feel restrictive to some users
4. **Maintenance**: Must stay current with pedagogical research

### Neutral

1. **Documentation Burden**: Requires comprehensive guides and examples
2. **Validation Logic**: Complex validation rules increase testing needs

## Implementation Details

### Required Metadata Fields

```yaml
learning_objectives:
  - id: "LO1"
    description: "Students will be able to apply statistical tests to research data"
```

```markdown
**Bloom's Level**: Apply
**Learning Objectives**: LO1, LO3
```

### Validation Rules

1. **Bloom's Level Match**:
   - Extract verb from objective description
   - Map to Bloom's taxonomy level
   - Compare with question's stated level
   - Warn if mismatch

2. **Coverage Completeness**:
   - Ensure every objective has ≥1 question
   - Flag objectives with >40% of questions (over-representation)

3. **Feedback Quality**:
   - Check all feedback fields populated
   - Warn if feedback is minimal (e.g., just "Correct!")

### User Workflow Integration

1. **Test Planning**: Use planning template with Bloom's distribution guidance
2. **Question Generation**: Templates show appropriate examples for each Bloom's level
3. **Validation**: Run validator before finalizing
4. **Revision**: Address alignment warnings
5. **Reporting**: Review coverage and distribution

## Success Criteria

- Users create more balanced Bloom's distributions (measured via validator reports)
- Learning objectives are explicitly defined and assessed
- Feedback is meaningful and explanatory (not just "correct/incorrect")
- Tool is cited in AIED publications
- Educators report improved assessment quality

## References

### Academic Sources

- Anderson, L. W., & Krathwohl, D. R. (Eds.). (2001). *A taxonomy for learning, teaching, and assessing: A revision of Bloom's taxonomy of educational objectives*. New York: Longman.
- Roediger, H. L., & Karpicke, J. D. (2006). Test-enhanced learning: Taking memory tests improves long-term retention. *Psychological Science, 17*(3), 249-255.
- Biggs, J., & Tang, C. (2011). *Teaching for quality learning at university* (4th ed.). Maidenhead: Open University Press.

### Implementation

- Theoretical framework document: `docs/theoretical_framework.md`
- Metadata specification: `docs/specifications/markdown_specification.md`
- Validation module: `src/validator/` (to be implemented)

## Superseded By

None

## Related Decisions

- ADR 001: Markdown Input Format (supports rich pedagogical metadata)
- ADR 002: XML Template Strategy (templates must accommodate pedagogical fields)
