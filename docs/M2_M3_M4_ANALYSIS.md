# M2-M4 METODOLOGIGRANSKNING - KOMPLETT ANALYS

**Datum:** 2026-01-15  
**Syfte:** Dokumentera stage-struktur för qf-scaffolding implementation  
**Status:** ✅ KOMPLETT

---

## SAMMANFATTNING

### Filstruktur bekräftad

| Modul | Filer | Stages/Phases | Typ | Tid | Status |
|-------|-------|---------------|-----|-----|--------|
| M1 | 8 (0-7) | 8 stages | Content Analysis | ~3h | ✅ IMPLEMENTERAD |
| M2 | 9 (0-8) | 7 stages | Assessment Design | ~2h | ⏳ ANALYSERAD |
| M3 | 5 (0-4) | 3 stages | Question Generation | ~5h | ⏳ ANALYSERAD |
| M4 | 6 (0-5) | 4 phases | Quality Assurance | ~2h | ⏳ ANALYSERAD |

**Total:** 28 filer över 4 moduler  
**Total workflow tid:** ~12 timmar (M1→M2→M3→M4)

---

## M2: ASSESSMENT DESIGN (BB2)

### Filstruktur (9 filer)

```
m2_0_intro.md                    → Introduction & Theoretical Foundations
m2_1_objective_validation.md     → Stage 1: Learning Objective Validation
m2_2_strategy_definition.md      → Stage 2: Assessment Strategy Definition
m2_3_question_target.md          → Stage 3: Question Target Determination
m2_4_blooms_distribution.md      → Stage 4: Bloom's Distribution Planning
m2_5_question_type_mix.md        → Stage 5: Question Type Mix Planning
m2_6_difficulty_distribution.md  → Stage 6: Difficulty Distribution Planning
m2_7_blueprint_construction.md   → Stage 7: Blueprint Construction
m2_8_best_practices.md           → Facilitation Best Practices
```

### Stage-struktur

