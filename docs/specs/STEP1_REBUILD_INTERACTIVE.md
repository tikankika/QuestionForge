# STEP 1 REBUILD: Interactive Guide

**Problem:** Step 1 blev auto-batch, inte interaktiv guide  
**Lösning:** Ändra flow till fråga-för-fråga med lärar-beslut  
**Datum:** 2026-01-08

---

## NUVARANDE FLOW (FEL)

```
step1_start → step1_transform (alla frågor på en gång) → klart
                    ↑
                    Inget lärar-involvement!
```

## NY FLOW (RÄTT)

```
step1_start
    ↓
┌─────────────────────────────────────────────────────────────┐
│                    QUESTION LOOP                             │
│                                                              │
│  step1_analyze (visa issues för DENNA fråga)                │
│       ↓                                                      │
│  CLAUDE PRESENTERAR:                                         │
│  "Q001 har 3 problem:                                        │
│   1. [AUTO] Gammal syntax @question: → ^question            │
│   2. [AUTO] Saknar @end_field                               │
│   3. [FRÅGA] Saknar Bloom-nivå i labels"                    │
│       ↓                                                      │
│  CLAUDE FRÅGAR:                                              │
│  "Vilken Bloom-nivå? [Remember] [Understand] [Apply]..."    │
│       ↓                                                      │
│  LÄRAREN SVARAR: "Remember"                                 │
│       ↓                                                      │
│  step1_fix_auto + step1_fix_manual                          │
│       ↓                                                      │
│  step1_next → nästa fråga                                   │
│       ↓                                                      │
│  (repeat until all questions done)                          │
└─────────────────────────────────────────────────────────────┘
    ↓
step1_finish → rapport
```

---

## ÄNDRADE MCP TOOLS

### 1. step1_transform → TA BORT eller ÄNDRA

```python
# GAMMALT (fel):
def step1_transform(question_id=None):
    """Transformera alla frågor automatiskt"""
    # Kör alla transforms på alla frågor
    # Ingen interaktion
    
# NYTT (rätt):
def step1_transform(question_id=None):
    """
    Transformera ENDAST syntax-fixes som är 100% säkra.
    Returnerar lista av vad som INTE kunde fixas automatiskt.
    """
    # BARA syntax-transforms:
    # - @question: → ^question
    # - {{BLANK-1}} → {{blank_1}}
    # - Lägg till @end_field
    
    # RETURNERA issues som kräver input:
    return {
        "auto_fixed": ["Syntax converted", "Added @end_field"],
        "needs_input": [
            {"field": "^labels", "prompt": "select_bloom"},
            {"field": "partial_feedback", "prompt": "suggest_feedback"}
        ]
    }
```

### 2. step1_analyze → BEHÅLL men FÖRBÄTTRA

```python
def step1_analyze(question_id=None):
    """
    Analysera EN fråga och returnera issues KATEGORISERADE.
    """
    return {
        "question_id": "Q001",
        "question_type": "text_entry",
        
        # Kategorisera issues
        "auto_fixable": [
            {"id": 1, "message": "Gammal syntax @question:"},
            {"id": 2, "message": "Saknar @end_field"}
        ],
        "needs_input": [
            {
                "id": 3, 
                "field": "^labels",
                "message": "Saknar Bloom-nivå",
                "prompt_type": "select_bloom",
                "options": ["Remember", "Understand", "Apply", "Analyze"]
            },
            {
                "id": 4,
                "field": "partial_feedback", 
                "message": "Saknar partial_feedback",
                "prompt_type": "suggest_feedback",
                "suggestion": "Kopiera från correct_feedback?"
            }
        ],
        
        # Instruktion till Claude
        "instruction": "Fixa auto_fixable, fråga användaren om needs_input"
    }
```

### 3. step1_fix → SEPARERA auto och manual

```python
def step1_fix_auto(question_id=None):
    """
    Applicera BARA automatiska fixes.
    Returnera vad som fixades och vad som återstår.
    """
    return {
        "fixed": ["Syntax converted", "Added @end_field"],
        "remaining": [
            {"field": "^labels", "prompt": "select_bloom"},
            {"field": "partial_feedback", "prompt": "suggest_feedback"}
        ]
    }

def step1_fix_manual(question_id: str, field: str, value: str):
    """
    Applicera EN manuell fix baserat på lärar-input.
    """
    # Exempel: field="^labels", value="^labels #EXAMPLE_COURSE #Remember #Easy"
    return {
        "fixed": True,
        "field": field,
        "new_value": value
    }
```

