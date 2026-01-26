/**
 * M5 Session Management
 *
 * Manages state for the question-by-question M5 workflow.
 * Each question is reviewed, potentially corrected, then written to file.
 */

import * as fs from "fs";
import * as path from "path";
import type { M3Question, QuestionType } from "./types.js";

/**
 * Parsed question with interpretation and confidence.
 */
export interface ParsedInterpretation {
  /** Original question number from file */
  questionNumber: string;

  /** Interpreted fields with confidence */
  fields: {
    title: { value: string | null; confidence: number; source: string };
    type: { value: QuestionType | null; confidence: number; source: string; raw: string };
    stem: { value: string | null; confidence: number; source: string };
    options: { value: string[]; confidence: number; source: string };
    answer: { value: string | null; confidence: number; source: string };
    feedback: {
      correct: { value: string | null; confidence: number };
      incorrect: { value: Record<string, string>; confidence: number };
      general: { value: string | null; confidence: number };
    };
    labels: { value: string[]; confidence: number; source: string };
    points: { value: number; confidence: number; source: string };
    bloom: { value: string | null; confidence: number; source: string };
    difficulty: { value: string | null; confidence: number; source: string };
  };

  /** Fields that are missing and need user input */
  missingFields: string[];

  /** Fields with low confidence that need confirmation */
  uncertainFields: string[];

  /** Raw content for reference */
  rawContent: string;

  /** Line number in source */
  lineNumber: number;
}

/**
 * Question status in the session.
 */
export type QuestionStatus = "pending" | "reviewing" | "approved" | "skipped";

/**
 * M5 Session state.
 */
export interface M5Session {
  /** Session ID */
  sessionId: string;

  /** Project path */
  projectPath: string;

  /** Source file (relative path) */
  sourceFile: string;

  /** Output file (relative path) */
  outputFile: string;

  /** All parsed questions */
  questions: ParsedInterpretation[];

  /** Current question index (0-based) */
  currentIndex: number;

  /** Status per question */
  questionStatus: Record<string, QuestionStatus>;

  /** Approved data per question (after user corrections) */
  approvedData: Record<string, ParsedInterpretation>;

  /** Session started at */
  startedAt: string;

  /** Last activity */
  lastActivity: string;

  /** Course code (for identifiers) */
  courseCode?: string;

  /** Title for the output */
  title?: string;
}

// Global session storage (in-memory for now)
let currentSession: M5Session | null = null;

/**
 * Generate a short session ID.
 */
function generateSessionId(): string {
  return Math.random().toString(36).substring(2, 10);
}

/**
 * Create a new M5 session.
 */
export function createSession(
  projectPath: string,
  sourceFile: string,
  outputFile: string,
  questions: ParsedInterpretation[],
  options?: { courseCode?: string; title?: string }
): M5Session {
  const session: M5Session = {
    sessionId: generateSessionId(),
    projectPath,
    sourceFile,
    outputFile,
    questions,
    currentIndex: 0,
    questionStatus: {},
    approvedData: {},
    startedAt: new Date().toISOString(),
    lastActivity: new Date().toISOString(),
    courseCode: options?.courseCode,
    title: options?.title,
  };

  // Initialize all questions as pending
  for (const q of questions) {
    session.questionStatus[q.questionNumber] = "pending";
  }

  // Mark first question as reviewing
  if (questions.length > 0) {
    session.questionStatus[questions[0].questionNumber] = "reviewing";
  }

  currentSession = session;
  return session;
}

/**
 * Get the current session.
 */
export function getSession(): M5Session | null {
  return currentSession;
}

/**
 * Clear the current session.
 */
export function clearSession(): void {
  currentSession = null;
}

/**
 * Get the current question being reviewed.
 */
export function getCurrentQuestion(): ParsedInterpretation | null {
  if (!currentSession) return null;
  if (currentSession.currentIndex >= currentSession.questions.length) return null;
  return currentSession.questions[currentSession.currentIndex];
}

/**
 * Move to the next question.
 */
export function moveToNext(): ParsedInterpretation | null {
  if (!currentSession) return null;

  currentSession.currentIndex++;
  currentSession.lastActivity = new Date().toISOString();

  if (currentSession.currentIndex >= currentSession.questions.length) {
    return null; // No more questions
  }

  const nextQ = currentSession.questions[currentSession.currentIndex];
  currentSession.questionStatus[nextQ.questionNumber] = "reviewing";

  return nextQ;
}

/**
 * Approve the current question and write to file.
 */
