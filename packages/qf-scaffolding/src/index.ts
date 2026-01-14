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
import { loadStage, loadStageSchema, getAllStages } from "./tools/load_stage.js";

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

// Get stage descriptions for tool documentation
const stageDescriptions = getAllStages("m1")
  .map((s, i) => `${i}: ${s.name}`)
  .join(", ");

// Tool definitions
const TOOLS: Tool[] = [
  {
    name: "load_stage",
    description:
      `Load a methodology stage from M1 (Material Analysis). ` +
      `Returns the complete markdown content plus progress info. ` +
      `Stages: ${stageDescriptions}. ` +
      `Use this to guide the teacher through M1 step by step.`,
    inputSchema: {
      type: "object",
      properties: {
        module: {
          type: "string",
          enum: ["m1"],
          description: "Module to load from. MVP only supports 'm1' (Material Analysis).",
        },
        stage: {
          type: "number",
          minimum: 0,
          maximum: 7,
          description:
            "Stage index (0-7). " +
            "0=Introduction, 1=Stage0 (AI analysis), 2=Stage1 (validation), " +
            "3=Stage2 (emphasis), 4=Stage3 (examples), 5=Stage4 (misconceptions), " +
            "6=Stage5 (objectives), 7=Best Practices.",
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
        const header = [
          `# ${result.stage?.name}`,
          ``,
          `**Modul:** M1 (Material Analysis)`,
          `**Stage:** ${result.stage?.index} av ${result.progress?.totalStages}`,
          `**Estimerad tid:** ${result.stage?.estimatedTime}`,
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
            : `**Status:** M1 komplett!`,
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
  console.error(`QF-Scaffolding MCP Server v${VERSION} running (M1 minimal MVP)`);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
