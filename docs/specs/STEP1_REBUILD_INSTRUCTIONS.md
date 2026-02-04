# STEP 1 REBUILD INSTRUCTIONS

**For:** Code/Developer  
**Version:** 2.0 (Interactive Rebuild)  
**Date:** 2026-01-08  
**Status:** Refactoring of existing code

---

## SUMMARY

Existing code in `step1/` has all building blocks but `step1_tools.py` uses them incorrectly.

**Problem:** `step1_transform()` runs all transforms on all questions without user interaction.

**Solution:** Change tools to return "needs_input" to Claude, which asks the user.

---

## EXISTING CODE - KEEP

| File | Status | Comment |
|------|--------|---------|
| `session.py` | ✅ KEEP | Works well |
| `detector.py` | ✅ KEEP | Works well |
| `parser.py` | ✅ KEEP | Works well |
| `analyzer.py` | ✅ KEEP | Has `prompt_key` - needed! |
| `transformer.py` | ✅ KEEP | All transforms work |
| `prompts.py` | ✅ KEEP | Has everything - start USING it! |

---

## CHANGE: step1_tools.py

### Current tools (WRONG):

```python
step1_start()      # OK but message is wrong
step1_status()     # OK
step1_analyze()    # OK but not used correctly
step1_transform()  # ❌ WRONG - Runs everything without questions
step1_next()       # OK
step1_preview()    # OK  
step1_finish()     # OK
```

### New/Changed tools (CORRECT):

```python
step1_start()          # Change message
step1_status()         # Keep
step1_analyze()        # Change return format
step1_fix_auto()       # NEW - Only auto-fixable
step1_fix_manual()     # NEW - One fix at a time
step1_suggest()        # NEW - Generate suggestions
step1_batch_preview()  # NEW - Show similar questions
step1_batch_apply()    # NEW - Apply to multiple
step1_skip()           # NEW - Skip issue
step1_next()           # Keep
step1_preview()        # Keep
step1_finish()         # Keep
```

---

## IMPLEMENTATION DETAILS

### 1. CHANGE `step1_start()`

```python
async def step1_start(...) -> Dict[str, Any]:
    # ... existing code ...
    
    # CHANGE return message:
    return {
        # ... existing fields ...
        
        # NEW: Instruction to Claude about how the process works
        "instruction": (
            "Step 1 is interactive. For each question:\n"
            "1. Run step1_analyze() to see issues\n"
            "2. Run step1_fix_auto() for automatic fixes\n"
            "3. For issues with 'needs_input': ask the user\n"
            "4. Run step1_fix_manual() with the user's answer\n"
            "5. Run step1_next() for the next question"
        ),
        
        # NEW: First question ready for analysis
        "next_action": "step1_analyze"
    }
```

### 2. CHANGE `step1_analyze()`

Return issues categorised:

```python
async def step1_analyze(question_id: Optional[str] = None) -> Dict[str, Any]:
    # ... existing code to find question and analyse ...
    
    issues = analyze_question(question.raw_content, question.detected_type)
    
    # NEW: Categorise issues
    auto_fixable = [i for i in issues if i.auto_fixable]
    needs_input = [i for i in issues if not i.auto_fixable and i.prompt_key]
    
    return {
        "question_id": target_id,
        "question_type": question.detected_type,
        "question_preview": question.raw_content[:200] + "...",
        
        # NEW: Separated categories
        "auto_fixable": [
            {
                "id": idx,
                "message": i.message,
                "transform_id": i.transform_id
            }
            for idx, i in enumerate(auto_fixable)
        ],
        
        "needs_input": [
            {
                "id": idx,
                "field": i.field,
                "message": i.message,
                "prompt_key": i.prompt_key,
                "current_value": i.current_value,
                # NEW: Include prompt info so Claude can ask
                "prompt": get_prompt(i.prompt_key) if i.prompt_key else None
            }
            for idx, i in enumerate(needs_input)
        ],
        
        # NEW: Instruction to Claude
        "instruction": (
            f"{len(auto_fixable)} auto-fixable (run step1_fix_auto), "
            f"{len(needs_input)} need input (ask the user)"
        )
    }
```

