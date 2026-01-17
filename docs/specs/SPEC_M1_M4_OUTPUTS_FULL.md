# FULL OUTPUT SPECIFICATION: 10 Methodology Files

## Decision: FULL Implementation (10 filer)

**Rationale:**
- Primary user: Gymnasielärare
- Goal: Högkvalitativa frågor till pipeline
- Priority: Pedagogisk kvalitet
- Requirement: Kollegor ska förstå

**Strategy:** Maximal transparens och dokumentation från start

---

## File Structure Overview

```
project/
├── session.yaml
├── 00_materials/
│   ├── lecture_01.pdf
│   └── slides.pdf
├── 01_methodology/
│   ├── m1_learning_objectives.md      # 1. M1 MANDATORY
│   ├── m1_emphasis_patterns.md        # 2. M1 MANDATORY
│   ├── m1_misconceptions.md           # 3. M1 MANDATORY
│   ├── m1_examples.md                 # 4. M1 MANDATORY
│   ├── m1_material_analysis.md        # 5. M1 DOCUMENTATION
│   ├── m2_blueprint.md                # 6. M2 MANDATORY
│   ├── m2_gap_analysis.md             # 7. M2 CONDITIONAL
│   ├── m3_generation_log.md           # 8. M3 DOCUMENTATION
│   ├── m4_qa_report.md                # 9. M4 MANDATORY
│   └── m4_detailed_feedback.md        # 10. M4 DOCUMENTATION
└── 02_working/
    └── questions.md
```

---

## File Format Specifications

### Standard YAML Frontmatter Pattern

All methodology files follow:

```yaml
---
# Core metadata
module: m1|m2|m3|m4
stage: 0-5 (for M1 only)
output_type: learning_objectives|emphasis_patterns|misconceptions|...
created: 2026-01-17T15:30:00Z
session_id: abc-123-def

# File-specific structured data
[specific YAML data here]
---

# Markdown body (human readable)
[formatted content here]
```

---

## M1 OUTPUT FILES (5 filer)

### 1. m1_learning_objectives.md (MANDATORY)

**Created:** M1 Stage 5  
**Purpose:** Final learning objectives with tier classification  
**Dependencies:** None  
**Used by:** M2 (blueprint creation)

**Format:**
```yaml
---
module: m1
stage: 5
output_type: learning_objectives
created: 2026-01-17T15:30:00Z
course: "Celler och Virus"
instructor: "Niklas Karlsson"

learning_objectives:
  tier1:
    - id: LO1.1
      text: "Describe the basic structure of prokaryotic and eukaryotic cells"
      bloom: Remember
      rationale: "Fundamental concept, 30% of instruction time"
    - id: LO1.2
      text: "Explain the function of mitochondria in cellular respiration"
      bloom: Understand
      rationale: "Explicitly stated as 'critical for exam'"
  tier2:
    - id: LO2.1
      text: "Analyze how cell membrane structure relates to function"
      bloom: Analyze
      rationale: "Important for lab work, moderate emphasis"
  tier3:
    - id: LO3.1
      text: "Describe the endosymbiotic theory"
      bloom: Remember
      rationale: "Background knowledge, mentioned once"
  tier4_excluded:
    - "Advanced molecular genetics (explicitly out of scope)"
    - "Detailed biochemical pathways (covered in BI2002)"
---

# M1 Learning Objectives

**Course:** Celler och Virus (BI1001)  
**Instructor:** Niklas Karlsson  
**Date:** 2026-01-17  
**Analysis Period:** Lectures 1-8, Labs 1-3

## Tier 1: Core Concepts (Must Assess)

These concepts received the highest emphasis and are critical for assessment.

- **LO1.1** (Remember): Describe the basic structure of prokaryotic and eukaryotic cells
  - *Rationale:* Fundamental concept, 30% of instruction time, repeated in 5 contexts
  
- **LO1.2** (Understand): Explain the function of mitochondria in cellular respiration
  - *Rationale:* Explicitly stated as "critical for exam", lab focus

## Tier 2: Important (Should Assess)

- **LO2.1** (Analyze): Analyze how cell membrane structure relates to function
  - *Rationale:* Important for lab work, moderate emphasis (15% time)

## Tier 3: Useful Background (Could Assess)

- **LO3.1** (Remember): Describe the endosymbiotic theory
  - *Rationale:* Background knowledge, mentioned once, "interesting but not critical"

## Tier 4: Excluded from Assessment

- Advanced molecular genetics (explicitly stated: "out of scope for this course")
- Detailed biochemical pathways (covered in BI2002 next semester)

---

**Next Step:** Use these learning objectives in M2 Assessment Design to create blueprint.
```

---

### 2. m1_emphasis_patterns.md (MANDATORY)

**Created:** M1 Stage 2  
**Purpose:** Document emphasis signals and tier rationale  
**Dependencies:** None  
**Used by:** M2 (blueprint prioritization), M4 (validate coverage)

**Format:**
```yaml
---
module: m1
stage: 2
output_type: emphasis_patterns
created: 2026-01-17T14:45:00Z

emphasis_analysis:
  tier1:
    - topic: "Mitochondria function"
      signals:
        - type: explicit
          count: 6
          examples: ["Detta är VIKTIGT för tentan", "Kom ihåg till examen"]
        - type: time
          percentage: 30
          context: "3 of 8 lectures focused primarily on this"
        - type: repetition
          count: 5
          context: "Repeated in different contexts (lecture, lab, reading)"
      rationale: "Highest combination of explicit, time, and repetition signals"
      
    - topic: "Cell structure basics"
      signals:
        - type: repetition
          count: 5
          context: "Diagrams emphasized in multiple lectures"
        - type: foundational
          evidence: "Required for all subsequent topics"
      rationale: "Foundation for everything else, heavily diagrammed"

  tier2:
    - topic: "Membrane transport"
      signals:
        - type: time
          percentage: 15
          context: "Dedicated lab session"
        - type: explicit
          count: 2
          examples: ["Important for understanding cellular function"]
      rationale: "Practical application focus, moderate emphasis"

  tier3:
    - topic: "Endosymbiotic theory"
      signals:
        - type: explicit
          count: 1
          examples: ["Interesting background, won't be on exam"]
      rationale: "Explicitly marked as non-critical"

  tier4:
    - topic: "Advanced molecular genetics"
      signals:
        - type: explicit
          count: 1
          examples: ["Out of scope for this course, covered in BI2002"]
      rationale: "Explicitly excluded from scope"
---

# M1 Emphasis Patterns Analysis

**Analysis Date:** 2026-01-17  
**Materials Analyzed:** 8 lectures, 3 labs, 4 reading chapters  
**Total Instruction Time:** 12 hours

## Tier 1: Critical Emphasis (Must Assess)

### Mitochondria Function
**Emphasis Signals:**
- **Explicit priority:** 6 mentions
  - "Detta är VIKTIGT för tentan" (Lecture 2)
  - "Kom ihåg till examen" (Lecture 3)
  - "Kritisk förståelse" (Lab 2 handout)
  
- **Time allocation:** 30% of instruction
  - Lectures 2, 3, 5 focused primarily on this (3.6 hours)
  
- **Repetition:** 5 contexts
  - Lecture introduction → Lab application → Reading reinforcement → Exam prep review

**Rationale:** Highest combination of explicit statements, time invested, and repetition across contexts.

---

### Cell Structure Basics
**Emphasis Signals:**
- **Repetition:** 5 diagrams across lectures
- **Foundational:** Required for all subsequent topics
- **Visual emphasis:** Detailed diagrams with annotations

**Rationale:** Foundation for everything else, instructor spent significant time on visual explanations.

---

## Tier 2: Important (Should Assess)

### Membrane Transport
**Emphasis Signals:**
- **Time:** 15% of instruction (dedicated Lab 1)
- **Explicit:** "Important for understanding cellular function" (2 mentions)
- **Practical application:** Hands-on lab focus

**Rationale:** Moderate emphasis with practical application component.

---

## Tier 3: Useful Background (Could Assess)

### Endosymbiotic Theory
**Emphasis Signals:**
- **Explicit de-emphasis:** "Interesting background, won't be on exam"
- **Time:** 5% of instruction (brief mention)

**Rationale:** Explicitly marked as non-critical by instructor.

---

## Tier 4: Excluded

### Advanced Molecular Genetics
**Exclusion Signal:**
- **Explicit:** "Out of scope for this course, covered in BI2002 next semester"

**Rationale:** Explicitly excluded from this course scope.

---

## Summary Statistics

| Tier | Topics | Avg Time % | Explicit Signals | Repetition |
|------|--------|-----------|------------------|------------|
| 1    | 2      | 30%       | High (4-6)       | High (5+)  |
| 2    | 1      | 15%       | Medium (2-3)     | Medium (3) |
| 3    | 1      | 5%        | Low (1)          | Low (1)    |
| 4    | 1      | 0%        | Excluded         | N/A        |

---

**Next Step:** M2 uses these tiers to prioritize blueprint question distribution.
```

---

### 3. m1_misconceptions.md (MANDATORY)

**Created:** M1 Stage 4  
**Purpose:** Document common student errors for distractor creation  
**Dependencies:** None  
**Used by:** M3 (realistic distractor creation), M4 (validate distractor quality)

