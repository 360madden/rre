"""Unit tests for early_guard function."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from m4a_guards import early_guard, _validate_sample, _is_finite_number, _validate_position


def make_valid_sample(
    t_ms: int = 0,
    scene_id: str = 'fixture-zone-A',
    player_pos: dict = None,
    target_id: str = 'target-A',
    target_pos: dict = None,
    cancel_requested: bool = False,
    target_none: bool = False,
) -> dict:
    """Create a valid sample for testing."""
    if player_pos is None:
        player_pos = {'x': 0.0, 'y': 0.0, 'z': 0.0}
    if target_pos is None:
        target_pos = {'x': 10.0, 'y': 0.0, 'z': 0.0}

    target = None if target_none else {
        'id': target_id,
        'x': target_pos['x'],
        'y': target_pos['y'],
        'z': target_pos['z'],
    }

    return {
        'tMs': t_ms,
        'sceneId': scene_id,
        'player': player_pos,
        'target': target,
        'cancelRequested': cancel_requested,
    }


class TestIsFiniteNumber(unittest.TestCase):
    def test_valid_integers(self):
        self.assertTrue(_is_finite_number(0))
        self.assertTrue(_is_finite_number(1))
        self.assertTrue(_is_finite_number(-1))
        self.assertTrue(_is_finite_number(1000000))

    def test_valid_floats(self):
        self.assertTrue(_is_finite_number(0.0))
        self.assertTrue(_is_finite_number(1.5))
        self.assertTrue(_is_finite_number(-3.14))

    def test_invalid_booleans(self):
        self.assertFalse(_is_finite_number(True))
        self.assertFalse(_is_finite_number(False))

    def test_invalid_nan(self):
        self.assertFalse(_is_finite_number(float('nan')))

    def test_invalid_inf(self):
        self.assertFalse(_is_finite_number(float('inf')))
        self.assertFalse(_is_finite_number(float('-inf')))

    def test_invalid_types(self):
        self.assertFalse(_is_finite_number('123'))
        self.assertFalse(_is_finite_number(None))
        self.assertFalse(_is_finite_number([1, 2, 3]))
        self.assertFalse(_is_finite_number({'x': 1}))


class TestValidatePosition(unittest.TestCase):
    def test_valid_position(self):
        pos = {'x': 1.0, 'y': 2.0, 'z': 3.0}
        self.assertTrue(_validate_position(pos, 'test'))

    def test_invalid_missing_keys(self):
        self.assertFalse(_validate_position({'x': 1.0, 'y': 2.0}, 'test'))
        self.assertFalse(_validate_position({'x': 1.0, 'z': 3.0}, 'test'))
        self.assertFalse(_validate_position({'y': 2.0, 'z': 3.0}, 'test'))

    def test_invalid_extra_keys(self):
        self.assertFalse(_validate_position({'x': 1.0, 'y': 2.0, 'z': 3.0, 'w': 4.0}, 'test'))

    def test_invalid_coordinates(self):
        self.assertFalse(_validate_position({'x': float('nan'), 'y': 2.0, 'z': 3.0}, 'test'))
        self.assertFalse(_validate_position({'x': float('inf'), 'y': 2.0, 'z': 3.0}, 'test'))
        self.assertFalse(_validate_position({'x': True, 'y': 2.0, 'z': 3.0}, 'test'))
        self.assertFalse(_validate_position({'x': '1.0', 'y': 2.0, 'z': 3.0}, 'test'))


class TestValidateSample(unittest.TestCase):
    def test_valid_sample_tms_zero(self):
        sample = make_valid_sample(t_ms=0)
        self.assertTrue(_validate_sample(sample))

    def test_valid_sample_tms_positive(self):
        sample = make_valid_sample(t_ms=300)
        self.assertTrue(_validate_sample(sample))

    def test_valid_target_none(self):
        sample = make_valid_sample(target_none=True)
        self.assertTrue(_validate_sample(sample))

    def test_invalid_not_dict(self):
        self.assertFalse(_validate_sample(None))
        self.assertFalse(_validate_sample('string'))
        self.assertFalse(_validate_sample([1, 2, 3]))

    def test_invalid_missing_fields(self):
        sample = make_valid_sample()
        del sample['tMs']
        self.assertFalse(_validate_sample(sample))

    def test_invalid_extra_fields(self):
        sample = make_valid_sample()
        sample['extra'] = 'field'
        self.assertFalse(_validate_sample(sample))

    def test_invalid_tms_type(self):
        sample = make_valid_sample(t_ms='1000')
        self.assertFalse(_validate_sample(sample))
        sample = make_valid_sample(t_ms=-1)
        self.assertFalse(_validate_sample(sample))
        sample = make_valid_sample(t_ms=True)
        self.assertFalse(_validate_sample(sample))
        sample = make_valid_sample(t_ms=1.5)
        self.assertFalse(_validate_sample(sample))

    def test_invalid_scene_id(self):
        sample = make_valid_sample(scene_id='')
        self.assertFalse(_validate_sample(sample))
        sample = make_valid_sample(scene_id=123)
        self.assertFalse(_validate_sample(sample))

    def test_invalid_cancel_requested(self):
        sample = make_valid_sample(cancel_requested='true')
        self.assertFalse(_validate_sample(sample))
        sample = make_valid_sample(cancel_requested=1)
        self.assertFalse(_validate_sample(sample))

    def test_invalid_player_missing_keys(self):
        sample = make_valid_sample()
        del sample['player']['x']
        self.assertFalse(_validate_sample(sample))

    def test_invalid_player_nan(self):
        sample = make_valid_sample()
        sample['player']['x'] = float('nan')
        self.assertFalse(_validate_sample(sample))

    def test_invalid_player_bool(self):
        sample = make_valid_sample()
        sample['player']['y'] = True
        self.assertFalse(_validate_sample(sample))

    def test_invalid_target_missing_id(self):
        sample = make_valid_sample()
        del sample['target']['id']
        self.assertFalse(_validate_sample(sample))

    def test_invalid_target_missing_coords(self):
        sample = make_valid_sample()
        del sample['target']['x']
        self.assertFalse(_validate_sample(sample))

    def test_invalid_target_nan_coords(self):
        sample = make_valid_sample()
        sample['target']['x'] = float('nan')
        self.assertFalse(_validate_sample(sample))

    def test_invalid_target_bool_coords(self):
        sample = make_valid_sample()
        sample['target']['y'] = True
        self.assertFalse(_validate_sample(sample))

    def test_valid_target_empty_id(self):
        sample = make_valid_sample()
        sample['target']['id'] = ''
        self.assertTrue(_validate_sample(sample))


class TestEarlyGuardTerminalLatch(unittest.TestCase):
    def test_terminal_arrived_latches(self):
        result = early_guard(
            sample=make_valid_sample(),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state='arrived',
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'arrived')

    def test_terminal_cancelled_latches(self):
        result = early_guard(
            sample=make_valid_sample(),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state='cancelled',
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'cancelled')

    def test_all_terminal_states_latch(self):
        for state in ['arrived', 'cancelled', 'target-unavailable', 'target-changed',
                      'scene-changed', 'telemetry-stale', 'invalid-sample', 'unqualified-source',
                      'height-unsafe', 'no-progress', 'moving-away']:
            result = early_guard(
                sample=make_valid_sample(),
                initial_scene_id='fixture-zone-A',
                initial_target_id='target-A',
                previous_t_ms=None,
                terminal_state=state,
                policy={'staleAfterGapMs': 1200},
            )
            self.assertEqual(result, state)

    def test_moving_away_latches_even_if_target_changes(self):
        sample = make_valid_sample(target_id='target-B')
        result = early_guard(
            sample=sample,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state='moving-away',
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'moving-away')


class TestEarlyGuardSourceKind(unittest.TestCase):
    def test_unqualified_source(self):
        result = early_guard(
            sample=make_valid_sample(),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
            source_kind='live-game',
        )
        self.assertEqual(result, 'unqualified-source')

    def test_synthetic_fixture_passes(self):
        result = early_guard(
            sample=make_valid_sample(),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
            source_kind='synthetic-fixture',
        )
        self.assertIsNone(result)

    def test_terminal_latch_before_source_kind(self):
        result = early_guard(
            sample=make_valid_sample(),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state='arrived',
            policy={'staleAfterGapMs': 1200},
            source_kind='live-game',
        )
        self.assertEqual(result, 'arrived')


class TestEarlyGuardInvalidSample(unittest.TestCase):
    def test_invalid_sample_none(self):
        result = early_guard(
            sample=None,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'invalid-sample')

    def test_invalid_sample_missing_fields(self):
        sample = make_valid_sample()
        del sample['tMs']
        result = early_guard(
            sample=sample,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'invalid-sample')

    def test_invalid_nan_player_coords(self):
        sample = make_valid_sample()
        sample['player']['x'] = float('nan')
        result = early_guard(
            sample=sample,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'invalid-sample')

    def test_invalid_bool_player_coords(self):
        sample = make_valid_sample()
        sample['player']['y'] = True
        result = early_guard(
            sample=sample,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'invalid-sample')

    def test_invalid_tms_bool(self):
        sample = make_valid_sample(t_ms=True)
        result = early_guard(
            sample=sample,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'invalid-sample')

    def test_invalid_tms_negative(self):
        sample = make_valid_sample(t_ms=-1)
        result = early_guard(
            sample=sample,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'invalid-sample')

    def test_invalid_nan_target_coords(self):
        sample = make_valid_sample()
        sample['target']['x'] = float('nan')
        result = early_guard(
            sample=sample,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'invalid-sample')

    def test_invalid_bool_target_coords(self):
        sample = make_valid_sample()
        sample['target']['y'] = True
        result = early_guard(
            sample=sample,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'invalid-sample')


class TestEarlyGuardTimeValidation(unittest.TestCase):
    def test_tms_zero_valid(self):
        result = early_guard(
            sample=make_valid_sample(t_ms=0),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertIsNone(result)

    def test_previous_tms_zero_valid(self):
        result = early_guard(
            sample=make_valid_sample(t_ms=100),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=0,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertIsNone(result)

    def test_duplicate_timestamp_invalid(self):
        result = early_guard(
            sample=make_valid_sample(t_ms=100),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=100,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'invalid-sample')

    def test_decreasing_timestamp_invalid(self):
        result = early_guard(
            sample=make_valid_sample(t_ms=50),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=100,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'invalid-sample')

    def test_previous_tms_negative_invalid(self):
        result = early_guard(
            sample=make_valid_sample(t_ms=100),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=-1,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'invalid-sample')

    def test_previous_tms_bool_invalid(self):
        result = early_guard(
            sample=make_valid_sample(t_ms=100),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=True,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'invalid-sample')


class TestEarlyGuardCancelRequested(unittest.TestCase):
    def test_cancel_requested_true(self):
        result = early_guard(
            sample=make_valid_sample(cancel_requested=True),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'cancelled')


class TestEarlyGuardTargetUnavailable(unittest.TestCase):
    def test_target_none(self):
        result = early_guard(
            sample=make_valid_sample(target_none=True),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'target-unavailable')

    def test_target_empty_id(self):
        sample = make_valid_sample()
        sample['target']['id'] = ''
        result = early_guard(
            sample=sample,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'target-unavailable')


class TestEarlyGuardTargetChanged(unittest.TestCase):
    def test_target_changed(self):
        result = early_guard(
            sample=make_valid_sample(target_id='target-B'),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'target-changed')

    def test_target_same_no_change(self):
        result = early_guard(
            sample=make_valid_sample(target_id='target-A'),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertIsNone(result)

    def test_target_none_initial_no_change(self):
        result = early_guard(
            sample=make_valid_sample(target_id='target-A'),
            initial_scene_id='fixture-zone-A',
            initial_target_id=None,
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertIsNone(result)

    def test_target_none_sample_is_unavailable_not_changed(self):
        result = early_guard(
            sample=make_valid_sample(target_none=True),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'target-unavailable')


class TestEarlyGuardSceneChanged(unittest.TestCase):
    def test_scene_changed(self):
        result = early_guard(
            sample=make_valid_sample(scene_id='fixture-zone-B'),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'scene-changed')

    def test_scene_same_no_change(self):
        result = early_guard(
            sample=make_valid_sample(scene_id='fixture-zone-A'),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertIsNone(result)

    def test_scene_none_initial_no_change(self):
        result = early_guard(
            sample=make_valid_sample(scene_id='fixture-zone-A'),
            initial_scene_id=None,
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertIsNone(result)


class TestEarlyGuardTelemetryStale(unittest.TestCase):
    def test_telemetry_stale_gap_gt_1200(self):
        result = early_guard(
            sample=make_valid_sample(t_ms=3000),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=1000,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'telemetry-stale')

    def test_telemetry_not_stale_gap_lt_1200(self):
        result = early_guard(
            sample=make_valid_sample(t_ms=2000),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=1000,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertIsNone(result)

    def test_telemetry_not_stale_gap_eq_1200(self):
        result = early_guard(
            sample=make_valid_sample(t_ms=2200),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=1000,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertIsNone(result)

    def test_telemetry_no_previous_tms(self):
        result = early_guard(
            sample=make_valid_sample(t_ms=1000),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertIsNone(result)


class TestEarlyGuardPolicyValidation(unittest.TestCase):
    def test_invalid_policy_stale_threshold(self):
        with self.assertRaises(ValueError):
            early_guard(
                sample=make_valid_sample(t_ms=2000),
                initial_scene_id='fixture-zone-A',
                initial_target_id='target-A',
                previous_t_ms=1000,
                terminal_state=None,
                policy={'staleAfterGapMs': 0},
            )

        with self.assertRaises(ValueError):
            early_guard(
                sample=make_valid_sample(t_ms=2000),
                initial_scene_id='fixture-zone-A',
                initial_target_id='target-A',
                previous_t_ms=1000,
                terminal_state=None,
                policy={'staleAfterGapMs': -1},
            )

        with self.assertRaises(ValueError):
            early_guard(
                sample=make_valid_sample(t_ms=2000),
                initial_scene_id='fixture-zone-A',
                initial_target_id='target-A',
                previous_t_ms=1000,
                terminal_state=None,
                policy={'staleAfterGapMs': '1200'},
            )


class TestEarlyGuardPrecedence(unittest.TestCase):
    def test_source_kind_before_invalid_sample(self):
        result = early_guard(
            sample=None,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
            source_kind='live-game',
        )
        self.assertEqual(result, 'unqualified-source')

    def test_invalid_sample_before_cancelled(self):
        sample = make_valid_sample(cancel_requested=True)
        sample['player']['x'] = float('nan')
        result = early_guard(
            sample=sample,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'invalid-sample')

    def test_cancelled_before_target_unavailable(self):
        sample = make_valid_sample(cancel_requested=True, target_none=True)
        result = early_guard(
            sample=sample,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'cancelled')

    def test_target_unavailable_before_target_changed(self):
        sample = make_valid_sample(target_none=True, target_id='target-B')
        result = early_guard(
            sample=sample,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'target-unavailable')

    def test_target_changed_before_scene_changed(self):
        sample = make_valid_sample(target_id='target-B', scene_id='fixture-zone-B')
        result = early_guard(
            sample=sample,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'target-changed')

    def test_scene_changed_before_telemetry_stale(self):
        result = early_guard(
            sample=make_valid_sample(scene_id='fixture-zone-B', t_ms=3000),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=1000,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'scene-changed')

    def test_time_validation_before_cancelled(self):
        sample = make_valid_sample(t_ms=100, cancel_requested=True)
        result = early_guard(
            sample=sample,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=200,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'invalid-sample')


class TestEarlyGuardNoReentry(unittest.TestCase):
    def test_arrived_terminal_prevents_reentry(self):
        result = early_guard(
            sample=make_valid_sample(scene_id='different-zone', target_id='different-target', t_ms=5000),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=1000,
            terminal_state='arrived',
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'arrived')

    def test_cancelled_terminal_prevents_reentry(self):
        result = early_guard(
            sample=make_valid_sample(cancel_requested=False),
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state='cancelled',
            policy={'staleAfterGapMs': 1200},
        )
        self.assertEqual(result, 'cancelled')


class TestEarlyGuardInputsNotMutated(unittest.TestCase):
    def test_sample_not_mutated(self):
        sample = make_valid_sample()
        sample_copy = {
            'tMs': sample['tMs'],
            'sceneId': sample['sceneId'],
            'player': dict(sample['player']),
            'target': dict(sample['target']) if sample['target'] else None,
            'cancelRequested': sample['cancelRequested'],
        }

        early_guard(
            sample=sample,
            initial_scene_id='fixture-zone-A',
            initial_target_id='target-A',
            previous_t_ms=None,
            terminal_state=None,
            policy={'staleAfterGapMs': 1200},
        )

        self.assertEqual(sample['tMs'], sample_copy['tMs'])
        self.assertEqual(sample['sceneId'], sample_copy['sceneId'])
        self.assertEqual(sample['player'], sample_copy['player'])
        if sample['target']:
            self.assertEqual(sample['target'], sample_copy['target'])
        self.assertEqual(sample['cancelRequested'], sample_copy['cancelRequested'])


if __name__ == '__main__':
    unittest.main()