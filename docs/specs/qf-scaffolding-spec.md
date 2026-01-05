# QF-SCAFFOLDING-MCP Specification

**Version:** 1.0  
**Status:** Draft  
**MCP Name:** qf-scaffolding  
**Language:** TypeScript (Node.js)  
**Related ADRs:** ADR-001, ADR-002, ADR-003, ADR-004

---

## Overview

qf-scaffolding is a methodology guidance MCP that helps teachers create assessment questions through a structured, pedagogical process. It implements Modules M1-M4, providing flexible navigation with teacher control at every stage.

**Pattern:** NON-LINEAR, flexible entry points  
**Output:** Markdown questions ready for qf-pipeline

---

## Modules

### M1: Content Analysis
**Purpose:** Analyze what was actually taught  
**Entry requirements:** Instructional materials (lectures, slides, transcripts)  
**Output:** Learning objectives, examples catalog, misconceptions registry

| Stage | Name | Description |
|-------|------|-------------|
| 0 | Material Analysis | AI reads all materials, identifies emphasis patterns |
| 1 | Initial Validation | Teacher validates AI analysis |
| 2 | Emphasis Refinement | Deep dive into content priorities |
| 3 | Example Catalog | Document effective instructional examples |
| 4 | Misconception Analysis | Identify common student errors |
| 5 | Scope & Objectives | Finalize learning objectives |

### M2: Assessment Planning
**Purpose:** Design the assessment structure  
**Entry requirements:** Learning objectives (from M1 or existing)  
**Output:** Blueprint with question distribution, metadata schema, labels

| Stage | Name | Description |
|-------|------|-------------|
| 1 | Metadata Schema Definition | What to track (topic, difficulty, bloom) |
| 2 | Label Taxonomy Design | Hierarchical label system |
| 3 | Question Type Selection | Which types, with technical requirements shown |
| 4 | Distribution Planning | How many of each type, cognitive level spread |
| 5 | Platform Requirements | Inspera-specific needs (optional) |

### M3: Question Generation
**Purpose:** Create the questions  
**Entry requirements:** Blueprint (from M2 or existing)  
**Output:** Draft questions in markdown format

| Stage | Name | Description |
|-------|------|-------------|
| 1 | Template Selection | Choose question templates per type |
| 2 | Draft Generation | AI generates initial drafts |
| 3 | Teacher Review | Teacher reviews and refines |
| 4 | Iteration | Refine based on feedback |

### M4: Quality Assurance
**Purpose:** Validate questions pedagogically  
**Entry requirements:** Questions (from M3 or existing)  
**Output:** Reviewed, validated questions

| Stage | Name | Description |
|-------|------|-------------|
| 1 | Distractor Analysis | Check MC distractors for quality |
| 2 | Cognitive Level Verification | Verify Bloom's levels are correct |
| 3 | Language Review | Check clarity, terminology consistency |
| 4 | Alignment Check | Verify questions align with objectives |

---

## Tools

### Navigation Tools

```typescript
interface GetModuleInstructionsParams {
  module: 1 | 2 | 3 | 4;      // M1-M4
  stage?: number;              // Optional specific stage
}

interface GetModuleInstructionsResult {
  module_name: string;
  stages: Stage[];
  current_stage?: Stage;
  instructions: string;        // Methodology guidance for Claude
  teacher_guide: string;       // What teacher should expect
}
```

```typescript
interface SuggestNextStepParams {
  current_module: number;
  current_stage: number;
  completed_outputs: string[]; // What's been produced
}

interface SuggestNextStepResult {
  suggested_module: number;
  suggested_stage: number;
  rationale: string;
  alternatives: Alternative[];
}
```

### Stage Management Tools

```typescript
interface GetStageGateChecklistParams {
  module: number;
  stage: number;
}

interface GetStageGateChecklistResult {
  checklist: ChecklistItem[];
  required_outputs: string[];
  teacher_approval_needed: boolean;
}
```

```typescript
interface ValidateStageOutputParams {
  module: number;
  stage: number;
  output_content: string;
}

interface ValidateStageOutputResult {
  valid: boolean;
  missing_elements: string[];
  warnings: string[];
}
```

### Flexible Navigation Tools

