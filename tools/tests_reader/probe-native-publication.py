"""Controlled host-only RREC2 acquisition with existing native tools. Never selects RIFT/VMs."""
from __future__ import annotations
import argparse
import base64
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
NATIVE_SHA = 'f4148b838af694ef95fd46de76859ce9df55194a9fe8be1df74fc2f8f0bce80f'
READER_SHA = '92008d80b72001683a32eae1f82d7b9b15461c4f3c96fc0d5dd2ef0e3225d949'
REGION_BYTES = 262144


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read_json(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write_json(path, value): Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def fixture(path):
    artifact = read_json(path); frames = [s.encode('ascii') for s in artifact['frames']]
    assert 1 <= len(frames) <= 6 and all(len(f) <= 8192 for f in frames)
    buffer = ctypes.create_string_buffer(REGION_BYTES); base = ctypes.addressof(buffer)
    # Many fragment-only decoys precede the real frames, forcing a small generic
    # fragment probe to disclose its exhausted match budget.
    noise = b'RREC2|x\0' * 1000
    ctypes.memmove(base + 64, noise, len(noise))
    addresses = []
    for i, frame in enumerate(frames):
        address = base + 16384 + i * 32768 + i % 4
        ctypes.memmove(address, frame, len(frame)); addresses.append(address)
    # Same session, wrong header sequence: selective token hits remain candidates.
    stale = bytearray(frames[0]); stale[39:55] = b'0000000000000003'
    ctypes.memmove(base + 12288, bytes(stale), min(len(stale), 4096))
    print(json.dumps(dict(pid=os.getpid(), base=f'0x{base:X}', regionBytes=REGION_BYTES,
                         expectedAddresses=[f'0x{x:X}' for x in addresses], frameBytes=[len(f) for f in frames])), flush=True)
    for line in sys.stdin:
        command = line.strip()
        if command == 'exit': break
        if command == 'clear':
            for address in addresses: ctypes.memset(address, 0, 8192)
            print('{"cleared":true}', flush=True)
    return 0


def line_with_timeout(stream):
    result = queue.Queue()
    thread = threading.Thread(target=lambda: result.put(stream.readline()), daemon=True)
    thread.start()
    value = result.get(timeout=5)
    if not value: raise RuntimeError('fixture-closed-stdout')
    return json.loads(value)


def target_for(child, executable):
    class FileTime(ctypes.Structure): _fields_ = [('low', wintypes.DWORD), ('high', wintypes.DWORD)]
    get_times = ctypes.WinDLL('kernel32', use_last_error=True).GetProcessTimes
    get_times.argtypes = [wintypes.HANDLE, *([ctypes.POINTER(FileTime)] * 4)]; get_times.restype = wintypes.BOOL
    times = [FileTime() for _ in range(4)]
    assert get_times(int(child._handle), *[ctypes.byref(x) for x in times])
    ticks = ((times[0].high << 32) | times[0].low) + 504911232000000000
    return dict(processId=child.pid, processStartUtcTicks=ticks, executableSha256=sha(executable).upper())


def execute(argv, out, label):
    begin = time.perf_counter()
    run = subprocess.run([str(x) for x in argv], cwd=ROOT, stdin=subprocess.DEVNULL, capture_output=True,
                         timeout=20, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    (out / (label + '.stdout.txt')).write_bytes(run.stdout); (out / (label + '.stderr.txt')).write_bytes(run.stderr)
    return run, 1000 * (time.perf_counter() - begin)


def cleanup_fixture(child):
    errors = []
    if child.poll() is None:
        try: child.stdin.write('exit\n'); child.stdin.flush()
        except (OSError, ValueError) as error: errors.append('graceful-stdin-' + type(error).__name__)
    for action in [None, 'terminate', 'kill']:
        if child.poll() is not None: break
        try:
            if action: getattr(child, action)()
            child.wait(timeout=5)
        except (OSError, ValueError, subprocess.TimeoutExpired) as error:
            errors.append((action or 'graceful') + '-' + type(error).__name__)
    return dict(fixtureExited=child.poll() is not None, fixtureExitCode=child.returncode, cleanupErrors=errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', type=Path)
    parser.add_argument('--publication', type=Path)
    parser.add_argument('--native', type=Path)
    parser.add_argument('--reader', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.fixture: return fixture(args.fixture)
    assert all([args.publication, args.native, args.reader, args.output])
    assert sha(args.native) == NATIVE_SHA
    assert sha(args.reader) == READER_SHA, 'reader-not-accepted-0.1.2'
    dotnet = Path(shutil.which('dotnet') or '').resolve()
    assert dotnet.is_file(), 'dotnet-host-missing'
    publication = read_json(args.publication); frames = publication['frames']
    assert len(frames) == 5
    session = frames[0].split('|')[1]; sequence = int(frames[0].split('|')[2], 16)
    prefix = f'RREC2|{session}|{sequence:016X}|'.encode('ascii')
    assert sequence == 4 and all(f.startswith(prefix.decode('ascii')) for f in frames)
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    # A Windows venv redirector can have a different PID from its interpreter.
    # Launch the already installed base interpreter directly so its OS handle,
    # reported allocation owner and executable identity describe one process.
    fixture_exe = Path(sys._base_executable).resolve()
    inputs = {str(Path(p).resolve()): sha(p) for p in [args.publication, args.native, args.reader, __file__, fixture_exe, dotnet]}
    child = subprocess.Popen([str(fixture_exe), '-B', str(Path(__file__).resolve()), '--fixture', str(args.publication.resolve())],
                             cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    receipt = dict(status='failed', scope='controlled-host-fixture-only', gameProcessRead=False, guestOperations=0,
                   nativeSha256=NATIVE_SHA, sourceHashes=inputs, runs=[])
    try:
        meta = line_with_timeout(child.stdout); assert meta['pid'] == child.pid
        target = target_for(child, fixture_exe); write_json(out / 'fixture-identity.json', dict(metadata=meta, target=target, session=session, sequence=sequence))
        expected = {int(s, 16) for s in meta['expectedAddresses']}; qualified = []
        for name, anchor, cap, after in [('fragment', 0, 8, 252), ('session-selective', 10, 64, 252), ('boundary-selective', 34, 64, 64)]:
            refs = [dict(name=f'prefix-offset-{anchor + shift}', type='int32',
                         value=str(int.from_bytes(prefix[anchor + shift:anchor + shift + 4], 'little', signed=True))) for shift in range(4)]
            request = dict(schemaVersion=1, evidenceKind='native-value-scout-request/1', target=target,
                           startAddress=meta['base'], references=refs, contextBeforeBytes=anchor + 3, contextAfterBytes=after,
                           maxScanBytes=REGION_BYTES, maxDurationMilliseconds=5000, maxRegionCount=32768, maxMatchCount=cap)
            request_path = out / (name + '.request.json'); write_json(request_path, request)
            run, elapsed = execute([args.native, 'scout-values-native', '--request', request_path, '--output', out / name], out, name)
            assert run.returncode in (0, 3), run.stderr[:500]
            index = read_json(out / name / 'index.json'); assert all(index['identity'][k] == v for k, v in target.items())
            matches = []
            for candidate in index['candidates']:
                capture = read_json(out / name / candidate['snapshotFile'])
                assert all(capture['identity'][k] == v for k, v in target.items())
                assert sha(out / name / candidate['snapshotFile']).upper() == candidate['snapshotSha256']
                assert sha(out / name / candidate['requestFile']).upper() == candidate['requestSha256']
                assert read_json(out / name / candidate['requestFile'])['target'] == target
                chunk = capture['chunks'][0]; raw = base64.b64decode(chunk['bytesBase64'], validate=True)
                assert hashlib.sha256(raw).hexdigest().upper() == chunk['bytesSha256'] and chunk['status'] == 'success'
                assert chunk['address'] == candidate['contextAddress'] and len(raw) == candidate['contextByteLength']
                offsets = {r['name']: anchor + i for i, r in enumerate(refs)}
                assert candidate['width'] == 4 and candidate['referenceNames']
                for reference in candidate['referenceNames']:
                    # Bind a candidate to its exact matched DWORD offset, not a
                    # fuzzy prefix found elsewhere in captured context bytes.
                    start = int(candidate['address'], 16) - offsets[reference]
                    offset = start - int(chunk['address'], 16)
                    if 0 <= offset <= 3 and raw[offset:offset + len(prefix)] == prefix: matches.append(start)
            receipt['runs'].append(dict(name=name, anchorOffset=anchor, contextBeforeBytes=anchor + 3, candidateCount=len(index['candidates']),
                exactFrameAddresses=len(set(matches)), status=index['status'], reason=index['reason'], nextAddress=index['nextAddress'],
                contextByteLengthSum=sum(c['contextByteLength'] for c in index['candidates']),
                attemptedBytes=index['attemptedBytes'], wallMilliseconds=elapsed, exitCode=run.returncode))
            if name == 'fragment': assert not matches and index['status'] == 'partial'
            else:
                assert set(matches) == expected and {address % 4 for address in expected} == {0, 1, 2, 3}
                qualified = sorted(set(matches))
        request = dict(schemaVersion=1, evidenceKind='native-memory-snapshot-request/1', target=target,
                       maxDurationMilliseconds=5000, ranges=[dict(addressKind='absolute-session-address', address=f'0x{x:X}', byteLength=8192) for x in qualified])
        request_path = out / 'frames.request.json'; write_json(request_path, request)
        snapshot = out / 'frames.snapshot.json'
        run, copy_elapsed = execute([args.native, 'snapshot-native', '--request', request_path, '--output', snapshot], out, 'snapshot')
        assert run.returncode == 0, run.stderr[:500]
        copied = read_json(snapshot); assert copied['status'] == 'complete' and all(copied['identity'][k] == v for k, v in target.items())
        chunks = {int(c['address'], 16): base64.b64decode(c['bytesBase64'], validate=True) for c in copied['chunks']}
        for address, original in zip(meta['expectedAddresses'], frames):
            start = int(address, 16); raw = chunks[start] + chunks[start + 4096]
            assert raw[:len(original)] == original.encode('ascii')
        output = out / 'reader.json'
        run, decode_elapsed = execute([dotnet, args.reader, 'capture', '--source', 'native-snapshot', '--input', snapshot,
             '--request', request_path, '--session', session, '--sequence', sequence, '--output', output], out, 'reader')
        assert run.returncode == 0, run.stderr[:500]
        decoded = read_json(output)
        documents = [json.loads(f.split('|', 4)[4][:-9]) for f in frames]
        raw_payload = b''.join(base64.b64decode(b['data'], validate=True) for b in sorted(documents, key=lambda b: b['part']))
        expected_doc = json.loads(raw_payload.decode('utf-8'))
        assert decoded['modules']['abilities']['records'] == expected_doc['abilities'] and len(expected_doc['abilities']) == 54
        assert decoded['modules']['context']['value'] == expected_doc['context'] and decoded['source']['counts'] == expected_doc['counts']
        assert decoded['source']['payloadSha256'] == hashlib.sha256(raw_payload).hexdigest()
        assert all(decoded['qualification'][k] is False for k in ['live', 'freshnessVerified', 'processBuildVerified', 'runtimeProducerVerified', 'sourceAuthenticityVerified', 'atomicSnapshotVerified', 'restartQualified'])
        stale, _ = execute([dotnet, args.reader, 'validate', '--source', 'native-snapshot', '--input', snapshot,
             '--request', request_path, '--session', session, '--sequence', sequence + 1], out, 'stale')
        assert stale.returncode == 2 and b'production-frame-prefix' in stale.stderr
        child.stdin.write('clear\n'); child.stdin.flush(); assert line_with_timeout(child.stdout)['cleared']
        cleared = out / 'cleared.snapshot.json'
        run, _ = execute([args.native, 'snapshot-native', '--request', request_path, '--output', cleared], out, 'cleared-copy')
        assert run.returncode == 0
        rejected, _ = execute([dotnet, args.reader, 'validate', '--source', 'native-snapshot', '--input', cleared,
             '--request', request_path, '--session', session, '--sequence', sequence], out, 'cleared-rejection')
        assert rejected.returncode == 2 and b'frame-prefix' in rejected.stderr
        assert inputs == {p: sha(p) for p in inputs}
        receipt.update(status='passed', exactRecords=54, exactContextAndCounts=True, allFourAlignmentsRecovered=True,
                       exactFiveFramesCopied=True, staleSequenceRejected=True, clearedAddressesRejected=True,
                       copyWallMilliseconds=copy_elapsed, decodeWallMilliseconds=decode_elapsed,
                       nativeSnapshotSha256=sha(snapshot), payloadSha256=hashlib.sha256(raw_payload).hexdigest(),
                       readerOutputSha256=sha(output), wholeProcessAbsenceProven=False, liveBridgeQualified=False)
    finally:
        receipt.update(cleanup_fixture(child))
        if not receipt['fixtureExited']: receipt.update(status='failed', failure='fixture-cleanup-incomplete')
        write_json(out / 'receipt.json', receipt)
    assert receipt['fixtureExited'], 'fixture-cleanup-incomplete'
    print(json.dumps(receipt)); return 0


if __name__ == '__main__': raise SystemExit(main())
