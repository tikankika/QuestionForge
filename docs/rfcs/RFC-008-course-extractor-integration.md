# RFC-008: Course Extractor MCP Integration

| Field | Value |
|-------|-------|
| Status | Draft |
| Created | 2026-01-20 |
| Author | Niklas Karlsson |
| Context | M1 PDF extraction needs images |
| Relates to | RFC-004, RFC-007 |

## Summary

Integrate `course-extractor-mcp` (Python) med QuestionForge M1 för att extrahera text **och bilder** från PDF-kursmaterial.

## Problem

`read_materials.ts` använder `pdf-parse` som endast extraherar text. Kursmaterial innehåller ofta diagram, figurer och tabeller som är viktiga för att skapa bra frågor.

## Lösning: Claude Orchestration

Två separata MCPs, Claude koordinerar:

```
┌─────────────────────────────────────────────────────────┐
│  course-extractor-mcp (Python, AGPL)                    │
│  └── extract_pdf → text_markdown + images[]            │
└─────────────────────────────────────────────────────────┘
                          │
                    Claude läser
                    bilder (vision)
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  qf-scaffolding (TypeScript, MIT)                       │
│  └── M1 workflow med content från course-extractor     │
└─────────────────────────────────────────────────────────┘
```

## Varför Separation?

1. **AGPL-isolering**: course-extractor använder PyMuPDF (AGPL). Separat repo = ingen licenssmitt.
2. **RFC-004 filosofi**: "Claude läser content, MCP hanterar projekt"
3. **Enkelhet**: Inga MCP-till-MCP-bryggor behövs

## M1 Workflow med Integration

```
Stage 0:
1. Lärare laddar upp PDF
2. Claude anropar: course-extractor.extract_pdf(file_path)
   → Returnerar: { text_markdown, images: [{saved_path}] }
3. Claude läser bilder (multimodal vision)
4. Claude anropar: qf-scaffolding.load_stage(stage=0)
5. Claude analyserar content (text + bildförståelse)
6. Fortsätt M1 workflow enligt RFC-007 Option A
```

## Konfiguration

### Claude Desktop (claude_desktop_config.json)

```json
{
  "mcpServers": {
    "course-extractor": {
      "command": "python",
      "args": ["/path/to/course-extractor-mcp/server.py"]
    },
    "qf-scaffolding": {
      "command": "node",
      "args": ["/path/to/QuestionForge/packages/qf-scaffolding/dist/index.js"]
    }
  }
}
```

## Repos

| Repo | Licens | Syfte |
|------|--------|-------|
| `course-extractor-mcp` | AGPL 3.0 | PDF text+bilder |
| `QuestionForge` | MIT | Scaffolding + Pipeline |

## Implementation

**Ingen kodändring krävs i qf-scaffolding.**

Endast:
1. Dokumentera workflow i M1 instructions
2. Uppdatera Stage 0 prompt att nämna course-extractor

## Verifiering

1. Starta båda MCPs
2. Ladda upp PDF med bilder i Claude Desktop
3. Verifiera att Claude:
   - Anropar extract_pdf först
   - Läser extraherade bilder
   - Fortsätter med M1 workflow

## Decision

- [x] Godkänd för implementation
