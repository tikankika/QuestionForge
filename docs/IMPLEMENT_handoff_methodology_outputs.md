# IMPLEMENTATION HANDOFF: Methodology Outputs (3-Tool Design)

**Date:** 2026-01-17  
**Target:** Code (Windsurf)  
**Context:** M1-M4 methodology outputs via complete_stage integration  
**Related Spec:** SPEC_M1_M4_OUTPUTS_FULL.md

---

## CRITICAL: Design Change from Spec

**SPEC_M1_M4_OUTPUTS_FULL.md shows OLD design (4 tools):**
- ❌ save_methodology_doc (separate tool)
- ✅ complete_stage (logging only)

**ACTUAL implementation (3 tools):**
- ✅ load_stage (unchanged)
- ✅ complete_stage (EXTENDED - handles output creation)
- ✅ update_questions (new)

**Why the change:**
- 1:1 mapping: Each output tied to specific stage
- Atomic operation: Stage completion + output creation together
- Simpler API: Claude calls one tool instead of two
- Prevents forgetting: Can't complete stage without creating required output

---

## Architecture Overview

### Tool Responsibilities

**load_stage:**
- Loads methodology markdown
- **NEW:** Returns output schema guidance for Claude
- Example:
```typescript
{
  content: "# Stage 5: Learning Objectives\n...",
  metadata: { module: "m1", stage: 5 },
  output_expected: {
    type: "learning_objectives",
    required_fields: {
      course: "string",
      tier1: "array of {id, text, bloom, rationale}",
      tier2: "array of {id, text, bloom, rationale}",
      tier3: "array of {id, text, bloom, rationale}",
      tier4_excluded: "array of strings"
    }
  }
}
```

**complete_stage (EXTENDED):**
- Validates output data against schema
- Generates YAML frontmatter
- Generates Markdown body
- Writes file to 01_methodology/
- Updates session.yaml
- Logs stage_complete event
- Returns filepath

**update_questions:**
- Modifies 02_working/questions.md
- Actions: add, update, annotate
- Used by M1 (read), M2 (analyze), M3 (add), M4 (annotate)

---

## File Organization

```
packages/qf-scaffolding/src/
├── tools/
│   ├── load_stage.ts           ← Update: add output_expected to response
│   ├── complete_stage.ts        ← EXTEND: add output handling
│   └── update_questions.ts      ← NEW
│
├── outputs/                     ← NEW DIRECTORY
│   ├── index.ts                 ← Export all schemas/templates
│   ├── learning_objectives.ts   ← M1 Stage 5
│   ├── emphasis_patterns.ts     ← M1 Stage 2
│   ├── misconceptions.ts        ← M1 Stage 4
│   ├── examples.ts              ← M1 Stage 3
│   ├── material_analysis.ts     ← M1 Stage 0
│   ├── blueprint.ts             ← M2
│   ├── gap_analysis.ts          ← M2 (conditional)
│   ├── generation_log.ts        ← M3
│   ├── qa_report.ts             ← M4
│   └── detailed_feedback.ts     ← M4
│
└── schemas/                     ← Shared types
    └── methodology.ts
```

---

## Implementation: Phase 1 (Start Here)

### Step 1: Create Output Module Structure

**Create:** `packages/qf-scaffolding/src/outputs/learning_objectives.ts`

```typescript
import { z } from 'zod';

// Schema (from SPEC_M1_M4_OUTPUTS_FULL.md)
export const LearningObjectivesSchema = z.object({
  course: z.string(),
  instructor: z.string().optional(),
  tier1: z.array(z.object({
    id: z.string(),
    text: z.string(),
    bloom: z.string(),
    rationale: z.string()
  })),
  tier2: z.array(z.object({
    id: z.string(),
    text: z.string(),
    bloom: z.string(),
    rationale: z.string()
  })),
  tier3: z.array(z.object({
    id: z.string(),
    text: z.string(),
    bloom: z.string(),
    rationale: z.string()
  })),
  tier4_excluded: z.array(z.string())
});

export type LearningObjectivesData = z.infer<typeof LearningObjectivesSchema>;

// YAML Frontmatter Generator
export function generateFrontmatter(data: LearningObjectivesData, metadata: {
  module: string;
  stage: number;
  sessionId: string;
}): string {
  const yaml = {
    module: metadata.module,
    stage: metadata.stage,
    output_type: 'learning_objectives',
    created: new Date().toISOString(),
    session_id: metadata.sessionId,
    course: data.course,
    instructor: data.instructor,
    learning_objectives: {
      tier1: data.tier1,
      tier2: data.tier2,
      tier3: data.tier3,
      tier4_excluded: data.tier4_excluded
    }
  };
  
  // Use js-yaml library
  const YAML = require('js-yaml');
  return YAML.dump(yaml);
}

// Markdown Template Generator
export function generateMarkdown(data: LearningObjectivesData): string {
  return `