**Format:**
```yaml
---
module: m1
stage: 4
output_type: misconceptions
created: 2026-01-17T15:00:00Z

misconceptions:
  - id: M1
    topic: "Mitochondria function"
    misconception: "Mitochondria create energy from nothing"
    correct: "Mitochondria convert chemical energy (glucose → ATP)"
    evidence:
      - source: "Formative quiz week 3"
        frequency: "8/15 students"
      - source: "Lab 2 discussion"
        frequency: "Common verbal error"
    severity: high
    rationale: "Fundamental misunderstanding of energy transformation"
    teaching_strategy: "Emphasize conversion not creation, use analogy"
    distractor_example: "Mitokondrier skapar energi"
    
  - id: M2
    topic: "Cell walls"
    misconception: "All cells have cell walls"
    correct: "Only plant cells and prokaryotes have cell walls"
    evidence:
      - source: "Homework assignment 1"
        frequency: "5/15 students"
    severity: medium
    rationale: "Overgeneralization from plant cell focus"
    teaching_strategy: "Explicitly contrast animal vs plant cells"
    distractor_example: "Alla celler har cellvägg"
    
  - id: M3
    topic: "DNA location"
    misconception: "DNA is only in the nucleus"
    correct: "DNA is primarily in nucleus, but also in mitochondria"
    evidence:
      - source: "Class discussion week 5"
        frequency: "3/15 students"
    severity: low
    rationale: "Incomplete understanding, not fundamentally wrong"
    teaching_strategy: "Mention mitochondrial DNA explicitly"
    distractor_example: "DNA finns bara i cellkärnan"
---

# M1 Common Student Misconceptions

**Analysis Date:** 2026-01-17  
**Evidence Sources:** Formative quizzes, homework, lab discussions, class Q&A  
**Student Sample:** 15 students, BI1001 Fall 2025

---

## HIGH SEVERITY Misconceptions

These represent fundamental misunderstandings that must be addressed.

### M1: "Mitochondria Create Energy"

**Misconception:** Mitochondria create energy from nothing  
**Correct Understanding:** Mitochondria convert chemical energy (glucose → ATP)

**Evidence:**
- Formative quiz week 3: **8/15 students** (53%)
- Lab 2 discussion: Common verbal error during group work
- Persistent after initial instruction

**Severity:** HIGH  
**Rationale:** Violates fundamental principle of energy conservation

**Teaching Strategy Used:**
- Emphasized "transformation" not "creation"
- Analogy: "Battery charges, doesn't create electricity"
- Repeated clarification in 3 contexts

**Distractor Potential:** ⭐⭐⭐⭐⭐  
**Example Distractor:** "Mitokondrier skapar energi från ingenting"

**Notes:** This misconception persisted even after explicit correction, suggesting deep-seated conceptual error. High-quality distractor for Remember/Understand questions.

---

## MEDIUM SEVERITY Misconceptions

### M2: "All Cells Have Cell Walls"

**Misconception:** All cells have cell walls  
**Correct Understanding:** Only plant cells and prokaryotes have cell walls; animal cells do not

**Evidence:**
- Homework assignment 1: **5/15 students** (33%)
- Mentioned in 2 student questions during lecture

**Severity:** MEDIUM  
**Rationale:** Overgeneralization from plant cell focus in early lectures

**Teaching Strategy Used:**
- Explicit contrast table: Animal vs Plant cells
- Visual diagram highlighting cell membrane vs cell wall
- Lab 1 observation of both types

**Distractor Potential:** ⭐⭐⭐⭐  
**Example Distractor:** "Alla celler har cellvägg för strukturellt stöd"

**Notes:** Common error from generalization. Good distractor for multiple choice questions about cell structure.

---

## LOW SEVERITY Misconceptions

### M3: "DNA Only in Nucleus"

**Misconception:** DNA is only found in the nucleus  
**Correct Understanding:** DNA is primarily in nucleus, but also in mitochondria (and chloroplasts in plants)

**Evidence:**
- Class discussion week 5: **3/15 students** (20%)
- One written error on quiz

**Severity:** LOW  
**Rationale:** Incomplete rather than fundamentally wrong; mitochondrial DNA is advanced topic

**Teaching Strategy Used:**
- Brief mention during mitochondria lecture
- "Bonus fact" framing

**Distractor Potential:** ⭐⭐⭐  
**Example Distractor:** "DNA finns bara i cellkärnan"

**Notes:** Minor misconception, suitable for "except" type questions or higher-difficulty items.

---

## Misconception Summary Table

| ID | Topic | Misconception | Frequency | Severity | Distractor ⭐ |
|----|-------|---------------|-----------|----------|-------------|
| M1 | Mitochondria | Creates energy | 53% | High | ⭐⭐⭐⭐⭐ |
| M2 | Cell walls | All cells have | 33% | Medium | ⭐⭐⭐⭐ |
| M3 | DNA location | Only in nucleus | 20% | Low | ⭐⭐⭐ |

---

## Usage Guidelines for M3 (Question Generation)

**For HIGH severity misconceptions:**
- Use in Remember/Understand questions
- Can be primary distractor
- Explicitly address in feedback

**For MEDIUM severity misconceptions:**
- Use in Understand/Apply questions
- Good secondary distractor
- Include in partial credit feedback

**For LOW severity misconceptions:**
- Use in Apply/Analyze questions
- Optional distractor
- Brief mention in feedback sufficient

---

**Next Step:** M3 uses these documented misconceptions to create realistic, pedagogically-grounded distractors.
```

---

### 4. m1_examples.md (MANDATORY)

**Created:** M1 Stage 3  
**Purpose:** Catalog instructional examples for question context  
**Dependencies:** None  
**Used by:** M3 (question stems with familiar context), M4 (validate example references)

