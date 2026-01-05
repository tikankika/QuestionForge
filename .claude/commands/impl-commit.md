# COMMIT Phase (Implementation Layer)

You are in the COMMIT phase of ACDM implementation.

## Prerequisites

- CODE phase complete
- All tests passing
- Code self-reviewed

## Your Task

Finalize the work and deliver for review.

## Steps

1. **Final Test Run**
   - Run full test suite
   - Confirm everything passes
   - Check for regressions

2. **Update CHANGELOG**
   Add entry under `[Unreleased]`:
   ```markdown
   ### Added
   - [New feature/capability]
   
   ### Changed
   - [Modified behavior]
   
   ### Fixed
   - [Bug fix]
   ```

3. **Update Documentation**
   - CLAUDE.md (if new patterns)
   - README (if user-facing changes)
   - API docs (if applicable)

4. **Create PR / Final Commit**
   - Clear title
   - Description with:
     - What was done
     - How to test
     - Related spec/ADR

5. **Report Completion**
   Tell human:
   - What was implemented
   - What tests were added
   - Any deviations from spec
   - Any issues found

## PR Description Template

```markdown
## Summary
[What this PR does]

## Related Documents
- Spec: [link]
- ADR: [link]

## Changes
- [Change 1]
- [Change 2]

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing done

## Checklist
- [ ] Tests pass
- [ ] CHANGELOG updated
- [ ] Documentation updated
- [ ] Self-reviewed
```

## Rules

- ✅ All tests must pass
- ✅ CHANGELOG must be updated
- ✅ Clear commit messages
- ✅ Report any spec deviations
- ❌ Don't merge without review (if team)

## Completion Report Format

```
## Implementation Complete: [Task]

### What was done
- [Summary]

### Tests added
- [Test 1]
- [Test 2]

### Files changed
- [File 1]: [what changed]
- [File 2]: [what changed]

### Deviations from spec
- [Any changes from original spec, or "None"]

### Issues found
- [Any problems discovered, or "None"]

### Ready for
- [ ] Human review
- [ ] Merge
```

## Output

After COMMIT:
- [ ] Tests pass
- [ ] CHANGELOG updated
- [ ] PR created (or final commit)
- [ ] Completion report shared

## Feedback Loop

After delivery:
- Human reviews
- Feedback → back to CODE (if changes needed)
- Or → back to SHAPE (if scope changes)
- Success → Update ADR with "Validated" evidence

---

*ACDM v1.0 - Implementation Layer*
