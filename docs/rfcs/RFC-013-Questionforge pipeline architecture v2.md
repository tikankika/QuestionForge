# RFC-013: QuestionForge Pipeline Architecture v2.1
## Quality-First Approach with Interactive Guided Build

**RFC Status:** Draft  
**Created:** 2026-01-25  
**Authors:** Niklas Karlsson, Claude  
**Version:** 2.1 (Major Redesign)  
**Supersedes:** Previous pipeline architecture discussions

### Related RFCs
- **RFC-012:** Subprocess architecture, unified validator, single source of truth for parsing

---

## Executive Summary

QuestionForge Pipeline v2.0 introduces a fundamental architectural shift with emphasis on **teacher-guided quality control**:

1. **M5 Quality Assurance** - Ensures complete content BEFORE file generation
2. **Step 1: Interactive Guided Build** - Teacher-approved structural normalization with:
   - Progress tracking via frontmatter
   - Question-by-question review workflow
   - MCP tools for teacher interaction
3. **Step 3: Auto-Fix Iteration Engine** - Self-learning from validation loops
4. **Dual self-learning systems** - Both Step 1 and Step 3 improve over time

**Core Principle:** Quality at the source + Teacher in control + Learn from every decision

---

## Current Problems (v1.0)

### Pipeline v1.0 Issues

```
Step 0 → Step 1 (Transform) → Step 2 (Validate) → [Manual Fix Gap] → Step 4 (Export)
                    ↑                                      ↓
                    └──────── CONFUSION & REWORK ─────────┘
```

**Problems:**
1. ❌ No systematic quality assurance before generation
2. ❌ Step 1 has dual role (transform + fix) - confusing
3. ❌ No automatic fix after validation
4. ❌ Manual intervention required but no workflow support
5. ❌ No learning from repeated errors
6. ❌ Question-by-question QA missing
7. ❌ No progress tracking during long editing sessions

---

## Architecture v2.0

### Complete Pipeline Flow

```
┌──────────────────────────────────────────────────────────────┐
│  QUESTIONFORGE PIPELINE v2.0                                  │
│  Quality-First + Interactive Guided Build                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Step 0: Session Setup                                       │
│  - Initialize project structure (updated!)                   │
│  - Load materials/references                                 │
│  - Create working directories                                │
│     ↓                                                         │
│  ┌──────────────────────────────────────────┐                │
│  │ M1: Material Analysis (scaffolding)      │                │
│  │ M2: Assessment Design (scaffolding)      │                │
│  │ M3: Question Generation (scaffolding)    │                │
│  │ M4: [Reserved for future use]            │                │
│  │                                           │                │
│  │ LOCATION: qf-scaffolding (TypeScript)    │                │
│  └──────────────────────────────────────────┘                │
│     ↓                                                         │
│  ┌──────────────────────────────────────────┐                │
│  │ ✨ M5: QUALITY ASSURANCE (NEW!)          │                │
│  │ ════════════════════════════════════════ │                │
│  │ PURPOSE: Ensure complete data BEFORE     │                │
│  │          markdown file generation        │                │
│  │                                           │                │
│  │ DIALOGUE-DRIVEN, ONE QUESTION AT A TIME: │                │
│  │                                           │                │
│  │ For each question:                       │                │
│  │   1. Display question preview            │                │
│  │   2. Check required fields (by type)     │                │
│  │   3. Dialogue if missing                 │                │
│  │      - AI suggests content               │                │
│  │      - User accepts/modifies/provides    │                │
│  │   4. Save decision (log for learning)    │                │
│  │   5. Next question                       │                │
│  │                                           │                │
│  │ OUTPUT: Raw MQG markdown ✅               │                │
│  │ (Complete content, may need structural   │                │
│  │  normalization)                          │                │
│  │                                           │                │
│  │ SAVES TO: questions/m5_output.md         │                │
│  │ LOCATION: qf-scaffolding (TypeScript)    │                │
│  └──────────────────────────────────────────┘                │
│     ↓                                                         │
│  ┌──────────────────────────────────────────┐                │
│  │ 🎯 Step 1: INTERACTIVE GUIDED BUILD      │                │
│  │ ════════════════════════════════════════ │                │
│  │ PURPOSE: Teacher-guided structural       │                │
│  │          normalization with full control │                │
│  │                                           │                │
│  │ PHASE 1: INITIALIZATION                  │                │
│  │ 1. Add progress frontmatter (YAML)       │                │
│  │    - Current question position           │                │
│  │    - Status tracking                     │                │
│  │    - Session metadata                    │                │
│  │ 2. Copy to pipeline/                     │                │
│  │                                           │                │
│  │ PHASE 2: QUESTION-BY-QUESTION REVIEW     │                │
│  │ For each question:                       │                │
│  │   1. Display question                    │                │
│  │   2. Analyze structural issues:          │                │
│  │      - Missing separators (---)          │                │
│  │      - Malformed syntax                  │                │
│  │      - Junk content                      │                │
│  │   3. AI suggests fixes                   │                │
│  │   4. TEACHER APPROVAL GATE:              │                │
│  │      ├─ Accept AI suggestion             │                │
│  │      ├─ Modify suggestion                │                │
│  │      ├─ Provide own fix                  │                │
│  │      ├─ Skip (mark for later)            │                │
│  │      └─ Delete question                  │                │
│  │   5. Log decision for learning           │                │
│  │   6. Update progress frontmatter         │                │
│  │   7. Navigate: Next / Previous / Jump    │                │
│  │                                           │                │
│  │ PHASE 3: COMPLETION                      │                │
│  │ - Remove progress frontmatter            │                │
│  │ - Generate summary report                │                │
│  │ - Save to output/                        │                │
│  │                                           │                │
│  │ 🧠 LEARNING:                             │                │
│  │ - Track teacher decisions                │                │
│  │ - Build pattern database                 │                │
│  │ - Improve future suggestions             │                │
│  │ - Share learnings with Step 3            │                │
│  │                                           │                │
│  │ MCP TOOLS:                                │                │
│  │ - step1_start                            │                │
│  │ - step1_status                           │                │
│  │ - step1_next/previous/jump               │                │
│  │ - step1_analyze_question                 │                │
│  │ - step1_apply_fix                        │                │
│  │ - step1_skip                             │                │
│  │ - step1_finish                           │                │
│  │                                           │                │
│  │ LOCATION: qf-pipeline (Python MCP)       │                │
│  └──────────────────────────────────────────┘                │
│     ↓                                                         │
│  ┌──────────────────────────────────────────┐                │
│  │ Step 2: VALIDATION                       │                │
│  │ ════════════════════════════════════════ │                │
│  │ PURPOSE: Validate against MQG schema     │                │
│  │                                           │                │
│  │ OPERATIONS:                              │                │
│  │ - Parse all questions                    │                │
│  │ - Check against schema v6.5              │                │
│  │ - Categorize errors                      │                │
│  │                                           │                │
│  │ OUTPUT: issues.json                      │                │
│  │ {                                         │                │
│  │   "pedagogical": [...],  // → M5         │                │
│  │   "structural": [...],   // → Step 1     │                │
│  │   "mechanical": [...]    // → Step 3     │                │
│  │ }                                         │                │
│  │                                           │                │
│  │ LOCATION: qf-pipeline (Python)           │                │
│  └──────────────────────────────────────────┘                │
│     ↓                                                         │
│  ┌──────────────────────────────────────────┐                │
│  │ 🔀 ROUTING LAYER                         │                │
│  │ ════════════════════════════════════════ │                │
│  │ Read issues.json:                        │                │
│  │                                           │                │
│  │ IF pedagogical issues → M5 (EXIT)        │                │
│  │ ELIF structural issues → Step 1 (EXIT)   │                │
│  │ ELIF mechanical issues → Step 3          │                │
│  │ ELSE → Step 4 Export ✅                  │                │
│  └──────────────────────────────────────────┘                │
│     ↓ (mechanical issues only)                                │
│  ┌──────────────────────────────────────────┐                │
│  │ Step 3: AUTO-FIX ITERATION ENGINE        │                │
│  │ ════════════════════════════════════════ │                │
│  │ PURPOSE: Fix mechanical errors one at    │                │
│  │          a time until valid              │                │
│  │                                           │                │
│  │ ITERATION LOOP (MAX 10x):                │                │
│  │   ┌─────────────────────────────────┐    │                │
│  │   │ 1. Read issues.json             │    │                │
│  │   │ 2. Pick 1 mechanical issue      │    │                │
│  │   │ 3. Edit questions.md (fix it)   │    │                │
│  │   │ 4. Save updated questions.md    │─┐  │                │
│  │   └─────────────────────────────────┘ │  │                │
│  │                                        │  │                │
│  │   ┌─────────────────────────────────┐ │  │                │
│  │   │ Step 2: Validate again          │◄┘  │                │
│  │   │ → Create NEW issues.json        │    │                │
│  │   └─────────────────────────────────┘    │                │
│  │     ↓                                     │                │
│  │   Still mechanical issues?                │                │
│  │     ├─ YES → Loop (if < 10 iterations)    │                │
│  │     ├─ NO → Check other issue types:      │                │
│  │     │   ├─ Pedagogical? → M5 (EXIT)       │                │
│  │     │   ├─ Structural? → Step 1 (EXIT)    │                │
│  │     │   └─ None? → Step 4 Export ✅       │                │
│  │     └─ MAX 10 reached → ERROR REPORT      │                │
│  │                                           │                │
│  │ 🧠 SELF-LEARNING:                        │                │
│  │ - Track which fixes work                 │                │
│  │ - Build fix rule database                │                │
│  │ - Log successful patterns                │                │
│  │                                           │                │
│  │ LOCATION: qf-pipeline (Python)           │                │
│  └──────────────────────────────────────────┘                │
│     ↓                                                         │
│  Step 4: EXPORT (QTI/Canvas)                                 │
│  - Generate QTI package                                      │
│  - Ready for LMS import                                      │
│                                                               │
│  ┌──────────────────────────────────────────┐                │
│  │ 📊 LOGGING & LEARNING LAYER              │                │
│  │ ════════════════════════════════════════ │                │
│  │ Continuous throughout pipeline:          │                │
│  │                                           │                │
│  │ - M5 decisions → Step 1/3 learning       │                │
│  │ - Step 1 teacher approvals → patterns    │                │
│  │ - Step 3 iterations → fix rules          │                │
│  │ - Pattern detection & rule generation    │                │
│  │ - Cross-learning between steps           │                │
│  │ - Success rate tracking                  │                │
│  │                                           │                │
│  │ LOGS:                                     │                │
│  │ - session.jsonl (RFC-001)                │                │
│  │ - m5_decisions.jsonl                     │                │
│  │ - step1_decisions.jsonl (NEW)            │                │
│  │ - step1_patterns.json (NEW)              │                │
│  │ - step3_iterations.jsonl                 │                │
│  │ - patterns_learned.jsonl                 │                │
│  └──────────────────────────────────────────┘                │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Component Boundaries & Routing Logic

### Error Classification

The pipeline uses a three-tier classification system to route errors to the appropriate component:

#### MECHANICAL ERRORS (Step 3 - Auto-fix)

**Characteristics:**
- Pattern-based fixes
- No human judgment required
- Quantity doesn't matter (1 error or 100 errors)
- Systematic, repeatable transformations

**Examples:**
```markdown
# Q001
@end_field
# Q002  ← Missing separator (---)
@end_field
# Q003  ← Missing separator (---)
...
# Q040  ← Missing separator (---)

