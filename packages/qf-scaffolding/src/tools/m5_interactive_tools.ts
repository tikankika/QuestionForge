/**
 * M5 Interactive MCP Tools
 *
 * Question-by-question workflow with human confirmation.
 */

import { z } from "zod";
import * as fs from "fs";
import * as path from "path";
// NOTE: flexible_parser.ts removed per RFC-016 (self-learning approach)
// Now using format_learner.ts for all parsing
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
import { logEvent, logError } from "../utils/logger.js";
import {
  loadPatterns,
  savePatterns,
  createPattern,
  findPotentialMarkers,
  detectFormat,
  parseWithPattern,
  parseWithPatternValidated,
  updatePatternStats,
  toQFMD,
  type FieldMapping,
  type FormatPattern,
  type ParsedQuestion,
  type ParseValidation,
} from "../m5/format_learner.js";

// ============================================================================
// Convert ParsedQuestion to ParsedInterpretation
// ============================================================================

/**
 * Convert format_learner's ParsedQuestion to session's ParsedInterpretation.
 * This bridges the RFC-016 self-learning parser with the existing session system.
 *
 * BUG 4 FIX (2026-01-29): Handle more field variants from pattern mappings
 */
function convertToInterpretation(
  pq: ParsedQuestion,
  index: number,
  patternConfidence: number
): ParsedInterpretation {
  const questionNumber = pq.identifier || `Q${String(index + 1).padStart(3, "0")}`;

  // Parse labels string to array
  const labelsArray = pq.labels
    ? pq.labels.split(/\s+/).filter(l => l.startsWith("#")).map(l => l.substring(1))
    : [];

  // BUG 4 FIX: Use bloom/difficulty directly from parsed fields, not just from labels
  const bloomLevels = ["remember", "understand", "apply", "analyze", "evaluate", "create"];
  const difficultyLevels = ["easy", "medium", "hard"];

  // First check direct fields, then labels
  let bloom = pq.bloom || null;
  let difficulty = pq.difficulty || null;

  // If not found directly, try extracting from labels
  if (!bloom) {
    bloom = labelsArray.find(l => bloomLevels.includes(l.toLowerCase())) || null;
  }
  if (!difficulty) {
    difficulty = labelsArray.find(l => difficultyLevels.includes(l.toLowerCase())) || null;
  }

  // BUG 4 FIX: Handle feedback fields properly
  // Prefer specific feedback fields over generic
  const feedbackCorrect = pq.feedback_correct || pq.feedback || null;
  const feedbackIncorrect = pq.feedback_incorrect || null;
  const feedbackGeneral = pq.feedback || pq.feedback_correct || null;

  // Build interpretation
  const interpretation: ParsedInterpretation = {
    questionNumber,
    fields: {
      title: {
        value: pq.title || null,
        confidence: pq.title ? 90 : 0,
        source: pq.title ? "parsed" : "missing",
      },
      type: {
        value: pq.type as any || null,
        confidence: pq.type ? patternConfidence : 0,
        source: pq.type ? "parsed" : "missing",
        raw: pq.type || "",
      },
      stem: {
        value: pq.question_text || null,
        confidence: pq.question_text ? 90 : 0,
        source: pq.question_text ? "parsed" : "missing",
      },
      options: {
        value: [], // Format learner doesn't parse options (yet)
        confidence: 0,
        source: "missing",
      },
      answer: {
        value: pq.answer || null,
        confidence: pq.answer ? 90 : 0,
        source: pq.answer ? "parsed" : "missing",
      },
      feedback: {
        correct: { value: feedbackCorrect, confidence: feedbackCorrect ? 70 : 0 },
        incorrect: { value: feedbackIncorrect ? { default: feedbackIncorrect } : {}, confidence: feedbackIncorrect ? 70 : 0 },
        general: { value: feedbackGeneral, confidence: feedbackGeneral ? 70 : 0 },
      },
      labels: {
        value: labelsArray,
        confidence: labelsArray.length > 0 ? 90 : 0,
        source: labelsArray.length > 0 ? "parsed" : "missing",
      },
      points: {
        value: pq.points || 1,
        confidence: pq.points ? 95 : 50,
        source: pq.points ? "parsed" : "default",
      },
      bloom: {
        value: bloom,
        confidence: bloom ? 90 : 0,
        source: bloom ? (pq.bloom ? "parsed" : "labels") : "missing",
      },
      difficulty: {
        value: difficulty,
        confidence: difficulty ? 90 : 0,
        source: difficulty ? (pq.difficulty ? "parsed" : "labels") : "missing",
      },
    },
    missingFields: [],
    uncertainFields: [],
    rawContent: pq.raw_content,
    lineNumber: 0,
    detectionConfidence: patternConfidence,
    detectionPattern: "format_learner",
  };

  // Determine missing/uncertain fields
  if (!interpretation.fields.title.value) interpretation.missingFields.push("title");
  if (!interpretation.fields.type.value) interpretation.missingFields.push("type");
  if (!interpretation.fields.stem.value) interpretation.missingFields.push("stem");
  if (!interpretation.fields.answer.value) interpretation.uncertainFields.push("answer"); // Not always required
  if (!interpretation.fields.feedback.correct.value) interpretation.uncertainFields.push("feedback");
  if (!interpretation.fields.bloom.value) interpretation.uncertainFields.push("bloom");
  if (!interpretation.fields.difficulty.value) interpretation.uncertainFields.push("difficulty");

  return interpretation;
}

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
  // BUG 6 FIX: Explicit acknowledgment of missing fields
  acknowledge_missing: z
    .boolean()
    .optional()
    .describe("Set to true to acknowledge and proceed despite missing optional fields"),
  force_approve: z
    .boolean()
    .optional()
    .describe("Set to true to force approval despite critical issues (use with caution!)"),
});

