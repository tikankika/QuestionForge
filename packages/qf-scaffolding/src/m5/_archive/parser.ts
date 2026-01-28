/**
 * M5 Parser - Parse M3 Human-Readable Format
 *
 * Parses the human-readable question format from M3 output.
 *
 * M3 Format Example:
 * ```
 * ### Q1 - Definition av AI
 *
 * **Metadata:**
 * - LO: LO1
 * - Bloom: Remember
 * - Difficulty: Easy
 * - Type: Multiple Choice (MC-Single)
 * - Points: 1
 *
 * **Labels (Inspera):**
 * - ARTI1000X
 * - Test1
 *
 * **Question Stem:**
 * Vad är artificiell intelligens (AI)?
 *
 * **Answer Options:**
 * A) Ett samlingsbegrepp...
 * B) ...
 *
 * **Correct Answer:** A
 *
 * **Feedback:**
 * **Correct (A):** Rätt! ...
 * **Incorrect (B):** ...
 * ```
 */

import type { M3Question, BloomLevel, DifficultyLevel } from "./types.js";

/**
 * Parse M3 human-readable format into structured questions.
 */
export function parseM3Content(content: string): M3Question[] {
  const questions: M3Question[] = [];
  const lines = content.split("\n");

  // Find question boundaries (### Q1, ### Q2, etc.)
  const questionStarts: number[] = [];
  for (let i = 0; i < lines.length; i++) {
    if (/^###\s+Q\d+/.test(lines[i])) {
      questionStarts.push(i);
    }
  }

  // Parse each question
  for (let i = 0; i < questionStarts.length; i++) {
    const startLine = questionStarts[i];
    const endLine =
      i < questionStarts.length - 1 ? questionStarts[i + 1] : lines.length;

    const questionContent = lines.slice(startLine, endLine).join("\n");
    const parsed = parseQuestion(questionContent, startLine + 1);

    if (parsed) {
      questions.push(parsed);
    }
  }

  return questions;
}

/**
 * Parse a single question block.
 */
function parseQuestion(content: string, lineNumber: number): M3Question | null {
  const lines = content.split("\n");

  // Extract question header: ### Q1 - Title
  const headerMatch = lines[0].match(/^###\s+(Q\d+)\s*-?\s*(.*)$/);
  if (!headerMatch) {
    return null;
  }

  const questionNumber = headerMatch[1];
  const title = headerMatch[2].trim();

  // Initialize question object
  const question: M3Question = {
    questionNumber,
    title,
    metadata: {},
    labels: [],
    questionStem: "",
    options: [],
    correctAnswer: "",
    feedback: {},
    rawContent: content,
    lineNumber,
  };

  // Parse sections
  let currentSection = "";
  let sectionContent: string[] = [];

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];

    // Detect section headers
    if (line.startsWith("**Metadata:**")) {
      saveSection(question, currentSection, sectionContent);
      currentSection = "metadata";
      sectionContent = [];
    } else if (
      line.startsWith("**Labels") ||
      line.startsWith("**Etiketter")
    ) {
      saveSection(question, currentSection, sectionContent);
      currentSection = "labels";
      sectionContent = [];
    } else if (
      line.startsWith("**Question Stem:**") ||
      line.startsWith("**Frågetext:**")
    ) {
      saveSection(question, currentSection, sectionContent);
      currentSection = "stem";
      sectionContent = [];
    } else if (
      line.startsWith("**Answer Options:**") ||
      line.startsWith("**Svarsalternativ:**")
    ) {
      saveSection(question, currentSection, sectionContent);
      currentSection = "options";
      sectionContent = [];
    } else if (
      line.startsWith("**Correct Answer:**") ||
      line.startsWith("**Rätt svar:**")
    ) {
      saveSection(question, currentSection, sectionContent);
      currentSection = "answer";
      // Extract inline answer
      const answerMatch = line.match(/\*\*(?:Correct Answer|Rätt svar):\*\*\s*(.+)/);
      if (answerMatch) {
        question.correctAnswer = answerMatch[1].trim();
      }
      sectionContent = [];
    } else if (line.startsWith("**Feedback:**")) {
      saveSection(question, currentSection, sectionContent);
      currentSection = "feedback";
      sectionContent = [];
    } else if (
      line.startsWith("**Source Explanation:**") ||
      line.startsWith("**Källförklaring:**")
    ) {
      saveSection(question, currentSection, sectionContent);
      currentSection = "source";
      sectionContent = [];
    } else if (line.startsWith("**Image:**") || line.startsWith("**Bild:**")) {
      // Extract image reference
      const imageMatch = line.match(/\*\*(?:Image|Bild):\*\*\s*(.+)/);
      if (imageMatch) {
        if (!question.images) question.images = [];
        question.images.push(imageMatch[1].trim());
      }
    } else {
      // Add to current section
      sectionContent.push(line);
    }
  }

  // Save final section
  saveSection(question, currentSection, sectionContent);

  return question;
}

/**
 * Save parsed section content to question object.
 */
function saveSection(
  question: M3Question,
  section: string,
  content: string[]
): void {
  const text = content.join("\n").trim();

  switch (section) {
    case "metadata":
      parseMetadata(question, text);
      break;
    case "labels":
      parseLabels(question, text);
      break;
    case "stem":
      question.questionStem = text;
      break;
    case "options":
      question.options = parseOptions(text);
      break;
    case "feedback":
      parseFeedback(question, text);
      break;
    case "source":
      question.sourceExplanation = text;
      break;
  }
}

/**
 * Parse metadata section.
 */