→ Step 3 auto-fixes ALL (even 100 missing separators)
```

**Error Types:**
- Missing separators (`---`)
- Syntax normalization (`type:` → `^type`)
- Format corrections (spacing, indentation)
- Known pattern-based issues

**Why Step 3?**
- Mechanical transformation
- No pedagogical decision needed
- Can be learned and automated
- High confidence fixes

---

#### STRUCTURAL DECISIONS (Step 1 - Teacher)

**Characteristics:**
- Requires human judgment
- Ambiguous or context-dependent
- Teacher must choose/decide
- Question-by-question approval needed

**Examples:**
```markdown
# ???  ← What should this question be named?
^type multiple_choice_single
...

→ Teacher must decide: "Q001"? "Fråga_AI_Definition"? "intro_question"?
```

**Error Types:**
- Question naming/identifiers (when missing or ambiguous)
- Structural ambiguities (unclear question boundaries)
- Format decisions requiring context
- Teacher preference choices

**Why Step 1?**
- Human judgment required
- Context-dependent decisions
- No clear "correct" answer
- Teacher maintains control

---

#### PEDAGOGICAL CONTENT (M5)

**Characteristics:**
- Missing essential content
- Teacher must create/provide content
- Pedagogical decisions required
- Large gaps in question data

**Examples:**
```markdown
# Q001
(no ^type tag!)           ← What type is this question?
(no correct_answer!)      ← Which answer is correct?
(no feedback!)            ← What feedback for students?

→ M5 required: Teacher must choose type, mark correct answer, write feedback
```

**Error Types:**
- Missing question type
- Missing correct answer markers
- Missing feedback (correct/incorrect/partial)
- Missing required fields for question type
- Incomplete pedagogical metadata (bloom_level, difficulty)

**Why M5?**
- Content creation needed
- Pedagogical expertise required
- Cannot be auto-generated
- Teacher must author/choose

---

### Routing Flow

```
Step 2: Validation
  ↓
  Creates: issues.json
  ↓
Routing Layer (reads issues.json):
  ├─ PEDAGOGICAL errors?
  │    ↓
  │  M5: Content creation (EXIT)
  │
  ├─ STRUCTURAL DECISIONS errors?
  │    ↓
  │  Step 1: Teacher review (EXIT)
  │
  └─ MECHANICAL errors?
       ↓
     Step 3: Auto-fix iteration
       │
       ├─ Round 1: Fix 1 issue → questions.md updated
       ├─ Step 2 validate → NEW issues.json (fewer errors)
       ├─ Round 2: Fix 1 issue → questions.md updated  
       ├─ Step 2 validate → NEW issues.json (fewer errors)
       ├─ ...
       ├─ Round N:
       │   ├─ NO mechanical errors left?
       │   │   ├─ Pedagogical/Structural found? → Route to M5/Step1 (EXIT)
       │   │   └─ No errors? → Step 4 Export ✅
       │   └─ Still mechanical errors? → Continue loop
       └─ Max 10 rounds reached? → ERROR REPORT