# M1 Learning Objectives

**Course:** ${data.course}  
**Instructor:** ${data.instructor || 'N/A'}  
**Date:** ${new Date().toISOString().split('T')[0]}

## Tier 1: Core Concepts (Must Assess)

These concepts received the highest emphasis and are critical for assessment.

${data.tier1.map(lo => `
- **${lo.id}** (${lo.bloom}): ${lo.text}
  - *Rationale:* ${lo.rationale}
`).join('\n')}

## Tier 2: Important (Should Assess)

${data.tier2.map(lo => `
- **${lo.id}** (${lo.bloom}): ${lo.text}
  - *Rationale:* ${lo.rationale}
`).join('\n')}

## Tier 3: Useful Background (Could Assess)

${data.tier3.map(lo => `
- **${lo.id}** (${lo.bloom}): ${lo.text}
  - *Rationale:* ${lo.rationale}
`).join('\n')}

## Tier 4: Excluded from Assessment

${data.tier4_excluded.map(item => `- ${item}`).join('\n')}

---

**Next Step:** Use these learning objectives in M2 Assessment Design to create blueprint.
`.trim();
}

// Export for complete_stage
export const learningObjectivesOutput = {
  type: 'learning_objectives',
  schema: LearningObjectivesSchema,
  generateFrontmatter,
  generateMarkdown,
  filename: (module: string) => `${module}_learning_objectives.md`
};
```

---

### Step 2: Create misconceptions.ts (Second Implementation)

**Create:** `packages/qf-scaffolding/src/outputs/misconceptions.ts`

```typescript
import { z } from 'zod';

export const MisconceptionsSchema = z.object({
  misconceptions: z.array(z.object({
    id: z.string(),
    topic: z.string(),
    misconception: z.string(),
    correct: z.string(),
    evidence: z.array(z.object({
      source: z.string(),
      frequency: z.string()
    })),
    severity: z.enum(['high', 'medium', 'low']),
    rationale: z.string(),
    teaching_strategy: z.string(),
    distractor_example: z.string()
  }))
});

export type MisconceptionsData = z.infer<typeof MisconceptionsSchema>;

export function generateFrontmatter(data: MisconceptionsData, metadata: {
  module: string;
  stage: number;
  sessionId: string;
}): string {
  const YAML = require('js-yaml');
  return YAML.dump({
    module: metadata.module,
    stage: metadata.stage,
    output_type: 'misconceptions',
    created: new Date().toISOString(),
    session_id: metadata.sessionId,
    misconceptions: data.misconceptions
  });
}

export function generateMarkdown(data: MisconceptionsData): string {
  const high = data.misconceptions.filter(m => m.severity === 'high');
  const medium = data.misconceptions.filter(m => m.severity === 'medium');
  const low = data.misconceptions.filter(m => m.severity === 'low');
  
  return `
# M1 Common Student Misconceptions

**Analysis Date:** ${new Date().toISOString().split('T')[0]}

---

## HIGH SEVERITY Misconceptions

${high.map(m => `
### ${m.id}: "${m.misconception}"

**Misconception:** ${m.misconception}  
**Correct Understanding:** ${m.correct}

**Evidence:**
${m.evidence.map(e => `- ${e.source}: **${e.frequency}**`).join('\n')}

**Severity:** HIGH  
**Rationale:** ${m.rationale}

**Teaching Strategy Used:**
${m.teaching_strategy}

**Distractor Potential:** ⭐⭐⭐⭐⭐  
**Example Distractor:** "${m.distractor_example}"
`).join('\n---\n')}

