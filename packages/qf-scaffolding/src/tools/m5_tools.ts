/**
 * M5 MCP Tools
 *
 * Tools for M5 content completeness checking and QFMD generation.
 */

import { z } from "zod";
import * as fs from "fs";
import * as path from "path";
import {
  parseM3Content,
  getQuestionSummary,
  checkCompleteness,
  formatCompletenessReport,
  generateQFMDFile,
} from "../m5/index.js";

// ============================================================================
// Schemas
// ============================================================================

export const m5CheckSchema = z.object({
  project_path: z.string().describe("Absolute path to the project folder"),
  source_file: z
    .string()
    .optional()
    .describe(
      "Relative path to M3 output file. Default: questions/m3_output.md"
    ),
});

export const m5GenerateSchema = z.object({
  project_path: z.string().describe("Absolute path to the project folder"),
  source_file: z
    .string()
    .optional()
    .describe(
      "Relative path to M3 output file. Default: questions/m3_output.md"
    ),
  output_file: z
    .string()
    .optional()
    .describe(
      "Relative path for QFMD output. Default: questions/m5_output.md"
    ),
  course_code: z
    .string()
    .optional()
    .describe("Course code for identifiers (e.g., ARTI1000X)"),
  title: z.string().optional().describe("Title for the question set"),
  skip_incomplete: z
    .boolean()
    .optional()
    .default(false)
    .describe("Skip questions with completeness errors"),
  overwrite: z
    .boolean()
    .optional()
    .default(false)
    .describe("Overwrite existing output file"),
});

// ============================================================================
// Tool: m5_check
// ============================================================================

export interface M5CheckResult {
  success: boolean;
  error?: string;

  // File info
  source_file?: string;
  source_path?: string;

  // Summary
  total_questions?: number;
  passed_questions?: number;
  questions_with_issues?: number;

  // By severity
  errors?: number;
  warnings?: number;
  info?: number;

  // Distributions
  by_type?: Record<string, number>;
  by_bloom?: Record<string, number>;
  by_difficulty?: Record<string, number>;

  // Report
  report?: string;

  // Status
  ready_for_generation?: boolean;
}

export async function m5Check(
  input: z.infer<typeof m5CheckSchema>
): Promise<M5CheckResult> {
  const projectPath = input.project_path;

  // Determine source file
  const sourceFile = input.source_file || "questions/m3_output.md";
  const sourcePath = path.join(projectPath, sourceFile);

  // Check if source exists
  if (!fs.existsSync(sourcePath)) {
    return {
      success: false,
      error: `Källfil finns inte: ${sourceFile}. Har M3 körts?`,
    };
  }

  // Read content
  let content: string;
  try {
    content = fs.readFileSync(sourcePath, "utf-8");
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `Kunde inte läsa fil: ${message}`,
    };
  }

  // Parse questions
  const questions = parseM3Content(content);

  if (questions.length === 0) {
    return {
      success: false,
      error: "Inga frågor hittades i filen. Kontrollera M3-formatet.",
    };
  }

  // Get summary
  const summary = getQuestionSummary(questions);

  // Check completeness
  const completeness = checkCompleteness(questions);

  // Generate report
  const report = formatCompletenessReport(completeness);

  // Count by severity
  const errors = completeness.issues.filter((i) => i.severity === "error").length;
  const warnings = completeness.issues.filter((i) => i.severity === "warning").length;
  const infos = completeness.issues.filter((i) => i.severity === "info").length;

  return {
    success: true,
    source_file: sourceFile,
    source_path: sourcePath,
    total_questions: summary.total,
    passed_questions: completeness.passedQuestions,
    questions_with_issues: summary.total - completeness.passedQuestions,
    errors,
    warnings,
    info: infos,
    by_type: summary.byType,
    by_bloom: summary.byBloom,
    by_difficulty: summary.byDifficulty,
    report,
    ready_for_generation: completeness.status !== "errors",
  };
}

// ============================================================================
// Tool: m5_generate
// ============================================================================

export interface M5GenerateResult {
  success: boolean;
  error?: string;

  // File info
  source_file?: string;
  output_file?: string;
  output_path?: string;

  // Generation stats
  total_questions?: number;
  generated_questions?: number;
  skipped_questions?: string[];

  // Warnings/errors from generation
  generation_warnings?: string[];
  generation_errors?: string[];

  // Preview (first 500 chars)
  preview?: string;
}

export async function m5Generate(
  input: z.infer<typeof m5GenerateSchema>
): Promise<M5GenerateResult> {
  const projectPath = input.project_path;

  // Determine source file
  const sourceFile = input.source_file || "questions/m3_output.md";
  const sourcePath = path.join(projectPath, sourceFile);

  // Determine output file
  const outputFile = input.output_file || "questions/m5_output.md";
  const outputPath = path.join(projectPath, outputFile);

  // Check if source exists
  if (!fs.existsSync(sourcePath)) {
    return {
      success: false,
      error: `Källfil finns inte: ${sourceFile}. Har M3 körts?`,
    };
  }

  // Check if output exists and overwrite not set
  if (fs.existsSync(outputPath) && !input.overwrite) {
    return {
      success: false,
      error: `Utdatafil finns redan: ${outputFile}. Använd overwrite=true för att skriva över.`,
    };
  }

  // Read content
  let content: string;
  try {
    content = fs.readFileSync(sourcePath, "utf-8");
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `Kunde inte läsa fil: ${message}`,
    };
  }

  // Parse questions
  const questions = parseM3Content(content);

  if (questions.length === 0) {
    return {
      success: false,
      error: "Inga frågor hittades i filen. Kontrollera M3-formatet.",
    };
  }

  // Check completeness first
  const completeness = checkCompleteness(questions);

  // Filter if requested
  let questionsToGenerate = questions;
  const skipped: string[] = [];

  if (input.skip_incomplete) {
    questionsToGenerate = questions.filter((q) => {
      const status = completeness.questionStatus[q.questionNumber];
      if (status && status.status === "errors") {
        skipped.push(q.questionNumber);
        return false;
      }
      return true;
    });
  } else if (completeness.status === "errors") {
    // Don't generate if there are errors and skip_incomplete is false
    return {
      success: false,
      error: `Det finns ${completeness.issues.filter((i) => i.severity === "error").length} fel i frågorna. Använd m5_check för att se detaljer, eller skip_incomplete=true för att hoppa över felaktiga frågor.`,
    };
  }

  // Generate QFMD
  const result = generateQFMDFile(questionsToGenerate, {
    courseCode: input.course_code,
    title: input.title,
    includeHeader: true,
  });

  if (!result.qfmdContent) {
    return {
      success: false,
      error: "Generering misslyckades. Ingen QFMD-innehåll skapades.",
      generation_errors: result.errors,
    };
  }

  // Create output directory if needed
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Write output
  try {
    fs.writeFileSync(outputPath, result.qfmdContent, "utf-8");
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      error: `Kunde inte skriva fil: ${message}`,
    };
  }

  // Combine skipped lists
  const allSkipped = [...new Set([...skipped, ...result.skippedQuestions])];

  return {
    success: true,
    source_file: sourceFile,
    output_file: outputFile,
    output_path: outputPath,
    total_questions: questions.length,
    generated_questions: result.questionCount,
    skipped_questions: allSkipped.length > 0 ? allSkipped : undefined,
    generation_warnings:
      result.warnings.length > 0 ? result.warnings : undefined,
    generation_errors: result.errors.length > 0 ? result.errors : undefined,
    preview: result.qfmdContent.substring(0, 500) + "...",
  };
}
