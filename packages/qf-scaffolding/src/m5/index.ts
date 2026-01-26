/**
 * M5 Module - Content Completeness & QFMD Generation
 *
 * M5 is responsible for:
 * 1. Parsing M3 human-readable format
 * 2. Checking content completeness per question type
 * 3. Generating QFMD output for the pipeline
 *
 * This module bridges the pedagogical scaffolding (M1-M4) with the
 * technical pipeline (Step 1-4).
 */

// Type exports
export type {
  QuestionType,
  BloomLevel,
  DifficultyLevel,
  M3Question,
  CompletenessIssue,
  CompletenessResult,
  QFMDQuestion,
  M5GenerationResult,
} from "./types.js";

export { M3_TYPE_MAP } from "./types.js";

// Import internal modules for processM3ToQFMD
import type { CompletenessResult, M5GenerationResult, M3Question } from "./types.js";
import { parseM3Content as _parseM3Content, getQuestionSummary as _getQuestionSummary } from "./parser.js";
import {
  checkCompleteness as _checkCompleteness,
  checkQuestion as _checkQuestion,
  resolveQuestionType as _resolveQuestionType,
  formatCompletenessReport as _formatCompletenessReport,
} from "./checker.js";
import {
  generateQFMD as _generateQFMD,
  generateQFMDFile as _generateQFMDFile,
  generateQFMDHeader as _generateQFMDHeader,
} from "./generator.js";

// Parser exports
export { parseM3Content, getQuestionSummary } from "./parser.js";

// Checker exports
export {
  checkCompleteness,
  checkQuestion,
  resolveQuestionType,
  formatCompletenessReport,
} from "./checker.js";

// Generator exports
export {
  generateQFMD,
  generateQFMDFile,
  generateQFMDHeader,
} from "./generator.js";

/**
 * Complete M5 workflow: Parse → Check → Generate
 *
 * @param content - M3 human-readable format content
 * @param options - Generation options
 * @returns Combined result with completeness check and QFMD
 */
export function processM3ToQFMD(
  content: string,
  options: {
    courseCode?: string;
    title?: string;
    includeHeader?: boolean;
    includeSourceComments?: boolean;
    skipIncomplete?: boolean;
  } = {}
): {
  completeness: CompletenessResult;
  generation: M5GenerationResult;
  summary: {
    totalQuestions: number;
    passedCompleteness: number;
    generatedQuestions: number;
    skippedQuestions: string[];
    hasErrors: boolean;
  };
} {
  // Step 1: Parse
  const questions: M3Question[] = _parseM3Content(content);

  // Step 2: Check completeness
  const completeness = _checkCompleteness(questions);

  // Step 3: Filter if requested
  let questionsToGenerate = questions;
  const skipped: string[] = [];

  if (options.skipIncomplete) {
    questionsToGenerate = questions.filter((q: M3Question) => {
      const status = completeness.questionStatus[q.questionNumber];
      if (status && status.status === "errors") {
        skipped.push(q.questionNumber);
        return false;
      }
      return true;
    });
  }

  // Step 4: Generate QFMD
  const generation = _generateQFMDFile(questionsToGenerate, options);

  // Combine skipped lists
  const allSkipped = [...new Set([...skipped, ...generation.skippedQuestions])];

  return {
    completeness,
    generation,
    summary: {
      totalQuestions: questions.length,
      passedCompleteness: completeness.passedQuestions,
      generatedQuestions: generation.questionCount,
      skippedQuestions: allSkipped,
      hasErrors:
        completeness.status === "errors" || generation.errors.length > 0,
    },
  };
}