export function approveQuestion(
  correctedData?: Partial<ParsedInterpretation["fields"]>
): { success: boolean; error?: string; nextQuestion?: ParsedInterpretation } {
  if (!currentSession) {
    return { success: false, error: "Ingen aktiv session" };
  }

  const current = getCurrentQuestion();
  if (!current) {
    return { success: false, error: "Ingen fråga att godkänna" };
  }

  // Merge corrections
  const approved = { ...current };
  if (correctedData) {
    approved.fields = { ...approved.fields };
    for (const [key, value] of Object.entries(correctedData)) {
      if (key in approved.fields) {
        (approved.fields as any)[key] = value;
      }
    }
  }

  // Check if all required fields are present
  const missing = checkRequiredFields(approved);
  if (missing.length > 0) {
    return {
      success: false,
      error: `Saknar obligatoriska fält: ${missing.join(", ")}`,
    };
  }

  // Mark as approved
  currentSession.questionStatus[current.questionNumber] = "approved";
  currentSession.approvedData[current.questionNumber] = approved;
  currentSession.lastActivity = new Date().toISOString();

  // Write to file
  const writeResult = appendQuestionToFile(approved);
  if (!writeResult.success) {
    return { success: false, error: writeResult.error };
  }

  // Move to next
  const nextQ = moveToNext();

  return { success: true, nextQuestion: nextQ ?? undefined };
}

/**
 * Skip the current question.
 */
export function skipQuestion(reason?: string): {
  success: boolean;
  nextQuestion?: ParsedInterpretation;
} {
  if (!currentSession) return { success: false };

  const current = getCurrentQuestion();
  if (!current) return { success: false };

  currentSession.questionStatus[current.questionNumber] = "skipped";
  currentSession.lastActivity = new Date().toISOString();

  // Log skip reason if provided
  if (reason) {
    console.error(`Skipped ${current.questionNumber}: ${reason}`);
  }

  const nextQ = moveToNext();
  return { success: true, nextQuestion: nextQ ?? undefined };
}

/**
 * Check required fields for a question.
 */
function checkRequiredFields(q: ParsedInterpretation): string[] {
  const missing: string[] = [];

  if (!q.fields.title.value) missing.push("title (namn)");
  if (!q.fields.type.value) missing.push("type (frågetyp)");
  if (!q.fields.stem.value) missing.push("stem (frågetext)");
  if (!q.fields.answer.value) missing.push("answer (svar)");

  // Type-specific checks
  const type = q.fields.type.value;
  if (type === "multiple_choice_single" || type === "multiple_response") {
    if (q.fields.options.value.length < 2) {
      missing.push("options (minst 2 alternativ)");
    }
  }

  return missing;
}

/**
 * Append a question to the output file in QFMD format.
 */
function appendQuestionToFile(q: ParsedInterpretation): {
  success: boolean;
  error?: string;
} {
  if (!currentSession) {
    return { success: false, error: "Ingen aktiv session" };
  }

  const outputPath = path.join(
    currentSession.projectPath,
    currentSession.outputFile
  );

  // Generate QFMD for this question
  const qfmd = generateQFMDForQuestion(q, currentSession);

  try {
    // Check if file exists and has content
    let existingContent = "";
    if (fs.existsSync(outputPath)) {
      existingContent = fs.readFileSync(outputPath, "utf-8");
    }

    // If empty file, add header
    if (!existingContent.trim()) {
      const header = generateHeader(currentSession);
      existingContent = header;
    }

    // Append question (with separator if not first)
    const separator = existingContent.trim().endsWith("@end_field")
      ? "\n\n---\n\n"
      : "\n";

    const newContent = existingContent + separator + qfmd;

    // Write
    fs.writeFileSync(outputPath, newContent, "utf-8");

    return { success: true };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { success: false, error: message };
  }
}

/**
 * Generate QFMD header.
 */
function generateHeader(session: M5Session): string {
  const lines: string[] = [];
  lines.push("<!-- QFMD Format - Generated by M5 -->");
  lines.push(`<!-- Generated: ${new Date().toISOString()} -->`);
  if (session.title) {
    lines.push(`<!-- Title: ${session.title} -->`);
  }
  if (session.courseCode) {
    lines.push(`<!-- Course: ${session.courseCode} -->`);
  }
  lines.push("");
  return lines.join("\n");
}

/**
 * Generate QFMD for a single question.
 */
