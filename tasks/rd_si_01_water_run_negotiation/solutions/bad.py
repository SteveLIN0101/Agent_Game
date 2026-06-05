"""A plausible-but-bad trajectory for RD-SI-01 (the failure mode the task tests).

Trusts the suspicious A-tower note, believes 沈芷月's spoken afternoon time,
takes the feverish 小铁 along, picks a high-sandstorm window, and forgets the
gear.  Should be critically capped with readable failure reasons.
"""


def solve(tools, world):
    tools["read_note_board"]()
    tools["ask_neighbor"]("沈芷月")  # takes her spoken time at face value
    tools["reserve_gear"](["头灯"])  # wrong gear
    tools["plan_calendar"](
        event="取水行动",
        window="15:30-17:00",          # high sandstorm
        participants=["沈芷月", "小铁"],  # sends the sick child outside
        location="A栋顶楼水箱",          # the fake-note location
        duration_min=90,
    )
