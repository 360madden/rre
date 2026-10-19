import unittest
import math
import sys
sys.path.insert(0, 'tools/agents/c2m')

from m4a_geometry import horizontal_distance, vertical_difference, classify_geometry


class TestHorizontalDistance(unittest.TestCase):
    def test_basic(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 3, 'y': 0, 'z': 4}
        self.assertEqual(horizontal_distance(player, target), 5.0)

    def test_same_position(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 0, 'y': 0, 'z': 0}
        self.assertEqual(horizontal_distance(player, target), 0.0)

    def test_negative_coords(self):
        player = {'x': -5, 'y': 0, 'z': -5}
        target = {'x': 5, 'y': 0, 'z': 5}
        self.assertAlmostEqual(horizontal_distance(player, target), math.hypot(10, 10))

    def test_input_unchanged(self):
        player = {'x': 1, 'y': 2, 'z': 3}
        target = {'x': 4, 'y': 5, 'z': 6}
        p_copy = dict(player)
        t_copy = dict(target)
        horizontal_distance(player, target)
        self.assertEqual(player, p_copy)
        self.assertEqual(target, t_copy)


class TestVerticalDifference(unittest.TestCase):
    def test_basic(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 0, 'y': 5, 'z': 0}
        self.assertEqual(vertical_difference(player, target), 5.0)

    def test_same_height(self):
        player = {'x': 0, 'y': 10, 'z': 0}
        target = {'x': 5, 'y': 10, 'z': 5}
        self.assertEqual(vertical_difference(player, target), 0.0)

    def test_negative_difference(self):
        player = {'x': 0, 'y': 10, 'z': 0}
        target = {'x': 0, 'y': 5, 'z': 0}
        self.assertEqual(vertical_difference(player, target), 5.0)

    def test_input_unchanged(self):
        player = {'x': 1, 'y': 2, 'z': 3}
        target = {'x': 4, 'y': 5, 'z': 6}
        p_copy = dict(player)
        t_copy = dict(target)
        vertical_difference(player, target)
        self.assertEqual(player, p_copy)
        self.assertEqual(target, t_copy)


