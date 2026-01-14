# IMPLEMENT_handoff: Minimal M1 MVP

**Date:** 2026-01-14  
**For:** Claude Code (Windsurf)  
**Priority:** HIGH  
**Related:** ADR-015, qf-scaffolding-spec.md v2.2  
**Estimated Time:** 4-6 hours

---

## Overview

Build minimal qf-scaffolding with ONLY `load_stage` tool for M1 (Material Analysis).

**Scope:** 1 tool, M1 only, no session tracking, no other modules.

**See:** ADR-015-minimal-m1-mvp.md for architecture decision.

---

## Pre-requisites

### Source Files Location

**Methodology files to copy:**
```
/Users/niklaskarlsson/AIED_EdTech_Dev_documentation_projects/Modular QGen - Modular Question Generation Framework/docs/MQG_0.2/

Files needed (8 total):
- MQG_bb1a_Introduction_Framework.md
- MQG_bb1b_Stage0_Material_Analysis.md
- MQG_bb1c_Stage1_Initial_Validation.md  
- MQG_bb1d_Stage2_Emphasis_Refinement.md
- MQG_bb1e_Stage3_Example_Catalog.md
- MQG_bb1f_Stage4_Misconception_Analysis.md
- MQG_bb1g_Stage5_Scope_Objectives.md
- MQG_bb1h_Facilitation_Best_Practices.md
```

**Destination:**
```
/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qf-scaffolding/methodology/m1/
```

---

## TASK 1: Copy Methodology Files

### Step 1.1: Create directory structure

```bash
cd /Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qf-scaffolding
mkdir -p methodology/m1
```

### Step 1.2: Copy and rename files

```bash
SOURCE="/Users/niklaskarlsson/AIED_EdTech_Dev_documentation_projects/Modular QGen - Modular Question Generation Framework/docs/MQG_0.2"
DEST="/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qf-scaffolding/methodology/m1"

# Copy with renaming (remove MQG_ prefix)
cp "$SOURCE/MQG_bb1a_Introduction_Framework.md" "$DEST/bb1a_Introduction_Framework.md"
cp "$SOURCE/MQG_bb1b_Stage0_Material_Analysis.md" "$DEST/bb1b_Stage0_Material_Analysis.md"
cp "$SOURCE/MQG_bb1c_Stage1_Initial_Validation.md" "$DEST/bb1c_Stage1_Initial_Validation.md"
cp "$SOURCE/MQG_bb1d_Stage2_Emphasis_Refinement.md" "$DEST/bb1d_Stage2_Emphasis_Refinement.md"
cp "$SOURCE/MQG_bb1e_Stage3_Example_Catalog.md" "$DEST/bb1e_Stage3_Example_Catalog.md"
cp "$SOURCE/MQG_bb1f_Stage4_Misconception_Analysis.md" "$DEST/bb1f_Stage4_Misconception_Analysis.md"
cp "$SOURCE/MQG_bb1g_Stage5_Scope_Objectives.md" "$DEST/bb1g_Stage5_Scope_Objectives.md"
cp "$SOURCE/MQG_bb1h_Facilitation_Best_Practices.md" "$DEST/bb1h_Facilitation_Best_Practices.md"
```

### Verification

```bash
ls -la methodology/m1/
# Should show 8 .md files
```

---

## TASK 2: Setup package.json

### File: `package.json`

**Location:** `packages/qf-scaffolding/package.json`

```json
{
  "name": "qf-scaffolding",
  "version": "0.1.0",
  "description": "QuestionForge Scaffolding MCP - M1 Minimal MVP",
  "type": "module",
  "main": "build/index.js",
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch",
    "start": "node build/index.js"
  },
  "keywords": [
    "mcp",
    "questionforge",
    "scaffolding",
    "methodology"
  ],
  "author": "Niklas Karlsson",
  "license": "MIT",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.4"
  },
  "devDependencies": {
    "@types/node": "^22.10.2",
    "typescript": "^5.7.2"
  }
}
```

### Install dependencies

```bash
cd /Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qf-scaffolding
npm install
```

---

## TASK 3: Setup tsconfig.json

### File: `tsconfig.json`

**Location:** `packages/qf-scaffolding/tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "lib": ["ES2022"],
    "outDir": "./build",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "build"]
}
```

---

## TASK 4: Implement load_stage Tool

### File: `src/tools/load_stage.ts`

**Location:** `packages/qf-scaffolding/src/tools/load_stage.ts`