export const m5UpdateFieldSchema = z.object({
  field: z.string().describe("Field to update (e.g., 'title', 'type', 'answer')"),
  value: z.any().describe("New value for the field"),
});

export const m5SkipSchema = z.object({
  reason: z.string().optional().describe("Reason for skipping"),
});

export const m5SubmitQfmdSchema = z.object({
  qfmd_content: z.string().describe("Complete QFMD content for the current question"),
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

  // NEW: When parser needs help from teacher
  needs_teacher_help?: boolean;
  teacher_question?: string;
  file_preview?: string;
  detected_sections?: { line: number; content: string; confidence: number }[];
  suggested_action?: string;

  // BUG 3 & 7 FIX: Validation results
  validation_warnings?: string[];
  validation_errors?: string[];
  fields_summary?: {
    total_expected: number;
    total_found: number;
    missing_required: string[];
    missing_optional: string[];
  };

  // BUG 6 FIX: Mandatory STOP point
  requires_teacher_confirmation?: boolean;
  stop_reason?: string;
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

  // BUG 6 & 7 FIX: Warnings and STOP requirement
  warnings?: string[];
  requires_confirmation?: boolean;
  confirmation_reason?: string;
}

/**
 * Format a question for review.
 *
 * BUG 6 & 7 FIX: Add warnings and confirmation requirements
 */
function formatQuestionReview(q: ParsedInterpretation): QuestionReview {
  const f = q.fields;
  const questions: string[] = [];
  const warnings: string[] = [];

  // Determine what needs user input
  const titleNeeds = !f.title.value;
  const typeNeeds = !f.type.value || f.type.confidence < 70;
  const answerNeeds = !f.answer.value;
  const feedbackNeeds = !f.feedback.correct.value && !f.feedback.general.value;
  const stemNeeds = !f.stem.value;

  // BUG 6 FIX: Critical fields that MUST be present
  if (stemNeeds) {
    questions.push("❌ KRITISKT: Frågetexten (Stem) saknas! Vad är frågan?");
  }
  if (titleNeeds) questions.push("Vad ska frågan heta?");
  if (typeNeeds) questions.push(`Vilken frågetyp? (rådata: "${f.type.raw}")`);
  if (answerNeeds) questions.push("Vad är rätt svar?");
  if (feedbackNeeds) questions.push("Vad är feedback för rätt svar?");

  // BUG 7 FIX: Add warnings for missing optional fields
  if (!f.bloom.value) {
    warnings.push("⚠️ Bloom-nivå saknas (rekommenderas för pedagogisk kvalitet)");
  }
  if (!f.difficulty.value) {
    warnings.push("⚠️ Svårighetsgrad saknas (rekommenderas för pedagogisk kvalitet)");
  }
  if (f.labels.value.length === 0) {
    warnings.push("⚠️ Inga etiketter/tags (hjälper med filtrering i Inspera)");
  }

  // BUG 6 FIX: Determine if confirmation is REQUIRED (STOP point)
  const hasCriticalIssues = stemNeeds || titleNeeds || typeNeeds;
  const hasWarnings = warnings.length > 0 || answerNeeds || feedbackNeeds;
  const requiresConfirmation = hasCriticalIssues || hasWarnings;

  let confirmationReason = "";
  if (hasCriticalIssues) {
    confirmationReason = "🛑 STOP: Kritiska fält saknas - kan INTE godkännas utan lärarens input!";
  } else if (hasWarnings) {
    confirmationReason = "⚠️ VARNING: Fält saknas - granska innan godkännande.";
  }

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
    // BUG 6 & 7 FIX: New fields
    warnings: warnings,
    requires_confirmation: requiresConfirmation,
    confirmation_reason: confirmationReason,
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

  // =========================================================================
  // RFC-016: Self-Learning Format Recognition
  // =========================================================================
  // 1. Load learned patterns
  // 2. Try to detect format
  // 3. If detected → parse with that pattern
  // 4. If not detected → ASK TEACHER for help
  // =========================================================================

  const patternsData = loadPatterns(projectPath);
  const detection = detectFormat(content, patternsData.patterns);

  let questions: ParsedInterpretation[];

  // BUG 3 & 7 FIX: Use validated parsing
  let validationResult: ParseValidation | null = null;

  if (detection.detected && detection.pattern) {
    // Format recognized! Parse with the learned pattern + validation
    const parseResult = parseWithPatternValidated(content, detection.pattern);
    const parsedQuestions = parseResult.questions;
    validationResult = parseResult.validation;

    if (parsedQuestions.length === 0) {
      // Pattern matched but no questions found - unusual case
      return {
        success: false,
        needs_teacher_help: true,
        teacher_question: `Formatet "${detection.pattern.name}" kändes igen men inga frågor hittades. Kan du verifiera att filen innehåller frågor?`,
        file_preview: content.split("\n").slice(0, 30).join("\n"),
        detected_sections: [],
        suggested_action: "Kontrollera att frågorna följer det förväntade formatet.",
        source_file: sourceFile,
        validation_errors: validationResult.errors,
      };
    }

    // Convert to ParsedInterpretation format
    questions = parsedQuestions.map((pq, idx) =>
      convertToInterpretation(pq, idx, detection.confidence)
    );

    // Update pattern statistics
    updatePatternStats(projectPath, detection.pattern.pattern_id, questions.length);

    logEvent(projectPath, "", "m5_start", "format_detected", "info", {
      pattern_id: detection.pattern.pattern_id,
      pattern_name: detection.pattern.name,
      confidence: detection.confidence,
      questions_parsed: questions.length,
      validation: {
        is_valid: validationResult.is_valid,
        errors: validationResult.errors.length,
        warnings: validationResult.warnings.length,
      },
    });
  } else {
    // No format detected - need teacher help
    questions = []; // Will trigger the teacher help flow below
  }

  // If no questions found, ASK THE TEACHER FOR HELP instead of failing
  if (questions.length === 0) {
    // Analyze the file to give teacher context
    const lines = content.split("\n");
    const potentialSections: { line: number; content: string; confidence: number }[] = [];

    // Find anything that looks like it could be a question boundary
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      // Headers
      if (/^#+\s+/.test(line)) {
        potentialSections.push({ line: i + 1, content: line.substring(0, 80), confidence: 60 });
      }
      // Separators followed by content
      if (line.trim() === "---" && i + 1 < lines.length && lines[i + 1].trim()) {
        potentialSections.push({ line: i + 1, content: `--- (separator)`, confidence: 40 });
      }
      // Bold markers that often indicate structure
      if (/^\*\*(Title|Type|Stem|Question|Fråga|Titel)/i.test(line)) {
        potentialSections.push({ line: i + 1, content: line.substring(0, 80), confidence: 50 });
      }
    }

    // Create a preview of the file (first 30 lines or so)
    const preview = lines.slice(0, 30).join("\n") + (lines.length > 30 ? "\n..." : "");

    return {
      success: false,
      needs_teacher_help: true,
      teacher_question: `Jag kunde inte automatiskt identifiera frågegränserna i filen.

Kan du hjälpa mig?

**Vad jag letar efter:**
- Frågor som börjar med \`### Q1\`, \`## Question 1\`, \`## Fråga 1\` eller liknande
- Sektioner som \`**Question Stem:**\`, \`**Stem:**\`, \`**Answer:**\`

**Vad jag hittade:**
${potentialSections.length > 0
  ? potentialSections.slice(0, 5).map(s => `- Rad ${s.line}: ${s.content}`).join("\n")
  : "- Inga tydliga sektioner"}

**Hur du kan hjälpa:**
1. Berätta hur frågorna är strukturerade i din fil
2. Eller: Använd \`m5_manual_parse\` för att ange frågegränserna manuellt
3. Eller: Justera M3-filen så varje fråga börjar med \`## Question N\` eller \`### QN\``,
      file_preview: preview,
      detected_sections: potentialSections.slice(0, 10),
      suggested_action: "Beskriv hur dina frågor är strukturerade, så anpassar jag parsningen.",
      source_file: sourceFile,
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

  // Log session start with parse statistics
  const parseStats = {
    total: questions.length,
    auto_ready: questions.filter(q => q.missingFields.length === 0 && q.uncertainFields.length === 0).length,
    needs_input: questions.filter(q => q.missingFields.length > 0).length,
    uncertain: questions.filter(q => q.uncertainFields.length > 0).length,
    by_type: questions.reduce((acc, q) => {
      const t = q.fields.type.value || "unknown";
      acc[t] = (acc[t] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
  };

  logEvent(projectPath, "", "m5_start", "session_started", "info", {
    session_id: session.sessionId,
    source_file: sourceFile,
    output_file: outputFile,
    parse_stats: parseStats,
  });

  // Log parse details for each question
  for (const q of questions) {
    logEvent(projectPath, "", "m5_start", "question_parsed", "debug", {
      question_id: q.questionNumber,
      type: q.fields.type.value,
      type_confidence: q.fields.type.confidence,
      missing_fields: q.missingFields,
      uncertain_fields: q.uncertainFields,
      needs_fallback: q.missingFields.length > 0 || q.uncertainFields.length > 0,
    });
  }

  // Get first question
  const firstQ = getCurrentQuestion();
  if (!firstQ) {
    logError(projectPath, "m5_start", "no_first_question", "Kunde inte hämta första frågan");
    return {
      success: false,
      error: "Kunde inte hämta första frågan",
    };
  }

  // BUG 6 FIX: Check if STOP is required before proceeding
  const firstQuestionReview = formatQuestionReview(firstQ);
  const hasValidationIssues = validationResult && (!validationResult.is_valid || validationResult.warnings.length > 0);

  // Calculate fields summary
  const expectedFieldsPerQuestion = 7; // title, type, stem, answer, feedback, bloom, difficulty
  const totalExpected = questions.length * expectedFieldsPerQuestion;
  const missingRequired = validationResult?.errors || [];
  const missingOptional = validationResult?.warnings || [];

  return {
    success: true,
    session_id: session.sessionId,
    total_questions: questions.length,
    source_file: sourceFile,
    output_file: outputFile,
    first_question: firstQuestionReview,

    // BUG 3 & 7 FIX: Include validation results
    validation_warnings: validationResult?.warnings,
    validation_errors: validationResult?.errors,
    fields_summary: {
      total_expected: totalExpected,
      total_found: validationResult?.fields_found.length || 0,
      missing_required: missingRequired,
      missing_optional: missingOptional.map(w => w.replace(/^Q\d+: /, "")),
    },

    // BUG 6 FIX: STOP requirement
    requires_teacher_confirmation: hasValidationIssues || firstQuestionReview.requires_confirmation,
    stop_reason: hasValidationIssues
      ? `🛑 VALIDERING: ${validationResult?.errors.length || 0} fel, ${validationResult?.warnings.length || 0} varningar. Granska innan du fortsätter!`
      : firstQuestionReview.confirmation_reason,
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

  // BUG 6 FIX: STOP point info
  blocked?: boolean;
  stop_reason?: string;
  missing_critical?: string[];
  missing_optional?: string[];
  action_required?: string;
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

  // Re-fetch after corrections
  const currentQ = getCurrentQuestion();
  if (!currentQ) {
    return { success: false, error: "Kunde inte hämta aktuell fråga" };
  }

  // BUG 6 FIX: Identify critical vs optional missing fields
  const criticalFields = ["title", "type", "stem"];
  const optionalFields = ["answer", "feedback", "bloom", "difficulty"];

  const missingCritical: string[] = [];
  const missingOptional: string[] = [];

  for (const f of criticalFields) {
    const field = (currentQ.fields as any)[f];
    if (!field?.value) {
      missingCritical.push(f);
    }
  }

  for (const f of optionalFields) {
    const field = (currentQ.fields as any)[f];
    const feedbackField = f === "feedback" ? currentQ.fields.feedback : null;
    const hasFeedback = feedbackField && (feedbackField.correct.value || feedbackField.general.value);

    if (f === "feedback" && !hasFeedback) {
      missingOptional.push(f);
    } else if (f !== "feedback" && !field?.value) {
      missingOptional.push(f);
    }
  }

  // BUG 6 FIX: STOP if critical fields missing (unless force_approve)
  if (missingCritical.length > 0 && !input.force_approve) {
    logEvent(session.projectPath, "", "m5_approve", "blocked_critical_missing", "warn", {
      question_id: current.questionNumber,
      missing_critical: missingCritical,
    });

    return {
      success: false,
      blocked: true,
      stop_reason: `🛑 STOP: Kritiska fält saknas!`,
      missing_critical: missingCritical,
      missing_optional: missingOptional,
      action_required: `Använd m5_update_field för att fylla i: ${missingCritical.join(", ")}
Eller sätt force_approve: true för att tvinga godkännande (ej rekommenderat).`,
      error: `Kan inte godkänna: saknar ${missingCritical.join(", ")}`,
    };
  }

  // BUG 6 FIX: Warn if optional fields missing (unless acknowledge_missing)
  if (missingOptional.length > 0 && !input.acknowledge_missing && !input.force_approve) {
    logEvent(session.projectPath, "", "m5_approve", "warning_optional_missing", "info", {
      question_id: current.questionNumber,
      missing_optional: missingOptional,
    });

    return {
      success: false,
      blocked: true,
      stop_reason: `⚠️ VARNING: Rekommenderade fält saknas`,
      missing_critical: [],
      missing_optional: missingOptional,
      action_required: `Fyll i med m5_update_field: ${missingOptional.join(", ")}
Eller sätt acknowledge_missing: true för att fortsätta ändå.`,
      error: `Saknar rekommenderade fält: ${missingOptional.join(", ")}. Sätt acknowledge_missing: true för att fortsätta.`,
    };
  }

  // Approve and write to file
  const result = approveQuestion();

  if (!result.success) {
    logError(session.projectPath, "m5_approve", "approve_failed", result.error || "Unknown error", {
      question_id: current.questionNumber,
    });
    return { success: false, error: result.error };
  }

  // Log successful approval
  logEvent(session.projectPath, "", "m5_approve", "question_approved", "info", {
    question_id: current.questionNumber,
    type: current.fields.type.value,
    method: "auto_parse",
    corrections_applied: input.corrections ? Object.keys(input.corrections) : [],
    confidence_scores: {
      type: current.fields.type.confidence,
      answer: current.fields.answer.confidence,
      stem: current.fields.stem.confidence,
    },
  });

  const progress = getProgress();

  // Check if session is complete
  if (!result.nextQuestion) {
    logEvent(session.projectPath, "", "m5_approve", "session_complete", "info", {
      total_approved: progress?.approved,
      total_skipped: progress?.skipped,
    });
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

  const current = getCurrentQuestion();
  const oldValue = current ? (current.fields as any)[input.field]?.value : undefined;

  const result = updateField(input.field, input.value);

  if (!result.success) {
    logError(session.projectPath, "m5_update_field", "update_failed", result.error || "Unknown error", {
      question_id: current?.questionNumber,
      field: input.field,
    });
    return { success: false, error: result.error };
  }

  // Log field update
  logEvent(session.projectPath, "", "m5_update_field", "field_updated", "info", {
    question_id: current?.questionNumber,
    field: input.field,
    old_value: oldValue,
    new_value: input.value,
  });

  const updatedCurrent = getCurrentQuestion();

  return {
    success: true,
    updated_field: input.field,
    new_value: input.value,
    current_question: updatedCurrent ? formatQuestionReview(updatedCurrent) : undefined,
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

  // Log skip event
  logEvent(session.projectPath, "", "m5_skip", "question_skipped", "info", {
    question_id: current.questionNumber,
    type: current.fields.type.value,
    reason: input.reason || "no reason provided",
    missing_fields: current.missingFields,
    uncertain_fields: current.uncertainFields,
  });

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

  // Log session finish
  logEvent(session.projectPath, "", "m5_finish", "session_finished", "info", {
    session_id: session.sessionId,
    duration_ms: Date.now() - new Date(session.startedAt).getTime(),
    total_questions: summary.total_questions,
    approved: summary.approved,
    skipped: summary.skipped,
    output_file: summary.output_file,
    approval_rate: summary.total_questions > 0
      ? Math.round((summary.approved / summary.total_questions) * 100)
      : 0,
  });

  // Clear session
  clearSession();

  return {
    success: true,
    summary,
  };
}

// ============================================================================
// Tool: m5_fallback - When parser fails, present to Claude Desktop
// ============================================================================

// QFMD templates per question type (from qti-core fixtures)
const QFMD_TEMPLATES: Record<string, string> = {
  text_entry: `# Q00X [Title]
^question Q00X
^type text_entry
^identifier TE_Q00X
^title [Title]
^points [N]
^labels #Label1 #Label2

@field: question_text
[Question with {{blank_1}} and {{blank_2}} markers]
@end_field

@field: blanks

@@field: blank_1
^Correct_Answers
- answer1
- alternative1
^Case_Sensitive No
@@end_field

@@field: blank_2
^Correct_Answers
- answer2
- alternative2
^Case_Sensitive No
@@end_field

@end_field

@field: feedback

@@field: correct_feedback
[Feedback for all correct]
@@end_field

@@field: incorrect_feedback
[Feedback for incorrect]
@@end_field

@@field: partial_feedback
[Feedback for partially correct]
@@end_field

@end_field`,

  inline_choice: `# Q00X [Title]
^question Q00X
^type inline_choice
^identifier IC_Q00X
^title [Title]
^points [N]
^labels #Label1 #Label2

@field: question_text
[Question with {{dropdown_1}} and {{dropdown_2}} markers]
@end_field

@field: dropdown_1
^Shuffle Yes
- correct_answer*
- wrong_option1
- wrong_option2
@end_field

@field: dropdown_2
^Shuffle Yes
- correct_answer*
- wrong_option1
- wrong_option2
@end_field

@field: feedback

@@field: correct_feedback
[Feedback for all correct]
@@end_field

@@field: incorrect_feedback
[Feedback for incorrect]
@@end_field

@end_field`,

  true_false: `# Q00X [Title]
^question Q00X
^type true_false
^identifier TF_Q00X
^title [Title]
^points 1
^labels #Label1 #Label2

@field: question_text
[Statement to evaluate as true or false]
@end_field

@field: answer
True
@end_field

@field: feedback

@@field: correct_feedback
[Feedback for correct]
@@end_field

@@field: incorrect_feedback
[Feedback for incorrect]
@@end_field

@end_field`,

  match: `# Q00X [Title]
^question Q00X
^type match
^identifier MATCH_Q00X
^title [Title]
^points [N = number of pairs]
^labels #Label1 #Label2

@field: question_text
[Instructions for matching]
@end_field

@field: premises
1. [Premise 1]
2. [Premise 2]
3. [Premise 3]
@end_field

@field: choices
A. [Choice A]
B. [Choice B]
C. [Choice C]
D. [Distractor]
@end_field

@field: answer
1 -> A
2 -> B
3 -> C
@end_field

@field: feedback

@@field: correct_feedback
[Feedback for all correct]
@@end_field

@@field: incorrect_feedback
[Feedback for incorrect]
@@end_field

@end_field`,

  multiple_choice_single: `# Q00X [Title]
^question Q00X
^type multiple_choice_single
^identifier MC_Q00X
^title [Title]
^points 1
^labels #Label1 #Label2
^shuffle Yes

@field: question_text
[Question text]
@end_field

@field: options
A. [Option A]
B. [Option B]
C. [Option C]
D. [Option D]
@end_field

@field: answer
[A/B/C/D]
@end_field

@field: feedback

@@field: correct_feedback
[Feedback for correct]
@@end_field

@@field: incorrect_feedback
[Feedback for incorrect]
@@end_field

@end_field`,

  multiple_response: `# Q00X [Title]
^question Q00X
^type multiple_response
^identifier MR_Q00X
^title [Title]
^points 1
^labels #Label1 #Label2
^shuffle Yes

@field: question_text
[Question text - select all that apply]
@end_field

@field: options
A. [Option A]
B. [Option B]
C. [Option C]
D. [Option D]
E. [Option E]
@end_field

@field: answer
A, C, E
@end_field

@field: feedback

@@field: correct_feedback
[Feedback for all correct]
@@end_field

@@field: incorrect_feedback
[Feedback for incorrect]
@@end_field

@end_field`,
};

export interface M5FallbackResult {
  success: boolean;
  error?: string;
  question_number?: string;
  detected_type?: string;
  raw_m3_content?: string;
  expected_qfmd_format?: string;
  instructions?: string;
}

export async function m5Fallback(): Promise<M5FallbackResult> {
  const session = getSession();
  if (!session) {
    return { success: false, error: "Ingen aktiv M5-session. Kör m5_start först." };
  }

  const current = getCurrentQuestion();
  if (!current) {
    return { success: false, error: "Ingen aktuell fråga" };
  }

  // Get detected type
  const detectedType = current.fields.type.value || "unknown";
  const typeRaw = current.fields.type.raw || "unknown";

  // Get template for this type
  const template = QFMD_TEMPLATES[detectedType] || QFMD_TEMPLATES["multiple_choice_single"];

  // Log fallback mode entry
  logEvent(session.projectPath, "", "m5_fallback", "fallback_requested", "warn", {
    question_id: current.questionNumber,
    detected_type: detectedType,
    type_raw: typeRaw,
    missing_fields: current.missingFields,
    uncertain_fields: current.uncertainFields,
    type_confidence: current.fields.type.confidence,
    raw_content_preview: current.rawContent.substring(0, 200),
  });

  return {
    success: true,
    question_number: current.questionNumber,
    detected_type: detectedType,
    raw_m3_content: current.rawContent,
    expected_qfmd_format: template,
    instructions: `
## FALLBACK MODE - Parser kunde inte extrahera alla fält

### Din uppgift:
1. Läs RAW M3 CONTENT nedan
2. Skapa QFMD enligt EXPECTED FORMAT
3. Anropa m5_submit_qfmd med den genererade QFMD:en

### Detected type: ${detectedType} (raw: "${typeRaw}")

### Viktig info:
- Byt ut Q00X mot ${current.questionNumber}
- Använd korrekt identifier-format (t.ex. TE_${current.questionNumber} för text_entry)
- För text_entry: använd {{blank_N}} i question_text
- För inline_choice: använd {{dropdown_N}} i question_text
- Asterisk (*) markerar rätt svar i dropdown: "- correct*"
- ^Correct_Answers måste vara en lista med - prefix

När du är klar, anropa:
m5_submit_qfmd({ qfmd_content: "..." })
`,
  };
}

// ============================================================================
// Tool: m5_submit_qfmd - Submit Claude-generated QFMD
// ============================================================================

export interface M5SubmitQfmdResult {
  success: boolean;
  error?: string;
  submitted_question?: string;
  written_to_file?: boolean;
  next_question?: QuestionReview;
  progress?: {
    approved: number;
    total: number;
    remaining: number;
  };
  session_complete?: boolean;
}

export async function m5SubmitQfmd(
  input: z.infer<typeof m5SubmitQfmdSchema>
): Promise<M5SubmitQfmdResult> {
  const session = getSession();
  if (!session) {
    return { success: false, error: "Ingen aktiv M5-session" };
  }

  const current = getCurrentQuestion();
  if (!current) {
    return { success: false, error: "Ingen aktuell fråga att submitta" };
  }

  // Validate QFMD has basic structure
  const qfmd = input.qfmd_content.trim();
  if (!qfmd.includes("^type") || !qfmd.includes("@field:")) {
    logError(session.projectPath, "m5_submit_qfmd", "invalid_qfmd", "Saknar ^type eller @field: struktur", {
      question_id: current.questionNumber,
      qfmd_preview: qfmd.substring(0, 200),
    });
    return {
      success: false,
      error: "Ogiltig QFMD: saknar ^type eller @field: struktur",
    };
  }

  // Write to output file
  const outputPath = path.join(session.projectPath, session.outputFile);

  // Ensure directory exists
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Append or create file
  const separator = fs.existsSync(outputPath) ? "\n---\n\n" : "";
  const header = !fs.existsSync(outputPath)
    ? `<!-- QFMD Format - Generated by M5 -->\n<!-- Generated: ${new Date().toISOString()} -->\n\n`
    : "";

  fs.appendFileSync(outputPath, header + separator + qfmd + "\n", "utf-8");

  // Mark question as approved and advance
  session.questionStatus[current.questionNumber] = "approved";
  session.currentIndex++;

  // Log successful fallback submission
  const typeMatch = qfmd.match(/\^type\s+(\S+)/);
  const submittedType = typeMatch ? typeMatch[1] : "unknown";

  logEvent(session.projectPath, "", "m5_submit_qfmd", "qfmd_submitted", "info", {
    question_id: current.questionNumber,
    method: "fallback_claude_generated",
    submitted_type: submittedType,
    qfmd_length: qfmd.length,
  });

  const progress = getProgress();

  // Check if done
  if (session.currentIndex >= session.questions.length) {
    return {
      success: true,
      submitted_question: current.questionNumber,
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

  // Get next question
  const nextQ = getCurrentQuestion();

  return {
    success: true,
    submitted_question: current.questionNumber,
    written_to_file: true,
    next_question: nextQ ? formatQuestionReview(nextQ) : undefined,
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
// Tool: m5_help_parse - Teacher helps identify question structure
// ============================================================================

export const m5HelpParseSchema = z.object({
  project_path: z.string().describe("Absolute path to the project folder"),
  source_file: z.string().optional().describe("Relative path to source file"),
  question_pattern: z
    .string()
    .describe("How questions are marked in your file. Examples: '## Question N', '### QN', '## Fråga N', or describe in your own words"),
  section_markers: z
    .record(z.string())
    .optional()
    .describe("Custom section markers: { 'stem': '**Stem:**', 'answer': '**Answer:**' }"),
});

export interface M5HelpParseResult {
  success: boolean;
  error?: string;
  questions_found?: number;
  preview?: { question_number: string; title: string | null; line: number }[];
  ready_to_start?: boolean;
  first_question?: QuestionReview;
}

export async function m5HelpParse(
  input: z.infer<typeof m5HelpParseSchema>
): Promise<M5HelpParseResult> {
  const projectPath = input.project_path;
  const sourceFile = input.source_file || "questions/m3_output.md";
  const sourcePath = path.join(projectPath, sourceFile);

  if (!fs.existsSync(sourcePath)) {
    return { success: false, error: `Fil finns inte: ${sourceFile}` };
  }

  const content = fs.readFileSync(sourcePath, "utf-8");
  const lines = content.split("\n");

  // Build custom regex from teacher's description
  let questionPattern: RegExp;
  const patternInput = input.question_pattern.toLowerCase();

  if (patternInput.includes("## question")) {
    questionPattern = /^##\s+Question\s+(\d+)/i;
  } else if (patternInput.includes("### q")) {
    questionPattern = /^###\s+(Q\d+)/i;
  } else if (patternInput.includes("## fråga")) {
    questionPattern = /^##\s+Fråga\s+(\d+)/i;
  } else if (patternInput.includes("# q")) {
    questionPattern = /^#\s+(Q\d+)/i;
  } else {
    // Try to extract pattern from description
    // e.g., "varje fråga börjar med ## och ett nummer" -> /^##\s+.*\d+/
    if (patternInput.includes("##") && patternInput.includes("nummer")) {
      questionPattern = /^##\s+.*\d+/i;
    } else if (patternInput.includes("#") && patternInput.includes("nummer")) {
      questionPattern = /^#+\s+.*\d+/i;
    } else {
      // Fallback: any header with content
      questionPattern = /^#+\s+.+/;
    }
  }

  // Find questions with custom pattern
  const foundQuestions: { line: number; questionNumber: string; title: string | null }[] = [];

  for (let i = 0; i < lines.length; i++) {
    const match = lines[i].match(questionPattern);
    if (match) {
      // Extract question number
      let qNum: string;
      if (match[1]) {
        qNum = match[1].toUpperCase().startsWith("Q") ? match[1].toUpperCase() : `Q${match[1]}`;
      } else {
        qNum = `Q${foundQuestions.length + 1}`;
      }

      // Try to extract title
      const titleMatch = lines[i].match(/^#+\s+(?:Q\d+|Question\s+\d+|Fråga\s+\d+)\s*[-:]?\s*(.*)$/i);
      const title = titleMatch?.[1]?.trim() || null;

      foundQuestions.push({ line: i + 1, questionNumber: qNum, title });
    }
  }

  if (foundQuestions.length === 0) {
    return {
      success: false,
      error: `Hittade inga frågor med mönstret "${input.question_pattern}". Kan du beskriva strukturen mer detaljerat?`,
    };
  }

  // Log that teacher helped
  logEvent(projectPath, "", "m5_help_parse", "teacher_helped_parse", "info", {
    pattern_description: input.question_pattern,
    questions_found: foundQuestions.length,
  });

  return {
    success: true,
    questions_found: foundQuestions.length,
    preview: foundQuestions.slice(0, 5).map((q) => ({
      question_number: q.questionNumber,
      title: q.title,
      line: q.line,
    })),
    ready_to_start: true,
    // Note: To actually start, teacher should call m5_start again
    // This tool just confirms the pattern works
  };
}

// ============================================================================
// Tool: m5_generate_from_raw - Generate QFMD directly from raw content
// ============================================================================

export const m5GenerateFromRawSchema = z.object({
  project_path: z.string().describe("Absolute path to the project folder"),
  raw_content: z.string().describe("The raw question content to convert to QFMD"),
  question_number: z.string().optional().describe("Question ID (e.g., 'Q001')"),
  question_type: z.string().describe("Question type: essay, multiple_choice_single, true_false, etc."),
  output_file: z.string().optional().describe("Output file path"),
});

export interface M5GenerateFromRawResult {
  success: boolean;
  error?: string;
  generated_qfmd?: string;
  written_to_file?: boolean;
  output_path?: string;
}

export async function m5GenerateFromRaw(
  input: z.infer<typeof m5GenerateFromRawSchema>
): Promise<M5GenerateFromRawResult> {
  const projectPath = input.project_path;
  const outputFile = input.output_file || "questions/m5_output.md";
  const outputPath = path.join(projectPath, outputFile);

  // Generate a basic QFMD structure that Claude can then refine
  const qNum = input.question_number || "Q001";
  const qType = input.question_type || "essay";

  // Extract what we can from raw content
  const lines = input.raw_content.split("\n");
  let title = "";
  let stem = "";
  let answer = "";

  // Simple extraction - look for common markers
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^\*\*Title:?\*\*/i.test(line)) {
      title = line.replace(/^\*\*Title:?\*\*:?\s*/i, "").trim();
    } else if (/^\*\*Stem:?\*\*/i.test(line) || /^\*\*Question:?\*\*/i.test(line) || /^\*\*Fråga:?\*\*/i.test(line)) {
      // Collect lines until next marker
      const stemLines: string[] = [];
      for (let j = i + 1; j < lines.length && !/^\*\*[A-Z]/i.test(lines[j]); j++) {
        stemLines.push(lines[j]);
      }
      stem = stemLines.join("\n").trim();
    } else if (/^\*\*Answer:?\*\*/i.test(line) || /^\*\*Svar:?\*\*/i.test(line)) {
      const answerLines: string[] = [];
      for (let j = i + 1; j < lines.length && !/^\*\*[A-Z]/i.test(lines[j]); j++) {
        answerLines.push(lines[j]);
      }
      answer = answerLines.join("\n").trim();
    }
  }

  // If no structured content found, use the whole thing as stem
  if (!stem) {
    stem = input.raw_content;
  }

  // Generate QFMD
  const qfmd = `# ${qNum} ${title || "Untitled Question"}
^question ${qNum}
^type ${qType}
^identifier ${qType.toUpperCase().substring(0, 2)}_${qNum}
^title ${title || "Untitled Question"}
^points 1

@field: question_text
${stem}
@end_field

@field: answer
${answer || "[Teacher: please provide answer]"}
@end_field

@field: feedback

@@field: general_feedback
[Teacher: please provide feedback]
@@end_field

@end_field
`;

  // Write to file
  try {
    const dir = path.dirname(outputPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    const separator = fs.existsSync(outputPath) ? "\n---\n\n" : "";
    fs.appendFileSync(outputPath, separator + qfmd, "utf-8");

    logEvent(projectPath, "", "m5_generate_from_raw", "qfmd_generated", "info", {
      question_number: qNum,
      question_type: qType,
      has_title: !!title,
      has_stem: !!stem,
      has_answer: !!answer,
    });

    return {
      success: true,
      generated_qfmd: qfmd,
      written_to_file: true,
      output_path: outputPath,
    };
  } catch (error) {
    return {
      success: false,
      error: `Kunde inte skriva fil: ${error}`,
    };
  }
}

// ============================================================================
// Tool: m5_teach_format (RFC-016)
// ============================================================================

export const m5TeachFormatSchema = z.object({
  project_path: z.string().describe("Absolute path to the project folder"),
  pattern_name: z.string().describe("Name for this format pattern (e.g., 'M3 Bold Headers')"),
  mappings: z.record(z.object({
    qfmd_field: z.string().nullable().describe("QFMD field name (title, type, points, labels, question_text, answer, feedback) or null to skip"),
    extraction: z.enum(["single_line", "multiline_until_next", "number", "tags", "skip"]).describe("How to extract the value"),
    transform: z.enum(["prepend_hash", "keep_as_is"]).optional().describe("Optional transformation"),
    required: z.boolean().optional().describe("Is this field required for detection?"),
  })).describe("Mappings from source markers to QFMD fields"),
  question_separator: z.string().optional().describe("What separates questions (default: ---)"),
});

export interface M5TeachFormatResult {
  success: boolean;
  error?: string;
  pattern_id?: string;
  pattern_name?: string;
  message?: string;
  detected_markers?: string[];
}

export async function m5TeachFormat(
  input: z.infer<typeof m5TeachFormatSchema>
): Promise<M5TeachFormatResult> {
  const { project_path, pattern_name, mappings, question_separator } = input;

  // Convert to internal format
  const internalMappings: Record<string, FieldMapping> = {};
  for (const [marker, mapping] of Object.entries(mappings)) {
    internalMappings[marker] = {
      qfmd_field: mapping.qfmd_field,
      extraction: mapping.extraction,
      transform: mapping.transform,
      required: mapping.required,
    };
  }

  // Generate session ID
  const sessionId = `teach_${Date.now().toString(36)}`;

  // Create and save pattern
  const pattern = createPattern(
    pattern_name,
    internalMappings,
    question_separator || "---",
    sessionId
  );

  const data = loadPatterns(project_path);
  data.patterns.push(pattern);
  savePatterns(project_path, data);

  logEvent(project_path, "", "m5_teach_format", "pattern_created", "info", {
    pattern_id: pattern.pattern_id,
    pattern_name: pattern_name,
    mappings_count: Object.keys(mappings).length,
  });

  return {
    success: true,
    pattern_id: pattern.pattern_id,
    pattern_name: pattern_name,
    message: `Mönstret "${pattern_name}" har sparats! Nästa gång du kör m5_start kommer detta format att kännas igen automatiskt.`,
    detected_markers: Object.keys(mappings),
  };
}

// ============================================================================
// Tool: m5_list_formats (RFC-016)
// ============================================================================

export const m5ListFormatsSchema = z.object({
  project_path: z.string().describe("Absolute path to the project folder"),
});

export interface M5ListFormatsResult {
  success: boolean;
  patterns: Array<{
    pattern_id: string;
    name: string;
    builtin: boolean;
    times_used: number;
    questions_processed: number;
    detection_markers: string[];
    learned_date?: string;
  }>;
  total_patterns: number;
}

export async function m5ListFormats(
  input: z.infer<typeof m5ListFormatsSchema>
): Promise<M5ListFormatsResult> {
  const data = loadPatterns(input.project_path);

  const patterns = data.patterns.map((p) => ({
    pattern_id: p.pattern_id,
    name: p.name,
    builtin: p.builtin || false,
    times_used: p.statistics.times_used,
    questions_processed: p.statistics.questions_processed,
    detection_markers: p.detection.required_markers,
    learned_date: p.learned_from?.date,
  }));

  return {
    success: true,
    patterns: patterns,
    total_patterns: patterns.length,
  };
}

// ============================================================================
// Tool: m5_detect_format (RFC-016) - Helper for teacher dialog
// ============================================================================

export const m5DetectFormatSchema = z.object({
  project_path: z.string().describe("Absolute path to the project folder"),
  source_file: z.string().describe("Relative path to file to analyze"),
});

export interface M5DetectFormatResult {
  success: boolean;
  detected: boolean;
  pattern_name?: string;
  confidence?: number;
  potential_markers?: string[];
  file_preview?: string;
  suggestion?: string;
}

export async function m5DetectFormat(
  input: z.infer<typeof m5DetectFormatSchema>
): Promise<M5DetectFormatResult> {
  const { project_path, source_file } = input;
  const sourcePath = path.join(project_path, source_file);

  if (!fs.existsSync(sourcePath)) {
    return {
      success: false,
      detected: false,
      suggestion: `Filen finns inte: ${source_file}`,
    };
  }

  const content = fs.readFileSync(sourcePath, "utf-8");
  const data = loadPatterns(project_path);

  // Detect format using learned patterns
  const result = detectFormat(content, data.patterns);

  const lines = content.split("\n");
  const preview = lines.slice(0, 25).join("\n") + (lines.length > 25 ? "\n..." : "");
  const potentialMarkers = findPotentialMarkers(content);

  if (result.detected && result.pattern) {
    return {
      success: true,
      detected: true,
      pattern_name: result.pattern.name,
      confidence: result.confidence,
      file_preview: preview,
      suggestion: `Formatet "${result.pattern.name}" kändes igen (confidence: ${result.confidence}%). Kör m5_start för att bearbeta frågorna.`,
    };
  }

  return {
    success: true,
    detected: false,
    potential_markers: potentialMarkers,
    file_preview: preview,
    suggestion: `Okänt format. Hittade dessa möjliga markörer: ${potentialMarkers.join(", ")}

Använd m5_teach_format för att lära mig detta format. Exempel:

m5_teach_format({
  project_path: "${project_path}",
  pattern_name: "Mitt format",
  mappings: {
    "**Title:**": { qfmd_field: "title", extraction: "single_line" },
    "**Stem:**": { qfmd_field: "question_text", extraction: "multiline_until_next" }
  }
})`,
  };
}
