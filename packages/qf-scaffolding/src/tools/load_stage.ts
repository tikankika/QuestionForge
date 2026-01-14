/**
 * load_stage tool for qf-scaffolding MCP
 *
 * Loads methodology documents one stage at a time from M1 (Material Analysis).
 * MVP: Only M1 is implemented.
 */

import { z } from "zod";
import { readFile } from "fs/promises";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Input schema for load_stage tool
export const loadStageSchema = z.object({
  module: z.enum(["m1"]), // MVP: Only M1 available
  stage: z.number().min(0).max(7), // bb1a (0) through bb1h (7)
});

export type LoadStageInput = z.infer<typeof loadStageSchema>;

// Stage information with file mapping and descriptions
interface StageInfo {
  filename: string;
  name: string;
  description: string;
  estimatedTime: string;
}

const M1_STAGES: Record<number, StageInfo> = {
  0: {
    filename: "m1_0_intro.md",
    name: "Introduction",
    description: "Framework overview and principles for Material Analysis",
    estimatedTime: "15 min read",
  },
  1: {
    filename: "m1_1_stage0_material_analysis.md",
    name: "Stage 0: Material Analysis",
    description: "AI analyzes instructional materials (AI solo phase)",
    estimatedTime: "60-90 min",
  },
  2: {
    filename: "m1_2_stage1_validation.md",
    name: "Stage 1: Initial Validation",
    description: "Teacher validates AI's material analysis",
    estimatedTime: "20-30 min",
  },
  3: {
    filename: "m1_3_stage2_emphasis.md",
    name: "Stage 2: Emphasis Refinement",
    description: "Deep dive into teaching priorities and emphasis",
    estimatedTime: "30-45 min",
  },
  4: {
    filename: "m1_4_stage3_examples.md",
    name: "Stage 3: Example Catalog",
    description: "Document effective examples from teaching",
    estimatedTime: "20-30 min",
  },
  5: {
    filename: "m1_5_stage4_misconceptions.md",
    name: "Stage 4: Misconception Analysis",
    description: "Identify and document common student misconceptions",
    estimatedTime: "20-30 min",
  },
  6: {
    filename: "m1_6_stage5_objectives.md",
    name: "Stage 5: Scope & Objectives",
    description: "Finalize learning objectives from analysis",
    estimatedTime: "45-60 min",
  },
  7: {
    filename: "m1_7_best_practices.md",
    name: "Best Practices",
    description: "Facilitation principles and guidelines",
    estimatedTime: "15 min read",
  },
};

// Result type for load_stage
export interface LoadStageResult {
  success: boolean;
  content?: string;
  stage?: {
    module: string;
    index: number;
    name: string;
    description: string;
    estimatedTime: string;
  };
  progress?: {
    currentStage: number;
    totalStages: number;
    remaining: string[];
  };
  nextAction?: string;
  error?: string;
}

/**
 * Load a specific methodology stage
 */
export async function loadStage(input: LoadStageInput): Promise<LoadStageResult> {
  const { module, stage } = input;

  // MVP: Only M1 supported
  if (module !== "m1") {
    return {
      success: false,
      error: `Module '${module}' is not available in MVP. Only 'm1' is supported.`,
    };
  }

  // Get stage info
  const stageInfo = M1_STAGES[stage];
  if (!stageInfo) {
    return {
      success: false,
      error: `Invalid stage ${stage} for module ${module}. Valid stages: 0-7`,
    };
  }

  try {
    // Build path to methodology file
    // From build/tools/ -> up to package root -> up to QuestionForge root -> methodology/m1/
    const methodologyPath = join(
      __dirname,
      "..",
      "..",
      "..",
      "..",
      "methodology",
      module,
      stageInfo.filename
    );

    // Read the file
    const content = await readFile(methodologyPath, "utf-8");

    // Calculate remaining stages
    const remainingStages: string[] = [];
    for (let i = stage + 1; i <= 7; i++) {
      remainingStages.push(M1_STAGES[i].name);
    }

    // Determine next action
    let nextAction: string;
    if (stage === 0) {
      nextAction = "Läs igenom introduktionen. Säg 'fortsätt' när du är redo för Stage 0.";
    } else if (stage === 7) {
      nextAction = "M1 komplett! Du kan nu fortsätta till M2 (Assessment Design) eller börja skriva frågor.";
    } else {
      nextAction = `Följ instruktionerna ovan. När ni är klara, säg 'fortsätt' för ${M1_STAGES[stage + 1]?.name || 'nästa steg'}.`;
    }

    return {
      success: true,
      content,
      stage: {
        module,
        index: stage,
        name: stageInfo.name,
        description: stageInfo.description,
        estimatedTime: stageInfo.estimatedTime,
      },
      progress: {
        currentStage: stage,
        totalStages: 8,
        remaining: remainingStages,
      },
      nextAction,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    return {
      success: false,
      error: `Failed to load stage: ${errorMessage}`,
    };
  }
}

/**
 * Get stage info without loading content
 */
export function getStageInfo(module: string, stage: number): StageInfo | undefined {
  if (module === "m1") {
    return M1_STAGES[stage];
  }
  return undefined;
}

/**
 * Get all stages for a module
 */
export function getAllStages(module: string): StageInfo[] {
  if (module === "m1") {
    return Object.values(M1_STAGES);
  }
  return [];
}