**Format:**
```yaml
---
module: m1
stage: 3
output_type: examples
created: 2026-01-17T14:50:00Z

examples:
  - id: EX1
    title: "Red Blood Cell Diagram"
    source: "Lecture 1, Slide 12"
    topic: "Cell structure - animal cells"
    learning_objective: LO1.1
    context: "Compared to plant cell to show structural differences"
    visual: true
    usage_count: 3
    contexts:
      - "Lecture 1: Introduction to cell types"
      - "Lab 1: Microscopy observation"
      - "Lecture 4: Review before quiz"
    effectiveness: high
    student_familiarity: very_high
    question_potential:
      bloom_levels: [Remember, Understand]
      question_types: [multiple_choice, labeling]
      example_stem: "Som vi såg i Lecture 1, vilken struktur saknar röda blodkroppar?"
      
  - id: EX2
    title: "Mitochondria ATP Production Animation"
    source: "Lecture 2, Slide 18-22"
    topic: "Cellular respiration"
    learning_objective: LO1.2
    context: "Step-by-step animation of electron transport chain"
    visual: true
    usage_count: 4
    contexts:
      - "Lecture 2: Introduced concept"
      - "Lab 2: Live microscopy observation"
      - "Lecture 5: Detailed mechanism"
      - "Review session: Student questions"
    effectiveness: very_high
    student_familiarity: very_high
    question_potential:
      bloom_levels: [Understand, Apply]
      question_types: [multiple_choice, process_ordering]
      example_stem: "Baserat på animationen från Lecture 2, vad är första steget i ATP-produktion?"
      
  - id: EX3
    title: "Membrane Transport Lab Demonstration"
    source: "Lab 1, Practical Exercise"
    topic: "Membrane transport - diffusion"
    learning_objective: LO2.1
    context: "Hands-on demonstration with dye diffusion"
    visual: true
    hands_on: true
    usage_count: 2
    contexts:
      - "Lab 1: Practical demonstration"
      - "Lecture 3: Theoretical explanation"
    effectiveness: very_high
    student_familiarity: high
    question_potential:
      bloom_levels: [Apply, Analyze]
      question_types: [scenario_based, prediction]
      example_stem: "I Lab 1 observerade vi färgdiffusion. Om koncentrationen ökas, vad händer med diffusionshastigheten?"
---

# M1 Instructional Examples Catalog

**Analysis Date:** 2026-01-17  
**Materials Reviewed:** 8 lectures, 3 labs, assigned readings  
**Total Examples Cataloged:** 3 (high-value examples only)

---

## Example 1: Red Blood Cell Diagram

**Source:** Lecture 1, Slide 12  
**Topic:** Cell structure - animal cells  
**Learning Objective:** LO1.1

### Context
Instructor used detailed diagram of red blood cell to contrast with plant cell structure, emphasizing lack of nucleus and organelles in mature RBCs.

### Usage Across Course
1. **Lecture 1:** Introduction to cell types
   - First introduction of concept
   - Compared to plant cell diagram side-by-side
   
2. **Lab 1:** Microscopy observation
   - Students viewed actual RBCs under microscope
   - Connected visual to diagram
   
3. **Lecture 4:** Review before formative quiz
   - Referenced as "remember the RBC from week 1"
   - Used to test understanding of cell structure

### Effectiveness Assessment
- **Student Familiarity:** Very High (referenced 3 times, visual memory)
- **Visual Impact:** High (clear, simple diagram)
- **Pedagogical Value:** High (effective contrast example)

### Question Potential

**Suitable Bloom Levels:** Remember, Understand

**Question Types:**
- Multiple choice (structure identification)
- Labeling diagram
- Comparison questions

**Example Question Stem:**
> "Som vi såg i Lecture 1, vilken struktur saknar mogna röda blodkroppar som de flesta andra djurceller har?"

**Why This Example Works:**
- Familiar to all students (seen 3x)
- Visual memory aid
- Clear correct answer
- Good distractors available (nucleus, mitochondria, cell wall)

---

## Example 2: Mitochondria ATP Production Animation

**Source:** Lecture 2, Slides 18-22  
**Topic:** Cellular respiration  
**Learning Objective:** LO1.2

### Context
Instructor used step-by-step animation showing electron transport chain and ATP synthase function. Animation was paused at each step for explanation.

### Usage Across Course
1. **Lecture 2:** Initial introduction
   - Animation played 2x for clarity
   - Students asked to pause and predict next step
   
2. **Lab 2:** Live microscopy
   - Viewed mitochondria under high magnification
   - Connected structure to animation function
   
3. **Lecture 5:** Detailed mechanism
   - Animation replayed with more technical detail
   - "Remember this from Lecture 2? Now let's go deeper"
   
4. **Review Session:** Student-requested replay
   - Multiple students asked to see it again
   - Clear indicator of high value

### Effectiveness Assessment
- **Student Familiarity:** Very High (4 viewings, student-requested)
- **Visual Impact:** Very High (dynamic, process-oriented)
- **Pedagogical Value:** Very High (complex concept made visual)

### Question Potential

**Suitable Bloom Levels:** Understand, Apply

**Question Types:**
- Process ordering
- Multiple choice (mechanism)
- Scenario application

**Example Question Stems:**
> "Baserat på animationen från Lecture 2, vad är första steget när elektroner transporteras genom mitokondriemembranet?"

> "Om ATP synthase blockeras (som i animationen), vad händer med protongradient?"

**Why This Example Works:**
- Extremely familiar (4 viewings)
- Students actively engaged (pause-predict)
- Process-based (good for ordering questions)
- Multiple touchpoints (lecture + lab)

---

## Example 3: Membrane Transport Lab Demonstration

**Source:** Lab 1, Practical Exercise  
**Topic:** Membrane transport - diffusion  
**Learning Objective:** LO2.1

### Context
Hands-on lab demonstration where students observed dye diffusion through membrane. Students measured diffusion rate under different conditions.

### Usage Across Course
1. **Lab 1:** Hands-on practical
   - Students directly manipulated variables
   - Recorded observations in lab notebook
   
2. **Lecture 3:** Theoretical explanation
   - Instructor referenced "your lab results from last week"
   - Connected observation to theory

### Effectiveness Assessment
- **Student Familiarity:** High (hands-on + lecture reference)
- **Visual Impact:** High (observed directly)
- **Hands-On Component:** Very High (personal experience)
- **Pedagogical Value:** Very High (concrete → abstract)

### Question Potential

**Suitable Bloom Levels:** Apply, Analyze

**Question Types:**
- Scenario-based questions
- Prediction questions
- Variable manipulation

**Example Question Stems:**
> "I Lab 1 observerade ni färgdiffusion genom en membran. Om ni ökar koncentrationsgradienten, vad händer med diffusionshastigheten?"

> "Baserat på er lab-data, förutsäg vad som skulle hända om membranens permeabilitet minskar."

**Why This Example Works:**
- Personal experience (high retention)
- Data-driven (students have their own results)
- Variable manipulation (good for Apply/Analyze)
- Concrete observation → theoretical application

---

## Example Usage Guidelines for M3

### High Familiarity Examples (EX1, EX2)
**Use for:**
- Remember/Understand questions
- Foundation questions
- All students will recognize reference

**Question Stems:**
- "Som vi såg i [source]..."
- "I [context], vilket..."
- "Baserat på [example]..."

### Hands-On Examples (EX3)
**Use for:**
- Apply/Analyze questions
- Scenario-based questions
- Questions requiring data interpretation

**Question Stems:**
- "I [lab], ni observerade... Om [variable], vad händer?"
- "Baserat på er lab-data..."
- "Förut säg resultatet om..."

### Multi-Context Examples (EX1, EX2)
**Benefits:**
- Reinforced memory (seen 3-4x)
- Multiple retrieval cues
- High validity (reflects actual instruction)

**Question Strategy:**
- Reference the FIRST introduction (Lecture 1, Lab 1)
- Students will have strongest memory of initial learning

---

## Summary Statistics

| Example | Source Type | Usage Count | Familiarity | Bloom Levels | Question Types |
|---------|------------|-------------|-------------|--------------|----------------|
| EX1: RBC | Lecture + Lab | 3 | Very High | Rem, Und | MC, Labeling |
| EX2: ATP | Lecture + Lab | 4 | Very High | Und, App | Process, MC |
| EX3: Diffusion | Lab + Lecture | 2 | High | App, Ana | Scenario, Pred |

---

**Next Step:** M3 uses these examples to create contextually-grounded question stems that students will find familiar and valid.
```

---

### 5. m1_material_analysis.md (DOCUMENTATION)

**Created:** M1 Stage 0  
**Purpose:** Audit trail of what was analyzed  
**Dependencies:** None  
**Used by:** Documentation, revision tracking

**Format:**
```yaml
---
module: m1
stage: 0
output_type: material_analysis
created: 2026-01-17T14:00:00Z
analysis_duration: 90

materials_analyzed:
  lectures:
    - title: "Lecture 1: Introduction to Cells"
      date: "2025-09-15"
      duration: 90
      slides: 45
      transcript: true
      
    - title: "Lecture 2: Mitochondria and Energy"
      date: "2025-09-22"
      duration: 60
      slides: 30
      transcript: true
      
  labs:
    - title: "Lab 1: Cell Observation"
      date: "2025-09-20"
      handout_pages: 8
      practical: true
      
  readings:
    - title: "Campbell Biology Ch. 3-4"
      pages: 45
      required: true
      
completeness:
  all_lectures: true
  all_labs: true
  all_readings: true
  missing: ["Guest lecture (scheduled 2026-02-05)"]
---

# M1 Material Analysis

**Analysis Date:** 2026-01-17  
**Time Spent:** 90 minutes  
**Analyst:** Claude Sonnet 4

---

## Materials Analyzed

### Lectures (8 total)

1. **Lecture 1: Introduction to Cells**
   - Date: 2025-09-15
   - Duration: 90 minutes
   - Slides: 45
   - Transcript: ✅ Available
   - Topics: Cell types, prokaryotic vs eukaryotic, basic structure
   
2. **Lecture 2: Mitochondria and Energy**
   - Date: 2025-09-22
   - Duration: 60 minutes
   - Slides: 30
   - Transcript: ✅ Available
   - Topics: Cellular respiration, ATP production, electron transport
   
[Continue for all 8 lectures...]

### Labs (3 total)

1. **Lab 1: Cell Observation and Membrane Transport**
   - Date: 2025-09-20
   - Handout: 8 pages
   - Practical: ✅ Yes
   - Activities: Microscopy, diffusion demonstration
   
[Continue for all 3 labs...]

### Readings (4 chapters)

1. **Campbell Biology Ch. 3-4**
   - Pages: 45
   - Required: ✅ Yes
   - Topics: Cell structure, organelles
   
[Continue for all readings...]

---

## Completeness Check

✅ **All scheduled lectures analyzed** (8/8)  
✅ **All lab materials analyzed** (3/3)  
✅ **All required readings analyzed** (4/4)  
⚠️ **Missing:** Guest lecture (scheduled 2026-02-05, not yet delivered)

---

## Analysis Approach

### Phase 1: Initial Read-Through (30 min)
- Read all materials chronologically
- Noted topics covered
- Identified recurring themes

### Phase 2: Emphasis Signal Detection (40 min)
- Flagged explicit priority statements
- Tracked time allocation per topic
- Noted repetition patterns
- Cataloged examples used

### Phase 3: Synthesis (20 min)
- Grouped related content
- Identified learning objectives
- Classified by importance (Tier 1-4)

---

## Material Quality Assessment

### Lecture Materials
- **Clarity:** High (well-structured slides, clear explanations)
- **Consistency:** High (topics build logically)
- **Emphasis Signals:** Very High (explicit statements, time allocation clear)

### Lab Materials
- **Hands-On Component:** Strong (3 practical sessions)
- **Connection to Theory:** Good (labs referenced in lectures)
- **Examples Generated:** High-value (EX3 from Lab 1)

### Reading Materials
- **Alignment:** Strong (chapters match lecture topics)
- **Supplementary Value:** Good (provides depth beyond lectures)

---

**Next Step:** Use this material base to proceed with Stages 1-5 of M1.
```

---

## M2 OUTPUT FILES (2 filer)

### 6. m2_blueprint.md (MANDATORY)

**Created:** M2 Stage completion  
**Purpose:** Assessment design plan with Bloom/difficulty distribution  
**Dependencies:** M1 (learning_objectives, emphasis_patterns)  
**Used by:** M3 (question generation specs)