function parseMetadata(question: M3Question, text: string): void {
  const lines = text.split("\n");

  for (const line of lines) {
    // Match "- Key: Value" or "- Key Value"
    const match = line.match(/^-\s*(\w+):?\s*(.+)$/);
    if (match) {
      const key = match[1].toLowerCase();
      const value = match[2].trim();

      switch (key) {
        case "lo":
        case "learningobjective":
          question.metadata.lo = value;
          break;
        case "bloom":
          question.metadata.bloom = parseBloomLevel(value);
          break;
        case "difficulty":
        case "svårighetsgrad":
          question.metadata.difficulty = parseDifficultyLevel(value);
          break;
        case "type":
        case "typ":
          question.metadata.type = value;
          break;
        case "points":
        case "poäng":
          question.metadata.points = parseInt(value, 10) || 1;
          break;
      }
    }
  }
}

/**
 * Parse labels section.
 */
function parseLabels(question: M3Question, text: string): void {
  const lines = text.split("\n");

  for (const line of lines) {
    // Match "- Label" format
    const match = line.match(/^-\s*(.+)$/);
    if (match) {
      const label = match[1].trim();
      if (label) {
        question.labels.push(label);
      }
    }
  }
}

/**
 * Parse answer options.
 */
function parseOptions(text: string): string[] {
  const options: string[] = [];
  const lines = text.split("\n");

  for (const line of lines) {
    // Match "A) ..." or "A. ..." or "1) ..." or "1. ..."
    const match = line.match(/^([A-F]|[1-6])[.)]\s*(.+)$/i);
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
 * Parse feedback section.
 */
function parseFeedback(question: M3Question, text: string): void {
  const lines = text.split("\n");
  let currentFeedbackType = "";
  let currentContent: string[] = [];

  for (const line of lines) {
    // Check for feedback type headers
    const correctMatch = line.match(
      /^\*\*(?:Correct|Rätt)\s*\(([A-F])\):\*\*\s*(.*)/i
    );
    const incorrectMatch = line.match(
      /^\*\*(?:Incorrect|Fel)\s*\(([A-F])\):\*\*\s*(.*)/i
    );
    const generalMatch = line.match(
      /^\*\*(?:General|Generell):\*\*\s*(.*)/i
    );

    if (correctMatch) {
      saveFeedback(question, currentFeedbackType, currentContent);
      currentFeedbackType = "correct";
      currentContent = [correctMatch[2]];
    } else if (incorrectMatch) {
      saveFeedback(question, currentFeedbackType, currentContent);
      const option = incorrectMatch[1].toUpperCase();
      currentFeedbackType = `incorrect_${option}`;
      currentContent = [incorrectMatch[2]];
    } else if (generalMatch) {
      saveFeedback(question, currentFeedbackType, currentContent);
      currentFeedbackType = "general";
      currentContent = [generalMatch[1]];
    } else if (line.trim()) {
      currentContent.push(line);
    }
  }

  // Save final feedback
  saveFeedback(question, currentFeedbackType, currentContent);
}

/**
 * Save feedback content.
 */
function saveFeedback(
  question: M3Question,
  type: string,
  content: string[]
): void {
  const text = content.join("\n").trim();
  if (!text || !type) return;

  if (type === "correct") {
    question.feedback.correct = text;
  } else if (type === "general") {
    question.feedback.general = text;
  } else if (type.startsWith("incorrect_")) {
    const option = type.replace("incorrect_", "");
    if (!question.feedback.incorrect) {
      question.feedback.incorrect = {};
    }
    question.feedback.incorrect[option] = text;
  }
}

/**
 * Parse Bloom's taxonomy level.
 */
function parseBloomLevel(value: string): BloomLevel | undefined {
  const normalized = value.toLowerCase().trim();

  const bloomMap: Record<string, BloomLevel> = {
    remember: "Remember",
    minnas: "Remember",
    understand: "Understand",
    förstå: "Understand",
    apply: "Apply",
    tillämpa: "Apply",
    analyze: "Analyze",
    analysera: "Analyze",
    evaluate: "Evaluate",
    utvärdera: "Evaluate",
    create: "Create",
    skapa: "Create",
  };

  return bloomMap[normalized];
}

/**
 * Parse difficulty level.
 */
function parseDifficultyLevel(value: string): DifficultyLevel | undefined {
  const normalized = value.toLowerCase().trim();

  const difficultyMap: Record<string, DifficultyLevel> = {
    easy: "Easy",
    enkel: "Easy",
    lätt: "Easy",
    medium: "Medium",
    medel: "Medium",
    hard: "Hard",
    svår: "Hard",
  };

  return difficultyMap[normalized];
}

/**
 * Get question count summary from parsed questions.
 */
export function getQuestionSummary(questions: M3Question[]): {
  total: number;
  byType: Record<string, number>;
  byBloom: Record<string, number>;
  byDifficulty: Record<string, number>;
} {
  const summary = {
    total: questions.length,
    byType: {} as Record<string, number>,
    byBloom: {} as Record<string, number>,
    byDifficulty: {} as Record<string, number>,
  };

  for (const q of questions) {
    // Count by type
    const type = q.metadata.type || "unknown";
    summary.byType[type] = (summary.byType[type] || 0) + 1;

    // Count by Bloom level
    const bloom = q.metadata.bloom || "unknown";
    summary.byBloom[bloom] = (summary.byBloom[bloom] || 0) + 1;

    // Count by difficulty
    const difficulty = q.metadata.difficulty || "unknown";
    summary.byDifficulty[difficulty] =
      (summary.byDifficulty[difficulty] || 0) + 1;
  }

  return summary;
}
