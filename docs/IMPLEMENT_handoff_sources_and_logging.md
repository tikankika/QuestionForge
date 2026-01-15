# QuestionForge Filhantering - Implementation Plan

**Status:** BESLUTAD  
**Datum:** 2026-01-14 23:40

---

## ✅ BEKRÄFTADE BESLUT

### 1. qf-pipeline kopierar methodology
- ✅ step0_start kopierar hela methodology/ (28 filer)
- ✅ Sker INNAN load_stage (entry point execution)
- ✅ Projektet blir self-contained

### 2. sources.yaml är LEVANDE
- ❌ INTE manuell ifyllnad
- ✅ Uppdateras LÖPANDE av BÅDA MCP:erna
- ✅ qf-pipeline lägger till vid setup
- ✅ qf-scaffolding lägger till när nya källor upptäcks i M1-M4

### 3. Loggning löpande
- ✅ Måste dokumenteras kontinuerligt
- ✅ Båda MCP:erna loggar

---

## IMPLEMENTATION: Phase 1 (NU)

### qf-pipeline: step0_start uppdateringar

```python
def create_session(entry_point="m1", initial_sources=None):
    """Setup projekt med metodologi + sources."""
    
    # 1. Skapa mappar
    create_folders()  # 00_materials/, methodology/, logs/, ...
    
    # 2. Kopiera metodologi från QuestionForge/methodology/
    copy_methodology()
    
    # 3. Initiera sources.yaml med initial_sources
    if initial_sources:
        update_sources_yaml(initial_sources, append=False)  # Skapa ny
    else:
        create_empty_sources_yaml()
    
    # 4. Setup loggning
    init_logging()
    log_event("session_start", entry_point=entry_point)
    
    # 5. Skapa README + session.yaml
    create_readme_with_wikilinks()
    save_session()
    
    log_event("session_created", methodology_files=28, sources_count=len(initial_sources or []))
    
    return {"success": True, "project_path": str(project_path)}
```

### qf-scaffolding: load_stage uppdateringar

```typescript
async function loadStage(module: string, stage: number, project_path?: string) {
    // 1. Logga stage load
    await log_event(project_path, "stage_loaded", { module, stage });
    
    // 2. Läs från projekt/methodology/ (kopierat av qf-pipeline)
    const content = await readStageContent(project_path, module, stage);
    
    // 3. Om nya källor upptäcks → uppdatera sources.yaml
    if (newSourcesDiscovered) {
        await update_sources_yaml(project_path, newSources, append=true);
        await log_event(project_path, "sources_updated", { count: newSources.length });
    }
    
    return { content, ... };
}
```

---

## SOURCES.YAML: Shared Write Access

### Format med write tracking
```yaml
# sources.yaml (uppdateras av båda MCP:erna)

metadata:
  created_at: "2026-01-14T23:00:00Z"
  created_by: "qf-pipeline:step0_start"
  last_updated: "2026-01-14T23:45:00Z"
  last_updated_by: "qf-scaffolding:load_stage"

sources:
  # Initial källor (från qf-pipeline)
  - id: "src001"
    path: /Users/.../Cellen.txt
    location: nextcloud
    type: lecture_transcript
    added_at: "2026-01-14T23:00:00Z"
    added_by: "qf-pipeline:step0_start"
    metadata:
      date: 2025-10-20
      topic: Cellen
  
  # Upptäckt i M1 Stage 0 (från qf-scaffolding)
  - id: "src002"
    path: /Users/.../Extra_notes.pdf
    location: nextcloud
    type: supplementary_material
    added_at: "2026-01-14T23:45:00Z"
    added_by: "qf-scaffolding:m1:stage0"
    discovered_in: "M1 Stage 0 analysis"
    metadata:
      referenced_in: Cellen.txt line 45
```

### Helper Function (i båda MCP:erna)
```python
def update_sources_yaml(project_path, new_sources, append=True):
    """Uppdatera sources.yaml thread-safe.
    
    Args:
        project_path: Project directory
        new_sources: Lista med nya källor
        append: True=lägg till, False=ersätt
    """
    import fcntl  # File locking
    
    sources_file = project_path / "sources.yaml"
    
    with open(sources_file, 'r+') as f:
        # Lock file för thread-safety
        fcntl.flock(f, fcntl.LOCK_EX)
        
        data = yaml.safe_load(f)
        
        if append:
            data["sources"].extend(new_sources)
        else:
            data["sources"] = new_sources
        
        data["metadata"]["last_updated"] = get_timestamp()
        data["metadata"]["last_updated_by"] = f"{mcp_name}:{tool_name}"
        
        f.seek(0)
        f.truncate()
        yaml.safe_dump(data, f)
        
        fcntl.flock(f, fcntl.LOCK_UN)
```

---

## LOGGNING: Shared Logging Infrastructure

### Logg-struktur
```
projekt/
└── logs/
    ├── session.log           ← Human-readable
    ├── session.jsonl         ← Strukturerad (append-only)
    └── events/
        ├── qf-pipeline.jsonl
        └── qf-scaffolding.jsonl
```

