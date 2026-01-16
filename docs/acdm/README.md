# ACDM Documentation Structure

**AI-Collaborative Development Method (ACDM)**

This folder contains ACDM-related documentation organized by purpose.

---

## Structure

```
docs/
├── DISCOVERY_BRIEF.md              ← "Living" summary documents
├── EXPLORE_PHASE_SUMMARY.md        ← Updated over time
├── IMPLEMENT_handoff_*.md          ← Handoff documents
│
├── acdm/
│   ├── README.md                   ← This file
│   ├── logs/                       ← Chronological work logs
│   │   └── YYYY-MM-DD_PHASE_*.md   ← Dated session logs
│   └── meta/                       ← ACDM process reflections
│       └── YYYY-MM-DD_ACDM_*.md    ← Learnings about ACDM itself
│
├── adr/                            ← Architecture Decision Records
│   └── ADR-NNN-*.md                ← Numbered decisions
│
├── analysis/                       ← Technical analyses
│   └── *_Analysis.md               ← Deep technical comparisons
│
├── specs/                          ← Implementation specifications
│   └── *-spec.md                   ← Technical specs
│
└── chat_claude_desctop/            ← Saved conversations
    └── *.md                        ← Full dialogue exports
```

---

## Document Types

### Living Documents (docs root)
- **Purpose:** High-level summaries that evolve over time
- **Naming:** `PHASE_description.md` (e.g., `DISCOVERY_BRIEF.md`)
- **Updates:** Refined as understanding deepens
- **Audience:** Anyone needing project overview

### ACDM Meta Notes (acdm/meta/)
- **Purpose:** Reflections on the ACDM process itself
- **Naming:** `YYYY-MM-DD_ACDM_topic.md`
- **Updates:** Created after sessions with notable learnings
- **Audience:** Future ACDM methodology development

### ACDM Logs (acdm/logs/)
- **Purpose:** Chronological record of ACDM sessions
- **Naming:** `YYYY-MM-DD_PHASE_topic.md`
- **Updates:** Created once, rarely modified
- **Audience:** Developers tracing decision history

### ADRs (adr/)
- **Purpose:** Record architectural decisions
- **Naming:** `ADR-NNN-short-title.md`
- **Updates:** Status changes only (Proposed → Accepted)
- **Audience:** Developers understanding why choices were made

### Technical Analyses (analysis/)
- **Purpose:** Deep technical comparisons and research
- **Naming:** `Topic_Analysis.md`
- **Updates:** As needed when new information emerges
- **Audience:** Developers implementing features

### Specifications (specs/)
- **Purpose:** Implementation details and contracts
- **Naming:** `component-spec.md`
- **Updates:** Versioned as requirements change
- **Audience:** Developers building features

---

## ACDM Phases

| Phase | Purpose | Output Location |
|-------|---------|-----------------|
| DISCOVER | Understand problem space | `docs/DISCOVERY_BRIEF.md` + `acdm/logs/` |
| SHAPE | Design solutions | `docs/` + `acdm/logs/` |
| DECIDE | Make architectural choices | `adr/ADR-*.md` |
| COORDINATE | Plan implementation | `specs/*-spec.md` |
| EXPLORE | Investigate codebase | `docs/EXPLORE_*.md` |
| PLAN | Create tasks | External (issues, tasks) |
| CODE | Implement | Source code |
| COMMIT | Finalize | Git commits |

---

## Workflow

1. **During session:** Create dated log in `acdm/logs/`
2. **After session:** Update living document in `docs/` if insights are significant
3. **If decision made:** Create or update ADR in `adr/`
4. **If specification needed:** Create in `specs/`

---

## Current Logs

| Date | Phase | Topic | File |
|------|-------|-------|------|
| 2026-01-06 | DISCOVER | Terminal vs qf-pipeline comparison | `logs/2026-01-06_DISCOVER_Terminal_vs_qf-pipeline.md` |
| 2026-01-06 | DISCOVER | qf-pipeline wrapper analysis | `logs/2026-01-06_DISCOVER_qf-pipeline_wrapper_analysis.md` |
| 2026-01-06 | DISCOVER | Consolidated analysis (Code + Claude.ai) | `logs/2026-01-06_DISCOVER_consolidated_analysis.md` |
| 2026-01-06 | DISCOVER | Detailed Terminal vs qf-pipeline comparison | `logs/2026-01-06_DISCOVER_detailed_comparison.md` |

## Related ADRs

| ADR | Topic | Status |
|-----|-------|--------|
| ADR-008 | Project Configuration Location | Proposed |
| ADR-009 | Resource Handling in Export | Proposed, 🔴 CRITICAL |
| ADR-010 | Step 3 Decision Architecture | Proposed |
| ADR-011 | Question Set Builder | Proposed |
| ADR-012 | Validation Output Improvement | Proposed, 🔴 BUG |

## Meta Notes

| Date | Topic | File |
|------|-------|------|
| 2026-01-06 | Process learnings: Multi-agent, handoffs, ADRs | `meta/2026-01-06_ACDM_process_learnings.md` |

---

*Structure established: 2026-01-06*
