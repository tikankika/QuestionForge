# Pipeline Implementation Discussion Summary

**Date:** 2026-01-22
**Participants:** Niklas + Claude Sonnet
**Related:** RFC-012, WORKFLOW.md Appendix A.1.2

---

## Diskussionens gång

### 1. Initial upptäckt
Niklas upptäckte att manuella scripts och pipeline inte gör samma sak.

### 2. Djupdykning
Vi verifierade VARJE steg i Appendix A.1.2 genom källkodsanalys.

**Resultat:**
- 7/9 steg korrekta ✅
- 2/9 steg inkorrekta ❌

### 3. Identifierade buggar

| Bug | Beskrivning | Allvarlighet |
|-----|-------------|--------------|
| **Validering skippad** | step4_export validerar inte före export | ⚠️ Medium |
| **Path mapping saknas** | apply_resource_mapping() körs aldrig | 🔴 Kritisk |

---

## Lösningsförslag

### Niklas förslag
"Låt pipeline köra scripts direkt via subprocess - så vet vi att det blir samma resultat!"

### RFC-012 förslag  
"Refactor scripts först så de är importerbara, sen importera dem."

### Vårt beslut: HYBRID ✅

**Phase 1 (NU):** Subprocess
- Snabbt (1 dag)
- Låg risk
- Fungerar omedelbart

**Phase 2 (SENARE):** Refactor
- Renare arkitektur
- Bättre performance
- Tar längre tid (3-5 dagar)

---

## Motivering för hybrid approach

1. **Kritisk bug måste fixas NU**
   - Bilder fungerar inte i QTI-export
   - Användarimpact är hög

2. **Subprocess är säkert**
   - Scripts fungerar redan perfekt
   - Inga ändringar behövs
   - Perfekt isolation

3. **Lär oss requirements**
   - Genom subprocess ser vi exakt vad som behövs
   - Enklare att refactora när vi vet kraven

4. **Migration path är klar**
   - Phase 1 → Phase 2 väl definierad
   - Kan göras steg för steg
   - Låg risk att introducera nya buggar

---

## Nästa steg

1. ✅ Uppdatera RFC-012 (KLART)
2. [ ] Implementera Phase 1 i server.py
3. [ ] Testa subprocess approach
4. [ ] Dokumentera i WORKFLOW.md
5. [ ] Planera Phase 2 refactoring

---

## Key insights

1. **"Use filesystem"** - Niklas reminder att alltid använda Filesystem tools
2. **Scripts är source of truth** - Pipeline ska anropa scripts, inte reimplementera
3. **Subprocess först är OK** - MVP > Perfection initialt
4. **Dokumentation är kritisk** - RFC + WORKFLOW.md håller allt tydligt

---

*Discussion Summary | 2026-01-22*