### 3. NEW: `step1_fix_auto()`

Apply ONLY automatic transforms, return remaining:

```python
async def step1_fix_auto(question_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Apply only auto-fixable transforms on a question.
    
    Returns:
        fixed: List of what was fixed
        remaining: Issues that require input
    """
    if not _step1_session:
        return {"error": "No active session"}
    
    # Read file and find question
    working_path = Path(_step1_session.working_file)
    content = working_path.read_text(encoding='utf-8')
    questions = parse_file(content)
    
    target_id = question_id or _step1_session.questions[_step1_session.current_index].question_id
    question = get_question_by_id(questions, target_id)
    
    if not question:
        return {"error": f"Question not found: {target_id}"}
    
    # Apply transforms
    new_content, changes = transformer.apply_all_auto(question.raw_content)
    
    if changes:
        # Update file
        full_content = content.replace(question.raw_content, new_content)
        working_path.write_text(full_content, encoding='utf-8')
        
        # Log changes
        for change_desc in changes:
            _step1_session.add_change(
                question_id=target_id,
                field='auto',
                old_value=None,
                new_value=change_desc,
                change_type='auto'
            )
    
    # Analyse again to see what remains
    # Read updated version
    updated_content = working_path.read_text(encoding='utf-8')
    updated_questions = parse_file(updated_content)
    updated_question = get_question_by_id(updated_questions, target_id)
    
    remaining_issues = analyze_question(updated_question.raw_content, updated_question.detected_type)
    needs_input = [i for i in remaining_issues if not i.auto_fixable and i.prompt_key]
    
    return {
        "question_id": target_id,
        "fixed": changes,
        "fixed_count": len(changes),
        
        # What remains and requires input
        "remaining": [
            {
                "field": i.field,
                "message": i.message,
                "prompt_key": i.prompt_key,
                "prompt": get_prompt(i.prompt_key) if i.prompt_key else None
            }
            for i in needs_input
        ],
        "remaining_count": len(needs_input),
        
        # Instruction to Claude
        "instruction": (
            f"Fixed {len(changes)} auto-issues. "
            f"{len(needs_input)} require user input."
            if needs_input else
            "All issues fixed! Run step1_next() for the next question."
        )
    }
```

### 4. NEW: `step1_fix_manual()`

Apply a manual fix based on user input:

```python
async def step1_fix_manual(
    question_id: str,
    field: str,
    value: str
) -> Dict[str, Any]:
    """
    Apply a manual fix from user input.
    
    Args:
        question_id: Question ID
        field: Field to update (e.g., "bloom", "difficulty", "partial_feedback")
        value: Value from user
        
    Returns:
        Confirmation of change
    """
    if not _step1_session:
        return {"error": "No active session"}
    
    working_path = Path(_step1_session.working_file)
    content = working_path.read_text(encoding='utf-8')
    questions = parse_file(content)
    
    question = get_question_by_id(questions, question_id)
    if not question:
        return {"error": f"Question not found: {question_id}"}
    
    new_content = question.raw_content
    
    # Handle different types of fixes
    if field == "bloom":
        # Add Bloom level to ^tags
        new_content = _add_to_tags(new_content, f"#{value}")
        
    elif field == "difficulty":
        # Add difficulty to ^tags
        new_content = _add_to_tags(new_content, f"#{value}")
        
    elif field == "partial_feedback":
        # Add partial_feedback subfield
        new_content = _add_feedback_subfield(new_content, "partial_feedback", value)
        
    elif field == "correct_answers":
        # Add correct_answers for multiple_response
        new_content = _add_correct_answers(new_content, value)
        
    else:
        return {"error": f"Unknown field: {field}"}
    
    # Update file
    full_content = content.replace(question.raw_content, new_content)
    working_path.write_text(full_content, encoding='utf-8')
    
    # Log change
    _step1_session.add_change(
        question_id=question_id,
        field=field,
        old_value=None,
        new_value=value,
        change_type='user_input'
    )
    
    return {
        "question_id": question_id,
        "field": field,
        "value": value,
        "success": True,
        "message": f"Updated {field} for {question_id}"
    }


def _add_to_tags(content: str, tag: str) -> str:
    """Add tag to ^tags line."""
    import re
    match = re.search(r'(\^tags\s+.+)$', content, re.MULTILINE)
    if match:
        old_tags = match.group(1)
        new_tags = f"{old_tags} {tag}"
        return content.replace(old_tags, new_tags)
    return content


def _add_feedback_subfield(content: str, subfield_name: str, value: str) -> str:
    """Add a feedback subfield."""
    # Find @field: feedback ... @end_field
    import re
    
    # Find last @@end_field before @end_field for feedback
    pattern = r'(@@field: \w+_feedback\n.*?@@end_field)\n(@end_field)'
    
    replacement = f'\\1\n\n@@field: {subfield_name}\n{value}\n@@end_field\n\\2'
    return re.sub(pattern, replacement, content, flags=re.DOTALL)


def _add_correct_answers(content: str, answers: str) -> str:
    """Add correct_answers section for multiple_response."""
    # Implementation depends on exact format
    pass
```