### 4. NYTT: step1_suggest

```python
def step1_suggest(question_id: str, field: str):
    """
    Generera förslag för ett fält baserat på kontext.
    Användaren kan acceptera, modifiera, eller skriva eget.
    """
    if field == "partial_feedback":
        # Kopiera från correct_feedback
        correct = get_field(question_id, "correct_feedback")
        return {
            "field": field,
            "suggestion": correct,
            "options": [
                ("accept", "Acceptera förslaget"),
                ("modify", "Modifiera"),
                ("custom", "Skriv egen"),
                ("skip", "Hoppa över")
            ]
        }
    
    if field == "^labels":
        # Generera baserat på frågetyp och innehåll
        return {
            "field": field,
            "suggestion": "^labels #EXAMPLE_COURSE #Matsmältning #Remember #Easy",
            "needs_confirmation": True
        }
```

---

## HUR CLAUDE ANVÄNDER TOOLS

### Nuvarande (fel):
```
User: "Kör Step 1 på filen"
Claude: 
  1. step1_start() 
  2. step1_transform()  ← Allt på en gång!
  3. "Klart, 19 fel kvar"
```

### Nytt (rätt):
```
User: "Kör Step 1 på filen"

Claude:
  1. step1_start()
  → "27 frågor hittades i v6.3 format"
  
  2. step1_analyze()
  → "Q001 har 4 issues: 2 auto-fixable, 2 behöver input"
  
  3. step1_fix_auto()
  → "Fixade syntax. Kvar: Bloom-nivå, partial_feedback"
  
  4. Claude till användaren:
  "Q001 saknar Bloom-nivå. Vilken kognitiv nivå testar frågan?
   [Remember] [Understand] [Apply] [Analyze]"
  
  5. Användaren: "Remember"
  
  6. step1_fix_manual(field="bloom", value="Remember")
  
  7. Claude till användaren:
  "Q001 saknar partial_feedback. Ska jag kopiera från correct_feedback?
   [Ja] [Nej, jag skriver] [Hoppa över]"
  
  8. Användaren: "Ja"
  
  9. step1_fix_manual(field="partial_feedback", value=<kopierat>)
  
  10. step1_next()
  → "Q002 (2 av 27)"
  
  ... repeat för varje fråga ...
  
  27. step1_finish()
  → Rapport
```

---

## BATCH-APPLY (VIKTIGT!)

När samma issue finns i flera frågor:

```python
def step1_batch_preview(issue_type: str):
    """
    Visa alla frågor med samma issue.
    """
    return {
        "issue": "Saknar partial_feedback",
        "affected_questions": ["Q001", "Q005", "Q006", "Q007", "Q009", ...],
        "count": 11,
        "preview": {
            "Q001": "Peristaltik är de vågrörelser...",
            "Q005": "Enzymer är proteiner som...",
            # ... första 3 som preview
        }
    }

def step1_batch_apply(issue_type: str, fix_type: str, questions: list = None):
    """
    Applicera samma fix på flera frågor.
    
    Args:
        issue_type: "missing_partial_feedback"
        fix_type: "copy_from_correct" eller "custom"
        questions: Lista av frågor, eller None för alla
    """
    return {
        "applied_to": ["Q001", "Q005", "Q006", ...],
        "success": 11,
        "failed": 0
    }
```

### Claude använder batch:
```
Claude: "11 frågor saknar partial_feedback:
Q001, Q005, Q006, Q007, Q009, Q017, Q018, Q020, Q023, Q025

Vill du:
1. Kopiera från correct_feedback för alla 11
2. Gå igenom en i taget
3. Hoppa över alla"

Användaren: "1"

Claude: step1_batch_apply("missing_partial_feedback", "copy_from_correct")
→ "Fixade 11 frågor"
```

---

## IMPLEMENTATION PRIORITY

```
1. ÄNDRA step1_transform
   - Endast syntax-fixes
   - Returnera "needs_input" lista
   
2. FÖRBÄTTRA step1_analyze  
   - Kategorisera: auto_fixable vs needs_input
   - Inkludera prompt_type och options
   
3. LÄGG TILL step1_suggest
   - Generera förslag för saknade fält
   
4. LÄGG TILL step1_batch_preview + step1_batch_apply
   - Effektivisera repetitiva fixes
   
5. UPPDATERA prompts.py
   - Använd faktiskt PROMPTS-dictionary
   - Format för Claude att presentera
```

