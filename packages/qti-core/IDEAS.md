# Feature Ideas and Future Enhancements

**Version**: 1.0
**Last Updated**: 2025-11-01
**Protocol Level**: 3 (Feature Capture and Prioritization)
**Last Reviewed**: 2025-11-01

---

## Purpose

This document captures spontaneous ideas, user requests, and future enhancements for the QTI Generator. Ideas documented here are:
- Reviewed weekly during planning sessions
- Promoted to [ROADMAP.md](ROADMAP.md) when prioritized and scheduled
- Detailed in sprint planning when scheduled for implementation

**Workflow**:
```
Idea captured here (30 seconds)
    ↓ (weekly review)
Promoted to ROADMAP.md milestone
    ↓ (sprint planning)
Detailed in docs/sprints/sprint-XX.md
    ↓ (implementation)
GitHub Issue with full specification
```

---

## Recently Implemented (Moved from Ideas)

### Question Bank Conversion Utilities ✓
**Status**: Completed in v0.2.3-alpha (2025-11-02)
**Implementation**:
- `scripts/convert_evolution_format.py` - Dual-structure markdown converter
  - Extracts labels from separate Metadata/Question Content sections
  - Generates YAML frontmatter with test metadata
  - Merges into inline **Labels**: field
- `scripts/filter_supported_questions.py` - Question type filter
  - Filters question banks to only supported types
  - Reports statistics on skipped questions by type
  - Successfully processed 68-question Evolution bank (56 supported, 12 skipped)

**Impact**: Enables importing question banks from external sources without manual reformatting
**Workflow**: Convert → Filter → Generate QTI (3-step pipeline)
**Next Steps**:
- Integrate into main.py CLI (v0.3.0)
- Add batch processing mode (v0.3.0)
- Create unit tests (v0.3.0)

### Custom Labels System ✓
**Status**: Breaking change implemented in v0.2.3-alpha (2025-11-02)
**Change**: Removed auto-generated labels (Bloom:, LO:, Type:, Subject:)
**Rationale**: Aligns with actual Inspera native export format (plain text, no prefixes)
**Impact**: Users have complete control via **Labels**: field in markdown

---

## HIGH PRIORITY: Missing Question Type Implementations

These question types are blocking conversion of real question banks (Evolution bank case study).

### True/False Questions (URGENT)
**Description**: Implement true_false question type
**Blocker**: 6 questions from Evolution bank cannot be converted
**Status**: Prioritized for v0.3.0 milestone
**Tasks**:
- [ ] Analyze Inspera export format for true/false questions
- [ ] Create `true_false.xml` template
- [ ] Implement converter logic with boolean response handling
- [ ] Test with Evolution bank questions

**Complexity**: Low | **User Value**: Very High (common question type)
**Effort**: 1 week

### Multiple Choice Multiple (URGENT)
**Description**: Complete multiple_choice_multiple implementation
**Blocker**: 4 questions from Evolution bank cannot be converted
**Current State**: XML template exists (`multiple_response.xml`) but converter logic incomplete
**Status**: Prioritized for v0.3.0 milestone
**Tasks**:
- [ ] Determine if distinct from `multiple_response` or same Inspera type
- [ ] Implement advanced partial credit mapping logic
- [ ] Add all-or-nothing vs. partial credit scoring options
- [ ] Test with Evolution bank questions

**Complexity**: Medium-High | **User Value**: Very High (common question type)
**Effort**: 1.5 weeks

### Fill-in-the-Blank (MEDIUM PRIORITY)
**Description**: Implement fill_blank question type (single text entry field)
**Blocker**: 2 questions from Evolution bank cannot be converted
**Status**: Prioritized for v0.3.0 milestone
**Tasks**:
- [ ] Analyze Inspera export format
- [ ] Create `fill_blank.xml` template
- [ ] Implement string matching logic (case-sensitive/insensitive options)
- [ ] Support multiple acceptable answer variants
- [ ] Distinguish from `text_entry` (multiple blanks)

**Complexity**: Medium | **User Value**: High (common in language/STEM)
**Effort**: 1.5 weeks

---

## Candidate Features (Not Yet Scheduled)

### Question Type Enhancements

#### Calculated Questions
**Description**: Randomized numeric values in question text and answer options
- [ ] Variable placeholders in question text (e.g., `{{x}}`, `{{y}}`)
- [ ] Formula-based correct answer generation
- [ ] Configurable ranges for random values (e.g., `x: 1-100`)
- [ ] Decimal precision control
- [ ] Support for common mathematical operations (+, -, ×, ÷, ^, √)