```typescript
interface ListAvailableModulesResult {
  modules: ModuleInfo[];
  // Each module shows: name, entry_requirements, can_start_now
}
```

```typescript
interface CanStartModuleParams {
  module: number;
  available_inputs: string[]; // What the teacher has
}

interface CanStartModuleResult {
  can_start: boolean;
  missing_prerequisites: string[];
  suggestions: string[];
}
```

### Analysis Tools (for M4 and MCP 2 integration)

```typescript
interface AnalyzeDistractorsParams {
  question_content: string;
  question_type: 'multiple_choice_single' | 'multiple_response';
}

interface AnalyzeDistractorsResult {
  quality_score: number;       // 0-100
  issues: DistractorIssue[];
  suggestions: string[];
}
```

```typescript
interface CheckLanguageConsistencyParams {
  questions: string[];         // Array of question contents
}

interface CheckLanguageConsistencyResult {
  consistent: boolean;
  terminology_variations: TermVariation[];
  suggestions: string[];
}
```

---

## File Structure

```
packages/qf-scaffolding/
├── src/
│   ├── index.ts               # MCP server entry
│   ├── tools/
│   │   ├── navigation.ts      # get_module_instructions, suggest_next_step
│   │   ├── stage-management.ts # get_stage_gate_checklist, validate_stage_output
│   │   ├── flexible-nav.ts    # list_available_modules, can_start_module
│   │   └── analysis.ts        # analyze_distractors, check_language_consistency
│   ├── modules/
│   │   ├── m1-content-analysis/
│   │   │   ├── stages.ts
│   │   │   └── instructions.md
│   │   ├── m2-assessment-planning/
│   │   │   ├── stages.ts
│   │   │   └── instructions.md
│   │   ├── m3-question-generation/
│   │   │   ├── stages.ts
│   │   │   └── instructions.md
│   │   └── m4-quality-assurance/
│   │       ├── stages.ts
│   │       └── instructions.md
│   └── utils/
│       └── checklist.ts
├── package.json
├── tsconfig.json
└── README.md
```

---

## Tool Summary

| Tool | Purpose | Used By |
|------|---------|---------|
| `get_module_instructions` | Get methodology guidance | Claude Desktop |
| `suggest_next_step` | Recommend next action | Claude Desktop |
| `get_stage_gate_checklist` | Get approval checklist | Claude Desktop |
| `validate_stage_output` | Check stage completion | Claude Desktop |
| `list_available_modules` | Show all modules | Claude Desktop |
| `can_start_module` | Check prerequisites | Claude Desktop |
| `analyze_distractors` | QA for MC questions | M4, MCP 2 Step 1.5 |
| `check_language_consistency` | QA for terminology | M4, MCP 2 Step 1.5 |

---

## Integration with qf-pipeline (MCP 2)

qf-pipeline can call qf-scaffolding tools in **Step 1.5 (Summary Analysis)**:

- `analyze_distractors` - Called for MC question quality check
- `check_language_consistency` - Called for terminology review

This integration is FUTURE development. Steps 1-4 of qf-pipeline work without it.

---

## Output Format

qf-scaffolding outputs questions in markdown format compatible with qf-specifications:

```markdown
# Q001 Question Title
@question: Q001
@type: multiple_choice_single
@identifier: COURSE_TOPIC_Q001
@points: 1
@tags: #Course #Topic #Bloom #Difficulty

---

## Question Text
@field: question_text
Question content here?

## Options
@field: options
A. First choice
B. Second choice
C. Third choice
D. Fourth choice

## Answer
@field: answer
B

## Feedback
@field: feedback
[... feedback structure per type ...]
```

---

## Dependencies

- `@modelcontextprotocol/sdk` - MCP TypeScript SDK
- `qf-specifications/` - Shared question type specs

---

## Configuration

```json
{
  "name": "qf-scaffolding",
  "version": "1.0.0",
  "description": "QuestionForge methodology scaffolding MCP",
  "mcp": {
    "tools": [
      "get_module_instructions",
      "suggest_next_step",
      "get_stage_gate_checklist",
      "validate_stage_output",
      "list_available_modules",
      "can_start_module",
      "analyze_distractors",
      "check_language_consistency"
    ]
  }
}
```

---

*Specification v1.0 | QuestionForge | 2026-01-02*
