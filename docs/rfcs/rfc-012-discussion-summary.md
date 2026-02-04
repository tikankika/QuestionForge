# Pipeline Implementation Discussion Summary

**Date:** 2026-01-22
**Participants:** Niklas + Claude Sonnet
**Related:** RFC-012, WORKFLOW.md Appendix A.1.2

---

## Discussion Flow

### 1. Initial Discovery
Niklas discovered that manual scripts and pipeline don't do the same thing.

### 2. Deep Dive
We verified EVERY step in Appendix A.1.2 through source code analysis.

**Result:**
- 7/9 steps correct ✅
- 2/9 steps incorrect ❌

### 3. Identified Bugs

| Bug | Description | Severity |
|-----|-------------|----------|
| **Validation skipped** | step4_export doesn't validate before export | ⚠️ Medium |
| **Path mapping missing** | apply_resource_mapping() never runs | 🔴 Critical |

---

## Solution Proposals

### Niklas's Proposal
"Let pipeline run scripts directly via subprocess - then we know the result will be the same!"

### RFC-012 Proposal  
"Refactor scripts first so they're importable, then import them."

### Our Decision: HYBRID ✅

**Phase 1 (NOW):** Subprocess
- Quick (1 day)
- Low risk
- Works immediately

**Phase 2 (LATER):** Refactor
- Cleaner architecture
- Better performance
- Takes longer (3-5 days)

---

## Rationale for Hybrid Approach

1. **Critical bug must be fixed NOW**
   - Images don't work in QTI export
   - User impact is high

2. **Subprocess is safe**
   - Scripts already work perfectly
   - No changes needed
   - Perfect isolation

3. **Learn the requirements**
   - Through subprocess we see exactly what's needed
   - Easier to refactor when we know the requirements

4. **Migration path is clear**
   - Phase 1 → Phase 2 well defined
   - Can be done step by step
   - Low risk of introducing new bugs

---

## Next Steps

1. ✅ Update RFC-012 (DONE)
2. [ ] Implement Phase 1 in server.py
3. [ ] Test subprocess approach
4. [ ] Document in WORKFLOW.md
5. [ ] Plan Phase 2 refactoring

---

## Key Insights

1. **"Use filesystem"** - Niklas's reminder to always use Filesystem tools
2. **Scripts are source of truth** - Pipeline should call scripts, not re-implement
3. **Subprocess first is OK** - MVP > Perfection initially
4. **Documentation is critical** - RFC + WORKFLOW.md keeps everything clear

---

*Discussion Summary | 2026-01-22*