## MEDIUM SEVERITY Misconceptions

${medium.map(m => `
### ${m.id}: "${m.misconception}"

**Correct Understanding:** ${m.correct}

**Evidence:**
${m.evidence.map(e => `- ${e.source}: **${e.frequency}**`).join('\n')}

**Severity:** MEDIUM  
**Distractor Potential:** ⭐⭐⭐⭐
`).join('\n---\n')}

## LOW SEVERITY Misconceptions

${low.map(m => `
### ${m.id}: "${m.misconception}"

**Correct Understanding:** ${m.correct}

**Severity:** LOW  
**Distractor Potential:** ⭐⭐⭐
`).join('\n---\n')}

---

**Next Step:** M3 uses these documented misconceptions to create realistic, pedagogically-grounded distractors.
`.trim();
}

export const misconceptionsOutput = {
  type: 'misconceptions',
  schema: MisconceptionsSchema,
  generateFrontmatter,
  generateMarkdown,
  filename: (module: string) => `${module}_misconceptions.md`
};
```

---

### Step 3: Create Outputs Index

**Create:** `packages/qf-scaffolding/src/outputs/index.ts`

```typescript
import { learningObjectivesOutput } from './learning_objectives';
import { misconceptionsOutput } from './misconceptions';
// Import others as implemented...

export const OUTPUT_HANDLERS = {
  learning_objectives: learningObjectivesOutput,
  misconceptions: misconceptionsOutput,
  // Add others here...
} as const;

export type OutputType = keyof typeof OUTPUT_HANDLERS;

export function getOutputHandler(type: OutputType) {
  return OUTPUT_HANDLERS[type];
}
```

---

### Step 4: Extend complete_stage

**Update:** `packages/qf-scaffolding/src/tools/complete_stage.ts`

```typescript
import { getOutputHandler, OutputType } from '../outputs';
import { SessionManager } from '../session/manager';
import * as fs from 'fs/promises';
import * as path from 'path';

interface CompleteStageParams {
  project_path: string;
  module: 'm1' | 'm2' | 'm3' | 'm4';
  stage: number;
  output?: {
    type: OutputType;
    data: any;  // Will be validated by schema
  };
  overwrite?: boolean;
}

export async function complete_stage(params: CompleteStageParams) {
  const session = new SessionManager(params.project_path);
  await session.load();
  
  // Existing: Validate stage can be completed
  const currentStage = session.getCurrentStage(params.module);
  if (currentStage !== params.stage && !params.overwrite) {
    throw new Error(`Cannot complete stage ${params.stage}, current stage is ${currentStage}`);
  }
  
  let outputFilepath: string | undefined;
  
  // NEW: Handle output if provided
  if (params.output) {
    const handler = getOutputHandler(params.output.type);
    
    // 1. Validate data against schema
    const validatedData = handler.schema.parse(params.output.data);
    
    // 2. Generate YAML frontmatter
    const frontmatter = handler.generateFrontmatter(validatedData, {
      module: params.module,
      stage: params.stage,
      sessionId: session.getSessionId()
    });
    
    // 3. Generate Markdown body
    const markdown = handler.generateMarkdown(validatedData);
    
    // 4. Combine
    const content = `---\n${frontmatter}---\n\n${markdown}`;
    
    // 5. Write file
    const filename = handler.filename(params.module);
    const methodologyDir = path.join(params.project_path, '01_methodology');
    await fs.mkdir(methodologyDir, { recursive: true });
    
    outputFilepath = path.join(methodologyDir, filename);
    await fs.writeFile(outputFilepath, content, 'utf-8');
    
    // 6. Update session.yaml
    session.addOutput(params.module, params.output.type, outputFilepath);
  }
  
  // Existing: Mark stage complete
  session.completeStage(params.module, params.stage);
  
  // Existing: Log stage_complete event
  session.logEvent({
    type: 'stage_complete',
    module: params.module,
    stage: params.stage,
    timestamp: new Date().toISOString(),
    output_created: !!outputFilepath
  });
  
  await session.save();
  
  return {
    stage_completed: true,
    output_filepath: outputFilepath
  };
}
```

---

### Step 5: Update load_stage to Guide Claude

