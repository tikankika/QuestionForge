RFC-007: LLM Workflow Control Patterns for MCP-Based Systems
FieldValueStatusDraftCreated2026-01-19AuthorNiklas KarlssonContextQuestionForge M1 workflow issuesRelates toRFC-004, m1_complete_workflow.md

Executive Summary
This RFC analyzes fundamental challenges in controlling LLM workflow execution through MCP (Model Context Protocol) servers, based on real-world failures in QuestionForge's M1 (Material Analysis) implementation. We document why certain workflow patterns fail, identify principles that govern LLM behavior in tool-calling contexts, and provide proven patterns for building reliable multi-step workflows.
Key Finding: MCP cannot "control" Claude's execution - it can only provide tools and guidance. Reliable workflows require either explicit user intervention at each step OR tool-level constraints that prevent incorrect sequences.

1. Problem Statement
1.1 The Intended Workflow (M1 Stage 0)
QuestionForge M1 Stage 0 was designed as an iterative process:
DESIGNED WORKFLOW:
1. load_stage(stage=0) → Returns methodology
2. read_materials(filename=null) → List files
3. FOR EACH material:
   a. Read ONE material (user uploads OR MCP reads)
   b. Claude analyzes
   c. Claude presents findings to teacher
   d. Teacher provides feedback
   e. save_m1_progress(action="add_material")
   f. Continue to next material
4. After ALL materials analyzed:
   save_m1_progress(action="save_stage")
5. Proceed to Stage 1
Expected tool calls:

load_stage: 1×
read_materials (list): 1×
read_materials (read) OR user upload: N× (one per material)
save_m1_progress: N+1× (N materials + 1 stage complete)

1.2 What Actually Happened (ARTI1000X Session)
ACTUAL EXECUTION:
1. load_stage(stage=0) ✅ (methodology returned)
2. read_materials(filename=null) ✅ (10 files listed)
3. Claude read ALL 10 PDFs via repeated read_materials calls ❌
4. Claude analyzed everything in one response ❌
5. Claude called save_m1_progress ONCE with all data ❌
6. Claude immediately tried to proceed to Stage 1 ❌
Problems:

❌ No teacher feedback loop between materials
❌ No progressive saving after each material
❌ No validation checkpoints
❌ Workflow completed in minutes instead of expected 60-90 min

1.3 Why This Matters
The failure represents three fundamental misunderstandings about LLM workflow control:

Assumption: "Methodology files act as executable programs"

Reality: They're contextual suggestions that may be ignored


Assumption: "MCP can enforce execution order"

Reality: MCP is pull-based; Claude decides when/how to call tools


Assumption: "'WAIT' instructions will pause Claude"

Reality: Claude generates complete responses; can't pause mid-execution




2. Core Principles of LLM Workflow Control
Principle 1: Pull-Based Architecture Constraint
MCP's Fundamental Design:
┌─────────────────────────────────────────────┐
│ MCP IS REACTIVE, NOT PROACTIVE              │
├─────────────────────────────────────────────┤
│                                             │
│  ✅ Claude calls tool → MCP responds        │
│  ❌ MCP cannot initiate actions             │
│  ❌ MCP cannot "push" commands to Claude    │
│  ❌ MCP cannot interrupt Claude's reasoning │
│                                             │
└─────────────────────────────────────────────┘
Implications:

MCP cannot enforce "you MUST call tool X before tool Y"
MCP cannot prevent Claude from calling tools in wrong order
MCP cannot force Claude to wait for user input
MCP can only respond to what Claude asks for

What MCP CAN do:

Return error messages if prerequisites not met
Include "next step" guidance in responses
Track state and inform Claude of progress
Refuse to execute operations that violate constraints

Principle 2: Single-Turn Completion Bias
LLMs are trained to complete tasks in one response:
User: "Analyze these 10 PDFs"

Claude's internal reasoning:
"I should analyze all 10 PDFs to fully answer the question.
 I'll read them all, synthesize findings, present complete analysis.
 This is most helpful to the user."
Why this happens:

Training on helpfulness: "Complete the task fully"
Efficiency optimization: "Don't make user wait for multiple turns"
Pattern matching: "List of items → process all items"

Counterintuitive result:
Even when methodology says "ONE at a time", Claude sees the end goal (all materials analyzed) and optimizes toward completing it quickly.
Mitigation strategies:

Make each step a separate user request
Use tool-level constraints (refuse to process multiple items)
Provide strong immediate feedback after each item

Principle 3: Instruction Following Is Probabilistic
Methodology files are not code:
┌─────────────────────────────────────────────┐
│ METHODOLOGY ≠ DETERMINISTIC PROGRAM         │
├─────────────────────────────────────────────┤
│                                             │
│  Methodology: "Do A, then B, then C"        │
│                                             │
│  Claude's interpretation (probabilistic):   │
│  - 70% chance: Follows A → B → C            │
│  - 20% chance: Does A and C, skips B        │
│  - 10% chance: Optimizes to different order │
│                                             │
└─────────────────────────────────────────────┘
Factors affecting compliance:

Length of methodology: Longer = more skimming
Clarity of instructions: Ambiguous = more interpretation
Task complexity: Multi-step = more deviation
Explicit vs implicit: "Do NOT do X" > "After X, do Y"

Real example from M1:
markdownMethodology said: 
"UPPREPA steg 2-6 för varje fil"

Claude interpreted:
"Process all files to complete the task"
```

### Principle 4: Context Dilution Effect

**Long methodology files get less attention:**
```
Lines of methodology:
0-100:   High attention, detailed following
100-300: Medium attention, key points followed  
300-500: Skimming, pattern matching
500+:    May be partially ignored
```

**Evidence:**
- M1 Stage 0 methodology: 267 lines
- Critical "one-at-a-time" instruction: Around line 40
- Stage completion workflow: Around line 250
- Claude clearly read beginning but skipped later details

**Design implication:**
Most critical constraints should be in:
1. Tool names themselves (`list_materials` vs `read_single_material`)
2. Tool descriptions (seen every time tool is considered)
3. First 50 lines of methodology
4. Tool response messages (reinforcement)

### Principle 5: User Agency Is Required for Reliability

**The uncomfortable truth:**
```
┌─────────────────────────────────────────────┐
│ FOR RELIABLE MULTI-STEP WORKFLOWS:          │
│                                             │
│  Fully Automated (Claude decides) → Fragile │
│  Semi-Automated (User + Claude) → Reliable  │
│  Manual (User decides each step) → Most     │
│                                     Reliable │
└─────────────────────────────────────────────┘
Why user involvement helps:

Forces one-step-at-a-time execution
Provides natural checkpoints
Allows for corrections mid-workflow
Matches pedagogical goal (teacher control)

The pedagogical alignment:
QuestionForge's philosophy: "Teacher must maintain decision-making authority"
This actually ALIGNS with technical reality: User-in-the-loop workflows are more reliable than fully automated ones.

3. Patterns That Work
Pattern 1: Explicit User-Driven Steps
Design Principle: Each stage = one user request
Implementation:
markdown## FOR TEACHERS: How to Run M1 Stage 0

You will guide Claude through analyzing each material:

### Step 1: Start Stage 0
Say: "Start M1 Stage 0 analysis"

### Step 2: For Each Material
Say: "Analyze [filename.pdf]"
- Review Claude's analysis
- Provide feedback if needed
- Say: "Save and continue"

### Repeat until all materials analyzed

### Step 3: Complete Stage
Say: "Finalize Stage 0"
Tool design to support this:
typescript// Each user request maps to ONE tool call + ONE action

User: "Analyze lecture1.pdf"
→ Claude calls read_single_material("lecture1.pdf")
→ Claude analyzes and presents findings
→ Stops and waits for next user instruction

User: "Save and continue"  
→ Claude calls save_m1_progress(action="add_material")
→ Claude asks: "Which file should I analyze next?"
→ Stops and waits
Pros:

✅ Most reliable (user controls flow)
✅ Natural checkpoints
✅ Easy to resume if interrupted
✅ Teacher maintains control (pedagogical goal)

Cons:

❌ More manual than hoped
❌ Requires discipline from user
❌ Slower than automated flow

When to use:

Critical workflows where errors are costly
Pedagogical contexts requiring teacher control
Processes with many decision points

Pattern 2: Tool-Enforced Constraints
Design Principle: Tools refuse invalid operations
Implementation:
typescript// BAD: Flexible tool that can be misused
interface ReadMaterialsInput {
  filename?: string;  // Can read any file, multiple calls
}

