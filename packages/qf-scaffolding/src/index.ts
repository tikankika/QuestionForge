#!/usr/bin/env node

/**
 * QF-Scaffolding MCP Server
 *
 * MCP server for M1-M5 methodology guidance with output creation.
 *
 * Tools:
 * - load_stage: Load methodology content for a stage
 * - complete_stage: Complete a stage with optional output creation
 * - read_materials: Read instructional materials from materials/ (RFC-004)
 * - read_reference: Read reference documents from project root (RFC-004)
 * - m5_check: Check M3 output for content completeness
 * - m5_generate: Generate QFMD from M3 output
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
import { saveM1Progress, saveM1ProgressSchema } from "./tools/save_m1_progress.js";
import { writeM1Stage, writeM1StageSchema } from "./tools/write_m1_stage.js";
import {
  readProjectFile,
  readProjectFileSchema,
  writeProjectFile,
  writeProjectFileSchema,
} from "./tools/project_files.js";
import { getStageOutputType } from "./outputs/index.js";
// REMOVED: m5_tools.js imports (m5_check, m5_generate deprecated)
import {
  m5Start,
  m5StartSchema,
  m5Approve,
  m5ApproveSchema,
  m5UpdateField,
  m5UpdateFieldSchema,
  m5Skip,
  m5SkipSchema,
  m5Status,
  m5Finish,
  // REMOVED: m5Fallback, m5SubmitQfmd (replaced by m5_manual)
  // RFC-016: Self-learning format recognition
  m5TeachFormat,
  m5TeachFormatSchema,
  m5ListFormats,
  m5ListFormatsSchema,
  m5DetectFormat,
  m5DetectFormatSchema,
} from "./tools/m5_interactive_tools.js";

// Server version
const VERSION = "0.4.1";

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
      `include the output data and it will be validated, formatted, and saved to preparation/.`,
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
      `⚠️ PRIMÄRT för att LISTA filer i materials/ (filename=null). ` +
      `För PDF-analys: Be användaren LADDA UPP filen till chatten istället - Claude.ai har bättre PDF-läsning! ` +
      `Read mode (filename="X.pdf") är endast FALLBACK om användaren inte kan ladda upp.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        filename: {
          type: ["string", "null"],
          description:
            "null/omit = LIST mode (returnerar filnamn). " +
            "'X.pdf' = READ mode (FALLBACK - be användaren ladda upp istället!).",
        },
        file_pattern: {
          type: "string",
          description:
            "DEPRECATED: Use filename instead. " +
            "Optional glob pattern to filter files in list mode.",
        },
        extract_text: {
          type: "boolean",
          description:
            "Extract text content from files. Default: true. " +
            "Only applies in read mode.",
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
  {
    name: "save_m1_progress",
    description:
      `Save M1 (Material Analysis) progress to preparation/m1_analysis.md. ` +
      `Three actions: (1) add_material - progressive saves during Stage 0 after each PDF; ` +
      `(2) save_stage - saves completed stage output (Stage 0-5); ` +
      `(3) finalize_m1 - marks M1 complete, ready for M2. ` +
      `All stages save to ONE document that grows progressively.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        stage: {
          type: "number",
          minimum: 0,
          maximum: 5,
          description:
            "M1 stage number (0-5). Required for add_material and save_stage actions.",
        },
        action: {
          type: "string",
          enum: ["add_material", "save_stage", "finalize_m1"],
          description:
            "add_material = save after each PDF in Stage 0; " +
            "save_stage = save completed stage output; " +
            "finalize_m1 = mark M1 complete.",
        },
        data: {
          type: "object",
          description:
            "Data to save. Structure depends on action: " +
            "add_material needs {material: {...}}; " +
            "save_stage needs {stage_output: {...}}; " +
            "finalize_m1 needs {final_summary: {...}}.",
          properties: {
            material: {
              type: "object",
              description: "Material analysis data (for add_material action).",
            },
            stage_output: {
              type: "object",
              description: "Stage output data (for save_stage action).",
            },
            final_summary: {
              type: "object",
              description: "Final summary data (for finalize_m1 action).",
            },
          },
        },
      },
      required: ["project_path", "action", "data"],
    },
  },
  {
    name: "write_m1_stage",
    description:
      `Write content directly to an M1 stage file. ` +
      `Each stage gets its own file (m1_stage0_materials.md, m1_stage1_validation.md, etc.). ` +
      `What you write = what gets saved. No transformation. ` +
      `Safe: Won't overwrite existing files unless overwrite=true. ` +
      `Progress is tracked automatically in m1_progress.yaml.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        stage: {
          type: "number",
          minimum: 0,
          maximum: 5,
          description:
            "M1 stage number (0-5). " +
            "0=Materials, 1=Validation, 2=Emphasis, 3=Examples, 4=Misconceptions, 5=Objectives.",
        },
        content: {
          type: "string",
          description:
            "Raw markdown content to write. This is saved EXACTLY as provided. " +
            "Include all analysis, examples, misconceptions, etc. in markdown format.",
        },
        overwrite: {
          type: "boolean",
          description: "Set to true to overwrite existing stage file. Default: false (safe).",
          default: false,
        },
      },
      required: ["project_path", "stage", "content"],
    },
  },
  {
    name: "read_project_file",
    description:
      `Read any file within the project directory. ` +
      `Use this when you need to read files outside of materials/. ` +
      `For example: questions in questions/, outputs in output/, etc. ` +
      `Security: Only allows reading files within the project directory.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        relative_path: {
          type: "string",
          description:
            "Path relative to project folder. Examples: " +
            "'output/questions.md', 'questions/draft.md', 'session.yaml'",
        },
      },
      required: ["project_path", "relative_path"],
    },
  },
  {
    name: "write_project_file",
    description:
      `Write any file within the project directory. ` +
      `Use this when you need to create or update files outside standard folders. ` +
      `Creates parent directories automatically. ` +
      `Security: Only allows writing files within the project directory.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        relative_path: {
          type: "string",
          description:
            "Path relative to project folder. Examples: " +
            "'output/questions.md', 'questions/draft.md'",
        },
        content: {
          type: "string",
          description: "Content to write to the file.",
        },
        create_dirs: {
          type: "boolean",
          description: "Create parent directories if they don't exist. Default: true.",
          default: true,
        },
        overwrite: {
          type: "boolean",
          description: "Overwrite if file exists. Default: true.",
          default: true,
        },
      },
      required: ["project_path", "relative_path", "content"],
    },
  },
  // ========== M5 INTERACTIVE TOOLS (Simplified) ==========
  // REMOVED: m5_check, m5_generate (redundant with m5_start)
  {
    name: "m5_start",
    description:
      `Start M5 interactive session for question-by-question QFMD generation. ` +
      `Parses M3 file with best-effort extraction and shows first question for review. ` +
      `If fields are missing, will ask user to provide them.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder.",
        },
        source_file: {
          type: "string",
          description: "Relative path to M3 file. Default: questions/m3_output.md",
        },
        output_file: {
          type: "string",
          description: "Relative path for QFMD output. Default: questions/m5_output.md",
        },
        course_code: {
          type: "string",
          description: "Course code for identifiers (e.g., ARTI1000X).",
        },
        title: {
          type: "string",
          description: "Title for the question set.",
        },
      },
      required: ["project_path"],
    },
  },
  {
    name: "m5_approve",
    description:
      `Approve current question and write to QFMD file. ` +
      `Optionally provide corrections for any fields. ` +
      `After approval, shows next question for review.`,
    inputSchema: {
      type: "object",
      properties: {
        corrections: {
          type: "object",
          description: "Field corrections: { fieldName: newValue }",
        },
      },
      required: [],
    },
  },
  {
    name: "m5_update_field",
    description:
      `Update a field in the current question. ` +
      `Use this when a field is missing or needs correction before approval.`,
    inputSchema: {
      type: "object",
      properties: {
        field: {
          type: "string",
          description: "Field to update (title, type, stem, answer, feedback.correct, etc.)",
        },
        value: {
          description: "New value for the field",
        },
      },
      required: ["field", "value"],
    },
  },
  {
    name: "m5_skip",
    description:
      `Skip current question and move to next. ` +
      `Skipped questions are not written to output file.`,
    inputSchema: {
      type: "object",
      properties: {
        reason: {
          type: "string",
          description: "Reason for skipping (optional)",
        },
      },
      required: [],
    },
  },
  {
    name: "m5_status",
    description:
      `Get current M5 session status. ` +
      `Shows progress: approved, skipped, pending questions.`,
    inputSchema: {
      type: "object",
      properties: {},
      required: [],
    },
  },
  {
    name: "m5_finish",
    description:
      `Finish M5 session and get summary. ` +
      `Clears session state.`,
    inputSchema: {
      type: "object",
      properties: {},
      required: [],
    },
  },
  {
    name: "m5_manual",
    description:
      `Submit manually-created QFMD when parser can't extract automatically. ` +
      `Use when m5_start returns needs_teacher_help=true. ` +
      `Teacher provides QFMD content directly, written to output file.`,
    inputSchema: {
      type: "object",
      properties: {
        qfmd_content: {
          type: "string",
          description: "Complete QFMD content for the question(s)",
        },
        append: {
          type: "boolean",
          description: "Append to existing file (true) or overwrite (false). Default: true",
          default: true,
        },
      },
      required: ["qfmd_content"],
    },
  },
  // RFC-016: Self-learning format recognition
  {
    name: "m5_teach_format",
    description:
      `Teach M5 to recognize a new question format. ` +
      `Use when m5_start doesn't recognize the format. ` +
      `Teacher defines how source markers map to QFMD fields.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder",
        },
        pattern_name: {
          type: "string",
          description: "Name for this format pattern (e.g., 'M3 Bold Headers')",
        },
        mappings: {
          type: "object",
          description: "Mappings from source markers to QFMD fields",
          additionalProperties: {
            type: "object",
            properties: {
              qfmd_field: {
                type: "string",
                nullable: true,
                description: "QFMD field name or null to skip",
              },
              extraction: {
                type: "string",
                enum: ["single_line", "multiline_until_next", "number", "tags", "skip"],
              },
              transform: {
                type: "string",
                enum: ["prepend_hash", "keep_as_is"],
              },
              required: { type: "boolean" },
            },
          },
        },
        question_separator: {
          type: "string",
          description: "What separates questions (default: ---)",
        },
      },
      required: ["project_path", "pattern_name", "mappings"],
    },
  },
  {
    name: "m5_list_formats",
    description: "List all learned format patterns for M5.",
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder",
        },
      },
      required: ["project_path"],
    },
  },
  {
    name: "m5_detect_format",
    description:
      `Analyze a file to detect its format. ` +
      `Use before m5_start to check if format is recognized.`,
    inputSchema: {
      type: "object",
      properties: {
        project_path: {
          type: "string",
          description: "Absolute path to the project folder",
        },
        source_file: {
          type: "string",
          description: "Relative path to file to analyze",
        },
      },
      required: ["project_path", "source_file"],
    },
  },
  // REMOVED: m5_fallback, m5_submit_qfmd (combined into m5_manual)
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

        // RFC-007: Gate after load_stage - require user approval before proceeding
        const stopGate = [
          `🛑 **STOP - VÄNTA PÅ GODKÄNNANDE**`,
          ``,
          `Metodologin för denna stage visas nedan.`,
          ``,
          `**INSTRUKTION FÖR CLAUDE:**`,
          `1. Presentera en KORT sammanfattning av vad denna stage innebär`,
          `2. Fråga: "Ska vi börja med denna stage?"`,
          `3. VÄNTA på att läraren säger "ok", "ja", "fortsätt" eller liknande`,
          `4. Anropa INGA verktyg förrän läraren godkänt`,
          ``,
          `---`,
          ``,
        ].join("\n");

        // Special warning for M1 Stage 0 (RFC-007: User-driven workflow)
        const m1Stage0Warning = (validatedInput.module === "m1" && validatedInput.stage === 0)
          ? `⚠️ **VIKTIGT: ONE FILE AT A TIME!** Följ "QUICK START FOR TEACHERS" nedan. Analysera EN fil, presentera, vänta på feedback, spara. ALDRIG flera filer samtidigt!\n\n`
          : "";

        const header = [
          stopGate,
          `# ${result.stage?.name}`,
          ``,
          m1Stage0Warning,
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

  // Handle read_materials (RFC-004: updated with list/read modes)
  if (name === "read_materials") {
    try {
      // Validate input
      const validatedInput = readMaterialsSchema.parse(args);

      // Read materials
      const result = await readMaterials(validatedInput);

      if (result.success) {
        const lines: string[] = [];

        if (result.mode === "list") {
          // List mode response
          lines.push(`# Materials in materials/`);
          lines.push(``);
          lines.push(`**Mode:** List (file metadata only)`);
          lines.push(`**Total files:** ${result.total_files}`);
          lines.push(``);

          if (result.files && result.files.length > 0) {
            lines.push(`| # | Filename | Type | Size |`);
            lines.push(`|---|----------|------|------|`);
            result.files.forEach((f, i) => {
              lines.push(`| ${i + 1} | ${f.filename} | ${f.content_type} | ${f.size_bytes.toLocaleString()} bytes |`);
            });
            lines.push(``);
            lines.push(`*Use read_materials(filename="X.pdf") to read a specific file.*`);
          } else {
            lines.push(`*No materials found in materials/*`);
          }
        } else {
          // Read mode response
          lines.push(`# Material: ${result.material?.filename}`);
          lines.push(``);
          lines.push(`**Mode:** Read (single file)`);
          lines.push(`**Type:** ${result.material?.content_type}`);
          lines.push(`**Size:** ${result.material?.size_bytes?.toLocaleString()} bytes`);
          if (result.total_chars) {
            lines.push(`**Characters:** ${result.total_chars.toLocaleString()}`);
          }
          lines.push(``);

          if (result.material?.error) {
            lines.push(`**Error:** ${result.material.error}`);
          } else if (result.material?.text_content) {
            lines.push(`---`);
            lines.push(``);
            lines.push(result.material.text_content);
          }
        }

        return {
          content: [
            {
              type: "text",
              text: lines.join("\n"),
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

  // Handle save_m1_progress (RFC-004: new tool)
  if (name === "save_m1_progress") {
    try {
      // Validate input
      const validatedInput = saveM1ProgressSchema.parse(args);

      // Save progress
      const result = await saveM1Progress(validatedInput);

      if (result.success) {
        const lines: string[] = [];
        const action = validatedInput.action;

        if (action === "add_material") {
          lines.push(`✅ Material saved to m1_analysis.md`);
          lines.push(``);
          lines.push(`**Materials analyzed:** ${result.materials_analyzed}/${result.total_materials}`);
        } else if (action === "save_stage") {
          lines.push(`✅ Stage ${validatedInput.stage} saved to m1_analysis.md`);
          lines.push(``);
          lines.push(`**Stages completed:** ${result.stages_completed.join(", ")}`);
        } else if (action === "finalize_m1") {
          lines.push(`🎉 M1 Complete!`);
          lines.push(``);
          lines.push(`**All stages completed:** ${result.stages_completed.join(", ")}`);
          lines.push(`**Ready for M2:** Yes`);
        }

        lines.push(``);
        lines.push(`**Document:** ${result.document_path}`);

        return {
          content: [
            {
              type: "text",
              text: lines.join("\n"),
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `Error saving M1 progress: ${result.error}`,
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

  // Handle write_m1_stage
  if (name === "write_m1_stage") {
    try {
      // Validate input
      const validatedInput = writeM1StageSchema.parse(args);

      // Write stage
      const result = await writeM1Stage(validatedInput);

      if (result.success) {
        const lines: string[] = [];
        lines.push(`✅ Stage ${validatedInput.stage} written to ${result.file_path}`);
        lines.push(``);
        lines.push(`**Stage:** ${result.stage_name}`);
        lines.push(`**Characters:** ${result.char_count?.toLocaleString()}`);
        lines.push(``);
        lines.push(`**Progress:**`);
        lines.push(`- Completed: ${result.progress?.completed.join(", ") || "none"}`);
        lines.push(`- Pending: ${result.progress?.pending.join(", ") || "none"}`);
        lines.push(`- Status: ${result.progress?.status}`);

        return {
          content: [
            {
              type: "text",
              text: lines.join("\n"),
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `Error writing stage: ${result.error}`,
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

  // Handle read_project_file
  if (name === "read_project_file") {
    try {
      const validatedInput = readProjectFileSchema.parse(args);
      const result = await readProjectFile(validatedInput);

      if (result.success && result.content) {
        const lines: string[] = [];
        lines.push(`# File: ${result.relative_path}`);
        lines.push(``);
        lines.push(`**Size:** ${result.size_bytes?.toLocaleString()} bytes`);
        lines.push(`**Path:** ${result.file_path}`);
        lines.push(``);
        lines.push(`---`);
        lines.push(``);
        lines.push(result.content);

        return {
          content: [
            {
              type: "text",
              text: lines.join("\n"),
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `Error reading file: ${result.error}`,
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

  // Handle write_project_file
  if (name === "write_project_file") {
    try {
      const validatedInput = writeProjectFileSchema.parse(args);
      const result = await writeProjectFile(validatedInput);

      if (result.success) {
        const lines: string[] = [];
        lines.push(`✅ File written: ${result.relative_path}`);
        lines.push(``);
        lines.push(`**Bytes written:** ${result.bytes_written?.toLocaleString()}`);
        lines.push(`**Full path:** ${result.file_path}`);
        if (result.created_dirs) {
          lines.push(`**Created directories:** Yes`);
        }

        return {
          content: [
            {
              type: "text",
              text: lines.join("\n"),
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `Error writing file: ${result.error}`,
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

  // REMOVED: m5_check, m5_generate handlers (use m5_start instead)

  // ========== M5 INTERACTIVE HANDLERS (Simplified) ==========

  // Handle m5_start
  if (name === "m5_start") {
    try {
      const validatedInput = m5StartSchema.parse(args);
      const result = await m5Start(validatedInput);

      // NEW: Handle needs_teacher_help case - ASK TEACHER instead of failing
      if (result.needs_teacher_help) {
        const lines: string[] = [];
        lines.push(`# 🤔 M5 behöver din hjälp!`);
        lines.push(``);
        lines.push(`**Källa:** ${result.source_file}`);
        lines.push(``);
        lines.push(`---`);
        lines.push(``);
        lines.push(result.teacher_question || "");
        lines.push(``);
        lines.push(`---`);
        lines.push(``);
        lines.push(`## Förhandsgranskning av filen (första 30 rader):`);
        lines.push(``);
        lines.push("```markdown");
        lines.push(result.file_preview || "");
        lines.push("```");
        lines.push(``);

        if (result.detected_sections && result.detected_sections.length > 0) {
          lines.push(`## Detekterade sektioner:`);
          lines.push(``);
          for (const s of result.detected_sections) {
            lines.push(`- **Rad ${s.line}:** ${s.content} (confidence: ${s.confidence}%)`);
          }
          lines.push(``);
        }

        lines.push(`---`);
        lines.push(``);
        lines.push(`**Alternativ:**`);
        lines.push(`1. Beskriv hur dina frågor är strukturerade → jag anpassar parsern`);
        lines.push(`2. Använd \`m5_manual\` för att skriva QFMD direkt`);
        lines.push(`3. Justera M3-filen så varje fråga börjar med \`## Question N\` eller \`### QN\``);

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      }

      if (result.success && result.first_question) {
        const q = result.first_question;
        const lines: string[] = [];

        // Get session progress for type info
        const { getProgress: getM5Progress } = await import("./m5/session.js");
        const progress = getM5Progress();

        lines.push(`# M5 Session Started`);
        lines.push(``);
        lines.push(`**Session ID:** ${result.session_id}`);
        lines.push(`**Total Questions:** ${result.total_questions}`);
        lines.push(`**Source:** ${result.source_file}`);
        lines.push(`**Output:** ${result.output_file}`);
        lines.push(``);

        // Show type grouping
        if (progress && progress.typeOrder.length > 0) {
          lines.push(`## Frågor grupperade per typ:`);
          lines.push(``);
          for (const type of progress.typeOrder) {
            const typeProgress = progress.progressByType[type];
            const isCurrent = type === progress.currentType;
            const marker = isCurrent ? "→" : " ";
            lines.push(`${marker} **${type}:** ${typeProgress.total} frågor`);
          }
          lines.push(``);
          lines.push(`*Bearbetar en typ i taget. Nuvarande typ: **${progress.currentType}***`);
          lines.push(``);
        }

        lines.push(`---`);
        lines.push(``);
        lines.push(`## Fråga ${progress?.currentTypeIndex || 1} av ${progress?.questionsInCurrentType || 1} (${progress?.currentType || "unknown"})`);
        lines.push(`### ${q.question_number} - Review`);
        lines.push(``);

        // Show interpretation
        lines.push(`### Min tolkning:`);
        lines.push(``);
        lines.push(`| Fält | Värde | Confidence |`);
        lines.push(`|------|-------|------------|`);
        lines.push(`| **Titel** | ${q.interpretation.title.value || "❓ SAKNAS"} | ${q.interpretation.title.confidence}% |`);
        lines.push(`| **Typ** | ${q.interpretation.type.value || "❓ SAKNAS"} (raw: "${q.interpretation.type.raw}") | ${q.interpretation.type.confidence}% |`);
        lines.push(`| **Frågetext** | ${q.interpretation.stem.preview}... | ${q.interpretation.stem.confidence}% |`);
        lines.push(`| **Alternativ** | ${q.interpretation.options.count} st | ${q.interpretation.options.confidence}% |`);
        lines.push(`| **Svar** | ${q.interpretation.answer.value || "❓ SAKNAS"} | ${q.interpretation.answer.confidence}% |`);
        lines.push(`| **Feedback** | ${q.interpretation.feedback.has_correct ? "✓" : "❌"} correct, ${q.interpretation.feedback.has_incorrect ? "✓" : "❌"} incorrect | |`);
        lines.push(`| **Bloom** | ${q.interpretation.bloom.value || "-"} | |`);
        lines.push(`| **Difficulty** | ${q.interpretation.difficulty.value || "-"} | |`);
        lines.push(`| **Labels** | ${q.interpretation.labels.values.slice(0, 3).join(", ")}${q.interpretation.labels.count > 3 ? "..." : ""} | |`);
        lines.push(``);

        // Questions for user
        if (q.needs_user_input) {
          lines.push(`### ❓ Behöver svar:`);
          lines.push(``);
          for (const question of q.questions_for_user) {
            lines.push(`- ${question}`);
          }
          lines.push(``);
          lines.push(`*Använd m5_update_field för att fylla i saknade fält, sedan m5_approve.*`);
        } else {
          lines.push(`### ✅ Redo för godkännande`);
          lines.push(``);
          lines.push(`*Kör m5_approve för att godkänna och skriva till fil.*`);
        }

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      } else {
        return {
          content: [{ type: "text", text: `Error: ${result.error}` }],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Validation error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Handle m5_approve
  if (name === "m5_approve") {
    try {
      const validatedInput = m5ApproveSchema.parse(args);
      const result = await m5Approve(validatedInput);

      if (result.success) {
        const lines: string[] = [];

        // Get updated progress with type info
        const { getProgress: getM5Progress } = await import("./m5/session.js");
        const progress = getM5Progress();

        lines.push(`✅ **${result.approved_question} godkänd och skriven till fil**`);
        lines.push(``);

        if (progress) {
          // Show type-based progress
          const typeProgress = progress.currentType
            ? progress.progressByType[progress.currentType]
            : null;

          if (typeProgress) {
            lines.push(`**Typ ${progress.currentType}:** ${typeProgress.approved}/${typeProgress.total} godkända`);
          }
          lines.push(`**Totalt:** ${progress.approved}/${progress.total} godkända`);
          lines.push(``);
        }

        if (result.session_complete) {
          lines.push(`🎉 **Session klar!** Alla frågor är behandlade.`);
          lines.push(``);
          lines.push(`*Kör m5_finish för att se sammanfattning.*`);
        } else if (result.next_question) {
          const q = result.next_question;

          // Check if we moved to a new type
          const prevType = q.interpretation.type.value;
          if (progress && progress.currentTypeIndex === 1 && progress.remainingInCurrentType >= 0) {
            // First question of a new type
            lines.push(`---`);
            lines.push(``);
            lines.push(`## Ny frågetyp: **${progress.currentType}**`);
            lines.push(``);
            lines.push(`*${progress.questionsInCurrentType} frågor av denna typ*`);
            lines.push(``);
          }

          lines.push(`---`);
          lines.push(``);
          lines.push(`## Fråga ${progress?.currentTypeIndex || "?"} av ${progress?.questionsInCurrentType || "?"} (${progress?.currentType || "unknown"})`);
          lines.push(`### ${q.question_number} - Review`);
          lines.push(``);

          lines.push(`### Min tolkning:`);
          lines.push(``);
          lines.push(`| Fält | Värde | Confidence |`);
          lines.push(`|------|-------|------------|`);
          lines.push(`| **Titel** | ${q.interpretation.title.value || "❓ SAKNAS"} | ${q.interpretation.title.confidence}% |`);
          lines.push(`| **Typ** | ${q.interpretation.type.value || "❓ SAKNAS"} | ${q.interpretation.type.confidence}% |`);
          lines.push(`| **Frågetext** | ${q.interpretation.stem.preview}... | |`);
          lines.push(`| **Alternativ** | ${q.interpretation.options.count} st | |`);
          lines.push(`| **Svar** | ${q.interpretation.answer.value || "❓ SAKNAS"} | ${q.interpretation.answer.confidence}% |`);
          lines.push(`| **Feedback** | ${q.interpretation.feedback.has_correct ? "✓" : "❌"} correct | |`);
          lines.push(``);

          if (q.needs_user_input) {
            lines.push(`### ❓ Behöver svar:`);
            for (const question of q.questions_for_user) {
              lines.push(`- ${question}`);
            }
            lines.push(``);
          } else {
            lines.push(`### ✅ Redo för godkännande`);
          }
        }

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      } else {
        return {
          content: [{ type: "text", text: `Error: ${result.error}` }],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Validation error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Handle m5_update_field
  if (name === "m5_update_field") {
    try {
      const validatedInput = m5UpdateFieldSchema.parse(args);
      const result = await m5UpdateField(validatedInput);

      if (result.success) {
        const lines: string[] = [];
        lines.push(`✅ **Uppdaterade ${result.updated_field}:** ${JSON.stringify(result.new_value)}`);
        lines.push(``);

        if (result.current_question) {
          const q = result.current_question;
          if (q.needs_user_input && q.questions_for_user.length > 0) {
            lines.push(`**Kvarstående frågor:**`);
            for (const question of q.questions_for_user) {
              lines.push(`- ${question}`);
            }
          } else {
            lines.push(`✅ **Redo för godkännande** - Kör m5_approve`);
          }
        }

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      } else {
        return {
          content: [{ type: "text", text: `Error: ${result.error}` }],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Validation error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Handle m5_skip
  if (name === "m5_skip") {
    try {
      const validatedInput = m5SkipSchema.parse(args);
      const result = await m5Skip(validatedInput);

      if (result.success) {
        const lines: string[] = [];
        lines.push(`⏭️ **Hoppade över ${result.skipped_question}**`);
        lines.push(``);

        if (result.progress) {
          lines.push(`**Progress:** ${result.progress.approved} godkända, ${result.progress.skipped} hoppade över`);
          lines.push(``);
        }

        if (result.session_complete) {
          lines.push(`🎉 **Session klar!**`);
          lines.push(`*Kör m5_finish för sammanfattning.*`);
        } else if (result.next_question) {
          const q = result.next_question;
          lines.push(`---`);
          lines.push(`## ${q.question_number} - Review`);
          lines.push(``);
          lines.push(`| Fält | Värde |`);
          lines.push(`|------|-------|`);
          lines.push(`| **Titel** | ${q.interpretation.title.value || "❓ SAKNAS"} |`);
          lines.push(`| **Typ** | ${q.interpretation.type.value || "❓ SAKNAS"} |`);
          lines.push(`| **Svar** | ${q.interpretation.answer.value || "❓ SAKNAS"} |`);
        }

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      } else {
        return {
          content: [{ type: "text", text: `Error skipping question` }],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Validation error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Handle m5_status
  if (name === "m5_status") {
    try {
      const result = await m5Status();

      // Get detailed progress with type info
      const { getProgress: getM5Progress } = await import("./m5/session.js");
      const progress = getM5Progress();

      const lines: string[] = [];
      lines.push(`# M5 Session Status`);
      lines.push(``);

      if (!result.session_active) {
        lines.push(`**Status:** Ingen aktiv session`);
        lines.push(``);
        lines.push(`*Kör m5_start för att börja.*`);
      } else {
        lines.push(`**Session ID:** ${result.session_id}`);
        lines.push(`**Output:** ${result.output_file}`);
        lines.push(``);

        // Show type-based progress
        if (progress && progress.typeOrder.length > 0) {
          lines.push(`## Progress per typ:`);
          lines.push(``);
          lines.push(`| Typ | Godkända | Kvar | Total |`);
          lines.push(`|-----|----------|------|-------|`);

          for (const type of progress.typeOrder) {
            const tp = progress.progressByType[type];
            const isCurrent = type === progress.currentType;
            const marker = isCurrent ? "→ " : "  ";
            lines.push(`| ${marker}**${type}** | ${tp.approved} | ${tp.pending} | ${tp.total} |`);
          }
          lines.push(``);

          lines.push(`## Nuvarande:`);
          lines.push(``);
          lines.push(`- **Typ:** ${progress.currentType || "Klar"}`);
          lines.push(`- **Fråga:** ${progress.currentTypeIndex} av ${progress.questionsInCurrentType}`);
          lines.push(`- **Kvar i typ:** ${progress.remainingInCurrentType}`);
          lines.push(``);
        }

        if (result.progress) {
          lines.push(`## Totalt:`);
          lines.push(``);
          lines.push(`| Status | Antal |`);
          lines.push(`|--------|-------|`);
          lines.push(`| Godkända | ${result.progress.approved} |`);
          lines.push(`| Hoppade över | ${result.progress.skipped} |`);
          lines.push(`| Kvar | ${result.progress.pending} |`);
          lines.push(`| **Total** | ${result.progress.total} |`);
        }
      }

      return {
        content: [{ type: "text", text: lines.join("\n") }],
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Handle m5_finish
  if (name === "m5_finish") {
    try {
      const result = await m5Finish();

      if (result.success && result.summary) {
        const lines: string[] = [];
        lines.push(`# M5 Session Complete`);
        lines.push(``);
        lines.push(`## Sammanfattning`);
        lines.push(``);
        lines.push(`| Metric | Antal |`);
        lines.push(`|--------|-------|`);
        lines.push(`| Total frågor | ${result.summary.total_questions} |`);
        lines.push(`| Godkända | ${result.summary.approved} |`);
        lines.push(`| Hoppade över | ${result.summary.skipped} |`);
        lines.push(``);
        lines.push(`**Output fil:** ${result.summary.output_file}`);
        lines.push(``);
        lines.push(`---`);
        lines.push(``);
        lines.push(`**Nästa steg:** Kör Step 1 (step1_start) för att validera QFMD.`);

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      } else {
        return {
          content: [{ type: "text", text: `Error: ${result.error}` }],
          isError: true,
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Handle m5_manual (replaces m5_fallback + m5_submit_qfmd)
  if (name === "m5_manual") {
    try {
      const qfmdContent = (args as any).qfmd_content;
      const append = (args as any).append !== false; // Default true

      if (!qfmdContent || typeof qfmdContent !== "string") {
        return {
          content: [{ type: "text", text: `Error: qfmd_content krävs` }],
          isError: true,
        };
      }

      // Validate QFMD has basic structure
      if (!qfmdContent.includes("^type") || !qfmdContent.includes("@field:")) {
        return {
          content: [{
            type: "text",
            text: `⚠️ Varning: QFMD saknar standard-struktur (^type eller @field:).\n\n` +
                  `Förväntad struktur:\n` +
                  "```\n" +
                  `# Q001 Title\n` +
                  `^type essay\n` +
                  `^identifier ES_Q001\n` +
                  `\n@field: question_text\n...\n@end_field\n` +
                  "```\n\n" +
                  `Vill du fortsätta ändå? Använd write_project_file för att skriva direkt.`
          }],
          isError: true,
        };
      }

      // Get session for output path, or use default
      const session = await (await import("./m5/session.js")).getSession();
      const outputPath = session
        ? `${session.projectPath}/${session.outputFile}`
        : null;

      if (!outputPath) {
        return {
          content: [{
            type: "text",
            text: `Ingen aktiv M5-session. Använd write_project_file för att skriva direkt:\n\n` +
                  `write_project_file({ project_path: "...", relative_path: "questions/m5_output.md", content: "..." })`
          }],
          isError: true,
        };
      }

      // Write QFMD to file
      const fs = await import("fs");
      const existingContent = fs.existsSync(outputPath)
        ? fs.readFileSync(outputPath, "utf-8")
        : "";

      const separator = append && existingContent.trim() ? "\n---\n\n" : "";
      const header = !existingContent.trim()
        ? `<!-- QFMD Format - Generated by M5 -->\n<!-- Generated: ${new Date().toISOString()} -->\n\n`
        : "";

      const newContent = append
        ? existingContent + separator + header + qfmdContent
        : header + qfmdContent;

      fs.writeFileSync(outputPath, newContent, "utf-8");

      const lines: string[] = [];
      lines.push(`# ✅ QFMD skriven till fil`);
      lines.push(``);
      lines.push(`**Fil:** ${outputPath}`);
      lines.push(`**Mode:** ${append ? "Append" : "Overwrite"}`);
      lines.push(`**Tecken:** ${qfmdContent.length}`);
      lines.push(``);
      lines.push(`**Nästa steg:** Kör step2_validate för att validera QFMD-formatet.`);

      return {
        content: [{ type: "text", text: lines.join("\n") }],
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Handle m5_teach_format (RFC-016)
  if (name === "m5_teach_format") {
    try {
      const validatedInput = m5TeachFormatSchema.parse(args);
      const result = await m5TeachFormat(validatedInput);

      if (!result.success) {
        return {
          content: [{ type: "text", text: `Error: ${result.error}` }],
          isError: true,
        };
      }

      const lines: string[] = [];
      lines.push(`# M5 Format Pattern Saved`);
      lines.push(``);
      lines.push(`**Pattern ID:** ${result.pattern_id}`);
      lines.push(`**Name:** ${result.pattern_name}`);
      lines.push(``);
      lines.push(`${result.message}`);
      lines.push(``);
      lines.push(`**Detected Markers:**`);
      for (const marker of result.detected_markers || []) {
        lines.push(`- \`${marker}\``);
      }
      lines.push(``);
      lines.push(`**Nästa steg:** Kör \`m5_start\` för att bearbeta frågorna med det nya mönstret.`);

      return {
        content: [{ type: "text", text: lines.join("\n") }],
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Handle m5_list_formats (RFC-016)
  if (name === "m5_list_formats") {
    try {
      const validatedInput = m5ListFormatsSchema.parse(args);
      const result = await m5ListFormats(validatedInput);

      const lines: string[] = [];
      lines.push(`# M5 Learned Format Patterns`);
      lines.push(``);
      lines.push(`**Total:** ${result.total_patterns} mönster`);
      lines.push(``);

      for (const p of result.patterns) {
        lines.push(`## ${p.name} ${p.builtin ? "(inbyggd)" : ""}`);
        lines.push(`- **ID:** ${p.pattern_id}`);
        lines.push(`- **Använd:** ${p.times_used} gånger`);
        lines.push(`- **Frågor processade:** ${p.questions_processed}`);
        lines.push(`- **Detektionsmarkörer:** ${p.detection_markers.join(", ")}`);
        if (p.learned_date) {
          lines.push(`- **Lärd:** ${p.learned_date}`);
        }
        lines.push(``);
      }

      return {
        content: [{ type: "text", text: lines.join("\n") }],
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Handle m5_detect_format (RFC-016)
  if (name === "m5_detect_format") {
    try {
      const validatedInput = m5DetectFormatSchema.parse(args);
      const result = await m5DetectFormat(validatedInput);

      const lines: string[] = [];

      if (result.detected) {
        lines.push(`# Format Detected!`);
        lines.push(``);
        lines.push(`**Pattern:** ${result.pattern_name}`);
        lines.push(`**Confidence:** ${result.confidence}%`);
        lines.push(``);
        lines.push(result.suggestion || "");
      } else {
        lines.push(`# Unknown Format`);
        lines.push(``);
        lines.push(`Hittade dessa möjliga markörer i filen:`);
        for (const marker of result.potential_markers || []) {
          lines.push(`- \`${marker}\``);
        }
        lines.push(``);
        lines.push(`**Förhandsvisning:**`);
        lines.push("```");
        lines.push(result.file_preview || "");
        lines.push("```");
        lines.push(``);
        lines.push(result.suggestion || "");
      }

      return {
        content: [{ type: "text", text: lines.join("\n") }],
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      return {
        content: [{ type: "text", text: `Error: ${errorMessage}` }],
        isError: true,
      };
    }
  }

  // Unknown tool
  return {
    content: [
      {
        type: "text",
        text: `Unknown tool: ${name}. Available tools: load_stage, complete_stage, read_materials, read_reference, save_m1_progress, write_m1_stage, read_project_file, write_project_file, m5_start, m5_approve, m5_update_field, m5_skip, m5_status, m5_finish, m5_manual, m5_teach_format, m5_list_formats, m5_detect_format`,
      },
    ],
    isError: true,
  };
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`QF-Scaffolding MCP Server v${VERSION} running (M1-M5 Interactive)`);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
