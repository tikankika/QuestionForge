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
// NOTE: parser.ts removed per RFC-016 (replaced by format_learner.ts)
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
import {
  loadPatterns,
  detectFormat,
  parseWithPattern,
  type ParsedQuestion,
} from "./format_learner.js";

// Format Learner exports (RFC-016 - replaces old parser)
export {
  loadPatterns,
  savePatterns,
  detectFormat,
  parseWithPattern,
  findPotentialMarkers,
  createPattern,
  updatePatternStats,
  toQFMD,
} from "./format_learner.js";

export type {
  FormatPattern,
  FieldMapping,
  DetectionResult,
  ParsedQuestion as FormatLearnerQuestion,
} from "./format_learner.js";

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
 * @deprecated RFC-016: Use m5_start MCP tool instead.
 *
 * This function used the old static parser which has been replaced by
 * the self-learning format_learner.ts. The interactive MCP tools
 * (m5_start, m5_approve, etc.) now use the new approach which:
 *
 * 1. Tries to detect format using LEARNED patterns
 * 2. If no pattern matches → asks teacher for help
 * 3. Teacher can teach new formats via m5_teach_format
 *
 * For programmatic access, use:
 * - loadPatterns(projectPath) - Load learned patterns
 * - detectFormat(content, patterns) - Detect format
 * - parseWithPattern(content, pattern) - Parse with a pattern
 * - toQFMD(questions) - Convert to QFMD format
 */
export function processM3ToQFMD(
  _content: string,
  _options: {
    courseCode?: string;
    title?: string;
    includeHeader?: boolean;
    includeSourceComments?: boolean;
    skipIncomplete?: boolean;
    projectPath?: string; // NEW: Required for self-learning
  } = {}
): never {
  throw new Error(
    "processM3ToQFMD is deprecated (RFC-016). " +
    "Use the m5_start MCP tool for interactive processing, or use " +
    "loadPatterns(), detectFormat(), parseWithPattern() directly."
  );
}
