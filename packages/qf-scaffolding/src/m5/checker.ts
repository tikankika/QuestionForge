/**
 * M5 Checker - Content Completeness Verification
 *
 * Checks that all required fields are present for each question type.
 * Uses Step 4 specs as source of truth for required fields.
 */

import type {
  M3Question,
  QuestionType,
  CompletenessIssue,
  CompletenessResult,
  M3_TYPE_MAP,
} from "./types.js";

/**
 * Required fields per question type.
 * Based on qf-pipeline/specs/*.yaml (Step 4 source of truth).
 */
const TYPE_REQUIREMENTS: Record<
  QuestionType,
  {
    requiredMetadata: string[];
    requiredFields: string[];
    optionalFields: string[];
    constraints: Record<string, (q: M3Question) => string | null>;
  }
> = {
  multiple_choice_single: {
    requiredMetadata: ["type", "points", "bloom", "difficulty"],
    requiredFields: ["questionStem", "options", "correctAnswer", "feedback"],
    optionalFields: ["labels", "images"],
    constraints: {
      minOptions: (q) =>
        q.options.length < 3
          ? `Endast ${q.options.length} alternativ, minimum är 3`
          : null,
      maxOptions: (q) =>
        q.options.length > 6
          ? `${q.options.length} alternativ, rekommenderat max är 6`
          : null,
      singleAnswer: (q) =>
        q.correctAnswer.includes(",")
          ? "Flera svar angivna - borde vara multiple_response?"
          : null,
      validAnswer: (q) => {
        const answer = q.correctAnswer.trim().toUpperCase();
        const validLetters = q.options.map((_, i) => "ABCDEF"[i]);
        return !validLetters.includes(answer)
          ? `Svar "${answer}" matchar inte något alternativ`
          : null;
      },
    },
  },

  multiple_response: {
    requiredMetadata: ["type", "points", "bloom", "difficulty"],
    requiredFields: ["questionStem", "options", "correctAnswer", "feedback"],
    optionalFields: ["labels", "images"],
    constraints: {
      minOptions: (q) =>
        q.options.length < 3
          ? `Endast ${q.options.length} alternativ, minimum är 3`
          : null,
      multipleAnswers: (q) =>
        !q.correctAnswer.includes(",") && !q.correctAnswer.includes(" och ")
          ? "Endast ett svar angivet - borde vara multiple_choice_single?"
          : null,
    },
  },

  true_false: {
    requiredMetadata: ["type", "points", "bloom", "difficulty"],
    requiredFields: ["questionStem", "correctAnswer", "feedback"],
    optionalFields: ["labels"],
    constraints: {
      validAnswer: (q) => {
        const answer = q.correctAnswer.toLowerCase().trim();
        const valid = ["true", "false", "sant", "falskt", "t", "f"];
        return !valid.includes(answer)
          ? `Svar "${answer}" är inte giltigt för Sant/Falskt`
          : null;
      },
    },
  },

  inline_choice: {
    requiredMetadata: ["type", "points", "bloom", "difficulty"],
    requiredFields: ["questionStem", "options", "correctAnswer", "feedback"],
    optionalFields: ["labels"],
    constraints: {},
  },

  text_entry: {
    requiredMetadata: ["type", "points", "bloom", "difficulty"],
    requiredFields: ["questionStem", "correctAnswer", "feedback"],
    optionalFields: ["labels"],
    constraints: {},
  },

  text_entry_math: {
    requiredMetadata: ["type", "points", "bloom", "difficulty"],
    requiredFields: ["questionStem", "correctAnswer", "feedback"],
    optionalFields: ["labels"],
    constraints: {},
  },

  text_entry_numeric: {
    requiredMetadata: ["type", "points", "bloom", "difficulty"],
    requiredFields: ["questionStem", "correctAnswer", "feedback"],
    optionalFields: ["labels", "tolerance"],
    constraints: {
      numericAnswer: (q) => {
        const answer = q.correctAnswer.trim();
        if (isNaN(parseFloat(answer))) {
          return `Svar "${answer}" är inte numeriskt`;
        }
        return null;
      },
    },
  },

  text_area: {
    requiredMetadata: ["type", "points", "bloom", "difficulty"],
    requiredFields: ["questionStem", "feedback"],
    optionalFields: ["labels", "rubric"],
    constraints: {},
  },

  essay: {
    requiredMetadata: ["type", "points", "bloom", "difficulty"],
    requiredFields: ["questionStem"],
    optionalFields: ["labels", "rubric", "feedback"],
    constraints: {},
  },

  match: {
    requiredMetadata: ["type", "points", "bloom", "difficulty"],
    requiredFields: ["questionStem", "options", "correctAnswer", "feedback"],
    optionalFields: ["labels"],
    constraints: {
      minPairs: (q) =>
        q.options.length < 2
          ? `Endast ${q.options.length} matchningspar, minimum är 2`
          : null,
    },
  },

  hotspot: {
    requiredMetadata: ["type", "points", "bloom", "difficulty"],
    requiredFields: ["questionStem", "images", "correctAnswer", "feedback"],
    optionalFields: ["labels"],
    constraints: {
      hasImage: (q) =>
        !q.images || q.images.length === 0
          ? "Hotspot kräver minst en bild"
          : null,
    },
  },

  graphicgapmatch_v2: {
    requiredMetadata: ["type", "points", "bloom", "difficulty"],
    requiredFields: ["questionStem", "images", "options", "feedback"],
    optionalFields: ["labels"],
    constraints: {
      hasImage: (q) =>
        !q.images || q.images.length === 0
          ? "GraphicGapMatch kräver minst en bild"
          : null,
    },
  },

  text_entry_graphic: {
    requiredMetadata: ["type", "points", "bloom", "difficulty"],
    requiredFields: ["questionStem", "images", "correctAnswer", "feedback"],
    optionalFields: ["labels"],
    constraints: {
      hasImage: (q) =>
        !q.images || q.images.length === 0
          ? "TextEntryGraphic kräver minst en bild"
          : null,
    },
  },

  audio_record: {
    requiredMetadata: ["type", "points", "bloom", "difficulty"],
    requiredFields: ["questionStem"],
    optionalFields: ["labels", "rubric", "feedback"],
    constraints: {},
  },

  composite_editor: {
    requiredMetadata: ["type", "points"],
    requiredFields: ["questionStem"],
    optionalFields: ["labels", "feedback"],
    constraints: {},
  },

  nativehtml: {
    requiredMetadata: ["type"],
    requiredFields: ["questionStem"],
    optionalFields: ["labels"],
    constraints: {},
  },
};