// GOOD: Separate tools with clear constraints
interface ListMaterialsInput {
  project_path: string;
  // No filename - can ONLY list
}

interface ReadSingleMaterialInput {
  project_path: string;
  filename: string;  // Must specify ONE file
}

// BETTER: Tool tracks state and enforces order
interface ReadSingleMaterialInput {
  project_path: string;
  filename: string;
}

async function read_single_material(input) {
  // Check: Has this material already been analyzed?
  const state = await getM1State(input.project_path);
  
  if (state.materials[input.filename]?.analyzed) {
    return {
      error: "Material already analyzed",
      suggestion: "Call list_materials() to see which files remain"
    };
  }
  
  // Check: Are we in the right stage?
  if (state.current_stage !== 0) {
    return {
      error: `Cannot read materials in Stage ${state.current_stage}`,
      suggestion: "Complete current stage first"
    };
  }
  
  // Proceed with reading...
}
State tracking in save_m1_progress:
typescriptinterface M1State {
  current_stage: 0 | 1 | 2 | 3 | 4 | 5;
  materials: {
    [filename: string]: {
      analyzed: boolean;
      saved: boolean;
      analyzed_at: string;
    }
  };
  can_proceed_to_stage_1: boolean;
  next_required_action: string;
}

async function save_m1_progress(action, data) {
  const state = await loadState();
  
  if (action === "add_material") {
    // Mark this material as saved
    state.materials[data.filename] = {
      analyzed: true,
      saved: true,
      analyzed_at: new Date().toISOString()
    };
    
    // Check if all materials complete
    const remaining = Object.values(state.materials)
      .filter(m => !m.analyzed);
    
    state.can_proceed_to_stage_1 = remaining.length === 0;
    state.next_required_action = remaining.length > 0
      ? `Analyze next material: ${remaining[0].filename}`
      : `All materials complete. Call save_m1_progress(action="save_stage")`;
    
    return {
      success: true,
      progress: `${state.materials.filter(m => m.analyzed).length}/${state.materials.length}`,
      next_step: state.next_required_action,
      can_proceed: state.can_proceed_to_stage_1
    };
  }
  
  if (action === "save_stage") {
    if (!state.can_proceed_to_stage_1) {
      return {
        error: "Cannot complete Stage 0 - materials not fully analyzed",
        remaining: state.materials.filter(m => !m.analyzed).map(m => m.filename)
      };
    }
    
    // Save stage completion...
  }
}
Pros:

✅ Prevents many common errors
✅ Provides helpful guidance
✅ State persists across sessions
✅ Can enforce prerequisites

Cons:

❌ More complex implementation
❌ Requires state management
❌ Can't prevent ALL deviations

When to use:

When tools could be called in wrong order
When state needs to persist
When prerequisites must be met

Pattern 3: Progressive Feedback Loops
Design Principle: Tool responses guide next actions
Implementation:
typescript// Tool responses include explicit next steps

// After listing materials
{
  materials: ["file1.pdf", "file2.pdf", "file3.pdf"],
  next_step: "Analyze first material: read_single_material('file1.pdf')",
  workflow_hint: "Analyze materials one at a time, save after each"
}

// After reading one material
{
  filename: "file1.pdf",
  content: "...",
  next_step: "Present findings to teacher, then save with save_m1_progress()",
  reminder: "Do NOT proceed to next material without teacher feedback"
}

// After saving one material (1 of 3)
{
  success: true,
  progress: "1/3 materials analyzed",
  next_step: "Analyze next material: read_single_material('file2.pdf')",
  reminder: "⚠️ Do NOT skip to Stage 1 - 2 materials remain"
}

// After saving last material (3 of 3)
{
  success: true,
  progress: "3/3 materials analyzed",
  next_step: "Complete stage: save_m1_progress(action='save_stage')",
  ready_for_next_stage: true
}

// After completing stage
{
  success: true,
  stage_complete: true,
  summary: "Stage 0 complete: 3 materials analyzed",
  next_step: "Proceed to Stage 1: load_stage(stage=1)"
}
Enhanced methodology to support this:
markdown## FOR CLAUDE: Using Tool Responses

IMPORTANT: Tool responses include `next_step` field - FOLLOW IT.

After each tool call:
1. Read the `next_step` field
2. Present findings to teacher (if applicable)
3. Follow the next_step instruction
4. Do NOT improvise or skip ahead
Pros:

✅ Continuous guidance at each step
✅ Reduces need for long methodology
✅ Adapts to actual state
✅ Reinforces correct behavior

Cons:

❌ Still relies on Claude following guidance
❌ Requires thoughtful response design
❌ Not as reliable as tool constraints

When to use:

In combination with other patterns
When workflow has clear linear progression
When you want to guide without forcing

Pattern 4: State Machines in MCP
Design Principle: MCP tracks workflow state, refuses invalid transitions
Implementation:
typescriptinterface M1WorkflowState {
  stage: 0 | 1 | 2 | 3 | 4 | 5 | "complete";
  stage_status: "not_started" | "in_progress" | "complete";
  
  // Stage 0 specific
  materials_total: number;
  materials_analyzed: number;
  current_material?: string;
  
  // Allowed next actions
  allowed_actions: string[];
  
  // Transition history
  transitions: Array<{
    from_stage: number;
    to_stage: number;
    timestamp: string;
    trigger: string;
  }>;
}

class M1StateMachine {
  async transition(from: M1WorkflowState, action: string): Promise<M1WorkflowState> {
    // Validate transition
    if (!from.allowed_actions.includes(action)) {
      throw new Error(
        `Invalid action '${action}' in stage ${from.stage}. ` +
        `Allowed: ${from.allowed_actions.join(", ")}`
      );
    }
    
    // Execute transition
    switch (action) {
      case "start_stage_0":
        return {
          ...from,
          stage: 0,
          stage_status: "in_progress",
          allowed_actions: ["analyze_material", "load_stage_1"]
        };
        
      case "analyze_material":
        return {
          ...from,
          materials_analyzed: from.materials_analyzed + 1,
          allowed_actions: 
            from.materials_analyzed + 1 < from.materials_total
              ? ["analyze_material", "save_stage_0"]
              : ["save_stage_0"]
        };
        
      case "save_stage_0":
        if (from.materials_analyzed < from.materials_total) {
          throw new Error(
            `Cannot complete Stage 0: only ${from.materials_analyzed}/${from.materials_total} analyzed`
          );
        }
        return {
          ...from,
          stage_status: "complete",
          allowed_actions: ["load_stage_1"]
        };
        
      case "load_stage_1":
        if (from.stage_status !== "complete") {
          throw new Error("Must complete Stage 0 before proceeding to Stage 1");
        }
        return {
          ...from,
          stage: 1,
          stage_status: "in_progress",
          allowed_actions: ["stage_1_actions..."]
        };
    }
  }
}
Using the state machine in tools:
typescriptasync function load_stage(stage: number) {
  const state = await getState();
  
  // Validate transition
  const action = `load_stage_${stage}`;
  if (!state.allowed_actions.includes(action)) {
    return {
      error: `Cannot load Stage ${stage} from current state`,
      current_stage: state.stage,
      current_status: state.stage_status,
      required_action: state.allowed_actions[0],
      hint: getHintForAction(state.allowed_actions[0])
    };
  }
  
  // Proceed with loading stage...
}
Pros:

✅ Enforces valid transitions
✅ Prevents skipping stages
✅ Clear error messages
✅ Auditable workflow history

Cons:

❌ Most complex to implement
❌ Requires careful state design
❌ Can be overly rigid if poorly designed

When to use:

Complex workflows with many stages
When stage order is critical
When you need audit trails
When multiple paths are possible


4. Anti-Patterns (What NOT to Do)
Anti-Pattern 1: "WAIT" Instructions in Methodology
What it looks like:
markdown## Workflow

1. Read first PDF
2. WAIT for user to provide feedback
3. Save the analysis
4. WAIT for user to confirm
5. Read next PDF
```

**Why it fails:**
- LLMs don't have "wait" capability
- Each LLM response is complete and self-contained
- Claude will try to complete all steps in one turn
- "WAIT" is interpreted as "then continue"

**What actually happens:**
```
Claude's reasoning:
"I should read the PDF, anticipate what feedback might be,
 save the analysis, and move to the next PDF. This completes
 the task efficiently."
Correct approach:
markdown## FOR TEACHERS: Workflow

### Request 1: "Analyze PDF #1"
Claude will analyze and present findings.
Review the analysis.

### Request 2: "Save and continue"  
Claude will save and ask for next file.

