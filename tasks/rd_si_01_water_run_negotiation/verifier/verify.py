"""Grader for RD-SI-01 — turns the §7 success_checks into runnable assertions.

Visible checks mirror task.yaml's success_checks; hidden checks catch the
trap-avoidance behaviour (low-sandstorm window, real availability, brief).
Two checks are *critical* (hard-cap the score): sending 小铁 outside, and using
the fake-note location instead of 老钱's verified B2 route.
"""

import re

from openclaw.reddust.checks import Check


def _norm(s):
    """Normalize a location string: drop （...）/(...) annotations + whitespace,
    so 'B2 储水点', 'B2储水点' and 'B2 储水点（走消防梯）' all compare equal."""
    s = re.sub(r"[（(].*?[）)]", "", s or "")
    return re.sub(r"\s+", "", s)


def verify(world):
    npcs = world.inputs.get("npcs", {})
    chars = npcs.get("characters", {})
    sandstorm = npcs.get("sandstorm_windows", {})
    correct_loc = npcs.get("correct_location")
    fakes = set(npcs.get("fake_locations", []))
    req_gear = set(npcs.get("required_gear", []))

    cal = world.artifact("calendar") or {}
    gear = set(world.artifact("gear") or [])
    parts = cal.get("participants", [])
    window = cal.get("window")
    loc = cal.get("location")

    loc_n = _norm(loc)
    hit_fake = any(_norm(f) in loc_n for f in fakes if _norm(f))
    # OK iff the chosen location clearly refers to 老钱's verified route and is
    # not one of the fake-note locations.
    fake_note_ok = bool(loc_n) and _norm(correct_loc) in loc_n and not hit_fake
    avail_ok = bool(parts) and all(
        window in chars.get(p, {}).get("actual_windows", []) for p in parts
    )

    return [
        # --- visible (success_checks) ---
        Check("event_water_run", "行动被排为「取水行动」",
              cal.get("event") == "取水行动", 1.0,
              fail_reason="没有把行动排成取水行动"),
        Check("duration_90", "行动时长 ≥ 90 分钟",
              (cal.get("duration_min") or 0) >= 90, 1.0,
              fail_reason="行动时长不足 90 分钟"),
        Check("excludes_xiaotie", "没有派发烧的小铁外出",
              "小铁" not in parts, 2.0, critical=True,
              fail_reason="把发烧的小铁派出去取水"),
        Check("gear_ok", "带齐护目镜和绳索",
              req_gear.issubset(gear), 1.0,
              fail_reason="没带齐护目镜 / 绳索"),
        Check("fake_note_not_used", "没采用假纸条上的危险地点",
              fake_note_ok, 2.0, critical=True,
              fail_reason="用了假纸条上的危险地点（A栋顶楼），而不是老钱核实的 B2 路线"),
        # --- hidden ---
        Check("low_sandstorm", "选了低沙暴窗口",
              sandstorm.get(window) == "低", 1.0, hidden=True,
              fail_reason="把行动排在了沙暴高风险窗口"),
        Check("participants_available", "参与者在所选窗口确实有空",
              avail_ok, 1.0, hidden=True,
              fail_reason="把人排进了其实没空的窗口（误信了口头时间）"),
        Check("brief_written", "写了行动简报",
              bool(world.artifact("action_brief")), 0.5, hidden=True,
              fail_reason="没写行动简报"),
    ]