/**
 * Check content completeness for all questions.
 */
export function checkCompleteness(questions: M3Question[]): CompletenessResult {
  const result: CompletenessResult = {
    status: "pass",
    totalQuestions: questions.length,
    passedQuestions: 0,
    issues: [],
    questionStatus: {},
  };

  for (const question of questions) {
    const questionIssues = checkQuestion(question);

    const qId = question.questionNumber;
    const hasErrors = questionIssues.some((i) => i.severity === "error");
    const hasWarnings = questionIssues.some((i) => i.severity === "warning");

    result.questionStatus[qId] = {
      status: hasErrors ? "errors" : hasWarnings ? "warnings" : "pass",
      issues: questionIssues,
    };

    result.issues.push(...questionIssues);

    if (!hasErrors) {
      result.passedQuestions++;
    }
  }

  // Set overall status
  const hasErrors = result.issues.some((i) => i.severity === "error");
  const hasWarnings = result.issues.some((i) => i.severity === "warning");
  result.status = hasErrors ? "errors" : hasWarnings ? "warnings" : "pass";

  return result;
}

/**
 * Check a single question for completeness.
 */
export function checkQuestion(question: M3Question): CompletenessIssue[] {
  const issues: CompletenessIssue[] = [];
  const qId = question.questionNumber;

  // Determine question type
  const typeString = question.metadata.type || "";
  const questionType = resolveQuestionType(typeString);

  if (!questionType) {
    issues.push({
      questionId: qId,
      severity: "error",
      field: "type",
      message: `Okänd frågetyp: "${typeString}"`,
      suggestion: "Ange en giltig frågetyp (t.ex. Multiple Choice, True/False)",
      autoFixable: false,
    });
    return issues; // Can't check further without knowing type
  }

  const requirements = TYPE_REQUIREMENTS[questionType];
  if (!requirements) {
    issues.push({
      questionId: qId,
      severity: "error",
      field: "type",
      message: `Frågetyp "${questionType}" har inga definierade krav`,
      autoFixable: false,
    });
    return issues;
  }

  // Check required metadata
  for (const field of requirements.requiredMetadata) {
    const value = getMetadataValue(question, field);
    if (!value) {
      issues.push({
        questionId: qId,
        severity: "error",
        field,
        message: `Saknar obligatorisk metadata: ${field}`,
        suggestion: getSuggestion(field),
        autoFixable: isAutoFixable(field),
      });
    }
  }

  // Check required fields
  for (const field of requirements.requiredFields) {
    const value = getFieldValue(question, field);
    if (!value || (Array.isArray(value) && value.length === 0)) {
      issues.push({
        questionId: qId,
        severity: "error",
        field,
        message: `Saknar obligatoriskt fält: ${field}`,
        suggestion: getSuggestion(field),
        autoFixable: isAutoFixable(field),
      });
    }
  }

  // Check feedback subfields for MC questions
  if (
    requirements.requiredFields.includes("feedback") &&
    question.feedback
  ) {
    if (!question.feedback.correct) {
      issues.push({
        questionId: qId,
        severity: "warning",
        field: "feedback.correct",
        message: "Saknar feedback för korrekt svar",
        suggestion: "Lägg till förklarande feedback för rätt svar",
        autoFixable: false,
      });
    }

    // Check if there's any incorrect feedback
    const hasIncorrectFeedback =
      question.feedback.incorrect &&
      Object.keys(question.feedback.incorrect).length > 0;

    if (!hasIncorrectFeedback && !question.feedback.general) {
      issues.push({
        questionId: qId,
        severity: "warning",
        field: "feedback.incorrect",
        message: "Saknar feedback för felaktiga svar",
        suggestion: "Lägg till förklarande feedback för fel svar",
        autoFixable: false,
      });
    }
  }

  // Run type-specific constraints
  for (const [constraintName, checkFn] of Object.entries(
    requirements.constraints
  )) {
    const error = checkFn(question);
    if (error) {
      issues.push({
        questionId: qId,
        severity: constraintName.includes("max") ? "warning" : "error",
        field: constraintName,
        message: error,
        autoFixable: false,
      });
    }
  }

  // Check labels for Bloom and Difficulty
  if (question.labels.length > 0) {
    const hasBloomLabel = question.labels.some((l) =>
      ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"].some(
        (b) => l.toLowerCase().includes(b.toLowerCase())
      )
    );

    const hasDifficultyLabel = question.labels.some((l) =>
      ["Easy", "Medium", "Hard"].some((d) =>
        l.toLowerCase().includes(d.toLowerCase())
      )
    );

    if (!hasBloomLabel && question.metadata.bloom) {
      issues.push({
        questionId: qId,
        severity: "info",
        field: "labels",
        message: `Bloom-nivå (${question.metadata.bloom}) saknas i labels`,
        suggestion: `Lägg till #${question.metadata.bloom} i labels`,
        autoFixable: true,
      });
    }

    if (!hasDifficultyLabel && question.metadata.difficulty) {
      issues.push({
        questionId: qId,
        severity: "info",
        field: "labels",
        message: `Svårighetsgrad (${question.metadata.difficulty}) saknas i labels`,
        suggestion: `Lägg till #${question.metadata.difficulty} i labels`,
        autoFixable: true,
      });
    }
  }

  return issues;
}

