# ADR-012: Validation Output Improvement

**Status:** Accepted ✅  
**Date:** 2026-01-07  
**Deciders:** Niklas  
**Context:** qf-pipeline step2_validate output quality  
**Priority:** 🟡 Medium

---

## Context

Current `step2_validate` output is significantly worse than Terminal QTI-Generator, making it hard for teachers to identify and fix validation errors.

### Current qf-pipeline Output

```
Invalid: /path/to/file.md
  Fragor: 27
  [ERROR] Missing ^labels field (rad ?)
  [ERROR] Missing ^labels field (rad ?)
  [ERROR] Match pairs must use inline format (rad ?)
```

### Terminal QTI-Generator Output

```
================================================================================
MQG FORMAT VALIDATION REPORT (v6.5)
================================================================================

❌ ERRORS FOUND:

Question 1 (BIOG_FYS_Q001):
  Missing ^labels field

Question 2 (BIOG_FYS_Q002):
  Missing ^labels field

Question 13 (BIOG_FYS_Q013):
  Match pairs must use inline format: "1. X → Y" (table format not supported)

================================================================================
SUMMARY
================================================================================
Total Questions: 27
✅ Valid: 25
❌ Errors: 29
⚠️  Warnings: 0

STATUS: ❌ NOT READY - Fix 29 error(s) before QTI generation
```

---

## Problems Identified

### 1. No Question Grouping
- Errors shown as flat list
- Can't see which question has which error
- Multiple errors per question not grouped

### 2. No Question ID
- No "Question 1 (BIOG_FYS_Q001):" prefix
- Teacher can't find the question in file

### 3. No Summary
- No total/valid/error/warning counts
- No clear "READY" or "NOT READY" status

### 4. Line Numbers Don't Work
- Always shows "(rad ?)"
- `line_num` not populated from validator

### 5. 🔴 BUG: Case Mismatch
```python
# wrappers/validator.py returns:
"level": getattr(i, "level", "ERROR")  # UPPERCASE

# server.py checks:
if i.get("level") == "error"  # lowercase
```
**Error count is ALWAYS ZERO due to case mismatch!**

### 6. No Persistent Output
- Output only shown in Claude chat
- Not saved to file
- Can't review later

---

## Decision

### Fix the output to match Terminal quality

#### 1. Fix Case Mismatch (BUG)

```python
# In server.py, change to uppercase:
error_count = sum(1 for i in result.get("issues", []) if i.get("level") == "ERROR")
warning_count = sum(1 for i in result.get("issues", []) if i.get("level") == "WARNING")
```

#### 2. Group Errors by Question

```python
def format_validation_output(result: dict, file_path: str) -> str:
    """Format validation result like Terminal QTI-Generator."""
    lines = [
        "=" * 60,
        "MQG FORMAT VALIDATION REPORT (v6.5)",
        "=" * 60,
        ""
    ]
    
    if not result["valid"]:
        lines.append("❌ ERRORS FOUND:\n")
        
        # Group by question
        by_question = {}
        for issue in result["issues"]:
            q_num = issue.get("question_num", 0)
            q_id = issue.get("question_id", "?")
            key = (q_num, q_id)
            if key not in by_question:
                by_question[key] = []
            by_question[key].append(issue)
        
        # Output grouped
        for (q_num, q_id), issues in sorted(by_question.items()):
            lines.append(f"Question {q_num} ({q_id}):")
            for issue in issues:
                lines.append(f"  {issue['message']}")
            lines.append("")
    
    # Summary
    lines.extend([
        "=" * 60,
        "SUMMARY",
        "=" * 60,
        f"Total Questions: {result.get('total_questions', '?')}",
        f"✅ Valid: {result.get('valid_questions', '?')}",
        f"❌ Errors: {error_count}",
        f"⚠️  Warnings: {warning_count}",
        "",
    ])
    
    if result["valid"]:
        lines.append("STATUS: ✅ READY FOR QTI GENERATION")
    else:
        lines.append(f"STATUS: ❌ NOT READY - Fix {error_count} error(s)")
    
    return "\n".join(lines)
```

#### 3. Save Report to File (Optional)

```python
# Save validation report to session folder
if session:
    report_path = session.project_path / "validation_report.txt"
    with open(report_path, 'w') as f:
        f.write(formatted_output)
```

---

## Implementation

### Files to Modify

| File | Change |
|------|--------|
| `server.py` | Fix case mismatch, add `format_validation_output()` |
| `wrappers/validator.py` | Ensure question_num and question_id populated |

### New Output Format

```
============================================================
MQG FORMAT VALIDATION REPORT (v6.5)
============================================================

❌ ERRORS FOUND:

Question 1 (BIOG_FYS_Q001):
  Missing ^labels field

Question 2 (BIOG_FYS_Q002):
  Missing ^labels field

Question 13 (BIOG_FYS_Q013):
  Match pairs must use inline format: "1. X → Y" (table format not supported)
  Missing ^labels field

============================================================
SUMMARY
============================================================
Total Questions: 27
✅ Valid: 24
❌ Errors: 29
⚠️  Warnings: 0

STATUS: ❌ NOT READY - Fix 29 error(s) before QTI generation

Report saved to: /path/to/project/validation_report.txt
```

---

## Consequences

### Positive
- Teachers can easily find which question has errors
- Clear summary shows overall status
- Matches familiar Terminal output
- Optional file save enables later review

### Negative
- Longer output in Claude chat
- Requires code changes in server.py

### Neutral
- Same underlying validation logic
- Just presentation layer change

---

## Testing

```python
def test_case_sensitivity():
    """Ensure ERROR/WARNING levels counted correctly."""
    result = {"issues": [
        {"level": "ERROR", "message": "test"},
        {"level": "WARNING", "message": "test2"},
    ]}
    error_count = sum(1 for i in result["issues"] if i.get("level") == "ERROR")
    assert error_count == 1

def test_grouping_by_question():
    """Ensure errors grouped by question."""
    # ... test grouped output format
```

---

## Priority

🔴 **BUG FIX (case mismatch):** Immediate  
🟡 **Output formatting:** Medium  
🟢 **File save:** Low (nice to have)

---

*ADR-012 | QuestionForge | 2026-01-07*