### JSONL Format (append-only, thread-safe)
```jsonl
{"ts":"2026-01-14T23:00:00Z","mcp":"qf-pipeline","tool":"step0_start","event":"session_start","entry_point":"m1"}
{"ts":"2026-01-14T23:00:01Z","mcp":"qf-pipeline","tool":"step0_start","event":"methodology_copied","files":28,"size_mb":1.2}
{"ts":"2026-01-14T23:00:02Z","mcp":"qf-pipeline","tool":"step0_start","event":"sources_init","count":6}
{"ts":"2026-01-14T23:15:00Z","mcp":"qf-scaffolding","tool":"load_stage","event":"stage_loaded","module":"m1","stage":0}
{"ts":"2026-01-14T23:45:00Z","mcp":"qf-scaffolding","tool":"load_stage","event":"sources_updated","added":1,"total":7}
{"ts":"2026-01-14T23:50:00Z","mcp":"qf-scaffolding","tool":"load_stage","event":"m1_stage0_complete","duration_min":35}
```

### Logger Helper (båda MCP:erna)
```python
def log_event(project_path, event_type, **kwargs):
    """Logga event till session.jsonl (append-only)."""
    import json
    from datetime import datetime
    
    log_entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "mcp": "qf-pipeline",  # eller "qf-scaffolding"
        "tool": get_current_tool_name(),
        "event": event_type,
        **kwargs
    }
    
    log_file = project_path / "logs" / "session.jsonl"
    
    # Append-only, thread-safe
    with open(log_file, 'a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps(log_entry) + "\n")
        fcntl.flock(f, fcntl.LOCK_UN)
```

---

## USE CASES: Hur sources.yaml uppdateras

### Use Case 1: Initial Setup (qf-pipeline)
```python
step0_start(
    entry_point="m1",
    initial_sources=[
        {"path": "/Users/.../Cellen.txt", "type": "lecture_transcript"},
        {"path": "/Users/.../Virus.txt", "type": "lecture_transcript"}
    ]
)
# → sources.yaml skapas med 2 källor
```

### Use Case 2: M1 Stage 0 upptäcker ny källa (qf-scaffolding)
```
M1 Stage 0 analyserar Cellen.txt
→ Hittar referens: "Se också extra_notes.pdf"
→ qf-scaffolding uppdaterar sources.yaml automatiskt:
    update_sources_yaml(project_path, [
        {"path": "/Users/.../extra_notes.pdf", 
         "discovered_in": "M1 Stage 0",
         "referenced_in": "Cellen.txt"}
    ], append=True)
```

### Use Case 3: Lärare lägger till manuellt (via Claude)
```
Lärare: "Jag vill lägga till denna presentation också: slides.pdf"
Claude: 
    update_sources_yaml(project_path, [
        {"path": "/Users/.../slides.pdf", 
         "type": "presentation",
         "added_by": "teacher_request"}
    ], append=True)
```

---

## EXEMPEL: M1 Session med sources uppdatering

### Timeline
```
23:00 → step0_start(entry_point="m1", initial_sources=[Cellen, Virus])
        - Kopierar methodology/
        - Skapar sources.yaml med 2 källor
        - Loggar: session_start
        
23:15 → load_stage(module="m1", stage=0)
        - Läser m1_0_intro.md från projekt/methodology/
        - Loggar: stage_loaded
        
23:20 → M1 Stage 0 analys startar
        - Läser Cellen.txt (från sources.yaml)
        - Upptäcker referens till "genetik_summary.pdf"
        - Uppdaterar sources.yaml: +1 källa
        - Loggar: sources_updated
        
23:45 → M1 Stage 0 klar
        - Loggar: m1_stage0_complete
        - sources.yaml har nu 3 källor
```

---

## IMPLEMENTATION TASKS

### qf-pipeline updates
- [ ] 1. Hårdkoda path till QuestionForge/methodology/ (senare: config)
- [ ] 2. copy_methodology() function
- [ ] 3. update_sources_yaml() med file locking
- [ ] 4. log_event() helper
- [ ] 5. create_empty_sources_yaml() med metadata
- [ ] 6. Uppdatera step0_start med initial_sources parameter

### qf-scaffolding updates
- [ ] 1. update_sources_yaml() (TypeScript version)
- [ ] 2. log_event() helper (TypeScript version)
- [ ] 3. Uppdatera load_stage med sources discovery
- [ ] 4. Läs från projekt/methodology/ istället för package

### Shared
- [ ] 1. sources.yaml schema definition
- [ ] 2. JSONL log format spec
- [ ] 3. Event types dokumentation
- [ ] 4. File locking strategy (fcntl vs alternativer)

---

## NEXT STEPS

**Prioritet 1: qf-pipeline (2-3h)**
1. Implementera copy_methodology()
2. Implementera update_sources_yaml() med locking
3. Implementera log_event()
4. Uppdatera step0_start

**Prioritet 2: qf-scaffolding (1-2h)**
1. TypeScript versioner av update_sources_yaml() + log_event()
2. Uppdatera load_stage att läsa från projekt/methodology/

**Prioritet 3: Testing (1h)**
1. Testa step0_start → kopiera metodologi
2. Testa sources.yaml concurrent writes
3. Testa loggning från båda MCP:erna

---

## SUMMARY

**BEKRÄFTAT:**
- ✅ qf-pipeline kopierar methodology vid step0_start
- ✅ INNAN load_stage körs
- ✅ sources.yaml uppdateras LÖPANDE av båda MCP:erna
- ✅ Loggning dokumenteras kontinuerligt

**NÄSTA:**
Implementera qf-pipeline updates först (copy_methodology + sources + logging)

---

*Implementation Plan: 2026-01-14 23:40*  
*Auto-compacted och ready to execute!*