/**
 * Resolve M3 type string to QFMD QuestionType.
 */
export function resolveQuestionType(typeString: string): QuestionType | null {
  // Import the map from types
  const M3_TYPE_MAP: Record<string, QuestionType> = {
    // Multiple choice variants
    "Multiple Choice (MC-Single)": "multiple_choice_single",
    "Multiple Choice (Single Answer)": "multiple_choice_single",
    "MC-Single": "multiple_choice_single",
    "Flerval (ett svar)": "multiple_choice_single",
    "Multiple Choice": "multiple_choice_single",

    // Multiple response variants
    "Multiple Response (MR)": "multiple_response",
    "Multiple Response": "multiple_response",
    MR: "multiple_response",
    "Flerval (flera svar)": "multiple_response",

    // True/false
    "True/False": "true_false",
    "Sant/Falskt": "true_false",
    TF: "true_false",

    // Inline choice (dropdown)
    "Inline Choice": "inline_choice",
    Dropdown: "inline_choice",

    // Text entry
    "Text Entry": "text_entry",
    "Fill in the Blank": "text_entry",
    "Fyll i lucka": "text_entry",

    // Match
    Match: "match",
    Matchning: "match",

    // Essay
    Essay: "essay",
    "Essä": "essay",

    // Text area
    "Text Area": "text_area",
    "Extended Text": "text_area",
    Fritext: "text_area",
  };

  // Direct lookup
  if (M3_TYPE_MAP[typeString]) {
    return M3_TYPE_MAP[typeString];
  }

  // Case-insensitive lookup
  const normalized = typeString.toLowerCase().trim();
  for (const [key, value] of Object.entries(M3_TYPE_MAP)) {
    if (key.toLowerCase() === normalized) {
      return value;
    }
  }

  // Partial match
  if (normalized.includes("multiple choice") || normalized.includes("mc")) {
    if (normalized.includes("single") || !normalized.includes("response")) {
      return "multiple_choice_single";
    }
    return "multiple_response";
  }

  if (normalized.includes("true") || normalized.includes("false")) {
    return "true_false";
  }

  if (normalized.includes("essay") || normalized.includes("essä")) {
    return "essay";
  }

  return null;
}