**Update:** `packages/qf-scaffolding/src/tools/load_stage.ts`

```typescript
import { getOutputHandler } from '../outputs';

// Add after loading stage content
function getOutputGuidance(module: string, stage: number) {
  // Map stage to expected output type
  const stageOutputMap: Record<string, Record<number, string>> = {
    m1: {
      0: 'material_analysis',
      2: 'emphasis_patterns',
      3: 'examples',
      4: 'misconceptions',
      5: 'learning_objectives'
    },
    // m2, m3, m4...
  };
  
  const outputType = stageOutputMap[module]?.[stage];
  if (!outputType) return null;
  
  const handler = getOutputHandler(outputType as any);
  
  // Generate human-readable schema description
  const schema = handler.schema;
  const shape = schema._def.shape(); // Zod internals
  
  return {
    type: outputType,
    required_fields: describeSchema(shape) // Helper function
  };
}

// Update return value
return {
  content: stageContent,
  metadata: { module, stage },
  output_expected: getOutputGuidance(module, stage) // NEW
};
```

---

## Testing Strategy

### Unit Tests

**Create:** `packages/qf-scaffolding/src/outputs/__tests__/learning_objectives.test.ts`

```typescript
import { learningObjectivesOutput } from '../learning_objectives';

describe('Learning Objectives Output', () => {
  const testData = {
    course: "Celler och Virus",
    instructor: "Niklas Karlsson",
    tier1: [
      {
        id: "LO1.1",
        text: "Describe cell structure",
        bloom: "Remember",
        rationale: "Foundation concept"
      }
    ],
    tier2: [],
    tier3: [],
    tier4_excluded: ["Advanced genetics"]
  };
  
  test('validates correct data', () => {
    expect(() => {
      learningObjectivesOutput.schema.parse(testData);
    }).not.toThrow();
  });
  
  test('rejects invalid data', () => {
    const invalid = { ...testData, tier1: "not an array" };
    expect(() => {
      learningObjectivesOutput.schema.parse(invalid);
    }).toThrow();
  });
  
  test('generates valid YAML', () => {
    const yaml = learningObjectivesOutput.generateFrontmatter(testData, {
      module: 'm1',
      stage: 5,
      sessionId: 'test-123'
    });
    
    expect(yaml).toContain('module: m1');
    expect(yaml).toContain('stage: 5');
    expect(yaml).toContain('output_type: learning_objectives');
  });
  
  test('generates valid Markdown', () => {
    const md = learningObjectivesOutput.generateMarkdown(testData);
    
    expect(md).toContain('# M1 Learning Objectives');
    expect(md).toContain('**LO1.1**');
    expect(md).toContain('Describe cell structure');
  });
});
```

### Integration Tests

**Create:** `packages/qf-scaffolding/src/tools/__tests__/complete_stage.integration.test.ts`

```typescript
import { complete_stage } from '../complete_stage';
import * as fs from 'fs/promises';
import * as path from 'path';

describe('complete_stage integration', () => {
  const testProjectPath = '/tmp/test-qf-project';
  
  beforeEach(async () => {
    // Create test project structure
    await fs.mkdir(testProjectPath, { recursive: true });
    // Initialize session.yaml...
  });
  
  afterEach(async () => {
    // Cleanup
    await fs.rm(testProjectPath, { recursive: true, force: true });
  });
  
  test('creates learning_objectives file', async () => {
    const result = await complete_stage({
      project_path: testProjectPath,
      module: 'm1',
      stage: 5,
      output: {
        type: 'learning_objectives',
        data: {
          course: "Test Course",
          tier1: [{ id: "LO1", text: "Test", bloom: "Remember", rationale: "Test" }],
          tier2: [],
          tier3: [],
          tier4_excluded: []
        }
      }
    });
    
    expect(result.stage_completed).toBe(true);
    expect(result.output_filepath).toBeDefined();
    
    // Verify file exists
    const content = await fs.readFile(result.output_filepath!, 'utf-8');
    expect(content).toContain('---'); // YAML frontmatter
    expect(content).toContain('# M1 Learning Objectives');
  });
  
  test('updates session.yaml', async () => {
    await complete_stage({
      project_path: testProjectPath,
      module: 'm1',
      stage: 5,
      output: {
        type: 'learning_objectives',
        data: { /* ... */ }
      }
    });
    
    const sessionPath = path.join(testProjectPath, 'session.yaml');
    const sessionContent = await fs.readFile(sessionPath, 'utf-8');
    const YAML = require('js-yaml');
    const session = YAML.load(sessionContent);
    
    expect(session.methodology.m1.outputs.learning_objectives).toBeDefined();
    expect(session.methodology.m1.completed_stages).toContain(5);
  });
});
```

