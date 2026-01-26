/**
 * M5 Generator - Generate QFMD from M3 Questions
 *
 * Converts parsed M3 questions to QFMD format for the pipeline.
 */

import type {
  M3Question,
  QFMDQuestion,
  QuestionType,
  M5GenerationResult,
} from "./types.js";
import { resolveQuestionType } from "./checker.js";

/**
 * Generate QFMD content from M3 questions.
 */
export function generateQFMD(
  questions: M3Question[],
  options: {
    courseCode?: string;
    includeSourceComments?: boolean;
  } = {}
): M5GenerationResult {
  const result: M5GenerationResult = {
    success: true,
    questionCount: 0,
    warnings: [],
    errors: [],
    skippedQuestions: [],
  };

  const qfmdQuestions: string[] = [];

  for (const m3q of questions) {
    const qId = m3q.questionNumber;

    // Resolve type
    const questionType = resolveQuestionType(m3q.metadata.type || "");
    if (!questionType) {
      result.errors.push(
        `${qId}: Okänd frågetyp "${m3q.metadata.type}" - hoppar över`
      );
      result.skippedQuestions.push(qId);
      continue;
    }

    // Convert to QFMD
    try {
      const qfmd = convertToQFMD(m3q, questionType, options);
      qfmdQuestions.push(qfmd);
      result.questionCount++;
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      result.errors.push(`${qId}: ${message}`);
      result.skippedQuestions.push(qId);
    }
  }

  // Join questions with separators
  result.qfmdContent = qfmdQuestions.join("\n---\n\n");
  result.success = result.errors.length === 0;

  return result;
}

/**
 * Convert single M3 question to QFMD format.
 */
