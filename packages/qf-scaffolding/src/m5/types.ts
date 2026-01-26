/**
 * M5 Type Definitions
 *
 * Types for parsing M3 human-readable format and generating QFMD.
 */

/**
 * Question types supported by the pipeline.
 * Must match codes in qf-pipeline/specs/*.yaml
 */
export type QuestionType =
  | "multiple_choice_single"
  | "multiple_response"
  | "true_false"
  | "inline_choice"
  | "text_entry"
  | "text_entry_math"
  | "text_entry_numeric"
  | "text_area"
  | "essay"
  | "match"
  | "hotspot"
  | "graphicgapmatch_v2"
  | "text_entry_graphic"
  | "audio_record"
  | "composite_editor"
  | "nativehtml";

/**
 * Mapping from M3 human-readable type names to QFMD type codes.
 */
export const M3_TYPE_MAP: Record<string, QuestionType> = {
  // Multiple choice variants
  "Multiple Choice (MC-Single)": "multiple_choice_single",
  "Multiple Choice (Single Answer)": "multiple_choice_single",
  "MC-Single": "multiple_choice_single",
  "Flerval (ett svar)": "multiple_choice_single",
  "Multiple Choice": "multiple_choice_single",

  // Multiple response variants
  "Multiple Response (MR)": "multiple_response",
  "Multiple Response": "multiple_response",
  "MR": "multiple_response",
  "Flerval (flera svar)": "multiple_response",

  // True/false
  "True/False": "true_false",
  "Sant/Falskt": "true_false",
  "TF": "true_false",

  // Inline choice (dropdown)
  "Inline Choice": "inline_choice",
  "Dropdown": "inline_choice",

  // Text entry
  "Text Entry": "text_entry",
  "Fill in the Blank": "text_entry",
  "Fyll i lucka": "text_entry",

  // Match
  "Match": "match",
  "Matchning": "match",

  // Essay
  "Essay": "essay",
  "Essä": "essay",

  // Text area
  "Text Area": "text_area",
  "Extended Text": "text_area",
  "Fritext": "text_area",
};

/**
 * Bloom's taxonomy levels.
 */
export type BloomLevel =
  | "Remember"
  | "Understand"
  | "Apply"
  | "Analyze"
  | "Evaluate"
  | "Create";

/**
 * Difficulty levels.
 */
export type DifficultyLevel = "Easy" | "Medium" | "Hard";

/**
 * Parsed question from M3 human-readable format.
 */
export interface M3Question {
  /** Question number from M3 (e.g., "Q1", "Q2") */
  questionNumber: string;

  /** Question title/topic */
  title: string;

  /** Raw metadata from M3 */
  metadata: {
    lo?: string; // Learning Objective
    bloom?: BloomLevel;
    difficulty?: DifficultyLevel;
    type?: string; // Raw type string from M3
    points?: number;
  };

  /** Labels from M3 (course codes, topics, etc.) */
  labels: string[];

  /** Question stem text */
  questionStem: string;

  /** Answer options (for MC questions) */
  options: string[];

  /** Correct answer(s) */
  correctAnswer: string;

  /** Feedback sections */
  feedback: {
    correct?: string;
    incorrect?: Record<string, string>; // Option -> feedback
    general?: string;
  };

  /** Image references */
  images?: string[];

  /** Source explanation (for M3 traceability) */
  sourceExplanation?: string;

  /** Raw content for debugging */
  rawContent: string;

  /** Line number in source file */
  lineNumber: number;
}

/**
 * Content completeness issue.
 */
export interface CompletenessIssue {
  /** Question identifier */
  questionId: string;

  /** Issue severity */
  severity: "error" | "warning" | "info";

  /** Field that has the issue */
  field: string;

  /** Issue message (Swedish) */
  message: string;

  /** Suggestion for fixing */
  suggestion?: string;

  /** Is this auto-fixable by M5? */
  autoFixable: boolean;
}

/**
 * Result of content completeness check.
 */
export interface CompletenessResult {
  /** Overall status */
  status: "pass" | "warnings" | "errors";

  /** Total questions checked */
  totalQuestions: number;

  /** Questions that passed */
  passedQuestions: number;

  /** All issues found */
  issues: CompletenessIssue[];

  /** Questions grouped by status */
  questionStatus: Record<
    string,
    {
      status: "pass" | "warnings" | "errors";
      issues: CompletenessIssue[];
    }
  >;
}

/**
 * QFMD question output format.
 */
export interface QFMDQuestion {
  /** Question ID (e.g., "Q001") */
  questionId: string;

  /** Question type code */
  type: QuestionType;

  /** Identifier for Inspera */
  identifier: string;

  /** Title (optional) */
  title?: string;

  /** Points */
  points: number;

  /** Labels as hashtags */
  labels: string[];

  /** Shuffle options */
  shuffle?: boolean;

  /** Question text */
  questionText: string;

  /** Options (for MC) */
  options?: string[];

  /** Answer */
  answer: string;

  /** Feedback structure */
  feedback: {
    general: string;
    correct: string;
    incorrect: string;
    unanswered: string;
  };

  /** Option-specific feedback */
  optionFeedback?: Record<string, string>;
}

/**
 * M5 generation result.
 */
export interface M5GenerationResult {
  /** Whether generation succeeded */
  success: boolean;

  /** Generated QFMD content */
  qfmdContent?: string;

  /** Number of questions generated */
  questionCount: number;

  /** Any warnings during generation */
  warnings: string[];

  /** Errors that prevented generation */
  errors: string[];

  /** Questions that were skipped */
  skippedQuestions: string[];
}