### 5. NEW: `step1_suggest()`

Generate suggestion for a field:

```python
async def step1_suggest(
    question_id: str,
    field: str
) -> Dict[str, Any]:
    """
    Generate suggestion for a field based on context.
    
    Args:
        question_id: Question ID
        field: Field to suggest value for
        
    Returns:
        Suggestion that user can accept/modify
    """
    if not _step1_session:
        return {"error": "No active session"}
    
    working_path = Path(_step1_session.working_file)
    content = working_path.read_text(encoding='utf-8')
    questions = parse_file(content)
    
    question = get_question_by_id(questions, question_id)
    if not question:
        return {"error": f"Question not found: {question_id}"}
    
    suggestion = None
    
    if field == "partial_feedback":
        # Copy from correct_feedback
        import re
        match = re.search(r'@@field: correct_feedback\n(.*?)@@end_field', 
                         question.raw_content, re.DOTALL)
        if match:
            suggestion = match.group(1).strip()
    
    elif field == "bloom":
        # Guess based on question type
        if question.detected_type == 'text_entry':
            suggestion = "Remember"
        elif question.detected_type == 'multiple_response':
            suggestion = "Understand"
        else:
            suggestion = "Understand"
    
    elif field == "difficulty":
        suggestion = "Medium"  # Default
    
    return {
        "question_id": question_id,
        "field": field,
        "suggestion": suggestion,
        "options": [
            ("accept", "Accept suggestion"),
            ("modify", "Modify"),
            ("skip", "Skip")
        ],
        "instruction": f"Suggestion for {field}: '{suggestion}'. Accept, modify, or skip?"
    }
```

### 6. NEW: `step1_batch_preview()`

Show questions with the same issue:

```python
async def step1_batch_preview(issue_type: str) -> Dict[str, Any]:
    """
    Show all questions with the same type of issue.
    
    Args:
        issue_type: E.g., "missing_partial_feedback", "missing_bloom"
        
    Returns:
        List of affected questions with preview
    """
    if not _step1_session:
        return {"error": "No active session"}
    
    working_path = Path(_step1_session.working_file)
    content = working_path.read_text(encoding='utf-8')
    questions = parse_file(content)
    
    affected = []
    
    for q in questions:
        issues = analyze_question(q.raw_content, q.detected_type)
        for issue in issues:
            if _matches_issue_type(issue, issue_type):
                affected.append({
                    "question_id": q.question_id,
                    "title": q.title,
                    "preview": q.raw_content[:100] + "..."
                })
                break
    
    return {
        "issue_type": issue_type,
        "count": len(affected),
        "questions": affected[:5],  # Show max 5 as preview
        "all_ids": [a["question_id"] for a in affected],
        "instruction": (
            f"{len(affected)} questions have the same problem. "
            "Do you want to apply the same fix to all?"
        ),
        "options": [
            ("all", f"Apply to all {len(affected)}"),
            ("select", "Let me choose which ones"),
            ("one", "Just the current question")
        ]
    }


def _matches_issue_type(issue, issue_type: str) -> bool:
    """Check if issue matches type."""
    type_mapping = {
        "missing_partial_feedback": lambda i: "partial_feedback" in i.message.lower(),
        "missing_bloom": lambda i: "bloom" in i.message.lower(),
        "missing_difficulty": lambda i: "difficulty" in i.message.lower(),
        "missing_correct_answers": lambda i: "correct_answers" in i.message.lower(),
    }
    check = type_mapping.get(issue_type)
    return check(issue) if check else False
```

