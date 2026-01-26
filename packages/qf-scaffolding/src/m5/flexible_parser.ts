/**
 * M5 Flexible Parser
 *
 * Best-effort parsing of M3 human-readable format.
 * Identifies missing/uncertain fields for user confirmation.
 */

import type { QuestionType } from "./types.js";
import type { ParsedInterpretation } from "./session.js";

/**
 * Parse M3 content with best-effort extraction.
 * Returns interpretations with confidence scores and missing field lists.
 */
export function parseM3Flexible(content: string): ParsedInterpretation[] {
  const questions: ParsedInterpretation[] = [];
  const lines = content.split("\n");

  // Find question boundaries (### Q1, ### Q2, etc.)
  const questionStarts: number[] = [];
  for (let i = 0; i < lines.length; i++) {
    if (/^###\s+Q\d+/i.test(lines[i])) {
      questionStarts.push(i);
    }
  }

  // Parse each question
  for (let i = 0; i < questionStarts.length; i++) {
    const startLine = questionStarts[i];
    const endLine =
      i < questionStarts.length - 1 ? questionStarts[i + 1] : lines.length;

    const questionContent = lines.slice(startLine, endLine).join("\n");
    const parsed = parseQuestionFlexible(questionContent, startLine + 1);

    if (parsed) {
      questions.push(parsed);
    }
  }

  return questions;
}

/**
 * Parse a single question with best-effort extraction.
 */
