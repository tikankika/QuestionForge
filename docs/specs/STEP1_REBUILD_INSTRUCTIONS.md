# STEP 1 REBUILD INSTRUCTIONS

**För:** Code/Developer  
**Version:** 2.0 (Interactive Rebuild)  
**Datum:** 2026-01-08  
**Status:** Refaktorering av befintlig kod

---

## SAMMANFATTNING

Befintlig kod i `step1/` har alla byggblock men `step1_tools.py` använder dem fel.

**Problem:** `step1_transform()` kör alla transforms på alla frågor utan användarinteraktion.

**Lösning:** Ändra tools att returnera "needs_input" till Claude, som frågar användaren.

---

## BEFINTLIG KOD - BEHÅLL

| Fil | Status | Kommentar |
|-----|--------|-----------|
| `session.py` | ✅ BEHÅLL | Fungerar bra |
| `detector.py` | ✅ BEHÅLL | Fungerar bra |
| `parser.py` | ✅ BEHÅLL | Fungerar bra |
| `analyzer.py` | ✅ BEHÅLL | Har `prompt_key` - behövs! |
| `transformer.py` | ✅ BEHÅLL | Alla transforms fungerar |
| `prompts.py` | ✅ BEHÅLL | Har allt - börja ANVÄNDA det! |

---

## ÄNDRA: step1_tools.py

### Nuvarande tools (FEL):

```python
step1_start()      # OK men meddelandet är fel
step1_status()     # OK
step1_analyze()    # OK men används inte rätt
step1_transform()  # ❌ FEL - Kör allt utan frågor
step1_next()       # OK
step1_preview()    # OK  
step1_finish()     # OK
```

### Nya/Ändrade tools (RÄTT):

```python
step1_start()          # Ändra meddelande
step1_status()         # Behåll
step1_analyze()        # Ändra return format
step1_fix_auto()       # NY - Endast auto-fixable
step1_fix_manual()     # NY - En fix i taget
step1_suggest()        # NY - Generera förslag
step1_batch_preview()  # NY - Visa liknande frågor
step1_batch_apply()    # NY - Applicera på flera
step1_skip()           # NY - Hoppa över issue
step1_next()           # Behåll
step1_preview()        # Behåll
step1_finish()         # Behåll
```

---

## IMPLEMENTATION DETAILS

### 1. ÄNDRA `step1_start()`

```python
async def step1_start(...) -> Dict[str, Any]:
    # ... befintlig kod ...
    
    # ÄNDRA return message:
    return {
        # ... befintliga fält ...
        
        # NYTT: Instruktion till Claude om hur processen fungerar
        "instruction": (
            "Step 1 är interaktiv. För varje fråga:\n"
            "1. Kör step1_analyze() för att se issues\n"
            "2. Kör step1_fix_auto() för automatiska fixar\n"
            "3. För issues med 'needs_input': fråga användaren\n"
            "4. Kör step1_fix_manual() med användarens svar\n"
            "5. Kör step1_next() för nästa fråga"
        ),
        
        # NYTT: Första frågan klar för analys
        "next_action": "step1_analyze"
    }
```

### 2. ÄNDRA `step1_analyze()`

Returnera issues kategoriserade:

```python
async def step1_analyze(question_id: Optional[str] = None) -> Dict[str, Any]:
    # ... befintlig kod för att hitta fråga och analysera ...
    
    issues = analyze_question(question.raw_content, question.detected_type)
    
    # NYTT: Kategorisera issues
    auto_fixable = [i for i in issues if i.auto_fixable]
    needs_input = [i for i in issues if not i.auto_fixable and i.prompt_key]
    
    return {
        "question_id": target_id,
        "question_type": question.detected_type,
        "question_preview": question.raw_content[:200] + "...",
        
        # NYTT: Separerade kategorier
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
                # NYTT: Inkludera prompt-info så Claude kan fråga
                "prompt": get_prompt(i.prompt_key) if i.prompt_key else None
            }
            for idx, i in enumerate(needs_input)
        ],
        
        # NYTT: Instruktion till Claude
        "instruction": (
            f"{len(auto_fixable)} auto-fixable (kör step1_fix_auto), "
            f"{len(needs_input)} behöver input (fråga användaren)"
        )
    }
```

### 3. NY: `step1_fix_auto()`

Applicera ENDAST automatiska transforms, returnera remaining:

```python
async def step1_fix_auto(question_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Applicera endast auto-fixable transforms på en fråga.
    
    Returns:
        fixed: Lista av vad som fixades
        remaining: Issues som kräver input
    """
    if not _step1_session:
        return {"error": "No active session"}
    
    # Läs fil och hitta fråga
    working_path = Path(_step1_session.working_file)
    content = working_path.read_text(encoding='utf-8')
    questions = parse_file(content)
    
    target_id = question_id or _step1_session.questions[_step1_session.current_index].question_id
    question = get_question_by_id(questions, target_id)
    
    if not question:
        return {"error": f"Question not found: {target_id}"}
    
    # Applicera transforms
    new_content, changes = transformer.apply_all_auto(question.raw_content)
    
    if changes:
        # Uppdatera fil
        full_content = content.replace(question.raw_content, new_content)
        working_path.write_text(full_content, encoding='utf-8')
        
        # Logga ändringar
        for change_desc in changes:
            _step1_session.add_change(
                question_id=target_id,
                field='auto',
                old_value=None,
                new_value=change_desc,
                change_type='auto'
            )
    
    # Analysera igen för att se vad som återstår
    # Läs uppdaterad version
    updated_content = working_path.read_text(encoding='utf-8')
    updated_questions = parse_file(updated_content)
    updated_question = get_question_by_id(updated_questions, target_id)
    
    remaining_issues = analyze_question(updated_question.raw_content, updated_question.detected_type)
    needs_input = [i for i in remaining_issues if not i.auto_fixable and i.prompt_key]
    
    return {
        "question_id": target_id,
        "fixed": changes,
        "fixed_count": len(changes),
        
        # Vad som återstår och kräver input
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
        
        # Instruktion till Claude
        "instruction": (
            f"Fixade {len(changes)} auto-issues. "
            f"{len(needs_input)} kräver användarinput."
            if needs_input else
            "Alla issues fixade! Kör step1_next() för nästa fråga."
        )
    }
```

### 4. NY: `step1_fix_manual()`

Applicera en manuell fix baserat på användarinput:

```python
async def step1_fix_manual(
    question_id: str,
    field: str,
    value: str
) -> Dict[str, Any]:
    """
    Applicera en manuell fix från användarinput.
    
    Args:
        question_id: Fråge-ID
        field: Fält att uppdatera (t.ex. "bloom", "difficulty", "partial_feedback")
        value: Värde från användaren
        
    Returns:
        Bekräftelse av ändring
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
    
    # Hantera olika typer av fixes
    if field == "bloom":
        # Lägg till Bloom-nivå i ^tags
        new_content = _add_to_tags(new_content, f"#{value}")
        
    elif field == "difficulty":
        # Lägg till difficulty i ^tags
        new_content = _add_to_tags(new_content, f"#{value}")
        
    elif field == "partial_feedback":
        # Lägg till partial_feedback subfield
        new_content = _add_feedback_subfield(new_content, "partial_feedback", value)
        
    elif field == "correct_answers":
        # Lägg till correct_answers för multiple_response
        new_content = _add_correct_answers(new_content, value)
        
    else:
        return {"error": f"Unknown field: {field}"}
    
    # Uppdatera fil
    full_content = content.replace(question.raw_content, new_content)
    working_path.write_text(full_content, encoding='utf-8')
    
    # Logga ändring
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
        "message": f"Uppdaterade {field} för {question_id}"
    }


def _add_to_tags(content: str, tag: str) -> str:
    """Lägg till tag i ^tags rad."""
    import re
    match = re.search(r'(\^tags\s+.+)$', content, re.MULTILINE)
    if match:
        old_tags = match.group(1)
        new_tags = f"{old_tags} {tag}"
        return content.replace(old_tags, new_tags)
    return content


def _add_feedback_subfield(content: str, subfield_name: str, value: str) -> str:
    """Lägg till en feedback subfield."""
    # Hitta @field: feedback ... @end_field
    import re
    
    # Hitta sista @@end_field innan @end_field för feedback
    pattern = r'(@@field: \w+_feedback\n.*?@@end_field)\n(@end_field)'
    
    replacement = f'\\1\n\n@@field: {subfield_name}\n{value}\n@@end_field\n\\2'
    return re.sub(pattern, replacement, content, flags=re.DOTALL)


def _add_correct_answers(content: str, answers: str) -> str:
    """Lägg till correct_answers section för multiple_response."""
    # Implementation beror på exakt format
    pass
```

### 5. NY: `step1_suggest()`

Generera förslag för ett fält:

```python
async def step1_suggest(
    question_id: str,
    field: str
) -> Dict[str, Any]:
    """
    Generera förslag för ett fält baserat på kontext.
    
    Args:
        question_id: Fråge-ID
        field: Fält att föreslå värde för
        
    Returns:
        Förslag som användaren kan acceptera/modifiera
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
        # Kopiera från correct_feedback
        import re
        match = re.search(r'@@field: correct_feedback\n(.*?)@@end_field', 
                         question.raw_content, re.DOTALL)
        if match:
            suggestion = match.group(1).strip()
    
    elif field == "bloom":
        # Gissa baserat på frågetyp
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
            ("accept", "Acceptera förslaget"),
            ("modify", "Modifiera"),
            ("skip", "Hoppa över")
        ],
        "instruction": f"Förslag för {field}: '{suggestion}'. Acceptera, modifiera, eller hoppa över?"
    }
```