---

## Implementation Plan: Phased Rollout

### PHASE 1: Proof of Concept (Start Here)

**Implement:** 2 output types only
1. `learning_objectives.ts` (M1 Stage 5) - Most complex
2. `misconceptions.ts` (M1 Stage 4) - Medium complexity

**Tasks:**
- [ ] Create outputs/ directory structure
- [ ] Implement learning_objectives.ts with schema + templates
- [ ] Implement misconceptions.ts
- [ ] Create outputs/index.ts
- [ ] Extend complete_stage with output handling
- [ ] Update load_stage to return output_expected
- [ ] Write unit tests for both output types
- [ ] Write integration test for complete_stage
- [ ] Manual E2E test: Run M1 Stage 4 + 5 with real data

**Success Criteria:**
- complete_stage successfully creates both file types
- Files have valid YAML frontmatter
- Files have correct Markdown formatting
- session.yaml updates correctly
- Claude can complete stages with output

**Timeline:** 4-6 hours

---

### PHASE 2: M1 Completion

**Implement:** Remaining M1 outputs
3. `emphasis_patterns.ts` (M1 Stage 2)
4. `examples.ts` (M1 Stage 3)
5. `material_analysis.ts` (M1 Stage 0)

**Tasks:**
- [ ] Implement 3 remaining M1 output types
- [ ] Add to outputs/index.ts
- [ ] Unit tests for each
- [ ] E2E test: Complete M1 Stage 0 → 5 workflow

**Success Criteria:**
- All M1 stages can be completed with outputs
- Full M1 workflow produces 5 files in 01_methodology/

**Timeline:** 3-4 hours

---

### PHASE 3: M2, M3, M4

**Implement:** Remaining modules
6. `blueprint.ts` (M2)
7. `gap_analysis.ts` (M2, conditional)
8. `generation_log.ts` (M3)
9. `qa_report.ts` (M4)
10. `detailed_feedback.ts` (M4)

**Tasks:**
- [ ] Implement 5 remaining output types
- [ ] Handle conditional outputs (gap_analysis only if entry 'pipeline')
- [ ] Integration across modules
- [ ] Full workflow test: M1 → M2 → M3 → M4

**Success Criteria:**
- Complete methodology workflow works end-to-end
- All 10 output types functional

**Timeline:** 4-5 hours

---

## Edge Cases to Handle

### 1. Overwrite Existing Output

**Scenario:** Teacher wants to revise Stage 5 output

```typescript
complete_stage({
  module: 'm1',
  stage: 5,
  output: { type: 'learning_objectives', data: { /* revised */ } },
  overwrite: true  // ← Explicit flag required
});
```

**Behavior:**
- If `overwrite: false` and output exists → Error
- If `overwrite: true` → Replace file, update session.yaml

---

### 2. Conditional Outputs

**Scenario:** M2 `gap_analysis` only if entry point 'pipeline'

```typescript
// In m2 stage completion
const hasExistingQuestions = await checkQuestionsExist(projectPath);

if (hasExistingQuestions) {
  // Create gap_analysis output
  await complete_stage({
    module: 'm2',
    stage: 7,
    output: { type: 'gap_analysis', data: { ... } }
  });
} else {
  // No gap_analysis needed
  await complete_stage({
    module: 'm2',
    stage: 7
    // No output
  });
}
```

---

### 3. Optional Fields

**Scenario:** Some YAML fields are optional

```typescript
// Schema with optional fields
export const LearningObjectivesSchema = z.object({
  course: z.string(),
  instructor: z.string().optional(),  // ← Optional
  tier1: z.array(...),
  // ...
});

// Template handles optional
export function generateMarkdown(data) {
  return `
