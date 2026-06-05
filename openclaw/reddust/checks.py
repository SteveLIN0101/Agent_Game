"""A single grader assertion for a Red Dust task."""

from dataclasses import dataclass


@dataclass
class Check:
    """One success/failure assertion evaluated against the final World.

    Attributes:
        id: stable identifier (e.g. ``"excludes_xiaotie"``).
        desc: human-readable description (shown to the audience).
        passed: whether the assertion held.
        weight: relative contribution to the score (default 1.0).
        hidden: if True, this is a hidden-grader check (not in the public
            ``success_checks`` list shown to the agent).
        critical: if True, failing it hard-caps the score (e.g. opened a door,
            leaked water, sent 小铁 outside).
        fail_reason: short, human-readable reason used in the result card when
            the check fails (G6: failures compress to ≤3 readable reasons).
    """

    id: str
    desc: str
    passed: bool
    weight: float = 1.0
    hidden: bool = False
    critical: bool = False
    fail_reason: str = ""
