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
  module: z.enum(["m1", "m2", "m3", "m4"]),
  stage: z.number().min(0).max(8), // Max 8 for M2
});

export type LoadStageInput = z.infer<typeof loadStageSchema>;

// Stage information with file mapping and descriptions
interface StageInfo {
  filename: string;
  name: string;
  description: string;
  estimatedTime: string;
  requiresApproval: boolean | "conditional"; // Stage gate control
}

// Maximum stage index for each module
const MAX_STAGES: Record<string, number> = {
  m1: 7,  // 0-7 (8 files)
  m2: 8,  // 0-8 (9 files)
  m3: 4,  // 0-4 (5 files)
  m4: 5,  // 0-5 (6 files)
};

// Module display names
const MODULE_NAMES: Record<string, string> = {
  m1: "M1 (Material Analysis)",
  m2: "M2 (Assessment Design)",
  m3: "M3 (Question Generation)",
  m4: "M4 (Quality Assurance)",
};

const M1_STAGES: Record<number, StageInfo> = {
  0: {
    filename: "m1_0_intro.md",
    name: "Introduction",
    description: "Framework overview and principles for Material Analysis",
    estimatedTime: "15 min read",
    requiresApproval: false,
  },
  1: {
    filename: "m1_1_stage0_material_analysis.md",
    name: "Stage 0: Material Analysis",
    description: "AI analyzes instructional materials (AI solo phase)",
    estimatedTime: "60-90 min",
    requiresApproval: false, // AI solo work
  },
  2: {
    filename: "m1_2_stage1_validation.md",
    name: "Stage 1: Initial Validation",
    description: "Teacher validates AI's material analysis",
    estimatedTime: "20-30 min",
    requiresApproval: true,
  },
  3: {
    filename: "m1_3_stage2_emphasis.md",
    name: "Stage 2: Emphasis Refinement",
    description: "Deep dive into teaching priorities and emphasis",
    estimatedTime: "30-45 min",
    requiresApproval: true,
  },
  4: {
    filename: "m1_4_stage3_examples.md",
    name: "Stage 3: Example Catalog",
    description: "Document effective examples from teaching",
    estimatedTime: "20-30 min",
    requiresApproval: true,
  },
  5: {
    filename: "m1_5_stage4_misconceptions.md",
    name: "Stage 4: Misconception Analysis",
    description: "Identify and document common student misconceptions",
    estimatedTime: "20-30 min",
    requiresApproval: true,
  },
  6: {
    filename: "m1_6_stage5_objectives.md",
    name: "Stage 5: Scope & Objectives",
    description: "Finalize learning objectives from analysis",
    estimatedTime: "45-60 min",
    requiresApproval: true,
  },
  7: {
    filename: "m1_7_best_practices.md",
    name: "Best Practices",
    description: "Facilitation principles and guidelines",
    estimatedTime: "15 min read",
    requiresApproval: false, // Reference material
  },
};

// M2 (Assessment Design) stage information
const M2_STAGES: Record<number, StageInfo> = {
  0: {
    filename: "m2_0_intro.md",
    name: "Introduction",
    description: "Theoretical foundations for assessment design",
    estimatedTime: "15-20 min",
    requiresApproval: false,
  },
  1: {
    filename: "m2_1_objective_validation.md",
    name: "Stage 1: Objective Validation",
    description: "Validates learning objectives for assessment",
    estimatedTime: "15-20 min",
    requiresApproval: true,
  },
  2: {
    filename: "m2_2_strategy_definition.md",
    name: "Stage 2: Strategy Definition",
    description: "Establishes assessment purpose and constraints",
    estimatedTime: "10-15 min",
    requiresApproval: true,
  },
  3: {
    filename: "m2_3_question_target.md",
    name: "Stage 3: Question Target",
    description: "Determines total number of questions",
    estimatedTime: "10-15 min",
    requiresApproval: true,
  },
  4: {
    filename: "m2_4_blooms_distribution.md",
    name: "Stage 4: Bloom's Distribution",
    description: "Allocates questions across cognitive levels",
    estimatedTime: "15-20 min",
    requiresApproval: true,
  },
  5: {
    filename: "m2_5_question_type_mix.md",
    name: "Stage 5: Question Type Mix",
    description: "Selects question format types",
    estimatedTime: "20-25 min",
    requiresApproval: true,
  },
  6: {
    filename: "m2_6_difficulty_distribution.md",
    name: "Stage 6: Difficulty Distribution",
    description: "Distributes questions by difficulty levels",
    estimatedTime: "15-20 min",
    requiresApproval: true,
  },
  7: {
    filename: "m2_7_blueprint_construction.md",
    name: "Stage 7: Blueprint Construction",
    description: "Synthesizes all decisions into complete blueprint",
    estimatedTime: "20-30 min",
    requiresApproval: true,
  },
  8: {
    filename: "m2_8_best_practices.md",
    name: "Best Practices",
    description: "Facilitation guidance and common pitfalls",
    estimatedTime: "15 min",
    requiresApproval: false,
  },
};

// M3 (Question Generation) stage information
const M3_STAGES: Record<number, StageInfo> = {
  0: {
    filename: "m3_0_intro.md",
    name: "Introduction",
    description: "Teacher-led three-stage generation process",
    estimatedTime: "15-20 min",
    requiresApproval: false,
  },
  1: {
    filename: "m3_1_basic_generation.md",
    name: "Stage 4A: Basic Generation",
    description: "Creative content generation through dialogue",
    estimatedTime: "2-3 hours",
    requiresApproval: true,
  },
  2: {
    filename: "m3_2_distribution_review.md",
    name: "Stage 4B: Distribution Review",
    description: "Systematic analysis against blueprint",
    estimatedTime: "1-1.5 hours",
    requiresApproval: true,
  },
  3: {
    filename: "m3_3_finalization.md",
    name: "Stage 4C: Finalization",
    description: "Technical formatting and quality approval",
    estimatedTime: "1.5-2 hours",
    requiresApproval: true,
  },
  4: {
    filename: "m3_4_process_guidelines.md",
    name: "Process Guidelines",
    description: "Detailed facilitation guidance",
    estimatedTime: "20 min",
    requiresApproval: false,
  },
};

