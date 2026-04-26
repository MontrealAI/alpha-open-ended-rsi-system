import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { join, relative } from "node:path";

export function timestampTag(date = new Date()): string {
  return date.toISOString().replace(/[:.]/g, "-");
}

export function ensureDir(path: string): void {
  mkdirSync(path, { recursive: true });
}

export function writeJson(path: string, value: unknown): void {
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

export function writeText(path: string, value: string): void {
  writeFileSync(path, value, "utf8");
}

function collectFiles(rootDir: string): string[] {
  const entries = readdirSync(rootDir);
  const files: string[] = [];
  for (const entry of entries) {
    const full = join(rootDir, entry);
    const st = statSync(full);
    if (st.isDirectory()) {
      files.push(...collectFiles(full));
    } else {
      files.push(full);
    }
  }
  return files;
}

export function generateChecksums(rootDir: string): string {
  const files = collectFiles(rootDir).sort();
  return files
    .map((filePath) => {
      const content = readFileSync(filePath);
      const hash = createHash("sha256").update(content).digest("hex");
      const relativePath = relative(rootDir, filePath);
      return `${hash}  ${relativePath}`;
    })
    .join("\n");
}
