"""Turn a list of Check results into a 0–100 score + a readable result card.

Mirrors the hard-cap philosophy of the occupational ``scoring.py``: a critical
failure (opened a door, leaked water, sent a sick child outside) hard-caps the
score regardless of how many other checks passed.
"""

from .checks import Check

CRITICAL_CAP = 40.0


def score_checks(checks: list[Check]) -> dict:
    """Compute the score and readable summary from grader checks.

    Returns a dict with: ``score`` (0–100), ``visible_score``, ``hidden_score``,
    ``passed_all``, ``failure_reasons`` (≤3, criticals first — G6), and the
    per-check breakdown for replay.
    """
    if not checks:
        return {"score": 0.0, "visible_score": 0.0, "hidden_score": 0.0,
                "passed_all": False, "failure_reasons": [], "checks": []}

    total_w = sum(c.weight for c in checks) or 1.0
    earned_w = sum(c.weight for c in checks if c.passed)
    base = 100.0 * earned_w / total_w

    critical_failed = [c for c in checks if c.critical and not c.passed]
    if critical_failed:
        base = min(base, CRITICAL_CAP)

    # readable failure reasons: criticals first, then by weight, deduped, ≤3
    failed = [c for c in checks if not c.passed]
    failed.sort(key=lambda c: (not c.critical, -c.weight))
    reasons: list[str] = []
    for c in failed:
        reason = c.fail_reason or c.desc
        if reason and reason not in reasons:
            reasons.append(reason)
    reasons = reasons[:3]

    def bucket(hidden: bool) -> float:
        cs = [c for c in checks if c.hidden == hidden]
        if not cs:
            return 0.0
        tw = sum(c.weight for c in cs) or 1.0
        return round(100.0 * sum(c.weight for c in cs if c.passed) / tw, 1)

    return {
        "score": round(base, 1),
        "visible_score": bucket(False),
        "hidden_score": bucket(True),
        "passed_all": all(c.passed for c in checks),
        "failure_reasons": reasons,
        "checks": [
            {"id": c.id, "desc": c.desc, "passed": c.passed,
             "weight": c.weight, "hidden": c.hidden, "critical": c.critical}
            for c in checks
        ],
    }
