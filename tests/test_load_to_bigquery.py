import json

import load_to_bigquery


def test_item_rows_builds_one_row_per_item(tmp_path, monkeypatch):
    monkeypatch.setattr(load_to_bigquery, "RAW_DIR", tmp_path)
    folder = tmp_path / "commits" / "repo=pallets__flask"
    folder.mkdir(parents=True)
    content = {
        "repo": "pallets/flask",
        "since": "2026-10-01T00:00:00Z",
        "extracted_at": "2026-11-10T14:00:00Z",
        "commits": [{"sha": "a1"}, {"sha": "b2"}],
    }
    (folder / "since=20261001T000000Z.json").write_text(json.dumps(content))

    rows = load_to_bigquery.item_rows("commits", "sha", "2026-11-10T15:00:00+00:00")

    assert [row["sha"] for row in rows] == ["a1", "b2"]
    assert rows[0]["repo"] == "pallets/flask"
    assert (
        rows[0]["batch_id"] == "commits/repo=pallets__flask/since=20261001T000000Z.json"
    )
    assert json.loads(rows[0]["payload"]) == {"sha": "a1"}


def test_batch_keys_for_payload_tables_are_unique_batch_ids():
    rows = [{"batch_id": "a"}, {"batch_id": "a"}, {"batch_id": "b"}]
    assert load_to_bigquery.batch_keys("commits", rows) == ["a", "b"]


def test_batch_keys_for_snapshots_combine_date_and_repo():
    rows = [{"snapshot_date": "2026-11-10", "repo": "pallets/flask"}]
    assert load_to_bigquery.batch_keys("repo_snapshots", rows) == [
        "2026-11-10|pallets/flask"
    ]
def test_item_rows_applies_repo_aliases(tmp_path, monkeypatch):
    monkeypatch.setattr(load_to_bigquery, "RAW_DIR", tmp_path)
    monkeypatch.setattr(load_to_bigquery, "REPO_ALIASES", {"old/name": "new/name"})
    folder = tmp_path / "commits" / "repo=old__name"
    folder.mkdir(parents=True)
    content = {
        "repo": "old/name",
        "since": "x",
        "extracted_at": "2026-11-10T14:00:00Z",
        "commits": [{"sha": "a1"}],
    }
    (folder / "since=x.json").write_text(json.dumps(content))

    rows = load_to_bigquery.item_rows("commits", "sha", "2026-11-10T15:00:00+00:00")

    assert rows[0]["repo"] == "new/name"