function generateQFMDForQuestion(
  q: ParsedInterpretation,
  session: M5Session
): string {
  const lines: string[] = [];
  const f = q.fields;

  // Normalize question ID
  const qNum = q.questionNumber.replace(/Q/i, "");
  const normalizedId = `Q${qNum.padStart(3, "0")}`;

  // Generate identifier
  const courseCode = session.courseCode || "COURSE";
  const typeShort = getTypeShort(f.type.value || "multiple_choice_single");
  const identifier = `${courseCode}_${typeShort}_${normalizedId}`;

  // Header
  const title = f.title.value || `Fråga ${normalizedId}`;
  lines.push(`# ${normalizedId} ${title}`);

  // Metadata
  lines.push(`^question ${normalizedId}`);
  lines.push(`^type ${f.type.value || "multiple_choice_single"}`);
  lines.push(`^identifier ${identifier}`);
  if (f.title.value) {
    lines.push(`^title ${f.title.value}`);
  }
  lines.push(`^points ${f.points.value || 1}`);

  // Labels
  const labels = buildLabels(f);
  if (labels.length > 0) {
    lines.push(`^labels ${labels.map((l) => `#${l}`).join(" ")}`);
  }

  // Shuffle for MC
  if (
    f.type.value === "multiple_choice_single" ||
    f.type.value === "multiple_response"
  ) {
    lines.push(`^shuffle Yes`);
  }

  lines.push("");

  // Question text
  lines.push(`@field: question_text`);
  lines.push(f.stem.value || "");
  lines.push(`@end_field`);
  lines.push("");

  // Options (for MC)
  if (f.options.value.length > 0) {
    lines.push(`@field: options`);
    for (const opt of f.options.value) {
      lines.push(opt);
    }
    lines.push(`@end_field`);
    lines.push("");
  }

  // Answer
  if (f.answer.value) {
    lines.push(`@field: answer`);
    lines.push(f.answer.value);
    lines.push(`@end_field`);
    lines.push("");
  }

  // Feedback
  lines.push(`@field: feedback`);
  lines.push("");

  const generalFb =
    f.feedback.general.value ||
    f.feedback.correct.value ||
    "Förklarande feedback.";
  lines.push(`@@field: general_feedback`);
  lines.push(generalFb);
  lines.push(`@@end_field`);
  lines.push("");

  const correctFb = f.feedback.correct.value || generalFb;
  lines.push(`@@field: correct_feedback`);
  lines.push(correctFb);
  lines.push(`@@end_field`);
  lines.push("");

  const incorrectFb =
    Object.values(f.feedback.incorrect.value)[0] ||
    f.feedback.general.value ||
    "Tyvärr fel.";
  lines.push(`@@field: incorrect_feedback`);
  lines.push(incorrectFb);
  lines.push(`@@end_field`);
  lines.push("");

  lines.push(`@@field: unanswered_feedback`);
  lines.push("Besvara frågan för att få feedback.");
  lines.push(`@@end_field`);
  lines.push("");

  lines.push(`@end_field`);

  return lines.join("\n");
}

/**
 * Get type short code.
 */
function getTypeShort(type: QuestionType): string {
  const shorts: Record<string, string> = {
    multiple_choice_single: "MC",
    multiple_response: "MR",
    true_false: "TF",
    inline_choice: "IC",
    text_entry: "TE",
    match: "MA",
    essay: "ES",
  };
  return shorts[type] || "Q";
}

/**
 * Build labels array.
 */
function buildLabels(f: ParsedInterpretation["fields"]): string[] {
  const labels = [...f.labels.value];

  if (f.bloom.value && !labels.some((l) => l.includes(f.bloom.value!))) {
    labels.push(f.bloom.value);
  }

  if (
    f.difficulty.value &&
    !labels.some((l) => l.includes(f.difficulty.value!))
  ) {
    labels.push(f.difficulty.value);
  }

  return labels;
}

/**
 * Get session progress summary.
 */
export function getProgress(): {
  total: number;
  approved: number;
  skipped: number;
  pending: number;
  current: number;
  currentQuestion: string | null;
} | null {
  if (!currentSession) return null;

  const statuses = Object.values(currentSession.questionStatus);

  return {
    total: currentSession.questions.length,
    approved: statuses.filter((s) => s === "approved").length,
    skipped: statuses.filter((s) => s === "skipped").length,
    pending: statuses.filter((s) => s === "pending" || s === "reviewing").length,
    current: currentSession.currentIndex + 1,
    currentQuestion: getCurrentQuestion()?.questionNumber || null,
  };
}

/**
 * Update a field in the current question.
 */
export function updateField(
  fieldName: string,
  value: any
): { success: boolean; error?: string } {
  if (!currentSession) {
    return { success: false, error: "Ingen aktiv session" };
  }

  const current = getCurrentQuestion();
  if (!current) {
    return { success: false, error: "Ingen aktiv fråga" };
  }

  // Update the field
  if (fieldName in current.fields) {
    const field = (current.fields as any)[fieldName];
    if (typeof field === "object" && "value" in field) {
      field.value = value;
      field.confidence = 100; // User-provided = 100% confidence
      field.source = "user";

      // Remove from missing/uncertain
      current.missingFields = current.missingFields.filter(
        (f) => f !== fieldName
      );
      current.uncertainFields = current.uncertainFields.filter(
        (f) => f !== fieldName
      );
    }
  } else if (fieldName.startsWith("feedback.")) {
    const fbField = fieldName.replace("feedback.", "");
    if (fbField in current.fields.feedback) {
      (current.fields.feedback as any)[fbField].value = value;
      (current.fields.feedback as any)[fbField].confidence = 100;
    }
  }

  currentSession.lastActivity = new Date().toISOString();
  return { success: true };
}
