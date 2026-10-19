"""Early guard checks for follow lane M4A."""

from typing import Any, Dict, Optional


TERMINAL_STATES = frozenset({
    'arrived',
    'cancelled',
    'target-unavailable',
    'target-changed',
    'scene-changed',
    'telemetry-stale',
    'invalid-sample',
    'unqualified-source',
    'height-unsafe',
    'no-progress',
    'moving-away',
})


def _is_finite_number(value: Any) -> bool:
    """Check if value is a finite number (not bool, not NaN, not inf)."""
    if isinstance(value, bool):
        return False
    if not isinstance(value, (int, float)):
        return False
    if isinstance(value, float):
        return value == value and value != float('inf') and value != float('-inf')
    return True


def _validate_position(pos: Any, name: str) -> bool:
    """Validate a position object with flat x, y, z coordinates."""
    if not isinstance(pos, dict):
        return False
    required_keys = {'x', 'y', 'z'}
    if set(pos.keys()) != required_keys:
        return False
    for key in required_keys:
        if not _is_finite_number(pos[key]):
            return False
    return True


def _validate_target_coords(target: dict) -> bool:
    """Validate target x, y, z coordinates (target also has 'id')."""
    required_keys = {'x', 'y', 'z'}
    for key in required_keys:
        if key not in target:
            return False
        if not _is_finite_number(target[key]):
            return False
    return True


def _validate_sample(sample: Any) -> bool:
    """Validate the sample structure and types."""
    if not isinstance(sample, dict):
        return False

    required_fields = {'tMs', 'sceneId', 'player', 'target', 'cancelRequested'}
    if set(sample.keys()) != required_fields:
        return False

    t_ms = sample['tMs']
    if isinstance(t_ms, bool) or not isinstance(t_ms, int) or t_ms < 0:
        return False

    if not isinstance(sample['sceneId'], str) or not sample['sceneId']:
        return False

    player = sample['player']
    if not _validate_position(player, 'player'):
        return False

    target = sample['target']
    if target is not None:
        if not isinstance(target, dict):
            return False
        if 'id' not in target:
            return False
        if not isinstance(target['id'], str):
            return False
        if not _validate_target_coords(target):
            return False

    if not isinstance(sample['cancelRequested'], bool):
        return False

    return True


def early_guard(
    sample: Any,
    *,
    initial_scene_id: Optional[str],
    initial_target_id: Optional[str],
    previous_t_ms: Optional[int],
    terminal_state: Optional[str],
    policy: Dict[str, Any],
    source_kind: str = 'synthetic-fixture',
) -> Optional[str]:
    """
    Early guard checks for follow lane.

    Returns a terminal state string if a guard triggers, None otherwise.
    """
    if terminal_state in TERMINAL_STATES:
        return terminal_state

    if source_kind != 'synthetic-fixture':
        return 'unqualified-source'

    if not _validate_sample(sample):
        return 'invalid-sample'

    if previous_t_ms is not None:
        if not isinstance(previous_t_ms, int) or isinstance(previous_t_ms, bool) or previous_t_ms < 0:
            return 'invalid-sample'
        if sample['tMs'] <= previous_t_ms:
            return 'invalid-sample'

    if sample['cancelRequested']:
        return 'cancelled'

    target = sample['target']
    if target is None or not target.get('id'):
        return 'target-unavailable'

    if initial_target_id is not None and target['id'] != initial_target_id:
        return 'target-changed'

    if initial_scene_id is not None and sample['sceneId'] != initial_scene_id:
        return 'scene-changed'

    if previous_t_ms is not None:
        stale_threshold = policy.get('staleAfterGapMs', 1200)
        if not isinstance(stale_threshold, int) or stale_threshold <= 0:
            raise ValueError("policy['staleAfterGapMs'] must be a positive integer")
        gap = sample['tMs'] - previous_t_ms
        if gap > stale_threshold:
            return 'telemetry-stale'

    return None