**Format:**
```yaml
---
module: m2
output_type: blueprint
created: 2026-01-17T16:00:00Z
based_on:
  - 01_methodology/m1_learning_objectives.md
  - 01_methodology/m1_emphasis_patterns.md

assessment_parameters:
  total_questions: 20
  duration_minutes: 60
  format: "Multiple choice and short answer"
  
blueprint:
  dimensions:
    bloom_levels: [Remember, Understand, Apply, Analyze]
    difficulty: [Easy, Medium, Hard]
    
  distribution:
    - bloom: Remember
      easy: 5
      medium: 3
      hard: 0
      total: 8
      rationale: "Foundation concepts, Tier 1 topics"
      
    - bloom: Understand
      easy: 3
      medium: 4
      hard: 1
      total: 8
      rationale: "Core understanding, mix of Tier 1-2"
      
    - bloom: Apply
      easy: 0
      medium: 2
      hard: 1
      total: 3
      rationale: "Lab applications, Tier 2 topics"
      
    - bloom: Analyze
      easy: 0
      medium: 0
      hard: 1
      total: 1
      rationale: "Advanced, Tier 2 only"
      
  total_by_difficulty:
    easy: 8
    medium: 9
    hard: 3
    
  tier_coverage:
    tier1: 14  # 70% of questions
    tier2: 6   # 30% of questions
    tier3: 0   # Not assessed
    tier4: 0   # Excluded

question_specifications:
  - id: "Q001-Q005"
    bloom: Remember
    difficulty: Easy
    tier: 1
    learning_objective: LO1.1
    topic: "Cell structure basics"
    suggested_format: "Multiple choice"
    notes: "Use EX1 (RBC diagram) for context"
    
  - id: "Q006-Q008"
    bloom: Remember
    difficulty: Medium
    tier: 1
    learning_objective: LO1.2
    topic: "Mitochondria function"
    suggested_format: "Multiple choice"
    notes: "Use M1 misconception for distractor"
    
  [Continue for all 20 questions...]
---

# M2 Assessment Blueprint

**Created:** 2026-01-17  
**Course:** Celler och Virus (BI1001)  
**Assessment Type:** Midterm Exam  
**Duration:** 60 minutes  
**Total Questions:** 20

---

## Design Philosophy

This blueprint prioritizes **Tier 1 learning objectives** (70% of questions) to ensure comprehensive assessment of critical concepts while including **Tier 2 objectives** (30%) for breadth.

**Key Principles:**
- Emphasis-driven: Question distribution reflects instructional emphasis
- Bloom-balanced: Progresses from Remember to Analyze
- Difficulty-appropriate: Mostly Easy/Medium for midterm timing

---

## Question Distribution Matrix

### By Bloom Level and Difficulty

| Bloom Level | Easy | Medium | Hard | Total | % of Exam |
|-------------|------|--------|------|-------|-----------|
| Remember    | 5    | 3      | 0    | 8     | 40%       |
| Understand  | 3    | 4      | 1    | 8     | 40%       |
| Apply       | 0    | 2      | 1    | 3     | 15%       |
| Analyze     | 0    | 0      | 1    | 1     | 5%        |
| **Total**   | **8**| **9**  | **3**| **20**| **100%**  |

**Rationale:**
- 40% Remember: Foundation (aligned with Tier 1 emphasis)
- 40% Understand: Core comprehension (Tier 1-2 mix)
- 15% Apply: Lab applications (Tier 2 focus)
- 5% Analyze: Advanced integration (Tier 2 only)

---

### By Tier Coverage

| Tier | Questions | % of Exam | Rationale |
|------|-----------|-----------|-----------|
| 1    | 14        | 70%       | Highest instructional emphasis |
| 2    | 6         | 30%       | Important but moderate emphasis |
| 3    | 0         | 0%        | Useful background, not assessed |
| 4    | 0         | 0%        | Explicitly excluded |

**Alignment Check:**
- Tier 1 received 45% of instruction time → 70% of assessment ✅
- Tier 2 received 25% of instruction time → 30% of assessment ✅
- Proportional to emphasis patterns from M1

---

## Question Specifications for M3

### Remember Level (8 questions)

#### Q001-Q005: Cell Structure Basics (Easy)
- **Learning Objective:** LO1.1
- **Tier:** 1
- **Difficulty:** Easy
- **Suggested Format:** Multiple choice
- **Context:** Use EX1 (Red Blood Cell diagram from Lecture 1)
- **Example Stem:** "Som vi såg i Lecture 1, vilken struktur saknar mogna röda blodkroppar?"
- **Distractor Source:** Use M2 (cell wall misconception)

#### Q006-Q008: Mitochondria Function (Medium)
- **Learning Objective:** LO1.2
- **Tier:** 1
- **Difficulty:** Medium
- **Suggested Format:** Multiple choice
- **Context:** Use EX2 (ATP animation from Lecture 2)
- **Example Stem:** "Baserat på ATP-produktionsprocessen från Lecture 2..."
- **Distractor Source:** Use M1 (energy creation misconception)

---

### Understand Level (8 questions)

#### Q009-Q011: Cell Membrane Function (Easy)
- **Learning Objective:** LO2.1
- **Tier:** 2
- **Difficulty:** Easy
- **Suggested Format:** Multiple choice
- **Context:** General cell membrane structure-function
- **Distractor Source:** Common structural misconceptions

#### Q012-Q015: Mitochondria Mechanism (Medium)
- **Learning Objective:** LO1.2
- **Tier:** 1
- **Difficulty:** Medium
- **Suggested Format:** Multiple choice or short answer
- **Context:** Explain ATP synthesis process
- **Distractor Source:** Mechanism misconceptions

---

### Apply Level (3 questions)

#### Q016-Q017: Membrane Transport Application (Medium)
- **Learning Objective:** LO2.1
- **Tier:** 2
- **Difficulty:** Medium
- **Suggested Format:** Scenario-based
- **Context:** Use EX3 (Lab 1 diffusion demonstration)
- **Example Stem:** "I Lab 1, ni observerade... Om variabel X ändras, vad händer?"
- **Requires:** Apply understanding to new scenario

#### Q018: Cell Structure Application (Hard)
- **Learning Objective:** LO1.1 + LO1.2
- **Tier:** 1
- **Difficulty:** Hard
- **Suggested Format:** Integrated scenario
- **Requires:** Apply knowledge of multiple concepts

---

### Analyze Level (1 question)

#### Q019: Integrated Analysis (Hard)
- **Learning Objective:** LO2.1
- **Tier:** 2
- **Difficulty:** Hard
- **Suggested Format:** Short answer or multi-part
- **Requires:** Analyze relationship between structure and function
- **Example:** Compare two cell types and explain functional differences

---

## Time Allocation Estimate

- Remember questions (Easy): ~1.5 min each = 7.5 min
- Remember questions (Medium): ~2 min each = 6 min
- Understand questions (Easy): ~2 min each = 6 min
- Understand questions (Medium): ~3 min each = 12 min
- Understand questions (Hard): ~4 min each = 4 min
- Apply questions (Medium): ~4 min each = 8 min
- Apply questions (Hard): ~5 min each = 5 min
- Analyze questions (Hard): ~6 min = 6 min

**Total estimated time:** 54.5 minutes (leaves 5.5 min buffer)

---

## Quality Checkpoints

Before finalizing questions in M3, ensure:

✅ All Tier 1 LOs assessed (minimum 2 questions each)  
✅ Question distribution matches blueprint  
✅ Examples from instruction referenced where possible  
✅ Misconceptions used for realistic distractors  
✅ Difficulty progression is smooth (Easy → Hard)  
✅ Time estimate realistic for 60-minute exam

---

**Next Step:** M3 uses these specifications to generate 20 questions matching blueprint exactly.
```

---

### 7. m2_gap_analysis.md (CONDITIONAL - only if entry 'pipeline')

**Created:** M2 Stage (if existing questions.md)  
**Purpose:** Analyze coverage gaps in existing questions  
**Dependencies:** M1 (learning_objectives), questions.md (existing)  
**Used by:** M2 blueprint, M3 (what to generate)