---

## FLOW DIAGRAM

```
                    ┌─────────────────┐
                    │  step1_start    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
            ┌──────►│  step1_analyze  │◄──────┐
            │       └────────┬────────┘       │
            │                │                │
            │       ┌────────▼────────┐       │
            │       │  step1_fix_auto │       │
            │       └────────┬────────┘       │
            │                │                │
            │     ┌──────────▼──────────┐     │
            │     │  needs_input?       │     │
            │     └──────────┬──────────┘     │
            │                │                │
            │         ┌──────┴──────┐         │
            │         │             │         │
            │    ┌────▼────┐   ┌────▼────┐    │
            │    │ PROMPT  │   │  BATCH  │    │
            │    │ USER    │   │ PREVIEW │    │
            │    └────┬────┘   └────┬────┘    │
            │         │             │         │
            │    ┌────▼────┐   ┌────▼────┐    │
            │    │  USER   │   │  USER   │    │
            │    │ DECIDES │   │ DECIDES │    │
            │    └────┬────┘   └────┬────┘    │
            │         │             │         │
            │    ┌────▼────────────▼────┐     │
            │    │  step1_fix_manual    │     │
            │    │  OR step1_batch_apply│     │
            │    └──────────┬───────────┘     │
            │               │                 │
            │      ┌────────▼────────┐        │
            │      │  step1_next     │        │
            │      └────────┬────────┘        │
            │               │                 │
            │      ┌────────▼────────┐        │
            │      │  more questions?│────────┘
            │      └────────┬────────┘
            │               │ no
            │      ┌────────▼────────┐
            └──────│  step1_finish   │
                   └─────────────────┘
```

---

## EXEMPEL: Komplett Session

```
USER: Kör Step 1 på EXAMPLE_COURSE_Fys_v63.md

CLAUDE: [step1_start]
📁 Session startad!
- Fil: EXAMPLE_COURSE_Fys_v63.md
- Format: v6.3 (behöver uppgradering till v6.5)
- Frågor: 27 st

Ska jag börja med Q001?

USER: Ja

CLAUDE: [step1_analyze(Q001)]
**Q001: Muskelrörelse i mag-tarmkanalen**
Typ: text_entry

Hittade 4 issues:
✅ AUTO: Konvertera @question: → ^question
✅ AUTO: Konvertera @tags: → ^labels  
✅ AUTO: Lägg till @end_field
❓ INPUT: Saknar partial_feedback

[step1_fix_auto]
Fixade 3 syntax-issues.

Kvar: Q001 saknar partial_feedback.

Vill du:
1. Kopiera från correct_feedback
2. Skriva egen
3. Hoppa över

USER: 1

CLAUDE: [step1_fix_manual(field="partial_feedback", value=<kopierat>)]
✅ Q001 klar!

[step1_next]
**Q002: Var produceras galla** (2 av 27)
...

--- EFTER 5 FRÅGOR ---

CLAUDE: Jag ser att 9 frågor till saknar partial_feedback.
Vill du applicera samma fix (kopiera från correct) på alla?

[step1_batch_preview("missing_partial_feedback")]
Påverkade frågor: Q005, Q006, Q007, Q009, Q017, Q018, Q020, Q023, Q025

1. Ja, fixa alla 9
2. Nej, gå igenom en i taget
3. Hoppa över alla

USER: 1

CLAUDE: [step1_batch_apply(...)]
✅ Fixade partial_feedback för 9 frågor

--- FORTSÄTTER ---

CLAUDE: [step1_finish]
📊 Step 1 Klar!

Resultat:
- 27 frågor behandlade
- 24 helt klara
- 3 med varningar (Q013, Q021, Q023 - match-format)
- 0 skippade

Klar för Step 2 validate?
```

---

## SAMMANFATTNING

| Gammalt | Nytt |
|---------|------|
| Auto-batch allt | Fråga-för-fråga |
| Ingen interaktion | Claude frågar, läraren svarar |
| 19 fel kvar som Claude fixar | Alla fel hanteras i loopen |
| prompts.py oanvänd | prompts.py används aktivt |

---

*Step 1 Rebuild Spec | 2026-01-08*
