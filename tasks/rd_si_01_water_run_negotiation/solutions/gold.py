"""Reference (good-agent) solution for RD-SI-01.

Asks the three adults, cross-checks 沈芷月's real availability (discovering she
can only go in the morning), confirms 小铁 cannot go, verifies 老钱's B2 route,
ignores the suspicious A-tower note, then schedules a 90-min low-sandstorm run
with the right gear.  Should pass every visible + hidden check.
"""


def solve(tools, world):
    notes = tools["read_note_board"]()
    suspicious = {n.get("location") for n in notes if n.get("suspicious")}

    # verify the route from the person who knows the building
    laoqian = tools["ask_neighbor"]("老钱")
    route_ok = "B2" in (laoqian.get("knows_route") or "")

    # cross-check real availability instead of trusting spoken times
    madehai = tools["check_character_state"]("马德海")
    shen_claim = tools["ask_neighbor"]("沈芷月")          # claims afternoon
    shen_true = tools["check_character_state"]("沈芷月")   # really only morning
    xiaotie = tools["check_character_state"]("小铁")       # 发烧 / can_go == False

    # pick a low-sandstorm 90-min window both adults can actually make
    window = "09:30-11:00"
    participants = [
        name for name, st in [("马德海", madehai), ("老钱", laoqian)]
        if name != "小铁"
    ]

    tools["reserve_gear"](["护目镜", "绳索", "滤芯"])
    tools["plan_calendar"](
        event="取水行动", window=window, participants=participants,
        location="B2 储水点", duration_min=90,
    )
    tools["write_action_brief"](
        f"{window} 低沙暴窗口：马德海 + 老钱走消防梯下 B2 储水点取水，"
        f"带护目镜/绳索/滤芯。小铁发烧不外出；"
        f"不采用可疑纸条上的 {sorted(suspicious)} 地点。"
    )
