// Run every top-level tools/*.mjs module that imports Node's built-in test runner.
// This prevents a curated short list from silently omitting new offline tests.
// Usage: node tools/run-rre-node-tests.mjs [--list]
import { spawnSync } from "node:child_process";
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const toolsDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(toolsDir, "..");
const importsNodeTest = /\bfrom\s*["']node:test["']|^\s*import\s*["']node:test["']|\brequire\(["']node:test["']\)/m;
const testFiles = readdirSync(toolsDir, { withFileTypes: true })
  .filter(entry => entry.isFile() && entry.name.endsWith(".mjs"))
  .filter(entry => importsNodeTest.test(readFileSync(path.join(toolsDir, entry.name), "utf8")))
  .map(entry => path.join("tools", entry.name))
  .sort();

const options = process.argv.slice(2);
if (options.length > 1 || (options.length === 1 && options[0] !== "--list")) {
  console.error("Usage: node tools/run-rre-node-tests.mjs [--list]");
  process.exitCode = 2;
} else if (testFiles.length === 0) {
  console.error("No top-level Node test modules discovered; refusing an empty green gate.");
  process.exitCode = 2;
} else if (options[0] === "--list") {
  console.log(JSON.stringify({ moduleCount: testFiles.length, testFiles }, null, 2));
} else {
  console.log(`RRE offline Node gate: ${testFiles.length} discovered top-level modules`);
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
