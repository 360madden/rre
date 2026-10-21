#!/usr/bin/env python3
"""NAV-003: bounded, file-only request/physical-stop evidence evaluation.

This consumes normalized records, not live game state. It neither sends inputs
nor authenticates records/images. A positive telemetry predicate NEVER accepts
T0 or establishes cancellation causality, arrival exclusion, or native routing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_SAMPLES = 2048
MAX_TIME = (1 << 53) - 1
BINDING_KEYS = {'vm', 'epoch', 'buildSha256', 'scene', 'player', 'clock', 'window', 'sourceEpoch'}
TOP_KEYS = {'schemaVersion', 'kind', 'binding', 'policy', 'frame', 'actions',
            'samples', 'observationEndMs'}
POLICY_KEYS = {'positionTolerance', 'minimumMovement', 'maxAgeMs', 'maxGapMs',
               'baselineSpanMs', 'postSpanMs', 'settleMs', 'budgetMs', 'frozenAtMs'}
SHA = re.compile(r'[0-9a-f]{64}\Z')


class EvidenceError(ValueError):
    """Malformed or unsupported evidence, never a game-response failure."""


def _object(value: Any, keys: set[str], where: str) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        raise EvidenceError(f'{where}: expected exactly {sorted(keys)}')
    return value


def _integer(value: Any, where: str, low: int = 0, high: int = MAX_TIME) -> int:
    if type(value) is not int or not low <= value <= high:
        raise EvidenceError(f'{where}: expected integer in [{low}, {high}]')
    return value


def _number(value: Any, where: str, low: float = -1e12, high: float = 1e12) -> float:
    if type(value) not in (int, float) or not low <= value <= high or not math.isfinite(value):
        raise EvidenceError(f'{where}: finite bounded number required')
    return float(value)


def _label(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 160:
        raise EvidenceError(f'{where}: nonempty bounded text required')
    if any(ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF for c in value):
        raise EvidenceError(f'{where}: invalid text scalar')
    return value


def _binding(value: Any) -> dict:
    b = _object(value, BINDING_KEYS, 'binding')
    for k in BINDING_KEYS:
        _label(b[k], k)
    if not SHA.fullmatch(b['buildSha256']):
        raise EvidenceError('buildSha256: lowercase SHA-256 required')
    return b


def _interval(value: dict) -> None:
    start = _integer(value['startMs'], 'startMs')
    end = _integer(value['endMs'], 'endMs')
    if end < start:
        raise EvidenceError('negative acquisition/action interval')


def _point(value: dict) -> None:
    width = _integer(value['width'], 'width', 1, 16384)
    height = _integer(value['height'], 'height', 1, 16384)
    p = value['point']
    if not isinstance(p, list) or len(p) != 2:
        raise EvidenceError('point: exactly two integer client coordinates required')
    _integer(p[0], 'point.x', 0, width - 1)
    _integer(p[1], 'point.y', 0, height - 1)
    _label(value['captureId'], 'captureId')


def _validate(value: Any) -> None:
    d = _object(value, TOP_KEYS, 'trace')
    if type(d['schemaVersion']) is not int or d['schemaVersion'] != 1:
        raise EvidenceError('unsupported schemaVersion')
    if d['kind'] not in ('synthetic-fixture', 'recorded-normalized'):
        raise EvidenceError('unsupported source kind')
    _binding(d['binding'])
    p = _object(d['policy'], POLICY_KEYS, 'policy')
    tolerance = _number(p['positionTolerance'], 'positionTolerance', 0, 1e6)
    movement = _number(p['minimumMovement'], 'minimumMovement', 0, 1e9)
    if tolerance <= 0 or movement <= 2 * tolerance:
        raise EvidenceError('positive explicit tolerance and movement > twice tolerance required')
    for key in ('maxAgeMs', 'maxGapMs'):
        _integer(p[key], key, 1, 1000)
    _integer(p['baselineSpanMs'], 'baselineSpanMs', 1500, 60000)
    _integer(p['postSpanMs'], 'postSpanMs', 2000, 60000)
    _integer(p['settleMs'], 'settleMs', 0, 2000)
    _integer(p['budgetMs'], 'budgetMs', 1, 10000)
    _integer(p['frozenAtMs'], 'frozenAtMs')
    _integer(d['observationEndMs'], 'observationEndMs')
    f = _object(d['frame'], {'binding', 'captureId', 'imageSha256', 'startMs',
                            'endMs', 'width', 'height', 'point'}, 'frame')
    _binding(f['binding']); _interval(f); _point(f)
    if not isinstance(f['imageSha256'], str) or not SHA.fullmatch(f['imageSha256']):
        raise EvidenceError('imageSha256: lowercase SHA-256 required')
    if not isinstance(d['actions'], list) or len(d['actions']) > 8:
        raise EvidenceError('actions: bounded list required')
    for a in d['actions']:
        if not isinstance(a, dict) or a.get('kind') not in ('activate', 'cancel'):
            raise EvidenceError('unsupported action kind')
        keys = {'kind', 'binding', 'startMs', 'endMs', 'delivery', 'released'}
        if a['kind'] == 'activate':
            keys |= {'captureId', 'width', 'height', 'point'}
        _object(a, keys, 'action'); _binding(a['binding']); _interval(a)
        if not 1 <= a['endMs'] - a['startMs'] <= 250:
            raise EvidenceError('action interval must be 1 through 250 ms')
        if a['delivery'] not in ('confirmed', 'unknown', 'failed') or type(a['released']) is not bool:
            raise EvidenceError('invalid action delivery/release state')
        if a['kind'] == 'activate':
            _point(a)
    samples = d['samples']
    if not isinstance(samples, list) or not 1 <= len(samples) <= MAX_SAMPLES:
        raise EvidenceError(f'samples: 1 through {MAX_SAMPLES} records required')
    for s in samples:
        _object(s, {'binding', 'seq', 'startMs', 'endMs', 'receivedMs', 'status', 'xyz'}, 'sample')
        _binding(s['binding']); _interval(s)
        _integer(s['seq'], 'seq', 0, (1 << 63) - 1)
        _integer(s['receivedMs'], 'receivedMs')
        if s['status'] not in ('ok', 'unavailable', 'invalid'):
            raise EvidenceError('invalid sample status')
        if s['xyz'] is None and s['status'] != 'ok':
            continue
        if not isinstance(s['xyz'], list) or len(s['xyz']) != 3:
            raise EvidenceError('xyz: three finite coordinates required')
        for coordinate in s['xyz']:
            _number(coordinate, 'xyz')


def _diameter(samples: list[dict]) -> float:
    """Exact maximum sampled pair distance, bounded by MAX_SAMPLES (not just endpoints)."""
    largest = 0.0
    for i, sample in enumerate(samples):
        for j in range(i):
            largest = max(largest, math.dist(sample['xyz'], samples[j]['xyz']))
    return largest


def _span(samples: list[dict]) -> int:
    # Guaranteed time separation, conservatively excluding acquisition duration.
    return samples[-1]['startMs'] - samples[0]['endMs'] if len(samples) >= 2 else 0


def evaluate(value: Any) -> dict[str, Any]:
    """Pure deterministic evaluation; all provenance and clock labels are supplied claims."""
    result: dict[str, Any] = {
        'schemaVersion': 1, 'task': 'NAV-003', 'mode': 'file-only-evidence-analysis',
        'sourceKind': None, 'verdict': 'invalid', 'reason': None,
        'telemetrySupportsStop': False, 't0Accepted': False,
        'nativeRoutingVerified': False, 'imageBytesVerified': False,
        'provenanceAuthenticated': False, 'gameInputSent': False, 'commandsIssued': 0,
        'metrics': {},
        'limits': [
            'Normalized records and clock/identity labels are not independently authenticated.',
            'Matching capture hash/point metadata is not verification of image pixels or actual input.',
            'Stationary samples do not prove cancellation caused stopping, exclude arrival/contact, or exclude between-sample motion.',
            'Actual live T0 acceptance requires separately reviewed original images, telemetry, context and authority.'
        ]
    }

    def finish(verdict: str, reason: str) -> dict:
        result.update(verdict=verdict, reason=reason,
                      telemetrySupportsStop=verdict == 'movement-then-stationary')
        return result

    try:
        _validate(value)
    except (EvidenceError, TypeError, OverflowError, RecursionError) as error:
        return finish('invalid', str(error))
    d = value; p = d['policy']; samples = d['samples']; frame = d['frame']
    result['sourceKind'] = d['kind']
    result['metrics']['samplesInspected'] = len(samples)
    # Validate the ENTIRE stream before making any positive predicate. No terminal latch.
    for item in [frame, *d['actions'], *samples]:
        if item['binding'] != d['binding']:
            return finish('aborted', 'identity-scene-or-clock-changed')
    if [a['kind'] for a in d['actions']] != ['activate', 'cancel']:
        return finish('inconclusive', 'requires-one-activation-and-one-cancel')
    activation, cancel = d['actions']
    if any(a['delivery'] != 'confirmed' or not a['released'] for a in d['actions']):
        return finish('inconclusive', 'unconfirmed-action')
    if cancel['startMs'] <= activation['endMs'] or d['observationEndMs'] <= cancel['endMs']:
        return finish('inconclusive', 'action-order-or-observation-end')
    if p['frozenAtMs'] >= activation['startMs']:
        return finish('inconclusive', 'policy-not-frozen-before-input')
    if d['observationEndMs'] - activation['startMs'] > p['budgetMs']:
        return finish('inconclusive', 'observation-budget-exceeded')
    if any(activation[k] != frame[k] for k in ('captureId', 'point', 'width', 'height')):
        return finish('inconclusive', 'reviewed-point-mismatch')
    # Earliest capture/sample time gives the conservative age bound.
    if frame['endMs'] > activation['startMs'] or activation['startMs'] - frame['startMs'] > p['maxAgeMs']:
        return finish('inconclusive', 'stale-or-late-frame')
    previous = None
    for s in samples:
        if s['status'] != 'ok':
            return finish('inconclusive', 'unavailable-sample')
        if s['receivedMs'] < s['endMs'] or s['receivedMs'] - s['startMs'] > p['maxAgeMs'] or s['receivedMs'] > d['observationEndMs']:
            return finish('inconclusive', 'stale-or-unreceived-sample')
        if previous is not None:
            if s['seq'] <= previous['seq']:
                return finish('inconclusive', 'nonadvancing-source')
            if s['startMs'] < previous['endMs'] or s['endMs'] <= previous['endMs']:
                return finish('inconclusive', 'overlapping-or-reversed-acquisition')
            # Worst-case measurement separation, not just the gap between scans.
            if s['endMs'] - previous['startMs'] > p['maxGapMs']:
                return finish('inconclusive', 'sample-gap')
        previous = s
    if d['observationEndMs'] - samples[-1]['startMs'] > p['maxGapMs']:
        return finish('inconclusive', 'unobserved-tail')
    baseline = [s for s in samples if s['endMs'] <= p['frozenAtMs']]
    moving = [s for s in samples if s['startMs'] > activation['endMs'] and s['endMs'] < cancel['startMs']]
    after = [s for s in samples if s['startMs'] >= cancel['endMs'] + p['settleMs']]
    result['metrics'].update(baselineSamples=len(baseline), movementSamples=len(moving),
                             postCancelSamples=len(after),
                             settlingAllowanceMs=p['settleMs'])
    if len(baseline) < 3 or _span(baseline) < p['baselineSpanMs']:
        return finish('inconclusive', 'baseline-coverage')
    if any(s['receivedMs'] > p['frozenAtMs'] for s in baseline):
        return finish('inconclusive', 'baseline-not-available-at-freeze')
    if activation['startMs'] - baseline[-1]['startMs'] > p['maxGapMs']:
        return finish('inconclusive', 'stale-baseline')
    baseline_spread = _diameter(baseline)
    result['metrics']['baselineDiameter'] = baseline_spread
    if baseline_spread > p['positionTolerance']:
        return finish('inconclusive', 'baseline-not-stationary')
    if len(moving) < 2:
        return finish('inconclusive', 'movement-interval-coverage')
    if len(after) < 3 or _span(after) < p['postSpanMs']:
        return finish('inconclusive', 'post-cancel-coverage')
    displacement = [math.dist(s['xyz'], baseline[-1]['xyz']) for s in moving]
    # Subtract measured baseline spread rather than treating baseline jitter as motion.
    moved_samples = sum(max(0.0, x - baseline_spread) > p['minimumMovement'] for x in displacement)
    spread = _diameter(after)
    result['metrics'].update(maximumPreCancelDisplacement=max(displacement),
                             displacedSampleCount=moved_samples,
                             postCancelDiameter=spread, postCancelSpanMs=_span(after),
                             positionTolerance=p['positionTolerance'],
                             firstPostCancelSequence=after[0]['seq'],
                             lastPostCancelSequence=after[-1]['seq'])
    if moved_samples < 2:
        return finish('no-pre-cancel-movement-observed', 'insufficient-pre-cancel-displacement')
    if spread > p['positionTolerance']:
        return finish('post-cancel-motion', 'post-cancel-sampled-displacement-exceeds-tolerance')
    return finish('movement-then-stationary', 'conditional-sampled-stop-predicate-only')


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceError(f'duplicate JSON property: {key}')
        result[key] = value
    return result


def decode(raw: bytes) -> Any:
    if len(raw) > MAX_INPUT_BYTES:
        raise EvidenceError('input exceeds 2 MiB limit')
    def reject_constant(value: str) -> None:
        raise EvidenceError(f'nonstandard JSON number: {value}')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_pairs,
                          parse_constant=reject_constant)
    except (UnicodeError, RecursionError) as error:
        raise EvidenceError('invalid UTF-8 or excessive JSON nesting') from error


def _encoded(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + '\n').encode('utf-8')


def _write_new(path: Path, raw: bytes) -> None:
    with path.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def publish(result: dict, directory: Path) -> None:
    """Fresh directory, no clobber, hash-bound completion marker written LAST."""
    raw = _encoded(result)
    directory.mkdir(parents=False, exist_ok=False)
    _write_new(directory / 'report.json', raw)
    _write_new(directory / 'complete.json', _encoded({
        'schemaVersion': 1, 'file': 'report.json', 'bytes': len(raw),
        'sha256': hashlib.sha256(raw).hexdigest(),
        'meaning': 'File-set publication only; inspect report verdict, not a live-trial acceptance.'
    }))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, help='NEW directory under RRE artifacts/; parent must exist')
    parser.add_argument('--require-stop', action='store_true', help='Exit 4 unless conditional telemetry stop predicate passes')
    args = parser.parse_args(argv)
    try:
        with args.input.open('rb') as stream:
            raw = stream.read(MAX_INPUT_BYTES + 1)
        result = evaluate(decode(raw))
        result['inputSha256'] = hashlib.sha256(raw).hexdigest()
        result['toolSha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        if args.output_dir:
            target = args.output_dir.resolve()
            if (ROOT / 'artifacts').resolve() not in target.parents:
                raise EvidenceError('output must be a new directory under RRE artifacts/')
            publish(result, target)
        sys.stdout.write(_encoded(result).decode('utf-8'))
        if result['verdict'] == 'invalid':
            return 2
        if args.require_stop and not result['telemetrySupportsStop']:
            return 4
        return 0
    except (OSError, ValueError, TypeError, OverflowError) as error:
        sys.stderr.write(_encoded({'error': str(error), 'gameInputSent': False,
                                  'commandsIssued': 0, 't0Accepted': False}).decode('utf-8'))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
