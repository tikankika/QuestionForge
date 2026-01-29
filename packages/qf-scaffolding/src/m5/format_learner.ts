/**
 * M5 Format Learner (RFC-016)
 *
 * Self-learning format recognition system.
 * Instead of hardcoded parsers, M5 learns formats from teacher.
 *
 * Similar to Step 3's fix_rules.json but for format recognition.
 */

import * as fs from "fs";
import * as path from "path";

// ============================================================================
// Types
// ============================================================================

export interface FieldMapping {
  qfmd_field: string | null; // null = skip/ignore
  extraction: "single_line" | "multiline_until_next" | "number" | "tags" | "skip";
  transform?: "prepend_hash" | "keep_as_is";
  required?: boolean;
}

export interface FormatPattern {
  pattern_id: string;
  name: string;
  description?: string;
  builtin?: boolean; // true for migrated hardcoded patterns

  learned_from?: {
    session_id: string;
    date: string;
    teacher_confirmed: boolean;
  };

  detection: {
    required_markers: string[];
    optional_markers?: string[];
    question_separator?: string;
  };

  mappings: Record<string, FieldMapping> | "passthrough";

  statistics: {
    times_used: number;
    questions_processed: number;
    last_used?: string;
    teacher_corrections: number;
  };
}

export interface FormatPatternsFile {
  version: string;
  patterns: FormatPattern[];
}

export interface DetectionResult {
  detected: boolean;
  pattern?: FormatPattern;
  confidence: number;
  matched_markers: string[];
  missing_markers: string[];
}

export interface ParsedQuestion {
  title?: string;
  type?: string;
  identifier?: string;
  points?: number;
  labels?: string;
  question_text?: string;  // Also accepts "stem"
  answer?: string;
  feedback?: string;
  bloom?: string;
  difficulty?: string;
  learning_objective?: string;
  // Nested feedback fields
  feedback_correct?: string;
  feedback_incorrect?: string;
  feedback_partial?: string;
  raw_content: string;
}

// ============================================================================
// Validation Result (BUG 3 & 7 FIX)
// ============================================================================

export interface ParseValidation {
  is_valid: boolean;
  warnings: string[];
  errors: string[];
  fields_found: string[];
  fields_missing: string[];
  confidence_issues: Array<{ field: string; confidence: number; reason: string }>;
}

export interface ParseResult {
  questions: ParsedQuestion[];
  validation: ParseValidation;
  pattern_used: string;
}

// ============================================================================
// Default Patterns (migrated from hardcoded flexible_parser.ts)
// ============================================================================

const DEFAULT_PATTERNS: FormatPattern[] = [
  {
    pattern_id: "M5_FMT_BUILTIN_001",
    name: "QFMD v6.5 Native",
    description: "Already in QFMD format - passthrough",
    builtin: true,
    detection: {
      required_markers: ["^type", "^identifier", "@field:"],
    },
    mappings: "passthrough",
    statistics: {
      times_used: 0,
      questions_processed: 0,
      teacher_corrections: 0,
    },
  },
  {
    pattern_id: "M5_FMT_BUILTIN_002",
    name: "Markdown Headers (### QN)",
    description: "### Q1, ### Q2 format",
    builtin: true,
    detection: {
      required_markers: ["### Q"],
      question_separator: "---",
    },
    mappings: {
      "### Q": {
        qfmd_field: "question_number",
        extraction: "single_line",
      },
    },
    statistics: {
      times_used: 0,
      questions_processed: 0,
      teacher_corrections: 0,
    },
  },
  {
    pattern_id: "M5_FMT_BUILTIN_003",
    name: "Markdown Headers (## Question N)",
    description: "## Question 1, ## Fråga 1 format",
    builtin: true,
    detection: {
      required_markers: ["## Question", "## Fråga"],
      question_separator: "---",
    },
    mappings: {
      "## Question": {
        qfmd_field: "question_number",
        extraction: "single_line",
      },
      "## Fråga": {
        qfmd_field: "question_number",
        extraction: "single_line",
      },
    },
    statistics: {
      times_used: 0,
      questions_processed: 0,
      teacher_corrections: 0,
    },
  },
];

// ============================================================================
// Core Functions
// ============================================================================