```

### Routing Rules

**Routing Layer (after Step 2 validation fails):**

1. **Read issues.json** created by Step 2

2. **Priority-based routing:**
   - **PEDAGOGICAL errors first** (blocking)
     → Route to M5 (EXIT)
     → Teacher must provide content
   
   - **STRUCTURAL errors second** (requires judgment)
     → Route to Step 1 (EXIT)
     → Teacher must decide
   
   - **MECHANICAL errors third** (auto-fixable)
     → Route to Step 3
     → Iteration loop begins

3. **No errors**
   → Continue to Step 4 (Export)

**Step 3 Iteration Loop:**

```python
round = 0
max_rounds = 10

while round < max_rounds:
    # Read issues from Step 2
    issues = read_issues_json()
    
    # Check routing
    if issues['pedagogical']:
        return route_to_m5(issues['pedagogical'])
    
    if issues['structural']:
        return route_to_step1(issues['structural'])
    
    if not issues['mechanical']:
        return route_to_step4()  # No errors left!
    
    # Pick 1 mechanical issue
    issue = pick_one(issues['mechanical'])
    
    # Fix it
    fix_in_questions_md(issue)
    save_questions_md()
    
    # Re-validate
    run_step2_validation()
    
    round += 1

# Max rounds reached
return error_report(remaining_issues)
```

**Key Points:**
- Step 3 NEVER routes back to M5 or Step 1 itself
- Routing happens in the layer BETWEEN Step 2 and Step 3
- Each round: 1 fix → validate → check routing → next fix
- Files: issues.json (input) + questions.md (edit in-place)

---

### Pattern Learning & Sharing Strategy

#### Phase 1-3: Separate Pattern Systems (CURRENT)

**Step 1 Patterns:**
- **Location:** `logs/step1_patterns.json`
- **Purpose:** Improve AI suggestions for teacher
- **Learning source:** Teacher decisions in Step 1
- **Usage:** Step 1 AI suggestions only

**Step 3 Fix Rules:**
- **Location:** `logs/step3_fix_rules.json`
- **Purpose:** Auto-fix mechanical errors
- **Learning source:** Successful iterations in Step 3
- **Usage:** Step 3 auto-fixes only

**No cross-communication in Phase 1-3** - Each system learns independently.

**Why separate initially?**
- Simpler to implement
- No risk of conflicts
- Each system can stabilize independently
- Clear separation of concerns

---

#### Phase 4-5: Cross-Learning System (FUTURE UPGRADE)

**Bidirectional learning between Step 1 and Step 3:**

##### Step 1 → Step 3 Learning

**Scenario:**
```
Day 1 - Step 1 Session:
Teacher approves: "Insert --- separator"
  ↓
Logged to step1_patterns.json
{
  "pattern_id": "STEP1_001",
  "type": "missing_separator_after",
  "fix": "Insert '---' after @end_field",
  "confidence": 0.85,
  "teacher_approved": 23
}

Day 2 - Step 3 Iteration:
Step 3 detects: "40 questions missing separators"
  ↓
Checks step1_patterns.json
  ↓
Finds high-confidence pattern (0.85)
  ↓
Auto-applies to all 40 questions ✅
```

**Benefit:** Step 3 leverages Step 1's teacher-approved patterns for auto-fixes.

---

##### Step 3 → Step 1 Learning

**Scenario:**
```
Day 1 - Step 3 Auto-fixes:
Step 3 successfully fixes "missing_separator" 47/48 times
  ↓
Logged to step3_fix_rules.json
{
  "rule_id": "STEP3_001",
  "error_type": "missing_separator",
  "success_rate": 0.98,
  "applied_count": 47
}

Day 2 - Step 1 Session:
Step 1 detects: "Q005 missing separator"
  ↓
Checks step3_fix_rules.json
  ↓
Finds high success rate (98%)
  ↓
Suggests with HIGH confidence:
"This fix worked 47/48 times in auto-mode - highly recommended"
```

**Benefit:** Step 1 AI suggestions become more confident based on Step 3's success data.

---

##### Cross-Learning Log

**New log file:** `logs/cross_learning.jsonl`

**Tracks pattern sharing between components:**
```jsonl
{
  "timestamp": "2026-02-15T10:30:00Z",
  "learning_type": "step1_to_step3",
  "pattern_id": "STEP1_001",
  "description": "Step 3 adopted Step 1 pattern for missing_separator",
  "source_confidence": 0.85,
  "target_component": "step3",
  "first_use": "2026-02-15T10:30:15Z",
  "success_rate_after_adoption": 0.96
}
```

---

##### Pattern Merging Strategy

**When Step 1 and Step 3 have patterns for same error:**

```python
def merge_patterns(step1_pattern, step3_rule):
    """
    Smart merging of patterns from both systems
    """
    merged = {
        "pattern_id": step1_pattern.id,
        "rule_id": step3_rule.id,
        "type": step1_pattern.type,
        "fix": step1_pattern.fix,  # Use Step 1 fix (teacher-approved)
        
        # Combined confidence:
        "confidence": calculate_combined_confidence(
            teacher_approvals=step1_pattern.teacher_approved,
            auto_success_rate=step3_rule.success_rate,
            auto_count=step3_rule.applied_count
        ),
        
        "sources": ["step1", "step3"],
        "merged_at": datetime.now()
    }
    
    return merged
```

**Confidence calculation:**
- Teacher approval carries high weight (human validation)
- Auto-fix success rate provides volume validation
- Combined = More reliable than either alone

---

##### Implementation Plan for Cross-Learning

**Phase 4 (Week 4-5):**
1. Implement cross-learning log structure
2. Step 3 reads step1_patterns.json
3. High-confidence Step 1 patterns (>0.8) usable in Step 3
4. Log all cross-learning events

**Phase 5 (Week 5-6):**
1. Step 1 reads step3_fix_rules.json
2. High success Step 3 rules (>0.9 success rate) inform Step 1 suggestions
3. Pattern merging for conflicts
4. Comprehensive testing of cross-learning

**Success Metrics for Cross-Learning:**
- ✅ Step 3 auto-fix rate increases by 20%+ after reading Step 1 patterns
- ✅ Step 1 suggestion acceptance increases by 15%+ after reading Step 3 rules
- ✅ Overall teacher time reduced by 30%+ through smarter automation

---

## Component Details

### Step 0: Session Setup

**Purpose:** Initialize project structure and session

**Updated Project Structure (RFC-013 v2.1):**

```
/project_name/
├── materials/              # Input (lectures, slides) - M1 reads
├── methodology/            # Method guides (copied in Step 0)
├── preparation/            # M1 + M2 output (foundation for questions)
│   ├── m1_analysis.md
│   └── m2_design.md
├── questions/              # Questions (M3 creates, M4/M5 edit)
│   ├── m3_questions.md
│   ├── m5_output.md       # ← M5 generates here
│   └── history/           # Automatic backups per step
├── pipeline/               # Step 1-3 working area
│   ├── step1_working.md   # Current working file
│   ├── step1_backup_*.md  # Backups at each save
│   └── history/           # Backups
├── output/                 # Final output
│   ├── questions_final.md
│   └── qti/               # QTI packages (.zip)
├── logs/                   # Session logs (shared by both MCPs)
│   ├── session.jsonl
│   ├── m5_decisions.jsonl
│   ├── step1_decisions.jsonl
│   └── step3_iterations.jsonl
├── sources.yaml            # Source tracking (updated by both MCPs)
└── session.yaml            # Session metadata
```

**What Step 0 Does:**

1. Creates all directories (materials, methodology, preparation, questions, pipeline, output, logs)
2. Copies instructional materials to materials/
3. Copies method guides to methodology/
4. Fetches reference documents (kursplan, etc.) to project root
5. Initializes session.yaml and sources.yaml
6. **Auto-registers all materials in sources.yaml** with:
   - File path and type detection (pdf→lecture_slides, docx→document, etc.)
   - Original path and copy timestamp
   - Reference documents registered as type "syllabus"
7. Creates empty logs/ directory

**Session Initialization:**
- Determines entry point (m1/m2/m3/m4/pipeline)
- Sets up appropriate folder structure
- Logs initialization to session.jsonl

---

### M5: Quality Assurance Module

**Location:** `qf-scaffolding` (TypeScript MCP)  
**Purpose:** Ensure all questions have complete content before markdown generation

#### Stage Structure

```
STAGE 0: Introduction
- Explain M5 purpose and process
- Show progress overview
- Set expectations

