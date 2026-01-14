# ADR-014: Shared Session Between qf-scaffolding and qf-pipeline

**Status:** Accepted  
**Date:** 2026-01-14  
**Deciders:** Niklas  
**Related:** ADR-001 (Two MCP Architecture), ADR-013 (Migration Strategy)

---

## Context

QuestionForge has two MCPs:
- **qf-pipeline:** Technical processing (validation, export)
- **qf-scaffolding:** Methodology guidance (M1-M4)

Questions to decide:
- How do these MCPs interact?
- Should they share session state?
- What's the user experience flow?

---

## Decision

### 1. Shared Session

Both MCPs share the same session created by `qf-pipeline step0_start`.

```
qf-pipeline                    qf-scaffolding
───────────────────            ───────────────────
step0_start ──────────────────→ reads session.yaml
step0_status                    module_status
step1-4_*                       list_modules, load_stage
         ↓                              ↓
    session.yaml ←───── SHARED ─────→ session.yaml
```

### 2. Common Init Output

Both MCPs return the SAME init instructions:

```markdown
"Vad har du att börja med?"

A) Material (föreläsningar, slides) → M1-M4 → Pipeline
B) Lärandemål → M2-M4 → Pipeline
C) Blueprint → M3-M4 → Pipeline
D) Markdown med frågor → Pipeline direkt
```

### 3. Extended Project Structure

```
project_name/
├── 00_materials/           ← NEW: Input for M1
├── 01_source/              ← Original markdown
├── 02_working/             ← Working copy
├── 03_output/              ← QTI export
├── methodology/            ← NEW: M1-M4 outputs
│   ├── m1_objectives.md
│   ├── m2_blueprint.md
│   └── m3_questions.md
└── session.yaml            ← Extended with methodology progress
```

### 4. Extended session.yaml

```yaml
# Existing (qf-pipeline)
session_id: "abc123"
source_file: "..."
working_file: "..."
validation_status: "pending"

# New (qf-scaffolding)
methodology:
  entry_point: "materials"
  active_module: "m1"
  m1:
    status: "in_progress"
    loaded_stages: [0, 1, 2]
    outputs:
      objectives: "methodology/m1_objectives.md"
  m2: { status: "not_started" }
  m3: { status: "not_started" }
  m4: { status: "not_started" }
```

### 5. Session Creator

**qf-pipeline** always creates session via `step0_start`.

**qf-scaffolding** reads existing session, never creates.

If no session exists when calling qf-scaffolding tools:
```
{
  error: "Ingen aktiv session",
  instruction: "Kör step0_start först (qf-pipeline)"
}
```

---

## Consequences

### Positive
- Unified user experience
- Single project folder
- Clear entry point routing (A/B/C/D)
- Progress tracked in one place
- Methodology outputs integrated with pipeline

### Negative
- qf-scaffolding depends on qf-pipeline being available
- session.yaml format must be coordinated
- Both MCPs must be updated together when session format changes

### Neutral
- User must start with init regardless of which MCP they call
- Clear separation: qf-pipeline = technical, qf-scaffolding = pedagogical

---

## Implementation

1. **qf-pipeline changes:**
   - Update init output to include A/B/C/D options
   - Add `00_materials/` and `methodology/` to project structure
   - Extend session.yaml schema (optional methodology section)

2. **qf-scaffolding implementation:**
   - Create `session_reader.ts` to read qf-pipeline session.yaml
   - Write methodology progress back to session.yaml
   - Return error if no session exists

---

## Alternatives Considered

### A: Separate Sessions (rejected)
- Each MCP has own session
- User must manually coordinate
- Rejected: Poor UX, confusing

### B: qf-scaffolding Creates Session (rejected)
- Either MCP can create session
- Risk of conflicts
- Rejected: Single source of truth is better

### C: Single MCP (rejected)
- Merge qf-scaffolding into qf-pipeline
- One large MCP
- Rejected: Different concerns, different languages (Python vs TypeScript)

---

*ADR-014 | QuestionForge | 2026-01-14*
