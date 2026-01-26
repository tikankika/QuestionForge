/**
 * M5 Interactive MCP Tools
 *
 * Question-by-question workflow with human confirmation.
 */

import { z } from "zod";
import * as fs from "fs";
import * as path from "path";
import { parseM3Flexible } from "../m5/flexible_parser.js";
import {
  createSession,
  getSession,
  clearSession,
  getCurrentQuestion,
  approveQuestion,
  skipQuestion,
  getProgress,
  updateField,
  type ParsedInterpretation,
} from "../m5/session.js";

// ============================================================================
// Schemas
// ============================================================================

export const m5StartSchema = z.object({
  project_path: z.string().describe("Absolute path to the project folder"),
  source_file: z
    .string()
    .optional()
    .describe("Relative path to M3 output file. Default: questions/m3_output.md"),
  output_file: z
    .string()
    .optional()
    .describe("Relative path for QFMD output. Default: questions/m5_output.md"),
  course_code: z
    .string()
    .optional()
    .describe("Course code for identifiers (e.g., ARTI1000X)"),
  title: z.string().optional().describe("Title for the question set"),
});

export const m5ApproveSchema = z.object({
  corrections: z
    .record(z.any())
    .optional()
    .describe("Field corrections: { fieldName: newValue }"),
});

export const m5UpdateFieldSchema = z.object({
  field: z.string().describe("Field to update (e.g., 'title', 'type', 'answer')"),
  value: z.any().describe("New value for the field"),
});

export const m5SkipSchema = z.object({
  reason: z.string().optional().describe("Reason for skipping"),
});

// ============================================================================
// Tool: m5_start
// ============================================================================

export interface M5StartResult {
  success: boolean;
  error?: string;
  session_id?: string;
  total_questions?: number;
  source_file?: string;
  output_file?: string;
  first_question?: QuestionReview;
}

export interface QuestionReview {
  question_number: string;
  interpretation: {
    title: { value: string | null; confidence: number; needs_input: boolean };
    type: { value: string | null; confidence: number; raw: string; needs_input: boolean };
    stem: { value: string | null; confidence: number; preview: string };
    options: { count: number; confidence: number; preview: string[] };
    answer: { value: string | null; confidence: number; needs_input: boolean };
    feedback: { has_correct: boolean; has_incorrect: boolean; needs_input: boolean };
    labels: { count: number; values: string[] };
    bloom: { value: string | null };
    difficulty: { value: string | null };
    points: { value: number };
  };
  missing_fields: string[];
  uncertain_fields: string[];
  needs_user_input: boolean;
  questions_for_user: string[];
}

/**
 * Format a question for review.
 */
function formatQuestionReview(q: ParsedInterpretation): QuestionReview {
  const f = q.fields;
  const questions: string[] = [];

  // Determine what needs user input
  const titleNeeds = !f.title.value;
  const typeNeeds = !f.type.value || f.type.confidence < 70;
  const answerNeeds = !f.answer.value;
  const feedbackNeeds = !f.feedback.correct.value && !f.feedback.general.value;

  if (titleNeeds) questions.push("Vad ska frågan heta?");
  if (typeNeeds) questions.push(`Vilken frågetyp? (rådata: "${f.type.raw}")`);
  if (answerNeeds) questions.push("Vad är rätt svar?");
  if (feedbackNeeds) questions.push("Vad är feedback för rätt svar?");

  return {
    question_number: q.questionNumber,
    interpretation: {
      title: {
        value: f.title.value,
        confidence: f.title.confidence,
        needs_input: titleNeeds,
      },
      type: {
        value: f.type.value,
        confidence: f.type.confidence,
        raw: f.type.raw,
        needs_input: typeNeeds,
      },
      stem: {
        value: f.stem.value,
        confidence: f.stem.confidence,
        preview: f.stem.value?.substring(0, 100) || "",
      },
      options: {
        count: f.options.value.length,
        confidence: f.options.confidence,
        preview: f.options.value.slice(0, 3),
      },
      answer: {
        value: f.answer.value,
        confidence: f.answer.confidence,
        needs_input: answerNeeds,
      },
      feedback: {
        has_correct: !!f.feedback.correct.value,
        has_incorrect: Object.keys(f.feedback.incorrect.value).length > 0,
        needs_input: feedbackNeeds,
      },
      labels: {
        count: f.labels.value.length,
        values: f.labels.value,
      },
      bloom: { value: f.bloom.value },
      difficulty: { value: f.difficulty.value },
      points: { value: f.points.value },
    },
    missing_fields: q.missingFields,
    uncertain_fields: q.uncertainFields,
    needs_user_input: questions.length > 0,
    questions_for_user: questions,
  };
}