**Index 0: Introduction (m2_0)**
- **Typ:** Framework overview
- **Innehåll:** Theoretical foundations (Constructive Alignment, Bloom's, Formative/Summative)
- **Estimerad tid:** 15-20 min läsning
- **requires_approval:** false (läsmaterial)
- **Dialog:** Ingen - läs och förstå

**Index 1: Objective Validation (m2_1)**
- **Typ:** Validation dialogue
- **Syfte:** Ensures objectives are observable, measurable, comprehensive
- **Estimerad tid:** 15-20 min
- **Output:** Validated learning objectives
- **requires_approval:** true
- **Stage gate:** STOP before Stage 2
- **Dialog:**
  - AI presents objectives from M1 organized by Bloom's level
  - Teacher reviews distribution
  - Validates or refines objectives
  - Explicit approval before proceeding

**Index 2: Strategy Definition (m2_2)**
- **Typ:** Strategic decision dialogue  
- **Syfte:** Establish assessment purpose (formative vs summative)
- **Estimerad tid:** 10-15 min
- **Output:** Assessment strategy document
- **requires_approval:** true
- **Stage gate:** STOP before Stage 3
- **Dialog:**
  - AI explains formative vs summative implications
  - Teacher chooses assessment purpose
  - Defines constraints (time, attempts, feedback)
  - Lock-in strategy

**Index 3: Question Target (m2_3)**
- **Typ:** Calculation + validation dialogue
- **Syfte:** Determine total number of questions
- **Estimerad tid:** 10-15 min
- **Output:** Question count target
- **requires_approval:** true
- **Stage gate:** STOP before Stage 4
- **Dialog:**
  - AI proposes coverage-based calculation
  - Validates against time constraints
  - Teacher approves or adjusts target
  - Final number locked

**Index 4: Bloom's Distribution (m2_4)**
- **Typ:** Distribution planning dialogue
- **Syfte:** Allocate questions across cognitive levels (Remember→Evaluate)
- **Estimerad tid:** 15-20 min
- **Output:** Bloom's distribution plan
- **requires_approval:** true
- **Stage gate:** STOP before Stage 5
- **Dialog:**
  - AI proposes distribution based on objectives
  - Teacher adjusts to match pedagogical priorities
  - Validates totals match question target
  - Lock-in distribution

**Index 5: Question Type Mix (m2_5)**
- **Typ:** Format selection dialogue
- **Syfte:** Select question format types (MC, Text, Fill-in, etc)
- **Estimerad tid:** 20-25 min
- **Output:** Question type distribution
- **requires_approval:** true
- **Stage gate:** STOP before Stage 6
- **Dialog:**
  - AI explains affordances/constraints of each type
  - Teacher selects appropriate formats
  - Distributes types across Bloom's levels
  - Validates grading feasibility

**Index 6: Difficulty Distribution (m2_6)**
- **Typ:** Difficulty planning dialogue
- **Syfte:** Distribute questions by difficulty (Easy/Medium/Hard)
- **Estimerad tid:** 15-20 min
- **Output:** Difficulty distribution plan
- **requires_approval:** true
- **Stage gate:** STOP before Stage 7
- **Dialog:**
  - AI proposes difficulty curves (formative vs summative)
  - Teacher adjusts to match student needs
  - Validates balance
  - Finalize distribution

**Index 7: Blueprint Construction (m2_7)**
- **Typ:** Synthesis + final approval
- **Syfte:** Synthesize all decisions into complete blueprint
- **Estimerad tid:** 20-30 min
- **Output:** **COMPLETE ASSESSMENT BLUEPRINT** (→ M3)
- **requires_approval:** true
- **Stage gate:** STOP before M3
- **Dialog:**
  - AI presents complete blueprint
  - Teacher validates all components
  - Comprehensive validation checks
  - **FINAL APPROVAL** for question generation

**Index 8: Best Practices (m2_8)**
- **Typ:** Facilitation guidance
- **Innehåll:** Cross-cutting tips, common pitfalls, dialogue best practices
- **Estimerad tid:** 15 min läsning
- **requires_approval:** false (reference material)

### Key Insights för M2

**Output Chain:**
```
M2 Stage 1 → Validated Objectives
M2 Stage 2 → Assessment Strategy (Formative/Summative)
M2 Stage 3 → Question Count Target
M2 Stage 4 → Bloom's Distribution Plan
M2 Stage 5 → Question Type Mix
M2 Stage 6 → Difficulty Distribution
M2 Stage 7 → COMPLETE BLUEPRINT (→ M3)
```

**Stage Gates:**
- ALLA stages 1-7 har explicit STOP commands
- ALLA stages 1-7 requires_approval: true
- Ingen automatisk progression mellan stages
- Varje stage = en dialog = ett beslut

**Total tid:** 1.5-2.5 timmar

---

## M3: QUESTION GENERATION (BB4)

### Filstruktur (5 filer)

```
m3_0_intro.md                → Introduction & Principles
m3_1_basic_generation.md     → Stage 4A: Basic Generation
m3_2_distribution_review.md  → Stage 4B: Distribution Review
m3_3_finalization.md         → Stage 4C: Finalization
m3_4_process_guidelines.md   → Process Guidelines
```

### Stage-struktur

**Index 0: Introduction (m3_0)**
- **Typ:** Framework overview
- **Innehåll:** Three-stage model, teacher authority principles, process schematic
- **Estimerad tid:** 15-20 min läsning
- **requires_approval:** false (läsmaterial)
- **Core principle:** TEACHER LEADS, AI SUPPORTS

**Index 1: Basic Generation (m3_1) - Stage 4A**
- **Typ:** Creative dialogue (explorative, iterative)
- **Syfte:** Generate questions through teacher-AI collaboration
- **Estimerad tid:** 2-3 timmar (iterative generation)
- **Output:** Pool of generated questions (raw, unrefined)
- **requires_approval:** true
- **Stage gate:** STOP before Stage 4B
- **Dialog:**
  - Teacher directs content focus
  - AI proposes question drafts
  - Teacher evaluates and refines
  - Iterative until sufficient pool created
  - Teacher approves pool for review

**Index 2: Distribution Review (m3_2) - Stage 4B**
- **Typ:** Analytical dialogue (systematic, decision-driven)
- **Syfte:** Analyze generated questions against blueprint from M2
- **Estimerad tid:** 1-1.5 timmar
- **Output:** Gap analysis + validated distribution
- **requires_approval:** true
- **Stage gate:** STOP before Stage 4C
- **Dialog:**
  - AI presents distribution analysis
  - Compares generated vs blueprint targets
  - Identifies gaps (coverage, Bloom's, difficulty)
  - Teacher makes strategic decisions
  - Generate additional questions if needed
  - Approve when distribution meets goals

**Index 3: Finalization (m3_3) - Stage 4C**
- **Typ:** Technical implementation dialogue (practical, solution-oriented)
- **Syfte:** Format, polish, and prepare questions for QA
- **Estimerad tid:** 1.5-2 timmar
- **Output:** **FINAL QUESTION SET** (ready for M4)
- **requires_approval:** true
- **Stage gate:** STOP before M4
- **Dialog:**
  - AI formats questions to technical specs
  - Teacher approves formatting choices
  - Creates feedback for each question
  - Final technical validation
  - **APPROVAL** for Quality Assurance

**Index 4: Process Guidelines (m3_4)**
- **Typ:** Reference material
- **Innehåll:** Detailed facilitation guidance, dialogue patterns, iteration strategies
- **Estimerad tid:** 20 min läsning
- **requires_approval:** false (reference)

### Key Insights för M3

**Three-Stage Model:**
```
4A: CREATE        → 4B: ANALYZE       → 4C: FINALIZE
(Content focus)     (Strategic review)   (Technical polish)
```

**Teacher Authority:**
- M3 emphasizes teacher-led process throughout
- AI proposes, teacher decides at every step
- Dialogic, not automated
- Teacher makes ALL pedagogical decisions

**Stage Gates:**
- Stages 1-3 alla har STOP commands
- Alla stages requires_approval: true
- Stage 1 → Stage 2: After sufficient generation pool
- Stage 2 → Stage 3: After gaps filled and distribution approved
- Stage 3 → M4: After final formatting approval

**Dialogue Character:**
- Stage 4A: Explorative, creative
- Stage 4B: Analytical, systematic
- Stage 4C: Practical, implementation-focused

**Total tid:** ~5 timmar (longest module!)

---

## M4: QUALITY ASSURANCE (BB5)

### Filstruktur (6 filer)

```
m4_0_intro.md                 → Introduction & Foundations
m4_1_automated_validation.md  → Phase 1: Automated Technical Validation
m4_2_pedagogical_review.md    → Phase 2: Pedagogical Quality Review
m4_3_collective_analysis.md   → Phase 3: Collective Assessment Analysis
m4_4_documentation.md          → Phase 4: Quality Documentation
m4_5_output_transition.md      → Output Artifacts & Transition to Pipeline
```

### Phase-struktur (NOTE: "Phases" not "Stages")

**Index 0: Introduction (m4_0)**
- **Typ:** Framework overview
- **Innehåll:** Quality dimensions, validation framework (Messick), Haladyna & Rodriguez
- **Estimerad tid:** 15-20 min läsning
- **requires_approval:** false (läsmaterial)
- **Classification:** HYBRID (automated + expert judgment)

**Index 1: Automated Validation (m4_1) - Phase 1**
- **Typ:** Automated analysis (minimal dialogue)
- **Syfte:** Run comprehensive technical compliance checks
- **Estimerad tid:** ~5 min (automated execution)
- **Output:** Technical validation report
- **requires_approval:** "conditional"
  - Auto-proceed if all checks pass
  - STOP if errors found → teacher fixes → re-validate
- **Process:**
  - AI runs validation automatically
  - Checks: Format, metadata, QTI compliance, structural correctness
  - Reports errors if found
  - Teacher fixes errors
  - Re-validate until clean
  - Proceed to Phase 2 when all checks pass

**Index 2: Pedagogical Review (m4_2) - Phase 2**
- **Typ:** Expert review dialogue
- **Syfte:** Instructor validates pedagogical quality
- **Estimerad tid:** 1-2 min per question (~40-80 min for 40 questions)
- **Output:** Pedagogical quality notes
- **requires_approval:** true
- **Stage gate:** STOP before Phase 3
- **Dialog:**
  - AI presents questions systematically
  - Teacher reviews each for:
    - Disciplinary accuracy
    - Appropriateness for students
    - Teaching value
    - Cognitive alignment
  - Notes issues for revision
  - Approve for collective analysis

**Index 3: Collective Analysis (m4_3) - Phase 3**
- **Typ:** Holistic assessment dialogue
- **Syfte:** Evaluate complete question set as coherent instrument
- **Estimerad tid:** 15-20 min
- **Output:** Exam-level validation report
- **requires_approval:** true
- **Stage gate:** STOP before Phase 4
- **Dialog:**
  - AI analyzes coverage, distribution, balance
  - Uses dashboard from M3 assembly
  - Identifies systemic issues
  - Teacher validates coherence
  - Checks for question dependencies
  - Approve assessment character

**Index 4: Documentation (m4_4) - Phase 4**
- **Typ:** Synthesis + reporting
- **Syfte:** Create quality assurance documentation
- **Estimerad tid:** 10-15 min
- **Output:** **QA REPORT + FINAL APPROVAL**
- **requires_approval:** true
- **Stage gate:** STOP before Pipeline export
- **Dialog:**
  - AI synthesizes all validation results
  - Produces comprehensive quality report
  - Teacher reviews evidence
  - Makes final approval determination
  - **FINAL GATE** before deployment

**Index 5: Output Transition (m4_5)**
- **Typ:** Handoff documentation
- **Innehåll:** Output artifacts, integration requirements, transition to Pipeline
- **Estimerad tid:** 10 min läsning
- **requires_approval:** false (reference)
- **Transition:** M4 → Pipeline (qf-pipeline step3_export)

### Key Insights för M4

**Quality Gates:**
- Phase 1: Conditional (automated with error handling)
- Phases 2-4: ALL require teacher approval
- Iterative: Issues found → revise → re-validate

**Hybrid Nature:**
- Automated: Technical validation (Phase 1)
- Manual: Pedagogical judgment (Phases 2-4)
- Best of both approaches

**Quality Dimensions:**
1. Technical (automated)
2. Pedagogical (expert judgment)
3. Collective (systematic analysis)
4. Documentary (synthesis)

**KRITISKT BESLUT: analyze_distractors verktyg?**

**ANALYS:**

Från m4_1 (Automated Validation):
- Fokus: Technical checks (format, metadata, QTI compliance)
- INGEN NÄMNING av distractor analysis tool
- Validation är structural, inte content-based

Från m4_2 (Pedagogical Review):
- Fokus: Expert judgment on quality
- Mentions "plausible alternative conceptions" (distractors)
- BUT: Teacher reviews MANUALLY, not via automated tool

**SLUTSATS: INGET analyze_distractors VERKTYG BEHÖVS** ❌

M4 använder:
- Automated technical validation (redan exists i qf-pipeline step2_validate)
- Manual expert review (teacher-led dialogue)
- Collective analysis (statistical distributions, inte distractor-specifikt)

**Total tid:** 1-2 timmar

---

## SAMMANFATTAD STAGE-KARTA FÖR IMPLEMENTATION

### M1 (Content Analysis) - 8 files
```typescript
const M1_STAGES: Record<number, StageInfo> = {
  0: { filename: "m1_0_intro.md", name: "Introduction", 
       requiresApproval: false, estimatedTime: "15 min" },
  1: { filename: "m1_1_stage0_material_analysis.md", name: "Stage 0: Material Analysis",
       requiresApproval: false, estimatedTime: "60-90 min" },
  2: { filename: "m1_2_stage1_validation.md", name: "Stage 1: Validation",
       requiresApproval: true, estimatedTime: "20-30 min" },
  3: { filename: "m1_3_stage2_emphasis.md", name: "Stage 2: Emphasis",
       requiresApproval: true, estimatedTime: "30-45 min" },
  4: { filename: "m1_4_stage3_examples.md", name: "Stage 3: Examples",
       requiresApproval: true, estimatedTime: "20-30 min" },
  5: { filename: "m1_5_stage4_misconceptions.md", name: "Stage 4: Misconceptions",
       requiresApproval: true, estimatedTime: "20-30 min" },
  6: { filename: "m1_6_stage5_objectives.md", name: "Stage 5: Objectives",
       requiresApproval: true, estimatedTime: "45-60 min" },
  7: { filename: "m1_7_best_practices.md", name: "Best Practices",
       requiresApproval: false, estimatedTime: "15 min" },
}
```

### M2 (Assessment Design) - 9 files
```typescript
const M2_STAGES: Record<number, StageInfo> = {
  0: { filename: "m2_0_intro.md", name: "Introduction",
       requiresApproval: false, estimatedTime: "15-20 min" },
  1: { filename: "m2_1_objective_validation.md", name: "Stage 1: Objective Validation",
       requiresApproval: true, estimatedTime: "15-20 min" },
  2: { filename: "m2_2_strategy_definition.md", name: "Stage 2: Strategy Definition",
       requiresApproval: true, estimatedTime: "10-15 min" },
  3: { filename: "m2_3_question_target.md", name: "Stage 3: Question Target",
       requiresApproval: true, estimatedTime: "10-15 min" },
  4: { filename: "m2_4_blooms_distribution.md", name: "Stage 4: Bloom's Distribution",
       requiresApproval: true, estimatedTime: "15-20 min" },
  5: { filename: "m2_5_question_type_mix.md", name: "Stage 5: Question Type Mix",
       requiresApproval: true, estimatedTime: "20-25 min" },
  6: { filename: "m2_6_difficulty_distribution.md", name: "Stage 6: Difficulty Distribution",
       requiresApproval: true, estimatedTime: "15-20 min" },
  7: { filename: "m2_7_blueprint_construction.md", name: "Stage 7: Blueprint Construction",
       requiresApproval: true, estimatedTime: "20-30 min" },
  8: { filename: "m2_8_best_practices.md", name: "Best Practices",
       requiresApproval: false, estimatedTime: "15 min" },
}
```

### M3 (Question Generation) - 5 files
```typescript
const M3_STAGES: Record<number, StageInfo> = {
  0: { filename: "m3_0_intro.md", name: "Introduction",
       requiresApproval: false, estimatedTime: "15-20 min" },
  1: { filename: "m3_1_basic_generation.md", name: "Stage 4A: Basic Generation",
       requiresApproval: true, estimatedTime: "2-3 hours" },
  2: { filename: "m3_2_distribution_review.md", name: "Stage 4B: Distribution Review",
       requiresApproval: true, estimatedTime: "1-1.5 hours" },
  3: { filename: "m3_3_finalization.md", name: "Stage 4C: Finalization",
       requiresApproval: true, estimatedTime: "1.5-2 hours" },
  4: { filename: "m3_4_process_guidelines.md", name: "Process Guidelines",
       requiresApproval: false, estimatedTime: "20 min" },
}
```

### M4 (Quality Assurance) - 6 files
```typescript
const M4_STAGES: Record<number, StageInfo> = {
  0: { filename: "m4_0_intro.md", name: "Introduction",
       requiresApproval: false, estimatedTime: "15-20 min" },
  1: { filename: "m4_1_automated_validation.md", name: "Phase 1: Automated Validation",
       requiresApproval: "conditional", estimatedTime: "~5 min" },
  2: { filename: "m4_2_pedagogical_review.md", name: "Phase 2: Pedagogical Review",
       requiresApproval: true, estimatedTime: "1-2 min per question" },
  3: { filename: "m4_3_collective_analysis.md", name: "Phase 3: Collective Analysis",
       requiresApproval: true, estimatedTime: "15-20 min" },
  4: { filename: "m4_4_documentation.md", name: "Phase 4: Documentation",
       requiresApproval: true, estimatedTime: "10-15 min" },
  5: { filename: "m4_5_output_transition.md", name: "Output Transition",
       requiresApproval: false, estimatedTime: "10 min" },
}
```

---

## PATTERN ANALYSIS

### Gemensamma mönster över alla moduler

1. **File 0 = Introduction** (alla moduler)
   - Theoretical foundations
   - Process overview
   - Entry points
   - requiresApproval: false (läsmaterial)

2. **File N eller N-1 = Reference material** (alla moduler)
   - M1: File 7 (Best Practices)
   - M2: File 8 (Best Practices)
   - M3: File 4 (Process Guidelines)
   - M4: File 5 (Output Transition)
   - requiresApproval: false (reference)

3. **Arbetsstadier = Dialogue + Approval**
   - M1: Stages 2-6 (5 dialogues med approval)
   - M2: Stages 1-7 (7 dialogues med approval)
   - M3: Stages 1-3 (3 dialogues med approval)
   - M4: Phases 2-4 (3 dialogues med approval, Phase 1 conditional)

4. **Stage Gates konsekvent**
   - Explicit STOP commands i alla stages
   - requires_approval checks
   - No auto-progression mellan stages
   - Varje dialog stage = ett beslut = en approval

### Timing patterns

| Modul | Intro | Dialogues | Reference | Total |
|-------|-------|-----------|-----------|-------|
| M1 | 15 min | 2.5-3.5h | 15 min | ~3h |
| M2 | 20 min | 1.5-2.5h | 15 min | ~2h |
| M3 | 20 min | 5h | 20 min | ~5h |
| M4 | 20 min | 1-2h | 10 min | ~2h |

**TOTAL M1→M2→M3→M4 WORKFLOW:** ~12 timmar

---

## IMPLEMENTATION GUIDE FÖR QF-SCAFFOLDING

### load_stage.ts Updates Needed

**1. Update module enum:**
```typescript
export const loadStageSchema = z.object({
  module: z.enum(["m1", "m2", "m3", "m4"]), // Uppdatera från bara ["m1"]
  stage: z.number().min(0).max(8), // Max 8 för M2
});
```

**2. Dynamic stage max validation:**
```typescript
const MAX_STAGES: Record<string, number> = {
  m1: 7,  // 0-7 (8 filer)
  m2: 8,  // 0-8 (9 filer)
  m3: 4,  // 0-4 (5 filer)
  m4: 5,  // 0-5 (6 filer)
};

// I loadStage function:
const maxStage = MAX_STAGES[module];
if (stage > maxStage) {
  return {
    success: false,
    error: `Invalid stage ${stage} for module ${module}. Valid stages: 0-${maxStage}`,
  };
}
```

**3. Add requiresApproval metadata:**
```typescript
interface StageInfo {
  filename: string;
  name: string;
  description: string;
  estimatedTime: string;
  requiresApproval: boolean | "conditional";  // NEW field
}
```

**4. Create M2, M3, M4 stage mappings:**
```typescript
const M2_STAGES: Record<number, StageInfo> = {
  0: {
    filename: "m2_0_intro.md",
    name: "Introduction",
    description: "Theoretical foundations for assessment design",
    estimatedTime: "15-20 min",
    requiresApproval: false,
  },
  1: {
    filename: "m2_1_objective_validation.md",
    name: "Stage 1: Objective Validation",
    description: "Validates learning objectives for assessment",
    estimatedTime: "15-20 min",
    requiresApproval: true,
  },
  // ... stages 2-7 ...
  8: {
    filename: "m2_8_best_practices.md",
    name: "Best Practices",
    description: "Facilitation guidance and common pitfalls",
    estimatedTime: "15 min",
    requiresApproval: false,
  },
};

const M3_STAGES: Record<number, StageInfo> = {
  0: {
    filename: "m3_0_intro.md",
    name: "Introduction",
    description: "Teacher-led three-stage generation process",
    estimatedTime: "15-20 min",
    requiresApproval: false,
  },
  1: {
    filename: "m3_1_basic_generation.md",
    name: "Stage 4A: Basic Generation",
    description: "Creative content generation through dialogue",
    estimatedTime: "2-3 hours",
    requiresApproval: true,
  },
  // ... stages 2-3 ...
};

const M4_STAGES: Record<number, StageInfo> = {
  0: {
    filename: "m4_0_intro.md",
    name: "Introduction",
    description: "Quality assurance framework and validation dimensions",
    estimatedTime: "15-20 min",
    requiresApproval: false,
  },
  1: {
    filename: "m4_1_automated_validation.md",
    name: "Phase 1: Automated Validation",
    description: "Technical compliance checks (automated)",
    estimatedTime: "~5 min",
    requiresApproval: "conditional", // Special case!
  },
  // ... phases 2-4 ...
};
```

**5. Dynamic stage lookup function:**
```typescript
function getStages(module: string): Record<number, StageInfo> {
  switch(module) {
    case "m1": return M1_STAGES;
    case "m2": return M2_STAGES;
    case "m3": return M3_STAGES;
    case "m4": return M4_STAGES;
    default: throw new Error(`Unknown module: ${module}`);
  }
}

// Update loadStage to use dynamic lookup:
const stages = getStages(module);
const stageInfo = stages[stage];
```

**6. Enhanced response with approval info:**
```typescript
return {
  success: true,
  content,
  stage: {
    module,
    index: stage,
    name: stageInfo.name,
    description: stageInfo.description,
    estimatedTime: stageInfo.estimatedTime,
    requiresApproval: stageInfo.requiresApproval, // NEW
  },
  // ... rest of response ...
};
```

### Estimated Implementation Time

- Define M2_STAGES mapping: 30 min
- Define M3_STAGES mapping: 20 min
- Define M4_STAGES mapping: 25 min
- Update validation logic: 30 min
- Update response format: 15 min
- Testing all modules: 1 hour
- **Total: ~3 timmar**

---

## VERKTYGS-BESLUT

### analyze_distractors BEHÖVS INTE ❌

**Motivering från granskning:**

1. **M4 Phase 1 (Automated Validation):**
   - Fokus: Technical checks (format, metadata, QTI)
   - Strukturell validation, INTE content analysis
   - Ingen mention av distractor quality analysis

2. **M4 Phase 2 (Pedagogical Review):**
   - Fokus: Expert teacher judgment
   - Mentions "plausible alternative conceptions"
   - BUT: Manual review, inte automated tool
   - Teacher reviews VARJE fråga individuellt

3. **M4 Phase 3 (Collective Analysis):**
   - Fokus: Statistical distributions
   - Coverage validation
   - INTE distractor-specific analysis

**Konsekvens för implementation:**
- Ingen ny tool creation behövs för M4
- M4 Phase 1 använder befintlig qf-pipeline step2_validate
- M4 Phases 2-4 är dialogue-driven, inte tool-driven
- Focus on pedagogical dialogue, not automation

---

## ÖVERGÅNGAR MELLAN MODULER

### M1 → M2 Transition

**Output från M1:**
- Validated learning objectives (från Stage 5)
- Content tier assignments
- Bloom's level classifications
- Example catalog
- Misconception registry

**Input till M2:**
- Learning objectives (required)
- Tier structure (helpful)
- Bloom's classifications (required)

**Transition point:**
- M1 Stage 6 (Objectives) completion
- User says "fortsätt till M2" eller "börja assessment design"
- qf-scaffolding loads m2 module

### M2 → M3 Transition

**Output från M2:**
- Complete assessment blueprint
- Question count target
- Bloom's distribution plan
- Question type mix
- Difficulty distribution
- All strategic decisions locked

**Input till M3:**
- Assessment blueprint (required)
- All M2 specifications guide generation

**Transition point:**
- M2 Stage 7 (Blueprint Construction) approval
- User says "börja generera frågor"
- qf-scaffolding loads m3 module

### M3 → M4 Transition

**Output från M3:**
- Final question set
- All questions formatted
- Metadata complete
- Ready for validation

**Input till M4:**
- Generated questions (required)
- Assessment blueprint from M2 (validation reference)

**Transition point:**
- M3 Stage 3 (Finalization) approval
- User says "kör quality assurance"
- qf-scaffolding loads m4 module

### M4 → Pipeline Transition

**Output från M4:**
- QA-approved questions
- Quality assurance report
- Final approval documentation

**Input till Pipeline:**
- Validated question set (ready for export)

**Transition point:**
- M4 Phase 4 (Documentation) final approval
- User says "exportera till Inspera"
- qf-pipeline step3_export runs

---

## SLUTSATS

### ✅ GRANSKNING KOMPLETT

**Dokumenterat:**
- Stage-struktur för M2/M3/M4 (detaljerad)
- requires_approval patterns (tydliga)
- Output chains mellan moduler
- Timing estimates per stage
- Tool requirements (inga nya behövs)
- Övergångar mellan moduler

**Redo för implementation:**
- TypeScript stage mappings klara
- Validation logic defined
- Testing strategy clear
- Inga blockerare

**Ingen ytterligare granskning behövs:**
- Metodologifilerna är kompletta och konsistenta
- Strukturen är tydlig och logisk
- Stage gates väl definierade
- Inga nya verktyg krävs

### Nästa steg

**ALTERNATIV A: Implementera M2-M4 i qf-scaffolding NU**
- Skapa IMPLEMENT_handoff dokument
- Claude Code implementerar (~3 timmar)
- Testa varje modul
- Testa övergångar M1→M2→M3→M4

**ALTERNATIV B: Något annat**
- Återgå till MQG Building Blocks arbete?
- Fokusera på praktiskt QuestionForge-användning?
- Dokumentera user testing av M1?

---

*Granskning genomförd: 2026-01-15*  
*Gransk

ningstid: ~2 timmar*  
*Filer granskade: 28 filer (M1-M4)*  
*Status: KOMPLETT ✅*  
*Nästa: Implementation eller annat fokus*
