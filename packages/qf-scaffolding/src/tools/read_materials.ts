/**
 * read_materials tool for qf-scaffolding MCP
 *
 * Reads instructional materials from the project's 00_materials/ folder.
 * Supports PDF text extraction, markdown, and text files.
 *
 * RFC-004: Phase 1 - Core Read Tools
 */

import { z } from "zod";
import { readFile, readdir, stat } from "fs/promises";
import { join, extname } from "path";
import { PDFParse } from "pdf-parse";
import { logEvent, logError } from "../utils/logger.js";

// Input schema for read_materials tool
export const readMaterialsSchema = z.object({
  project_path: z.string(),
  file_pattern: z.string().optional(), // e.g., "*.pdf", "lecture*"
  extract_text: z.boolean().optional().default(true), // Extract text from PDFs
});

export type ReadMaterialsInput = z.infer<typeof readMaterialsSchema>;

// Material info type
export interface MaterialInfo {
  filename: string;
  path: string;
  content_type: "pdf" | "md" | "txt" | "pptx" | "other";
  size_bytes: number;
  text_content?: string;
  error?: string;
}

// Result type for read_materials
export interface ReadMaterialsResult {
  success: boolean;
  materials: MaterialInfo[];
  total_files: number;
  total_chars?: number;
  error?: string;
}

/**
 * Determine content type from file extension
 */
function getContentType(filename: string): MaterialInfo["content_type"] {
  const ext = extname(filename).toLowerCase();
  switch (ext) {
    case ".pdf":
      return "pdf";
    case ".md":
    case ".markdown":
      return "md";
    case ".txt":
      return "txt";
    case ".pptx":
      return "pptx";
    default:
      return "other";
  }
}

/**
 * Check if filename matches pattern
 * Supports simple glob patterns: *.pdf, lecture*, *analysis*
 */
function matchesPattern(filename: string, pattern?: string): boolean {
  if (!pattern) return true;

  // Convert glob pattern to regex
  const regexPattern = pattern
    .replace(/\./g, "\\.") // Escape dots
    .replace(/\*/g, ".*"); // * becomes .*

  const regex = new RegExp(`^${regexPattern}$`, "i");
  return regex.test(filename);
}

/**
 * Extract text from PDF file using pdf-parse library
 */
async function extractPdfText(filePath: string): Promise<string> {
  const buffer = await readFile(filePath);
  const pdfParser = new PDFParse({ data: buffer });
  const textResult = await pdfParser.getText();
  await pdfParser.destroy();
  return textResult.text;
}

/**
 * Read a single material file
 */
async function readMaterial(
  filePath: string,
  filename: string,
  extractText: boolean
): Promise<MaterialInfo> {
  const contentType = getContentType(filename);
  const stats = await stat(filePath);

  const material: MaterialInfo = {
    filename,
    path: filePath,
    content_type: contentType,
    size_bytes: stats.size,
  };

  if (extractText) {
    try {
      switch (contentType) {
        case "pdf":
          material.text_content = await extractPdfText(filePath);
          break;
        case "md":
        case "txt":
          material.text_content = await readFile(filePath, "utf-8");
          break;
        case "pptx":
          material.error = "PPTX extraction not yet implemented";
          break;
        default:
          material.error = `Cannot extract text from ${contentType} files`;
      }
    } catch (error) {
      material.error =
        error instanceof Error ? error.message : "Unknown extraction error";
    }
  }

  return material;
}

/**
 * Read instructional materials from project's 00_materials/ folder
 */
export async function readMaterials(
  input: ReadMaterialsInput
): Promise<ReadMaterialsResult> {
  const { project_path, file_pattern, extract_text = true } = input;
  const startTime = Date.now();

  // Log tool_start (TIER 1)
  logEvent(project_path, "", "read_materials", "tool_start", "info", {
    file_pattern,
    extract_text,
  });

  const materialsPath = join(project_path, "00_materials");

  try {
    // Check if materials folder exists
    try {
      await stat(materialsPath);
    } catch {
      const error = `Materials folder not found: ${materialsPath}`;
      logEvent(
        project_path,
        "",
        "read_materials",
        "tool_end",
        "warn",
        { success: false, error },
        Date.now() - startTime
      );
      return { success: false, materials: [], total_files: 0, error };
    }

    // Read directory contents
    const files = await readdir(materialsPath);

    // Filter by pattern
    const matchedFiles = files.filter((f) => matchesPattern(f, file_pattern));

    if (matchedFiles.length === 0) {
      const message = file_pattern
        ? `No files matching pattern '${file_pattern}' in 00_materials/`
        : `No files found in 00_materials/`;
      logEvent(
        project_path,
        "",
        "read_materials",
        "tool_end",
        "info",
        { success: true, total_files: 0, message },
        Date.now() - startTime
      );
      return { success: true, materials: [], total_files: 0 };
    }

    // Read each material
    const materials: MaterialInfo[] = [];
    let totalChars = 0;

    for (const filename of matchedFiles) {
      const filePath = join(materialsPath, filename);

      // Skip directories
      const fileStats = await stat(filePath);
      if (fileStats.isDirectory()) continue;

      const material = await readMaterial(filePath, filename, extract_text);
      materials.push(material);

      if (material.text_content) {
        totalChars += material.text_content.length;
      }
    }

    // Log tool_end with success (TIER 1)
    logEvent(
      project_path,
      "",
      "read_materials",
      "tool_end",
      "info",
      {
        success: true,
        total_files: materials.length,
        total_chars: totalChars,
        content_types: materials.reduce(
          (acc, m) => {
            acc[m.content_type] = (acc[m.content_type] || 0) + 1;
            return acc;
          },
          {} as Record<string, number>
        ),
      },
      Date.now() - startTime
    );

    return {
      success: true,
      materials,
      total_files: materials.length,
      total_chars: totalChars,
    };
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    const errorStack = error instanceof Error ? error.stack : undefined;

    // Log tool_error (TIER 1)
    logError(
      project_path,
      "read_materials",
      error instanceof Error ? error.constructor.name : "UnknownError",
      errorMessage,
      { stack: errorStack }
    );

    return {
      success: false,
      materials: [],
      total_files: 0,
      error: `Failed to read materials: ${errorMessage}`,
    };
  }
}