### Request 3: "Analyze PDF #2"
(Repeat process)
Anti-Pattern 2: Assuming Linear Execution
What it looks like:
typescript// Assuming tools will be called in order
// No validation of prerequisites

async function save_m1_progress(stage, action, data) {
  // Just save whatever is provided
  await writeFile(`stage_${stage}_${action}.json`, data);
  return { success: true };
}
```

**Why it fails:**
- Claude might call `save_m1_progress` before analyzing materials
- Claude might skip straight to Stage 1
- No validation means corrupted workflow state

**What actually happens:**
```
Claude might:
1. Call load_stage(0)
2. Immediately call save_m1_progress(stage=0, action="save_stage")
3. Call load_stage(1)

Result: Stage 0 "complete" with no actual analysis
Correct approach:
typescriptasync function save_m1_progress(stage, action, data) {
  // Validate prerequisites
  const state = await loadState();
  
  if (action === "save_stage" && state.materials_analyzed === 0) {
    return {
      error: "Cannot complete stage - no materials analyzed",
      required_action: "Analyze materials first",
      hint: "Call read_materials() then analyze each file"
    };
  }
  
  // Proceed only if valid...
}
Anti-Pattern 3: Long Methodology as "Program"
What it looks like:
markdown# M1 Complete Methodology (600 lines)

## Stage 0 Instructions
[100 lines of detailed instructions]

## Stage 1 Instructions  
[100 lines of detailed instructions]

## Stage 2 Instructions
[100 lines of detailed instructions]

...

## Detailed Examples
[200 lines of examples]
Why it fails:

Claude skims long documents
Critical constraints buried in middle get missed
Examples are read but specific instructions forgotten

Evidence from M1:

Methodology was 267 lines
Claude clearly read the beginning (knew what Stage 0 was)
But missed "one-at-a-time" constraint in middle
Improvised workflow based on understanding goal, not process

Correct approach:
markdown# M1 Stage 0 - Material Analysis

## CRITICAL CONSTRAINTS (READ FIRST)
- Analyze ONE material at a time
- Save after EACH material
- Do NOT proceed to Stage 1 until teacher approves

## Process
[Concise steps]

## Details
[More depth if needed]
OR even better: Split into separate files per stage, load only current stage.
Anti-Pattern 4: Implicit Stage Gates
What it looks like:
markdown## After Stage 0

You have now completed material analysis.
The next step is Stage 1: Initial Validation.
```

**Why it fails:**
- No explicit barrier
- Claude interprets "next step" as "continue now"
- No tool-level enforcement

**What actually happens:**
```
Claude's reasoning:
"I've completed Stage 0. The methodology says Stage 1 is next.
 I'll load Stage 1 and continue."

→ load_stage(stage=1) called immediately
→ Teacher never reviewed Stage 0 outputs
Correct approach:
Option A: Explicit user gate:
markdown## Stage 0 Complete

✅ Materials analyzed and saved.

**STOP HERE.**

Teacher will review outputs, then say: "Proceed to Stage 1"
Option B: Tool-enforced gate:
typescriptasync function load_stage(stage: number) {
  if (stage === 1) {
    const stage0 = await getStageStatus(0);
    if (!stage0.teacher_approved) {
      return {
        error: "Stage 1 requires teacher approval of Stage 0",
        action_required: "Teacher must review Stage 0 outputs and approve"
      };
    }
  }
  // Proceed...
}

5. Recommendations for QuestionForge
Option A: User-Guided Workflow (Highest Reliability)
Design:

Each stage = explicit user request
Teacher says "Start Stage 0", "Analyze file1.pdf", "Save and continue", etc.
MCP provides tools, Claude executes one step per user message

Implementation changes needed:

Update methodology files to be teacher-facing instructions
Simplify tool responses to just return data (no complex guidance)
Create user guide documenting exact commands to say

Pros:

✅ Most reliable
✅ Teacher maintains full control (aligns with pedagogy)
✅ Easy to implement
✅ Natural checkpoints

Cons:

❌ Most manual
❌ Requires teacher discipline

Recommended for:

Initial implementation
Validating the methodology
Critical production use

Option B: Tool-Enforced Constraints (Balanced)
Design:

Split tools: list_materials, read_single_material (not read_materials with optional param)
Add state tracking: track which materials analyzed, prevent skipping stages
Enhanced responses: guide Claude with next_step hints