**Instructor:** ${data.instructor || 'N/A'}  ← Graceful handling
  `;
}
```

---

## SessionManager Integration

### Required Updates to session.yaml Structure

**Add:** `methodology.outputs` field

```yaml
methodology:
  m1:
    status: complete
    completed_stages: [0, 1, 2, 3, 4, 5]
    outputs:  # ← NEW
      material_analysis: 01_methodology/m1_material_analysis.md
      emphasis_patterns: 01_methodology/m1_emphasis_patterns.md
      examples: 01_methodology/m1_examples.md
      misconceptions: 01_methodology/m1_misconceptions.md
      learning_objectives: 01_methodology/m1_learning_objectives.md
  m2:
    status: in_progress
    completed_stages: []
    outputs: {}
```

### SessionManager Methods Needed

```python
# In packages/qf-pipeline/qf_pipeline/session/manager.py

def add_output(self, module: str, output_type: str, filepath: str):
    """Register methodology output in session"""
    if 'outputs' not in self.data['methodology'][module]:
        self.data['methodology'][module]['outputs'] = {}
    
    self.data['methodology'][module]['outputs'][output_type] = filepath

def get_output(self, module: str, output_type: str) -> Optional[str]:
    """Get filepath for methodology output"""
    return self.data['methodology'][module].get('outputs', {}).get(output_type)
```

---

## Validation Checklist

Before merging each output type:

- [ ] Schema validates correct data
- [ ] Schema rejects invalid data
- [ ] YAML frontmatter is valid (use js-yaml)
- [ ] Markdown renders correctly
- [ ] File created in correct location
- [ ] session.yaml updated correctly
- [ ] Unit tests pass
- [ ] Integration test passes
- [ ] Manual test with real data
- [ ] load_stage returns correct output_expected

---

## Reference: All 10 Output Types Summary

| Output Type | Module | Stage | Conditional | Priority |
|-------------|--------|-------|-------------|----------|
| material_analysis | M1 | 0 | No | DOCUMENTATION |
| emphasis_patterns | M1 | 2 | No | MANDATORY |
| examples | M1 | 3 | No | MANDATORY |
| misconceptions | M1 | 4 | No | MANDATORY |
| learning_objectives | M1 | 5 | No | MANDATORY |
| blueprint | M2 | 7 | No | MANDATORY |
| gap_analysis | M2 | 7 | Yes (pipeline) | CONDITIONAL |
| generation_log | M3 | N/A | No | DOCUMENTATION |
| qa_report | M4 | N/A | No | MANDATORY |
| detailed_feedback | M4 | N/A | No | DOCUMENTATION |

**Implementation Order:**
1. learning_objectives (most complex)
2. misconceptions (medium)
3. emphasis_patterns, examples, material_analysis (similar to above)
4. blueprint (M2)
5. gap_analysis (conditional logic)
6. generation_log (M3)
7. qa_report, detailed_feedback (M4)

---

## Success Metrics

**Phase 1 Success:**
- [ ] 2 output types working
- [ ] complete_stage creates valid files
- [ ] Claude can complete M1 Stage 4 + 5

**Phase 2 Success:**
- [ ] All 5 M1 outputs working
- [ ] Full M1 workflow (Stage 0 → 5) works

**Phase 3 Success:**
- [ ] All 10 output types working
- [ ] Complete M1 → M2 → M3 → M4 workflow works
- [ ] Entry point 'pipeline' handles conditional outputs

---

## Questions for Niklas

1. **Priority:** Start Phase 1 immediately or discuss further?
2. **Testing:** Need sample data for real M1 Stage 5 test?
3. **Error Handling:** How should we handle partial failures? (e.g., file created but session.yaml update fails)

---

## Next Steps

**Immediate:**
1. Create `outputs/` directory structure
2. Implement `learning_objectives.ts`
3. Implement `misconceptions.ts`
4. Extend `complete_stage.ts`
5. Write tests
6. Manual test with real data

**After Phase 1:**
- Review with Niklas
- Adjust based on findings
- Roll out Phase 2

---

**Status:** READY FOR IMPLEMENTATION  
**Estimated Total Time:** 11-15 hours across 3 phases  
**Risk Level:** LOW (iterative approach, clear architecture)
