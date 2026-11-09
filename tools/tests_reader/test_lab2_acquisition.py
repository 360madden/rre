"""SC625 offline admission/locator checks. No RR2 imports or VMware operations."""
import copy
from datetime import datetime, timezone, timedelta
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import shutil
import re
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('rre_lab2_acquire', ROOT / 'tools/rre_lab2_acquire.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class AdmissionChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        image = self.root / 'artifacts/source.png'
        image.parent.mkdir()
        image.write_bytes(b'\x89PNG\r\n\x1a\nfixture-not-visual-validation')
        self.now = datetime(2026, 11, 7, 20, 0, tzinfo=timezone.utc)
        self.binding = dict(schemaVersion=1, evidenceKind='rre-lab2-publication-binding/1',
            processId=9752, processStartUtcTicks='639294897826627677', executableSha256=m.GAME_SHA,
            addonVersion='0.4.13', session='0b2a76e89de07abd58ee6c1149237445', sequence=5,
            parts=5, payloadBytes=18226, imagePath='artifacts/source.png', imageSha256=m.sha_bytes(image.read_bytes()),
            observedAtUtc='2026-11-07T19:59:00Z')
        self.window = dict(schemaVersion=1, evidenceKind='rre-lab2-window/1', target='Lab2',
            startsAtUtc='2026-11-07T19:58:00Z', endsAtUtc='2026-11-07T20:10:00Z', owner='explicit coordinated test')

    def validate(self):
        return m.validate_admission(self.binding, self.window, self.root, self.now)

    def test_exact_identity_is_not_rounded(self):
        target = self.validate()
        self.assertEqual(target['processStartUtcTicks'], 639294897826627677)
        self.assertEqual(target['executableSha256'], m.GAME_SHA.upper())

    def test_admission_rejects_stale_future_or_wrong_target(self):
        for key, value in [('observedAtUtc', '2026-11-07T19:44:59Z'), ('observedAtUtc', '2026-11-07T20:00:01Z'),
                           ('processStartUtcTicks', '0639294897826627677'), ('processStartUtcTicks', 639294897826627677),
                           ('executableSha256', '0' * 64), ('schemaVersion', True), ('sequence', True),
                           ('sequence', 2**53), ('session', self.binding['session'].upper()), ('parts', 4),
                           ('addonVersion', '0.4.14'), ('unexpected', 1)]:
            with self.subTest(key=key, value=value):
                original = self.binding
                self.binding = dict(original, **{key: value})
                with self.assertRaises(m.AcquisitionFailure): self.validate()
                self.binding = original

    def test_publication_observed_before_window_is_rejected(self):
        # A recent image is not necessarily evidence from this owner's window.
        self.binding['observedAtUtc'] = '2026-11-07T19:57:59Z'
        with self.assertRaisesRegex(m.AcquisitionFailure, 'binding-window'):
            self.validate()
        # An image observed exactly as the authorized window opens is eligible.
        self.binding['observedAtUtc'] = '2026-11-07T19:58:00Z'
        self.assertEqual(self.validate()['processId'], 9752)

    def test_control_window_not_inferred_from_record(self):
        for key, value in [('target', 'Lab1'), ('endsAtUtc', '2026-11-07T20:00:59Z'),
                           ('endsAtUtc', '2026-11-07T20:14:00Z'), ('startsAtUtc', '2026-11-07T20:01:00Z'),
                           ('startsAtUtc', '2026-11-07T19:58:00-05:00'), ('owner', ' ')]:
            with self.subTest(key=key):
                original = self.window
                self.window = dict(original, **{key: value})
                with self.assertRaises(m.AcquisitionFailure): self.validate()
                self.window = original

    def test_original_image_scope_and_drift(self):
        self.binding['imagePath'] = '../outside.png'
        with self.assertRaises(m.AcquisitionFailure): self.validate()
        self.binding['imagePath'] = 'artifacts/source.png'
        (self.root / self.binding['imagePath']).write_bytes(b'changed')
        with self.assertRaises(m.AcquisitionFailure): self.validate()

    def test_json_duplicate_and_nonfinite_fail(self):
        p = self.root / 'record.json'
        for data in [b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":1e999}', b'\xff', b'{"a":'+b'9'*5000+b'}']:
            p.write_bytes(data)
            with self.assertRaises(m.AcquisitionFailure): m.load_json(p)

    def test_malformed_clock_is_rejected(self):
        for now in [0, '', [], datetime(2026,11,7)]:
            with self.assertRaises(m.AcquisitionFailure):
                m.validate_admission(self.binding,self.window,self.root,now)


class RetainedLocatorChecks(unittest.TestCase):
    def test_real_partial_scout_exact_starts_and_corruption(self):
        directory = ROOT / 'artifacts/sc622-live-bridge-20261107-1428/scan-001/native'
        index = m.load_json(directory / 'index.json')
        self.assertEqual(index['status'], 'partial')
        expected = m.load_json(directory.parent / 'receipt.json')
        prefix, refs = m.prefix_references(expected['expected']['session'], expected['expected']['sequence'])
        self.assertEqual(refs, [{k:r[k] for k in ('name','type','value')} for r in index['request']['references']])
        target = index['request']['target']
        found = set()
        chosen = None
        for c in index['candidates']:
            snapshot = m.load_json(directory / c['snapshotFile'])
            request = m.load_json(directory / c['requestFile'])
            starts = m.candidate_starts(c, snapshot, request, target, prefix)
            found.update(starts)
            if starts: chosen = (c, snapshot, request)
        self.assertEqual({f'0x{x:X}' for x in found}, set(expected['exactFrameStarts']))
        self.assertEqual(len(found), 5)
        c, snapshot, request = copy.deepcopy(chosen)
        snapshot['chunks'][0]['bytesSha256'] = '0'*64
        with self.assertRaises(m.AcquisitionFailure): m.candidate_starts(c, snapshot, request, target, prefix)

    def test_unknown_reference_rejected(self):
        directory = ROOT / 'artifacts/sc622-live-bridge-20261107-1428/scan-001/native'
        index = m.load_json(directory/'index.json'); c=index['candidates'][0]
        snapshot=m.load_json(directory/c['snapshotFile']); request=m.load_json(directory/c['requestFile'])
        c['referenceNames']=['prefix-o33']
        prefix,_=m.prefix_references('0b2a76e89de07abd58ee6c1149237445',5)
        with self.assertRaises(m.AcquisitionFailure): m.candidate_starts(c,snapshot,request,index['request']['target'],prefix)

    def test_exact_match_address_and_allowed_reference_are_bound(self):
        directory=ROOT/'artifacts/sc622-live-bridge-20261107-1428/scan-001/native'
        index=m.load_json(directory/'index.json')
        original=next(c for c in index['candidates'] if c['referenceNames']==['prefix-o36'])
        snapshot=m.load_json(directory/original['snapshotFile']);request=m.load_json(directory/original['requestFile'])
        prefix,_=m.prefix_references('0b2a76e89de07abd58ee6c1149237445',5)
        for field,value in [('referenceNames',['prefix-o34']),('address',f"0x{int(original['address'],16)+4:X}")]:
            c=dict(original,**{field:value})
            with self.assertRaisesRegex(m.AcquisitionFailure,'candidate-match-bytes'):
                m.candidate_starts(c,snapshot,request,index['request']['target'],prefix)

    def test_malformed_snapshot_scalar_types_fail_closed(self):
        directory=ROOT/'artifacts/sc622-live-bridge-20261107-1428/scan-001/native'
        index=m.load_json(directory/'index.json');c=index['candidates'][0]
        original=m.load_json(directory/c['snapshotFile']);request=m.load_json(directory/c['requestFile'])
        prefix,_=m.prefix_references('0b2a76e89de07abd58ee6c1149237445',5)
        for value in [None,[],0,'']:
            s=copy.deepcopy(original);s['identity']=value
            with self.assertRaises(m.AcquisitionFailure):m.candidate_starts(c,s,request,index['request']['target'],prefix)
            s=copy.deepcopy(original);s['chunks'][0]['bytesBase64']=value
            with self.assertRaises(m.AcquisitionFailure):m.candidate_starts(c,s,request,index['request']['target'],prefix)


class OrchestrationChecks(unittest.TestCase):
    def test_actual_identity_path_cannot_precreate_native_snapshot_output(self):
        target=dict(processId=9752,processStartUtcTicks=639294897826627677,executableSha256=m.GAME_SHA.upper())
        class Guest:
            def __init__(self):self.files={};self.native_launches=0
            def powershell(self,text,timeout):
                destination=re.search(r"Set-Content -LiteralPath '([^']+)'",text)
                if 'Get-Process -Id' in text:
                    self.files[destination[1]]=json.dumps(dict(processId=9752,processStartUtcTicks=str(target['processStartUtcTicks']),
                        executablePath=r'C:\RIFT_TRANSFER\RIFT\rift_x64.exe',executableSha256=target['executableSha256'],machine='RIFT-LAB-2')).encode()
                elif 'Start-Process' in text:
                    output=re.search(r"if\(Test-Path -LiteralPath '([^']+)'\)\{throw 'owned-output-exists'",text)[1]
                    if output in self.files:raise m.AcquisitionFailure('owned-output-exists')
                    self.native_launches+=1;self.files[output]=b'controlled-native-fixture'
                    self.files[destination[1]]=json.dumps(dict(pid=123,ticks='1',path=m.NATIVE)).encode()
            def run(self,command,local,remote,**kwargs):self.files[remote]=Path(local).read_bytes()
            def copy_from_guest(self,remote,local,**kwargs):local.write_bytes(self.files[remote])
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory);guest=Guest();op=m.GuestAcquisition(guest,out,target,dict(endsAtUtc=(datetime.now(timezone.utc)+timedelta(minutes=10)).isoformat()))
            request=out/'request.json';request.write_text('{}',encoding='utf-8')
            output=op.root+'-snapshot.json'
            op.native('snapshot-native',request,output,'snapshot')
            self.assertEqual(guest.native_launches,1)
            self.assertIn(op.root+'-snapshot.identity.json',op.known)
            self.assertNotEqual(op.known[op.root+'-snapshot.identity.json'],None)
            self.assertTrue(op.processes[op.root+'-snapshot.process.json']['exitConfirmed'])

    def test_only_pinned_sanitized_session_error_details_are_preserved(self):
        session=type('SessionError',(RuntimeError,),{'__module__':'scripts.vmware_guest_session'})
        self.assertIn('guest-command-failed',m.error_code(session('guest-command-failed:runProgramInGuest:exit=1:category=program')))
        self.assertEqual(m.error_code(RuntimeError('do-not-expose-arbitrary-arguments')),'RuntimeError')
    def test_invalid_admission_keeps_failure_receipt_without_rr2_import(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts') as directory:
            root=Path(directory);binding=root/'binding.json';window=root/'window.json';binding.write_text('{}');window.write_text('{}')
            original_import=__import__
            def blocked(name,*args,**kwargs):
                if name.startswith('scripts.'):raise AssertionError('RR2 import before admission')
                return original_import(name,*args,**kwargs)
            with mock.patch('builtins.__import__',side_effect=blocked):
                with self.assertRaises(m.AcquisitionFailure):m.acquire(binding,window,root/'attempt')
            receipt=m.load_json(root/'attempt/failure.json')
            self.assertFalse(receipt['guestCleanupComplete'])
            self.assertEqual(receipt['error'],'binding-keys')

    def test_complete_real_scout_file_closure(self):
        d=ROOT/'artifacts/sc628-live-context-20261107-1533/scan-001/native'
        request=ROOT/'artifacts/sc628-live-context-20261107-1533/scan-001/request.json'
        target=m.load_json(request)['target'];prefix,_=m.prefix_references('0b6399207d0e277158ee6c11c3af1bd4',7)
        index,starts=m.read_scout(d,request,target,prefix)
        self.assertEqual(len(starts),5)
        self.assertEqual(index['status'],'partial')

    def test_native_and_batch_cleanup_commands_parse_with_bounded_arguments(self):
        class Guest:
            def __init__(self):self.commands=[]
            def powershell(self,text,timeout):self.commands.append(text)
            def run(self,*args,**kwargs):pass
            def copy_from_guest(self,remote,local,**kwargs):local.write_text(json.dumps(dict(pid=123,ticks='1',path=m.NATIVE)),encoding='utf-8')
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory);g=Guest()
            operation=m.GuestAcquisition(g,out,{'processId':9752},dict(endsAtUtc=(datetime.now(timezone.utc)+timedelta(minutes=10)).isoformat()))
            operation.verify_game=lambda _:None
            request=out/'request.json';request.write_text('{}',encoding='utf-8')
            operation.native('scout-values-native',request,operation.root+'-scout-1','scout-1')
            self.assertTrue(operation.cleanup())
            self.assertLessEqual(len(g.commands),5)
            parser="$t=[Console]::In.ReadToEnd();$tok=$null;$err=$null;[System.Management.Automation.Language.Parser]::ParseInput($t,[ref]$tok,[ref]$err)|Out-Null;if($err.Count){$err|ForEach-Object{$_.Message};exit 1}"
            for command in g.commands:
                result=subprocess.run([shutil.which('pwsh') or 'powershell','-NoProfile','-Command',parser],input=command,text=True,capture_output=True,timeout=10)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_cleanup_unknown_data_prevents_success(self):
        class Guest:
            def powershell(self,*args,**kwargs):pass
            def run(self,*args,**kwargs):pass
        with tempfile.TemporaryDirectory() as directory:
            operation=m.GuestAcquisition(Guest(),Path(directory),{}, {})
            operation.known[operation.root+'-unverified.json']=None
            self.assertFalse(operation.cleanup())

    def test_cleanup_persistence_failure_cannot_escape_as_success(self):
        class Guest:
            def powershell(self,*args,**kwargs):pass
            def run(self,*args,**kwargs):pass
        with tempfile.TemporaryDirectory() as directory:
            operation=m.GuestAcquisition(Guest(),Path(directory),{}, {})
            with mock.patch.object(operation,'persist_scope',side_effect=OSError('controlled receipt failure')):
                self.assertFalse(operation.cleanup())
            self.assertTrue(operation.quarantined)

    def test_expiry_blocks_dispatch_but_allows_essential_cleanup(self):
        class Guest:
            def __init__(self):self.calls=0
            def powershell(self,*args,**kwargs):self.calls+=1
            def run(self,*args,**kwargs):self.calls+=1
        with tempfile.TemporaryDirectory() as directory:
            guest=Guest();operation=m.GuestAcquisition(guest,Path(directory),{},dict(endsAtUtc='2020-01-01T00:00:00Z'))
            with self.assertRaises(m.AcquisitionFailure):operation.powershell('throw "must not run"')
            self.assertEqual(guest.calls,0)
            self.assertTrue(operation.cleanup())
            self.assertGreater(guest.calls,0)


if __name__ == '__main__':
    unittest.main()
