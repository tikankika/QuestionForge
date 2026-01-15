#!/usr/bin/env node

/**
 * QF-Scaffolding MCP Server
 *
 * Minimal MVP implementation with only load_stage tool for M1 (Material Analysis).
 *
 * This server provides methodology guidance for creating assessment questions
 * through a structured, pedagogical process.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { loadStage, loadStageSchema, getModuleName } from "./tools/load_stage.js";

// Server version
const VERSION = "0.1.0";

// Create MCP server
const server = new Server(
  {
    name: "qf-scaffolding",
    version: VERSION,
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
      `Load a methodology stage from QuestionForge modules. ` +
      `Supports: M1 (Material Analysis), M2 (Assessment Design), M3 (Question Generation), M4 (Quality Assurance). ` +
      `Returns the complete markdown content plus progress info. ` +
      `Use this to guide the teacher through the complete question generation workflow.`,
    inputSchema: {
      type: "object",
      properties: {
        module: {
          type: "string",
          enum: ["m1", "m2", "m3", "m4"],
          description:
            "Module to load from. " +
            "m1=Material Analysis (8 stages), " +
            "m2=Assessment Design (9 stages), " +
            "m3=Question Generation (5 stages), " +
            "m4=Quality Assurance (6 stages).",
        },
        stage: {
          type: "number",
          minimum: 0,
          maximum: 8,
          description:
            "Stage index (0-based). " +
            "M1: 0-7, M2: 0-8, M3: 0-4, M4: 0-5. " +
            "Stage 0 is always Introduction. Last stage is always reference material. " +
            "Middle stages are dialogue-driven with teacher approval gates.",
        },
      },
      required: ["module", "stage"],
    },
  },
];

// Handle tools/list request
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: TOOLS };
});

// Handle tools/call request
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "load_stage") {
    try {
      // Validate input
      const validatedInput = loadStageSchema.parse(args);

      // Load the stage
      const result = await loadStage(validatedInput);

      if (result.success && result.content) {
        // Format response with stage info and content
        const moduleName = result.stage?.module ? getModuleName(result.stage.module) : "Unknown";
        const header = [
          `# ${result.stage?.name}`,
          ``,
          `**Modul:** ${moduleName}`,
          `**Stage:** ${result.stage?.index} av ${result.progress?.totalStages}`,
          `**Estimerad tid:** ${result.stage?.estimatedTime}`,
          result.stage?.requiresApproval === true ? `**Kräver godkännande:** Ja` :
          result.stage?.requiresApproval === "conditional" ? `**Kräver godkännande:** Villkorligt (auto-pass)` :
          `**Kräver godkännande:** Nej`,
          ``,
          `---`,
          ``,
        ].join("\n");

        const footer = [
          ``,
          `---`,
          ``,
          `**Progress:** Stage ${(result.progress?.currentStage ?? 0) + 1}/${result.progress?.totalStages}`,
          result.progress?.remaining && result.progress.remaining.length > 0
            ? `**Återstår:** ${result.progress.remaining.join(" → ")}`
            : `**Status:** ${moduleName} komplett!`,
          ``,
          `**Nästa:** ${result.nextAction}`,
        ].join("\n");

        return {
          content: [
            {
              type: "text",
              text: header + result.content + footer,
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `Error: ${result.error}`,
            },
          ],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [
          {
            type: "text",
            text: `Validation error: ${errorMessage}`,
          },
        ],
        isError: true,
      };
    }
  }

  // Unknown tool
  return {
    content: [
      {
        type: "text",
        text: `Unknown tool: ${name}. Available tools: load_stage`,
      },
    ],
    isError: true,
  };
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`QF-Scaffolding MCP Server v${VERSION} running (M1-M4 support)`);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
