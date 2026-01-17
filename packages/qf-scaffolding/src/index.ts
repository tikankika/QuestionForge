#!/usr/bin/env node

/**
 * QF-Scaffolding MCP Server
 *
 * MCP server for M1-M4 methodology guidance with output creation.
 *
 * Tools:
 * - load_stage: Load methodology content for a stage
 * - complete_stage: Complete a stage with optional output creation
 * - read_materials: Read instructional materials from 00_materials/ (RFC-004)
 * - read_reference: Read reference documents from project root (RFC-004)
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
import { loadStage, loadStageSchema, getModuleName, getToolHintsForStage, formatToolHints } from "./tools/load_stage.js";
import { completeStage, completeStageSchema } from "./tools/complete_stage.js";
import { readMaterials, readMaterialsSchema } from "./tools/read_materials.js";
import { readReference, readReferenceSchema } from "./tools/read_reference.js";
import { getStageOutputType } from "./outputs/index.js";

// Server version
const VERSION = "0.2.0";

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
        project_path: {
          type: "string",
          description:
            "Optional: Absolute path to project folder. " +
            "If provided, stage loads are logged to logs/session.jsonl (RFC-001).",
        },
      },
      required: ["module", "stage"],
    },
  },
  {
    name: "complete_stage",
    description:
      `Complete a methodology stage with optional output creation. ` +
      `Call this when teacher approves a stage and is ready to move on. ` +
      `For stages that produce outputs (learning objectives, misconceptions, etc.), ` +
      `include the output data and it will be validated, formatted, and saved to 01_methodology/.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        module: {
          type: "string",
          enum: ["m1", "m2", "m3", "m4"],
          description: "Module being completed.",
        },
        stage: {
          type: "number",
          minimum: 0,
          maximum: 8,
          description: "Stage index being completed.",
        },
        output: {
          type: "object",
          description:
            "Optional output to create. Include for stages with methodology outputs. " +
            "Type must be: learning_objectives, misconceptions (more in Phase 2).",
          properties: {
            type: {
              type: "string",
              description: "Output type (e.g., 'learning_objectives', 'misconceptions').",
            },
            data: {
              type: "object",
              description: "Structured data for the output (validated against schema).",
            },
          },
          required: ["type", "data"],
        },
        overwrite: {
          type: "boolean",
          description: "Set to true to overwrite existing output file.",
          default: false,
        },
      },
      required: ["project_path", "module", "stage"],
    },
  },
  {
    name: "read_materials",
    description:
      `Read instructional materials from the project's 00_materials/ folder. ` +
      `Supports PDF text extraction, markdown, and text files. ` +
      `Use this to access teaching materials for analysis in M1 Material Analysis. ` +
      `Returns content within the response - no file copying needed.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        file_pattern: {
          type: "string",
          description:
            "Optional glob pattern to filter files (e.g., '*.pdf', 'lecture*'). " +
            "If omitted, all files are returned.",
        },
        extract_text: {
          type: "boolean",
          description:
            "Extract text content from files. Default: true. " +
            "Set to false to only get file metadata.",
          default: true,
        },
      },
      required: ["project_path"],
    },
  },
  {
    name: "read_reference",
    description:
      `Read reference documents from the project root (syllabus, grading criteria, etc.). ` +
      `These are typically saved by step0_start from URLs. ` +
      `Use this to access course context for M1 Material Analysis.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        filename: {
          type: "string",
          description:
            "Specific filename to read (e.g., 'kursplan.md'). " +
            "If omitted, all reference documents are returned.",
        },
      },
      required: ["project_path"],
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

        // Get tool hints for this stage
        const toolHints = getToolHintsForStage(
          validatedInput.module,
          validatedInput.stage
        );
        const toolHintsSection = formatToolHints(toolHints);

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
              text: header + result.content + toolHintsSection + footer,
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

  // Handle complete_stage
  if (name === "complete_stage") {
    try {
      // Validate input
      const validatedInput = completeStageSchema.parse(args);

      // Complete the stage
      const result = await completeStage(validatedInput);

      if (result.success) {
        // Check if output was expected for this stage
        const expectedOutput = getStageOutputType(validatedInput.module, validatedInput.stage);
        const outputNote = result.output_filepath
          ? `\n\n**Output created:** \`${result.output_filepath}\``
          : expectedOutput
          ? `\n\n**Note:** Stage ${validatedInput.stage} typically produces ${expectedOutput} output. Consider providing output data.`
          : '';

        return {
          content: [
            {
              type: "text",
              text: `✅ Stage ${validatedInput.stage} completed for ${validatedInput.module.toUpperCase()}.${outputNote}`,
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `Error completing stage: ${result.error}`,
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

  // Handle read_materials
  if (name === "read_materials") {
    try {
      // Validate input
      const validatedInput = readMaterialsSchema.parse(args);

      // Read materials
      const result = await readMaterials(validatedInput);

      if (result.success) {
        // Format response with material info
        const lines: string[] = [
          `# Materials from 00_materials/`,
          ``,
          `**Total files:** ${result.total_files}`,
          result.total_chars ? `**Total characters:** ${result.total_chars.toLocaleString()}` : '',
          ``,
        ];

        if (result.materials.length === 0) {
          lines.push(`*No materials found.*`);
        } else {
          for (const material of result.materials) {
            lines.push(`## ${material.filename}`);
            lines.push(`- **Type:** ${material.content_type}`);
            lines.push(`- **Size:** ${material.size_bytes.toLocaleString()} bytes`);

            if (material.error) {
              lines.push(`- **Error:** ${material.error}`);
            } else if (material.text_content) {
              lines.push(``);
              lines.push(`### Content`);
              lines.push(``);
              lines.push(material.text_content);
            }
            lines.push(``);
          }
        }

        return {
          content: [
            {
              type: "text",
              text: lines.filter(l => l !== '').join("\n"),
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

  // Handle read_reference
  if (name === "read_reference") {
    try {
      // Validate input
      const validatedInput = readReferenceSchema.parse(args);

      // Read references
      const result = await readReference(validatedInput);

      if (result.success) {
        // Format response
        const lines: string[] = [
          `# Reference Documents`,
          ``,
          `**Total documents:** ${result.references.length}`,
          ``,
        ];

        if (result.references.length === 0) {
          lines.push(`*No reference documents found in project root.*`);
        } else {
          for (const ref of result.references) {
            lines.push(`## ${ref.filename}`);
            if (ref.source_url) {
              lines.push(`- **Source URL:** ${ref.source_url}`);
            }
            lines.push(``);
            lines.push(ref.content);
            lines.push(``);
          }
        }

        return {
          content: [
            {
              type: "text",
              text: lines.filter(l => l !== '').join("\n"),
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
        text: `Unknown tool: ${name}. Available tools: load_stage, complete_stage, read_materials, read_reference`,
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
