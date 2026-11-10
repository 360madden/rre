import assert from "node:assert/strict";
import path from "node:path";
import test from "node:test";
import { defaultPathsForHost, javaFailureStatus, parseArguments, probePython, routeForHost } from "./native-toolchain-doctor.mjs";

test("host routes are explicit and never infer VMware access on LEGION", () => {
  assert.equal(routeForHost("Legion"), "physical-rift-only-no-vmware");
  assert.equal(routeForHost("AMD-DESKTOP"), "vmware-capable-subject-to-session-authorization");
  assert.equal(routeForHost("unknown"), "unknown-host-no-live-target-inferred");
});

test("LEGION defaults are explicit, Windows-only, and never leak into AMD-DESKTOP", () => {
  const root = path.resolve("rre-fake-work");
  const repo = path.join(root, "rre");
  const legion = defaultPathsForHost("LeGiOn", root, repo, "win32");
  assert.equal(legion.python, path.join(repo, ".venv", "Scripts", "python.exe"));
  assert.equal(legion.reaHome, path.join(root, "tools", "rea"));
  assert.equal(legion.ghidraHome, path.join(root, "tools", "ghidra_12.1.4_PUBLIC"));
  assert.equal(legion.javaHome, path.join(root, "tools", "jdk-21.0.13+9"));
  assert.deepEqual(defaultPathsForHost("AMD-DESKTOP", root, repo, "win32"), {});
  assert.deepEqual(defaultPathsForHost("unknown", root, repo, "win32"), {});
  assert.deepEqual(defaultPathsForHost("LEGION", root, repo, "linux"), {});
});

test("arguments require named absolute paths without duplicates", () => {
  const absolute = path.resolve("not-a-real-install");
  assert.deepEqual(parseArguments(["--python", absolute]), { python: absolute });
  assert.throws(() => parseArguments(["--python", "relative"]), /absolute-path-required/);
  assert.throws(() => parseArguments(["--python", absolute, "--python", absolute]), /duplicate/);
  assert.throws(() => parseArguments(["--vm", absolute]), /invalid/);
});

test("missing Python path remains an explicit unverified dependency", () => {
  const absent = path.resolve("rre-absent-python-" + process.pid + ".exe");
  const result = probePython(absent);
  assert.equal(result.status, "unavailable-at-specified-path");
  assert.equal(result.executable, absent);
});

test("Java failure status distinguishes absence from failed execution", () => {
  assert.equal(javaFailureStatus("ENOENT", null), "not-found-on-path");
  assert.equal(javaFailureStatus("EACCES", null), "unavailable-on-path");
  assert.equal(javaFailureStatus(undefined, null), "unavailable-on-path");
  assert.equal(javaFailureStatus("ENOENT", "C:\\example"), "unavailable-at-specified-path");
});

test("no Python selection is unverified rather than falsely absent", () => {
  assert.deepEqual(probePython(null), {
    status: "unverified", reason: "specify --python ABSOLUTE_PATH",
  });
});
