// Optional, read-only .NET 10 SDK probe for RRE's C# reader.
// Safe to import from native-toolchain-doctor.mjs: missing .NET is a result, not an exception.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

export function classifySdkList(output) {
  const lines = String(output ?? "").split(/\r?\n/).map(s => s.trim()).filter(Boolean);
  const versions = lines.map(line =>
    /^(\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?)\s+\[[^\]\r\n]+\]$/.exec(line)?.[1]
  ).filter(Boolean);
  if (versions.length !== lines.length)
    return { status: "unverified", reason: "unrecognized-dotnet-sdk-list-output" };
  if (!versions.length)
    return { status: "missing-sdk", requiredMajor: 10 };
  const net10 = versions.filter(version => Number(version.split(".")[0]) === 10);
  if (!net10.length)
    return { status: "missing-net10-sdk", requiredMajor: 10, availableSdkVersions: versions };
  return { status: "present", requiredMajor: 10, sdkVersion: net10.at(-1) };
}

export function probeDotnetSdk({
  host = os.hostname(),
  platform = process.platform,
  runner = spawnSync,
  exists = fs.existsSync,
  programFiles = process.env.ProgramFiles || "C:\\Program Files",
} = {}) {
  let executable = "dotnet";
  try {
    const options = {
      encoding: "utf8", shell: false, windowsHide: true,
      timeout: 4000, maxBuffer: 4096,
    };
    let result = runner(executable, ["--list-sdks"], options);
    if (result.error?.code === "ENOENT" && platform === "win32") {
      const fallback = path.win32.join(programFiles, "dotnet", "dotnet.exe");
      if (exists(fallback)) {
        executable = fallback;
        result = runner(executable, ["--list-sdks"], options);
      }
    }
    if (result.error)
      return { host, executable, status: result.error.code === "ENOENT" ? "not-found" : "probe-error",
        reason: String(result.error.code || result.error.name || "spawn-error") };
    if (result.status !== 0)
      return { host, executable, status: "probe-error", exitCode: result.status };
    return { host, executable, ...classifySdkList(result.stdout) };
  } catch (error) {
    return { host, executable, status: "probe-error",
      reason: String(error?.code || error?.name || "unexpected-error") };
  }
}

const self = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (self) process.stdout.write(JSON.stringify(probeDotnetSdk()) + "\n");
