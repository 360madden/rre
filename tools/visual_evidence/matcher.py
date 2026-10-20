"""Bounded screen-space patch diagnostics, not gameplay or camera calibration."""
from __future__ import annotations
import math
from PIL import Image

DEFAULTS = {"patchRadius": 6, "searchRadius": 12, "sampleStep": 2,
            "minVariance": 16.0, "maxMse": 100.0, "minDistinctGap": 5.0,
            "stationaryPixels": 1.0, "maxRadialResidual": 1.5}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def settings(value):
    require(isinstance(value, dict) and not (set(value) - set(DEFAULTS)), "Unknown matcher setting")
    result = DEFAULTS | value
    for key, low, high in (("patchRadius", 3, 12), ("searchRadius", 3, 16), ("sampleStep", 1, 3)):
        v = result[key]
        require(type(v) is int and low <= v <= high, "Invalid " + key)
    for key in set(DEFAULTS) - {"patchRadius", "searchRadius", "sampleStep"}:
        v = result[key]
        require(type(v) in (int, float) and math.isfinite(v) and 0 < v <= 65025, "Invalid " + key)
    require(result["stationaryPixels"] < result["searchRadius"], "Stationary threshold exceeds search")
    return result


def match_patch(before, after, point, policy):
    """Search a small integer translation; reject weak or ambiguous best matches."""
    x, y = point
    radius, search, step = (policy[k] for k in ("patchRadius", "searchRadius", "sampleStep"))
    margin = radius + search
    w, h = before.size
    require(margin <= x < w - margin and margin <= y < h - margin, "Patch/search outside image")
    a, b = before.load(), after.load()
    samples = [(dx, dy, a[x + dx, y + dy]) for dy in range(-radius, radius + 1, step)
               for dx in range(-radius, radius + 1, step)]
    mean = sum(v for _, _, v in samples) / len(samples)
    variance = sum((v - mean) ** 2 for _, _, v in samples) / len(samples)
    if variance < policy["minVariance"]:
        return {"center": point, "qualified": False, "reason": "textureless-patch", "variance": variance}
    candidates = []
    for sy in range(-search, search + 1):
        for sx in range(-search, search + 1):
            mse = sum((v - b[x + dx + sx, y + dy + sy]) ** 2 for dx, dy, v in samples) / len(samples)
            candidates.append((mse, sx, sy))
    candidates.sort()
    best, dx, dy = candidates[0]
    # Adjacent subpixel plateaus are not an independent competing landmark.
    alternate = min(v for v, sx, sy in candidates if max(abs(sx - dx), abs(sy - dy)) >= 3)
    gap = alternate - best
    reason = ("poor-match" if best > policy["maxMse"] else
              "ambiguous-match" if gap < policy["minDistinctGap"] else
              "search-boundary" if max(abs(dx), abs(dy)) == search else None)
    return {"center": point, "dx": dx, "dy": dy, "mse": best, "distinctGap": gap,
            "variance": variance, "qualified": reason is None, "reason": reason}


def compare(before: Image.Image, after: Image.Image, points, expectation, options=None):
    require(before.size == after.size, "Image dimensions differ")
    require(expectation in ("radial-in", "radial-out", "stationary"), "Unsupported visual predicate")
    require(isinstance(points, list) and 4 <= len(points) <= 8, "Require four to eight scene patches")
    require(all(isinstance(p, list) and len(p) == 2 and all(type(v) is int for v in p) for p in points),
            "Invalid patch center")
    require(len({tuple(p) for p in points}) == len(points), "Duplicate patch center")
    policy = settings({} if options is None else options)
    w, h = before.size
    require(min(p[0] for p in points) < w / 2 < max(p[0] for p in points) and
            max(p[1] for p in points) - min(p[1] for p in points) >= h * .15,
            "Patches lack spatial coverage")
    # Non-overlapping search neighborhoods avoid counting one texture repeatedly.
    separation = 2 * (policy["patchRadius"] + policy["searchRadius"])
    require(all(max(abs(a[0] - b[0]), abs(a[1] - b[1])) > separation
                for i, a in enumerate(points) for b in points[i + 1:]), "Overlapping patch searches")
    gray_a, gray_b = before.convert("L"), after.convert("L")
    rows = [match_patch(gray_a, gray_b, p, policy) for p in points]
    result = {"predicate": expectation, "status": "inconclusive", "reason": None,
              "policy": policy, "patches": rows, "scope": "selected screen-space texture patches only"}
    if not all(r["qualified"] for r in rows):
        result["reason"] = "unqualified-patch"
        return result
    magnitudes = [math.hypot(r["dx"], r["dy"]) for r in rows]
    stationary = all(v <= policy["stationaryPixels"] for v in magnitudes)
    if expectation == "stationary":
        result.update(status="passed" if stationary else "failed", reason="stationary" if stationary else "patches-moved")
        return result
    if stationary:
        result.update(status="failed", reason="no-measured-radial-motion")
        return result
    relative = [(r["center"][0] - w / 2, r["center"][1] - h / 2) for r in rows]
    scale = sum(x * r["dx"] + y * r["dy"] for (x, y), r in zip(relative, rows)) / sum(x*x + y*y for x, y in relative)
    residual = math.sqrt(sum((r["dx"] - scale*x)**2 + (r["dy"] - scale*y)**2
                             for (x, y), r in zip(relative, rows)) / len(rows))
    result.update(radialScaleDelta=scale, radialResidualPixels=residual)
    # The model is a diagnostic fit, not an estimate of camera distance.
    consistent = all((x*r["dx"] + y*r["dy"]) * scale > 0 for (x, y), r in zip(relative, rows))
    if residual > policy["maxRadialResidual"] or not consistent:
        result["reason"] = "motion-not-consistently-radial"
    else:
        correct = scale < 0 if expectation == "radial-in" else scale > 0
        result.update(status="passed" if correct else "failed",
                      reason="expected-radial-pattern" if correct else "opposite-radial-pattern")
    return result
