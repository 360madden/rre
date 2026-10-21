"""NAV-003 file-only acceptance. Every trajectory here is synthetic."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('navigation_stop_evidence', ROOT / 'tools/navigation_stop_evidence.py')
nav = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(nav)


def fixture():
    binding = dict(vm='synthetic-vm', epoch='synthetic-process-start', buildSha256='a'*64,
                   scene='synthetic-scene', player='synthetic-player', clock='guest-monotonic-ms',
                   window='synthetic-window', sourceEpoch='synthetic-reader-session')
    # One-ms acquisition intervals: 3500 -> 4499 guarantees <=1000 ms separation.
    times = [0, 800, 1600, 2500, 3000, 3500, 4499, 5000, 5500, 6250, 7000, 7750]
    positions = [0, 0, 0, 1, 2, 3, 3, 3, 3, 3, 3, 3]
    return dict(schemaVersion=1, kind='synthetic-fixture', binding=binding,
        policy=dict(positionTolerance=0.05, minimumMovement=0.2, maxAgeMs=1000,
                    maxGapMs=1000, baselineSpanMs=1500, postSpanMs=2000,
                    settleMs=1000, budgetMs=10000, frozenAtMs=1700),
        frame=dict(binding=copy.deepcopy(binding), captureId='synthetic-frame', imageSha256='b'*64,
                   startMs=1900, endMs=1901, width=1200, height=700, point=[450, 500]),
        actions=[dict(kind='activate', binding=copy.deepcopy(binding), startMs=2000, endMs=2050,
                      delivery='confirmed', released=True, captureId='synthetic-frame',
                      point=[450, 500], width=1200, height=700),
                 dict(kind='cancel', binding=copy.deepcopy(binding), startMs=4000, endMs=4100,
                      delivery='confirmed', released=True)],
        samples=[dict(binding=copy.deepcopy(binding), seq=i+1, startMs=t, endMs=t+1,
                      receivedMs=t+2, status='ok', xyz=[x, 0, 0])
                 for i, (t,x) in enumerate(zip(times, positions))], observationEndMs=8000)


class StopEvidenceTests(unittest.TestCase):
    def run_case(self, value):
        result = nav.evaluate(value)
        self.assertFalse(result['gameInputSent'])
        self.assertEqual(result['commandsIssued'], 0)
        self.assertFalse(result['t0Accepted'])
        self.assertFalse(result['nativeRoutingVerified'])
        self.assertFalse(result['imageBytesVerified'])
        return result

    def test_stable_after_real_displacement_is_conditional_stop(self):
        r=self.run_case(fixture()); self.assertTrue(r['telemetrySupportsStop'])
        self.assertEqual(r['verdict'], 'movement-then-stationary')
        self.assertEqual(r['sourceKind'], 'synthetic-fixture')

    def test_deterministic_and_input_unchanged(self):
        d=fixture(); before=copy.deepcopy(d)
        self.assertEqual(self.run_case(d), self.run_case(d)); self.assertEqual(d,before)

    def test_normalized_recorded_label_does_not_grant_t0(self):
        d=fixture(); d['kind']='recorded-normalized'
        self.assertTrue(self.run_case(d)['telemetrySupportsStop'])

    def test_continued_motion_after_cancel(self):
        d=fixture()
        for i,s in enumerate(d['samples'][8:]): s['xyz'][0]=4+i
        self.assertEqual(self.run_case(d)['verdict'],'post-cancel-motion')

    def test_pause_then_resume_is_not_a_stop(self):
        d=fixture(); d['samples'][-1]['xyz'][0]=4
        self.assertEqual(self.run_case(d)['verdict'],'post-cancel-motion')

    def test_moves_and_returns_to_same_endpoint(self):
        d=fixture(); d['samples'][-2]['xyz'][0]=4
        self.assertEqual(self.run_case(d)['verdict'],'post-cancel-motion')

    def test_small_step_drift_is_not_lost(self):
        d=fixture()
        for i,s in enumerate(d['samples'][8:]): s['xyz'][0]=3+0.02*i
        self.assertEqual(self.run_case(d)['verdict'],'post-cancel-motion')

    def test_vertical_motion_is_not_ignored(self):
        d=fixture(); d['samples'][-1]['xyz'][1]=0.2
        self.assertEqual(self.run_case(d)['verdict'],'post-cancel-motion')

    def test_stationary_without_activation_cannot_pass(self):
        d=fixture()
        for s in d['samples']: s['xyz']=[0,0,0]
        self.assertEqual(self.run_case(d)['verdict'],'no-pre-cancel-movement-observed')

    def test_baseline_drift_blocks_interpretation(self):
        d=fixture(); d['samples'][1]['xyz'][0]=0.2
        self.assertEqual(self.run_case(d)['reason'],'baseline-not-stationary')

    def test_drift_during_settling_is_reported_but_not_stationary_window(self):
        d=fixture(); d['samples'][6]['xyz'][0]=2.8; d['samples'][7]['xyz'][0]=2.9
        self.assertTrue(self.run_case(d)['telemetrySupportsStop'])

    def test_metadata_keyup_alone_cannot_pass(self):
        d=fixture(); d['samples']=d['samples'][:6]
        self.assertFalse(self.run_case(d)['telemetrySupportsStop'])

    def test_short_post_window_rejected(self):
        d=fixture(); d['samples']=d['samples'][:-2]; d['observationEndMs']=6500
        self.assertFalse(self.run_case(d)['telemetrySupportsStop'])

    def test_late_unobserved_tail_rejected(self):
        d=fixture(); d['observationEndMs']=9000
        self.assertEqual(self.run_case(d)['reason'],'unobserved-tail')

    def test_missing_baseline_rejected(self):
        d=fixture(); d['samples']=d['samples'][3:]
        self.assertEqual(self.run_case(d)['reason'],'baseline-coverage')

    def test_post_noise_threshold_not_silently_calibrated(self):
        d=fixture(); d['policy']['positionTolerance']=None
        self.assertEqual(self.run_case(d)['verdict'],'invalid')

    def test_old_receipt_shape_not_promoted(self):
        self.assertEqual(self.run_case({'schemaVersion':1,'gameReady':False,'observation':{'target':{}}})['verdict'],'invalid')

    def test_sample_bound(self):
        d=fixture(); d['samples']=d['samples']*200
        self.assertEqual(self.run_case(d)['verdict'],'invalid')

    def test_no_goal_distance_or_detour_policy_needed(self):
        d=fixture(); d['samples'][3]['xyz']=[-1,0,0]; d['samples'][4]['xyz']=[-2,0,0]
        self.assertTrue(self.run_case(d)['telemetrySupportsStop'])

    def test_delivery_failure_and_unknown_are_not_response(self):
        for status in ['failed','unknown']:
            d=fixture(); d['actions'][0]['delivery']=status
            self.assertEqual(self.run_case(d)['reason'],'unconfirmed-action')

    def test_release_failure_not_accepted(self):
        d=fixture(); d['actions'][1]['released']=False
        self.assertEqual(self.run_case(d)['reason'],'unconfirmed-action')

    def test_missing_cancel_is_inconclusive(self):
        d=fixture(); d['actions'].pop()
        self.assertEqual(self.run_case(d)['reason'],'requires-one-activation-and-one-cancel')

    def test_extra_input_rejected(self):
        d=fixture(); d['actions'].append(copy.deepcopy(d['actions'][0]))
        self.assertEqual(self.run_case(d)['reason'],'requires-one-activation-and-one-cancel')

    def test_wrong_client_point(self):
        d=fixture(); d['actions'][0]['point'][0]+=1
        self.assertEqual(self.run_case(d)['reason'],'reviewed-point-mismatch')

    def test_resized_window(self):
        d=fixture(); d['actions'][0]['width']+=1
        self.assertEqual(self.run_case(d)['reason'],'reviewed-point-mismatch')

    def test_wrong_capture(self):
        d=fixture(); d['actions'][0]['captureId']='another-frame'
        self.assertEqual(self.run_case(d)['reason'],'reviewed-point-mismatch')

    def test_frame_not_immediately_before_request(self):
        d=fixture(); d['frame']['startMs']=0; d['frame']['endMs']=1
        self.assertEqual(self.run_case(d)['reason'],'stale-or-late-frame')

    def test_point_out_of_bounds(self):
        d=fixture(); d['frame']['point'][0]=1200
        self.assertEqual(self.run_case(d)['verdict'],'invalid')

    def test_policy_changed_after_activation(self):
        d=fixture(); d['policy']['frozenAtMs']=2100
        self.assertEqual(self.run_case(d)['reason'],'policy-not-frozen-before-input')

    def test_budget_cannot_be_ignored(self):
        d=fixture(); d['observationEndMs']=13000
        self.assertEqual(self.run_case(d)['reason'],'observation-budget-exceeded')

    def test_baseline_must_arrive_before_policy_freeze(self):
        d=fixture(); d['samples'][2]['receivedMs']=1800
        self.assertEqual(self.run_case(d)['reason'],'baseline-not-available-at-freeze')

    def test_frame_age_uses_earliest_capture_time(self):
        d=fixture(); d['frame']['startMs']=0
        self.assertEqual(self.run_case(d)['reason'],'stale-or-late-frame')

    def test_wide_acquisition_cannot_hide_sample_gap(self):
        d=fixture(); d['samples'][3]['startMs']=2000
        self.assertEqual(self.run_case(d)['reason'],'sample-gap')

    def test_delay_age_uses_earliest_possible_measurement(self):
        d=fixture(); d['samples'][3]['startMs']=1700; d['samples'][3]['receivedMs']=2701
        self.assertEqual(self.run_case(d)['reason'],'stale-or-unreceived-sample')

    def test_cli_output_outside_artifacts_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'input.json'; p.write_text(json.dumps(fixture()),encoding='utf-8')
            out=Path(tmp)/'result'
            r=subprocess.run([sys.executable,'-B',str(ROOT/'tools/navigation_stop_evidence.py'),'--input',str(p),'--output-dir',str(out)],capture_output=True,text=True,timeout=10)
            self.assertEqual(r.returncode,2); self.assertFalse(out.exists())

    def test_published_receipt_matches_actual_bytes(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'result'; nav.publish(nav.evaluate(fixture()),out)
            raw=(out/'report.json').read_bytes(); receipt=json.loads((out/'complete.json').read_bytes())
            self.assertEqual(receipt['sha256'],hashlib.sha256(raw).hexdigest())
            self.assertEqual(receipt['bytes'],len(raw))

    def test_no_dynamic_native_or_network_imports(self):
        import ast
        tree=ast.parse((ROOT/'tools/navigation_stop_evidence.py').read_text(encoding='utf-8'))
        modules=set()
        for n in ast.walk(tree):
            if isinstance(n,ast.Import): modules.update(x.name.split('.')[0] for x in n.names)
            if isinstance(n,ast.ImportFrom) and n.module: modules.add(n.module.split('.')[0])
        self.assertFalse(modules & {'ctypes','socket','subprocess','requests','win32api','pyautogui'})


def add_mutation(name, mutate, reason=None, verdict=None):
    def test(self):
        d=fixture(); mutate(d); r=self.run_case(d)
        self.assertFalse(r['telemetrySupportsStop'])
        if reason: self.assertEqual(r['reason'],reason)
        if verdict: self.assertEqual(r['verdict'],verdict)
    setattr(StopEvidenceTests,'test_'+name,test)


for key in ('vm','epoch','buildSha256','scene','player','clock','window','sourceEpoch'):
    add_mutation('changed_'+key, lambda d,k=key: d['samples'][-1]['binding'].__setitem__(k, 'c'*64 if k=='buildSha256' else 'other'), verdict='aborted')
add_mutation('action_wrong_clock',lambda d: d['actions'][1]['binding'].__setitem__('clock','host-clock'),verdict='aborted')
add_mutation('frame_wrong_vm',lambda d: d['frame']['binding'].__setitem__('vm','other-vm'),verdict='aborted')
add_mutation('duplicate_sequence',lambda d: d['samples'][4].__setitem__('seq',d['samples'][3]['seq']),reason='nonadvancing-source')
add_mutation('out_of_order_time',lambda d: d['samples'][4].__setitem__('startMs',2400),reason='overlapping-or-reversed-acquisition')
add_mutation('stale_final_sample',lambda d: d['samples'][-1].__setitem__('receivedMs',9000),reason='stale-or-unreceived-sample')
add_mutation('large_gap',lambda d: d['samples'].__delitem__(slice(6,9)),reason='sample-gap')
add_mutation('unavailable_coordinate',lambda d: d['samples'][4].__setitem__('status','unavailable'),reason='unavailable-sample')
add_mutation('nan_coordinate',lambda d: d['samples'][4]['xyz'].__setitem__(0,float('nan')),verdict='invalid')
add_mutation('infinite_coordinate',lambda d: d['samples'][4]['xyz'].__setitem__(0,float('inf')),verdict='invalid')
add_mutation('boolean_coordinate',lambda d: d['samples'][4]['xyz'].__setitem__(0,True),verdict='invalid')
add_mutation('boolean_schema',lambda d: d.__setitem__('schemaVersion',True),verdict='invalid')
add_mutation('unknown_field',lambda d: d.__setitem__('cancelled',True),verdict='invalid')
add_mutation('boolean_receipt_time',lambda d: d['samples'][4].__setitem__('receivedMs',True),verdict='invalid')
add_mutation('malformed_sha',lambda d: d['frame'].__setitem__('imageSha256','not-a-hash'),verdict='invalid')


class JsonAndPublicationTests(unittest.TestCase):
    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(ValueError): nav.decode(b'{"schemaVersion":1,"schemaVersion":1}')

    def test_nonstandard_json_number_rejected(self):
        with self.assertRaises(ValueError): nav.decode(b'{"x":NaN}')

    def test_oversize_json_rejected(self):
        with self.assertRaises(ValueError): nav.decode(b' '*(nav.MAX_INPUT_BYTES+1))

    def test_partial_publication_has_no_completion_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'result'; real=nav._write_new
            def injected(p,raw):
                if p.name=='complete.json': raise OSError('injected publication failure')
                return real(p,raw)
            with mock.patch.object(nav,'_write_new',side_effect=injected):
                with self.assertRaises(OSError): nav.publish(nav.evaluate(fixture()),out)
            self.assertTrue((out/'report.json').exists()); self.assertFalse((out/'complete.json').exists())

    def test_publication_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'result'; nav.publish(nav.evaluate(fixture()),out)
            original=(out/'report.json').read_bytes()
            with self.assertRaises(FileExistsError): nav.publish(nav.evaluate(fixture()),out)
            self.assertEqual(original,(out/'report.json').read_bytes())

    def test_cli_synthetic_input_and_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'input.json'; p.write_text(json.dumps(fixture()),encoding='utf-8')
            cmd=[sys.executable,'-B',str(ROOT/'tools/navigation_stop_evidence.py'),'--input',str(p),'--require-stop']
            r=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
            self.assertEqual(r.returncode,0,r.stderr)
            result=json.loads(r.stdout); self.assertEqual(len(result['inputSha256']),64)
            self.assertFalse(result['t0Accepted'])

    def test_cli_negative_exit_is_not_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=fixture(); d['samples'][-1]['xyz'][0]=10
            p=Path(tmp)/'input.json'; p.write_text(json.dumps(d),encoding='utf-8')
            r=subprocess.run([sys.executable,'-B',str(ROOT/'tools/navigation_stop_evidence.py'),'--input',str(p),'--require-stop'],capture_output=True,text=True,timeout=10)
            self.assertEqual(r.returncode,4,r.stderr)
            self.assertFalse(json.loads(r.stdout)['telemetrySupportsStop'])

    def test_cli_malformed_json_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'input.json'; p.write_text('{broken',encoding='utf-8')
            r=subprocess.run([sys.executable,'-B',str(ROOT/'tools/navigation_stop_evidence.py'),'--input',str(p)],capture_output=True,text=True,timeout=10)
            self.assertEqual(r.returncode,2)
            self.assertFalse(json.loads(r.stderr)['gameInputSent'])


if __name__=='__main__': unittest.main()
