import math


def horizontal_distance(player, target):
    if not isinstance(player, dict) or not isinstance(target, dict):
        raise ValueError("Player and target must be dictionaries")
    required_keys = {'x', 'y', 'z'}
    if not required_keys.issubset(player.keys()) or not required_keys.issubset(target.keys()):
        raise ValueError("Position must contain x, y, z keys")
    for pos in (player, target):
        for key in required_keys:
            val = pos[key]
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                raise ValueError("Position coordinates must be numeric (int/float), not bool")
            if not math.isfinite(val):
                raise ValueError("Position coordinates must be finite numbers")
    return math.hypot(target['x'] - player['x'], target['z'] - player['z'])


def vertical_difference(player, target):
    if not isinstance(player, dict) or not isinstance(target, dict):
        raise ValueError("Player and target must be dictionaries")
    required_keys = {'x', 'y', 'z'}
    if not required_keys.issubset(player.keys()) or not required_keys.issubset(target.keys()):
        raise ValueError("Position must contain x, y, z keys")
    for pos in (player, target):
        for key in required_keys:
            val = pos[key]
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                raise ValueError("Position coordinates must be numeric (int/float), not bool")
            if not math.isfinite(val):
                raise ValueError("Position coordinates must be finite numbers")
    return abs(target['y'] - player['y'])


def classify_geometry(player, target, policy):
    if not isinstance(player, dict) or not isinstance(target, dict) or not isinstance(policy, dict):
        raise ValueError("Player, target, and policy must be dictionaries")
    required_keys = {'x', 'y', 'z'}
    if not required_keys.issubset(player.keys()) or not required_keys.issubset(target.keys()):
        raise ValueError("Position must contain x, y, z keys")
    for pos in (player, target):
        for key in required_keys:
            val = pos[key]
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                raise ValueError("Position coordinates must be numeric (int/float), not bool")
            if not math.isfinite(val):
                raise ValueError("Position coordinates must be finite numbers")
    required_policy_keys = {'arrivalRadiusM', 'maximumVerticalDifferenceM'}
    if not required_policy_keys.issubset(policy.keys()):
        raise ValueError("Policy must contain arrivalRadiusM and maximumVerticalDifferenceM")
    for key in required_policy_keys:
        val = policy[key]
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            raise ValueError("Policy thresholds must be numeric (int/float), not bool")
        if not math.isfinite(val):
            raise ValueError("Policy thresholds must be finite numbers")
        if val < 0:
            raise ValueError("Policy thresholds must be nonnegative")
        if val <= 0:
            raise ValueError("Policy thresholds must be > 0")

    dist_xz = horizontal_distance(player, target)
    height_delta = vertical_difference(player, target)

    if height_delta > policy['maximumVerticalDifferenceM']:
        state = 'height-unsafe'
    elif dist_xz <= policy['arrivalRadiusM']:
        state = 'arrived'
    else:
        state = 'approach-intent'

    return {
        'state': state,
        'distanceXZ': dist_xz,
        'heightDelta': height_delta
    }