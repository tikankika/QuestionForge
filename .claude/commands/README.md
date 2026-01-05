# ACDM Commands

Custom slash commands for AI-Collaborative Development Method (ACDM) v1.0.

## Commands

### Strategic Layer (Claude Desktop / Claude Code)

| Command | Phase | Purpose |
|---------|-------|---------|
| `/acdm-discover` | DISCOVER | Explore problem, gather context |
| `/acdm-shape` | SHAPE | Generate and analyze options |
| `/acdm-decide` | DECIDE | Document decision, create spec |
| `/acdm-coordinate` | COORDINATE | Prepare for implementation |
| `/acdm-status` | - | Quick reference, where am I? |

### Implementation Layer (Claude Code)

| Command | Phase | Purpose |
|---------|-------|---------|
| `/impl-explore` | EXPLORE | Read codebase, understand context |
| `/impl-plan` | PLAN | Create implementation plan |
| `/impl-code` | CODE | TDD implementation |
| `/impl-commit` | COMMIT | Finalize, PR, documentation |

---

## Typical Flow

```
STRATEGIC LAYER                  IMPLEMENTATION LAYER
───────────────                  ────────────────────
/acdm-discover
        ↓
/acdm-shape
        ↓
/acdm-decide
        ↓
/acdm-coordinate
        ↓
    [handoff] ──────────────────► /impl-explore
                                        ↓
                                  /impl-plan
                                        ↓
                                  /impl-code
                                        ↓
                                  /impl-commit
                                        ↓
    [feedback] ◄────────────────── [complete]
```

---

*ACDM v1.0*
