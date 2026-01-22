# ACDM Meta-Note: Lessons from 2026-01-06 Session

**Type:** Process reflection  
**Date:** 2026-01-06  
**Context:** Deep analysis of Terminal QTI Generator vs qf-pipeline

---

## KEY LEARNINGS

### 1. Multi-Agent Discovery is Powerful

**What happened:**
- Claude.ai focused on architecture, UX, config location
- Claude Code found critical bug (resources.py unused)

**Learning:**
- Different perspectives catch different issues
- Claude.ai: Good for high-level design, ADRs, documentation structure
- Claude Code: Good for code-level analysis, finding unused code, testing

**ACDM implication:**
- DISCOVER phase may benefit from multiple passes with different tools
- Consider "architecture review" vs "code review" as separate sub-phases

---

### 2. Handoff Documents Work Well

**What happened:**
- Created `IMPLEMENT_handoff_*.md` with exact code snippets
- Claude Code can execute directly from these

**Learning:**
- Handoff docs should include:
  - Priority order
  - Exact file paths
  - Copy-pasteable code
  - Test instructions
  - Verification steps

**ACDM implication:**
- Standardize handoff document format
- Consider template: `IMPLEMENT_handoff_TEMPLATE.md`

---

### 3. ADRs Before Implementation

**What happened:**
- Created ADR-008 (config location) and ADR-009 (resources) BEFORE coding
- Clear rationale documented for future reference

**Learning:**
- ADRs force structured thinking
- Prevents "just code it" impulse
- Creates audit trail

**ACDM implication:**
- DECIDE phase should always produce ADR for non-trivial changes
- ADR number = priority tracking

---

### 4. Documentation Structure Matters

**What happened:**
- Initially mixed patterns (root files vs subdirectories)
- Established hybrid structure with clear purpose for each location

**Learning:**
- Living docs (summaries) → root
- Logs (chronological) → acdm/logs/
- Decisions → adr/
- Handoffs → root with IMPLEMENT_ prefix

**ACDM implication:**
- Document the documentation structure itself (README in acdm/)
- Consistent naming conventions reduce cognitive load

---

### 5. Wrapper vs Utility Distinction

**What happened:**
- Initially proposed `wrappers/projects.py`
- Corrected to `utils/config.py` after discussion

**Learning:**
- Wrappers = wrap external CODE (classes, functions)
- Utils = internal LOGIC (file I/O, helpers)
- This distinction prevents architectural drift

**ACDM implication:**
- Architecture decisions emerge through dialogue
- Don't assume first proposal is correct
- Challenge categorization decisions

---

## PROCESS TIMELINE

```
Session: ~2 hours

DISCOVER (Claude.ai)
  → Terminal analysis
  → Wrapper analysis
  → Proposed config location

SHAPE (Dialogue)
  → wrappers/projects.py proposed
  → Corrected to utils/config.py

DECIDE
  → ADR-008: Config location

DISCOVER (Claude Code)
  → Deep code analysis
  → Critical bug: resources unused

DECIDE
  → ADR-009: Resource handling (priority shift!)

COORDINATE
  → Handoff document created
```

---

## ACDM PHASE OBSERVATIONS

| Phase | What Worked | What Could Improve |
|-------|-------------|-------------------|
| DISCOVER | Multi-agent analysis | Could start with Code for code bugs |
| SHAPE | Dialogue refined solution | Initial proposal was wrong |
| DECIDE | ADRs captured decisions | Need ADR template |
| COORDINATE | Handoff docs clear | Need handoff template |

---

## MULTI-AGENT PATTERN

```
┌─────────────────────────────────────────────────────┐
│  Claude.ai                                          │
│  ├─ Architecture analysis                           │
│  ├─ UX comparison                                   │
│  ├─ Documentation structure                         │
│  └─ ADR creation                                    │
└──────────────────────┬──────────────────────────────┘
                       │ Handoff
                       ▼
┌─────────────────────────────────────────────────────┐
│  Claude Code                                        │
│  ├─ Deep code analysis                              │
│  ├─ Find unused code/bugs                           │
│  ├─ Implementation                                  │
│  └─ Testing                                         │
└─────────────────────────────────────────────────────┘
```

**Key insight:** Priority can SHIFT based on Code's findings. Today: list_projects was prio 1, then resources bug became prio 1.

---

## SUGGESTED ACDM REFINEMENTS

1. **Split DISCOVER into sub-phases:**
   - DISCOVER-Architecture (Claude.ai)
   - DISCOVER-Code (Claude Code)

2. **Create templates:**
   - ADR template
   - Handoff template
   - ACDM log template

3. **Document multi-agent workflow:**
   - When to use each tool
   - How to consolidate findings
   - How to handle priority shifts

---

*Meta-note captured: 2026-01-06*