// M4 (Quality Assurance) phase information
const M4_STAGES: Record<number, StageInfo> = {
  0: {
    filename: "m4_0_intro.md",
    name: "Introduction",
    description: "Quality assurance framework and validation dimensions",
    estimatedTime: "15-20 min",
    requiresApproval: false,
  },
  1: {
    filename: "m4_1_automated_validation.md",
    name: "Phase 1: Automated Validation",
    description: "Technical compliance checks (automated)",
    estimatedTime: "~5 min",
    requiresApproval: "conditional", // Auto-proceed if pass, stop if errors
  },
  2: {
    filename: "m4_2_pedagogical_review.md",
    name: "Phase 2: Pedagogical Review",
    description: "Expert judgment on pedagogical quality",
    estimatedTime: "1-2 min per question",
    requiresApproval: true,
  },
  3: {
    filename: "m4_3_collective_analysis.md",
    name: "Phase 3: Collective Analysis",
    description: "Evaluates complete question set as coherent instrument",
    estimatedTime: "15-20 min",
    requiresApproval: true,
  },
  4: {
    filename: "m4_4_documentation.md",
    name: "Phase 4: Documentation",
    description: "Quality reports and final approval",
    estimatedTime: "10-15 min",
    requiresApproval: true,
  },
  5: {
    filename: "m4_5_output_transition.md",
    name: "Output Transition",
    description: "Handoff to Pipeline for export",
    estimatedTime: "10 min",
    requiresApproval: false,
  },
};

/**
 * Get stage mapping for a module
 */
function getStages(module: string): Record<number, StageInfo> {
  switch (module) {
    case "m1":
      return M1_STAGES;
    case "m2":
      return M2_STAGES;
    case "m3":
      return M3_STAGES;
    case "m4":
      return M4_STAGES;
    default:
      throw new Error(`Unknown module: ${module}`);
  }
}

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
    requiresApproval?: boolean | "conditional";
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

  // Validate module exists
  const maxStage = MAX_STAGES[module];
  if (maxStage === undefined) {
    return {
      success: false,
      error: `Unknown module '${module}'. Available modules: m1, m2, m3, m4`,
    };
  }

  // Validate stage is within range
  if (stage < 0 || stage > maxStage) {
    return {
      success: false,
      error: `Invalid stage ${stage} for module ${module}. Valid stages: 0-${maxStage}`,
    };
  }

  // Get stage info using dynamic lookup
  const stages = getStages(module);
  const stageInfo = stages[stage];

  if (!stageInfo) {
    return {
      success: false,
      error: `Stage ${stage} not found in module ${module}`,
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

    // Calculate remaining stages dynamically
    const remainingStages: string[] = [];
    const maxStageForModule = MAX_STAGES[module];
    for (let i = stage + 1; i <= maxStageForModule; i++) {
      const nextStageInfo = stages[i];
      if (nextStageInfo) {
        remainingStages.push(nextStageInfo.name);
      }
    }

    // Determine next action based on module and stage
    let nextAction: string;

    if (stage === 0) {
      // Introduction stage
      const nextStage = stages[1];
      nextAction = `Läs igenom introduktionen. Säg 'fortsätt' när du är redo för ${nextStage?.name || 'nästa steg'}.`;
    } else if (stage === maxStageForModule) {
      // Last stage - provide module completion message
      const nextModuleMap: Record<string, string> = {
        m1: "M1 komplett! Du kan nu fortsätta till M2 (Assessment Design).",
        m2: "M2 komplett! Du kan nu fortsätta till M3 (Question Generation).",
        m3: "M3 komplett! Du kan nu fortsätta till M4 (Quality Assurance).",
        m4: "M4 komplett! Frågor är klara för export till Inspera.",
      };
      nextAction = nextModuleMap[module] || "Modul komplett!";
    } else {
      // Middle stages
      const nextStage = stages[stage + 1];
      const requiresApproval = stageInfo.requiresApproval;

      if (requiresApproval === true) {
        nextAction = `Följ instruktionerna ovan. När ni är klara och har godkänt, säg 'fortsätt' för ${nextStage?.name || 'nästa steg'}.`;
      } else if (requiresApproval === "conditional") {
        nextAction = `Automatisk validering körs. Om inga fel hittas fortsätter processen automatiskt till ${nextStage?.name || 'nästa steg'}.`;
      } else {
        nextAction = `Läs igenom materialet. Säg 'fortsätt' för ${nextStage?.name || 'nästa steg'}.`;
      }
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
        requiresApproval: stageInfo.requiresApproval,
      },
      progress: {
        currentStage: stage,
        totalStages: MAX_STAGES[module] + 1, // +1 because stages are 0-indexed
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
  try {
    const stages = getStages(module);
    return stages[stage];
  } catch {
    return undefined;
  }
}

/**
 * Get all stages for a module
 */
export function getAllStages(module: string): StageInfo[] {
  try {
    const stages = getStages(module);
    return Object.values(stages);
  } catch {
    return [];
  }
}

/**
 * Get module display name
 */
export function getModuleName(module: string): string {
  return MODULE_NAMES[module] || module.toUpperCase();
}

/**
 * Get max stage for a module
 */
export function getMaxStage(module: string): number | undefined {
  return MAX_STAGES[module];
}
