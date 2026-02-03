# MarkItDown MCP - Komplett Installationsguide

**Version:** 1.1
**Datum:** 2026-01-31
**För:** macOS (anpassningsbar för Windows/Linux)
**Estimerad tid:** 30-45 minuter

---

## INNEHÅLL

1. [Översikt](#översikt)
2. [Förutsättningar](#förutsättningar)
3. [Installation Steg-för-Steg](#installation-steg-för-steg)
4. [Konfiguration för Claude Desktop](#konfiguration-för-claude-desktop)
5. [Testning](#testning)
6. [Kända begränsningar](#kända-begränsningar)
7. [Säkerhetsåtgärder](#säkerhetsåtgärder)
8. [Felsökning](#felsökning)
9. [Underhåll](#underhåll)

---

## ÖVERSIKT

### Vad är MarkItDown MCP?
Microsoft's officiella MCP-server för att konvertera **29+ filformat** till Markdown:
- **Office:** PDF, DOCX, PPTX, XLSX
- **Media:** JPG, PNG, MP3, WAV (med OCR/transkription)
- **Webb:** HTML, RSS, Wikipedia
- **Data:** CSV, JSON, XML, ZIP
- **Publicering:** EPUB, Jupyter notebooks

### Varför i roadmap?
- **Framtida projekt** med fler filformat
- **Backup-lösning** om egen MCP behöver kompletteras
- **Learning opportunity** att jämföra med egen implementation

---

## FÖRUTSÄTTNINGAR

### 1. System Requirements
```bash
# Verifiera Python version (behöver 3.10+)
python3 --version
# Output bör vara: Python 3.10.x eller högre

# Verifiera att Claude Desktop är installerat
# Öppna Claude Desktop app och verifiera att den fungerar
```

### 2. Verktyg som behövs
- **Claude Desktop** (inte webb-versionen claude.ai)
- **Python 3.10+**
- **uv** (Python package manager - rekommenderad av Anthropic)
- **Docker** (valfritt, för isolerad körning)
- **Tesseract OCR** (valfritt, för bildanalys)

### 3. Installera uv (om du inte har det)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verifiera installation
uv --version
```

---

## INSTALLATION STEG-FÖR-STEG

### METOD 1: Standard Python Installation (ENKLAST)

#### Steg 1: Skapa projektmapp
```bash
# Navigera till önskad plats
cd ~/Documents/MCP-Servers

# Skapa mapp för MarkItDown
mkdir markitdown-mcp-server
cd markitdown-mcp-server
```

#### Steg 2: Skapa virtuell miljö
```bash
# Skapa virtuell miljö med uv
uv venv --python=3.12 .venv

# Aktivera miljön
source .venv/bin/activate

# Din prompt bör nu visa (.venv)
```

#### Steg 3: Installera MarkItDown MCP
```bash
# Installera med ALLA format-stöd
uv pip install 'markitdown[all]'

# ELLER installera endast specifika format:
# uv pip install 'markitdown[pdf,docx,pptx,xlsx]'

# Installera MCP-server delen
uv pip install markitdown-mcp
```

#### Steg 4: Verifiera installation
```bash
# Testa MarkItDown CLI
markitdown --version

# Testa MCP server (ska inte ge error)
python -m markitdown_mcp
# Tryck Ctrl+C för att avsluta
```

---

### METOD 2: Docker Installation (SÄKRAST)

#### Steg 1: Bygg Docker image
```bash
# Navigera till arbetsmapp
cd ~/Documents/MCP-Servers
mkdir markitdown-docker
cd markitdown-docker

# Hämta Dockerfile från Microsoft
curl -O https://raw.githubusercontent.com/microsoft/markitdown/main/Dockerfile

# Bygg image
docker build -t markitdown-mcp:latest .
```

#### Steg 2: Testa Docker image
```bash
# Test-kör servern
docker run --rm -i markitdown-mcp:latest

# Testa med en fil
docker run --rm -i -v ~/Downloads:/workdir markitdown-mcp:latest < /workdir/test.pdf
```

---

## KONFIGURATION FÖR CLAUDE DESKTOP

### Hitta konfigurationsfilen

#### macOS:
```bash
# Öppna config-filen i textredigerare
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# ELLER editera direkt:
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### Windows:
```
%APPDATA%\Claude\claude_desktop_config.json
```

#### Linux:
```
~/.config/Claude/claude_desktop_config.json
```

---

### KONFIGURATION - Standard Python

Lägg till detta i `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/DITT-ANVÄNDARNAMN/Documents/MCP-Servers/markitdown-mcp-server",
        "run",
        "markitdown-mcp"
      ],
      "env": {
        "MARKITDOWN_ENABLE_PLUGINS": "false"
      }
    }
  }
}
```

**VIKTIGT:** Byt `/Users/DITT-ANVÄNDARNAMN/` till din faktiska hemkatalog!

**Hitta din path:**
```bash
cd ~/Documents/MCP-Servers/markitdown-mcp-server
pwd
# Kopiera output och använd i config
```

---

### KONFIGURATION - Docker (MED SÄKERHET)

```json
{
  "mcpServers": {
    "markitdown-docker": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v",
        "/Users/DITT-ANVÄNDARNAMN/Nextcloud/Courses:/workdir:ro",
        "markitdown-mcp:latest"
      ]
    }
  }
}
```

**KRITISKA SÄKERHETSDETALJER:**

1. **`:ro` = read-only mount**
   - Servern kan ENDAST läsa filer
   - Kan INTE skriva/ändra/radera
   - ALLTID använd `:ro` för säkerhet!

2. **Begränsa volume mount**
   - Montera ENDAST den mapp du behöver
   - INTE hela `/Users/DITT-ANVÄNDARNAMN`
   - Exempel: Endast `/Courses` eller `/Documents/Teaching`

3. **Exempel med flera mappar:**
```json
{
  "mcpServers": {
    "markitdown-docker": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v",
        "/Users/niklas/Nextcloud/Courses:/courses:ro",
        "-v",
        "/Users/niklas/Documents/Teaching:/teaching:ro",
        "markitdown-mcp:latest"
      ]
    }
  }
}
```

---

## TESTNING

### Steg 1: Starta om Claude Desktop
```bash
# Stäng Claude Desktop helt
# Öppna igen

# Alternativt via kommandorad:
killall Claude
open -a Claude
```

### Steg 2: Verifiera MCP-server
Öppna Claude Desktop och skriv:
```
Vilka MCP-servrar har du tillgång till?
```

Claude bör svara med att "markitdown" är tillgänglig.

### Steg 3: Testa konvertering
```
Använd MarkItDown för att konvertera filen /courses/ARTI1000X/material.pdf till Markdown
```

### Steg 4: Verifiera output
Claude bör:
1. Använda `convert_to_markdown` tool
2. Returnera strukturerad Markdown
3. Bevara headings, tabeller, listor

---

## KÄNDA BEGRÄNSNINGAR

### 1. Bildextraktion fungerar inte i Claude Desktop

**Problem:** När MarkItDown konverterar dokument med bilder, trunkeras base64-datan. Istället för fullständig bilddata visas bara `data:image/png;base64...`

**Symptom:**
- Markdown-output visar `![](data:image/png;base64...)`
- Försök att extrahera bilden misslyckas
- Claude Desktop kan nå max meddelandelängd om man försöker inkludera base64-datan

**Lösning:** Extrahera bilder direkt från Word-filen (som är ett ZIP-arkiv):

```python
import zipfile
import os

docx_path = "/path/to/dokument.docx"
output_dir = "/path/to/output/images"

os.makedirs(output_dir, exist_ok=True)

# Word-filer är ZIP-arkiv
with zipfile.ZipFile(docx_path, 'r') as z:
    media_files = [f for f in z.namelist() if f.startswith('word/media/')]

    for i, media_file in enumerate(media_files, 1):
        ext = os.path.splitext(media_file)[1]
        output_name = f"image{i}{ext}"

        with z.open(media_file) as src:
            with open(os.path.join(output_dir, output_name), 'wb') as dst:
                dst.write(src.read())
```

**Rekommendation:**
| Användning | Verktyg |
|------------|---------|
| Konvertera dokument → markdown text | MarkItDown MCP i Claude Desktop |
| Extrahera bilder | Python-script eller Claude Code |

---

### 2. uv måste anges med full sökväg

**Problem:** Claude Desktop har begränsad PATH. Om `uv` ligger i `~/.local/bin/` hittas den inte.

**Lösning:** Använd full sökväg i konfigurationen:
```json
{
  "command": "/Users/DITT-ANVÄNDARNAMN/.local/bin/uv",
  "args": [...]
}
```

**Hitta din uv-sökväg:**
```bash
which uv
# Output: ~/.local/bin/uv
```

---

## SÄKERHETSÅTGÄRDER

### OBLIGATORISKA ÅTGÄRDER

#### 1. Read-Only Mounts (Docker)
```json
"-v", "/path/to/folder:/workdir:ro"
       ↑                          ↑
       Source folder              READ-ONLY flag (KRITISKT!)
```

#### 2. Begränsa Folder Access
```bash
# DÅLIGT - ger access till allt:
"-v", "/Users/niklas:/workdir:ro"

# BRA - endast kursmaterial:
"-v", "/Users/niklas/Nextcloud/Courses:/workdir:ro"
```

#### 3. Localhost Binding
Om du kör i SSE mode (ej STDIO):
```json
{
  "env": {
    "MARKITDOWN_HOST": "127.0.0.1",
    "MARKITDOWN_PORT": "3000"
  }
}
```
**ALDRIG** `0.0.0.0` - endast `127.0.0.1` (localhost)!

#### 4. Disable Plugins (om osäker)
```json
{
  "env": {
    "MARKITDOWN_ENABLE_PLUGINS": "false"
  }
}
```

---

### REKOMMENDERADE ÅTGÄRDER

#### 1. Regelbundna Uppdateringar
```bash
# Aktivera virtuell miljö
cd ~/Documents/MCP-Servers/markitdown-mcp-server
source .venv/bin/activate

# Uppdatera MarkItDown
uv pip install --upgrade 'markitdown[all]'
uv pip install --upgrade markitdown-mcp

# Verifiera version
markitdown --version
```

**Schema:** Månadsvis eller vid säkerhetsuppdateringar

#### 2. Loggning & Monitoring
Skapa loggfil för debugging:
```bash
# Lägg till i Claude config:
{
  "mcpServers": {
    "markitdown": {
      "command": "uv",
      "args": [...],
      "env": {
        "MARKITDOWN_LOG_FILE": "/Users/niklas/logs/markitdown.log",
        "MARKITDOWN_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### 3. Test Before Production
```bash
# Testa med MCP Inspector först
npm install -g @modelcontextprotocol/inspector

# Kör inspector
npx @modelcontextprotocol/inspector uv --directory ~/Documents/MCP-Servers/markitdown-mcp-server run markitdown-mcp

# Öppna http://localhost:5173 i browser
```

---

## FELSÖKNING

### Problem 1: "Command not found: uv"
**Lösning:**
```bash
# Installera uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Lägg till i PATH (lägg till i ~/.zshrc eller ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"

# Ladda om shell
source ~/.zshrc
```

---

### Problem 2: "Permission denied" (Docker)
**Lösning:**
```bash
# Verifiera Docker kör
docker ps

# Om error, starta Docker Desktop
open -a Docker

# Vänta tills Docker är igång, testa igen
```

---

### Problem 3: Claude ser inte MCP-servern
**Lösning:**
```bash
# 1. Verifiera config-filen syntax
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | python -m json.tool

# Om error = ogiltig JSON, fixa syntax

# 2. Verifiera path
cd /den/path/du/angav
pwd
ls -la

# 3. Starta om Claude helt
killall Claude
sleep 2
open -a Claude
```

---

### Problem 4: "ModuleNotFoundError: markitdown"
**Lösning:**
```bash
# Aktivera rätt virtuell miljö
cd ~/Documents/MCP-Servers/markitdown-mcp-server
source .venv/bin/activate

# Installera igen
uv pip install 'markitdown[all]'
uv pip install markitdown-mcp

# Verifiera
python -c "import markitdown; print(markitdown.__version__)"
```

---

### Problem 5: Filer hittas inte
**Lösning:**

**För Docker:**
```bash
# Verifiera mount path
# I Docker är filer på: /workdir/filnamn.pdf
# INTE på: /Users/niklas/Nextcloud/Courses/filnamn.pdf

# Rätt sätt att referera:
convert_to_markdown("file:///workdir/filnamn.pdf")
```

**För Standard:**
```bash
# Använd absolut path
convert_to_markdown("file:///Users/niklas/Nextcloud/Courses/filnamn.pdf")

# ELLER relativ från hemkatalog
convert_to_markdown("file://~/Nextcloud/Courses/filnamn.pdf")
```

---

## UNDERHÅLL

### Månadsvis Checklista

```bash
# 1. Uppdatera dependencies
cd ~/Documents/MCP-Servers/markitdown-mcp-server
source .venv/bin/activate
uv pip list --outdated

# 2. Installera uppdateringar
uv pip install --upgrade 'markitdown[all]'
uv pip install --upgrade markitdown-mcp

# 3. Testa grundfunktionalitet
echo "Test" > /tmp/test.txt
markitdown /tmp/test.txt

# 4. Rensa gamla loggar (om du har loggning)
rm ~/logs/markitdown-old-*.log

# 5. Dokumentera version
markitdown --version >> ~/logs/markitdown-versions.txt
date >> ~/logs/markitdown-versions.txt
```

### Vid Säkerhetsuppdatering

```bash
# 1. Kolla GitHub för security advisories
open https://github.com/microsoft/markitdown/security/advisories

# 2. Läs release notes
open https://github.com/microsoft/markitdown/releases

# 3. Om kritisk update:
# - Uppdatera OMEDELBART
# - Testa efter uppdatering
# - Dokumentera i din egen changelog
```

---

## RESURSER

### Officiella länkar
- **GitHub:** https://github.com/microsoft/markitdown
- **MCP Package:** https://github.com/microsoft/markitdown/tree/main/packages/markitdown-mcp
- **Issues:** https://github.com/microsoft/markitdown/issues
- **Releases:** https://github.com/microsoft/markitdown/releases

### Community
- **Discussions:** https://github.com/microsoft/markitdown/discussions
- **Security:** https://github.com/microsoft/markitdown/security

### Support
- **Microsoft Support:** opencode@microsoft.com
- **Bug Reports:** https://github.com/microsoft/markitdown/issues/new

---

## CHANGELOG

| Datum | Version | Ändringar |
|-------|---------|-----------|
| 2026-01-31 | 1.1 | Lagt till "Kända begränsningar" - bildextraktion, uv PATH |
| 2026-01-20 | 1.0 | Initial version av guide |

---

**Skapad av:** Niklas Karlsson
**För projekt:** ARTI1000X Kunskapskontroll
**Syfte:** Roadmap för framtida MCP-integration
**Status:** Pending installation