### 6. NY: `step1_batch_preview()`

Visa frågor med samma issue:

```python
async def step1_batch_preview(issue_type: str) -> Dict[str, Any]:
    """
    Visa alla frågor med samma typ av issue.
    
    Args:
        issue_type: T.ex. "missing_partial_feedback", "missing_bloom"
        
    Returns:
        Lista av påverkade frågor med preview
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
        "questions": affected[:5],  # Visa max 5 som preview
        "all_ids": [a["question_id"] for a in affected],
        "instruction": (
            f"{len(affected)} frågor har samma problem. "
            "Vill du applicera samma fix på alla?"
        ),
        "options": [
            ("all", f"Applicera på alla {len(affected)}"),
            ("select", "Låt mig välja vilka"),
            ("one", "Bara nuvarande fråga")
        ]
    }


def _matches_issue_type(issue, issue_type: str) -> bool:
    """Kolla om issue matchar typ."""
    type_mapping = {
        "missing_partial_feedback": lambda i: "partial_feedback" in i.message.lower(),
        "missing_bloom": lambda i: "bloom" in i.message.lower(),
        "missing_difficulty": lambda i: "svårighetsgrad" in i.message.lower(),
        "missing_correct_answers": lambda i: "correct_answers" in i.message.lower(),
    }
    check = type_mapping.get(issue_type)
    return check(issue) if check else False
```

### 7. NY: `step1_batch_apply()`

Applicera samma fix på flera frågor:

```python
async def step1_batch_apply(
    issue_type: str,
    fix_type: str,
    question_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Applicera samma fix på flera frågor.
    
    Args:
        issue_type: T.ex. "missing_partial_feedback"
        fix_type: T.ex. "copy_from_correct", "add_bloom_remember"
        question_ids: Specifika frågor, eller None för alla
        
    Returns:
        Resultat av batch-operation
    """
    if not _step1_session:
        return {"error": "No active session"}
    
    working_path = Path(_step1_session.working_file)
    content = working_path.read_text(encoding='utf-8')
    
    # Hitta påverkade frågor
    if question_ids is None:
        # Hitta alla med detta issue
        preview = await step1_batch_preview(issue_type)
        question_ids = preview.get("all_ids", [])
    
    success = []
    failed = []
    
    for qid in question_ids:
        try:
            # Applicera fix beroende på typ
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
            
            # ... fler fix types ...
            
        except Exception as e:
            failed.append(qid)
    
    # Logga batch-change
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
        "message": f"Fixade {len(success)} av {len(question_ids)} frågor"
    }
```

### 8. NY: `step1_skip()`

Hoppa över en issue:

```python
async def step1_skip(
    question_id: Optional[str] = None,
    issue_field: Optional[str] = None,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Hoppa över en issue eller hel fråga.
    
    Args:
        question_id: Fråge-ID (default: aktuell)
        issue_field: Specifikt fält att hoppa över (None = hoppa hela frågan)
        reason: Anledning
        
    Returns:
        Bekräftelse
    """
    if not _step1_session:
        return {"error": "No active session"}
    
    target_id = question_id or _step1_session.questions[_step1_session.current_index].question_id
    
    if issue_field:
        # Hoppa över specifikt issue
        _step1_session.add_change(
            question_id=target_id,
            field=f"skip_{issue_field}",
            old_value=None,
            new_value=reason or "User skipped",
            change_type="skip"
        )
        
        # Uppdatera frågestatus
        q_status = next((q for q in _step1_session.questions if q.question_id == target_id), None)
        if q_status:
            q_status.issues_skipped += 1
        
        return {
            "question_id": target_id,
            "skipped_field": issue_field,
            "reason": reason,
            "message": f"Hoppade över {issue_field} för {target_id}"
        }
    else:
        # Hoppa över hela frågan
        _step1_session.mark_current_skipped(reason)
        
        return {
            "question_id": target_id,
            "skipped": True,
            "reason": reason,
            "message": f"Hoppade över hela {target_id}",
            "next_action": "step1_next"
        }
```

---

## UPPDATERADE TOOL REGISTRATIONS