function parseQuestionFlexible(
  content: string,
  lineNumber: number
): ParsedInterpretation | null {
  const lines = content.split("\n");

  // Extract question header: ### Q1 - Title or ### Q1
  const headerMatch = lines[0].match(/^###\s+(Q\d+)\s*-?\s*(.*)$/i);
  if (!headerMatch) {
    return null;
  }

  const questionNumber = headerMatch[1].toUpperCase();
  const headerTitle = headerMatch[2].trim() || null;

  // Initialize interpretation
  const interpretation: ParsedInterpretation = {
    questionNumber,
    fields: {
      title: { value: headerTitle, confidence: headerTitle ? 90 : 0, source: headerTitle ? "header" : "missing" },
      type: { value: null, confidence: 0, source: "missing", raw: "" },
      stem: { value: null, confidence: 0, source: "missing" },
      options: { value: [], confidence: 0, source: "missing" },
      answer: { value: null, confidence: 0, source: "missing" },
      feedback: {
        correct: { value: null, confidence: 0 },
        incorrect: { value: {}, confidence: 0 },
        general: { value: null, confidence: 0 },
      },
      labels: { value: [], confidence: 0, source: "missing" },
      points: { value: 1, confidence: 50, source: "default" },
      bloom: { value: null, confidence: 0, source: "missing" },
      difficulty: { value: null, confidence: 0, source: "missing" },
    },
    missingFields: [],
    uncertainFields: [],
    rawContent: content,
    lineNumber,
  };

  // Extract sections using flexible matching
  const sections = extractSections(content);

  // Parse metadata section
  if (sections.metadata) {
    parseMetadataFlexible(sections.metadata, interpretation);
  }

  // Parse labels section
  if (sections.labels) {
    parseLabelsFlexible(sections.labels, interpretation);
  }

  // Parse question stem
  if (sections.stem) {
    interpretation.fields.stem = {
      value: sections.stem.trim(),
      confidence: 95,
      source: "Question Stem section",
    };
  }

  // Parse options
  if (sections.options) {
    const options = parseOptionsFlexible(sections.options);
    interpretation.fields.options = {
      value: options,
      confidence: options.length > 0 ? 90 : 0,
      source: options.length > 0 ? "Answer Options section" : "missing",
    };
  }

  // Parse answer (try multiple patterns)
  const answer = extractAnswer(content);
  if (answer) {
    interpretation.fields.answer = {
      value: answer.value,
      confidence: answer.confidence,
      source: answer.source,
    };
  }

  // Parse feedback (flexible)
  parseFeedbackFlexible(sections.feedback || content, interpretation);

  // Determine missing and uncertain fields
  interpretation.missingFields = [];
  interpretation.uncertainFields = [];

  for (const [fieldName, field] of Object.entries(interpretation.fields)) {
    if (fieldName === "feedback") continue; // Handle separately

    const f = field as { value: any; confidence: number };
    if (f.value === null || (Array.isArray(f.value) && f.value.length === 0)) {
      if (isRequiredField(fieldName, interpretation.fields.type.value)) {
        interpretation.missingFields.push(fieldName);
      }
    } else if (f.confidence < 70) {
      interpretation.uncertainFields.push(fieldName);
    }
  }

  // Check feedback
  if (!interpretation.fields.feedback.correct.value &&
      !interpretation.fields.feedback.general.value) {
    interpretation.missingFields.push("feedback");
  }

  return interpretation;
}

/**
 * Extract sections from content using flexible matching.
 */
function extractSections(content: string): {
  metadata?: string;
  labels?: string;
  stem?: string;
  options?: string;
  answer?: string;
  feedback?: string;
} {
  const sections: {
    metadata?: string;
    labels?: string;
    stem?: string;
    options?: string;
    answer?: string;
    feedback?: string;
  } = {};

  // Split into lines for processing
  const lines = content.split("\n");
  let currentSection = "";
  let currentContent: string[] = [];

  const sectionPatterns: Record<string, RegExp[]> = {
    metadata: [/^\*\*Metadata/i, /^\*\*Meta/i],
    labels: [/^\*\*Labels/i, /^\*\*Etiketter/i, /^\*\*Tags/i],
    stem: [/^\*\*Question Stem/i, /^\*\*Frågetext/i, /^\*\*Question:/i, /^\*\*Fråga:/i],
    options: [/^\*\*Answer Options/i, /^\*\*Svarsalternativ/i, /^\*\*Options/i, /^\*\*Alternativ/i],
    answer: [/^\*\*Correct Answer/i, /^\*\*Rätt svar/i, /^\*\*Answer:/i, /^\*\*Svar:/i],
    feedback: [/^\*\*Feedback/i, /^\*\*Återkoppling/i],
  };

  for (const line of lines) {
    let foundSection = false;

    for (const [sectionName, patterns] of Object.entries(sectionPatterns)) {
      for (const pattern of patterns) {
        if (pattern.test(line)) {
          // Save previous section
          if (currentSection && currentContent.length > 0) {
            sections[currentSection as keyof typeof sections] = currentContent.join("\n");
          }
          currentSection = sectionName;
          currentContent = [];
          foundSection = true;

          // Check for inline content (e.g., "**Correct Answer:** A")
          const inlineMatch = line.match(/\*\*[^*]+\*\*:?\s*(.+)/);
          if (inlineMatch && inlineMatch[1].trim()) {
            currentContent.push(inlineMatch[1].trim());
          }
          break;
        }
      }
      if (foundSection) break;
    }

    if (!foundSection && currentSection) {
      currentContent.push(line);
    }
  }

  // Save last section
  if (currentSection && currentContent.length > 0) {
    sections[currentSection as keyof typeof sections] = currentContent.join("\n");
  }

  return sections;
}

/**
 * Parse metadata section flexibly.
 */
function parseMetadataFlexible(
  metadataText: string,
  interpretation: ParsedInterpretation
): void {
  const lines = metadataText.split("\n");

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("**")) continue;

    // Try to match "- Key: Value" or "Key: Value" or "- Key Value"
    const match = trimmed.match(/^-?\s*(\w+):?\s*(.+)$/);
    if (!match) continue;

    const key = match[1].toLowerCase();
    const value = match[2].trim();

    switch (key) {
      case "type":
      case "typ":
      case "frågetyp":
        const resolvedType = resolveTypeFlexible(value);
        interpretation.fields.type = {
          value: resolvedType.type,
          confidence: resolvedType.confidence,
          source: `Metadata: "${value}"`,
          raw: value,
        };
        break;

      case "bloom":
        interpretation.fields.bloom = {
          value: normalizeBloom(value),
          confidence: 90,
          source: "Metadata",
        };
        break;

      case "difficulty":
      case "svårighetsgrad":
        interpretation.fields.difficulty = {
          value: normalizeDifficulty(value),
          confidence: 90,
          source: "Metadata",
        };
        break;

      case "points":
      case "poäng":
        const points = parseInt(value, 10);
        interpretation.fields.points = {
          value: isNaN(points) ? 1 : points,
          confidence: isNaN(points) ? 50 : 95,
          source: "Metadata",
        };
        break;

      case "lo":
      case "learningobjective":
        // Add LO to labels
        interpretation.fields.labels.value.push(value);
        break;
    }
  }
}

