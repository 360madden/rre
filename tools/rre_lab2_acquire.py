"""SC625 bounded Lab2 acquisition using the existing GuestSession/F414 tools.

Pure standard-library functions do not contact VMware, import RR2, or send input.
The existing C# native-snapshot decoder remains the publication authority.
"""
from __future__ import annotations

import base64
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
import re
import argparse
import sys
import uuid
import zipfile
import time
from pathlib import PurePosixPath

RR2 = Path(r'C:\work\riftreader2')
VMX = Path(r'C:\rift modding\VMs\RIFT-Lab-2\RIFT-Lab.vmx')
VMRUN = Path(r'C:\Program Files\VMware\VMware Workstation\vmrun.exe')
NATIVE = r'C:\Users\mrkoo\AppData\Local\RiftReader2\codex-jobs\current-ability-records-F4148B838AF694EF\RiftReader2.Live.exe'
NATIVE_SHA = 'F4148B838AF694EF95FD46DE76859CE9DF55194A9FE8BE1DF74FC2F8F0BCE80F'
PINS = {
    RR2/'scripts/vmware_guest_session.py': 'a3808f907224fea709f2709cab56345859474d268b910087a4236b2a0aed4048',
    RR2/'scripts/vm_console_native.py': '5b6863660f23712c14c9548dff96a10fc0e7bf1dee95cf3b3d3362e35a4e6990',
    RR2/'scripts/launch_live_reader.py': 'e70ef5a1d80688adbe029874edee4052259a42f780342e37a751964a8c3c3199',
    VMRUN: '112ec6c7d122f8d9220a5d44cc4b59ad270ba1d7cefaecee38fd07c2a4dafe30',
    Path(r'C:\work\rre\.venv\Scripts\python.exe'): '199ce15a9f0d4f9522edba59338e4879d28cf61f88e377b8164bcb716275ed22',
    Path(r'C:\Python314\python.exe'): '03168c01b7b7491423350e82c26fee71f35b43694d1319d3c668bda6903a0c38',
    Path(r'C:\Python314\python314.dll'): 'fde89cdb5c2d08ae65de7ef4abca1876c93ba3796002f5ac0bf7e4d4f5a94da0',
}

GAME_SHA = '1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8'
MAX_SEQUENCE = 9_007_199_254_740_991


class AcquisitionFailure(ValueError):
    pass


def error_code(error):
    # Never expose an arbitrary dependency exception's arguments/command line.
    return str(error)[:120] if isinstance(error, AcquisitionFailure) else type(error).__name__


def require(condition, code):
    if not condition:
        raise AcquisitionFailure(code)


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def load_json(path, cap=1_048_576):
    return parse_json(read_bytes(path,cap))


def read_bytes(path,cap):
    require(Path(path).stat().st_size <= cap, 'json-byte-limit')
    data = Path(path).read_bytes()
    require(len(data) <= cap, 'json-byte-limit')
    return data


def parse_json(data):

    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'duplicate-json-key')
            result[key] = value
        return result

    def finite(text):
        value = float(text)
        require(math.isfinite(value), 'nonfinite-json')
        return value

    try:
        return json.loads(data.decode('utf-8-sig'), object_pairs_hook=unique,
                          parse_float=finite,
                          parse_constant=lambda _: (_ for _ in ()).throw(AcquisitionFailure('nonfinite-json')))
    except AcquisitionFailure:
        raise
    except (UnicodeError, ValueError) as error:
        raise AcquisitionFailure('invalid-json') from error


def exact(value, keys, code):
    require(type(value) is dict and set(value) == set(keys), code)


def integer(value, low, high, code):
    require(type(value) is int and low <= value <= high, code)


def utc(value):
    require(type(value) is str and re.fullmatch(
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,7})?(?:Z|\+00:00)', value) is not None,
        'utc-format')
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as error:
        raise AcquisitionFailure('utc-value') from error


