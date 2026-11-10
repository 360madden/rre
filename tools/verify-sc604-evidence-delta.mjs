import fs from "node:fs";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { canonicalRepositoryTextBytes } from "./repository-text-eol.mjs";

export const EXPECTED_FILES = Object.freeze([
  "REA-RIFT-SPELLCASTING-SC102-UI-SPELLDUMP-2026-11-02.md",
  "REA-RIFT-SPELLCASTING-SC103-EXACT-ID-CROSSWALK-2026-11-02.md",
  "REA-RIFT-SPELLCASTING-SC103-353-ID-DETAIL-ATLAS-2026-11-03.json",
  "REA-RIFT-SPELLCASTING-SC103-PROTECTORS-FURY-VARIANT-GAP-2026-11-03.md",
  "REA-RIFT-SPELLCASTING-SC306-QUEUE-ENUM-GAP-2026-10-27.md",
  "REA-RIFT-SPELLCASTING-SC103-LUAPAD-HOVER-PROBE-2026-11-03.md"
]);

const HEADING = "## Verified additions since the November 1 synthesis";
const ROW = /^\| \[[^\]\r\n]+\]\(([^)\r\n]+)\) — `([^`\r\n]+)` \|/;
const DIVIDER = /^\|\s*-{3,}\s*\|\s*-{3,}\s*\|\s*-{3,}\s*\|$/;
const HEX = /^[0-9a-f]{64}$/;
const digest = bytes => createHash("sha256").update(bytes).digest("hex");

export function verifyDeltaMarkdown(markdown, readBytes) {
  if (typeof markdown !== "string" || typeof readBytes !== "function") {
    throw new Error("Invalid verifier input");
  }
  const start = markdown.indexOf(HEADING);
  if (start < 0) throw new Error("SC604 evidence table missing");
  const end = markdown.indexOf("\n## ", start + HEADING.length);
  if (end < 0) throw new Error("SC604 evidence table not bounded");
  const tableLines = markdown.slice(start + HEADING.length, end)
    .split(/\r?\n/).filter(line => line.trimStart().startsWith("|"));
  // Count every pipe-prefixed table line; malformed extra rows must not disappear.
  if (tableLines.length !== EXPECTED_FILES.length + 2) {
    throw new Error("SC604 evidence source count mismatch");
  }
  if (!tableLines[0].startsWith("| ") || !DIVIDER.test(tableLines[1])) {
    throw new Error("Malformed SC604 table header");
  }
  const rows = tableLines.slice(2);

  const expected = new Set(EXPECTED_FILES);
  const seen = new Set();
  const verified = [];
  for (const row of rows) {
    const match = ROW.exec(row);
    if (!match) throw new Error("Malformed SC604 source row");
    const [, basename, sha256] = match;
    // Exact file allowlist rejects traversal, absolute paths, URLs and new sources
    // before any file is opened. This supplement never alters replay inputs.
    if (!expected.has(basename)) throw new Error("Unknown SC604 source path");
    if (seen.has(basename)) throw new Error("Duplicate SC604 source path");
    if (!HEX.test(sha256)) throw new Error("Malformed SC604 source digest");
    seen.add(basename);
    const bytes = readBytes(basename);
    if (!(bytes instanceof Uint8Array)) throw new Error("Invalid SC604 source bytes");
    if (digest(bytes) !== sha256) throw new Error("SC604 source hash mismatch: " + basename);
    verified.push({ basename, sha256 });
  }
  if (seen.size !== expected.size) throw new Error("Missing SC604 source");
  return { ok: true, sourcesVerified: verified.length, sources: verified };
}

export function verifyDeltaOnDisk() {
  const markdown = fs.readFileSync(
    new URL("../docs/REA-RIFT-SPELLCASTING-SC604-EVIDENCE-DELTA-2026-11-04.md", import.meta.url),
    "utf8"
  );
  return verifyDeltaMarkdown(markdown, basename => {
    const url = new URL("../docs/" + basename, import.meta.url);
    if (!fs.lstatSync(url).isFile()) throw new Error("SC604 source is not a regular file");
    return canonicalRepositoryTextBytes(fs.readFileSync(url));
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    process.stdout.write(JSON.stringify(verifyDeltaOnDisk()) + "\n");
  } catch (error) {
    process.stderr.write("SC604 evidence check failed: " + error.message + "\n");
    process.exitCode = 1;
  }
}
