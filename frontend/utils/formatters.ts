import { GeneratedFiles } from "@/types";

/**
 * Format a Date object into a short time string (e.g. "11:42 PM").
 */
export function formatTime(date: Date): string {
  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Format generated files dictionary into a readable markdown string with code fences.
 */
export function formatGeneratedFiles(files?: GeneratedFiles): string {
  if (!files || Object.keys(files).length === 0) {
    return "";
  }

  let formatted = "\n\n**Generated files:**\n";
  for (const [filename, fileContent] of Object.entries(files)) {
    formatted += `\n📄 ${filename}\n\`\`\`\n${fileContent}\n\`\`\`\n`;
  }
  return formatted;
}
