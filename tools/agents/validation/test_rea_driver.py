"""Run the unchanged REA driver against local fake MCP modules, never real REA.

The temporary modules implement a test double; no package installation or child
transport occurs. Fixtures and fake outputs stay under this lane and are removed.
"""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FAKE_CLIENT = """
import fs from 'node:fs';
const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
export class Client {
  async connect() {}
  getServerVersion() { return {name:'synthetic-mcp',version:'test'}; }
  async listTools() { return {tools:['open_binary','close_binary','export_evidence_bundle','xrefs'].map(name=>({name}))}; }
  async callTool({name,arguments:args}) {
    fs.appendFileSync(cfg.fakeCalls, name+'\\n');
    if (name==='open_binary') return {structuredContent:{result:{
      path:cfg.binary,sha256:cfg.syntheticScenario==='wrong-hash' ? '1'.repeat(64) : cfg.expectedSha256,
      architecture:'x86_64',format:args.format??'pe',kind:'executable'}}};
    if (name==='xrefs') return {isError:true,content:[{type:'text',text:'synthetic failure'}]};
    if (name==='export_evidence_bundle') {
      fs.writeFileSync(args.path, '{"records":[]}');
      return {structuredContent:{result:{records:0}}};
    }
    if (name==='close_binary') {
      fs.writeFileSync(args.snapshot_path, '{"entries":[]}');
      return {structuredContent:{result:{evidence_records:0}}};
    }
    throw new Error('unexpected synthetic operation');
  }
  async close() {}
}
"""
FAKE_TRANSPORT = """
export class StdioClientTransport {
  constructor() { this.stderr={on(){}}; }
}
"""


class DriverChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="driver-synthetic-", dir=HERE)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.out = self.folder / "output"
        (self.out / "requests").mkdir(parents=True)
        home = self.folder / "fake-rea-home"
        package = home / "node_modules/@modelcontextprotocol/client"
        package.mkdir(parents=True)
        (package / "package.json").write_text(json.dumps({
            "name": "@modelcontextprotocol/client", "type": "module",
            "exports": {".": "./index.mjs", "./stdio": "./stdio.mjs"}}))
        (package / "index.mjs").write_text(FAKE_CLIENT)
        (package / "stdio.mjs").write_text(FAKE_TRANSPORT)
        rea = home / "node_modules/rea-agents"
        rea.mkdir()
        (rea / "package.json").write_text('{"version":"synthetic"}')
        (home / "package.json").write_text('{"private":true}')
        binary = bytearray(256)
        binary[:2] = b"MZ"
        struct.pack_into("<I", binary, 0x3c, 0x80)
        struct.pack_into("<I", binary, 0x80, 0x4550)
        struct.pack_into("<H", binary, 0x84, 0x8664)
        struct.pack_into("<Q", binary, 0x80 + 48, 0x140000000)
        source = self.folder / "header-only-synthetic.exe"
        source.write_bytes(binary)
        self.cfg = {
            "binary": str(source), "expectedSha256": hashlib.sha256(binary).hexdigest(),
            "expectedReaVersion": "synthetic", "reaHome": str(home),
            "ghidraHome": str(self.folder / "absent-ghidra"),
            "javaHome": str(self.folder / "absent-java"),
            "outputDirectory": str(self.out), "durationSeconds": 60,
            "fakeCalls": str(self.folder / "calls.txt"), "syntheticScenario": "normal",
        }

    def run_driver(self, finish=True):
        if finish:
            (self.out / "requests/99-finish.json").write_text('{"finish":true}')
        config = self.folder / "options.json"
        config.write_text(json.dumps(self.cfg))
        result = subprocess.run([shutil.which("node"), str(ROOT / "tools/rea-session.mjs"), str(config)],
                                capture_output=True, text=True, timeout=10)
        status = json.loads((self.out / "status.json").read_text())
        calls = Path(self.cfg["fakeCalls"]).read_text().splitlines()
        return result, status, calls

    def test_clean_finish_exports_and_closes_without_real_transport(self):
        run, status, calls = self.run_driver()
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(status["state"], "completed")
        self.assertEqual(calls, ["open_binary", "export_evidence_bundle", "close_binary"])
        for line in run.stdout.splitlines():
            json.loads(line)

    def test_small_raw_probe_contract_uses_existing_driver(self):
        source = self.folder / "tiny-raw.bin"
        source.write_bytes(bytes([0xC3]))
        self.cfg.update({"binary": str(source),
                         "expectedSha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                         "format": "raw-binary", "architecture": "x86_64",
                         "entryPoint": "0x1400f3fa4"})
        run, status, calls = self.run_driver()
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(status["state"], "completed")
        self.assertEqual(status["identity"]["imageBase"], "0x1400f3fa4")
        self.assertEqual(status["identity"]["format"], "raw-binary")
        self.assertEqual(calls, ["open_binary", "export_evidence_bundle", "close_binary"])

    def test_tool_error_stops_without_second_open(self):
        (self.out / "requests/01-query.json").write_text('{"tool":"xrefs","arguments":{"address":"0x140001000"}}')
        run, status, calls = self.run_driver()
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(status["state"], "blocked")
        self.assertEqual(calls, ["open_binary", "xrefs", "export_evidence_bundle", "close_binary"])
        self.assertTrue(json.loads((self.out / "responses/01-query.json").read_text())["result"]["isError"])

    def test_bug_v3_provider_admission_hash_mismatch_is_rejected(self):
        self.cfg["syntheticScenario"] = "wrong-hash"
        run, status, calls = self.run_driver()
        self.assertEqual(status["state"], "failed")
        self.assertNotEqual(run.returncode, 0, "driver accepted a different provider target hash")
        self.assertEqual(calls, ["open_binary", "export_evidence_bundle", "close_binary"])
        self.assertIn("identity mismatch", str(status["failures"]))

    def test_bug_v4_unfinished_budget_is_nonzero_exit(self):
        self.cfg["durationSeconds"] = 0
        run, status, calls = self.run_driver(finish=False)
        self.assertEqual(status["state"], "time-budget-reached")
        self.assertNotEqual(run.returncode, 0, "unfinished session exited successfully")

    def test_bug_v5_existing_evidence_without_status_is_preserved(self):
        identity = self.out / "identity.json"
        identity.write_text('{"sentinel":"prior-evidence"}')
        config = self.folder / "options.json"
        config.write_text(json.dumps(self.cfg))
        run = subprocess.run([shutil.which("node"), str(ROOT / "tools/rea-session.mjs"),
                              str(config)], capture_output=True, text=True, timeout=10)
        self.assertNotEqual(run.returncode, 0, "prior evidence must block the session")
        self.assertEqual(json.loads(identity.read_text()), {"sentinel": "prior-evidence"})
        self.assertFalse((self.out / "status.json").exists())


if __name__ == "__main__":
    if "--strict" in sys.argv:
        sys.argv.remove("--strict")
        for method in DriverChecks.__dict__.values():
            if getattr(method, "__unittest_expecting_failure__", False):
                method.__unittest_expecting_failure__ = False
    unittest.main()