**Format:**
```yaml
---
module: m2
output_type: gap_analysis
created: 2026-01-17T16:10:00Z
conditional: true
condition: "Entry point 'pipeline' with existing questions"

existing_questions:
  total: 15
  source: "Fall 2024 Midterm Exam"
  
coverage_analysis:
  tier1:
    - objective: LO1.1
      coverage: "good"
      questions: [Q001, Q002, Q003]
      gap: null
      
    - objective: LO1.2
      coverage: "good"
      questions: [Q004, Q005]
      gap: null
      
    - objective: LO1.3
      coverage: "missing"
      questions: []
      gap: "Need 2-3 questions (Remember + Understand)"
      
  tier2:
    - objective: LO2.1
      coverage: "partial"
      questions: [Q012]
      gap: "Need 1-2 more Apply questions"
      
bloom_distribution:
  existing:
    Remember: 7
    Understand: 6
    Apply: 2
    Analyze: 0
  needed:
    Remember: 2  # For LO1.3
    Understand: 1  # For LO1.3
    Apply: 2  # For LO2.1
    Analyze: 0  # Not critical for midterm
    
difficulty_distribution:
  existing:
    Easy: 8
    Medium: 6
    Hard: 1
  needed:
    Easy: 1
    Medium: 3
    Hard: 1

gaps_identified:
  critical:
    - "LO1.3 (DNA/RNA comparison): MISSING (Tier 1)"
    - "LO2.1 (Membrane transport): UNDER-REPRESENTED (Tier 2)"
  moderate:
    - "No Analyze-level questions (acceptable for midterm)"
    - "Hard difficulty under-represented (only 1 question)"
    
recommended_additions:
  - id: "NEW_Q016"
    objective: LO1.3
    bloom: Remember
    difficulty: Easy
    rationale: "Fill critical Tier 1 gap"
    
  - id: "NEW_Q017"
    objective: LO1.3
    bloom: Remember
    difficulty: Easy
    rationale: "Fill critical Tier 1 gap"
    
  - id: "NEW_Q018"
    objective: LO1.3
    bloom: Understand
    difficulty: Medium
    rationale: "Fill critical Tier 1 gap, add Understand depth"
    
  - id: "NEW_Q019"
    objective: LO2.1
    bloom: Apply
    difficulty: Medium
    rationale: "Fill Tier 2 gap, use Lab 1 context"
    
  - id: "NEW_Q020"
    objective: LO2.1
    bloom: Apply
    difficulty: Hard
    rationale: "Fill Tier 2 gap, add difficulty balance"
---

# M2 Gap Analysis: Existing Questions

**Analysis Date:** 2026-01-17  
**Existing Questions:** 15 (from Fall 2024 Midterm)  
**Target:** 20 questions total  
**Gap:** 5 questions needed

---

## Coverage Analysis by Learning Objective

### Tier 1 Objectives (Critical)

#### LO1.1: Cell Structure - ✅ GOOD COVERAGE
**Existing Questions:** Q001, Q002, Q003 (3 questions)  
**Status:** Adequate coverage  
**Gap:** None  
**Rationale:** Foundational concept well-represented

---

#### LO1.2: Mitochondria Function - ✅ GOOD COVERAGE
**Existing Questions:** Q004, Q005 (2 questions)  
**Status:** Adequate coverage  
**Gap:** None  
**Rationale:** Core concept addressed, matches emphasis

---

#### LO1.3: DNA/RNA Comparison - ❌ MISSING (CRITICAL GAP)
**Existing Questions:** None  
**Status:** Complete gap  
**Gap:** **Need 2-3 questions minimum**  
**Severity:** HIGH (Tier 1 objective not assessed)  
**Recommendation:**
- Add 2x Remember (Easy) - basic identification
- Add 1x Understand (Medium) - comparison/contrast

---

### Tier 2 Objectives (Important)

#### LO2.1: Membrane Transport - ⚠️ PARTIAL COVERAGE
**Existing Questions:** Q012 (1 question)  
**Status:** Under-represented  
**Gap:** **Need 1-2 more Apply questions**  
**Severity:** MEDIUM (Tier 2, but lab-focused)  
**Recommendation:**
- Add 1x Apply (Medium) - use Lab 1 context
- Add 1x Apply (Hard) - scenario-based

---

## Distribution Gaps

### Bloom Level Distribution

| Bloom | Existing | Needed | Target | Gap |
|-------|----------|--------|--------|-----|
| Remember | 7 | +2 | 9 | Fill LO1.3 |
| Understand | 6 | +1 | 7 | Fill LO1.3 |
| Apply | 2 | +2 | 4 | Fill LO2.1 |
| Analyze | 0 | 0 | 0 | Not critical |

**Analysis:**
- Remember: Need more for LO1.3 coverage
- Understand: Slight increase for breadth
- Apply: Significantly under-represented (only 13% vs target 20%)

---

### Difficulty Distribution

| Difficulty | Existing | Needed | Target | Gap |
|------------|----------|--------|--------|-----|
| Easy | 8 | +1 | 9 | Minor |
| Medium | 6 | +3 | 9 | Significant |
| Hard | 1 | +1 | 2 | Add balance |

**Analysis:**
- Heavy on Easy questions (53% vs target 45%)
- Under-represented Medium (40% vs target 45%)
- Need more Hard questions for differentiation

---

## Recommended Additions (5 questions)

### Critical Additions (Tier 1 Gap)

**NEW_Q016:** LO1.3, Remember, Easy
- **Topic:** DNA structure identification
- **Rationale:** Fill critical Tier 1 gap
- **Suggested Stem:** "Vilken molekyl innehåller deoxiribos?"
- **Distractor:** Use M3 misconception if documented

**NEW_Q017:** LO1.3, Remember, Easy
- **Topic:** RNA structure identification
- **Rationale:** Fill critical Tier 1 gap
- **Suggested Stem:** "Vilken typ av ribos finns i RNA?"

**NEW_Q018:** LO1.3, Understand, Medium
- **Topic:** DNA/RNA comparison
- **Rationale:** Fill Tier 1 gap with higher-order thinking
- **Suggested Stem:** "Lista tre strukturella skillnader mellan DNA och RNA"
- **Format:** Short answer or multiple choice

---

### Important Additions (Tier 2 Gap + Balance)

**NEW_Q019:** LO2.1, Apply, Medium
- **Topic:** Membrane transport application
- **Rationale:** Fill Tier 2 Apply gap
- **Context:** Use EX3 (Lab 1 diffusion)
- **Suggested Stem:** "I Lab 1, ni observerade färgdiffusion. Om koncentrationsgradienten ökas, vad händer med diffusionshastigheten?"

**NEW_Q020:** LO2.1, Apply, Hard
- **Topic:** Complex transport scenario
- **Rationale:** Add Hard difficulty balance + Tier 2 Apply
- **Suggested Stem:** Scenario requiring integration of multiple transport mechanisms

---

## Gap Summary

### Critical Gaps (Must Fix)
1. ❌ **LO1.3 missing entirely** (Tier 1) → Add 3 questions
2. ⚠️ **Apply questions under-represented** → Add 2 questions

### Quality Improvements
3. ⚠️ **Medium difficulty under-represented** → Shift focus to Medium
4. ⚠️ **Hard questions too few** → Add 1 Hard for differentiation

---

## Blueprint Integration

These 5 additions + 15 existing = 20 total questions matching M2 blueprint:

| Component | Existing | Added | Total | Target | ✓ |
|-----------|----------|-------|-------|--------|---|
| Remember Easy | 5 | +2 | 7 | 7-9 | ✅ |
| Remember Med | 2 | 0 | 2 | 2-3 | ✅ |
| Understand Easy | 3 | 0 | 3 | 3 | ✅ |
| Understand Med | 3 | +1 | 4 | 4 | ✅ |
| Apply Medium | 1 | +1 | 2 | 2 | ✅ |
| Apply Hard | 1 | +1 | 2 | 2 | ✅ |

**Result:** Perfect alignment with blueprint ✅

---

**Next Step:** M3 generates ONLY the 5 identified gap questions, preserving existing 15 questions.
```

---

## M3 OUTPUT FILE (1 fil)

### 8. m3_generation_log.md (DOCUMENTATION)

**Created:** M3 completion  
**Purpose:** Metadata about question generation process  
**Dependencies:** M2 blueprint, questions.md  
**Used by:** Documentation, research tracking