```typescript
import { readFile } from "fs/promises";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

// Get __dirname in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Stage mapping for M1
 * Maps stage number (0-7) to filename
 */
const STAGE_FILES: Record<string, Record<number, string>> = {
  m1: {
    0: "bb1a_Introduction_Framework.md",
    1: "bb1b_Stage0_Material_Analysis.md",
    2: "bb1c_Stage1_Initial_Validation.md",
    3: "bb1d_Stage2_Emphasis_Refinement.md",
    4: "bb1e_Stage3_Example_Catalog.md",
    5: "bb1f_Stage4_Misconception_Analysis.md",
    6: "bb1g_Stage5_Scope_Objectives.md",
    7: "bb1h_Facilitation_Best_Practices.md",
  },
};

/**
 * Input for load_stage tool
 */
export interface LoadStageInput {
  module: "m1";
  stage: number; // 0-7
}

/**
 * Result from load_stage tool
 */
export interface LoadStageResult {
  success: boolean;
  content?: string;
  error?: string;
}

/**
 * Load a methodology stage file
 * 
 * @param input - Module and stage to load
 * @returns Content of the methodology file or error
 */
export async function loadStage(
  input: LoadStageInput
): Promise<LoadStageResult> {
  const { module, stage } = input;

  try {
    // Validate inputs
    if (module !== "m1") {
      return {
        success: false,
        error: `Invalid module: ${module}. Only "m1" is supported in MVP.`,
      };
    }

    if (stage < 0 || stage > 7) {
      return {
        success: false,
        error: `Invalid stage: ${stage}. Must be between 0-7.`,
      };
    }

    // Get filename
    const filename = STAGE_FILES[module]?.[stage];
    if (!filename) {
      return {
        success: false,
        error: `No file mapping for module ${module}, stage ${stage}`,
      };
    }

    // Build path: src/tools/ -> ../../methodology/m1/
    const methodologyPath = join(
      __dirname,
      "..",
      "..",
      "methodology",
      module,
      filename
    );

    // Read file
    const content = await readFile(methodologyPath, "utf-8");

    return {
      success: true,
      content,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

/**
 * Get stage name for display
 */
export function getStageName(stage: number): string {
  const names: Record<number, string> = {
    0: "Introduction & Framework",
    1: "Stage 0: Material Analysis",
    2: "Stage 1: Initial Validation",
    3: "Stage 2: Emphasis Refinement",
    4: "Stage 3: Example Catalog",
    5: "Stage 4: Misconception Analysis",
    6: "Stage 5: Scope & Objectives",
    7: "Facilitation Best Practices",
  };
  return names[stage] || `Stage ${stage}`;
}
```

---

## TASK 5: Implement MCP Server

### File: `src/index.ts`

**Location:** `packages/qf-scaffolding/src/index.ts`

```typescript
#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
  Tool,
  TextContent,
  ErrorCode,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import { loadStage, getStageName, LoadStageInput } from "./tools/load_stage.js";

// Create server instance
const server = new Server(
  {
    name: "qf-scaffolding",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Tool definitions
const TOOLS: Tool[] = [
  {
    name: "load_stage",
    description:
      "Load a specific methodology stage from M1 (Material Analysis). " +
      "Stages 0-7 correspond to different parts of the M1 methodology: " +
      "0=Introduction, 1=Stage0 (Material Analysis), 2=Stage1 (Validation), " +
      "3=Stage2 (Emphasis), 4=Stage3 (Examples), 5=Stage4 (Misconceptions), " +
      "6=Stage5 (Scope & Objectives), 7=Best Practices. " +
      "Returns the complete markdown content for that stage. " +
      "USAGE: Load stages sequentially (0→1→2...) as user progresses through M1.",
    inputSchema: {
      type: "object",
      properties: {
        module: {
          type: "string",
          enum: ["m1"],
          description: 'Module to load. Only "m1" available in MVP.',
        },
        stage: {
          type: "number",
          minimum: 0,
          maximum: 7,
          description: "Stage number (0-7). See tool description for mapping.",
        },
      },
      required: ["module", "stage"],
    },
  },
];

// Handle list_tools request
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: TOOLS };
});

// Handle call_tool request
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "load_stage") {
    try {
      // Validate and parse input
      const input: LoadStageInput = {
        module: args?.module as "m1",
        stage: args?.stage as number,
      };

      // Validate types
      if (typeof input.stage !== "number") {
        throw new McpError(
          ErrorCode.InvalidParams,
          `stage must be a number, got ${typeof input.stage}`
        );
      }

      // Load stage
      const result = await loadStage(input);

      if (result.success && result.content) {
        const stageName = getStageName(input.stage);
        return {
          content: [
            {
              type: "text",
              text: `# M1 - ${stageName}\n\n${result.content}`,
            } as TextContent,
          ],
        };
      } else {
        throw new McpError(
          ErrorCode.InternalError,
          result.error || "Failed to load stage"
        );
      }
    } catch (error) {
      if (error instanceof McpError) {
        throw error;
      }
      throw new McpError(
        ErrorCode.InternalError,
        error instanceof Error ? error.message : "Unknown error"
      );
    }
  }

  throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  // Log to stderr (stdout is for MCP protocol)
  console.error("qf-scaffolding MCP Server running (M1 MVP)");
  console.error("Available tools: load_stage");
  console.error("Module: m1 (stages 0-7)");
}

