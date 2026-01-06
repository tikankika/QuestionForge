# QuestionForge qf-pipeline - Implementation Handoff v5

**Datum:** 2026-01-06  
**Syfte:** Handoff till Claude Code för implementation av `init`-verktyg  
**ACDM Status:** IMPLEMENT pågår

---

## KRITISK UPPGIFT: Lägg till `init`-verktyg

### Problem som upptäcktes

Vid testning hoppade Claude över att fråga användaren om fil och mapp innan `step0_start` kördes. Detta bröt hela workflow:en.

### Lösning

Samma mönster som Assessment_suite: ett `init`-verktyg som Claude MÅSTE kalla först och som returnerar instruktioner.

**Referens:** `/Users/niklaskarlsson/AIED_EdTech_projects/Assessment_suite/packages/assessment-mcp/src/tools/init.ts`

---

## Init-verktyg specifikation

### Tool Definition (server.py)

```python
Tool(
    name="init",
    description=(
        "CALL THIS FIRST! Returns critical instructions for using qf-pipeline. "
        "You MUST follow these instructions. "
        "ALWAYS ask user for source_file and output_folder BEFORE calling step0_start. "
        "NEVER use bash/cat/ls - MCP has full file access."
    ),
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)
```

### Handler (server.py)

```python
async def handle_init() -> List[TextContent]:
    """Handle init tool call - return critical instructions."""
    
    instructions = """# QF-Pipeline - Kritiska Instruktioner

## REGLER (MÅSTE FÖLJAS)

1. **FRÅGA ALLTID användaren INNAN du kör step0_start:**
   - "Vilken markdown-fil vill du arbeta med?" (source_file)
   - "Var ska projektet sparas?" (output_folder)
   - Vänta på svar innan du fortsätter!

2. **ANVÄND INTE bash/cat/ls** - qf-pipeline har full filåtkomst

3. **SÄG ALDRIG "ladda upp filen"** - MCP kan läsa filer direkt

4. **FÖLJ PIPELINE-ORDNINGEN:**
   - step0_start → step2_validate → step4_export
   - Validera ALLTID innan export!

## STANDARD WORKFLOW

1. User: "Använd qf-pipeline" / "Exportera till QTI"
2. Claude: "Vilken markdown-fil vill du arbeta med?"
3. User: anger sökväg
4. Claude: "Var ska projektet sparas?"
5. User: anger output-mapp
6. Claude: [step0_start] → Skapar session
7. Claude: [step2_validate] → Validerar
8. Om valid: [step4_export] → Exporterar
   Om invalid: Visa fel, hjälp användaren fixa

## TILLGÄNGLIGA VERKTYG

- init: CALL THIS FIRST (denna instruktion)
- step0_start: Starta ny session eller ladda befintlig
- step0_status: Visa sessionstatus
- step2_validate: Validera markdown-fil
- step2_validate_content: Validera markdown-innehåll
- step4_export: Exportera till QTI-paket
- list_types: Lista stödda frågetyper (16 st)
"""
    
    return [TextContent(
        type="text",
        text=instructions
    )]
```

### Registrera i call_tool

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    try:
        if name == "init":
            return await handle_init()
        elif name == "step0_start":
            # ... existing code
```

---

## Komplett verktygslista efter implementation

```
System:
  init                    # CALL THIS FIRST!

Step 0 (Session):
  step0_start             # Ny eller ladda session
  step0_status            # Visa status

Step 2 (Validator):
  step2_validate          # Validera fil
  step2_validate_content  # Validera innehåll

Step 4 (Export):
  step4_export            # Skapa QTI-paket

Cross-Step:
  list_types              # Frågetyper
```

**Totalt:** 8 verktyg

---

## Implementation steg

### 1. Lägg till init i tool-lista (list_tools)

```python
Tool(
    name="init",
    description="CALL THIS FIRST! Returns critical instructions...",
    inputSchema={"type": "object", "properties": {}, "required": []},
),
```

### 2. Lägg till handler

```python
async def handle_init() -> List[TextContent]:
    # Se ovan för full implementation
```

### 3. Registrera i call_tool

```python
if name == "init":
    return await handle_init()
```

### 4. Testa

```bash
# Starta MCP-server och verifiera att init returnerar instruktioner
```

---

## Förväntat beteende efter implementation

```
User: "Använd qf-pipeline"

Claude: [init] → Läser instruktioner

Claude: "Vilken markdown-fil vill du arbeta med?"

User: "/Users/.../BIOG001X_Fys_v65_5.md"

Claude: "Var ska projektet sparas?"

User: "/Users/.../test_projects/"

Claude: [step0_start] → "Session startad!"

Claude: [step2_validate] → "27 frågor, 2 fel..."
```

---

## Relaterade dokument

- `docs/adr/ADR-007-tool-naming-convention.md` - Init-specifikation tillagd
- Assessment_suite referens: `/Assessment_suite/packages/assessment-mcp/src/tools/init.ts`

---

*Handoff v5 - 2026-01-06*  
*Fokus: Init-verktyg för att säkerställa korrekt workflow*
