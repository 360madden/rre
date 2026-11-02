// RRECollector release gate: strict TOC structure, ordered scripts, and optional installed-byte parity.
// Source/host parity is not an in-game UI-load claim. No writes, dependencies, or game input.
import assert from "node:assert/strict";
import {createHash} from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";

const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const addon = path.join(project, "addons", "RRECollector");
const requiredStrings = [
  "Identifier", "Name", "NameShort", "Description",
  "Author", "Email", "Version", "Environment"
];
const requiredTables = ["SavedVariables", "RunOnStartup"];
const expectedScripts = [
  "core.lua", "context.lua", "abilities.lua", "capabilities.lua",
  "candidate_catalog.lua", "candidates.lua", "ui.lua", "main.lua"
];

function parseToc(input) {
  assert.equal(input.charCodeAt(0) === 0xfeff, false, "TOC must not have a UTF-8 BOM");
  const scalars = new Map();
  const tables = new Map();
  let active = null;
  for (const [index, raw] of input.split(/\r?\n/).entries()) {
    const line = raw.trim();
    if (!line || line.startsWith("--")) continue;
    if (active) {
      if (line === "}" || line === "},") {active = null; continue;}
      if (active === "SavedVariables") {
        const m = line.match(/^([A-Za-z][A-Za-z0-9_]*)\s*=\s*"([^"\r\n]+)"\s*,?$/);
        assert.ok(m, `invalid SavedVariables entry at TOC line ${index + 1}`);
        const entries = tables.get(active);
        assert.equal(entries.some(e => e[0] === m[1]), false, "duplicate SavedVariables key");
        entries.push([m[1], m[2]]);
      } else {
        const m = line.match(/^"([A-Za-z0-9_.-]+\.lua)"\s*,?$/);
        assert.ok(m, `invalid RunOnStartup entry at TOC line ${index + 1}`);
        tables.get(active).push(m[1]);
      }
      continue;
    }
    const scalar = line.match(/^([A-Za-z][A-Za-z0-9_]*)\s*=\s*"([^"\r\n]+)"$/);
    if (scalar) {
      assert.equal(scalars.has(scalar[1]) || tables.has(scalar[1]), false,
        `duplicate TOC field ${scalar[1]}`);
      scalars.set(scalar[1], scalar[2]);
      continue;
    }
    const table = line.match(/^(SavedVariables|RunOnStartup)\s*=\s*\{$/);
    assert.ok(table, `unknown or invalid TOC syntax at line ${index + 1}`);
    assert.equal(tables.has(table[1]) || scalars.has(table[1]), false,
      `duplicate TOC field ${table[1]}`);
    active = table[1];
    tables.set(active, []);
  }
  assert.equal(active, null, "unclosed TOC table");
  assert.deepEqual([...scalars.keys()].sort(), [...requiredStrings].sort(),
    "TOC scalar fields differ from required contract");
  assert.deepEqual([...tables.keys()].sort(), [...requiredTables].sort(),
    "TOC table fields differ from required contract");
  assert.equal(scalars.get("Identifier"), path.basename(addon), "identifier/folder mismatch");
  assert.equal(scalars.get("Environment"), "4.4", "target environment mismatch");
  assert.deepEqual(tables.get("SavedVariables"), [["RRECollectorData", "character"]],
    "character SavedVariables contract changed");
  assert.deepEqual(tables.get("RunOnStartup"), expectedScripts,
    "dependency-ordered RunOnStartup list changed");
  return {version:scalars.get("Version"), scripts:tables.get("RunOnStartup")};
}

function sha(file) {
  return createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function verifySource() {
  const toc = parseToc(fs.readFileSync(path.join(addon, "RiftAddon.toc"), "utf8"));
  const core = fs.readFileSync(path.join(addon, "core.lua"), "utf8");
  const readme = fs.readFileSync(path.join(addon, "README.md"), "utf8");
  const m = core.match(/\bVERSION\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"/);
  assert.ok(m, "core.lua version not found");
  assert.equal(toc.version, m[1], "TOC/core version mismatch");
  assert.ok(readme.includes(`RRECollector v${toc.version}`), "TOC/README version mismatch");
  for (const name of toc.scripts) {
    assert.ok(fs.statSync(path.join(addon, name)).isFile(), `missing module ${name}`);
  }
  return {version:toc.version, files:[...toc.scripts, "README.md", "RiftAddon.toc"]};
}

function verifyInstalled(installRoot, names) {
  const resolved = path.resolve(installRoot);
  assert.equal(path.basename(resolved).toLowerCase(), "rrecollector",
    "install directory must be RRECollector");
  assert.equal(path.basename(path.dirname(resolved)).toLowerCase(), "addons",
    "install parent must be AddOns");
  let matched=0;
  for (const name of names) {
    const src = path.join(addon,name);
    const dest = path.join(resolved,name);
    assert.ok(fs.statSync(dest).isFile(), `installed file missing: ${name}`);
    assert.equal(sha(src),sha(dest), `installed file differs: ${name}`);
    matched++;
  }
  return matched;
}

try {
  const args=process.argv.slice(2);
  assert.ok(args.length===0 || (args.length===2 && args[0]==="--installed"),
    "usage: node tools/verify-rrecollector-package.mjs [--installed <AddOns/RRECollector>]");
  const source=verifySource();
  const installed=args.length===2 ? verifyInstalled(args[1],source.files) : null;
  console.log(JSON.stringify({
    package:"RRECollector", version:source.version, manifest:"strict-pass",
    sources:source.files.length, installedShaMatches:installed,
    runtimeUiVerified:false, note:"Runtime requires a normal RIFT addon load and observed toolbar/save."
  }));
} catch (error) {
  console.error("RRECollector package gate FAILED:",error.message);
  process.exitCode=1;
}