function convertToQFMD(
  m3q: M3Question,
  questionType: QuestionType,
  options: {
    courseCode?: string;
    includeSourceComments?: boolean;
  }
): string {
  const lines: string[] = [];

  // Question ID - normalize to Q001 format
  const qNum = m3q.questionNumber.replace(/Q/, "");
  const normalizedId = `Q${qNum.padStart(3, "0")}`;

  // Generate identifier
  const courseCode = options.courseCode || extractCourseCode(m3q.labels);
  const typeShort = getTypeShort(questionType);
  const identifier = `${courseCode}_${typeShort}_${normalizedId}`;

  // Header with title
  const title = m3q.title || `Fråga ${normalizedId}`;
  lines.push(`# ${normalizedId} ${title}`);

  // Metadata
  lines.push(`^question ${normalizedId}`);
  lines.push(`^type ${questionType}`);
  lines.push(`^identifier ${identifier}`);
  if (m3q.title) {
    lines.push(`^title ${m3q.title}`);
  }
  lines.push(`^points ${m3q.metadata.points || 1}`);

  // Labels
  const labels = buildLabels(m3q);
  if (labels.length > 0) {
    lines.push(`^labels ${labels.map((l) => `#${l}`).join(" ")}`);
  }

  // Shuffle (for MC questions)
  if (
    questionType === "multiple_choice_single" ||
    questionType === "multiple_response"
  ) {
    lines.push(`^shuffle Yes`);
  }

  lines.push("");

  // Question text field
  lines.push(`@field: question_text`);
  lines.push(m3q.questionStem);
  lines.push(`@end_field`);
  lines.push("");

  // Options field (for MC questions)
  if (m3q.options.length > 0) {
    lines.push(`@field: options`);
    for (const option of m3q.options) {
      lines.push(option);
    }
    lines.push(`@end_field`);
    lines.push("");
  }

  // Answer field
  if (m3q.correctAnswer) {
    lines.push(`@field: answer`);
    lines.push(normalizeAnswer(m3q.correctAnswer, questionType));
    lines.push(`@end_field`);
    lines.push("");
  }

  // Feedback field
  lines.push(`@field: feedback`);
  lines.push("");

  // General feedback
  const generalFeedback =
    m3q.feedback.general ||
    m3q.feedback.correct ||
    "Förklarande feedback saknas.";
  lines.push(`@@field: general_feedback`);
  lines.push(generalFeedback);
  lines.push(`@@end_field`);
  lines.push("");

  // Correct feedback
  const correctFeedback = m3q.feedback.correct || generalFeedback;
  lines.push(`@@field: correct_feedback`);
  lines.push(correctFeedback);
  lines.push(`@@end_field`);
  lines.push("");

  // Incorrect feedback
  const incorrectFeedback = buildIncorrectFeedback(m3q);
  lines.push(`@@field: incorrect_feedback`);
  lines.push(incorrectFeedback);
  lines.push(`@@end_field`);
  lines.push("");

  // Unanswered feedback
  lines.push(`@@field: unanswered_feedback`);
  lines.push("Besvara frågan för att få feedback.");
  lines.push(`@@end_field`);
  lines.push("");

  lines.push(`@end_field`);

  // Option-specific feedback (if available)
  if (
    m3q.feedback.incorrect &&
    Object.keys(m3q.feedback.incorrect).length > 0
  ) {
    lines.push("");
    lines.push(`@field: option_feedback`);
    for (const [option, feedback] of Object.entries(m3q.feedback.incorrect)) {
      lines.push(`@@field: option_${option}`);
      lines.push(feedback);
      lines.push(`@@end_field`);
    }
    // Add correct option feedback
    if (m3q.feedback.correct) {
      const correctOption = m3q.correctAnswer.trim().toUpperCase().charAt(0);
      lines.push(`@@field: option_${correctOption}`);
      lines.push(m3q.feedback.correct);
      lines.push(`@@end_field`);
    }
    lines.push(`@end_field`);
  }

  // Source comment (optional)
  if (options.includeSourceComments && m3q.sourceExplanation) {
    lines.push("");
    lines.push(`<!-- Source: ${m3q.sourceExplanation} -->`);
  }

  lines.push("");

  return lines.join("\n");
}

/**
 * Build labels array from M3 question.
 */
function buildLabels(m3q: M3Question): string[] {
  const labels: string[] = [];

  // Add course code and topic labels
  for (const label of m3q.labels) {
    // Clean up label (remove # if present)
    const clean = label.replace(/^#/, "").trim();
    if (clean) {
      labels.push(clean);
    }
  }

  // Add Bloom level if not already in labels
  if (m3q.metadata.bloom) {
    const bloomLabel = m3q.metadata.bloom;
    if (!labels.some((l) => l.toLowerCase() === bloomLabel.toLowerCase())) {
      labels.push(bloomLabel);
    }
  }

  // Add difficulty if not already in labels
  if (m3q.metadata.difficulty) {
    const diffLabel = m3q.metadata.difficulty;
    if (!labels.some((l) => l.toLowerCase() === diffLabel.toLowerCase())) {
      labels.push(diffLabel);
    }
  }

  // Add LO if not already in labels
  if (m3q.metadata.lo) {
    const loLabel = m3q.metadata.lo;
    if (!labels.some((l) => l.toLowerCase() === loLabel.toLowerCase())) {
      labels.push(loLabel);
    }
  }

  return labels;
}

/**
 * Extract course code from labels.
 */
function extractCourseCode(labels: string[]): string {
  // Look for typical course code pattern (e.g., ARTI1000X, BIOG001X)
  for (const label of labels) {
    const match = label.match(/^[A-Z]{3,4}\d{3,4}[A-Z]?$/i);
    if (match) {
      return label.toUpperCase();
    }
  }

  // Fallback
  return "COURSE";
}

/**
 * Get short type code for identifier.
 */
function getTypeShort(type: QuestionType): string {
  const shorts: Record<QuestionType, string> = {
    multiple_choice_single: "MC",
    multiple_response: "MR",
    true_false: "TF",
    inline_choice: "IC",
    text_entry: "TE",
    text_entry_math: "TEM",
    text_entry_numeric: "TEN",
    text_area: "TA",
    essay: "ES",
    match: "MA",
    hotspot: "HS",
    graphicgapmatch_v2: "GGM",
    text_entry_graphic: "TEG",
    audio_record: "AR",
    composite_editor: "CE",
    nativehtml: "NH",
  };

  return shorts[type] || "Q";
}

/**
 * Normalize answer format.
 */
function normalizeAnswer(answer: string, type: QuestionType): string {
  const trimmed = answer.trim();

  if (
    type === "multiple_choice_single" ||
    type === "multiple_response" ||
    type === "inline_choice"
  ) {
    // Extract just the letter(s)
    const letters = trimmed
      .toUpperCase()
      .replace(/[^A-F,]/g, "")
      .split(",")
      .map((l) => l.trim())
      .filter((l) => l)
      .join(", ");

    return letters || trimmed.toUpperCase().charAt(0);
  }

  if (type === "true_false") {
    const lower = trimmed.toLowerCase();
    if (lower === "true" || lower === "sant" || lower === "t") {
      return "True";
    }
    if (lower === "false" || lower === "falskt" || lower === "f") {
      return "False";
    }
  }

  return trimmed;
}

/**
 * Build incorrect feedback from M3 question.
 */
function buildIncorrectFeedback(m3q: M3Question): string {
  // If we have specific incorrect feedback, combine them
  if (m3q.feedback.incorrect) {
    const feedbacks = Object.values(m3q.feedback.incorrect);
    if (feedbacks.length > 0) {
      // Use the first incorrect feedback as the general incorrect
      return feedbacks[0];
    }
  }

  // Fall back to general feedback
  if (m3q.feedback.general) {
    return m3q.feedback.general;
  }

  // Generate generic incorrect feedback
  return "Tyvärr, det var inte rätt. Granska frågan och försök igen.";
}

/**
 * Generate QFMD header with metadata.
 */
export function generateQFMDHeader(options: {
  title?: string;
  description?: string;
  courseCode?: string;
  generatedAt?: Date;
}): string {
  const lines: string[] = [];

  lines.push("<!-- QFMD Format - Generated by M5 -->");
  lines.push(`<!-- Generated: ${(options.generatedAt || new Date()).toISOString()} -->`);

  if (options.title) {
    lines.push(`<!-- Title: ${options.title} -->`);
  }

  if (options.courseCode) {
    lines.push(`<!-- Course: ${options.courseCode} -->`);
  }

  lines.push("");

  return lines.join("\n");
}

/**
 * Generate complete QFMD file content.
 */
export function generateQFMDFile(
  questions: M3Question[],
  options: {
    title?: string;
    courseCode?: string;
    includeHeader?: boolean;
    includeSourceComments?: boolean;
  } = {}
): M5GenerationResult {
  const result = generateQFMD(questions, options);

  if (options.includeHeader !== false && result.qfmdContent) {
    const header = generateQFMDHeader({
      title: options.title,
      courseCode: options.courseCode,
      generatedAt: new Date(),
    });

    result.qfmdContent = header + result.qfmdContent;
  }

  return result;
}
