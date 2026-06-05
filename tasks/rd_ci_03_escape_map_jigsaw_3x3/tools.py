"""Tools for RD-CI-03 · 3×3 逃生地图拼回去.

Operates on the real fragment PNGs in inputs/fragments/.  ``compare_edges`` is a
genuine pixel-similarity signal an agent can use to match pieces; the assembly /
route / export tools record the agent's reconstruction into the World.
"""
import tempfile
from pathlib import Path

from PIL import Image

from openclaw.reddust import perception


def build_tools(world):
    idir = Path(world.inputs["_dir"])
    manifest = world.inputs.get("manifest", {})
    frags = manifest.get("fragments", [])

    def _img(frag_id):
        rec = next((f for f in frags if f["id"] == frag_id), None)
        if not rec:
            raise KeyError(frag_id)
        return Image.open(idir / rec["file"]).convert("RGB")

    def load_fragments():
        '''list the 15 fragments [{id,file}] to perceive and assemble.'''
        world.record("load_fragments", beat="看碎片")
        return frags

    def perceive_fragment(frag_id):
        '''returns {digit, rotation, red_sand}: the tile's printed cell number (0-8; None ⇒ distractor), its rotation (0/90/180/270), and whether it is red-sand.'''
        img = _img(frag_id)
        digit, rot = perception.read_tile(img)
        dom = perception.describe_image(img)["dominant_rgb"]
        red_sand = dom[0] > dom[1] + 25 and dom[0] > dom[2] + 25
        world.record("perceive_fragment", args={"id": frag_id}, beat="识别碎片")
        return {"digit": digit, "rotation": rot,
                "dominant_rgb": dom, "red_sand": red_sand}

    def compare_edges(id_a, side_a, id_b, side_b):
        '''edge similarity 0-1 between two fragments; side = top|bottom|left|right.'''
        def strip(img, side):
            w, h = img.size
            box = {"top": (0, 0, w, 2), "bottom": (0, h - 2, w, h),
                   "left": (0, 0, 2, h), "right": (w - 2, 0, w, h)}[side]
            return img.crop(box).tobytes()          # raw RGB bytes
        a, b = strip(_img(id_a), side_a), strip(_img(id_b), side_b)
        n = min(len(a), len(b)) or 1
        diff = sum(abs(a[i] - b[i]) for i in range(n))
        sim = 1.0 - diff / (n * 255)
        world.record("compare_edges",
                     args={"a": id_a, "b": id_b}, beat="比对边缘")
        return round(sim, 4)

    def rotate_piece(frag_id, degrees):
        '''note that fragment <frag_id> needs rotating by <degrees> (0/90/180/270) — optional; assemble_grid also takes rotation.'''
        rots = world.state.setdefault("rotations", {})
        rots[frag_id] = degrees
        world.record("rotate_piece",
                     args={"id": frag_id, "deg": degrees}, beat="旋转碎片")

    def assemble_grid(mapping):
        '''mapping = {"0":{"fragment":"frag_XX","rotation":0|90|180|270}, ... "8":{...}} — all 9 cells, row-major (0=top-left..8=bottom-right), exclude the 6 distractors.'''
        norm = {int(c): v for c, v in mapping.items()}
        world.set_artifact("assembly", norm)
        world.record("assemble_grid",
                     args={"cells": sorted(norm)}, beat="拼出楼道图")
        return norm

    def mark_route(cells):
        '''cells = [start..end] list of cell indices 0-8 forming a connected path that avoids the red-sand cells, e.g. [0,3,6,7,8].'''
        route = [int(c) for c in cells]
        world.set_artifact("route", route)
        world.record("mark_route", args={"route": route}, beat="标出可走路线")
        return route

    def export_image():
        '''render the assembled grid to an image — call once after assemble_grid.'''
        assembly = world.artifact("assembly") or {}
        if assembly:
            tile = manifest.get("tile_px", 100)
            canvas = Image.new("RGB", (tile * 3, tile * 3), (245, 245, 245))
            for cell, v in assembly.items():
                try:
                    img = _img(v["fragment"]).rotate(int(v.get("rotation", 0)),
                                                      expand=False)
                except KeyError:
                    continue
                r, col = divmod(int(cell), 3)
                canvas.paste(img, (col * tile, r * tile))
            out = Path(tempfile.gettempdir()) / "rd_ci03_assembled.png"
            canvas.save(out)
            world.set_artifact("export", str(out))
        world.record("export_image", beat="导出拼好的地图")
        return world.artifact("export")

    return {
        "load_fragments": load_fragments,
        "perceive_fragment": perceive_fragment,
        "compare_edges": compare_edges,
        "rotate_piece": rotate_piece,
        "assemble_grid": assemble_grid,
        "mark_route": mark_route,
        "export_image": export_image,
    }
