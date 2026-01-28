/**
 * M5 MCP Tools (DEPRECATED)
 *
 * @deprecated RFC-016: These static tools are replaced by interactive tools.
 * Use m5_start, m5_approve, m5_teach_format instead.
 *
 * The interactive tools use self-learning format recognition which:
 * - Asks teacher for help when format is unknown
 * - Learns new formats from teacher
 * - Remembers patterns for future use
 *
 * See: m5_interactive_tools.ts
 */

import { z } from "zod";
// NOTE: fs and path no longer used since tools are deprecated
// import * as fs from "fs";
// import * as path from "path";

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

/**
 * @deprecated Use m5_start from m5_interactive_tools.ts instead.
 * RFC-016: Static parsing replaced by self-learning format recognition.
 */
export async function m5Check(
  input: z.infer<typeof m5CheckSchema>
): Promise<M5CheckResult> {
  return {
    success: false,
    error: `DEPRECATED (RFC-016): m5_check ersatt av interaktiva verktyg.

Använd istället:
1. m5_start({ project_path: "${input.project_path}" }) - Startar interaktiv session
2. m5_detect_format(...) - Kontrollerar om format känns igen
3. m5_teach_format(...) - Lär M5 ett nytt format

Se m5_interactive_tools.ts för detaljer.`,
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

/**
 * @deprecated Use m5_start and m5_approve from m5_interactive_tools.ts instead.
 * RFC-016: Static parsing replaced by self-learning format recognition.
 */
export async function m5Generate(
  input: z.infer<typeof m5GenerateSchema>
): Promise<M5GenerateResult> {
  return {
    success: false,
    error: `DEPRECATED (RFC-016): m5_generate ersatt av interaktiva verktyg.

Använd istället:
1. m5_start({ project_path: "${input.project_path}" }) - Startar interaktiv session
2. m5_approve() - Godkänner frågor en i taget
3. m5_finish() - Avslutar sessionen

Fördelen med interaktiva verktyg:
- Formaten lärs in från läraren
- Frågor processas en i taget för granskning
- Okända format hanteras genom dialog

Se m5_interactive_tools.ts för detaljer.`,
  };
}