export async function m5Start(
  input: z.infer<typeof m5StartSchema>
): Promise<M5StartResult> {
  const projectPath = input.project_path;
  const sourceFile = input.source_file || "questions/m3_output.md";
  const outputFile = input.output_file || "questions/m5_output.md";
  const sourcePath = path.join(projectPath, sourceFile);
  const outputPath = path.join(projectPath, outputFile);

  // Check source exists
  if (!fs.existsSync(sourcePath)) {
    return {
      success: false,
      error: `Källfil finns inte: ${sourceFile}`,
    };
  }

  // Read and parse
  let content: string;
  try {
    content = fs.readFileSync(sourcePath, "utf-8");
  } catch (error) {
    return {
      success: false,
      error: `Kunde inte läsa fil: ${error}`,
    };
  }

  // Parse with flexible parser
  const questions = parseM3Flexible(content);

  if (questions.length === 0) {
    return {
      success: false,
      error: "Inga frågor hittades i filen",
    };
  }

  // Clear any existing output file
  if (fs.existsSync(outputPath)) {
    // Backup existing
    const backupPath = outputPath.replace(".md", `_backup_${Date.now()}.md`);
    fs.renameSync(outputPath, backupPath);
  }

  // Create session
  const session = createSession(projectPath, sourceFile, outputFile, questions, {
    courseCode: input.course_code,
    title: input.title,
  });

  // Get first question
  const firstQ = getCurrentQuestion();
  if (!firstQ) {
    return {
      success: false,
      error: "Kunde inte hämta första frågan",
    };
  }

  return {
    success: true,
    session_id: session.sessionId,
    total_questions: questions.length,
    source_file: sourceFile,
    output_file: outputFile,
    first_question: formatQuestionReview(firstQ),
  };
}

// ============================================================================
// Tool: m5_approve
// ============================================================================

export interface M5ApproveResult {
  success: boolean;
  error?: string;
  approved_question?: string;
  written_to_file?: boolean;
  next_question?: QuestionReview;
  progress?: {
    approved: number;
    total: number;
    remaining: number;
  };
  session_complete?: boolean;
}

export async function m5Approve(
  input: z.infer<typeof m5ApproveSchema>
): Promise<M5ApproveResult> {
  const session = getSession();
  if (!session) {
    return { success: false, error: "Ingen aktiv M5-session. Kör m5_start först." };
  }

  const current = getCurrentQuestion();
  if (!current) {
    return { success: false, error: "Ingen fråga att godkänna" };
  }

  // Apply corrections if provided
  if (input.corrections) {
    for (const [field, value] of Object.entries(input.corrections)) {
      updateField(field, value);
    }
  }

  // Check if required fields are still missing
  const currentQ = getCurrentQuestion();
  if (currentQ && currentQ.missingFields.length > 0) {
    // Check which ones are truly required and still missing
    const stillMissing = currentQ.missingFields.filter((f) => {
      const field = (currentQ.fields as any)[f];
      return !field?.value;
    });

    if (stillMissing.length > 0) {
      return {
        success: false,
        error: `Saknar fortfarande: ${stillMissing.join(", ")}. Använd m5_update_field för att fylla i.`,
      };
    }
  }

  // Approve and write to file
  const result = approveQuestion();

  if (!result.success) {
    return { success: false, error: result.error };
  }

  const progress = getProgress();

  // Check if session is complete
  if (!result.nextQuestion) {
    return {
      success: true,
      approved_question: current.questionNumber,
      written_to_file: true,
      session_complete: true,
      progress: progress
        ? {
            approved: progress.approved,
            total: progress.total,
            remaining: 0,
          }
        : undefined,
    };
  }

  return {
    success: true,
    approved_question: current.questionNumber,
    written_to_file: true,
    next_question: formatQuestionReview(result.nextQuestion),
    progress: progress
      ? {
          approved: progress.approved,
          total: progress.total,
          remaining: progress.pending,
        }
      : undefined,
  };
}