/**
 * Get metadata value from question.
 */
function getMetadataValue(
  question: M3Question,
  field: string
): string | number | undefined {
  switch (field) {
    case "type":
      return question.metadata.type;
    case "points":
      return question.metadata.points;
    case "bloom":
      return question.metadata.bloom;
    case "difficulty":
      return question.metadata.difficulty;
    case "lo":
      return question.metadata.lo;
    default:
      return undefined;
  }
}

/**
 * Get field value from question.
 */
function getFieldValue(
  question: M3Question,
  field: string
): string | string[] | object | undefined {
  switch (field) {
    case "questionStem":
      return question.questionStem;
    case "options":
      return question.options;
    case "correctAnswer":
      return question.correctAnswer;
    case "feedback":
      return question.feedback.correct || question.feedback.general
        ? question.feedback
        : undefined;
    case "images":
      return question.images;
    case "labels":
      return question.labels;
    default:
      return undefined;
  }
}

/**
 * Get suggestion for missing field.
 */
function getSuggestion(field: string): string {
  const suggestions: Record<string, string> = {
    type: "Ange frågetyp (t.ex. Multiple Choice, True/False)",
    points: "Ange poäng (t.ex. 1)",
    bloom: "Ange Bloom-nivå (Remember, Understand, Apply, Analyze, Evaluate, Create)",
    difficulty: "Ange svårighetsgrad (Easy, Medium, Hard)",
    questionStem: "Skriv frågetexten",
    options: "Lägg till svarsalternativ (A. ... B. ... C. ...)",
    correctAnswer: "Ange rätt svar",
    feedback: "Lägg till feedback för rätt och fel svar",
    images: "Lägg till bildreferens",
  };

  return suggestions[field] || `Fyll i ${field}`;
}

/**
 * Check if field can be auto-fixed.
 */
function isAutoFixable(field: string): boolean {
  const autoFixable = ["points"]; // Default points to 1
  return autoFixable.includes(field);
}

/**
 * Format completeness result as report.
 */
export function formatCompletenessReport(result: CompletenessResult): string {
  const lines: string[] = [];

  // Header
  lines.push("# M5 Completeness Check Report");
  lines.push("");
  lines.push(`**Status:** ${result.status.toUpperCase()}`);
  lines.push(`**Questions checked:** ${result.totalQuestions}`);
  lines.push(`**Questions passed:** ${result.passedQuestions}`);
  lines.push(
    `**Questions with issues:** ${result.totalQuestions - result.passedQuestions}`
  );
  lines.push("");

  // Summary by severity
  const errors = result.issues.filter((i) => i.severity === "error");
  const warnings = result.issues.filter((i) => i.severity === "warning");
  const infos = result.issues.filter((i) => i.severity === "info");

  lines.push("## Issue Summary");
  lines.push("");
  lines.push(`- **Errors:** ${errors.length}`);
  lines.push(`- **Warnings:** ${warnings.length}`);
  lines.push(`- **Info:** ${infos.length}`);
  lines.push("");

  // Details by question
  if (result.issues.length > 0) {
    lines.push("## Issues by Question");
    lines.push("");

    for (const [qId, status] of Object.entries(result.questionStatus)) {
      if (status.issues.length === 0) continue;

      lines.push(`### ${qId}`);
      lines.push("");

      for (const issue of status.issues) {
        const icon =
          issue.severity === "error"
            ? "❌"
            : issue.severity === "warning"
              ? "⚠️"
              : "ℹ️";
        lines.push(`${icon} **${issue.field}:** ${issue.message}`);
        if (issue.suggestion) {
          lines.push(`   → ${issue.suggestion}`);
        }
      }
      lines.push("");
    }
  }

  return lines.join("\n");
}
