from scripts import evaluate_agent_skill_outputs as eval_outputs


def test_parse_verifier_output_extracts_leaf_score():
    parsed = eval_outputs.parse_verifier_output(
        "RESULT: FAIL — core02_x  json leaf score: 3/5\n",
        exit_code=1,
    )

    assert parsed["passed"] is False
    assert parsed["result_status"] == "FAIL"
    assert parsed["result_task_id"] == "core02_x"
    assert parsed["leaf_score"] == 3
    assert parsed["leaf_total"] == 5
    assert parsed["leaf_ratio"] == 0.6


def test_classify_failure_tags_missing_and_mismatch():
    tags = eval_outputs.classify_failure(
        "FAIL: missing output: outputs/answer.json\n"
        "FAIL: text mismatch: outputs/report.md",
        "",
        exit_code=1,
    )

    assert "F4_output_contract" in tags
    assert "F8_domain_error" in tags


def test_summarize_pairs_computes_wtl():
    records = [
        {
            "task_id": "task",
            "role": "role",
            "difficulty": "hard",
            "condition": "control",
            "pass": False,
            "score": {"total_score": 40.0, "verifier_passed": False},
        },
        {
            "task_id": "task",
            "role": "role",
            "difficulty": "hard",
            "condition": "skill",
            "pass": True,
            "score": {"total_score": 100.0, "verifier_passed": True},
        },
    ]

    summary = eval_outputs.summarize(records)

    assert summary["n_pairs"] == 1
    assert summary["wins"] == 1
    assert summary["delta_pass_at_1"] == 1
    assert summary["delta_score"] == 60.0
