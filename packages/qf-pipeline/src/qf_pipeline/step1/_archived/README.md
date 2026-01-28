# Archived Step 1 Files

**Date:** 2026-01-28
**Reason:** Vision A - Minimal Step 1 refactor

## Why Archived

Step 1 was redesigned from ~3700 lines to ~200 lines based on these insights:

1. **Step 2 is now the validator** (source of truth)
2. **Step 3 handles auto-fixes** (mechanical errors)
3. **Router categorizes errors** (pipeline_route tool)
4. **Step 1 only needed for exceptions** (when Step 3 fails)

## Archived Files

| File | Lines | Replacement |
|------|-------|-------------|
| `analyzer.py` | 458 | Step 2 validator |
| `detector.py` | 78 | Not needed |
| `patterns.py` | 465 | Step 3 patterns |
| `prompts.py` | 189 | Simplified prompts |
| `session.py` | 136 | SessionManager |
| `structural_issues.py` | 367 | pipeline_router.py |
| `transformer.py` | 487 | Step 3 auto-fix |
| `step1_tools.py` | 947 | step1_minimal.py |

**Total archived:** ~3127 lines

## What Was Kept

- `frontmatter.py` - Progress tracking (still useful)
- `parser.py` - Parse questions from markdown
- `decision_logger.py` - Log teacher decisions

## Future: RFC-014

Resource handling (images, audio, hotspots) will be addressed in RFC-014.
This archived code may be useful reference for that work.

## Recovery

If needed, these files can be restored from git history or this archive.
