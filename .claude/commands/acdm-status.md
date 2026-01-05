# ACDM Status Check

Quick reference for where you are in the ACDM workflow.

## Current Phase Checklist

### Strategic Layer (Desktop)

**DISCOVER** - Problem exploration
- [ ] Problem clearly stated
- [ ] Pain points identified
- [ ] Constraints documented
- [ ] DISCOVERY_BRIEF.md created
→ Next: `/acdm-shape`

**SHAPE** - Options analysis
- [ ] 2-4 options generated
- [ ] Tradeoffs analyzed
- [ ] Rabbit holes identified
- [ ] No-gos defined
- [ ] Recommendation made
→ Next: Human decides, then `/acdm-decide`

**DECIDE** - Document decision
- [ ] ADR written
- [ ] Specification created
- [ ] CHANGELOG updated
→ Next: `/acdm-coordinate`

**COORDINATE** - Prep for implementation
- [ ] Implementation instructions written
- [ ] CLAUDE.md updated (if needed)
- [ ] Sync points defined
→ Next: Handoff to Claude Code

---

### Implementation Layer (Code)

**EXPLORE** - Understand codebase
- [ ] Instructions read
- [ ] Spec understood
- [ ] Relevant code explored
- [ ] Dependencies mapped
→ Next: `/impl-plan`

**PLAN** - Implementation planning
- [ ] Steps defined
- [ ] Test strategy clear
- [ ] Risks identified
→ Next: `/impl-code`

**CODE** - TDD implementation
- [ ] Tests written first
- [ ] Code passes tests
- [ ] Refactored
- [ ] Self-reviewed
→ Next: `/impl-commit`

**COMMIT** - Finalization
- [ ] All tests pass
- [ ] CHANGELOG updated
- [ ] PR created
- [ ] Completion reported
→ Done! Await review.

---

## Quick Commands

| Phase | Command | Layer |
|-------|---------|-------|
| Discover | `/acdm-discover` | Desktop/Code |
| Shape | `/acdm-shape` | Desktop/Code |
| Decide | `/acdm-decide` | Desktop/Code |
| Coordinate | `/acdm-coordinate` | Desktop/Code |
| Status | `/acdm-status` | Desktop/Code |
| Explore | `/impl-explore` | Code |
| Plan | `/impl-plan` | Code |
| Code | `/impl-code` | Code |
| Commit | `/impl-commit` | Code |

---

## Where Am I?

Look for these artifacts:

| Artifact | Phase Complete |
|----------|----------------|
| DISCOVERY_BRIEF.md | DISCOVER ✓ |
| Options analysis in chat | SHAPE ✓ |
| ADR-NNN.md | DECIDE ✓ |
| [task]-instructions.md | COORDINATE ✓ |
| Tests written | CODE (in progress) |
| PR created | COMMIT ✓ |

---

*ACDM v1.0 - Quick Reference*