STAGE 1: Question Iterator  
- Load questions from M3 output
- Navigate: Next/Previous/Jump to ID
- Display progress bar
- Current question preview

STAGE 2: Field Checker
- Get required fields for question type
- Check what's present vs. missing
- Display missing fields to teacher
- Provide context for each field

STAGE 3: Content Dialogue
- For each missing field:
  * AI generates suggestion
  * Teacher can: Accept / Modify / Provide own / Skip
  * Log decision for learning
- Validate field content
- Move to next field

STAGE 4: Question Review
- Display complete question
- Teacher approval gate:
  * Approve → Next question
  * Revise → Back to Stage 3
  * Skip → Mark for later

STAGE 5: Completion
- Save all QA'd questions to markdown
- Generate summary report
- Export to: questions/m5_output.md
- Ready for Step 1
```

#### M5 Output Format

**File:** `questions/m5_output.md`

**Content:** Raw MQG markdown with:
- ✅ All required fields present (question_text, options, feedback, etc.)
- ✅ Complete pedagogical metadata (bloom_level, difficulty, tier)
- ⚠️ May have structural issues (missing separators, syntax errors)
- ⚠️ May have formatting inconsistencies

**Example:**
```markdown
# Q001
^type multiple_choice_single
^identifier Q001
@field: question_text
Vad är artificiell intelligens?
@end_field
@field: options
A) En datorvetenskap som studerar intelligenta agenter
B) En typ av robotar
C) Ett programmeringsspråk
D) En databas
@end_field
@field: correct_answer
A
@end_field
@field: bloom_level
remember
@end_field
@field: feedback.correct
Korrekt! AI är studien av intelligenta agenter.
@end_field
@field: feedback.incorrect
Läs om definitionen av AI i kursmaterialet.
@end_field

# Q002
^type multiple_response
...
```

**Note:** This file goes directly to Step 1 for structural normalization.

---

### Step 1: Interactive Guided Build

**Location:** `qf-pipeline` (Python MCP)  
**Purpose:** Teacher-guided structural normalization

#### Overview

Step 1 transforms M5's raw output into a structurally valid MQG markdown file through an **interactive question-by-question workflow** where the teacher approves every structural change.

**Key Innovations:**
1. **Progress tracking** - YAML frontmatter shows current position
2. **Question-based workflow** - Not pattern-based file manipulation
3. **Teacher approval gates** - Human control over all structural changes
4. **Self-learning** - Builds pattern database from teacher decisions

---

#### Phase 1: Initialization

**What Happens:**

1. **Load M5 output** from `questions/m5_output.md`

2. **Add progress frontmatter** (YAML):
   ```yaml
   ---
   step1_progress:
     session_id: "abc123"
     total_questions: 40
     current_question: 1
     current_question_id: "Q001"
     status: in_progress
     started_at: "2026-01-25T14:30:00Z"
     last_updated: "2026-01-25T14:35:12Z"
     questions_completed: 0
     questions_skipped: 0
     questions_deleted: 0
   ---
   ```

3. **Save to working directory:**
   - File: `pipeline/step1_working.md`
   - Backup: `pipeline/step1_backup_001.md`

4. **Initialize session:**
   - Parse questions into structured format
   - Build question index (Q001, Q002, ...)
   - Detect structural issues per question
   - Ready for teacher interaction

---

#### Phase 2: Question-by-Question Review

**Workflow:**

```
FOR EACH question (Q001, Q002, ..., Q040):
  
  1. DISPLAY question
     - Show complete question
     - Visual separator between questions
  
  2. ANALYZE structural issues
     - Missing separator (---) before/after question
     - Malformed field syntax
     - Incomplete field blocks
     - Junk content (text after question end)
     - Syntax inconsistencies
  
  3. AI SUGGESTS fixes
     - For EACH detected issue:
       * Explain the problem
       * Show proposed fix
       * Explain why this fix is needed
  
  4. TEACHER APPROVAL GATE
     Options:
     ├─ Accept AI suggestion
     │  → Apply fix immediately
     │  → Log as "ai_accepted" (high confidence for learning)
     │  → Move to next issue or question
     │
     ├─ Modify suggestion
     │  → Show AI suggestion
     │  → Teacher provides modified version
     │  → Apply modified fix
     │  → Log as "ai_modified" (medium confidence for learning)
     │
     ├─ Provide own fix
     │  → Teacher writes fix from scratch
     │  → Apply teacher's fix
     │  → Log as "teacher_manual" (learn pattern carefully)
     │
     ├─ Skip this question
     │  → Mark question for later review
     │  → Log as "skipped"
     │  → Continue to next question
     │
     └─ Delete question
        → Confirm deletion
        → Remove question from file
        → Log as "deleted"
        → Continue to next question
  
  5. LOG decision
     - Save to step1_decisions.jsonl
     - Include question_id, issue, fix, decision
     - Capture teacher's reasoning (if provided)
  
  6. UPDATE progress frontmatter
     - Increment current_question
     - Update current_question_id
     - Update questions_completed/skipped/deleted
     - Update last_updated timestamp
     - Save backup to pipeline/
  
  7. NAVIGATE
     - Auto-advance to next question
     - OR teacher can: Previous / Jump to ID / Pause
```

**Example Teacher Interaction:**

```
═══════════════════════════════════════════════════════════
STEP 1: INTERACTIVE GUIDED BUILD
Progress: Question 5/40 [████░░░░░░] 12.5%
═══════════════════════════════════════════════════════════

Current Question: Q005
Lines: 089-112