**Format:**
```yaml
---
module: m3
output_type: generation_log
created: 2026-01-17T17:00:00Z

generation_session:
  start_time: "2026-01-17T16:30:00Z"
  end_time: "2026-01-17T17:15:00Z"
  duration_minutes: 45
  model: "Claude Sonnet 4"
  
input_documents:
  - 01_methodology/m2_blueprint.md
  - 01_methodology/m1_examples.md
  - 01_methodology/m1_misconceptions.md
  - 02_working/questions.md  # If entry 'pipeline'
  
generation_summary:
  total_generated: 20
  from_scratch: 20  # Or 5 if entry 'pipeline'
  modified_existing: 0
  
source_usage:
  examples_referenced: 8
  misconceptions_used: 12
  blueprint_specs_followed: 20
  
question_breakdown:
  - id: Q001
    bloom: Remember
    difficulty: Easy
    learning_objective: LO1.1
    tier: 1
    example_used: EX1
    misconception_used: null
    generation_time: "2 min"
    iterations: 1
    
  - id: Q002
    bloom: Remember
    difficulty: Easy
    learning_objective: LO1.2
    tier: 1
    example_used: EX2
    misconception_used: M1
    generation_time: "3 min"
    iterations: 2
    notes: "Revised distractor to match M1 misconception"
    
  [Continue for all questions...]
  
generation_statistics:
  avg_time_per_question: "2.25 min"
  questions_using_examples: 8
  questions_using_misconceptions: 12
  total_iterations: 25
  avg_iterations_per_question: 1.25
  
quality_notes:
  - "All questions match blueprint specifications"
  - "8/20 questions use instructional examples for context"
  - "12/20 questions use documented misconceptions for distractors"
  - "Tier 1 objectives: 14 questions (70%)"
  - "Tier 2 objectives: 6 questions (30%)"
---

# M3 Question Generation Log

**Generation Date:** 2026-01-17  
**Session Duration:** 45 minutes  
**Questions Generated:** 20  
**Model:** Claude Sonnet 4

---

## Generation Session Summary

**Start Time:** 16:30  
**End Time:** 17:15  
**Total Duration:** 45 minutes  
**Average per question:** 2.25 minutes

---

## Input Documents Used

✅ `01_methodology/m2_blueprint.md` - Question specifications  
✅ `01_methodology/m1_examples.md` - Instructional context  
✅ `01_methodology/m1_misconceptions.md` - Distractor sources  
✅ `01_methodology/m1_learning_objectives.md` - Tier classifications

---

## Generation Approach

### Phase 1: Blueprint Alignment (10 min)
- Reviewed M2 blueprint specifications
- Mapped questions to learning objectives
- Identified example and misconception opportunities

### Phase 2: Question Drafting (25 min)
- Generated questions in Bloom/difficulty order
- Remember → Understand → Apply → Analyze
- Easy → Medium → Hard within each Bloom level

### Phase 3: Quality Check (10 min)
- Verified blueprint compliance
- Ensured example references valid
- Confirmed misconception usage appropriate
- Cross-checked tier distribution

---

## Source Usage Analysis

### Instructional Examples Referenced

| Example | Questions Using | Purpose |
|---------|----------------|---------|
| EX1 (RBC Diagram) | Q001, Q002, Q003 | Familiar context |
| EX2 (ATP Animation) | Q006, Q007, Q008, Q012 | Process understanding |
| EX3 (Lab Diffusion) | Q016, Q019 | Applied scenarios |

**Total:** 8/20 questions (40%) use documented examples ✅

---

### Misconceptions Used for Distractors

| Misconception | Questions Using | Distractor Quality |
|---------------|----------------|-------------------|
| M1 (Energy creation) | Q006, Q007, Q008, Q012, Q013 | High (53% frequency) |
| M2 (Cell walls) | Q001, Q002, Q003, Q004 | Medium (33% frequency) |
| M3 (DNA nucleus only) | Q014, Q015, Q018 | Low (20% frequency) |

**Total:** 12/20 questions (60%) use documented misconceptions ✅

---

## Question-by-Question Generation Notes

### Q001: Cell Structure Basic (Remember, Easy, LO1.1)
- **Generation Time:** 2 minutes
- **Iterations:** 1
- **Example Used:** EX1 (Red Blood Cell diagram)
- **Misconception Used:** M2 (Cell walls)
- **Stem:** "Som vi såg i Lecture 1, vilken struktur saknar mogna röda blodkroppar?"
- **Notes:** Straightforward, used familiar context from EX1

---

### Q002: Mitochondria Misconception (Remember, Easy, LO1.2)
- **Generation Time:** 3 minutes
- **Iterations:** 2
- **Example Used:** EX2 (ATP Animation)
- **Misconception Used:** M1 (Energy creation)
- **Stem:** "Baserat på ATP-produktionsprocessen från Lecture 2, vad gör mitokondrier?"
- **Notes:** First iteration had generic distractor; revised to use M1 misconception ("skapar energi")

---

[Continue detailed notes for all 20 questions...]

---

## Generation Statistics

| Metric | Value |
|--------|-------|
| Total questions | 20 |
| Avg time per question | 2.25 min |
| Total iterations | 25 |
| Avg iterations per question | 1.25 |
| Questions using examples | 8 (40%) |
| Questions using misconceptions | 12 (60%) |
| Questions revised after initial draft | 5 (25%) |

---

## Blueprint Compliance Check

### Bloom Distribution

| Bloom | Target | Generated | ✓ |
|-------|--------|-----------|---|
| Remember | 8 | 8 | ✅ |
| Understand | 8 | 8 | ✅ |
| Apply | 3 | 3 | ✅ |
| Analyze | 1 | 1 | ✅ |

---

### Difficulty Distribution

| Difficulty | Target | Generated | ✓ |
|------------|--------|-----------|---|
| Easy | 8 | 8 | ✅ |
| Medium | 9 | 9 | ✅ |
| Hard | 3 | 3 | ✅ |

---

### Tier Coverage

| Tier | Target | Generated | ✓ |
|------|--------|-----------|---|
| 1 | 14 | 14 | ✅ |
| 2 | 6 | 6 | ✅ |
| 3 | 0 | 0 | ✅ |
| 4 | 0 | 0 | ✅ |

**Result:** 100% compliance with M2 blueprint specifications ✅

---

## Quality Assessment Notes

**Strengths:**
- ✅ All questions match blueprint exactly
- ✅ 40% of questions use documented instructional examples (high context validity)
- ✅ 60% of questions use documented misconceptions (realistic distractors)
- ✅ Tier distribution matches emphasis patterns from M1

**Areas for M4 Review:**
- ⚠️ Q012: Check if ATP animation reference is clear enough
- ⚠️ Q018: Verify DNA/RNA comparison is at correct difficulty level
- ⚠️ Q019: Lab context might need more explicit setup

**Iterative Improvements Made:**
- 5 questions revised after initial draft
- Primary revision: Improving distractor realism using misconceptions
- Secondary revision: Clarifying stems using example references

---

## Pedagogical Grounding Summary

**Example Integration:**
- 8/20 questions explicitly reference instructional materials
- Students will recognize contexts from lectures and labs
- High construct validity (questions test what was taught)

**Misconception-Based Distractors:**
- 12/20 questions use documented student errors
- Distractors are realistic (based on actual student responses)
- Tests genuine understanding, not trick questions

**Tier-Emphasis Alignment:**
- 70% questions on Tier 1 (highest instructional emphasis)
- 30% questions on Tier 2 (moderate emphasis)
- 0% questions on Tier 3-4 (background or excluded)
- Perfect alignment with M1 emphasis patterns ✅

---

**Next Step:** M4 Quality Assurance reviews all 20 questions for final approval.
```

---

## M4 OUTPUT FILES (2 filer)

### 9. m4_qa_report.md (MANDATORY)

**Created:** M4 completion  
**Purpose:** Summary of quality assurance process  
**Dependencies:** questions.md, M1 outputs (for validation)  
**Used by:** Final approval, revision tracking

