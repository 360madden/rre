"""Progress classification for collision avoidance.

Pure synthetic API: measures sampled distance only, not real velocity.
No obstacle/terrain claims.
"""

import math


def classify_progress(
    *,
    current_distance: float,
    previous_distance: float,
    baseline_distance: float,
    window_elapsed_ms: int,
    policy: dict
) -> str | None:
    """Classify progress toward a goal based on sampled distances.

    Args:
        current_distance: Current distance to goal (synthetic XZ horizontal, Y vertical, ms time).
        previous_distance: Previous sampled distance to goal.
        baseline_distance: Distance at start of progress window.
        window_elapsed_ms: Elapsed time in progress window (milliseconds).
        policy: Configuration dict with keys:
            - movingAwayToleranceM (float): Threshold for moving-away detection (default 0.75).
            - progressWindowMs (int): Progress window duration in ms (default 1500).
            - minimumProgressM (float): Minimum required progress in window (default 0.25).

    Returns:
        "moving-away" if moving away from goal,
        "no-progress" if insufficient progress in window,
        None otherwise.

    Raises:
        ValueError: If inputs are invalid (non-finite, negative, wrong types, etc.).
    """
    # Validate numeric finite nonnegative distances
    for name, value in [
        ("current_distance", current_distance),
        ("previous_distance", previous_distance),
        ("baseline_distance", baseline_distance),
    ]:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{name} must be a finite nonnegative number, got {type(value).__name__}")
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite, got {value}")
        if value < 0:
            raise ValueError(f"{name} must be nonnegative, got {value}")

    # Validate window_elapsed_ms: nonnegative int, not bool
    if not isinstance(window_elapsed_ms, int) or isinstance(window_elapsed_ms, bool):
        raise ValueError(f"window_elapsed_ms must be a nonnegative int, got {type(window_elapsed_ms).__name__}")
    if window_elapsed_ms < 0:
        raise ValueError(f"window_elapsed_ms must be nonnegative, got {window_elapsed_ms}")

    # Validate policy
    if not isinstance(policy, dict):
        raise ValueError("policy must be a dict")

    required_keys = ["movingAwayToleranceM", "progressWindowMs", "minimumProgressM"]
    for key in required_keys:
        if key not in policy:
            raise ValueError(f"policy missing required key: {key}")

    moving_away_tolerance = policy["movingAwayToleranceM"]
    progress_window_ms = policy["progressWindowMs"]
    minimum_progress_m = policy["minimumProgressM"]

    for name, value in [
        ("movingAwayToleranceM", moving_away_tolerance),
        ("progressWindowMs", progress_window_ms),
        ("minimumProgressM", minimum_progress_m),
    ]:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"policy['{name}'] must be a number, got {type(value).__name__}")
        if not math.isfinite(value):
            raise ValueError(f"policy['{name}'] must be finite, got {value}")

    if moving_away_tolerance <= 0:
        raise ValueError(f"policy['movingAwayToleranceM'] must be positive, got {moving_away_tolerance}")
    if progress_window_ms <= 0:
        raise ValueError(f"policy['progressWindowMs'] must be positive, got {progress_window_ms}")
    if minimum_progress_m <= 0:
        raise ValueError(f"policy['minimumProgressM'] must be positive, got {minimum_progress_m}")

    # Priority 1: moving-away detection
    if current_distance - previous_distance > moving_away_tolerance:
        return "moving-away"

    # Priority 2: no-progress detection
    if window_elapsed_ms >= progress_window_ms:
        progress_made = baseline_distance - current_distance
        if progress_made < minimum_progress_m:
            return "no-progress"

    return None


# Default policy for convenience
DEFAULT_POLICY = {
    "movingAwayToleranceM": 0.75,
    "progressWindowMs": 1500,
    "minimumProgressM": 0.25,
}