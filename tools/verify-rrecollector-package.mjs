// RRECollector release gate: strict TOC structure, ordered scripts, and optional installed-byte parity.
// Source/host parity is not an in-game UI-load claim. No writes, dependencies, or game input.
import assert from "node:assert/strict";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {COLLECTOR_MODULES, COLLECTOR_FILES, readCollectorPackage, requireExactPackage, packageText} from './read-rrecollector-package.mjs';

const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const addon = path.join(project, "addons", "RRECollector");
const requiredStrings = [
  "Identifier", "Name", "NameShort", "Description",
  "Author", "Email", "Version", "Environment"
];
const requiredTables = ["SavedVariables", "RunOnStartup"];
const expectedScripts = COLLECTOR_MODULES;

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

function verifySource() {
  const pkg=readCollectorPackage(addon);
  requireExactPackage(pkg);
  const toc = parseToc(packageText(pkg,"RiftAddon.toc"));
  const core = packageText(pkg,"core.lua");
  const readme = packageText(pkg,"README.md");
  const m = core.match(/\bVERSION\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"/);
  assert.ok(m, "core.lua version not found");
  assert.equal(toc.version, m[1], "TOC/core version mismatch");
  assert.ok(readme.includes(`RRECollector v${toc.version}`), "TOC/README version mismatch");
  // Future releases must show the shared VERSION in the window title and
  // startup chat; otherwise the operator can mistake old UI for a new build.
  const ui = packageText(pkg,"ui.lua");
  const main = packageText(pkg,"main.lua");
  assert.match(ui, /title:SetText\("RRE v"\s*\.\.\s*runtime\.VERSION\b/,
    "toolbar title must display the current shared addon version");
  assert.match(main, /local VERSION,\s*SCHEMA\s*=\s*RRECollectorRuntime\.VERSION\b/,
    "startup version must originate from the shared addon version");
  assert.match(main, /say\("v"\s*\.\.\s*VERSION\s*\.\.\s*" ready\. \/rre status"\)/,
    "startup chat must display the current shared addon version");
  return {version:toc.version, files:COLLECTOR_FILES, pkg};
}

function verifyInstalled(installRoot, source) {
  const resolved = path.resolve(installRoot);
  assert.equal(path.basename(resolved).toLowerCase(), "rrecollector",
    "install directory must be RRECollector");
  assert.equal(path.basename(path.dirname(resolved)).toLowerCase(), "addons",
    "install parent must be AddOns");
  const installed=readCollectorPackage(resolved);
  requireExactPackage(installed);
  let matched=0;
  for (const name of source.files) {
    assert.equal(source.pkg.records.get(name).sha256,installed.records.get(name).sha256,
      `installed file differs: ${name}`);
    matched++;
  }
  return {matched,retried:installed.retried};
}

try {
  const args=process.argv.slice(2);
  assert.ok(args.length===0 || (args.length===2 && args[0]==="--installed"),
    "usage: node tools/verify-rrecollector-package.mjs [--installed <AddOns/RRECollector>]");
  const source=verifySource();
  const installed=args.length===2 ? verifyInstalled(args[1],source) : null;
  console.log(JSON.stringify({
    package:"RRECollector", version:source.version, manifest:"strict-pass",
    sources:source.files.length, installedShaMatches:installed?.matched??null,
    stableReadRetries:{source:source.pkg.retried,installed:installed?.retried??[]},
    runtimeUiVerified:false, note:"Runtime requires a normal RIFT addon load and observed toolbar/save."
  }));
} catch (error) {
  console.error("RRECollector package gate FAILED:",error.message);
  process.exitCode=1;
}