main().catch((error) => {
  console.error("Fatal error starting server:", error);
  process.exit(1);
});
```

---

## TASK 6: Build and Test

### Step 6.1: Build TypeScript

```bash
cd /Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qf-scaffolding
npm run build
```

**Expected output:**
```
> qf-scaffolding@0.1.0 build
> tsc

# Should complete without errors
# Creates build/ directory with .js files
```

### Step 6.2: Verify build output

```bash
ls -la build/
# Should show:
# - index.js
# - index.d.ts
# - tools/load_stage.js
# - tools/load_stage.d.ts
```

### Step 6.3: Test locally (optional)

Create `test_local.js`:

```javascript
import { spawn } from "child_process";

const server = spawn("node", ["build/index.js"], {
  stdio: ["pipe", "pipe", "inherit"],
});

// Initialize
const initReq = {
  jsonrpc: "2.0",
  id: 1,
  method: "initialize",
  params: {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "test", version: "1.0.0" },
  },
};
server.stdin.write(JSON.stringify(initReq) + "\n");

// List tools
setTimeout(() => {
  const listReq = { jsonrpc: "2.0", id: 2, method: "tools/list", params: {} };
  server.stdin.write(JSON.stringify(listReq) + "\n");
}, 100);

// Load stage 0
setTimeout(() => {
  const callReq = {
    jsonrpc: "2.0",
    id: 3,
    method: "tools/call",
    params: { name: "load_stage", arguments: { module: "m1", stage: 0 } },
  };
  server.stdin.write(JSON.stringify(callReq) + "\n");
}, 200);

// Collect output
server.stdout.on("data", (data) => {
  console.log("RESPONSE:", data.toString());
});

// Cleanup
setTimeout(() => {
  server.kill();
  process.exit(0);
}, 1000);
```

Run: `node test_local.js`

---

## TASK 7: Configure Claude Desktop

### File: Claude Desktop Config

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json`

### Add to mcpServers section:

```json
{
  "mcpServers": {
    "qf-scaffolding": {
      "command": "node",
      "args": [
        "/Users/niklaskarlsson/AIED_EdTech_projects/QuestionForge/packages/qf-scaffolding/build/index.js"
      ]
    }
  }
}
```

**IMPORTANT:** Add comma after previous MCP if needed!

### Step 7.2: Restart Claude Desktop

1. Quit Claude Desktop completely (Cmd+Q)
2. Relaunch Claude Desktop
3. Verify "qf-scaffolding" appears in MCP list (hammer icon)

---

## Testing the MVP

### Test 1: Load Introduction

In Claude Desktop conversation:

```
User: "Load M1 introduction"

Expected:
Claude calls: load_stage(module="m1", stage=0)
Claude receives: Full bb1a content
Claude shows: Introduction and asks if ready to continue
```

### Test 2: Progress through stages

```
User: "Start M1"
Claude: load_stage(m1, 0) → shows introduction
User: "Continue"
Claude: load_stage(m1, 1) → shows Stage 0 instructions
Claude: Facilitates Stage 0 dialog (material analysis)
User: "Next stage"
Claude: load_stage(m1, 2) → shows Stage 1 instructions
... etc through all 8 stages ...
```

### Test 3: Error handling

```
User: "Load stage 10"
Claude calls: load_stage(m1, 10)
Expected: Error: "Invalid stage: 10. Must be between 0-7."
```

---

## Completion Checklist

- [ ] bb1a-bb1h files copied to `methodology/m1/`
- [ ] package.json created
- [ ] tsconfig.json created
- [ ] src/tools/load_stage.ts implemented
- [ ] src/index.ts implemented
- [ ] TypeScript compiles without errors (`npm run build`)
- [ ] build/ directory contains .js files
- [ ] Claude Desktop config updated
- [ ] Claude Desktop restarted
- [ ] load_stage tool visible in Claude Desktop
- [ ] Test: load_stage(m1, 0) returns bb1a content
- [ ] Test: Can facilitate M1 dialog

---

## After MVP Complete

### Update Documentation

1. **ROADMAP.md**
   - Mark "Fas 5: qf-scaffolding → M1 MVP: ✅ Klar"
   - Update status table

2. **CHANGELOG.md**
   - Add entry for v0.1.0 (M1 MVP)

3. **ACDM Log**
   - Document completion
   - Note any issues encountered
   - Mark ADR-015 as implemented

### Next Steps (Post-MVP)

1. Test with real user workflow (entry point A)
2. Gather feedback on M1 facilitation
3. Decide: Add session tracking or build M2 next?

---

## Troubleshooting

### Issue: TypeScript compilation errors

**Solution:** Check Node.js version (need 18+), verify @types/node version

### Issue: File not found when loading stage

**Solution:** Check methodology files are in correct location, verify path construction in load_stage.ts

### Issue: Claude Desktop doesn't see tool

**Solution:** Check config JSON syntax, restart Claude Desktop, verify build/ directory exists

---

*Handoff created: 2026-01-14*  
*Estimated time: 4-6 hours*  
*Status: READY FOR IMPLEMENTATION*
