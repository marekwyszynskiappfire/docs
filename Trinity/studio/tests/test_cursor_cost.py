from cursor_cost import record_cursor_usage, usage_summary_for_pipeline


def test_cursor_usage_summary_by_stage(studio_db):
    from db import db

    with db() as conn:
        record_cursor_usage(
            conn,
            stage="reviewer_analyze",
            conversation_id="conv-1",
            pipeline_run_id="pr-test",
            model="test-model",
            cost_cents=150,
            source="manual",
        )
        record_cursor_usage(
            conn,
            stage="creator",
            conversation_id="conv-2",
            pipeline_run_id="pr-test",
            model="test-model",
            cost_cents=50,
            source="manual",
        )
        summary = usage_summary_for_pipeline(conn, "pr-test")

    assert summary["total_cost_cents"] == 200
    assert len(summary["by_stage"]) == 2
    assert summary["models_used"][0]["model"] == "test-model"
