"""Perception-only solution for RD-CI-03 — proves the task is solvable by a
*text* agent, WITHOUT the answer key.

It uses only the perception bridge: ``perceive_fragment`` returns each tile's
digit + rotation (OCR) and whether it's red-sand (dominant colour). Tiles whose
digit is None are the distractors. Red-sand cells are obstacles; the route is a
BFS shortest path from start to end avoiding them.
"""
from collections import deque


def solve(tools, world):
    frags = tools["load_fragments"]()

    mapping, impassable = {}, set()
    for fr in frags:
        info = tools["perceive_fragment"](fr["id"])
        if info["digit"] is None:
            continue                         # distractor — reject
        cell = int(info["digit"])
        mapping[cell] = {"fragment": fr["id"], "rotation": info["rotation"]}
        if info["red_sand"]:
            impassable.add(cell)

    for cell, v in mapping.items():
        if v["rotation"]:
            tools["rotate_piece"](v["fragment"], v["rotation"])
    tools["assemble_grid"](mapping)

    man = world.inputs["manifest"]
    start, end = man["start_cell"], man["end_cell"]

    def neighbors(c):
        r, col = divmod(c, 3)
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, col + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                yield nr * 3 + nc

    prev = {start: None}
    q = deque([start])
    while q:
        c = q.popleft()
        if c == end:
            break
        for n in neighbors(c):
            if n not in prev and n not in impassable:
                prev[n] = c
                q.append(n)

    route = []
    if end in prev:
        c = end
        while c is not None:
            route.append(c)
            c = prev[c]
        route.reverse()
    tools["mark_route"](route)
    tools["export_image"]()