// ============================================================================
// Tool: m5_update_field
// ============================================================================

export interface M5UpdateFieldResult {
  success: boolean;
  error?: string;
  updated_field?: string;
  new_value?: any;
  current_question?: QuestionReview;
}

export async function m5UpdateField(
  input: z.infer<typeof m5UpdateFieldSchema>
): Promise<M5UpdateFieldResult> {
  const session = getSession();
  if (!session) {
    return { success: false, error: "Ingen aktiv M5-session" };
  }

  const result = updateField(input.field, input.value);

  if (!result.success) {
    return { success: false, error: result.error };
  }

  const current = getCurrentQuestion();

  return {
    success: true,
    updated_field: input.field,
    new_value: input.value,
    current_question: current ? formatQuestionReview(current) : undefined,
  };
}

// ============================================================================
// Tool: m5_skip
// ============================================================================

export interface M5SkipResult {
  success: boolean;
  skipped_question?: string;
  next_question?: QuestionReview;
  progress?: {
    approved: number;
    skipped: number;
    total: number;
    remaining: number;
  };
  session_complete?: boolean;
}

export async function m5Skip(
  input: z.infer<typeof m5SkipSchema>
): Promise<M5SkipResult> {
  const session = getSession();
  if (!session) {
    return { success: false };
  }

  const current = getCurrentQuestion();
  if (!current) {
    return { success: false };
  }

  const result = skipQuestion(input.reason);

  const progress = getProgress();

  if (!result.nextQuestion) {
    return {
      success: true,
      skipped_question: current.questionNumber,
      session_complete: true,
      progress: progress
        ? {
            approved: progress.approved,
            skipped: progress.skipped,
            total: progress.total,
            remaining: 0,
          }
        : undefined,
    };
  }

  return {
    success: true,
    skipped_question: current.questionNumber,
    next_question: formatQuestionReview(result.nextQuestion),
    progress: progress
      ? {
          approved: progress.approved,
          skipped: progress.skipped,
          total: progress.total,
          remaining: progress.pending,
        }
      : undefined,
  };
}

// ============================================================================
// Tool: m5_status
// ============================================================================

export interface M5StatusResult {
  success: boolean;
  error?: string;
  session_active?: boolean;
  session_id?: string;
  progress?: {
    total: number;
    approved: number;
    skipped: number;
    pending: number;
    current_index: number;
    current_question: string | null;
  };
  output_file?: string;
}

export async function m5Status(): Promise<M5StatusResult> {
  const session = getSession();

  if (!session) {
    return {
      success: true,
      session_active: false,
      error: "Ingen aktiv M5-session. Kör m5_start för att börja.",
    };
  }

  const progress = getProgress();

  return {
    success: true,
    session_active: true,
    session_id: session.sessionId,
    progress: progress
      ? {
          total: progress.total,
          approved: progress.approved,
          skipped: progress.skipped,
          pending: progress.pending,
          current_index: progress.current,
          current_question: progress.currentQuestion,
        }
      : undefined,
    output_file: session.outputFile,
  };
}

// ============================================================================
// Tool: m5_finish
// ============================================================================

export interface M5FinishResult {
  success: boolean;
  error?: string;
  summary?: {
    total_questions: number;
    approved: number;
    skipped: number;
    output_file: string;
  };
}

export async function m5Finish(): Promise<M5FinishResult> {
  const session = getSession();

  if (!session) {
    return { success: false, error: "Ingen aktiv M5-session" };
  }

  const progress = getProgress();

  const summary = {
    total_questions: session.questions.length,
    approved: progress?.approved || 0,
    skipped: progress?.skipped || 0,
    output_file: session.outputFile,
  };

  // Clear session
  clearSession();

  return {
    success: true,
    summary,
  };
}
