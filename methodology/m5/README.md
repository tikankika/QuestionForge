# M5 - QFMD Formatering

## Syfte

M5 är ett **manuellt försteg** till step2_validate. M5 tar oformaterad text från M3 och hjälper läraren att formatera den till korrekt QFMD-format.

## Varför M5 behövs

```
M3 output (oformaterat)
        │
        ▼
┌─────────────────────────────┐
│  M5 (manuellt steg)         │
│  • Visar råtext till lärare │
│  • Lärare + Claude Desktop  │
│    formaterar till QFMD     │
│  • Skriver till fil         │
└─────────────────────────────┘
        │
        ▼
step2_validate (kan nu läsa)
```

**M5 kan INTE anropa parsern** (olika MCP-servrar). Därför behöver M5 egen dokumentation om korrekt format.

## Workflow

### 1. Starta session
```
m5_simple_start({ project_path: "/path/to/project" })
```
Läser `questions/m3_output.md`, splittar vid `---`, visar första blocket.

### 2. För varje block

1. **Läs råinnehållet** som M5 visar
2. **Konsultera FORMAT_REFERENCE.md** för korrekt format
3. **Skapa QFMD** enligt mallen för rätt frågetyp
4. **Spara** med `m5_simple_create({ qfmd: "..." })`

Eller hoppa över med `m5_simple_skip()`.

### 3. Avsluta
```
m5_simple_finish()
```

### 4. Validera
```
step2_validate({ project_path: "..." })
```
Om fel → fixa och kör om.

## Verktyg

| Verktyg | Beskrivning |
|---------|-------------|
| `m5_simple_start` | Starta session, visa första block |
| `m5_simple_current` | Visa aktuellt block igen |
| `m5_simple_create` | Spara QFMD för aktuellt block |
| `m5_simple_skip` | Hoppa över aktuellt block |
| `m5_simple_status` | Visa progress |
| `m5_simple_finish` | Avsluta och visa sammanfattning |

## Viktigt

Se **FORMAT_REFERENCE.md** för exakt format per frågetyp.

Se **SYNC_STATUS.md** för information om synkronisering med parsern.