/**
 * Get path to format patterns file for a project
 */
export function getPatternsFilePath(projectPath: string): string {
  return path.join(projectPath, "logs", "m5_format_patterns.json");
}

/**
 * Load patterns from project (or return defaults)
 */
export function loadPatterns(projectPath: string): FormatPatternsFile {
  const filePath = getPatternsFilePath(projectPath);

  if (fs.existsSync(filePath)) {
    try {
      const content = fs.readFileSync(filePath, "utf-8");
      const data = JSON.parse(content) as FormatPatternsFile;

      // Merge with defaults (in case new builtins added)
      const existingIds = new Set(data.patterns.map((p) => p.pattern_id));
      for (const defaultPattern of DEFAULT_PATTERNS) {
        if (!existingIds.has(defaultPattern.pattern_id)) {
          data.patterns.push(defaultPattern);
        }
      }

      return data;
    } catch (e) {
      console.error("Error loading patterns file:", e);
    }
  }

  // Return defaults
  return {
    version: "1.0",
    patterns: [...DEFAULT_PATTERNS],
  };
}

/**
 * Save patterns to project
 */
export function savePatterns(
  projectPath: string,
  data: FormatPatternsFile
): void {
  const filePath = getPatternsFilePath(projectPath);
  const logsDir = path.dirname(filePath);

  // Ensure logs directory exists
  if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
  }

  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), "utf-8");
}

/**
 * Detect which format pattern matches the content
 *
 * BUG FIX (2026-01-28):
 * - Now validates that separator actually works with content
 * - Prefers patterns with working separators over broken ones
 * - Uses statistics (times_used, corrections) as tiebreaker
 */
export function detectFormat(
  content: string,
  patterns: FormatPattern[]
): DetectionResult {
  const contentLower = content.toLowerCase();

  let bestMatch: DetectionResult = {
    detected: false,
    confidence: 0,
    matched_markers: [],
    missing_markers: [],
  };

  for (const pattern of patterns) {
    const { required_markers, optional_markers } = pattern.detection;

    // Check required markers
    const matched: string[] = [];
    const missing: string[] = [];

    for (const marker of required_markers) {
      // Check if marker exists in content (case-insensitive for some)
      const markerLower = marker.toLowerCase();
      let found = false;

      // For markers like "^type", check exact
      if (marker.startsWith("^") || marker.startsWith("@")) {
        found = content.includes(marker);
      } else {
        // For text markers like "**Title:**", check case-insensitive
        found =
          contentLower.includes(markerLower) || content.includes(marker);
      }

      if (found) {
        matched.push(marker);
      } else {
        missing.push(marker);
      }
    }

    // Calculate base confidence
    const requiredCount = required_markers.length;
    const matchedCount = matched.length;

    // For OR-style markers (like ["## Question", "## Fråga"]), at least one must match
    const hasOrMarkers =
      required_markers.length > 1 &&
      required_markers.some((m) => m.includes("Question") || m.includes("Fråga"));

    let confidence = 0;
    if (hasOrMarkers && matchedCount > 0) {
      confidence = 80; // At least one OR marker matched
    } else if (matchedCount === requiredCount) {
      confidence = 95; // All required markers matched
    } else if (matchedCount > 0) {
      confidence = (matchedCount / requiredCount) * 70; // Partial match
    }

    // Check optional markers for bonus confidence
    if (optional_markers && confidence > 0) {
      for (const marker of optional_markers) {
        if (content.includes(marker) || contentLower.includes(marker.toLowerCase())) {
          confidence = Math.min(confidence + 2, 99);
        }
      }
    }

    // BUG FIX: Validate separator actually works with this content
    // A pattern with non-working separator should be penalized heavily
    if (confidence > 0 && pattern.detection.question_separator) {
      const separator = pattern.detection.question_separator;
      const testSplit = splitByQuestionSeparator(content, separator);

      if (testSplit.length <= 1) {
        // Separator didn't split anything - penalize this pattern
        confidence = Math.max(confidence - 30, 10);
      } else {
        // Separator works! Bonus confidence
        confidence = Math.min(confidence + 5, 99);
      }
    }

    // BUG FIX: Use statistics as tiebreaker
    // Prefer patterns that have been used successfully before
    if (confidence > 0 && pattern.statistics) {
      const successRate = pattern.statistics.questions_processed > 0
        ? (pattern.statistics.questions_processed - pattern.statistics.teacher_corrections)
          / pattern.statistics.questions_processed
        : 0.5;

      // Small bonus for proven patterns (max +3)
      confidence = Math.min(confidence + (successRate * 3), 99);
    }

    // Update best match (use >= to prefer later patterns with same score)
    if (confidence >= bestMatch.confidence && confidence >= 70) {
      bestMatch = {
        detected: true,
        pattern: pattern,
        confidence: Math.round(confidence),
        matched_markers: matched,
        missing_markers: missing,
      };
    }
  }

  return bestMatch;
}

