"""Unit tests for m4a_progress.classify_progress."""

import unittest
import math
from m4a_progress import classify_progress, DEFAULT_POLICY


class TestClassifyProgress(unittest.TestCase):
    """Tests for classify_progress function."""

    def setUp(self):
        self.policy = DEFAULT_POLICY.copy()

    # --- Moving away tests ---
    def test_moving_away_exceeds_tolerance(self):
        """Moving away: current - previous > movingAwayToleranceM (0.75)."""
        result = classify_progress(
            current_distance=11.0,
            previous_distance=10.0,
            baseline_distance=10.0,
            window_elapsed_ms=100,
            policy=self.policy,
        )
        self.assertEqual(result, "moving-away")

    def test_moving_away_exact_tolerance_not_triggered(self):
        """Exactly at tolerance should not trigger moving_away."""
        result = classify_progress(
            current_distance=10.75,
            previous_distance=10.0,
            baseline_distance=10.0,
            window_elapsed_ms=100,
            policy=self.policy,
        )
        self.assertIsNone(result)

    def test_moving_away_below_tolerance_not_triggered(self):
        """Below tolerance should not trigger moving_away."""
        result = classify_progress(
            current_distance=10.74,
            previous_distance=10.0,
            baseline_distance=10.0,
            window_elapsed_ms=100,
            policy=self.policy,
        )
        self.assertIsNone(result)

    # --- No progress tests ---
    def test_no_progress_window_elapsed_insufficient_progress(self):
        """No progress: window_elapsed_ms >= progressWindowMs (1500) and progress < minimumProgressM (0.25)."""
        result = classify_progress(
            current_distance=10.0,
            previous_distance=10.0,
            baseline_distance=10.0,
            window_elapsed_ms=1600,
            policy=self.policy,
        )
        self.assertEqual(result, "no-progress")

    def test_no_progress_exact_window_elapsed(self):
        """No progress at exact window boundary (1500ms)."""
        result = classify_progress(
            current_distance=10.0,
            previous_distance=10.0,
            baseline_distance=10.0,
            window_elapsed_ms=1500,
            policy=self.policy,
        )
        self.assertEqual(result, "no-progress")

    def test_no_progress_just_before_window_not_triggered(self):
        """Just before window should not trigger no_progress."""
        result = classify_progress(
            current_distance=10.0,
            previous_distance=10.0,
            baseline_distance=10.0,
            window_elapsed_ms=1499,
            policy=self.policy,
        )
        self.assertIsNone(result)

    def test_no_progress_sufficient_progress_not_triggered(self):
        """Sufficient progress within window should not trigger no_progress."""
        result = classify_progress(
            current_distance=9.74,
            previous_distance=10.0,
            baseline_distance=10.0,
            window_elapsed_ms=1600,
            policy=self.policy,
        )
        self.assertIsNone(result)

    def test_no_progress_exact_minimum_progress_not_triggered(self):
        """Exactly minimum progress should not trigger no_progress."""
        result = classify_progress(
            current_distance=9.75,
            previous_distance=10.0,
            baseline_distance=10.0,
            window_elapsed_ms=1600,
            policy=self.policy,
        )
        self.assertIsNone(result)

    # --- Priority: moving_away takes precedence over no_progress ---
    def test_moving_away_precedence_over_no_progress(self):
        """Moving away should be returned even if no_progress condition also met."""
        result = classify_progress(
            current_distance=11.0,
            previous_distance=10.0,
            baseline_distance=10.0,
            window_elapsed_ms=1600,
            policy=self.policy,
        )
        self.assertEqual(result, "moving-away")

    # --- Boundary threshold tests ---
    def test_prior_distance_changed_threshold_boundaries(self):
        """Test various prior distance changes around thresholds."""
        # Just below moving_away threshold
        result = classify_progress(
            current_distance=10.749,
            previous_distance=10.0,
            baseline_distance=10.0,
            window_elapsed_ms=100,
            policy=self.policy,
        )
        self.assertIsNone(result)

        # Just above moving-away threshold
        result = classify_progress(
            current_distance=10.751,
            previous_distance=10.0,
            baseline_distance=10.0,
            window_elapsed_ms=100,
            policy=self.policy,
        )
        self.assertEqual(result, "moving-away")

    # --- Invalid input tests ---
    def test_nonfinite_current_distance_raises(self):
        """Non-finite current_distance should raise ValueError."""
        for val in [float('inf'), float('-inf'), float('nan')]:
            with self.subTest(value=val):
                with self.assertRaises(ValueError):
                    classify_progress(
                        current_distance=val,
                        previous_distance=10.0,
                        baseline_distance=10.0,
                        window_elapsed_ms=100,
                        policy=self.policy,
                    )

    def test_nonfinite_previous_distance_raises(self):
        """Non-finite previous_distance should raise ValueError."""
        with self.assertRaises(ValueError):
            classify_progress(
                current_distance=10.0,
                previous_distance=float('nan'),
                baseline_distance=10.0,
                window_elapsed_ms=100,
                policy=self.policy,
            )

    def test_nonfinite_baseline_distance_raises(self):
        """Non-finite baseline_distance should raise ValueError."""
        with self.assertRaises(ValueError):
            classify_progress(
                current_distance=10.0,
                previous_distance=10.0,
                baseline_distance=float('inf'),
                window_elapsed_ms=100,
                policy=self.policy,
            )

    def test_negative_current_distance_raises(self):
        """Negative current_distance should raise ValueError."""
        with self.assertRaises(ValueError):
            classify_progress(
                current_distance=-1.0,
                previous_distance=10.0,
                baseline_distance=10.0,
                window_elapsed_ms=100,
                policy=self.policy,
            )

    def test_negative_previous_distance_raises(self):
        """Negative previous_distance should raise ValueError."""
        with self.assertRaises(ValueError):
            classify_progress(
                current_distance=10.0,
                previous_distance=-1.0,
                baseline_distance=10.0,
                window_elapsed_ms=100,
                policy=self.policy,
            )

    def test_negative_baseline_distance_raises(self):
        """Negative baseline_distance should raise ValueError."""
        with self.assertRaises(ValueError):
            classify_progress(
                current_distance=10.0,
                previous_distance=10.0,
                baseline_distance=-1.0,
                window_elapsed_ms=100,
                policy=self.policy,
            )

    def test_bool_current_distance_raises(self):
        """Bool current_distance should raise ValueError."""
        with self.assertRaises(ValueError):
            classify_progress(
                current_distance=True,
                previous_distance=10.0,
                baseline_distance=10.0,
                window_elapsed_ms=100,
                policy=self.policy,
            )

    def test_bool_previous_distance_raises(self):
        """Bool previous_distance should raise ValueError."""
        with self.assertRaises(ValueError):
            classify_progress(
                current_distance=10.0,
                previous_distance=False,
                baseline_distance=10.0,
                window_elapsed_ms=100,
                policy=self.policy,
            )

    def test_bool_baseline_distance_raises(self):
        """Bool baseline_distance should raise ValueError."""
        with self.assertRaises(ValueError):
            classify_progress(
                current_distance=10.0,
                previous_distance=10.0,
                baseline_distance=True,
                window_elapsed_ms=100,
                policy=self.policy,
            )

    def test_negative_window_elapsed_ms_raises(self):
        """Negative window_elapsed_ms should raise ValueError."""
        with self.assertRaises(ValueError):
            classify_progress(
                current_distance=10.0,
                previous_distance=10.0,
                baseline_distance=10.0,
                window_elapsed_ms=-1,
                policy=self.policy,
            )

    def test_bool_window_elapsed_ms_raises(self):
        """Bool window_elapsed_ms should raise ValueError."""
        with self.assertRaises(ValueError):
            classify_progress(
                current_distance=10.0,
                previous_distance=10.0,
                baseline_distance=10.0,
                window_elapsed_ms=True,
                policy=self.policy,
            )

    def test_float_window_elapsed_ms_raises(self):
        """Float window_elapsed_ms should raise ValueError."""
        with self.assertRaises(ValueError):
            classify_progress(
                current_distance=10.0,
                previous_distance=10.0,
                baseline_distance=10.0,
                window_elapsed_ms=100.0,
                policy=self.policy,
            )

    def test_invalid_policy_type_raises(self):
        """Non-dict policy should raise ValueError."""
        with self.assertRaises(ValueError):
            classify_progress(
                current_distance=10.0,
                previous_distance=10.0,
                baseline_distance=10.0,
                window_elapsed_ms=100,
                policy="not a dict",
            )

    def test_missing_policy_key_raises(self):
        """Missing policy key should raise ValueError."""
        for key in ["movingAwayToleranceM", "progressWindowMs", "minimumProgressM"]:
            with self.subTest(missing_key=key):
                bad_policy = self.policy.copy()
                del bad_policy[key]
                with self.assertRaises(ValueError):
                    classify_progress(
                        current_distance=10.0,
                        previous_distance=10.0,
                        baseline_distance=10.0,
                        window_elapsed_ms=100,
                        policy=bad_policy,
                    )

    def test_nonpositive_moving_away_tolerance_raises(self):
        """Non-positive movingAwayToleranceM should raise ValueError."""
        for val in [0, -0.1]:
            with self.subTest(value=val):
                bad_policy = self.policy.copy()
                bad_policy["movingAwayToleranceM"] = val
                with self.assertRaises(ValueError):
                    classify_progress(
                        current_distance=10.0,
                        previous_distance=10.0,
                        baseline_distance=10.0,
                        window_elapsed_ms=100,
                        policy=bad_policy,
                    )

    def test_nonpositive_progress_window_ms_raises(self):
        """Non-positive progressWindowMs should raise ValueError."""
        for val in [0, -1]:
            with self.subTest(value=val):
                bad_policy = self.policy.copy()
                bad_policy["progressWindowMs"] = val
                with self.assertRaises(ValueError):
                    classify_progress(
                        current_distance=10.0,
                        previous_distance=10.0,
                        baseline_distance=10.0,
                        window_elapsed_ms=100,
                        policy=bad_policy,
                    )

    def test_nonpositive_minimum_progress_m_raises(self):
        """Non-positive minimumProgressM should raise ValueError."""
        for val in [0, -0.1]:
            with self.subTest(value=val):
                bad_policy = self.policy.copy()
                bad_policy["minimumProgressM"] = val
                with self.assertRaises(ValueError):
                    classify_progress(
                        current_distance=10.0,
                        previous_distance=10.0,
                        baseline_distance=10.0,
                        window_elapsed_ms=100,
                        policy=bad_policy,
                    )

    def test_nonfinite_policy_values_raise(self):
        """Non-finite policy values should raise ValueError."""
        for key in ["movingAwayToleranceM", "progressWindowMs", "minimumProgressM"]:
            for val in [float('inf'), float('-inf'), float('nan')]:
                with self.subTest(key=key, value=val):
                    bad_policy = self.policy.copy()
                    bad_policy[key] = val
                    with self.assertRaises(ValueError):
                        classify_progress(
                            current_distance=10.0,
                            previous_distance=10.0,
                            baseline_distance=10.0,
                            window_elapsed_ms=100,
                            policy=bad_policy,
                        )

    def test_bool_policy_values_raise(self):
        """Bool policy values should raise ValueError."""
        for key in ["movingAwayToleranceM", "progressWindowMs", "minimumProgressM"]:
            with self.subTest(key=key):
                bad_policy = self.policy.copy()
                bad_policy[key] = True
                with self.assertRaises(ValueError):
                    classify_progress(
                        current_distance=10.0,
                        previous_distance=10.0,
                        baseline_distance=10.0,
                        window_elapsed_ms=100,
                        policy=bad_policy,
                    )

    # --- Determinism and caller data unchanged tests ---
    def test_determinism(self):
        """Same inputs should always produce same output."""
        for _ in range(100):
            result = classify_progress(
                current_distance=10.5,
                previous_distance=10.0,
                baseline_distance=10.0,
                window_elapsed_ms=1000,
                policy=self.policy,
            )
            self.assertIsNone(result)

    def test_caller_data_unchanged(self):
        """Function should not mutate caller's policy dict."""
        original_policy = self.policy.copy()
        classify_progress(
            current_distance=10.0,
            previous_distance=10.0,
            baseline_distance=10.0,
            window_elapsed_ms=100,
            policy=self.policy,
        )
        self.assertEqual(self.policy, original_policy)

    def test_none_returned_when_conditions_not_met(self):
        """None should be returned when neither condition is met."""
        result = classify_progress(
            current_distance=9.9,
            previous_distance=10.0,
            baseline_distance=10.0,
            window_elapsed_ms=1000,
            policy=self.policy,
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()