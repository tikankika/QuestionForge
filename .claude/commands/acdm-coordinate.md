# COORDINATE Phase

You are in the COORDINATE phase of ACDM (AI-Collaborative Development Method).

## Prerequisites

- DECIDE phase complete
- ADR exists
- Specification exists

## Your Task

Prepare everything needed for smooth implementation handoff to Claude Code.

## Steps

1. **Review Readiness**
   - Is spec complete and unambiguous?
   - Are all dependencies identified?
   - Any open questions that must be resolved first?

2. **Create Implementation Instructions**
   Location: `docs/instructions/[task]-instructions.md`
   
   Include:
   - Context (files to read first)
   - Goal (what to build)
   - Project setup (if new project)
   - Implementation steps
   - Key decisions (reference ADRs)
   - Testing strategy
   - Common mistakes to avoid
   - Checkpoints (when to report back)
   - Success criteria

3. **Update CLAUDE.md (if needed)**
   - New patterns established?
   - New conventions?
   - Architecture changes?

4. **Identify Sync Points**
   - When should Code report progress?
   - What decisions need human input during implementation?

## Rules

- ❌ Do NOT start coding (that's Code's job)
- ✅ Make instructions clear and complete
- ✅ Include all context Code needs
- ✅ Define checkpoints for sync
- ✅ Reference specs and ADRs

## Output

When COORDINATE is complete:
- [ ] Implementation instructions written
- [ ] CLAUDE.md updated (if needed)
- [ ] Sync points defined
- [ ] Ready for Claude Code

## Next Phase

Hand off to Claude Code → Implementation (EXPLORE → PLAN → CODE → COMMIT)

---

*ACDM v1.0 - Strategic Layer → Implementation Layer Handoff*