/**
 * Smart split that handles various separator formats
 *
 * BUG FIX (2026-01-28):
 * - Handles "---" correctly
 * - Handles header patterns like "## Question" (splits BEFORE each header)
 * - Returns meaningful blocks instead of failing silently
 */
function splitByQuestionSeparator(content: string, separator: string): string[] {
  // Case 1: Standard "---" separator
  if (separator === "---") {
    return content.split(/\n---\n/);
  }

  // Case 2: Header pattern like "## Question", "### Q", etc.
  // Split BEFORE each occurrence (keeping the header with its content)
  if (separator.startsWith("#")) {
    // Escape special regex characters
    const escaped = separator.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    // Match separator followed by optional space and number/text
    // Use lookahead to split BEFORE the pattern
    const regex = new RegExp(`(?=\\n${escaped}[\\s\\d])`, 'g');
    const parts = content.split(regex);
    return parts.filter(p => p.trim().length > 0);
  }

  // Case 3: Default - try exact match with newlines
  const parts = content.split(new RegExp(`\\n${separator}\\n`));
  return parts.filter(p => p.trim().length > 0);
}

/**
 * Find potential markers in content (for asking teacher)
 */
export function findPotentialMarkers(content: string): string[] {
  const markers: string[] = [];
  const lines = content.split("\n").slice(0, 50);

  for (const line of lines) {
    // Look for **Label:** patterns
    const boldMatch = line.match(/^\*\*([^*]+):\*\*/);
    if (boldMatch) {
      markers.push(`**${boldMatch[1]}:**`);
    }

    // Look for Label: patterns at start of line
    const labelMatch = line.match(/^([A-Z][a-z]+):\s/);
    if (labelMatch) {
      markers.push(`${labelMatch[1]}:`);
    }

    // Look for # headers
    const headerMatch = line.match(/^(#{1,3})\s+(.+)/);
    if (headerMatch) {
      markers.push(`${headerMatch[1]} [header]`);
    }
  }

  // Remove duplicates
  return [...new Set(markers)];
}

/**
 * Generate a unique pattern ID
 */
export function generatePatternId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 6);
  return `M5_FMT_${timestamp}_${random}`.toUpperCase();
}

/**
 * Create a new pattern from teacher input
 */
export function createPattern(
  name: string,
  mappings: Record<string, FieldMapping>,
  questionSeparator: string,
  sessionId: string
): FormatPattern {
  // Determine required markers from mappings
  const requiredMarkers = Object.keys(mappings).filter(
    (key) => mappings[key].required !== false && mappings[key].qfmd_field !== null
  );

  return {
    pattern_id: generatePatternId(),
    name: name,
    learned_from: {
      session_id: sessionId,
      date: new Date().toISOString(),
      teacher_confirmed: true,
    },
    detection: {
      required_markers: requiredMarkers.slice(0, 3), // Use first 3 as detection markers
      question_separator: questionSeparator,
    },
    mappings: mappings,
    statistics: {
      times_used: 0,
      questions_processed: 0,
      teacher_corrections: 0,
    },
  };
}

/**
 * Add a pattern to the patterns file
 */
export function addPattern(projectPath: string, pattern: FormatPattern): void {
  const data = loadPatterns(projectPath);
  data.patterns.push(pattern);
  savePatterns(projectPath, data);
}

/**
 * Update pattern statistics after use
 */
