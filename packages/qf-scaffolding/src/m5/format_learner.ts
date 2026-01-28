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
  question_text?: string;
  answer?: string;
  feedback?: string;
  raw_content: string;
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
 */
export function detectFormat(
  content: string,
  patterns: FormatPattern[]
): DetectionResult {
  const contentLower = content.toLowerCase();
  const contentLines = content.split("\n").slice(0, 50); // Check first 50 lines

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

    // Calculate confidence
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
          confidence = Math.min(confidence + 5, 99);
        }
      }
    }

    // Update best match
    if (confidence > bestMatch.confidence) {
      bestMatch = {
        detected: confidence >= 70,
        pattern: pattern,
        confidence: confidence,
        matched_markers: matched,
        missing_markers: missing,
      };
    }
  }

  return bestMatch;
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
 * Parse content using a learned pattern
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

  // Split content by question separator
  const blocks = content.split(new RegExp(`\\n${separator}\\n`));

  for (const block of blocks) {
    if (!block.trim()) continue;

    const question: ParsedQuestion = { raw_content: block };

    // Extract fields using mappings
    for (const [marker, mapping] of Object.entries(pattern.mappings)) {
      if (mapping.qfmd_field === null) continue; // Skip ignored fields

      const value = extractFieldValue(block, marker, mapping);

      if (value !== null) {
        const field = mapping.qfmd_field;

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
