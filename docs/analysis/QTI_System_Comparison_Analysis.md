# DJUP JÄMFÖRELSEANALYS: QTI-Generator vs qf-pipeline

## EXECUTIVE SUMMARY

Denna analys jämför två system för QTI-generering:
1. **Terminal QTI Generator** (`/Users/niklaskarlsson/QTI-Generator-for-Inspera/scripts/interactive_qti.py`)
2. **qf-pipeline MCP** (`/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qf-pipeline`)

**Kärnfråga:** Hur skiljer sig första steget i varje system, och vad betyder det för användarupplevelsen?

---

## DEL 1: TERMINAL QTI GENERATOR

### 1.1 Startprocess

```
╭───────────────────────────────────╮
│  QTI Generator - Interaktiv Meny  │
╰───────────────────────────────────╯

▶ Välj MQG folder:

  1. Biologi BIOG001X (Autumn 2025) ✓
  2. TRA265 LP2 2025 ✗
  3. Mate2b001x Autmn 2025 ✓
  4. Biog001x Cellbiologi Genetik 4 ✓
  5. Biog001x Fys ✓

  98. Ange egen sökväg manuellt
  0. Avsluta
```

### 1.2 Styrkor
- Snabb start - Fördefinierade mappar visas direkt
- Visuell status - ✓/✗ indikerar projektets tillstånd
- Enkel navigation - Nummerval kräver minimal inmatning
- Standalone - Kräver ingen AI-integration

### 1.3 Begränsningar
- Statisk konfiguration - Mappar måste fördefinieras
- Ingen AI-assistans - Fel måste åtgärdas manuellt
- Ingen session-hantering - Varje körning är isolerad

---

## DEL 2: qf-pipeline MCP

### 2.1 Styrkor
- AI-assistans - Claude hjälper med felkorrigering
- Session-hantering - Kan pausa och återuppta
- Integrerat validering - Validerar ALLTID innan export
- Felsökning - Claude kan läsa fil och hjälpa fixa problem

### 2.2 Begränsningar
- Kräver Claude - Inte standalone
- Ingen visuell mappöversikt - Måste fråga användaren

---

## DEL 3: GAP-ANALYS

### Vad qf-pipeline SAKNAR

| Feature | Terminal | qf-pipeline | Prioritet |
|---------|----------|-------------|-----------|
| Mappöversikt | ✅ | ❌ | **HÖG** |
| Status-indikatorer | ✅ | ❌ | **HÖG** |
| Nummerval | ✅ | ❌ | MEDIUM |
| Question Set | ✅ | ❌ | LÅG |
| Historik | ✅ | ❌ | LÅG |

---

## DEL 4: REKOMMENDATION

Implementera `list_projects` verktyg i qf-pipeline för att ge samma mappöversikt som Terminal.

---

*Analys skapad: 2026-01-06*