┌─────────────────────────────────────────────────────────┐
│ 089 # Q005                                              │
│ 090 ^type multiple_choice_single                        │
│ 091 ^identifier Q005                                    │
│ 092 @field: question_text                               │
│ 093 Vad menas med "supervised learning"?                │
│ 094 @end_field                                          │
│ 095 @field: options                                     │
│ 096 A) Lärande med märkt data                           │
│ 097 B) Lärande utan data                                │
│ 098 C) Lärande med omärkt data                          │
│ 099 D) Ingen av ovanstående                             │
│ 100 @end_field                                          │
│ 101 @field: correct_answer                              │
│ 102 A                                                    │
│ 103 @end_field                                          │
│ 104 @field: bloom_level                                 │
│ 105 remember                                            │
│ 106 @end_field                                          │
│ 107 @field: feedback.correct                            │
│ 108 Rätt! Supervised learning använder märkt data.      │
│ 109 @end_field                                          │
│ 110 @field: feedback.incorrect                          │
│ 111 Felaktigt. Läs om supervised learning.              │
│ 112 @end_field                                          │
└─────────────────────────────────────────────────────────┘

STRUCTURAL ISSUES DETECTED:

❌ Issue 1: Missing separator before question
   Line 089: # Q005
   Expected: Line 088 should contain "---"
   
   AI Suggestion:
   Insert "---" at line 088
   
   This ensures proper question separation for the parser.

❌ Issue 2: Missing separator after question
   Line 112: @end_field
   Expected: Line 113 should contain "---"
   
   AI Suggestion:
   Insert "---" at line 113
   
   This marks the end of the question block.

═══════════════════════════════════════════════════════════

How do you want to proceed?

1. Accept all AI suggestions (apply both fixes)
2. Review each suggestion individually
3. Skip this question (mark for later)
4. Delete this question
5. Navigate (Previous/Jump/Pause)

Your choice:
```

---

#### Phase 3: Completion

**When all questions reviewed:**

1. **Remove progress frontmatter**
   - Delete YAML block from top of file
   - File now contains only questions

2. **Final validation check**
   - Verify structural consistency
   - Check for any remaining issues

3. **Generate summary report**
   - Questions processed: 40
   - Questions completed: 35
   - Questions skipped: 3
   - Questions deleted: 2
   - Issues fixed: 87
   - Teacher decisions logged: 87
   - Patterns learned: 12

4. **Save final output**
   - File: `output/step1_complete.md`
   - Includes all structural fixes
   - Ready for Step 2 validation

5. **Archive working files**
   - Move pipeline/ working files to pipeline/history/
   - Preserve all backups
   - Preserve decision log

---

#### MCP Tools for Step 1

**Tool: `step1_start`**

**Purpose:** Initialize Step 1 session

**Parameters:**
- `project_path` (required) - Path to project directory
- `source_file` (optional) - Path to M5 output (default: questions/m5_output.md)

**Returns:**
- Session ID
- Total questions found
- Working file path
- Status

**What it does:**
1. Loads M5 output
2. Adds progress frontmatter
3. Saves to pipeline/step1_working.md
4. Creates initial backup
5. Parses questions
6. Returns session info

---

**Tool: `step1_status`**

**Purpose:** Get current session status

**Parameters:**
- (uses active session)

**Returns:**
- Current question (number and ID)
- Total questions
- Progress percentage
- Questions completed/skipped/deleted
- Time elapsed
- Estimated time remaining

---

**Tool: `step1_next` / `step1_previous` / `step1_jump`**

**Purpose:** Navigate between questions

**Parameters:**
- `direction`: "forward" | "back" | question_id (e.g., "Q007")

**Returns:**
- Current question display
- Detected structural issues
- Progress update

**What it does:**
1. Updates progress frontmatter
2. Loads question at new position
3. Analyzes structural issues
4. Displays question with issues
5. Waits for teacher decision

---

**Tool: `step1_analyze_question`**

**Purpose:** Analyze current question for structural issues

**Parameters:**
- `question_id` (optional) - Specific question to analyze (default: current)

**Returns:**
- List of structural issues
- AI suggestions for each issue
- Explanations

**Issue types detected:**
- `missing_separator_before` - No "---" before question
- `missing_separator_after` - No "---" after question
- `malformed_field_start` - @field: syntax error
- `malformed_field_end` - @end_field syntax error
- `incomplete_field_block` - Field not closed
- `junk_content` - Unexpected text
- `syntax_inconsistency` - Format doesn't match schema

---

**Tool: `step1_apply_fix`**

**Purpose:** Apply a fix based on teacher decision

**Parameters:**
- `question_id` (required)
- `issue_id` (required) - Which issue to fix
- `action` (required): "accept_ai" | "modify" | "manual"
- `fix_content` (optional) - For "modify" or "manual" actions
- `note` (optional) - Teacher's reasoning

**Returns:**
- Success status
- Updated question preview
- Next issue (if any)
- Progress update

**What it does:**
1. Applies the fix to working file
2. Logs decision to step1_decisions.jsonl
3. Learns pattern for future suggestions
4. Creates backup
5. Updates progress frontmatter
6. Moves to next issue or question

---

**Tool: `step1_skip`**

**Purpose:** Skip current question

**Parameters:**
- `question_id` (optional) - Default: current
- `reason` (optional) - Why skipping

**Returns:**
- Next question display
- Progress update

**What it does:**
1. Marks question as skipped
2. Logs skip decision
3. Moves to next question
4. Updates progress frontmatter

---

**Tool: `step1_finish`**

**Purpose:** Complete Step 1 session

**Parameters:**
- (uses active session)

**Returns:**
- Summary report
- Final output file path
- Issues remaining (if any)
- Patterns learned count

**What it does:**
1. Removes progress frontmatter
2. Final validation check
3. Generates summary report
4. Saves to output/step1_complete.md
5. Archives working files
6. Closes session

---

#### Progress Tracking (Frontmatter)

**Purpose:** Track position in long editing sessions for resumability

**Format:** YAML frontmatter at top of working file

**Location:** `pipeline/step1_working.md`

**Structure:**
```yaml
---
step1_progress:
  session_id: "abc123def456"
  total_questions: 40
  current_question: 12
  current_question_id: "Q012"
  status: in_progress
  started_at: "2026-01-25T14:30:00Z"
  last_updated: "2026-01-25T15:47:32Z"
  questions_completed: 11
  questions_skipped: 0
  questions_deleted: 0
  issues_fixed: 28
  teacher_decisions:
    accept_ai: 22
    modify: 4
    manual: 2
  pause_note: null
---
```

**Why YAML for Obsidian?**
- Obsidian natively supports YAML frontmatter
- Won't interfere with Obsidian's metadata
- Can be hidden in Obsidian reading view
- Easy to parse programmatically
- Human-readable

**When is it updated?**
- After every question processed
- After every decision logged
- When session is paused
- Before creating backups

**When is it removed?**
- At Step 1 completion (`step1_finish`)
- Before saving to output/

---

#### Self-Learning System

**Purpose:** Learn from teacher decisions to improve future suggestions

**What is learned:**

1. **Structural patterns**
   - Common separator mistakes
   - Frequent syntax errors
   - Typical field formatting issues

2. **Teacher preferences**
   - How teacher likes to phrase feedback
   - Preferred separator style
   - Formatting conventions

3. **Fix effectiveness**
   - Which AI suggestions are accepted
   - Which need modification
   - Which are rejected

**How patterns are learned:**

```
Teacher Decision → Pattern Extraction → Confidence Scoring → Database