```python
STEP1_TOOLS = [
    {
        "name": "step1_start",
        "description": "Starta Step 1 interaktiv session.",
    },
    {
        "name": "step1_status",
        "description": "Visa session status.",
    },
    {
        "name": "step1_analyze",
        "description": "Analysera en fråga. Returnerar auto_fixable och needs_input.",
    },
    {
        "name": "step1_fix_auto",
        "description": "Applicera ENDAST automatiska transforms. Returnerar remaining issues.",
    },
    {
        "name": "step1_fix_manual",
        "description": "Applicera EN manuell fix baserat på användarinput.",
        "parameters": {
            "question_id": "Fråge-ID",
            "field": "Fält (bloom, difficulty, partial_feedback, etc.)",
            "value": "Värde från användaren"
        }
    },
    {
        "name": "step1_suggest",
        "description": "Generera förslag för ett fält. Användaren kan acceptera/modifiera.",
        "parameters": {
            "question_id": "Fråge-ID",
            "field": "Fält att föreslå för"
        }
    },
    {
        "name": "step1_batch_preview",
        "description": "Visa alla frågor med samma issue-typ.",
        "parameters": {
            "issue_type": "T.ex. missing_partial_feedback"
        }
    },
    {
        "name": "step1_batch_apply",
        "description": "Applicera samma fix på flera frågor.",
        "parameters": {
            "issue_type": "Issue-typ",
            "fix_type": "Hur fixas (copy_from_correct, etc.)",
            "question_ids": "Lista (optional, None = alla)"
        }
    },
    {
        "name": "step1_skip",
        "description": "Hoppa över issue eller fråga.",
        "parameters": {
            "question_id": "Fråge-ID (optional)",
            "issue_field": "Specifikt fält, eller None för hel fråga",
            "reason": "Anledning (optional)"
        }
    },
    {
        "name": "step1_next",
        "description": "Gå till nästa/föregående fråga.",
    },
    {
        "name": "step1_preview",
        "description": "Förhandsgranska working file.",
    },
    {
        "name": "step1_finish",
        "description": "Avsluta och generera rapport.",
    }
]
```

---

## TA BORT eller ÄNDRA

### Ta bort helt:
- `step1_transform()` - Ersätts av `step1_fix_auto()` + interaktiv loop

### Ändra:
- `step1_start()` - Ändra return message
- `step1_analyze()` - Kategorisera output
- `step1_finish()` - Inkludera skipped issues i rapport

---

## EXPECTED FLOW EFTER REBUILD

```
Claude: step1_start()
        "27 frågor i v6.3 format. Börjar interaktiv genomgång."

Claude: step1_analyze("Q001")
        → auto_fixable: 3, needs_input: 2

Claude: step1_fix_auto("Q001")  
        → "Fixade 3. Kvar: bloom, partial_feedback"

Claude till User: "Q001 saknar Bloom-nivå. Vilken?"
                  [Remember] [Understand] [Apply] ...

User: "Remember"

Claude: step1_fix_manual("Q001", "bloom", "Remember")
        → "Uppdaterade bloom"

Claude: step1_suggest("Q001", "partial_feedback")
        → suggestion: "Peristaltik är..."

Claude till User: "Föreslår partial_feedback: 'Peristaltik är...'
                   Acceptera, modifiera, eller hoppa över?"

User: "Acceptera"

Claude: step1_fix_manual("Q001", "partial_feedback", "...")
        → "Uppdaterade partial_feedback"

Claude: step1_next()
        → "Q002 (2 av 27)"

--- EFTER 5 FRÅGOR ---

Claude: step1_batch_preview("missing_partial_feedback")
        → "9 frågor har samma problem"

Claude till User: "9 frågor saknar partial_feedback.
                   Kopiera från correct_feedback för alla?"

User: "Ja"

Claude: step1_batch_apply("missing_partial_feedback", "copy_from_correct")
        → "Fixade 9 frågor"

--- TILL SLUT ---

Claude: step1_finish()
        → Rapport
```

---

## IMPLEMENTATION ORDER

1. **Lägg till nya tool-funktioner** (step1_fix_auto, step1_fix_manual, etc.)
2. **Uppdatera step1_analyze()** return format
3. **Ta bort/disable step1_transform()**
4. **Testa på en fråga**
5. **Testa batch-flow**
6. **Testa på hel fil**

---

## TEST CASE

Fil: `BIOG001X_Fys_v63.md` (27 frågor)

Expected:
- `step1_start()` → Session startad
- `step1_analyze()` → Visar auto + needs_input
- `step1_fix_auto()` → Fixar syntax, returnerar remaining
- `step1_batch_preview()` → Hittar 11 med missing_partial_feedback
- `step1_batch_apply()` → Fixar alla 11
- `step1_finish()` → 27 klara, 0 skipped

---

*Step 1 Rebuild Instructions v2.0 | 2026-01-08*
