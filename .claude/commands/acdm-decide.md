# DECIDE Phase

You are in the DECIDE phase of ACDM (AI-Collaborative Development Method).

## Prerequisites

- DISCOVER phase complete
- SHAPE phase complete
- Human has chosen an option

## Your Task

Document the decision and create specification for implementation.

## Steps

1. **Confirm Decision**
   - Which option was chosen?
   - Any modifications to the chosen option?

2. **Create ADR (Architecture Decision Record)**
   Location: `docs/adr/ADR-NNN-[title].md`
   
   Include:
   - Context (why decision was needed)
   - Options considered (from SHAPE)
   - Decision (what was chosen)
   - Rationale (why this option)
   - Consequences (what this means)

3. **Create Specification**
   Location: `docs/specs/[feature]-spec.md`
   
   Include:
   - Overview (what we're building)
   - User story
   - Inputs/Outputs
   - Acceptance criteria
   - Edge cases
   - Technical notes
   - Dependencies

4. **Update CHANGELOG**
   Add entry under [Unreleased]

## Rules

- ❌ Do NOT start coding yet
- ✅ Document decision clearly
- ✅ Make spec detailed enough for implementation
- ✅ Include acceptance criteria
- ✅ Identify dependencies

## Output

When DECIDE is complete:
- [ ] ADR written
- [ ] Specification created
- [ ] CHANGELOG updated
- [ ] Ready for COORDINATE

## Next Phase

After docs complete → `/acdm-coordinate` to prepare for implementation.

---

*ACDM v1.0 - Strategic Layer*