**Format:**
```yaml
---
module: m4
output_type: qa_report
created: 2026-01-17T17:45:00Z
reviewed_by: "Claude + Niklas Karlsson"

qa_summary:
  total_reviewed: 20
  status:
    approved: 18
    needs_revision: 2
    rejected: 0
  approval_rate: 90%
  
quality_dimensions:
  technical:
    correct_answers_verified: 20
    distractor_plausibility: 18  # 2 need improvement
    stem_clarity: 18  # 2 need revision
  
  pedagogical:
    bloom_level_accurate: 19  # 1 needs adjustment
    difficulty_appropriate: 19  # 1 needs adjustment
    misconception_usage: 12  # All appropriate
    example_references: 8  # All valid
    
  alignment:
    blueprint_compliance: 20  # 100%
    tier_coverage: 20  # Matches M1 emphasis
    learning_objectives: 20  # All mapped correctly

issues_identified:
  critical: []
  moderate:
    - question: Q018
      issue: "Stem clarity - 'Compare' too vague"
      severity: medium
      action: revision_required
      
    - question: Q012
      issue: "Bloom level - should be Apply not Understand"
      severity: medium
      action: revision_required

feedback_summary:
  strengths:
    - "Strong use of instructional examples (8/20)"
    - "Realistic distractors from misconceptions (12/20)"
    - "Perfect tier distribution (70% Tier 1, 30% Tier 2)"
    
  improvements_needed:
    - "Q018: Make stem more specific"
    - "Q012: Adjust Bloom level or rewrite"
---

# M4 Quality Assurance Report

**QA Date:** 2026-01-17  
**Reviewed By:** Claude Sonnet 4 + Niklas Karlsson  
**Questions Reviewed:** 20  
**Approval Rate:** 90% (18/20 approved, 2 need revision)

---

## Executive Summary

**Overall Assessment:** HIGH QUALITY ✅

The question set demonstrates strong pedagogical grounding with:
- Perfect blueprint compliance (20/20)
- Excellent use of instructional examples (8/20, 40%)
- Realistic distractors from documented misconceptions (12/20, 60%)
- Appropriate tier emphasis distribution

**Required Actions:**
- 2 questions need revision (Q012, Q018)
- 18 questions approved for immediate use

---

## Approval Status

### ✅ APPROVED (18 questions)

Questions ready for exam without modification:

**Remember Level (7/8 approved):**
- Q001-Q005: ✅ Excellent
- Q006-Q007: ✅ Good
- Q008: ✅ Good

**Understand Level (8/8 approved):**
- Q009-Q011: ✅ Good
- Q013-Q015: ✅ Excellent
- Q016-Q017: ✅ Good

**Apply Level (2/3 approved):**
- Q019: ✅ Excellent (Lab context)
- Q020: ✅ Good

**Analyze Level (1/1 approved):**
- Q021: ✅ Good

---

### ⚠️ NEEDS REVISION (2 questions)

#### Q012: Bloom Level Mismatch
**Current Classification:** Understand, Medium  
**Issue:** Question asks to "apply" ATP knowledge to new scenario, not just understand  
**Recommended Action:** Reclassify as Apply OR rewrite to test understanding only  
**Severity:** MEDIUM  
**Impact:** Blueprint balance (Understand 8 → 7, Apply 3 → 4)

**Current Stem:**
> "Om ATP synthase blockeras, hur påverkas protongradient?"

**Analysis:**
- This requires APPLYING understanding of ATP synthesis
- Not just UNDERSTANDING the process
- Better suited for Apply level

**Recommendation:**
- **Option A:** Reclassify as Apply, Medium (preferred)
- **Option B:** Rewrite to test understanding: "Vad är funktionen av ATP synthase?"

**Decision:** Move to Apply category → Blueprint remains balanced ✅

---

#### Q018: Stem Clarity Issue
**Current Classification:** Understand, Medium  
**Issue:** Stem uses vague verb "Jämför" without specific criteria  
**Recommended Action:** Specify what type of comparison is required  
**Severity:** MEDIUM  
**Impact:** Student confusion, ambiguous answers

**Current Stem:**
> "Jämför DNA och RNA"

**Problem:**
- Too open-ended for multiple choice format
- Students don't know what aspect to compare
- Multiple valid comparisons possible

**Suggested Revision:**
> "Lista tre strukturella skillnader mellan DNA och RNA"

**Improvement:**
- Specific: "strukturella skillnader"
- Quantified: "tre"
- Clear expectation for answer format

**Decision:** Revise stem for clarity → Maintain classification ✅

---

## Quality Dimension Analysis

### Technical Quality (20/20 pass)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Correct answers verified | 20/20 | ✅ All scientifically accurate |
| Distractors plausible | 18/20 | ⚠️ Q003, Q015 have one weak distractor each |
| Stem clarity | 18/20 | ⚠️ Q018 too vague, Q012 needs adjustment |
| No tricks or gotchas | 20/20 | ✅ Fair questions |

**Notes:**
- Q003: Distractor "Mitokondrier producerar kväve" is implausible (too obviously wrong)
- Q015: Distractor needs minor improvement for plausibility
- Both are minor issues; questions still functional

---

### Pedagogical Quality (19/20 pass)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Bloom level accurate | 19/20 | ⚠️ Q012 should be Apply |
| Difficulty appropriate | 19/20 | ⚠️ Q018 might be Easy not Medium |
| Misconception usage | 12/12 | ✅ All appropriate uses |
| Example references | 8/8 | ✅ All valid and clear |
| Tier alignment | 20/20 | ✅ Perfect (70% T1, 30% T2) |

**Strong Points:**
- Misconceptions used realistically (M1: 53% student error → high-quality distractor)
- Examples from instruction (EX1, EX2, EX3 all referenced appropriately)
- Tier distribution matches emphasis perfectly

---

### Blueprint Compliance (20/20 pass)

| Component | Target | Actual | ✓ |
|-----------|--------|--------|---|
| Remember Easy | 5 | 5 | ✅ |
| Remember Medium | 3 | 3 | ✅ |
| Understand Easy | 3 | 3 | ✅ |
| Understand Medium | 4 | 3* | ⚠️ (Q012 moved to Apply) |
| Apply Medium | 2 | 3* | ⚠️ (Q012 moved here) |
| Apply Hard | 1 | 1 | ✅ |
| Analyze Hard | 1 | 1 | ✅ |

*After Q012 reclassification, distribution still matches blueprint intent ✅

---

## Detailed Question Feedback

### EXEMPLARY Questions (5 questions)

These questions demonstrate best practices:

**Q001: Red Blood Cell Structure**
- ✅ Uses familiar context (EX1 from Lecture 1)
- ✅ Realistic distractor from M2 misconception
- ✅ Clear, unambiguous stem
- ✅ Perfect Remember/Easy alignment
- **Rating:** ⭐⭐⭐⭐⭐

**Q006: Mitochondria Energy Function**
- ✅ References EX2 (ATP animation)
- ✅ Uses M1 misconception ("skapar energi") as distractor
- ✅ Tests critical Tier 1 concept
- ✅ Pedagogically grounded
- **Rating:** ⭐⭐⭐⭐⭐

**Q019: Lab Application (Diffusion)**
- ✅ Direct reference to Lab 1 (EX3)
- ✅ Requires application to new variable
- ✅ Perfect Apply/Medium difficulty
- ✅ Students will recognize context
- **Rating:** ⭐⭐⭐⭐⭐

---

### GOOD Questions (13 questions)

Solid quality, no issues:

Q002, Q003, Q004, Q005, Q007, Q008, Q009, Q010, Q011, Q013, Q014, Q016, Q017, Q020, Q021

**Common Strengths:**
- Clear stems
- Appropriate difficulty
- Valid distractors
- Blueprint-aligned

---

### NEEDS IMPROVEMENT (2 questions)

See detailed feedback above for Q012 and Q018.

---

## Misconception Usage Validation

| Misconception | Questions | Distractor Quality | Valid? |
|---------------|-----------|-------------------|--------|
| M1 (Energy creation) | Q006, Q007, Q008 | High (53% error rate) | ✅ |
| M2 (Cell walls) | Q001, Q002, Q003 | Medium (33% error rate) | ✅ |
| M3 (DNA location) | Q014, Q015 | Low (20% error rate) | ✅ |

**Assessment:** All misconceptions used appropriately ✅

**Notes:**
- M1 used most frequently (highest student error rate)
- M2 used for foundation questions
- M3 used sparingly (lower severity)

---

## Example Reference Validation

| Example | Questions | Reference Valid? | Student Familiarity |
|---------|-----------|-----------------|-------------------|
| EX1 (RBC) | Q001, Q002, Q003 | ✅ Yes | Very High (3 uses) |
| EX2 (ATP) | Q006, Q007, Q012 | ✅ Yes | Very High (4 uses) |
| EX3 (Lab) | Q019 | ✅ Yes | High (hands-on) |

**Assessment:** All example references valid and appropriate ✅

---

## Tier Coverage Validation

| Tier | Target % | Actual Questions | Actual % | ✓ |
|------|----------|-----------------|----------|---|
| 1 | 70% | 14 | 70% | ✅ |
| 2 | 30% | 6 | 30% | ✅ |
| 3 | 0% | 0 | 0% | ✅ |
| 4 | 0% | 0 | 0% | ✅ |

**Alignment:** Perfect match with M1 emphasis patterns ✅

---

## Recommendations

### Immediate Actions
1. **Q012:** Reclassify as Apply/Medium (or rewrite)
2. **Q018:** Revise stem for specificity

### Optional Improvements
3. **Q003:** Consider replacing one distractor with more plausible option
4. **Q015:** Minor distractor improvement for realism

### Strengths to Maintain
- Continue using instructional examples (high validity)
- Continue using documented misconceptions (realistic distractors)
- Maintain tier-based emphasis distribution

---

## Final Approval Decision

**Status:** CONDITIONAL APPROVAL

**Approved for Use:** 18/20 questions ✅  
**Revision Required:** 2/20 questions ⚠️

**Timeline:**
- Revise Q012, Q018 (estimated 15 minutes)
- Re-review revised questions
- Final approval expected same day

**Overall Quality Assessment:** EXCELLENT

---

**Next Step:** Revise Q012 and Q018, then proceed to final export.
```

---

### 10. m4_detailed_feedback.md (DOCUMENTATION)

**Created:** M4 completion  
**Purpose:** Granular per-question feedback for learning and documentation  
**Dependencies:** questions.md  
**Used by:** Team learning, future revisions, research