Implementation changes needed:

Refactor read_materials:

typescript// Remove read mode
list_materials(project_path) → returns file list

// Add new tool
read_single_material(project_path, filename) → returns ONE file
  - Validates file exists
  - Checks if already analyzed
  - Returns error if trying to read multiple

Add state management to save_m1_progress:

typescriptinterface M1State {
  materials: { [name: string]: { analyzed: boolean, saved: boolean } };
  current_stage: number;
  stage_complete: boolean;
}

save_m1_progress(action, data) {
  // Validate prerequisites
  // Update state
  // Return next_step guidance
}

Add gate to load_stage:

typescriptload_stage(stage) {
  if (stage > 0) {
    // Check previous stage complete
    // Refuse if not
  }
}
Pros:

✅ Prevents many common errors
✅ Provides helpful guidance
✅ Less manual than Option A

Cons:

❌ More implementation complexity
❌ Can't prevent ALL deviations
❌ Requires state management

Recommended for:

After validating with Option A
Production use with trained teachers
Balancing automation and control

Option C: State Machine + Enhanced Feedback (Most Automated)
Design:

Full state machine tracking workflow state
Every tool validates current state
Rich feedback in every response
Methodology optimized for compliance

Implementation changes needed:

Implement M1StateMachine (see Pattern 4)
All tools check state before executing
Methodology rewritten to 50-100 lines focused on critical constraints
Tool responses include detailed next_step guidance

Pros:

✅ Most automated
✅ Catches nearly all errors
✅ Auditable workflow

Cons:

❌ Most complex to implement
❌ Hardest to debug
❌ Can be overly rigid

Recommended for:

Future enhancement
After Options A & B validated
When scaling to many users


6. Recommended Implementation Roadmap
Phase 1: Validate with User-Guided (Option A)
Goal: Verify the M1 methodology works when properly followed
Actions:

Update methodology files to be teacher instructions
Document exact commands: "Say: 'Analyze file1.pdf'"
Test with 2-3 courses
Document pain points

Success criteria:

Teachers can complete M1 reliably
Outputs match expected quality
Process takes expected time (60-90 min)

Timeline: 1 week
Phase 2: Implement Tool Constraints (Option B)
Goal: Reduce manual effort while maintaining reliability
Actions:

Split read_materials → list_materials + read_single_material
Add state tracking to save_m1_progress
Add stage gate validation to load_stage
Update methodology to work with new tools

Success criteria:

Teachers can still guide workflow
Common errors prevented by tools
Process feels smoother than Phase 1

Timeline: 1-2 weeks
Phase 3: Enhanced Feedback (Option B+)
Goal: Guide Claude more effectively
Actions:

Add next_step to all tool responses
Shorten methodology to 50-100 lines
Test whether Claude follows guidance more reliably

Success criteria:

Reduced need for teacher intervention
Claude rarely attempts invalid operations
Workflow feels natural

Timeline: 1 week
Phase 4: Consider State Machine (Option C)
Goal: Maximum automation for trained users
Actions:

Design M1StateMachine
Implement in qf-scaffolding
Test with experienced teachers

Decision point: Only implement if Phases 1-3 show need for more automation
Timeline: 2-3 weeks (if needed)

7. Conclusion
Key Takeaway: MCP cannot "control" Claude - it can only provide tools and guidance. Reliable workflows require either explicit user intervention OR tool-level constraints.
For QuestionForge:

Start with Option A (user-guided) to validate methodology
Implement Option B (tool constraints) for production
Consider Option C (state machine) only if needed

General Principle:
The most reliable LLM workflows embrace user agency rather than fighting it. QuestionForge's pedagogical goal (teacher maintains control) actually aligns with technical reality (user-in-loop is most reliable).

---

## 8. Reality Check - What Actually Works

*Added 2026-01-19 based on Claude Code feedback*

### 8.1 The Uncomfortable Truth

Even with all proposed tool constraints (Option B/C), **Claude can still:**

```
❌ Call read_single_material 10 times in RAD (rapid succession)
❌ Run entire workflow in ONE user turn
❌ Ignore "next_step" guidance in tool responses
```