### 7. NEW: `step1_batch_apply()`

Apply the same fix to multiple questions:

```python
async def step1_batch_apply(
    issue_type: str,
    fix_type: str,
    question_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Apply the same fix to multiple questions.
    
    Args:
        issue_type: E.g., "missing_partial_feedback"
        fix_type: E.g., "copy_from_correct", "add_bloom_remember"
        question_ids: Specific questions, or None for all
        
    Returns:
        Result of batch operation
    """
    if not _step1_session:
        return {"error": "No active session"}
    
    working_path = Path(_step1_session.working_file)
    content = working_path.read_text(encoding='utf-8')
    
    # Find affected questions
    if question_ids is None:
        # Find all with this issue
        preview = await step1_batch_preview(issue_type)
        question_ids = preview.get("all_ids", [])
    
    success = []
    failed = []
    
    for qid in question_ids:
        try:
            # Apply fix depending on type
            if issue_type == "missing_partial_feedback" and fix_type == "copy_from_correct":
                result = await step1_suggest(qid, "partial_feedback")
                if result.get("suggestion"):
                    await step1_fix_manual(qid, "partial_feedback", result["suggestion"])
                    success.append(qid)
                else:
                    failed.append(qid)
            
            elif issue_type == "missing_bloom":
                await step1_fix_manual(qid, "bloom", fix_type.replace("add_bloom_", "").capitalize())
                success.append(qid)
            
            # ... more fix types ...
            
        except Exception as e:
            failed.append(qid)
    
    # Log batch change
    _step1_session.add_change(
        question_id="BATCH",
        field=issue_type,
        old_value=None,
        new_value=f"Fixed {len(success)} questions",
        change_type="batch"
    )
    
    return {
        "issue_type": issue_type,
        "fix_type": fix_type,
        "success": success,
        "success_count": len(success),
        "failed": failed,
        "failed_count": len(failed),
        "message": f"Fixed {len(success)} of {len(question_ids)} questions"
    }
```

### 8. NEW: `step1_skip()`

Skip an issue:

```python
async def step1_skip(
    question_id: Optional[str] = None,
    issue_field: Optional[str] = None,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Skip an issue or entire question.
    
    Args:
        question_id: Question ID (default: current)
        issue_field: Specific field to skip (None = skip entire question)
        reason: Reason
        
    Returns:
        Confirmation
    """
    if not _step1_session:
        return {"error": "No active session"}
    
    target_id = question_id or _step1_session.questions[_step1_session.current_index].question_id
    
    if issue_field:
        # Skip specific issue
        _step1_session.add_change(
            question_id=target_id,
            field=f"skip_{issue_field}",
            old_value=None,
            new_value=reason or "User skipped",
            change_type="skip"
        )
        
        # Update question status
        q_status = next((q for q in _step1_session.questions if q.question_id == target_id), None)
        if q_status:
            q_status.issues_skipped += 1
        
        return {
            "question_id": target_id,
            "skipped_field": issue_field,
            "reason": reason,
            "message": f"Skipped {issue_field} for {target_id}"
        }
    else:
        # Skip entire question
        _step1_session.mark_current_skipped(reason)
        
        return {
            "question_id": target_id,
            "skipped": True,
            "reason": reason,
            "message": f"Skipped entire {target_id}",
            "next_action": "step1_next"
        }
```

---

## UPDATED TOOL REGISTRATIONS