**Format:**
```yaml
---
module: m4
output_type: detailed_feedback
created: 2026-01-17T17:50:00Z

questions_reviewed: 20
feedback_categories:
  - stem_quality
  - distractor_quality
  - bloom_accuracy
  - difficulty_appropriateness
  - pedagogical_grounding
  - example_usage
  - misconception_usage
---

# M4 Detailed Quality Feedback

**Review Date:** 2026-01-17  
**Questions:** 20  
**Purpose:** Granular feedback for continuous improvement

---

## Question-by-Question Analysis

### Q001: Cell Structure Basic

**Status:** ✅ APPROVED  
**Classification:** Remember, Easy, LO1.1, Tier 1

**Stem Quality:** ⭐⭐⭐⭐⭐ EXCELLENT
- Clear and unambiguous
- References familiar context (Lecture 1, EX1)
- Specific: "mogna röda blodkroppar"

**Current Stem:**
> "Som vi såg i Lecture 1, vilken struktur saknar mogna röda blodkroppar?"

**Distractor Quality:** ⭐⭐⭐⭐ GOOD
- A) Cellkärna (Nucleus) ✅ CORRECT
- B) Cellvägg (Cell wall) - Uses M2 misconception ✅
- C) Cellmembran - Plausible ✅
- D) Ribosomer - Plausible ✅

**Bloom Level:** ✅ ACCURATE (Remember)
- Tests recall of learned information
- No application or analysis required

**Difficulty:** ✅ APPROPRIATE (Easy)
- Straightforward recall
- Familiar example
- Clear correct answer

**Pedagogical Grounding:**
- Example Used: EX1 (RBC diagram) ✅
- Misconception Used: M2 (Cell walls) ✅
- Tier 1 concept ✅
- Students saw this 3 times in instruction ✅

**Overall Rating:** ⭐⭐⭐⭐⭐ EXEMPLARY

**Notes:** Perfect example of well-grounded question. Uses familiar instructional context, realistic distractor from documented misconception, tests critical Tier 1 concept.

---

### Q002: Mitochondria Basic

**Status:** ✅ APPROVED  
**Classification:** Remember, Easy, LO1.2, Tier 1

**Stem Quality:** ⭐⭐⭐⭐ GOOD
- Clear question
- References instruction
- Could be slightly more specific

**Current Stem:**
> "Vad är mitokondriernas huvudfunktion?"

**Distractor Quality:** ⭐⭐⭐⭐⭐ EXCELLENT
- A) Omvandla glukos till ATP ✅ CORRECT
- B) Skapa energi från ingenting - Uses M1 misconception ✅✅
- C) Syntetisera proteiner - Plausible ✅
- D) Lagra DNA - Plausible ✅

**Bloom Level:** ✅ ACCURATE (Remember)
- Basic recall question
- No deeper processing required

**Difficulty:** ✅ APPROPRIATE (Easy)
- Foundation concept
- High familiarity (Lecture 2 emphasis)

**Pedagogical Grounding:**
- Misconception Used: M1 (53% student error rate) ✅✅
- Tier 1 concept (highest emphasis) ✅
- Distractor is most common student error ✅

**Overall Rating:** ⭐⭐⭐⭐⭐ EXEMPLARY

**Notes:** Excellent use of high-frequency misconception (53% error rate). Distractor B is exactly what students incorrectly believe, making this a highly diagnostic question.

---

### Q006: ATP Production Process

**Status:** ✅ APPROVED  
**Classification:** Remember, Medium, LO1.2, Tier 1

**Stem Quality:** ⭐⭐⭐⭐⭐ EXCELLENT
- References specific instruction (EX2 animation)
- Clear and specific
- Appropriate complexity for Medium

**Current Stem:**
> "Baserat på ATP-produktionsanimationen från Lecture 2, vad är första steget i elektrontransporten?"

**Distractor Quality:** ⭐⭐⭐⭐ GOOD
- A) Elektroner från NADH → Komplex I ✅ CORRECT
- B) Protonpumpning → Reasonable partial knowledge
- C) ATP synthase aktivering → Temporal confusion
- D) Glukosupptag → Too early in process

**Bloom Level:** ✅ ACCURATE (Remember)
- Recall of specific process step
- Seen in animation 4 times

**Difficulty:** ✅ APPROPRIATE (Medium)
- More specific than basic recall
- Requires sequencing knowledge
- Students saw multiple times but still requires precision

**Pedagogical Grounding:**
- Example Used: EX2 (ATP animation, 4 viewings) ✅✅
- Very high student familiarity ✅
- Tests well-instructed content ✅

**Overall Rating:** ⭐⭐⭐⭐⭐ EXEMPLARY

**Notes:** Strong example usage. Animation was shown 4 times, student-requested. High construct validity.

---

### Q012: ATP Synthase Blockage

**Status:** ⚠️ NEEDS REVISION  
**Classification:** Understand, Medium (SHOULD BE: Apply, Medium)  
**Issue:** Bloom level mismatch

**Stem Quality:** ⭐⭐⭐⭐ GOOD
- Clear scenario
- Specific condition ("if blocked")
- References instruction

**Current Stem:**
> "Om ATP synthase blockeras, hur påverkas protongradient över mitokondriemembranet?"

**Distractor Quality:** ⭐⭐⭐⭐ GOOD
- A) Gradiente ökar ✅ CORRECT (protons accumulate)
- B) Gradient minskar - Logical but incorrect
- C) Ingen förändring - Misunderstanding
- D) Gradient försvinner - Overgeneralization

**Bloom Level:** ❌ INACCURATE
- **Current:** Understand
- **Should be:** Apply
- **Rationale:** Requires applying understanding to NEW scenario (blockage)

**Difficulty:** ✅ APPROPRIATE (Medium)
- Requires causal reasoning
- Not just recall

**Pedagogical Grounding:**
- Example Used: EX2 (ATP animation) ✅
- Tests conceptual understanding ✅
- Apply-level question ✅

**Overall Rating:** ⭐⭐⭐⭐ GOOD (after reclassification)

**Recommendation:**
- **Option A (PREFERRED):** Reclassify as Apply, Medium
- **Option B:** Rewrite as simpler Understand question: "Vad är ATP synthase funktion?"

**Impact:** Blueprint balance maintained (Understand 8→7, Apply 3→4)

**Decision:** Reclassify as Apply ✅

---

### Q018: DNA/RNA Comparison

**Status:** ⚠️ NEEDS REVISION  
**Classification:** Understand, Medium  
**Issue:** Stem too vague

**Stem Quality:** ⭐⭐ NEEDS IMPROVEMENT
- Too open-ended
- No specific comparison criteria
- Ambiguous for multiple choice format

**Current Stem:**
> "Jämför DNA och RNA"

**Problem Analysis:**
- "Jämför" without criteria = unclear expectation
- Multiple valid comparisons possible:
  - Structural differences?
  - Functional differences?
  - Location differences?
  - Chemical differences?
- Student doesn't know what answer format is expected

**Suggested Revision:**
> "Lista tre strukturella skillnader mellan DNA och RNA"

**Improvements in Revision:**
- ✅ Specific comparison type ("strukturella")
- ✅ Quantified ("tre")
- ✅ Clear answer format expectation

**Distractor Quality:** ⭐⭐⭐ ACCEPTABLE
- (Will improve with clearer stem)

**Bloom Level:** ✅ ACCURATE (Understand)
- Requires understanding relationships
- Appropriate for comparison

**Difficulty:** ⚠️ MIGHT NEED ADJUSTMENT
- **Current:** Medium
- **After revision:** Might be Easy (if structural differences are well-taught)
- Monitor after revision

**Pedagogical Grounding:**
- Tier 1 concept (LO1.3) ✅
- Critical gap filled ✅

**Overall Rating:** ⭐⭐⭐ ACCEPTABLE (after revision)

**Recommendation:** Revise stem for specificity

**Decision:** Revise stem, monitor difficulty ✅

---

### Q019: Lab Diffusion Application

**Status:** ✅ APPROVED  
**Classification:** Apply, Medium, LO2.1, Tier 2

**Stem Quality:** ⭐⭐⭐⭐⭐ EXCELLENT
- Clear scenario from instruction
- Specific variable manipulation
- Appropriate complexity

**Current Stem:**
> "I Lab 1 observerade ni färgdiffusion genom en membran. Om koncentrationsgradienten ökas, vad händer med diffusionshastigheten?"

**Distractor Quality:** ⭐⭐⭐⭐ GOOD
- A) Ökar proportionellt ✅ CORRECT
- B) Minskar - Incorrect causal reasoning
- C) Ingen förändring - Misunderstanding variable relationship
- D) Ökar exponentiellt - Overgeneralization

**Bloom Level:** ✅ ACCURATE (Apply)
- Requires applying lab observation to new variable
- Not just recalling lab results

**Difficulty:** ✅ APPROPRIATE (Medium)
- Familiar context (Lab 1)
- Variable manipulation requires thought
- Not overly complex

**Pedagogical Grounding:**
- Example Used: EX3 (Lab 1 hands-on) ✅✅
- Personal student experience ✅
- Data-driven (students have lab results) ✅
- High construct validity ✅

**Overall Rating:** ⭐⭐⭐⭐⭐ EXEMPLARY

**Notes:** Perfect Apply-level question. Uses hands-on lab experience, requires application to new variable, realistic distractors. High pedagogical value.

---

## Summary Statistics

### Approval Distribution

| Status | Count | % |
|--------|-------|---|
| Approved | 18 | 90% |
| Needs Revision | 2 | 10% |
| Rejected | 0 | 0% |

---

### Rating Distribution

| Rating | Count | Questions |
|--------|-------|-----------|
| ⭐⭐⭐⭐⭐ Exemplary | 5 | Q001, Q002, Q006, Q019, Q021 |
| ⭐⭐⭐⭐ Good | 13 | [List] |
| ⭐⭐⭐ Acceptable | 2 | Q012, Q018 (after revision) |
| ⭐⭐ Needs Improvement | 0 | - |
| ⭐ Reject | 0 | - |

---

### Quality Dimension Scores

| Dimension | Avg Score | Range | Notes |
|-----------|-----------|-------|-------|
| Stem Quality | 4.1/5 | 2-5 | 2 questions need clarity |
| Distractor Quality | 4.0/5 | 3-5 | Mostly excellent |
| Bloom Accuracy | 4.95/5 | 4-5 | 1 misclassification |
| Difficulty | 4.95/5 | 4-5 | 1 potential adjustment |
| Pedagogical Grounding | 4.6/5 | 4-5 | Strong overall |

---

## Lessons Learned

### What Worked Well
1. **Example Integration:** Questions referencing instructional examples (EX1, EX2, EX3) have highest ratings
2. **Misconception Usage:** High-frequency misconceptions (M1: 53%) create excellent distractors
3. **Hands-On Context:** Lab-based questions (Q019) have high student engagement
4. **Tier Alignment:** 70% Tier 1 focus ensures critical concept coverage

### Areas for Improvement
1. **Stem Specificity:** Avoid vague verbs like "jämför" without criteria
2. **Bloom Classification:** Double-check Apply vs. Understand boundary
3. **Distractor Plausibility:** A few distractors could be more realistic

### Recommendations for Future
1. Always specify comparison criteria in Understand questions
2. Use "Apply" tag when questions involve NEW scenarios (not just understanding existing)
3. Prioritize high-frequency misconceptions for distractor creation
4. Reference instructional examples whenever possible for context validity

---

**Overall Assessment:** EXCELLENT pedagogical quality with minor revisions needed.
```

---

## IMPLEMENTATION NEXT STEPS

This specification is complete for Code (Windsurf) implementation.

**Ready for handoff:**
1. ✅ All 10 file formats specified
2. ✅ YAML frontmatter structures defined
3. ✅ Markdown body templates provided
4. ✅ Tool requirements clear
5. ✅ Workflow dependencies mapped

**Implementation Tools Needed:**
- `save_methodology_doc` (handles all 10 file types)
- `update_questions` (for questions.md)
- `complete_stage` (logging)
- `get_module_status` (optional)

**Implementation Priority:**
- PHASE 1: Core mandatory files (7 files)
- PHASE 2: Documentation files (3 files)
- PHASE 3: Integration and testing

---

**Approval Status:** AWAITING NIKLAS APPROVAL before creating implementation handoff for Code.