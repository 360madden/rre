#!/usr/bin/env node
// Read-only, host-local native-analysis dependency inventory.
// No game/VM access, installs, network calls, or recursive drive scans.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const script = fileURLToPath(import.meta.url);
const repository = path.resolve(path.dirname(script), "..");
const workRoot = path.resolve(repository, "..");
const choices = new Set(["--python", "--rea-home", "--ghidra-home", "--java-home"]);

export function routeForHost(host) {
  const name = String(host).toUpperCase();
  if (name === "LEGION") return "physical-rift-only-no-vmware";
  if (name === "AMD-DESKTOP") return "vmware-capable-subject-to-session-authorization";
  return "unknown-host-no-live-target-inferred";
}

// Known, host-local installations only; AMD-DESKTOP remains independently configurable.
// These defaults probe existing paths and never install software or infer a game target.
export function defaultPathsForHost(host, root = workRoot, repo = repository, platform = process.platform) {
  if (String(host).toUpperCase() !== "LEGION" || platform !== "win32") return {};
  return {
    python: path.join(repo, ".venv", "Scripts", "python.exe"),
    reaHome: path.join(root, "tools", "rea"),
    ghidraHome: path.join(root, "tools", "ghidra_12.1.4_PUBLIC"),
    javaHome: path.join(root, "tools", "jdk-21.0.13+9"),
  };
}

export function parseArguments(argv) {
  if (argv.length % 2) throw new Error("expected --option VALUE pairs");
  const result = {};
  for (let i = 0; i < argv.length; i += 2) {
    if (!choices.has(argv[i]) || !argv[i + 1] || argv[i].slice(2) in result)
      throw new Error("invalid-or-duplicate-option: " + argv[i]);
    if (!path.isAbsolute(argv[i + 1])) throw new Error("absolute-path-required: " + argv[i]);
    result[argv[i].slice(2)] = path.resolve(argv[i + 1]);
  }
  return result;
}

function invoke(executable, args) {
  const result = spawnSync(executable, args, {
    cwd: repository, encoding: "utf8", shell: false, windowsHide: true,
    timeout: 4000, maxBuffer: 16384,
  });
  if (result.error) return { ok: false, reason: result.error.code || result.error.name };
  return { ok: result.status === 0, status: result.status,
    output: (result.stdout || result.stderr || "").trim().slice(0, 1000) };
}

export function probePython(executable) {
  if (!executable) return { status: "unverified", reason: "specify --python ABSOLUTE_PATH" };
  const code = [
    "import importlib.metadata as m, json, platform",
    "out = {}",
    "for name in ('capstone', 'pefile', 'Pillow', 'iced-x86'):",
    " try: out[name] = m.version(name)",
    " except m.PackageNotFoundError: out[name] = None",
    "print(json.dumps({'python':platform.python_version(),'packages':out}))",
  ].join("\n");
  const p = invoke(executable, ["-c", code]);
  if (!p.ok) return { status: "unavailable-at-specified-path", executable, reason: p.reason || p.output };
  try { return { status: "present", executable, ...JSON.parse(p.output) }; }
  catch { return { status: "unverified", executable, reason: "unexpected-python-output" }; }
}

function probeRea(home) {
  const packagePath = path.join(home, "node_modules", "rea-agents", "package.json");
  if (!fs.existsSync(packagePath))
    return { status: "not-found-at-checked-path", home };
  try {
    const metadata = JSON.parse(fs.readFileSync(packagePath, "utf8"));
    return { status: "present", home, version: metadata.version || null };
  } catch { return { status: "unverified", home, reason: "unreadable-package-metadata" }; }
}

function probeGhidra(home) {
  if (!home) return { status: "unverified", reason: "no Ghidra home configured" };
  const names = ["ghidraRun.bat", path.join("support", "analyzeHeadless.bat")];
  return { status: names.some(name => fs.existsSync(path.join(home, name)))
    ? "present-at-checked-path" : "not-found-at-checked-path", home };
}

export function javaFailureStatus(reason, configuredHome) {
  if (configuredHome) return "unavailable-at-specified-path";
  return reason === "ENOENT" ? "not-found-on-path" : "unavailable-on-path";
}

function probeJava(home) {
  const executable = home ? path.join(home, "bin", process.platform === "win32" ? "java.exe" : "java") : "java";
  const p = invoke(executable, ["-version"]);
  if (!p.ok)
    return { status: javaFailureStatus(p.reason, home),
      executable, reason: p.reason || p.output };
  return { status: "present", executable, versionOutput: p.output };
}

export function run(argv = process.argv.slice(2)) {
  const flags = parseArguments(argv);
  const host = os.hostname();
  const defaults = defaultPathsForHost(host);
  const reaHome = flags["rea-home"] || process.env.REA_HOME || defaults.reaHome || path.join(workRoot, "tools", "rea");
  const ghidraHome = flags["ghidra-home"] || process.env.GHIDRA_INSTALL_DIR || defaults.ghidraHome || null;
  const javaHome = flags["java-home"] || process.env.JAVA_HOME || defaults.javaHome || null;
  const python = flags.python || process.env.RRE_PYTHON || defaults.python || null;
  return {
    schemaVersion: 1, hostname: host, hostRoute: routeForHost(host),
    observedAtUtc: new Date().toISOString(), repository,
    node: { status: "present", version: process.version },
    python: probePython(python), rea: probeRea(reaHome),
    ghidra: probeGhidra(ghidraHome), java: probeJava(javaHome),
    qualification: "dependency-inventory-only-not-native-or-live-game-acceptance",
  };
}

if (process.argv[1] && path.resolve(process.argv[1]) === script) {
  try { process.stdout.write(JSON.stringify(run()) + "\n"); }
  catch (e) { process.stderr.write(String(e.message || e) + "\n"); process.exitCode = 2; }
}
