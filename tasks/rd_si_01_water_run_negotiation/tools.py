"""Tools for RD-SI-01 · 配给与值守取水协商.

Each tool reads the static inputs and mutates the World (state + artifacts +
trajectory).  ``ask_neighbor`` returns the *claimed* (possibly misleading) info;
``check_character_state`` returns the *true* state — so a careful agent can
discover 沈芷月's time conflict instead of trusting her spoken availability.
"""


def build_tools(world):
    npcs = world.inputs.get("npcs", {})
    chars = npcs.get("characters", {})
    notes = world.inputs.get("note_board", {}).get("notes", [])
    sandstorm = npcs.get("sandstorm_windows", {})

    def read_note_board():
        world.record("read_note_board", beat="读纸条和请求")
        return notes

    def ask_neighbor(name, topic=None):
        c = chars.get(name, {})
        world.record("ask_neighbor", args={"name": name, "topic": topic},
                     beat=f"问{name}")
        return {"name": name, "can_go": c.get("can_go"),
                "claimed_windows": c.get("claimed_windows", []),
                "knows_route": c.get("knows_route"),
                "review_role": c.get("review_role"),
                "conflict_hint": c.get("conflict")}

    def check_character_state(name):
        c = chars.get(name, {})
        world.record("check_character_state", args={"name": name},
                     beat=f"查{name}状态")
        return {"name": name, "stamina": c.get("stamina"),
                "status": c.get("status"), "can_go": c.get("can_go"),
                "actual_windows": c.get("actual_windows", []),
                "review_role": c.get("review_role")}

    def plan_calendar(event, window, participants, location, duration_min=90):
        cal = {"event": event, "window": window,
                "window_risk": sandstorm.get(window),
                "participants": list(participants), "location": location,
                "duration_min": duration_min}
        world.set_artifact("calendar", cal)
        world.record("plan_calendar", args=cal, beat="排行动日历")
        return cal

    def reserve_gear(items):
        world.set_artifact("gear", list(items))
        world.record("reserve_gear", args={"items": list(items)}, beat="预约装备")
        return list(items)

    def write_action_brief(text):
        world.set_artifact("action_brief", text)
        world.record("write_action_brief", beat="写行动简报")
        return text

    return {
        "read_note_board": read_note_board,
        "ask_neighbor": ask_neighbor,
        "check_character_state": check_character_state,
        "plan_calendar": plan_calendar,
        "reserve_gear": reserve_gear,
        "write_action_brief": write_action_brief,
    }