export function updatePatternStats(
  projectPath: string,
  patternId: string,
  questionsProcessed: number,
  correction: boolean = false
): void {
  const data = loadPatterns(projectPath);
  const pattern = data.patterns.find((p) => p.pattern_id === patternId);

  if (pattern) {
    pattern.statistics.times_used++;
    pattern.statistics.questions_processed += questionsProcessed;
    pattern.statistics.last_used = new Date().toISOString();
    if (correction) {
      pattern.statistics.teacher_corrections++;
    }
    savePatterns(projectPath, data);
  }
}

/**
 * Normalize field names to standard ParsedQuestion fields (BUG 4 FIX)
 * Handles various field name conventions from different patterns
 */
function normalizeFieldName(field: string): string {
  const fieldMap: Record<string, string> = {
    // Stem variants
    "stem": "question_text",
    "question": "question_text",
    "fråga": "question_text",
    // Feedback variants (dotted notation)
    "feedback.correct": "feedback_correct",
    "feedback.incorrect": "feedback_incorrect",
    "feedback.partial": "feedback_partial",
    "general_feedback": "feedback",
    // Keep these as-is
    "title": "title",
    "type": "type",
    "points": "points",
    "answer": "answer",
    "bloom": "bloom",
    "difficulty": "difficulty",
    "labels": "labels",
    "tags": "labels",  // Normalize tags to labels
    "learning_objective": "learning_objective",
    "question_text": "question_text",
    "feedback": "feedback",
  };

  return fieldMap[field.toLowerCase()] || field;
}

/**
 * Parse content using a learned pattern
 *
 * BUG FIX (2026-01-28):
 * - Uses smart splitByQuestionSeparator() instead of broken regex
 * - Logs warning if split produces unexpected results
 *
 * BUG FIX (2026-01-29) - BUG 3, 4, 7:
 * - Normalizes field names to standard ParsedQuestion fields
 * - Validates parsed results
 * - Returns warnings for missing/low-confidence fields
 */
export function parseWithPattern(
  content: string,
  pattern: FormatPattern
): ParsedQuestion[] {
  if (pattern.mappings === "passthrough") {
    // Content is already QFMD - return as single question
    return [{ raw_content: content }];
  }

  const questions: ParsedQuestion[] = [];
  const separator = pattern.detection.question_separator || "---";

  // BUG FIX: Use smart split that handles various separator formats
  const blocks = splitByQuestionSeparator(content, separator);

  for (const block of blocks) {
    if (!block.trim()) continue;

    const question: ParsedQuestion = { raw_content: block };

    // Extract fields using mappings
    for (const [marker, mapping] of Object.entries(pattern.mappings)) {
      if (mapping.qfmd_field === null) continue; // Skip ignored fields

      const value = extractFieldValue(block, marker, mapping);

      if (value !== null) {
        // BUG 4 FIX: Normalize field name
        const field = normalizeFieldName(mapping.qfmd_field);

        if (mapping.transform === "prepend_hash" && !value.startsWith("#")) {
          (question as any)[field] =
            ((question as any)[field] || "") + ` #${value}`;
        } else if (field === "labels") {
          (question as any)[field] =
            ((question as any)[field] || "") + ` ${value}`;
        } else if (field === "points") {
          question.points = parseInt(value, 10);
        } else {
          (question as any)[field] = value;
        }
      }
    }

    // Clean up labels
    if (question.labels) {
      question.labels = question.labels.trim();
    }

    questions.push(question);
  }

  return questions.filter(
    (q) => q.title || q.question_text || Object.keys(q).length > 1
  );
}

/**
 * Parse with validation - returns detailed validation info (BUG 3 & 7 FIX)
 */
