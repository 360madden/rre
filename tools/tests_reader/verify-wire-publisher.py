"""SC622 offline interoperability using the existing pinned Lua runtime and host reader."""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import run_sc103_lua53_offline as lua_runtime


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(argv, env=None):
    result = subprocess.run([str(a) for a in argv], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                            capture_output=True, timeout=30, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if result.returncode:
        raise RuntimeError(f"child-exit-{result.returncode}: {result.stderr[:500].decode('utf-8', errors='replace')}")
    return result.stdout


def literal(value):
    # Every UTF-8 byte is a fixed-width decimal escape: no source interpolation.
    if isinstance(value, str):
        return '"' + ''.join('\\%03d' % b for b in value.encode('utf-8', errors='strict')) + '"'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return json.dumps(value, allow_nan=False)
    if isinstance(value, list):
        return '{' + ','.join(literal(v) for v in value) + '}'
    if isinstance(value, dict):
        return '{' + ','.join('[' + literal(k) + ']=' + literal(v) for k, v in value.items()) + '}'
    raise ValueError("unsupported-safe-lua-fixture-value")


def unpack(path):
    lines = path.read_text(encoding='ascii').splitlines()
    marker = re.fullmatch(r"RRE_WIRE_FIXTURE_PASS ([0-9]+) ([0-9a-f]{32}) ([0-9]+) ([0-9]+)", lines[0])
    assert marker, "missing Lua fixture receipt"
    session, sequence, parts = marker[2], int(marker[3]), int(marker[4])
    assert len(lines) == parts + 1
    bodies, chunks = [], []
    for index, frame in enumerate(lines[1:], 1):
        match = re.fullmatch(r"RREC2\|([0-9a-f]{32})\|([0-9A-F]{16})\|([0-9A-F]{8})\|(.*)\|ENDRREC2", frame)
        assert match and len(frame) <= 8192 and match[1] == session and int(match[2], 16) == sequence
        assert len(match[4].encode('ascii')) == int(match[3], 16)
        body = json.loads(match[4]); bodies.append(body)
        assert body['part'] == index and body['parts'] == parts and body['session'] == session and body['sequence'] == sequence
        chunk = base64.b64decode(body['data'], validate=True)
        assert base64.b64encode(chunk).decode('ascii') == body['data']
        assert len(chunk) == (4096 if index < parts else body['payloadBytes'] - 4096 * (parts - 1))
        chunks.append(chunk)
    payload = b''.join(chunks)
    assert len(payload) == bodies[0]['payloadBytes'] and len(payload) <= 65536
    assert all(b['adler32'] == f"{zlib.adler32(payload):08x}" and b['payloadBytes'] == len(payload) for b in bodies)
    document = json.loads(payload.decode('utf-8', errors='strict'))
    return dict(session=session, sequence=sequence, frames=lines[1:], document=document,
                payloadSha256=hashlib.sha256(payload).hexdigest(), payloadBytes=len(payload), luaChecks=int(marker[1]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--saved', required=True, type=Path)
    parser.add_argument('--reader', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    paths = [ROOT / 'addons/RRECollector/wire.lua', ROOT / 'addons/RRECollector/main.lua', ROOT / 'addons/RRECollector/core.lua', Path(__file__),
             ROOT / 'tools/tests_reader/wire-publisher-fixture.lua', ROOT / 'tools/tests_reader/capture-wire-lifecycle.lua',
             ROOT / 'tools/verify-rrecollector-capture-preserve.lua', ROOT / 'tools/rre-reader-saved-snapshot.mjs',
             ROOT / 'tools/read-rrecollector-saved.mjs', args.reader, args.saved]
    before = {str(p): sha(p) for p in paths}
    runtime_before = lua_runtime.all_hashes(); lua_runtime.check_runtime(runtime_before)
    env = dict(os.environ); env['PATH'] = str(lua_runtime.LUA_DLL.parent) + os.pathsep + env.get('PATH', '')
    synthetic = out / 'synthetic.frames.txt'
    stdout = run([lua_runtime.LUA_EXE, ROOT / 'tools/tests_reader/wire-publisher-fixture.lua', ROOT, synthetic], env)
    assert re.fullmatch(rb'RRE_WIRE_FIXTURE_PASS [0-9]+\r?\n', stdout)
    preservation = run([lua_runtime.LUA_EXE, ROOT / 'tools/verify-rrecollector-capture-preserve.lua'], env)
    assert re.fullmatch(rb'PASS [0-9]+ RC-27 capture preservation assertions \(mock handler\)\r?\n', preservation)
    lifecycle = run([lua_runtime.LUA_EXE, ROOT / 'tools/tests_reader/capture-wire-lifecycle.lua', ROOT], env)
    assert re.fullmatch(rb'SC622_CAPTURE_WIRE_LIFECYCLE_PASS [0-9]+\r?\n', lifecycle)
    exported = json.loads(run(['node', ROOT / 'tools/rre-reader-saved-snapshot.mjs', args.saved]))
    assert exported['sourceSha256'] == sha(args.saved)
    record = dict(exported['context'], addonVersion='0.4.12', sequence=exported['sequence'],
                  captureComplete=True, abilityList=exported['counts'], abilities=exported['abilities'])
    historical = out / 'historical.frames.txt'
    script = out / 'historical-fixture.lua'
    script.write_text('RRECollectorRuntime={VERSION="0.4.12",core={finite=function(v) return type(v)=="number" and v==v and v~=math.huge and v~=-math.huge end}}\n'
        + 'dofile(' + literal(str(ROOT / 'addons/RRECollector/wire.lua')) + ')\n'
        + 'local r=' + literal(record) + '\n'
        + 'local p=RRECollectorRuntime.wire.publish(r); assert(p.status=="complete",p.reason)\n'
        + 'local f=assert(io.open(' + literal(str(historical)) + ',"wb")); f:write("RRE_WIRE_FIXTURE_PASS 0 ",p.session," ",p.sequence," ",p.parts,"\\n")\n'
        + 'for _,v in ipairs(RRECollector_WireFrames) do f:write(v,"\\n") end; f:close()\n', encoding='utf-8')
    run([lua_runtime.LUA_EXE, script], env)
    receipts = []
    for label, source in [('synthetic', synthetic), ('historical54', historical)]:
        result = unpack(source)
        artifact = out / f'{label}.publication.json'
        artifact.write_text(json.dumps(dict(schemaVersion=1, evidenceKind='rrec2-publication-artifact/1',
            origin='offline-lua53-fixture-' + label, frames=result['frames']), separators=(',', ':')), encoding='utf-8')
        output = out / f'{label}.reader.json'
        run(['dotnet', args.reader, 'capture', '--source', 'publication', '--input', artifact,
             '--session', result['session'], '--sequence', result['sequence'], '--output', output])
        decoded = json.loads(output.read_text(encoding='utf-8'))
        assert decoded['modules']['abilities']['records'] == result['document']['abilities']
        assert decoded['modules']['context']['value'] == result['document']['context']
        assert decoded['source']['payloadSha256'] == result['payloadSha256']
        q = decoded['qualification']
        assert not q['fixture'] and all(q[k] is False for k in ['live', 'freshnessVerified', 'processBuildVerified', 'atomicSnapshotVerified', 'restartQualified', 'runtimeProducerVerified', 'sourceAuthenticityVerified'])
        if label == 'historical54':
            assert len(result['document']['abilities']) == 54 and result['document']['abilities'] == exported['abilities']
            # Literal SavedVariables cannot distinguish an empty Lua map from
            # an empty array. Wire context uses object maps; normalize only that
            # documented empty-table ambiguity, retaining every actual value.
            expected_context = {k: ({} if v == [] else v) for k, v in exported['context'].items()}
            assert result['document']['context'] == expected_context and result['document']['counts'] == exported['counts']
        else:
            row = result['document']['abilities'][0]
            assert row['name'] == 'Éclair 水 😀' and row['passive'] is False and row['cooldown'] == 0 and row['target'] == 'uTARGET'
            assert result['document']['context']['player']['power'] == 0 and result['document']['context']['player']['combat'] is False
        receipts.append(dict(case=label, session=result['session'], sequence=result['sequence'], parts=len(result['frames']),
            payloadBytes=result['payloadBytes'], payloadSha256=result['payloadSha256'], luaChecks=result['luaChecks'],
            artifactSha256=sha(artifact), outputSha256=sha(output), abilities=len(result['document']['abilities'])))
    assert before == {str(p): sha(p) for p in paths}, 'source drift'
    assert runtime_before == lua_runtime.all_hashes(), 'runtime drift'
    receipt = dict(status='passed', runtimeHashes=runtime_before, sourceHashes=before, cases=receipts,
                   historicalSourceVersion=exported['addonVersion'], offlineFixtureRetaggedVersion='0.4.12',
                   capturePreservation=preservation.decode('ascii').strip(), captureWireLifecycle=lifecycle.decode('ascii').strip(),
                   emptySavedContextTablesNormalizedToMaps=True,
                   gameExecution=False, liveAcceptance=False,
                   limit='Host Lua5.3 offline checks; no RIFT Lua5.1 load, VM read, addon deployment, or memory acquisition.')
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(status='passed', output=str(out), cases=receipts)))


if __name__ == '__main__':
    main()