def validate_admission(binding, window, repository, now=None):
    """Validate explicit context records and original image; this grants no lease."""
    now = datetime.now(timezone.utc) if now is None else now
    require(type(now) is datetime, 'clock-not-utc')
    offset = now.utcoffset()
    require(offset is not None and offset.total_seconds() == 0, 'clock-not-utc')
    exact(binding, ['schemaVersion', 'evidenceKind', 'processId', 'processStartUtcTicks',
                    'executableSha256', 'addonVersion', 'session', 'sequence', 'parts',
                    'payloadBytes', 'imagePath', 'imageSha256', 'observedAtUtc'], 'binding-keys')
    integer(binding['schemaVersion'], 1, 1, 'binding-schema')
    require(binding['evidenceKind'] == 'rre-lab2-publication-binding/1', 'binding-kind')
    integer(binding['processId'], 1, 2_147_483_647, 'process-id')
    ticks = binding['processStartUtcTicks']
    require(type(ticks) is str and re.fullmatch(r'[1-9][0-9]{0,18}', ticks) is not None
            and int(ticks) <= 3_155_378_975_999_999_999, 'process-start-ticks')
    require(type(binding['executableSha256']) is str
            and binding['executableSha256'].lower() == GAME_SHA, 'game-build')
    require(binding['addonVersion'] in ('0.4.12', '0.4.13'), 'addon-version')
    require(type(binding['session']) is str and re.fullmatch(r'[0-9a-f]{32}', binding['session']) is not None,
            'session-format')
    integer(binding['sequence'], 1, MAX_SEQUENCE, 'sequence')
    integer(binding['parts'], 1, 16, 'parts')
    integer(binding['payloadBytes'], 1, 65_536, 'payload-bytes')
    require(binding['parts'] == (binding['payloadBytes'] + 4095) // 4096, 'part-length-binding')
    age = (now - utc(binding['observedAtUtc'])).total_seconds()
    require(0 <= age <= 900, 'binding-age')

    exact(window, ['schemaVersion', 'evidenceKind', 'target', 'startsAtUtc', 'endsAtUtc', 'owner'], 'window-keys')
    integer(window['schemaVersion'], 1, 1, 'window-schema')
    require(window['evidenceKind'] == 'rre-lab2-window/1' and window['target'] == 'Lab2', 'window-target')
    require(type(window['owner']) is str and 0 < len(window['owner'].strip()) <= 256, 'window-owner')
    start, end = utc(window['startsAtUtc']), utc(window['endsAtUtc'])
    require(0 < (end - start).total_seconds() <= 900, 'window-duration')
    require(start <= now and (end - now).total_seconds() >= 60, 'window-admission')

    require(type(binding['imagePath']) is str and type(binding['imageSha256']) is str
            and re.fullmatch(r'[0-9a-f]{64}', binding['imageSha256']) is not None, 'image-binding')
    root = Path(repository).resolve()
    image = Path(binding['imagePath'])
    image = (image if image.is_absolute() else root / image).resolve()
    require(image.is_relative_to((root / 'artifacts').resolve()) and image.suffix.lower() == '.png', 'image-scope')
    require(image.is_file() and image.stat().st_size <= 20 * 1024 * 1024, 'image-size')
    data = image.read_bytes()
    require(data.startswith(b'\x89PNG\r\n\x1a\n') and sha_bytes(data) == binding['imageSha256'], 'image-sha')
    return {'processId': binding['processId'], 'processStartUtcTicks': int(ticks),
            'executableSha256': GAME_SHA.upper()}


def prefix_references(session, sequence):
    require(type(session) is str and re.fullmatch(r'[0-9a-f]{32}', session) is not None, 'session-format')
    integer(sequence, 1, MAX_SEQUENCE, 'sequence')
    prefix = f'RREC2|{session}|{sequence:016X}|'.encode('ascii')
    references = [{'name': f'prefix-o{o}', 'type': 'int32',
                   'value': str(int.from_bytes(prefix[o:o+4], 'little', signed=True))}
                  for o in (34, 35, 36, 37)]
    return prefix, references


def candidate_starts(candidate, snapshot, request, target, prefix):
    """Bind the existing SC623 DWORD locator to its exact successful context."""
    require(type(candidate) is dict and type(snapshot) is dict and type(request) is dict, 'candidate-object')
    require(type(snapshot.get('identity')) is dict, 'candidate-snapshot-identity')
    require(request.get('target') == target, 'candidate-request-target')
    require(all(snapshot.get('identity', {}).get(k) == v for k, v in target.items()), 'candidate-snapshot-target')
    require(candidate.get('width') == 4 and candidate.get('referenceNames'), 'candidate-width-or-reference')
    chunks = snapshot.get('chunks')
    require(type(chunks) is list and len(chunks) == 1, 'candidate-chunk-count')
    chunk = chunks[0]
    require(type(chunk) is dict, 'candidate-chunk-object')
    require(chunk.get('status') == 'success' and chunk.get('address') == candidate.get('contextAddress'), 'candidate-chunk')
    try:
        require(type(chunk.get('bytesBase64')) is str, 'candidate-base64')
        raw = base64.b64decode(chunk['bytesBase64'], validate=True)
    except (ValueError, TypeError, KeyError) as error:
        raise AcquisitionFailure('candidate-base64') from error
    require(len(raw) == candidate.get('contextByteLength') and len(raw) <= 105
            and sha_bytes(raw).upper() == chunk.get('bytesSha256'), 'candidate-bytes')
    address, context = candidate.get('address'), chunk.get('address')
    for value in (address, context):
        require(type(value) is str and re.fullmatch(r'0x[0-9A-F]+', value) is not None, 'candidate-address')
        require(0x10000 <= int(value,16) < 0x800000000000, 'candidate-address-range')
    require(int(address, 16) % 4 == 0, 'candidate-alignment')
    names = candidate['referenceNames']
    require(type(names) is list and all(type(n) is str for n in names)
            and len(names) == len(set(names)) and set(names) <=
            {'prefix-o34', 'prefix-o35', 'prefix-o36', 'prefix-o37'}, 'candidate-reference-name')
    found = set()
    for name in names:
        offset = int(name[8:])
        matched = int(address, 16) - int(context, 16)
        require(0 <= matched <= len(raw)-4 and raw[matched:matched+4] == prefix[offset:offset+4], 'candidate-match-bytes')
        start = int(address, 16) - offset
        relative = start - int(context, 16)
        if 0 <= relative <= 3 and raw[relative:relative+len(prefix)] == prefix:
            found.add(start)
    return found


def file_sha(path):
    return sha_bytes(Path(path).read_bytes())


def write_json(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def execution_hashes(binding_path,binding_bytes,window_path,window_bytes):
    values={str(p):file_sha(p) for p in PINS}
    require(all(values[str(p)]==digest for p,digest in PINS.items()),'dependency-pin-changed')
    require(Path(sys.executable).resolve()==Path(r'C:\work\rre\.venv\Scripts\python.exe').resolve(),'approved-interpreter-required')
    values.update({str(Path(__file__).resolve()):file_sha(__file__),str(Path(sys.executable)):file_sha(sys.executable),
                   str(Path(binding_path).resolve()):sha_bytes(binding_bytes),str(Path(window_path).resolve()):sha_bytes(window_bytes)})
    return values


def quoted(value):
    return "'" + str(value).replace("'", "''") + "'"


def read_scout(directory, request_path, target, prefix):
    """Validate retained artifact closure before applying the shared locator."""
    directory = Path(directory)
    index = load_json(directory/'index.json')
    require(index.get('schemaVersion') == 1 and index.get('evidenceKind') == 'native-value-scout/1', 'scout-schema')
    require(index.get('requestSha256') == file_sha(request_path).upper(), 'scout-request-sha')
    require(index.get('status') in ('complete', 'partial'), 'scout-status')
    require(all(index.get('identity', {}).get(k) == v for k, v in target.items()), 'scout-target')
    require(index.get('implementation', {}).get('bundleSha256') == NATIVE_SHA, 'scout-bundle')
    require(type(index.get('candidates')) is list and len(index['candidates']) <= 128, 'scout-candidates')
    allowed = {'index.json', 'source-request.json'}
    require(file_sha(directory/'source-request.json') == file_sha(request_path), 'scout-source-request')
    starts = set()
    for candidate in index['candidates']:
        require(type(candidate) is dict and candidate.get('status') == 'success', 'scout-candidate-status')
        for key in ('requestFile', 'snapshotFile'):
            name = candidate.get(key)
            require(type(name) is str and re.fullmatch(r'capture-[0-9]{3}\.(?:request|snapshot)\.json', name) is not None,
                    'scout-candidate-file')
            require(name not in allowed, 'scout-duplicate-file')
            allowed.add(name)
            require(file_sha(directory/name).upper() == candidate.get(key.replace('File', 'Sha256')), 'scout-candidate-sha')
        starts.update(candidate_starts(candidate, load_json(directory/candidate['snapshotFile']),
                                       load_json(directory/candidate['requestFile']), target, prefix))
    require({p.name for p in directory.iterdir() if p.is_file()} == allowed, 'scout-file-closure')
    return index, starts


def unpack_scout(archive_path, destination, remote_name):
    """Read bounded flat JSON members; do not call archive.extract/extractall."""
    destination.mkdir()
    with zipfile.ZipFile(archive_path) as archive:
        items = [item for item in archive.infolist() if not item.is_dir()]
        require(len(items) <= 258 and sum(i.file_size for i in items) <= 8*1024*1024, 'scout-zip-budget')
        seen = set()
        for item in items:
            parts = PurePosixPath(item.filename).parts
            require(len(parts) == 2 and parts[0] == remote_name
                    and re.fullmatch(r'(?:index|source-request|capture-[0-9]{3}\.(?:request|snapshot))\.json', parts[1]) is not None
                    and '..' not in parts and '\\' not in item.filename and parts[1] not in seen, 'scout-zip-path')
            require(item.file_size <= 1_048_576, 'scout-zip-member-budget')
            data = archive.read(item)
            require(len(data) == item.file_size, 'scout-zip-member-length')
            seen.add(parts[1])
            (destination/parts[1]).write_bytes(data)


class GuestAcquisition:
    """Short-lived owner; every guest write is journaled before dispatch."""
    def __init__(self, guest, output, target, window, deadline=None):
        self.guest, self.output, self.target, self.window = guest, output, target, window
        self.root = r'C:\Users\Public\Documents\RRE-Acquire-' + uuid.uuid4().hex
        self.known = {}
        self.directories = []
        self.cleanup_complete = False
        self.cleaning = False
        self.deadline = deadline if deadline is not None else time.monotonic()+200
        self.processes = {}
        self.quarantined = False
        self.persist_scope()

    def persist_scope(self):
        # A mutable recovery journal is not the final immutable acceptance receipt.
        (self.output/'guest-scope.json').write_text(json.dumps(dict(root=self.root, knownFiles=self.known,
            directories=self.directories, processes=self.processes, controlQuarantined=self.quarantined,
            cleanupComplete=self.cleanup_complete), indent=2)+'\n', encoding='utf-8')

    def remaining(self):
        if not self.cleaning:
            require(min((utc(self.window['endsAtUtc'])-datetime.now(timezone.utc)).total_seconds(),
                        self.deadline-time.monotonic()) >= 60, 'window-expired-or-short')

    def powershell(self, body, timeout=45):
        self.remaining()
        text = "$ErrorActionPreference='Stop';" + body
        require(len(base64.b64encode(text.encode('utf-16-le'))) <= 4096, 'guest-command-byte-limit')
        self.guest.powershell(text, timeout=min(timeout,15) if self.cleaning else timeout)

    def copy_request(self, local, remote):
        self.remaining()
        require(remote.startswith(self.root+'-'), 'guest-write-scope')
        self.known[remote] = file_sha(local).upper()
        self.persist_scope()
        self.powershell('if(Test-Path -LiteralPath '+quoted(remote)+"){throw 'owned-destination-exists'}")
        self.guest.run('copyFileFromHostToGuest', str(local), remote, timeout=10 if self.cleaning else 30)

    def copy_output(self, remote, local):
        self.remaining()
        self.guest.copy_from_guest(remote, local,timeout=10 if self.cleaning else 30)
        self.known[remote] = file_sha(local).upper()
        self.persist_scope()

    def verify_game(self, label):
        self.remaining()
        remote = self.root + '-' + label + '.json'
        self.known[remote] = None
        self.persist_scope()
        body = 'if(Test-Path -LiteralPath '+quoted(remote)+"){throw 'owned-destination-exists'};$g=Get-Process -Id " + str(self.target['processId']) + ";@{processId=$g.Id;processStartUtcTicks=$g.StartTime.ToUniversalTime().Ticks.ToString();executablePath=$g.Path;executableSha256=(Get-FileHash -LiteralPath $g.Path -Algorithm SHA256).Hash;machine=$env:COMPUTERNAME}|ConvertTo-Json -Compress|Set-Content -LiteralPath " + quoted(remote) + ' -Encoding UTF8'
        self.powershell(body)
        local = self.output/(label+'.identity.json')
        self.copy_output(remote, local)
        value = load_json(local)
        require(value['machine'] == 'RIFT-LAB-2' and value['executablePath'].lower() == r'c:\rift_transfer\rift\rift_x64.exe'
                and value['processId'] == self.target['processId']
                and value['processStartUtcTicks'] == str(self.target['processStartUtcTicks'])
                and value['executableSha256'] == self.target['executableSha256'], 'current-game-identity')
        return value

    def native(self, mode, request_path, remote_output, label):
        require(mode in ('scout-values-native','snapshot-native') and remote_output.startswith(self.root+'-'),'native-operation-scope')
        self.remaining()
        self.verify_game(label)
        remote_request = self.root + '-' + label + '.request.json'
        self.copy_request(request_path, remote_request)
        process_journal=self.root+'-'+label+'.process.json'
        self.known[process_journal]=None
        self.processes[process_journal]={'exitConfirmed':False,'hostJournal':str(self.output/(label+'.process.json'))}
        self.persist_scope()
        # Wait/kill refers only to this exact newly spawned helper process object.
        # The game process is read, never started, stopped, injected or modified.
        body = "$r=" + quoted(NATIVE) + ";if((Get-FileHash -LiteralPath $r -Algorithm SHA256).Hash -cne " + quoted(NATIVE_SHA) + "){throw 'native-bundle-changed'};if((Get-FileHash -LiteralPath " + quoted(remote_request) + " -Algorithm SHA256).Hash -cne " + quoted(file_sha(request_path).upper()) + "){throw 'request-changed'}"
        body += ';if(Test-Path -LiteralPath '+quoted(remote_output)+"){throw 'owned-output-exists'};$p=Start-Process -FilePath $r -ArgumentList @(" + quoted(mode) + ",'--request'," + quoted(remote_request) + ",'--output'," + quoted(remote_output) + ") -WindowStyle Hidden -PassThru;@{pid=$p.Id;ticks=$p.StartTime.ToUniversalTime().Ticks.ToString();path=$r}|ConvertTo-Json -Compress|Set-Content -LiteralPath "+quoted(process_journal)+" -Encoding UTF8;if(-not $p.WaitForExit(15000)){$p.Kill();if(-not $p.WaitForExit(5000)){throw 'native-still-running'};throw 'native-timeout'};if($p.ExitCode -notin @(0,3)){throw 'native-failed'}"
        self.remaining()
        try:
            self.powershell(body, timeout=30)
            self.processes[process_journal]['exitConfirmed']=True
            self.retain_process_journal(process_journal)
        except Exception:
            self.quarantined=True
            self.persist_scope()
            raise

    def retain_process_journal(self,remote):
        entry=self.processes[remote];local=Path(entry['hostJournal'])
        self.copy_output(remote,local)
        process=load_json(local,8192)
        require(type(process) is dict and process.get('path')==NATIVE,'native-process-path')
        integer(process.get('pid'),1,2_147_483_647,'native-process-id')
        require(type(process.get('ticks')) is str and re.fullmatch(r'[1-9][0-9]{0,18}',process['ticks']) is not None,'native-process-start')
        entry['identity']=process
        self.persist_scope()

    def cleanup(self):
        try:
            return self.cleanup_inner()
        except Exception as error:
            self.cleanup_complete=False
            self.quarantined=True
            try:
                self.persist_scope()
                if not (self.output/'guest-cleanup.json').exists():
                    write_json(self.output/'guest-cleanup.json',dict(complete=False,failures=[{'status':'cleanup-exception','error':error_code(error)}]))
            except Exception:
                pass # Never replace the primary acquisition error with host receipt persistence failure.
            return False

    def cleanup_inner(self):
        """Delete only known exact hashes; unknown/changed bytes remain for recovery."""
        self.cleaning = True
        for remote,entry in self.processes.items():
            if self.known.get(remote) is None:
                try:self.retain_process_journal(remote)
                except Exception:self.quarantined=True
        failures = [{'path':p,'status':'unverified-residual'} for p,h in self.known.items() if h is None]
        local=self.output/'cleanup-request.json';remote=self.root+'-cleanup.json'
        files=[{'path':p,'sha256':h} for p,h in self.known.items() if h is not None]
        require(all(p['path'].startswith(self.root+'-') for p in files), 'cleanup-scope')
        write_json(local,dict(files=files,directories=self.directories))
        try:
            self.copy_request(local,remote)
            # Validate all known files before deleting any; never recurse or delete unknown bytes.
            body='$m='+quoted(remote)+';if((Get-FileHash -LiteralPath $m -Algorithm SHA256).Hash -cne '+quoted(file_sha(local).upper())+"){throw 'cleanup-manifest-changed'};$v=Get-Content -LiteralPath $m -Raw|ConvertFrom-Json;foreach($f in $v.files){$p=[IO.Path]::GetFullPath($f.path);if(-not $p.StartsWith("+quoted(self.root+'-')+",[StringComparison]::OrdinalIgnoreCase)){throw 'cleanup-scope'};if(Test-Path -LiteralPath $p){if((Get-Item -LiteralPath $p).LinkType -or (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash -cne $f.sha256){throw 'cleanup-changed'}}};foreach($f in $v.files){Remove-Item -LiteralPath $f.path -ErrorAction SilentlyContinue};foreach($d in $v.directories){if(-not $d.StartsWith("+quoted(self.root+'-scout-')+",[StringComparison]::OrdinalIgnoreCase)){throw 'directory-scope'};if(Test-Path -LiteralPath $d){if((Get-Item -LiteralPath $d).LinkType -or @(Get-ChildItem -LiteralPath $d -Force).Count -ne 0){throw 'cleanup-nonempty'};Remove-Item -LiteralPath $d}};foreach($f in $v.files){if(Test-Path -LiteralPath $f.path){throw 'cleanup-residual'}};Remove-Item -LiteralPath $m"
            self.powershell(body,timeout=45)
        except Exception:
            failures.append({'path':self.root,'status':'batch-cleanup-failed-see-scope'})
        if self.quarantined:failures.append({'status':'control-quarantined-see-process-journals'})
        self.cleanup_complete = not failures
        self.persist_scope()
        write_json(self.output/'guest-cleanup.json', dict(complete=self.cleanup_complete, failures=failures))
        return self.cleanup_complete


def acquire(binding_path, window_path, output):
    deadline=time.monotonic()+200
    repository = Path(__file__).resolve().parents[1]
    output = Path(output).resolve()
    require(output.is_relative_to(repository/'artifacts') and not output.exists(), 'fresh-output-scope')
    output.mkdir()
    started = datetime.now(timezone.utc).isoformat()
    receipt = dict(status='failed', startedAtUtc=started, guestCleanupComplete=False)
    try:
        binding_bytes,window_bytes=read_bytes(binding_path,8192),read_bytes(window_path,8192)
        binding,window=parse_json(binding_bytes),parse_json(window_bytes)
        target = validate_admission(binding, window, repository)
        before=execution_hashes(binding_path,binding_bytes,window_path,window_bytes)
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(RR2))
        from scripts.vmware_guest_session import GuestSession
        from scripts.launch_live_reader import no_prompt
        from scripts.vm_console_native import validate_config, collect_identity, verify_identity, ControlMutex
        config = validate_config(VMX,5962,VMRUN,output,require_files=True)
        epoch = collect_identity(config)
        with ControlMutex(VMX) as owner:
            require(not owner.abandoned, 'abandoned-console-owner')
            validate_admission(binding,window,repository)
            with GuestSession(config.vmrun,config.vmx,lambda:verify_identity(config,epoch),
                              cache_guest_credentials=False,_guest_prompt=no_prompt) as guest:
                require(guest.credential_source == 'cache', 'cached-credential-required')
                operation = GuestAcquisition(guest,output,target,window,deadline)
                primary_error = None
                try:
                    identity = operation.verify_game('initial')
                    prefix, refs = prefix_references(binding['session'],binding['sequence'])
                    starts, passes, cursor = set(), [], '0x10000'
                    for number in range(1,4):
                        verify_identity(config,epoch)
                        request = dict(schemaVersion=1,evidenceKind='native-value-scout-request/1',target=target,
                            startAddress=cursor,references=refs,contextBeforeBytes=37,contextAfterBytes=64,
                            maxScanBytes=1_073_741_824,maxDurationMilliseconds=5000,maxRegionCount=32768,maxMatchCount=128)
                        request_path=output/f'scout-{number}.request.json';write_json(request_path,request)
                        remote_dir=operation.root+f'-scout-{number}'
                        operation.directories.append(remote_dir);operation.persist_scope()
                        operation.native('scout-values-native',request_path,remote_dir,f'scout-{number}')
                        remote_zip=remote_dir+'.zip';operation.known[remote_zip]=None;operation.persist_scope()
                        operation.powershell('Compress-Archive -LiteralPath '+quoted(remote_dir)+' -DestinationPath '+quoted(remote_zip)+' -CompressionLevel Fastest')
                        archive=output/f'scout-{number}.zip';operation.copy_output(remote_zip,archive)
                        directory=output/f'scout-{number}';unpack_scout(archive,directory,Path(remote_dir).name)
                        # Record every retained native byte for exact cleanup even if schema validation fails.
                        for file in directory.iterdir():operation.known[remote_dir+'\\'+file.name]=file_sha(file).upper()
                        operation.persist_scope()
                        index, found = read_scout(directory,request_path,target,prefix)
                        starts.update(found)
                        passes.append({k:index[k] for k in ['status','reason','nextAddress','attemptedBytes','examinedBytes','holes','coveredSpans']})
                        passes[-1].update(candidateCount=len(index['candidates']),exactStarts=[f'0x{x:X}' for x in sorted(found)])
                        require(len(starts) <= binding['parts'], 'ambiguous-frame-aliases')
                        saturated = len(index['candidates']) >= 128
                        if len(starts) == binding['parts'] and not saturated:break
                        next_address = index.get('nextAddress')
                        require(type(next_address) is str and re.fullmatch(r'0x[0-9A-F]+',next_address) is not None
                                and int(next_address,16)>int(cursor,16), 'scout-no-progress')
                        cursor=next_address
                    require(len(starts)==binding['parts'] and not saturated, 'publication-not-completely-located')
                    request=dict(schemaVersion=1,evidenceKind='native-memory-snapshot-request/1',target=target,
                        maxDurationMilliseconds=5000,ranges=[dict(addressKind='absolute-session-address',address=f'0x{x:X}',byteLength=8192) for x in sorted(starts)])
                    request_path=output/'request.json';write_json(request_path,request)
                    remote_snapshot=operation.root+'-snapshot.json';operation.known[remote_snapshot]=None;operation.persist_scope()
                    operation.native('snapshot-native',request_path,remote_snapshot,'snapshot')
                    operation.copy_output(remote_snapshot,output/'snapshot.json')
                    operation.verify_game('final');verify_identity(config,epoch)
                except Exception as error:
                    primary_error = error
                    raise
                finally:
                    clean = operation.cleanup()
                    if not clean and primary_error is None:
                        raise AcquisitionFailure('guest-cleanup-incomplete-see-journal')
        require(all(file_sha(p)==h for p,h in before.items()), 'dependency-drift')
        receipt=dict(schemaVersion=1,evidenceKind='rre-lab2-acquisition/1',status='acquired-cleaned-awaiting-decode',
            startedAtUtc=started,completedAtUtc=datetime.now(timezone.utc).isoformat(),
            bindingSha256=sha_bytes(binding_bytes),windowSha256=sha_bytes(window_bytes),requestSha256=file_sha(output/'request.json'),
            snapshotSha256=file_sha(output/'snapshot.json'),guestCleanupComplete=True,vmIdentity=epoch,
            scoutPasses=passes,sourceHashes=before,guestRoot=operation.root,freshGameIdentity=identity)
        write_json(output/'acquisition.json',receipt)
        return receipt
    except Exception as error:
        receipt.update(error=error_code(error),completedAtUtc=datetime.now(timezone.utc).isoformat())
        write_json(output/'failure.json',receipt)
        raise


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binding',required=True,type=Path)
    parser.add_argument('--window',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    arguments=parser.parse_args()
    try:
        result=acquire(arguments.binding,arguments.window,arguments.output)
        print(json.dumps(result,separators=(',',':')))
    except Exception as error:
        print(json.dumps({'error':error_code(error)}),file=sys.stderr)
        raise SystemExit(2)
