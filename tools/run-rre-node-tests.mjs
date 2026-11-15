// Run every test module under tools/ that imports Node's built-in test runner.
// This prevents a curated short list from silently omitting new offline tests.
// Usage: node tools/run-rre-node-tests.mjs [--list]
import { spawnSync } from "node:child_process";
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const toolsDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(toolsDir, "..");
const importsNodeTest = /\bfrom\s*["']node:test["']|^\s*import\s*["']node:test["']|\brequire\(["']node:test["']\)/m;
const excludedDirs = new Set([
  ".git", ".local", ".venv", "venv", "node_modules", "dist", "build", "bin",
  "obj", "coverage", "__pycache__", "artifacts", "scratch", "generated"
]);
const MAX_DEPTH = 6;
const MAX_ENTRIES = 10000;
let entriesVisited = 0;
function discoverTests(directory, relativeParts = [], depth = 0) {
  if (depth > MAX_DEPTH) throw new Error("Node test discovery exceeded directory depth limit");
  const result = [];
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    entriesVisited++;
    if (entriesVisited > MAX_ENTRIES) throw new Error("Node test discovery exceeded entry limit");
    if (entry.isSymbolicLink()) continue;
    if (entry.isDirectory()) {
      if (!excludedDirs.has(entry.name)) {
        result.push(...discoverTests(path.join(directory, entry.name),
          [...relativeParts, entry.name], depth + 1));
      }
    } else if (entry.isFile() && entry.name.endsWith(".mjs")) {
      const absolute = path.join(directory, entry.name);
      if (importsNodeTest.test(readFileSync(absolute, "utf8"))) {
        result.push(path.join("tools", ...relativeParts, entry.name));
      }
    }
  }
  return result;
}
const testFiles = discoverTests(toolsDir).sort();

const options = process.argv.slice(2);
if (options.length > 1 || (options.length === 1 && options[0] !== "--list")) {
  console.error("Usage: node tools/run-rre-node-tests.mjs [--list]");
  process.exitCode = 2;
} else if (testFiles.length === 0) {
  console.error("No Node test modules discovered under tools/; refusing an empty green gate.");
  process.exitCode = 2;
} else if (options[0] === "--list") {
  console.log(JSON.stringify({ moduleCount: testFiles.length, testFiles }, null, 2));
} else {
  console.log(`RRE offline Node gate: ${testFiles.length} discovered modules`);
  const result = spawnSync(process.execPath, ["--test", ...testFiles], {
    cwd: repoRoot, stdio: "inherit", windowsHide: true
  });
  if (result.error || result.status === null) {
    console.error(`Node test runner failed: ${result.error?.message ?? result.signal ?? "unknown"}`);
    process.exitCode = 1;
  } else {
    process.exitCode = result.status;
  }
}