```python
STEP1_TOOLS = [
    {
        "name": "step1_start",
        "description": "Start Step 1 interactive session.",
    },
    {
        "name": "step1_status",
        "description": "Show session status.",
    },
    {
        "name": "step1_analyze",
        "description": "Analyse a question. Returns auto_fixable and needs_input.",
    },
    {
        "name": "step1_fix_auto",
        "description": "Apply ONLY automatic transforms. Returns remaining issues.",
    },
    {
        "name": "step1_fix_manual",
        "description": "Apply ONE manual fix based on user input.",
        "parameters": {
            "question_id": "Question ID",
            "field": "Field (bloom, difficulty, partial_feedback, etc.)",
            "value": "Value from user"
        }
    },
    {
        "name": "step1_suggest",
        "description": "Generate suggestion for a field. User can accept/modify.",
        "parameters": {
            "question_id": "Question ID",
            "field": "Field to suggest for"
        }
    },
    {
        "name": "step1_batch_preview",
        "description": "Show all questions with the same issue type.",
        "parameters": {
            "issue_type": "E.g., missing_partial_feedback"
        }
    },
    {
        "name": "step1_batch_apply",
        "description": "Apply the same fix to multiple questions.",
        "parameters": {
            "issue_type": "Issue type",
            "fix_type": "How to fix (copy_from_correct, etc.)",
            "question_ids": "List (optional, None = all)"
        }
    },
    {
        "name": "step1_skip",
        "description": "Skip issue or question.",
        "parameters": {
            "question_id": "Question ID (optional)",
            "issue_field": "Specific field, or None for entire question",
            "reason": "Reason (optional)"
        }
    },
    {
        "name": "step1_next",
        "description": "Go to next/previous question.",
    },
    {
        "name": "step1_preview",
        "description": "Preview working file.",
    },
    {
        "name": "step1_finish",
        "description": "Finish and generate report.",
    }
]
```

---

## REMOVE or CHANGE

### Remove entirely:
- `step1_transform()` - Replaced by `step1_fix_auto()` + interactive loop

### Change:
- `step1_start()` - Change return message
- `step1_analyze()` - Categorise output
- `step1_finish()` - Include skipped issues in report

---

## EXPECTED FLOW AFTER REBUILD

```
Claude: step1_start()
        "27 questions in v6.3 format. Starting interactive walkthrough."

Claude: step1_analyze("Q001")
        → auto_fixable: 3, needs_input: 2

Claude: step1_fix_auto("Q001")  
        → "Fixed 3. Remaining: bloom, partial_feedback"

Claude to User: "Q001 is missing Bloom level. Which one?"
                [Remember] [Understand] [Apply] ...

User: "Remember"

Claude: step1_fix_manual("Q001", "bloom", "Remember")
        → "Updated bloom"

Claude: step1_suggest("Q001", "partial_feedback")
        → suggestion: "Peristalsis is..."

Claude to User: "Suggesting partial_feedback: 'Peristalsis is...'
                 Accept, modify, or skip?"

User: "Accept"

Claude: step1_fix_manual("Q001", "partial_feedback", "...")
        → "Updated partial_feedback"

Claude: step1_next()
        → "Q002 (2 of 27)"

--- AFTER 5 QUESTIONS ---

Claude: step1_batch_preview("missing_partial_feedback")
        → "9 questions have the same problem"

Claude to User: "9 questions are missing partial_feedback.
                 Copy from correct_feedback for all?"

User: "Yes"

Claude: step1_batch_apply("missing_partial_feedback", "copy_from_correct")
        → "Fixed 9 questions"

--- AT THE END ---

Claude: step1_finish()
        → Report
```

---

## IMPLEMENTATION ORDER

1. **Add new tool functions** (step1_fix_auto, step1_fix_manual, etc.)
2. **Update step1_analyze()** return format
3. **Remove/disable step1_transform()**
4. **Test on one question**
5. **Test batch flow**
6. **Test on entire file**

---

## TEST CASE

File: `EXAMPLE_COURSE_Fys_v63.md` (27 questions)

Expected:
- `step1_start()` → Session started
- `step1_analyze()` → Shows auto + needs_input
- `step1_fix_auto()` → Fixes syntax, returns remaining
- `step1_batch_preview()` → Finds 11 with missing_partial_feedback
- `step1_batch_apply()` → Fixes all 11
- `step1_finish()` → 27 complete, 0 skipped

---

*Step 1 Rebuild Instructions v2.0 | 2026-01-08*