**Use Cases**: Math, physics, chemistry problems with different numbers per student
**Complexity**: High | **User Value**: Very High (prevents cheating, testing procedural knowledge)

#### Adaptive Questions
**Description**: Difficulty adjustment based on student responses
- [ ] Branching logic (if answer A, show question 5; if answer B, show question 6)
- [ ] Difficulty scaling based on previous performance
- [ ] Prerequisite questions (must answer Q1 before Q5)

**Use Cases**: Diagnostic assessments, mastery-based progression
**Complexity**: Very High | **User Value**: Medium (requires platform support)
**Note**: May require Inspera-specific adaptive testing features

#### Question Pools
**Description**: Random selection from categories
- [ ] Define question pools in frontmatter
- [ ] Specify number of questions to select per pool
- [ ] Category tags for pool organization
- [ ] Difficulty-balanced selection (equal distribution across Bloom's levels)

**Use Cases**: Large question banks, alternate exam forms
**Complexity**: Medium | **User Value**: High (common in summative assessments)

---

### User Experience Improvements

#### Web-Based Preview Interface
**Description**: Preview generated QTI before export
- [ ] HTML rendering of all question types
- [ ] Interactive preview (answer questions, see feedback)
- [ ] Side-by-side markdown/preview comparison
- [ ] Mobile-responsive rendering

**Use Cases**: Quality assurance before Inspera import
**Complexity**: Medium | **User Value**: High (catch formatting errors early)

#### Question Bank Diff Tool
**Description**: Compare two versions of question bank
- [ ] Highlight changes, additions, deletions
- [ ] Show differences in question text, options, feedback
- [ ] Git integration (git diff support for markdown)
- [ ] Generate change reports for review/approval

**Use Cases**: Version control, collaborative development, change tracking
**Complexity**: Low-Medium | **User Value**: Medium (useful for teams)

#### Bulk Question Editing
**Description**: Update multiple questions simultaneously
- [ ] Batch update Bloom's level assignments
- [ ] Bulk change learning objective mappings
- [ ] Find/replace across question text
- [ ] Mass metadata updates (points, difficulty)

**Use Cases**: Refactoring large question banks, aligning with revised learning objectives
**Complexity**: Medium | **User Value**: Medium (efficiency for large banks)

---

### Utilities and Workflow Enhancements

#### Batch Conversion CLI (v0.3.0)
**Description**: Integrate conversion scripts into main.py for seamless workflow
**Tasks**:
- [ ] Add `--convert-from evolution` flag to main.py
- [ ] Automatic detection of source format (dual-structure vs. inline)
- [ ] Single command for convert → filter → generate pipeline
- [ ] Progress reporting for large batches (directory processing)
- [ ] Conversion statistics report (supported vs. unsupported counts)

**Use Cases**: One-command processing of external question banks
**Complexity**: Low | **User Value**: High (eliminates manual 3-step workflow)
**Effort**: 1 week
**Status**: Planned for v0.3.0 milestone

#### Conversion Script Testing (v0.3.0)
**Description**: Add automated tests for conversion utilities
**Tasks**:
- [ ] Unit tests for convert_evolution_format.py
- [ ] Unit tests for filter_supported_questions.py
- [ ] Integration tests with real Evolution data
- [ ] Validation of YAML frontmatter generation
- [ ] Edge case testing (malformed input, missing fields)

**Use Cases**: Ensure conversion pipeline reliability
**Complexity**: Low | **User Value**: Medium (quality assurance)
**Effort**: 0.5 weeks
**Status**: Planned for v0.3.0 milestone

#### Question Bank Statistics Dashboard (v0.4.0)
**Description**: Generate detailed report on question bank composition
**Features**:
- [ ] Question type distribution (pie chart or table)
- [ ] Bloom's level distribution visualization
- [ ] Learning objective coverage matrix
- [ ] Supported vs. unsupported type counts
- [ ] Labels usage analysis
- [ ] Readability scores (Flesch-Kincaid)

**Use Cases**: Quality assurance, curriculum alignment verification, accreditation documentation
**Complexity**: Low-Medium | **User Value**: Medium (nice-to-have for educators)
**Effort**: 1 week

#### Scripts Documentation (v0.3.0)
**Description**: Create comprehensive documentation for utility scripts
**Tasks**:
- [ ] Create scripts/README.md documenting all utility scripts
- [ ] Document usage, inputs, outputs for each script
- [ ] Add workflow examples showing 3-step pipeline
- [ ] Include troubleshooting section for common issues
- [ ] Add inline code documentation (docstrings)

**Use Cases**: Onboarding new users, reference documentation
**Complexity**: Low | **User Value**: Medium (improves usability)
**Effort**: 0.5 weeks
**Status**: Planned for v0.3.0 milestone

---

### Integration and Export

#### Canvas Direct LMS Integration
**Description**: Export directly to Canvas without file download/upload
- [ ] Canvas API authentication
- [ ] Direct question bank upload
- [ ] Course/module selection
- [ ] Automatic QTI 1.2 format conversion

**Use Cases**: Canvas users wanting seamless workflow
**Complexity**: Medium | **User Value**: Very High (Canvas is widely used)

#### Moodle Question Bank Import/Export
**Description**: Native Moodle XML support
- [ ] Moodle Question XML format implementation
- [ ] Category and subcategory structure
- [ ] Tag preservation and generation
- [ ] Import validation in Moodle

**Use Cases**: Moodle users, cross-platform migration
**Complexity**: Medium | **User Value**: High (popular in academia)

#### Export to Quizlet/Kahoot Formats
**Description**: Study tool export for student engagement
- [ ] Quizlet flashcard format
- [ ] Kahoot quiz format
- [ ] Multiple choice → flashcard conversion
- [ ] Automatic distractor removal (flashcards need only correct answers)

**Use Cases**: Study aids, flipped classroom, review sessions
**Complexity**: Low | **User Value**: Medium (supplementary to main assessments)

---

### AI-Assisted Features

#### Auto-Generate Distractors (Multiple Choice)
**Description**: AI-generated plausible wrong answers
- [ ] GPT-4 integration for distractor generation
- [ ] Pedagogically sound distractors (common misconceptions)
- [ ] Configurable distractor count (2-5 distractors)
- [ ] Human review/editing interface

**Use Cases**: Speed up multiple choice question creation
**Complexity**: High | **User Value**: Very High (most time-consuming part of MCQ authoring)
**Note**: Requires AI API integration, cost considerations

#### Suggest Bloom's Level from Question Text
**Description**: Automatic Bloom's taxonomy classification
- [ ] Natural language processing of question stem
- [ ] Action verb detection (list, explain, analyze, evaluate)
- [ ] Contextual analysis (domain-specific understanding)
- [ ] Confidence scores for suggestions

**Use Cases**: Quality assurance, automated tagging
**Complexity**: Medium-High | **User Value**: Medium (useful but should be reviewed)

#### Generate Questions from Learning Objectives
**Description**: AI-assisted question generation
- [ ] Input: learning objective description
- [ ] Output: 3-5 question candidates at specified Bloom's level
- [ ] Multiple question types suggested
- [ ] Feedback generation

**Use Cases**: Jump-starting question development, ensuring LO coverage
**Complexity**: Very High | **User Value**: High (addresses "blank page" problem)
**Note**: Requires substantial AI infrastructure, human quality control essential

---

### Quality Assurance and Analysis

#### Statistical Analysis Dashboard
**Description**: Item analysis metrics for assessment quality
- [ ] Item difficulty (p-value: proportion correct)
- [ ] Item discrimination (point-biserial correlation)
- [ ] Distractor analysis (% selecting each option)
- [ ] Reliability estimates (KR-20, Cronbach's alpha)
- [ ] Ferguson's delta (score variance)

**Use Cases**: Post-administration quality review, question bank refinement
**Complexity**: Medium | **User Value**: High (evidence-based assessment improvement)
**Note**: Requires student response data (integration with Inspera analytics or CSV import)

#### Accessibility Compliance Checker (WCAG 2.1 AA)
**Description**: Automated accessibility validation
- [ ] Alt text requirements for images
- [ ] Proper heading hierarchy (H1, H2, H3)
- [ ] Color contrast validation
- [ ] Screen reader compatibility checks
- [ ] Keyboard navigation testing

**Use Cases**: Ensure compliance with accessibility regulations
**Complexity**: Medium | **User Value**: High (legal requirement in many jurisdictions)

#### Question Bank Quality Dashboard
**Description**: At-a-glance quality metrics
- [ ] Bloom's level distribution visualization
- [ ] Learning objective coverage matrix
- [ ] Question type diversity metrics
- [ ] Readability scores (Flesch-Kincaid, SMOG)
- [ ] Feedback quality analysis (length, specificity)

**Use Cases**: Curriculum review, accreditation documentation
**Complexity**: Medium | **User Value**: Medium (helpful for educators, nice-to-have)

#### Plagiarism/Similarity Detection
**Description**: Detect duplicate or highly similar questions
- [ ] Question text similarity scoring
- [ ] Cross-question bank comparison
- [ ] Identify paraphrased versions
- [ ] Flag potential copyright issues

**Use Cases**: Question bank integrity, avoiding repetition
**Complexity**: Medium | **User Value**: Low-Medium (more important for large banks)

---

## User Requests

*This section will be populated as users submit feature requests via GitHub Issues or direct feedback.*

### Template for New Requests

```markdown
### [Feature Name]
**Requested by**: [User/Institution]
**Date**: YYYY-MM-DD
**Priority**: [Low/Medium/High/Critical]

**Description**: Brief description of requested feature

**Use Case**: How user would use this feature

**Workaround**: Current alternative approach (if any)

**Decision**: [Under Review / Accepted / Declined / Deferred]
```

---

## Research Opportunities

### Assessment Automation Quality Study
**Topic**: Comparing quality of AI-assisted vs. manual question authoring
- Research Question: Do AI-generated distractors maintain psychometric quality?
- Methodology: Item analysis on 500 questions (250 manual, 250 AI-assisted)
- Metrics: Difficulty, discrimination, reliability comparison
- Potential Publication: Educational Measurement journal

### Bloom's Taxonomy Alignment Analysis
**Topic**: Actual vs. intended Bloom's level in educator-authored questions
- Research Question: How accurately do educators self-assign Bloom's levels?
- Methodology: Expert panel review of 1000 questions with self-reported levels
- Analysis: Inter-rater reliability, common misclassifications
- Potential Publication**: AIED (AI in Education) conference

### Cognitive Load in Test Authoring
**Topic**: Markdown vs. GUI for assessment creation
- Research Question**: Does structured markdown reduce cognitive load compared to traditional GUI authoring?
- Methodology: Eye-tracking study, NASA-TLX surveys, time-on-task analysis
- Comparison: Markdown authoring vs. Inspera GUI vs. Moodle GUI
- Potential Publication: Learning @ Scale conference

### Learning Analytics Integration
**Topic**: Using QTI metadata for predictive analytics
- Research Question: Can assessment metadata predict student performance?
- Methodology: Logistic regression models using Bloom's level, question type, LO mappings
- Data: 10,000+ student responses across 100+ assessments
- Potential Publication: Journal of Learning Analytics

---

## Declined Ideas (with Rationale)

*Features that have been considered and explicitly rejected, to avoid reconsideration.*

### Example Template

```markdown
### [Declined Feature Name]
**Status**: Declined
**Date**: YYYY-MM-DD
**Rationale**: Explanation of why this won't be implemented

**Reason Categories**:
- Out of scope (not aligned with project vision)
- Technical infeasibility (platform limitations)
- Low user value (insufficient demand)
- Resource constraints (too expensive to maintain)
```

---

## Implementation Prioritization Criteria

When promoting ideas from this document to ROADMAP.md, consider:

### User Impact (Weight: 40%)
- How many users benefit?
- How significant is the time savings or quality improvement?
- Does it address a critical pain point or nice-to-have enhancement?

### Alignment with Vision (Weight: 30%)
- Does it support the long-term vision in VISION.md?
- Does it advance research goals or community building?
- Does it differentiate from competing tools?

### Technical Feasibility (Weight: 20%)
- Complexity (effort required)
- Dependencies (external APIs, platforms)
- Maintenance burden (ongoing support costs)

### Strategic Value (Weight: 10%)
- Publications potential (academic research)
- Partnership opportunities (institutional adoption)
- Ecosystem development (community contributions)

---

## Review Process

1. **Weekly Review** (during planning session):
   - Scan new ideas added since last review
   - Discuss feasibility and value with stakeholders
   - Categorize: Promote to Roadmap / Keep in Ideas / Decline with rationale

2. **Monthly Review** (during retrospectives):
   - Assess idea age (ideas >6 months without action may be declined)
   - Re-prioritize based on user feedback
   - Update status based on technical discoveries or market changes

3. **Quarterly Review** (strategic planning):
   - Align with VISION.md long-term goals
   - Consider ecosystem trends (new LMS features, AI capabilities)
   - Major architectural decisions (e.g., API development, cloud service)

---

**Next Review**: 2025-11-08 (weekly planning)

---

**Document Metadata**:
- **Protocol Document**: Level 3 Planning (Feature Capture)
- **Review Schedule**: Weekly (during sprint planning), Monthly (retrospectives)
- **Last Major Revision**: 2025-11-01
- **Next Review**: 2025-11-08