class TestClassifyGeometry(unittest.TestCase):
    def setUp(self):
        self.policy = {'arrivalRadiusM': 1.5, 'maximumVerticalDifferenceM': 2.0}

    def test_arrived(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 1, 'y': 0, 'z': 0}
        result = classify_geometry(player, target, self.policy)
        self.assertEqual(result['state'], 'arrived')
        self.assertEqual(result['distanceXZ'], 1.0)
        self.assertEqual(result['heightDelta'], 0.0)

    def test_approach_intent(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 10, 'y': 0, 'z': 0}
        result = classify_geometry(player, target, self.policy)
        self.assertEqual(result['state'], 'approach-intent')
        self.assertEqual(result['distanceXZ'], 10.0)
        self.assertEqual(result['heightDelta'], 0.0)

    def test_height_unsafe(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 1, 'y': 3, 'z': 0}
        result = classify_geometry(player, target, self.policy)
        self.assertEqual(result['state'], 'height-unsafe')
        self.assertEqual(result['distanceXZ'], 1.0)
        self.assertEqual(result['heightDelta'], 3.0)

    def test_height_unsafe_priority_over_arrival(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 1, 'y': 3, 'z': 0}
        result = classify_geometry(player, target, self.policy)
        self.assertEqual(result['state'], 'height-unsafe')

    def test_boundary_arrival_radius(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 1.5, 'y': 0, 'z': 0}
        result = classify_geometry(player, target, self.policy)
        self.assertEqual(result['state'], 'arrived')

    def test_boundary_vertical_safe(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 0, 'y': 2.0, 'z': 0}
        result = classify_geometry(player, target, self.policy)
        self.assertEqual(result['state'], 'arrived')

    def test_boundary_vertical_unsafe(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 0, 'y': 2.0001, 'z': 0}
        result = classify_geometry(player, target, self.policy)
        self.assertEqual(result['state'], 'height-unsafe')

    def test_repeat_evaluations(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 10, 'y': 0, 'z': 0}
        for _ in range(10):
            result = classify_geometry(player, target, self.policy)
            self.assertEqual(result['state'], 'approach-intent')
            self.assertEqual(result['distanceXZ'], 10.0)

    def test_input_unchanged(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 10, 'y': 0, 'z': 0}
        policy = dict(self.policy)
        p_copy = dict(player)
        t_copy = dict(target)
        pl_copy = dict(policy)
        classify_geometry(player, target, policy)
        self.assertEqual(player, p_copy)
        self.assertEqual(target, t_copy)
        self.assertEqual(policy, pl_copy)


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.policy = {'arrivalRadiusM': 1.5, 'maximumVerticalDifferenceM': 2.0}

    def test_missing_x_key(self):
        player = {'y': 0, 'z': 0}
        target = {'x': 1, 'y': 0, 'z': 0}
        with self.assertRaises(ValueError):
            horizontal_distance(player, target)

    def test_missing_y_key(self):
        player = {'x': 0, 'z': 0}
        target = {'x': 1, 'y': 0, 'z': 0}
        with self.assertRaises(ValueError):
            vertical_difference(player, target)

    def test_missing_z_key(self):
        player = {'x': 0, 'y': 0}
        target = {'x': 1, 'y': 0, 'z': 0}
        with self.assertRaises(ValueError):
            classify_geometry(player, target, self.policy)

    def test_nan_value(self):
        player = {'x': float('nan'), 'y': 0, 'z': 0}
        target = {'x': 1, 'y': 0, 'z': 0}
        with self.assertRaises(ValueError):
            horizontal_distance(player, target)

    def test_inf_value(self):
        player = {'x': float('inf'), 'y': 0, 'z': 0}
        target = {'x': 1, 'y': 0, 'z': 0}
        with self.assertRaises(ValueError):
            horizontal_distance(player, target)

    def test_bool_value(self):
        player = {'x': True, 'y': 0, 'z': 0}
        target = {'x': 1, 'y': 0, 'z': 0}
        with self.assertRaises(ValueError):
            horizontal_distance(player, target)

    def test_string_value(self):
        player = {'x': '0', 'y': 0, 'z': 0}
        target = {'x': 1, 'y': 0, 'z': 0}
        with self.assertRaises(ValueError):
            horizontal_distance(player, target)

    def test_policy_missing_keys(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 1, 'y': 0, 'z': 0}
        policy = {'arrivalRadiusM': 1.5}
        with self.assertRaises(ValueError):
            classify_geometry(player, target, policy)

    def test_policy_negative(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 1, 'y': 0, 'z': 0}
        policy = {'arrivalRadiusM': -1, 'maximumVerticalDifferenceM': 2.0}
        with self.assertRaises(ValueError):
            classify_geometry(player, target, policy)

    def test_policy_zero(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 1, 'y': 0, 'z': 0}
        policy = {'arrivalRadiusM': 0, 'maximumVerticalDifferenceM': 2.0}
        with self.assertRaises(ValueError):
            classify_geometry(player, target, policy)

    def test_policy_nan(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 1, 'y': 0, 'z': 0}
        policy = {'arrivalRadiusM': float('nan'), 'maximumVerticalDifferenceM': 2.0}
        with self.assertRaises(ValueError):
            classify_geometry(player, target, policy)

    def test_policy_bool(self):
        player = {'x': 0, 'y': 0, 'z': 0}
        target = {'x': 1, 'y': 0, 'z': 0}
        policy = {'arrivalRadiusM': True, 'maximumVerticalDifferenceM': 2.0}
        with self.assertRaises(ValueError):
            classify_geometry(player, target, policy)

    def test_not_dict_input(self):
        with self.assertRaises(ValueError):
            horizontal_distance("not a dict", {'x': 1, 'y': 0, 'z': 0})
        with self.assertRaises(ValueError):
            vertical_difference({'x': 0, 'y': 0, 'z': 0}, "not a dict")
        with self.assertRaises(ValueError):
            classify_geometry({'x': 0, 'y': 0, 'z': 0}, {'x': 1, 'y': 0, 'z': 0}, "not a dict")


if __name__ == '__main__':
    unittest.main()