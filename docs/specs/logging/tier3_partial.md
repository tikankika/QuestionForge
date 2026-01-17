# TIER 3 SPEC: Audit Trail Logging (PARTIAL)

**Status:** PARTIAL - Väntar på M1-M4 implementation  
**Datum:** 2026-01-17

---

## VARFÖR TIER 3?

**Use Case:**
```
Teacher: "Varför blev Question 5 'Easy' difficulty?"
Claude: *läser logs* "Du valde 'Easy' vid step1_fix_manual kl 10:23"
```

**Syfte:**
- Läraren kan se sina egna beslut
- Transparent process
- Förstå varför frågor blev som de blev

---

## EVENTS SOM ÄR KLARA (kan implementeras NU)

### 1. format_detected

**När:** `detect_format()` identifierar format

**Schema:**
```json
{
  "ts": "...",
  "tool": "detector",
  "event": "format_detected",
  "data": {
    "format": "QFMD" | "LEGACY_SYNTAX" | "SEMI_STRUCTURED" | "UNSTRUCTURED" | "UNKNOWN",
    "question_count": 15,
    "confidence": "high" | "medium" | "low"
  }
}
```

**Implementation:**
```python
# step1/detector.py
def detect_format(content: str) -> FormatLevel:
    format_level = _detect(content)
    
    log_event(
        tool="detector",
        event="format_detected",
        data={
            "format": format_level.value,
            "question_count": _count_questions(content),
            "confidence": "high"
        }
    )
    
    return format_level
```

---

### 2. format_converted

**När:** step1 konverterar från ett format till QFMD

**Schema:**
```json
{
  "ts": "...",
  "tool": "step1_finish",
  "event": "format_converted",
  "data": {
    "from_format": "LEGACY_SYNTAX",
    "to_format": "QFMD",
    "questions_converted": 15,
    "questions_skipped": 2,
    "auto_fixes": 120,
    "manual_fixes": 36,
    "duration_ms": 45000
  }
}
```

**Implementation:**
```python
# step1/session.py
def finish():
    summary = get_summary()
    
    log_event(
        tool="step1_finish",
        event="format_converted",
        data={
            "from_format": session.detected_format,
            "to_format": "QFMD",
            "questions_converted": summary.completed,
            "questions_skipped": summary.skipped,
            "auto_fixes": summary.auto_fixes,
            "manual_fixes": summary.manual_fixes
        },
        duration_ms=session.duration_ms
    )
```

---

## EVENTS SOM VÄNTAR PÅ M1-M4 (implementera SENARE)

### 3. user_decision (PLACEHOLDER)

**När:** User makes pedagogical decision

**KÄNT idag (step1 context):**
```json
{
  "event": "user_decision",
  "tool": "step1_fix_manual",
  "data": {
    "question_id": "Q005",
    "decision_type": "bloom_level",
    "options_presented": ["Remember", "Understand", "Apply", "Analyze"],
    "user_choice": "Remember"
  }
}
```

**OKÄNT idag (M1-M4 context):**
- Vilka beslut fattas i M1 Stage 0-5?
- Vilka beslut fattas i M2 Stage 1-9?
- Format på options?
- Behöver vi `rationale` field?

**TODO när M1-M4 implementeras:**
1. Identifiera ALLA decision points i M1-M4
2. Definiera decision_type för varje
3. Definiera options format
4. Beslut om rationale (optional free text?)

**EXEMPEL decision_type (preliminära):**
```
# step1:
- "bloom_level"
- "difficulty_level"
- "question_type"
- "skip_question"

# M1 (gissa):
- "emphasis_tier"
- "example_relevance"
- "misconception_severity"

# M2 (gissa):
- "question_distribution"
- "bloom_distribution"
- "difficulty_distribution"

# M3 (gissa):
- "accept_generated_question"
- "modify_question"

# M4 (gissa):
- "question_quality_rating"
- "approve_for_export"
```

---

### 4. module_decision (PLACEHOLDER)

**När:** User makes module-level decision (navigate, skip module, etc)

**Schema (DRAFT):**
```json
{
  "event": "module_decision",
  "tool": "scaffolding_init",
  "data": {
    "decision_type": "entry_point",
    "choice": "m1",
    "available_options": ["m1", "m2", "m3", "m4", "pipeline"]
  }
}
```

**OKÄNT:**
- Vilka module-level decisions finns?
- Navigation mellan moduler?
- Skip/redo modules?

**TODO:** Identifiera när M1-M4 är implementerat

---

## IMPLEMENTATION PLAN

### PHASE 1: Implementera KLARA events (NU)

**Files to update:**
1. `packages/qf-pipeline/src/qf_pipeline/step1/detector.py`
   - Add `format_detected` logging

2. `packages/qf-pipeline/src/qf_pipeline/step1/session.py` (or wherever step1_finish lives)
   - Add `format_converted` logging

**Test:**
```bash
# Run step1 on test file
# Check logs/session.jsonl contains:
# - format_detected event
# - format_converted event
```

---

### PHASE 2: user_decision spec (VÄNTAR PÅ M1-M4)

**När M1 implementeras:**
1. Gå igenom varje stage (0-5)
2. Identifiera decision points
3. Dokumentera decision_type + options
4. Add logging i load_stage.ts

**När M2-M4 implementeras:**
- Upprepa för varje modul
- Lägg till i spec

---

## TIER 3 SUMMARY

**KLART NU:**
- ✅ format_detected
- ✅ format_converted

**VÄNTAR:**
- ⏸️ user_decision (behöver M1-M4)
- ⏸️ module_decision (behöver M1-M4)

**APPROACH:**
- Implementera de 2 klara events NU
- Återkom till user_decision när M1-M4 är igång
- Inkrementell spec när vi lär oss mer

---

## ADDENDUM: När ska vi uppdatera denna spec?

**Triggers för uppdatering:**
1. M1 Stage 0-5 implementerad → spec user_decision för M1
2. M2 implementerad → spec user_decision för M2
3. M3 implementerad → spec user_decision för M3
4. M4 implementerad → spec user_decision för M4
5. Scaffolding navigation implementerad → spec module_decision

**Process:**
1. Developer dokumenterar decision points i implementation
2. Update denna spec med konkreta exempel
3. Add logging calls med rätt schema
4. Test att events loggas korrekt

---

**Status:** 2/4 events klara för implementation  
**Next:** Implementera format_detected + format_converted  
**Then:** Vänta på M1-M4, spec user_decision inkrementellt