**The core limitation:**
```
┌─────────────────────────────────────────────────────────────────┐
│ Claude generates its ENTIRE response before sending it.         │
│                                                                 │
│ There is no "pause mid-response and wait for user input".       │
│                                                                 │
│ If Claude DECIDES to process 10 files in one response,          │
│ no technical mechanism can prevent it.                          │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Reliability Matrix (Honest Assessment)

```
┌────────────────────┬────────────┬────────────┬─────────────┐
│ Approach           │ Reliability│ Automation │ Complexity  │
├────────────────────┼────────────┼────────────┼─────────────┤
│ User-Driven (A)    │ 95%        │ Low        │ Low         │
│ Tool Constraints(B)│ 70%        │ Medium     │ Medium      │
│ State Machine (C)  │ 70%        │ Medium     │ High        │
│ Batch + Gate       │ 90%        │ High       │ Low         │
└────────────────────┴────────────┴────────────┴─────────────┘
```

**Why Option B/C only reach 70%:**
- Tools can refuse invalid operations
- Tools CANNOT prevent Claude from making multiple valid calls in sequence
- Claude may follow guidance 70% of the time, deviate 30%

**Why User-Driven reaches 95%:**
- Each step is a separate user request
- Claude completes ONE action per request
- Natural stopping points after each response

### 8.3 MCP Sampling - Future Possibility

MCP specification includes "sampling" - allows server to request LLM completion:
```
Server → Client: "sampling/createMessage" request
Client → Server: LLM response
```

**Current status:** Claude Desktop does NOT support sampling yet.

If/when supported, this could enable:
- Server-initiated dialogue control
- "Stop and wait" patterns
- More reliable multi-step workflows

**For now:** Not available. Design for current limitations.

### 8.4 The Critical Question

**Is "one-at-a-time with feedback" a HARD requirement?**

**If YES:** → Option A (user-driven) is the ONLY reliable solution
**If NO:** → Batch + Gate provides 90% reliability with high automation

---

## 9. Final Recommendation

*Based on QuestionForge requirement: "one-at-a-time with teacher feedback" is a HARD pedagogical requirement.*

### 9.1 Recommendation: Option A (User-Driven Workflow)

```
┌─────────────────────────────────────────────────────────────────┐
│ FINAL RECOMMENDATION: OPTION A (USER-DRIVEN)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Reliability: 95%                                               │
│  Complexity: Low                                                │
│  Implementation: Process change, minimal code changes           │
│                                                                 │
│  Why: Only approach that GUARANTEES teacher feedback            │
│       between materials.                                        │
│                                                                 │
│  Trade-off: More manual, but aligns with pedagogical goals.     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Implementation: Teacher-Facing Workflow

```markdown
## For Teachers: M1 Stage 0 Workflow

### Step 1: Start
Say: "Start M1 Stage 0 analysis"

### Step 2: Analyze Each Material
Say: "Analyze [filename.pdf]"
- Review Claude's analysis
- Provide corrections if needed
Say: "Save and continue"

### Repeat for all materials

### Step 3: Complete
Say: "Finalize Stage 0"
```

### 9.3 Updated Implementation Phases

**Phase 1: User-Driven (REQUIRED - DO THIS FIRST)**
- Create teacher-facing instructions
- Test with 2-3 courses
- Validate methodology works when properly followed
- Timeline: 1 week

**Phase 2: OPTIONAL Tool Enhancements**
- Add basic constraints to prevent obvious errors
- NOT to automate workflow
- Accept that automation has limits
- Only if Phase 1 reveals specific pain points

### 9.4 Accepting Reality

```
We cannot make Claude reliably follow "one-at-a-time" workflow
automatically.

We CAN make teachers successfully guide Claude through it
step-by-step.

This is not a failure of design - it's acknowledging that
user-in-loop workflows are more reliable than fully automated ones.
```

### 9.5 Alignment with Pedagogical Goals

QuestionForge's core principle: **"Teacher maintains decision-making authority"**

This ALIGNS with the technical reality:
- User-in-loop workflows are most reliable
- Teacher control is both pedagogically desired AND technically optimal
- The "limitation" becomes a feature

---

## 10. Document History

| Date | Change |
|------|--------|
| 2026-01-19 | Initial draft (Sections 1-7) |
| 2026-01-19 | Added Section 8: Reality Check based on Claude Code research |
| 2026-01-19 | Added Section 9: Final Recommendation (Option A for hard requirement) |

---

*RFC-007 Status: COMPLETE - Ready for implementation*
