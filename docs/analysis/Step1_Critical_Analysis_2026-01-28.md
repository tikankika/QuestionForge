# Step 1 Critical Analysis

**Date:** 2026-01-28
**Status:** 70-75% Implemented
**Verdict:** Production-ready for TESTING, NOT for real use without fixes

---

## Executive Summary

RFC-013 Step 1 is SUBSTANTIALLY IMPLEMENTED but with GAPS and CONTRADICTIONS to specification.

- **RFC Specifies:** 2000+ line architecture for teacher-driven interactive build
- **Actually Implemented:** ~3000 lines of code delivering MOST core features
- **Critical Gaps:** Delete missing, per-issue granularity incomplete, counters broken

---

## What WORKS

| Component | Status | Notes |
|-----------|--------|-------|
| Session Initialization | ✅ | Frontmatter, parsing, format detection |
| Navigation | ✅ | next/prev/jump all work |
| Issue Detection | ✅ | 11 structural issue types |
| Pattern Learning | ✅ | Confidence, persistence, reuse |
| Decision Logging | ✅ | JSONL format, all events |
| Session Completion | ✅ | Remove frontmatter, archive, summary |

---

## Critical Issues

### 1. DELETE Not Implemented ❌

**RFC Spec (line 869):**
```
Teacher approval options:
├─ Accept AI suggestion
├─ Modify suggestion
├─ Provide own fix
├─ Skip
└─ Delete question  ← NOT IMPLEMENTED
```

**Impact:** Teacher cannot remove bad questions - must manually edit file.

**Fix:** Add "delete" action to `step1_apply_fix()`, implement removal logic.

---

### 2. Per-Question vs Per-Issue Workflow ⚠️

**RFC Spec (lines 827-889):**
```
FOR EACH question:
  FOR EACH detected issue:
    → AI suggests fix
    → Teacher approves/modifies/rejects
    → Log decision
```

**Actual Implementation:**
```python
if action == "accept_ai":
    new_content, changes = transformer.apply_all_auto(question.raw_content)
    # ^^^ Applies ALL auto-fixes at once!
```

**Impact:** Teacher can't granularly approve each issue separately.

**Fix:** Modify `accept_ai` to apply single issue based on `issue_type` parameter.

---

### 3. Progress Counter Bug ⚠️

**RFC Spec:**
```yaml
step1_progress:
  questions_completed: 0  # Should increment on fix
  questions_skipped: 0    # Increments on skip ✅
  questions_deleted: 0    # Should increment on delete
```

**Actual:** `questions_completed` is NEVER incremented. Always stays 0.

**Impact:** Progress tracking is broken - percentage always wrong.

**Fix:** Increment counter in `step1_apply_fix()` when fix succeeds.

---

### 4. No Final Validation ⚠️

**RFC Spec (line 965-995):**
```
Phase 3: Completion
1. Remove frontmatter
2. Final validation check  ← NOT IMPLEMENTED
3. Generate summary
4. Save output
```

**Impact:** Could pass malformed questions to Step 2.

**Fix:** Add `detect_structural_issues()` call in `step1_finish()`.

---

## Module Structure

```
/step1/
├── __init__.py          (210 lines) - Exports
├── analyzer.py          (414 lines) - Question analysis (legacy)
├── detector.py          (88 lines)  - Format detection
├── parser.py            (167 lines) - Parse questions
├── session.py           (137 lines) - Session state
├── transformer.py       (616 lines) - Auto-fix transforms
├── prompts.py           (193 lines) - Prompt generation
├── frontmatter.py       (191 lines) - YAML frontmatter ✅
├── patterns.py          (467 lines) - Pattern learning ✅
├── structural_issues.py (347 lines) - Issue detection ✅
└── decision_logger.py   (159 lines) - Decision logging ✅
```

**Total:** ~3,000 lines

---

## MCP Tools Status

| Tool | Status | Notes |
|------|--------|-------|
| `step1_start` | ✅ | Initializes session, creates frontmatter |
| `step1_status` | ✅ | Returns progress from frontmatter |
| `step1_next` | ✅ | Navigate to next question |
| `step1_previous` | ✅ | Navigate to previous question |
| `step1_jump` | ✅ | Jump to specific question ID |
| `step1_analyze_question` | ✅ | Detects structural issues |
| `step1_apply_fix` | ⚠️ | Works but missing delete, per-issue |
| `step1_skip` | ✅ | Skip question, update counter |
| `step1_finish` | ⚠️ | Works but no final validation |

