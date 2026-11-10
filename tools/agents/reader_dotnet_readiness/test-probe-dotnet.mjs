import assert from "node:assert/strict";
import test from "node:test";
import { classifySdkList, probeDotnetSdk } from "./probe-dotnet.mjs";

const sdk10 = "10.0.302 [C:\\Program Files\\dotnet\\sdk]\r\n";
const sdk8 = "8.0.405 [C:\\Program Files\\dotnet\\sdk]\n";

test("LEGION missing .NET is reported, not thrown", () => {
  const result = probeDotnetSdk({
    host: "LEGION", platform: "win32",
    runner: () => ({ error: { code: "ENOENT" } }),
    exists: () => false,
  });
  assert.deepEqual(result, {
    host: "LEGION", executable: "dotnet", status: "not-found", reason: "ENOENT",
  });
});

test("AMD-DESKTOP installed SDK 10 is recognized", () => {
  const result = probeDotnetSdk({
    host: "AMD-DESKTOP", platform: "win32",
    runner: () => ({ status: 0, stdout: sdk10 }),
  });
  assert.equal(result.host, "AMD-DESKTOP");
  assert.equal(result.status, "present");
  assert.equal(result.sdkVersion, "10.0.302");
});

test("hostnames label actual results; they do not hardcode readiness", () => {
  const result = probeDotnetSdk({
    host: "LEGION", platform: "win32",
    runner: () => ({ status: 0, stdout: sdk10 }),
  });
  assert.equal(result.status, "present");
});

test("PATH failure falls back to an installed standard Windows dotnet.exe", () => {
  const seen = [];
  const result = probeDotnetSdk({
    host: "LEGION", platform: "win32",
    runner: executable => {
      seen.push(executable);
      return seen.length === 1
        ? { error: { code: "ENOENT" } }
        : { status: 0, stdout: sdk10 };
    },
    exists: candidate => candidate === "C:\\Program Files\\dotnet\\dotnet.exe",
  });
  assert.deepEqual(seen, ["dotnet", "C:\\Program Files\\dotnet\\dotnet.exe"]);
  assert.equal(result.status, "present");
});

test("runtime-only and older SDK installations are not net10-ready", () => {
  assert.equal(classifySdkList("").status, "missing-sdk");
  assert.equal(classifySdkList(sdk8).status, "missing-net10-sdk");
  assert.equal(classifySdkList(sdk8 + sdk10).status, "present");
});

test("unexpected output or process failures remain unverified", () => {
  assert.equal(classifySdkList("garbage").status, "unverified");
  assert.equal(probeDotnetSdk({
    host: "AMD-DESKTOP", runner: () => ({ status: 1, stdout: "" }),
  }).status, "probe-error");
  assert.equal(probeDotnetSdk({
    runner: () => { throw new Error("unexpected"); },
  }).status, "probe-error");
});