/**
 * Resolve type string to QuestionType with confidence.
 */
function resolveTypeFlexible(raw: string): {
  type: QuestionType | null;
  confidence: number;
} {
  const lower = raw.toLowerCase();

  // High confidence matches
  if (lower.includes("multiple choice") && lower.includes("single")) {
    return { type: "multiple_choice_single", confidence: 95 };
  }
  if (lower.includes("mc-single") || lower === "mc") {
    return { type: "multiple_choice_single", confidence: 90 };
  }
  if (lower.includes("multiple response") || lower.includes("mc-multiple") || lower.includes("mr")) {
    return { type: "multiple_response", confidence: 90 };
  }
  if (lower.includes("true") && lower.includes("false")) {
    return { type: "true_false", confidence: 95 };
  }
  if (lower.includes("sant") && lower.includes("falskt")) {
    return { type: "true_false", confidence: 95 };
  }
  if (lower.includes("inline choice") || lower.includes("dropdown")) {
    return { type: "inline_choice", confidence: 90 };
  }
  if (lower.includes("text entry") || lower.includes("fyll i")) {
    return { type: "text_entry", confidence: 85 };
  }
  if (lower.includes("match")) {
    return { type: "match", confidence: 90 };
  }
  if (lower.includes("essay") || lower.includes("essä")) {
    return { type: "essay", confidence: 90 };
  }

  // Medium confidence - guess from context
  if (lower.includes("multiple")) {
    return { type: "multiple_choice_single", confidence: 60 };
  }

  return { type: null, confidence: 0 };
}

/**
 * Parse labels section.
 */
function parseLabelsFlexible(
  labelsText: string,
  interpretation: ParsedInterpretation
): void {
  const lines = labelsText.split("\n");
  const labels: string[] = [];

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("**")) continue;

    // Match "- Label" format
    const match = trimmed.match(/^-\s*(.+)$/);
    if (match) {
      const label = match[1].trim();
      if (label) labels.push(label);
    }
  }

  if (labels.length > 0) {
    interpretation.fields.labels = {
      value: labels,
      confidence: 90,
      source: "Labels section",
    };
  }
}

/**
 * Parse options flexibly.
 */
function parseOptionsFlexible(optionsText: string): string[] {
  const options: string[] = [];
  const lines = optionsText.split("\n");

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    // Match various formats: "A)", "A.", "a)", "1)", "1." etc.
    const match = trimmed.match(/^([A-Fa-f]|[1-6])[.)]\s*(.+)$/);
    if (match) {
      const letter = match[1].toUpperCase();
      const content = match[2].trim();

      // Normalize to "A. content" format
      const normalized =
        letter.match(/[1-6]/)
          ? `${"ABCDEF"[parseInt(letter) - 1]}. ${content}`
          : `${letter}. ${content}`;

      options.push(normalized);
    }
  }

  return options;
}

/**
 * Extract answer from content using multiple patterns.
 */
function extractAnswer(content: string): {
  value: string;
  confidence: number;
  source: string;
} | null {
  // Try various patterns

  // Pattern 1: **Correct Answer:** A
  const single = content.match(/\*\*Correct Answer:?\*\*:?\s*([A-Fa-f,\s]+)/i);
  if (single) {
    return {
      value: normalizeAnswer(single[1]),
      confidence: 95,
      source: "Correct Answer field",
    };
  }

  // Pattern 2: **Correct Answers:** A, C, E (plural for multiple response)
  const multiple = content.match(/\*\*Correct Answers:?\*\*:?\s*([A-Fa-f,\s]+)/i);
  if (multiple) {
    return {
      value: normalizeAnswer(multiple[1]),
      confidence: 95,
      source: "Correct Answers field",
    };
  }

  // Pattern 3: **Rätt svar:** A
  const swedish = content.match(/\*\*Rätt svar:?\*\*:?\s*([A-Fa-f,\s]+)/i);
  if (swedish) {
    return {
      value: normalizeAnswer(swedish[1]),
      confidence: 95,
      source: "Rätt svar field",
    };
  }

  // Pattern 4: True/False answer
  const tfMatch = content.match(/\*\*(?:Correct Answer|Rätt svar):?\*\*:?\s*(True|False|Sant|Falskt)/i);
  if (tfMatch) {
    const tfVal = tfMatch[1].toLowerCase();
    return {
      value: tfVal === "true" || tfVal === "sant" ? "True" : "False",
      confidence: 95,
      source: "True/False answer",
    };
  }

  // Pattern 5: Look in feedback for correct indicator
  const feedbackCorrect = content.match(/\*\*Correct \(([A-F,\s]+)\)/i);
  if (feedbackCorrect) {
    return {
      value: normalizeAnswer(feedbackCorrect[1]),
      confidence: 80,
      source: "Inferred from feedback",
    };
  }

  return null;
}