export function parseWithPatternValidated(
  content: string,
  pattern: FormatPattern
): ParseResult {
  const questions = parseWithPattern(content, pattern);

  // Validate results
  const validation: ParseValidation = {
    is_valid: true,
    warnings: [],
    errors: [],
    fields_found: [],
    fields_missing: [],
    confidence_issues: [],
  };

  // Required fields for a valid question
  const requiredFields = ["title", "type", "question_text"];
  const importantFields = ["answer", "bloom", "difficulty"];

  for (let i = 0; i < questions.length; i++) {
    const q = questions[i];
    const qNum = i + 1;

    // Check required fields
    for (const field of requiredFields) {
      const value = (q as any)[field];
      if (!value || (typeof value === "string" && !value.trim())) {
        validation.errors.push(`Q${qNum}: Saknar obligatoriskt fält '${field}'`);
        validation.fields_missing.push(`Q${qNum}.${field}`);
        validation.is_valid = false;
      } else {
        validation.fields_found.push(`Q${qNum}.${field}`);
      }
    }

    // Check important fields (warnings, not errors)
    for (const field of importantFields) {
      const value = (q as any)[field];
      if (!value || (typeof value === "string" && !value.trim())) {
        validation.warnings.push(`Q${qNum}: Saknar fält '${field}' (rekommenderas)`);
        validation.fields_missing.push(`Q${qNum}.${field}`);
      } else {
        validation.fields_found.push(`Q${qNum}.${field}`);
      }
    }

    // Check feedback fields
    if (!q.feedback && !q.feedback_correct) {
      validation.warnings.push(`Q${qNum}: Saknar feedback`);
    }
  }

  // Global validation
  if (questions.length === 0) {
    validation.errors.push("Inga frågor hittades!");
    validation.is_valid = false;
  }

  return {
    questions,
    validation,
    pattern_used: pattern.name,
  };
}

/**
 * Extract a field value from content block using mapping rules
 */
function extractFieldValue(
  block: string,
  marker: string,
  mapping: FieldMapping
): string | null {
  const lines = block.split("\n");

  // Find line containing marker
  let startIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes(marker)) {
      startIdx = i;
      break;
    }
  }

  if (startIdx === -1) return null;

  const line = lines[startIdx];

  switch (mapping.extraction) {
    case "single_line": {
      // Extract value after marker on same line
      const afterMarker = line.split(marker)[1] || "";
      return afterMarker.trim();
    }

    case "number": {
      const afterMarker = line.split(marker)[1] || "";
      const match = afterMarker.match(/\d+/);
      return match ? match[0] : null;
    }

    case "tags": {
      const afterMarker = line.split(marker)[1] || "";
      return afterMarker.trim();
    }

    case "multiline_until_next": {
      // Get all content until next marker or end
      const contentLines: string[] = [];

      // Start with rest of current line
      const afterMarker = line.split(marker)[1] || "";
      if (afterMarker.trim()) {
        contentLines.push(afterMarker.trim());
      }

      // Continue with following lines
      for (let i = startIdx + 1; i < lines.length; i++) {
        const nextLine = lines[i];

        // Stop if we hit another marker (bold label or separator)
        if (/^\*\*[^*]+:\*\*/.test(nextLine) || nextLine.trim() === "---") {
          break;
        }

        contentLines.push(nextLine);
      }

      return contentLines.join("\n").trim();
    }

    case "skip":
      return null;

    default:
      return null;
  }
}

/**
 * Convert parsed questions to QFMD format
 */
export function toQFMD(questions: ParsedQuestion[]): string {
  const qfmdBlocks: string[] = [];

  for (let i = 0; i < questions.length; i++) {
    const q = questions[i];
    const qNum = i + 1;
    const lines: string[] = [];

    // Header
    lines.push(`### Q${String(qNum).padStart(3, "0")} ${q.title || "Untitled"}`);
    lines.push(`^type ${q.type || "essay"}`);
    lines.push(`^identifier Q${String(qNum).padStart(3, "0")}`);
    lines.push(`^points ${q.points || 1}`);

    if (q.labels) {
      lines.push(`^labels ${q.labels}`);
    }

    lines.push("");

    // Question text
    if (q.question_text) {
      lines.push("@field: question_text");
      lines.push(q.question_text);
      lines.push("@end_field");
      lines.push("");
    }

    // Answer (for essay, this goes in feedback)
    if (q.answer) {
      lines.push("@field: feedback");
      lines.push("");
      lines.push("@@field: general_feedback");
      lines.push(q.answer);
      lines.push("@@end_field");
      lines.push("");
      lines.push("@end_field");
    }

    qfmdBlocks.push(lines.join("\n"));
  }

  return qfmdBlocks.join("\n\n---\n\n");
}
