# BUG: write_project_file Overwrites Instead of Appending

**Date:** 2026-01-26
**Component:** qf-scaffolding (M1/M2 tools)
**Severity:** HIGH - Data loss occurred
**Status:** OPEN

---

## Problem

Under M1 Stage 0 (Material Analysis) byggdes `preparation/m1_stage0_materials.md` inkrementellt:
- Material 1 ✅
- Material 2 ✅
- Material 3 ✅
- Material 4 ✅
- Material 5 → **Material 1-4 försvann!**

## Root Cause

`write_project_file` har **ingen append-mode**. Det ersätter alltid hela filens innehåll.

**Fungerande workflow (Material 1-4):**
```
1. read_project_file → får hela innehållet
2. Lägg till nytt material i minnet
3. write_project_file med ALLT (gammalt + nytt)
```

**Felaktigt workflow (Material 5):**
```
1. write_project_file med BARA nytt material
2. → Hela tidigare innehållet försvinner!
```

## Evidence

```
✅ Material 2 tillagt (5323 bytes)
✅ Material 3 tillagt (7956 bytes)
✅ Material 4 klar (10.4 KB)
...
💥 Problem! Material 1-4 förlorades.
```

## Affected File

`/Users/niklaskarlsson/Nextcloud/Courses/ARTI1000X/Test/Kunskapskontroll/Entery_check_modul2_hv_v17/preparation/m1_stage0_materials.md`

## Fix Options

### Option 1: Add append_mode parameter (Recommended)
```typescript
write_project_file({
  content: string,
  path: string,
  append?: boolean  // true = add to end, false = replace (default)
})
```

### Option 2: New append_to_project_file tool
```typescript
append_to_project_file({
  content: string,
  path: string
})
```

### Option 3: Document-only fix
- Update tool description: "WARNING: Replaces entire file"
- Add example of read→modify→write pattern

## Recommendation

**Option 1** - enklast, bakåtkompatibelt, flexibelt.

## Files to Modify

- `packages/qf-scaffolding/src/tools/project_files.ts`
- Tool registration in index.ts

## Impact

M1/M2 bygger dokument inkrementellt. Utan append måste Claude alltid:
1. Läsa hela filen först (token-kostnad)
2. Hålla allt i minnet
3. Skriva allt igen

Risk för exakt denna bugg varje gång.