Example:
Teacher accepts AI suggestion to add "---" after @end_field
  ↓
Pattern: "Questions should have '---' after final @end_field"
  ↓
Confidence: 0.8 (high, because teacher accepted)
  ↓
Save to step1_patterns.json
  ↓
Future: Auto-suggest this fix with high confidence
```

**Pattern Database:** `logs/step1_patterns.json`

**Pattern Structure:**
```json
{
  "pattern_id": "STEP1_001",
  "type": "missing_separator_after",
  "description": "Add '---' separator after question end",
  "trigger": "Question ends with @end_field but no separator follows",
  "fix": "Insert '---' on next line",
  "confidence": 0.85,
  "learned_from": 23,
  "success_rate": 0.91,
  "last_updated": "2026-01-25T15:47:32Z"
}
```

**Confidence Levels:**
- `0.9 - 1.0`: Very high - Auto-suggest with strong confidence
- `0.7 - 0.9`: High - Suggest as primary option
- `0.5 - 0.7`: Medium - Suggest with caveat
- `0.0 - 0.5`: Low - Don't auto-suggest, learn more

**Learning Sources:**

1. **Teacher approvals** (Step 1)
   - `accept_ai` → +0.2 confidence
   - `modify` → +0.1 confidence, learn modification
   - `manual` → +0.05 confidence, learn pattern carefully

2. **M5 decisions** (cross-learning)
   - Structural issues fixed in M5 → preventive patterns

3. **Step 3 iterations** (cross-learning)
   - Common auto-fix patterns → suggest in Step 1

**Pattern Sharing:**
- Step 1 → Step 3: "These structural errors are common, expect them"
- Step 3 → Step 1: "These auto-fixes work, suggest them"
- M5 → Step 1: "These structural issues appear often, prevent them"

---

### Step 2: Validation

**Location:** `qf-pipeline` (Python)  
**Purpose:** Validate against MQG schema

**Note:** Validator implemented in RFC-012. Uses `markdown_parser.validate()` - same parser as Step 4. Guarantees: validate pass → export works.

**No major changes from v1.0** - Step 2 remains focused on validation only.

**What it does:**
1. Parse all questions
2. Check against schema v6.5
3. Categorize errors:
   - Structural (syntax)
   - Semantic (missing required fields)
   - Content (pedagogical quality)
4. Generate detailed error report

**Input:** `output/step1_complete.md`  
**Output:** Error report with categories

---

### Step 3: Auto-Fix Iteration Engine (Self-Learning)

**Location:** `qf-pipeline` (Python)  
**Purpose:** Iteratively fix errors until valid OR max iterations

**No major changes from original v2.0 architecture** - Step 3 design remains solid.

**Key Features:**
- Iteration loop (max 10x)
- Error categorization
- Routing logic (back to M5/Step 1 if needed)
- Self-learning from successful fixes
- Pattern database
- Cross-learning with Step 1

**See original v2.0 architecture document for full Step 3 details.**

---

### Step 4: Export (QTI/Canvas)

**Location:** `qf-pipeline` (Python)  
**Purpose:** Generate QTI package for LMS import

**What it does:**
1. Load validated markdown from Step 3
2. Parse questions into QTI format
3. Generate manifest.xml
4. Package as .zip
5. Save to output/qti/

**Input:** Valid MQG markdown  
**Output:** QTI package (.zip)

---

## Logging Infrastructure

### Log Files

**1. Session Log** (`logs/session.jsonl`)
- Existing RFC-001 format
- Timeline of all pipeline events

**2. M5 Decisions** (`logs/m5_decisions.jsonl`)
- Teacher decisions during M5 content dialogue
- AI suggestions accepted/modified/rejected
- Learning data for future M5 sessions

**3. Step 1 Decisions** (`logs/step1_decisions.jsonl` - NEW!)

**Structure:**
```jsonl
{
  "timestamp": "2026-01-25T15:23:11.234Z",
  "session_id": "abc123",
  "question_id": "Q007",
  "issue_id": "missing_separator_after",
  "issue_description": "No separator after question end",
  "line_number": 145,
  "ai_suggestion": {
    "action": "insert",
    "content": "---",
    "location": "line 146",
    "reasoning": "Question should be separated from next"
  },
  "teacher_decision": "accept_ai",
  "applied_fix": {
    "action": "insert",
    "content": "---",
    "location": "line 146"
  },
  "teacher_note": null,
  "time_spent_seconds": 3.2,
  "pattern_learned": "STEP1_002"
}
```

**4. Step 1 Patterns** (`logs/step1_patterns.json` - NEW!)

**Structure:**
```json
{
  "patterns": [
    {
      "pattern_id": "STEP1_001",
      "type": "missing_separator_after",
      "description": "Add '---' separator after question end",
      "trigger": "Question ends with @end_field but no separator follows",
      "fix": "Insert '---' on next line",
      "confidence": 0.85,
      "learned_from": 23,
      "success_rate": 0.91,
      "created_at": "2026-01-20T10:15:00Z",
      "last_updated": "2026-01-25T15:47:32Z",
      "usage_count": 47
    }
  ],
  "metadata": {
    "total_patterns": 15,
    "avg_confidence": 0.78,
    "last_updated": "2026-01-25T15:47:32Z"
  }
}
```

**5. Step 3 Iterations** (`logs/step3_iterations.jsonl`)
- Existing format from original v2.0 architecture
- Track iteration fixes and success rates

**6. Cross-Learning Log** (`logs/cross_learning.jsonl` - NEW!)

**Purpose:** Track how components learn from each other

**Structure:**
```jsonl
{
  "timestamp": "2026-01-25T16:00:00Z",
  "learning_type": "step3_to_step1",
  "pattern_id": "STEP1_008",
  "description": "Step 3 found common error: missing bloom_level field",
  "action": "Create preventive pattern in Step 1",
  "confidence": 0.75,
  "source_data": {
    "step3_iterations": 12,
    "success_rate": 0.92
  }
}
```

---

## Implementation Plan

### Phase 1: Step 0 Update (Week 1)

**Tasks:**
1. Update project structure creator
   - Add pipeline/ directory
   - Update session initialization
2. Update documentation
3. Test with existing projects

**Deliverable:** Updated Step 0 with new folder structure

---

### Phase 2: Step 1 Core (Week 1-2)

**Priority: HIGHEST**

**Tasks:**
1. Progress frontmatter
   - YAML structure
   - Update mechanism
   - Obsidian compatibility testing

2. Question parser
   - Parse into structured questions
   - Handle malformed input
   - Build question index

3. Issue detection
   - Missing separators
   - Syntax errors
   - Malformed fields

**Deliverable:** Core Step 1 functionality without MCP tools

---

### Phase 3: Step 1 MCP Tools (Week 2-3)

**Priority: HIGHEST**

**Tasks:**
1. Implement MCP tools:
   - step1_start
   - step1_status
   - step1_next/previous/jump
   - step1_analyze_question
   - step1_apply_fix
   - step1_skip
   - step1_finish

2. Decision logging system
   - Log to step1_decisions.jsonl
   - Capture teacher reasoning
   - Track time spent

3. Backup system
   - Auto-backup on each decision
   - Preserve working history

**Deliverable:** Complete interactive Step 1 with MCP tools

**Testing:** Process Niklas's 40 ARTI1000X questions

---

### Phase 4: Step 1 Learning System (Week 3-4)

**Priority: HIGH**

**Tasks:**
1. Pattern extraction
   - Learn from teacher decisions
   - Build pattern database
   - Confidence scoring

2. Pattern application
   - Use patterns for AI suggestions
   - Improve suggestion quality
   - Track pattern success rates

3. Cross-learning integration
   - Learn from M5 decisions
   - Share with Step 3
   - Update patterns from Step 3 feedback

**Deliverable:** Self-learning Step 1

**Testing:** Track improvement over 50+ files

---

### Phase 5: Step 3 Integration (Week 4-5)

**Priority: MEDIUM**

**Tasks:**
1. Routing logic
   - Return to Step 1 on structural errors
   - Handle Step 1 output properly
   - Update iteration loop

2. Cross-learning
   - Send patterns to Step 1
   - Receive patterns from Step 1
   - Log cross-learning events

**Deliverable:** Full integration between Step 1 and Step 3

---

### Phase 6: Documentation & Testing (Week 5-6)

**Priority: MEDIUM**

**Tasks:**
1. User documentation
   - Step 1 workflow guide
   - MCP tools reference
   - Troubleshooting guide

2. Comprehensive testing
   - Test with diverse question types
   - Test with malformed input
   - Test resumability (pause/continue)
   - Test pattern learning

3. Performance optimization
   - Optimize question parsing
   - Optimize backup system

**Deliverable:** Production-ready Step 1

---

## Success Metrics

### Step 1: Interactive Guided Build

**Target Metrics:**
- ✅ 100% questions processed with teacher approval
- ✅ <30 seconds per question average
- ✅ 95%+ teacher acceptance of AI suggestions (after learning)
- ✅ 0 structural errors reaching Step 2
- ✅ Session resumable after any interruption

### Learning System

**Target Metrics:**
- ✅ +20% AI suggestion acceptance rate per 10 files processed
- ✅ 80%+ patterns with confidence >0.8 after 20 files
- ✅ 50+ unique patterns learned per month
- ✅ 90%+ pattern accuracy (accepted by teachers)

---

## Migration from v1.0

### For Existing Projects

1. **Update project structure**
   - Add pipeline/ directory
   - Existing projects continue to work
   - Can run Step 1 on old files

2. **New Step 1 workflow**
   - Old Step 1 transform deprecated
   - Use new Interactive Guided Build
   - Teacher required for first run

3. **Pattern database**
   - Starts empty for new users
   - Learns from each project
   - Shared across projects (optional)

### Migration Path

```
Old Project (v1.0)
  ↓
