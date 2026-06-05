"""Regression coverage for the 21 Red Dust tasks upgraded from generic scaffold
to shared family deep graders."""
import json
from pathlib import Path

import pytest

from openclaw.reddust.engine import run_task_dir

TASKS = Path(__file__).resolve().parents[1] / "tasks"

TARGET_FAMILIES = {
    "rd_ci_01_undocumented_vision_model": "build",
    "rd_ci_02_thermal_coord_fix": "code",
    "rd_ci_04_garage_route_jigsaw_4x4": "jigsaw",
    "rd_ci_05_station_coord_jigsaw_5x5": "jigsaw",
    "rd_ci_07_wall_dots_connect": "puzzle",
    "rd_ci_08_color_pipe_linkapix": "puzzle",
    "rd_ci_09_circuit_linkapix_easy": "puzzle",
    "rd_ci_10_shelter_broadcast_homepage": "build",
    "rd_ci_11_resident_skill_profile_page": "build",
    "rd_ci_12_station_starmap_162dots": "puzzle",
    "rd_cs_01_day7_action_report": "build",
    "rd_cs_02_corridor_highlight_clip": "build",
    "rd_cs_03_shelter_recruit_poster": "build",
    "rd_cs_04_radio_tutorial_notes": "build",
    "rd_cs_05_gear_video_to_json": "build",
    "rd_cs_06_outing_gear_outfit_image": "build",
    "rd_cs_07_water_paper_to_poster": "build",
    "rd_cs_08_aura_toolkit_docsite": "build",
    "rd_cs_09_repair_plan_slides": "build",
    "rd_cs_10_multisize_sos_poster": "build",
    "rd_cs_11_rescue_video_zh_dub": "build",
}


@pytest.mark.parametrize("slug,family", TARGET_FAMILIES.items(), ids=list(TARGET_FAMILIES))
def test_remaining_task_is_bound_to_deep_family(slug, family):
    task_dir = TASKS / slug
    brief = json.loads((task_dir / "inputs" / "brief.json").read_text(encoding="utf-8"))
    tools = (task_dir / "tools.py").read_text(encoding="utf-8")
    verify = (task_dir / "verifier" / "verify.py").read_text(encoding="utf-8")

    assert brief["family"] == family
    assert (task_dir / "inputs" / "data.json").exists()
    assert (task_dir / "expected" / "key.json").exists()
    assert "openclaw.reddust.deeplib" in tools
    assert "openclaw.reddust.deeplib" in verify
    assert "build_generic_tools" not in tools


@pytest.mark.parametrize("slug", TARGET_FAMILIES, ids=list(TARGET_FAMILIES))
def test_remaining_task_gold_scores_high_and_bad_is_readable(slug):
    task_dir = TASKS / slug
    g = run_task_dir(task_dir, "gold")
    b = run_task_dir(task_dir, "bad")
    assert g["score"] >= 85, (slug, g["failure_reasons"])
    assert g["score"] - b["score"] >= 30, (slug, g["score"], b["score"])
    assert b["failure_reasons"], slug
    assert len(b["failure_reasons"]) <= 3, slug