---

## Completeness by Area

| Area | RFC | Implemented | % |
|------|-----|-------------|---|
| Phases (3) | 3 | 3 | 100% |
| MCP Tools (7) | 7 | 7 | 100% |
| Frontmatter Fields | 8 | 8 | 100% |
| Issue Detection Types | 11 | 11 | 100% |
| Pattern Learning | Full | Full | 100% |
| Teacher Approvals | 5 options | 4 options | 80% |
| Progress Counters | 5 | 3 working | 60% |
| Issue Granularity | Per-issue | Per-question | 50% |
| Cross-Learning | Phase 4-5 | Not impl | 0% |

**Overall: 70-75%**

---

## Contradictions: RFC vs Implementation

### Contradiction 1: Issue Categorization

**RFC-013 Updates (Decision 7):**
> "Structural" is RELATIVE - depends on whether Step 3 has pattern

**Implementation:** Fixed list of STRUCTURAL_ISSUE_TYPES (static, not learned).

**Impact:** Cannot learn which issues Step 3 has learned to auto-fix.

---

### Contradiction 2: Skip Tracking

**RFC-013 Updates (Decision 10):**
> Skipped issues should NOT be shared to Step 3

**Implementation:** Skip is question-level, not issue-level. No `skip_reason` mapped to specific issue type.

**Impact:** Step 3 can't know what was skipped.

---

### Contradiction 3: Pattern Confidence Penalization

**RFC (lines 1259-1263):**
```
Confidence Levels:
- 0.9 - 1.0: Very high - Auto-suggest
- 0.7 - 0.9: High - Primary option
- 0.5 - 0.7: Medium - Suggest with caveat
- 0.0 - 0.5: Low - Don't auto-suggest
```

**Implementation:**
```python
weighted_score = (
    self.teacher_accepted * 1.0 +
    self.teacher_modified * 0.5 +
    self.teacher_manual * 0.1  # ← Very low!
)
```

**Problem:** 1 manual decision out of 3 drops confidence to 0.53 → below threshold.

**Impact:** Patterns may become unusable if teacher provides manual fixes.

---

## Recommendations

### Immediate Fixes (Before Production)

| # | Fix | Priority | Time |
|---|-----|----------|------|
| 1 | Implement DELETE action | 🔴 CRITICAL | 2-3h |
| 2 | Fix accept_ai to per-issue | 🔴 HIGH | 3-4h |
| 3 | Fix questions_completed counter | 🟠 MEDIUM | 1h |
| 4 | Add final validation | 🟠 MEDIUM | 2h |

**Total: 8-10 hours**

### Near-Term Improvements

| # | Fix | Priority | Time |
|---|-----|----------|------|
| 5 | Expose teacher notes in UI | 🟡 LOW-MED | 1-2h |
| 6 | Add pause/resume capability | 🟡 LOW-MED | 2-3h |
| 7 | Add session locking | 🟡 MEDIUM | 2h |

### Future (Phase 4-5)

| # | Feature | Notes |
|---|---------|-------|
| 8 | Step 1 ↔ Step 3 cross-learning | Share patterns |
| 9 | Pattern graduation | Step 3 success → Step 1 learns |

---

## Conclusion

Step 1 has a **solid foundation** with working:
- Session management
- Issue detection
- Pattern learning
- Decision logging

But is **NOT production-ready** without fixing:
1. DELETE functionality
2. Per-issue granularity
3. Progress counters
4. Final validation

**Estimated fix time:** 8-10 hours

---

## Files Analyzed

- `packages/qf-pipeline/src/qf_pipeline/step1/*.py` (10 modules)
- `packages/qf-pipeline/src/qf_pipeline/tools/step1_tools.py` (947 lines)
- `docs/rfcs/RFC-013-Questionforge pipeline architecture v2.md`
- `docs/rfcs/RFC-013-updates-for-desktop.md`