Update folder structure (add pipeline/, questions/, preparation/)
  ↓
Run M5 if content incomplete
  ↓
Run NEW Step 1 Interactive Guided Build
  ↓
Teacher approves structural fixes
  ↓
Step 2 validation
  ↓
Step 3 auto-fix
  ↓
Export to Step 4
  ↓
New Project (v2.0) ✅
```

---

## Key Differences from Original v2.0

### What Changed

**Step 0:**
- ✅ Added pipeline/ directory (replaces 02_working_files/)
- ✅ Renamed folders: materials/, methodology/, preparation/, questions/, output/

**Step 1:**
- ❌ REMOVED: MODE A (automatic normalization)
- ❌ REMOVED: MODE B terminology
- ❌ REMOVED: Pattern-based file manipulation
- ✅ ADDED: Progress frontmatter (YAML)
- ✅ ADDED: Question-by-question workflow
- ✅ ADDED: MCP tools (step1_start, step1_next, etc.)
- ✅ CHANGED: Always teacher-assisted (no auto mode)
- ✅ CHANGED: Works on questions, not patterns

**M5, Step 2, Step 3, Step 4:**
- No major changes (original design was solid)

---

## Open Questions

### For Discussion

1. **Progress Frontmatter Format**
   - YAML confirmed good for Obsidian
   - Should we support alternative formats?
   - Should session_id be auto-generated or user-provided?

2. **Pattern Sharing**
   - Should patterns be project-specific or global?
   - How to handle conflicts between projects?
   - Privacy concerns with shared patterns?

3. **Backup Strategy**
   - How many backups to keep?
   - When to auto-cleanup old backups?
   - Should backups be compressed?

4. **Resumability**
   - What if Claude Desktop crashes mid-session?
   - How to detect and recover from incomplete sessions?
   - Should we have auto-save intervals?

---

## Appendices

### A. Progress Frontmatter Examples

**Session Start:**
```yaml
---
step1_progress:
  session_id: "abc123"
  total_questions: 40
  current_question: 1
  current_question_id: "Q001"
  status: in_progress
  started_at: "2026-01-25T14:30:00Z"
  last_updated: "2026-01-25T14:30:05Z"
  questions_completed: 0
  questions_skipped: 0
  questions_deleted: 0
---
```

**Mid-Session:**
```yaml
---
step1_progress:
  session_id: "abc123"
  total_questions: 40
  current_question: 23
  current_question_id: "Q023"
  status: in_progress
  started_at: "2026-01-25T14:30:00Z"
  last_updated: "2026-01-25T15:47:32Z"
  questions_completed: 22
  questions_skipped: 0
  questions_deleted: 0
  issues_fixed: 58
---
```

**Session Paused:**
```yaml
---
step1_progress:
  session_id: "abc123"
  total_questions: 40
  current_question: 23
  current_question_id: "Q023"
  status: paused
  started_at: "2026-01-25T14:30:00Z"
  last_updated: "2026-01-25T15:50:00Z"
  paused_at: "2026-01-25T15:50:00Z"
  questions_completed: 22
  questions_skipped: 0
  questions_deleted: 0
  pause_note: "Lunch break - resume at Q023"
---
```

---

### B. MCP Tool Call Examples

**Starting a session:**
```typescript
// MCP tool call
step1_start({
  project_path: "/Users/niklas/Projects/ARTI1000X_Entry_Check",
  source_file: "questions/m5_output.md"
})

// Returns
{
  session_id: "abc123",
  total_questions: 40,
  working_file: "pipeline/step1_working.md",
  first_question: {
    id: "Q001",
    lines: "001-024",
    issues_detected: 2
  }
}
```

**Navigating to next question:**
```typescript
// MCP tool call
step1_next({ direction: "forward" })

// Returns
{
  question_id: "Q002",
  question_number: 2,
  total_questions: 40,
  lines: "025-048",
  content: "...",  // Question markdown with line numbers
  issues: [
    {
      issue_id: "missing_separator_before",
      line: 25,
      description: "No separator before question",
      ai_suggestion: "Insert '---' at line 024"
    }
  ],
  progress: {
    current: 2,
    completed: 1,
    remaining: 38,
    percentage: 2.5
  }
}
```

**Applying a fix:**
```typescript
// MCP tool call
step1_apply_fix({
  question_id: "Q002",
  issue_id: "missing_separator_before",
  action: "accept_ai"
})