/**
 * Normalize answer string.
 */
function normalizeAnswer(raw: string): string {
  return raw
    .toUpperCase()
    .replace(/[^A-F,]/g, "")
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s)
    .join(", ");
}

/**
 * Parse feedback flexibly.
 */
function parseFeedbackFlexible(
  text: string,
  interpretation: ParsedInterpretation
): void {
  // Pattern 1: **Correct (A):** text
  const correctMatch = text.match(/\*\*Correct \([^)]+\):?\*\*:?\s*([^\n*]+(?:\n(?!\*\*)[^\n*]+)*)/i);
  if (correctMatch) {
    interpretation.fields.feedback.correct = {
      value: correctMatch[1].trim(),
      confidence: 90,
    };
  }

  // Pattern 2: **Incorrect (B):** text - extract all
  const incorrectPattern = /\*\*Incorrect \(([A-F])[^)]*\):?\*\*:?\s*([^\n*]+(?:\n(?!\*\*)[^\n*]+)*)/gi;
  let match;
  while ((match = incorrectPattern.exec(text)) !== null) {
    interpretation.fields.feedback.incorrect.value[match[1].toUpperCase()] =
      match[2].trim();
    interpretation.fields.feedback.incorrect.confidence = 90;
  }

  // Pattern 3: General feedback without option indicator
  if (!interpretation.fields.feedback.correct.value) {
    // Look for any feedback-like text after "**Feedback:**"
    const generalMatch = text.match(/\*\*Feedback:?\*\*\s*\n+([^*\n][^\n]+)/i);
    if (generalMatch) {
      interpretation.fields.feedback.general = {
        value: generalMatch[1].trim(),
        confidence: 70,
      };
    }
  }
}

/**
 * Check if a field is required for the question type.
 */
function isRequiredField(
  fieldName: string,
  type: QuestionType | null
): boolean {
  const alwaysRequired = ["title", "type", "stem"];
  if (alwaysRequired.includes(fieldName)) return true;

  if (!type) return false;

  // Type-specific requirements
  if (type === "multiple_choice_single" || type === "multiple_response") {
    return ["options", "answer"].includes(fieldName);
  }

  if (type === "true_false") {
    return fieldName === "answer";
  }

  if (type === "text_entry" || type === "inline_choice") {
    return fieldName === "answer";
  }

  return false;
}

/**
 * Normalize Bloom level.
 */
function normalizeBloom(value: string): string {
  const lower = value.toLowerCase();
  if (lower.includes("remember") || lower.includes("minnas")) return "Remember";
  if (lower.includes("understand") || lower.includes("förstå")) return "Understand";
  if (lower.includes("apply") || lower.includes("tillämpa")) return "Apply";
  if (lower.includes("analyze") || lower.includes("analysera")) return "Analyze";
  if (lower.includes("evaluate") || lower.includes("utvärdera")) return "Evaluate";
  if (lower.includes("create") || lower.includes("skapa")) return "Create";
  return value;
}

/**
 * Normalize difficulty level.
 */
function normalizeDifficulty(value: string): string {
  const lower = value.toLowerCase();
  if (lower.includes("easy") || lower.includes("enkel") || lower.includes("lätt")) return "Easy";
  if (lower.includes("medium") || lower.includes("medel")) return "Medium";
  if (lower.includes("hard") || lower.includes("svår")) return "Hard";
  return value;
}
