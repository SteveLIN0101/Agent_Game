#!/usr/bin/env python3
"""Generate the real题面数据 for RD-CI-03 (3×3 escape-map jigsaw).

Produces, deterministically:
  inputs/fragments/frag_00.png .. frag_14.png   (9 correct rotated tiles + 6 distractors)
  inputs/manifest.json                          (agent-facing: ids + files + start/end, NO answers)
  inputs/source_map.png                         (the intact map, for reference/debug)
  expected/solution.json                        (grader truth: correct cell+rotation, distractors,
                                                 impassable 红沙 cells, start/end, a valid route)
"""
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / "tasks" / "rd_ci_03_escape_map_jigsaw_3x3"
FRAG_DIR = TASK / "inputs" / "fragments"
TILE = 100
N = 3

# pastel color per cell 0..8
COLORS = [
    (236, 201, 196), (201, 228, 222), (210, 214, 240), (243, 230, 196),
    (210, 235, 205), (228, 208, 235), (200, 222, 240), (240, 222, 200),
    (214, 235, 230),
]
IMPASSABLE = [2, 4]          # 红沙 (red-sand) cells — not passable
START, END = 0, 8
ROUTE = [0, 3, 6, 7, 8]      # a valid connected path avoiding {2,4}
# 5 of the 9 correct tiles are stored rotated; agent must report the rotation
APPLIED_ROT = {0: 0, 1: 90, 2: 0, 3: 180, 4: 0, 5: 270, 6: 90, 7: 0, 8: 180}


def _font(size):
    try:
        # TrueType so the printed digit is OCR-readable; prefer a serif face so
        # the digit "1" has a base/flag and is not misread as "4".
        for p in ("/System/Library/Fonts/Supplemental/Times New Roman.ttf",
                  "/System/Library/Fonts/Supplemental/Georgia.ttf",
                  "/System/Library/Fonts/Supplemental/Courier New.ttf",
                  "/System/Library/Fonts/Supplemental/Arial.ttf",
                  "/Library/Fonts/Arial.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"):
            if Path(p).exists():
                return ImageFont.truetype(p, size)
        return ImageFont.load_default(size=size)
    except (TypeError, OSError):
        return ImageFont.load_default()


def make_cell(idx: int) -> Image.Image:
    # White (passable) / light-red (red-sand) background → high digit contrast for
    # OCR; dominant colour still distinguishes red-sand. A solid square in the
    # UPRIGHT top-left corner is an orientation marker (rotation read geometrically,
    # not from the rotationally-ambiguous digit).
    bg = (244, 198, 192) if idx in IMPASSABLE else (250, 250, 250)
    img = Image.new("RGB", (TILE, TILE), bg)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, TILE - 1, TILE - 1], outline=(70, 80, 100), width=3)
    d.rectangle([5, 5, 23, 23], fill=(15, 15, 15))          # orientation marker
    d.text((TILE // 2, TILE // 2 + 4), str(idx), fill=(8, 8, 8), font=_font(60),
           anchor="mm", stroke_width=2, stroke_fill=(8, 8, 8))   # big bold digit
    return img


def make_distractor(seed_img: Image.Image, kind: int, rng: random.Random) -> Image.Image:
    # Grey noisy/striped tile with NO centered glyph and NO orientation marker →
    # OCR finds no clean digit and the dominant colour is grey (not red), so the
    # agent can reject it as a distractor.
    img = Image.new("RGB", (TILE, TILE), (rng.randint(80, 130),) * 3)
    d = ImageDraw.Draw(img)
    for _ in range(160):
        x, y = rng.randint(0, TILE), rng.randint(0, TILE)
        d.point((x, y), fill=(rng.randint(0, 255),) * 3)
    for k in range(0, TILE, 12):                       # diagonal stripes
        d.line([(k, 0), (0, k)], fill=(rng.randint(40, 90),) * 3, width=2)
    return img


def main() -> int:
    rng = random.Random(2026)
    FRAG_DIR.mkdir(parents=True, exist_ok=True)
    (TASK / "expected").mkdir(parents=True, exist_ok=True)

    # 1) intact source map
    source = Image.new("RGB", (TILE * N, TILE * N), (245, 245, 245))
    cells = {}
    for idx in range(9):
        c = make_cell(idx)
        cells[idx] = c
        r, col = divmod(idx, N)
        source.paste(c, (col * TILE, r * TILE))
    source.save(TASK / "inputs" / "source_map.png")

    # 2) the 9 correct fragments, each rotated by APPLIED_ROT
    items = []  # (kind, payload) where kind in {"correct","distractor"}
    for idx in range(9):
        rot = APPLIED_ROT[idx]
        frag = cells[idx].rotate(-rot, expand=False)  # clockwise by `rot`
        items.append(("correct", {"cell": idx, "rotation": rot, "img": frag}))

    # 3) six distractors
    for k in range(6):
        items.append(("distractor", {"img": make_distractor(source, k, rng)}))

    # 4) shuffle into frag_00..frag_14 and write
    order = list(range(15))
    rng.shuffle(order)
    manifest_frags = []
    correct = {}
    distractors = []
    for file_i, item_i in enumerate(order):
        kind, payload = items[item_i]
        fid = f"frag_{file_i:02d}"
        fname = f"fragments/{fid}.png"
        payload["img"].save(FRAG_DIR / f"{fid}.png")
        manifest_frags.append({"id": fid, "file": fname})
        if kind == "correct":
            correct[fid] = {"cell": payload["cell"], "rotation": payload["rotation"]}
        else:
            distractors.append(fid)

    manifest = {
        "grid_size": "3x3", "tile_px": TILE,
        "fragments": manifest_frags,
        "start_cell": START, "end_cell": END,
        "note": "15 张碎片里有 6 张是偏移/噪声干扰，请拼出 3×3 楼道图并标出绕开红沙(沙)的路线。",
    }
    (TASK / "inputs" / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    solution = {
        "grid_size": "3x3", "correct": correct, "distractors": sorted(distractors),
        "impassable_cells": IMPASSABLE, "start": START, "end": END, "route": ROUTE,
    }
    (TASK / "expected").joinpath("solution.json").write_text(
        json.dumps(solution, ensure_ascii=False, indent=2), encoding="utf-8")

    assert len(correct) == 9 and len(distractors) == 6
    print(f"wrote 15 fragments + manifest + solution to {TASK}")
    print(f"  correct: {len(correct)}  distractors: {len(distractors)}  route: {ROUTE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