// Returns
{
  success: true,
  fix_applied: "Inserted '---' at line 024",
  updated_question: "...",  // Updated markdown
  remaining_issues: 0,
  next_action: "advance_to_next_question"
}
```

---

## Appendix A: Error Routing & Categorization

**Added:** 2026-01-27
**Purpose:** Define how Step 2 validation errors are categorized and routed

### Error Categories

Step 2 (`markdown_parser.py`) returns validation errors. Each error is categorized:

| Category | Destination | Description | Human Required? |
|----------|-------------|-------------|-----------------|
| **MECHANICAL** | Step 3 | Syntax/format errors with deterministic fixes | No |
| **SEMANTIC** | Step 1 | Logic errors requiring judgment | Yes |
| **PEDAGOGICAL** | M5 | Content quality issues | Yes |

### Category Definitions

#### MECHANICAL (→ Step 3 Auto-fix)

Errors with **deterministic, rule-based fixes**. No human judgment needed.

```python
MECHANICAL_PATTERNS = [
    # Metadata format
    r"^\^type has colon",           # ^type: → ^type
    r"metadata.*colon",             # Any metadata with colon

    # Separator issues
    r"missing separator",           # Add --- before/after
    r"no separator",

    # Field syntax
    r"@field:.*syntax",             # Malformed @field:
    r"unclosed.*field",             # Missing @end_field
    r"@end_field.*mismatch",

    # Type aliases
    r"unknown.*type.*did you mean", # single_choice → multiple_choice_single

    # Field name corrections (content exists, just wrong name)
    r"multiple_response.*requires correct.?answers",  # @field: answer → @field: correct_answers
    r"true_false.*requires answer",                   # Add @field: answer with existing value
    r"requires.*field.*found.*instead",               # Wrong field name used
]
```

**Example fixes:**
- `^type: multiple_choice` → `^type multiple_choice`
- Missing `---` → Insert separator
- `@field answer` → `@field: answer`
- `@field: answer` (for multiple_response) → `@field: correct_answers`

#### SEMANTIC (→ Step 1 Human)

Errors requiring **human judgment** to fix correctly. AI can suggest, but teacher decides.

```python
SEMANTIC_PATTERNS = [
    # Missing required content (human must provide)
    r"missing.*options",
    r"missing.*answer.*content",
    r"no correct.*option.*marked",
    r"empty.*field",

    # Ambiguous situations
    r"multiple.*correct.*which",
    r"cannot determine.*type",

    # Content validation (not format)
    r"answer.*not in options",
    r"correct.*option.*not found",
]
```

**Why human needed:**
- Content is MISSING - human must provide it
- Ambiguous situation - human must decide

#### PEDAGOGICAL (→ M5)

Content quality issues. Not format errors - **the question content itself is problematic**.

```python
PEDAGOGICAL_PATTERNS = [
    # Distractor quality
    r"distractor.*implausible",
    r"option.*too obvious",

    # Question clarity
    r"ambiguous.*stem",
    r"unclear.*question",

    # Content completeness (should have been caught by M5)
    r"empty.*field",
    r"placeholder.*content",
]
```

**Note:** Most pedagogical issues should be caught by M5 BEFORE reaching pipeline. If they appear in Step 2, route back to M5.

### Routing Logic Implementation

```python
def categorize_error(error_message: str) -> str:
    """
    Categorize validation error for routing.

    Returns: "mechanical" | "semantic" | "pedagogical"
    """
    msg_lower = error_message.lower()

    # Check mechanical first (most specific)
    for pattern in MECHANICAL_PATTERNS:
        if re.search(pattern, msg_lower):
            return "mechanical"

    # Check semantic
    for pattern in SEMANTIC_PATTERNS:
        if re.search(pattern, msg_lower):
            return "semantic"

    # Check pedagogical
    for pattern in PEDAGOGICAL_PATTERNS:
        if re.search(pattern, msg_lower):
            return "pedagogical"

    # Default: semantic (safer - human reviews)
    return "semantic"
```

### Routing Tool: `pipeline_route`

Step 2 returnerar text som nu. En **separat router** kategoriserar och dirigerar:

```python
# MCP Tool: pipeline_route
async def pipeline_route(validation_report: str) -> dict:
    """
    Parse Step 2 validation output and route errors.

    Args:
        validation_report: Text output from step2_validate

    Returns:
        {
            "valid": bool,
            "errors": {
                "mechanical": [{"question_id": "...", "message": "..."}],
                "semantic": [...],
                "pedagogical": [...]
            },
            "destination": "step1" | "step3" | "step4" | "m5",
            "reason": "2 semantic error(s) → Step 1 human review"
        }
    """
```

**Användning:**
```
1. step2_validate → returnerar text rapport
2. pipeline_route → kategoriserar, returnerar destination
3. Användaren/Claude följer destination
```

### Pipeline Flow with Routing

```
Step 2 validates → Categorizes errors
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   pedagogical      semantic       mechanical
        ↓               ↓               ↓
      → M5          → Step 1        → Step 3
   (exit pipeline)  (human fix)    (auto-fix)
                        ↓               ↓
                        └───────┬───────┘
                                ↓
                        Step 2 (validate again)
                                ↓
                        0 errors? → Step 4 Export
```

### Self-Learning Integration

When Step 1 fixes a SEMANTIC error with human confirmation:
1. Log the fix pattern
2. If pattern seen 5+ times with same fix → Promote to MECHANICAL
3. Add to Step 3 auto-fix rules

```python
# Example: After 5 teachers all accept "answer → correct_answers" for multiple_response
{
    "rule_id": "GRADUATED_001",
    "origin": "step1_pattern_STEP1_007",
    "error_pattern": "multiple_response.*requires correct.?answers",
    "fix_function": "rename_field_answer_to_correct_answers",
    "confidence": 0.95,
    "graduated_at": "2026-01-27T12:00:00Z",
    "learned_from": 5
}
```

### Current Implementation Status

| Component | Status | File |
|-----------|--------|------|
| `step2_validate` | ✅ EXISTS | `server.py` |
| `pipeline_route` tool | ❌ TODO | `server.py` |
| `categorize_error()` | ❌ TODO | `routing.py` (new) |
| Step 1 + markdown_parser | ❌ TODO | `step1_tools.py` |
| Step 3 mechanical fixes | ✅ EXISTS | `step3_autofix.py` |
| Pattern graduation | ❌ TODO | `patterns.py` |

---

## Document Changelog

**v2.2 - 2026-01-27**
- Added Appendix A: Error Routing & Categorization
- Detailed MECHANICAL vs SEMANTIC vs PEDAGOGICAL definitions
- Added pattern-based categorization rules
- Added self-learning graduation from Step 1 → Step 3

**v2.1 - 2026-01-25 (This RFC-013)**
- Complete rewrite of Step 1
- Removed line numbering system (over-engineering - Question IDs sufficient)
- Added progress frontmatter (YAML)
- Removed MODE A/B terminology
- Changed to question-by-question workflow
- Added MCP tools specification
- Updated Step 0 folder structure
- Fixed question type names (multiple_choice_single not multiple_choice_question)
- Added RFC-012 reference
- No changes to M5, Step 2, Step 3, Step 4

**v2.0-rev1 - 2026-01-24**
- Original v2.0 architecture
- M5 before generation
- Self-learning Step 1 and Step 3
- Pattern-based approach

---

**END OF RFC-013**