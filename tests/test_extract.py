from datetime import UTC, datetime

from extract_commits import to_iso, to_stamp
from extract_issues_prs import fetch_pulls
from extract_repositories import build_snapshot, read_repo_list


class FakeClient:
    def __init__(self, items):
        self.items = items

    def get_paginated(self, path, params=None):
        return iter(self.items)


def test_read_repo_list_skips_blank_lines_and_comments(tmp_path):
    repos_file = tmp_path / "repos.txt"
    repos_file.write_text("pallets/flask\n\n# a comment\npsf/requests\n")
    assert read_repo_list(repos_file) == ["pallets/flask", "psf/requests"]


def test_build_snapshot_keeps_the_daily_numbers():
    repo_data = {
        "id": 1,
        "full_name": "pallets/flask",
        "stargazers_count": 75062,
        "forks_count": 17286,
        "open_issues_count": 312,
    }
    snapshot = build_snapshot(repo_data, "2026-11-10")
    assert snapshot["repo"] == "pallets/flask"
    assert snapshot["snapshot_date"] == "2026-11-10"
    assert snapshot["stars"] == 75062
    assert snapshot["watchers"] is None


def test_to_iso_formats_a_utc_timestamp():
    moment = datetime(2026, 11, 10, 14, 0, 5, tzinfo=UTC)
    assert to_iso(moment) == "2026-11-10T14:00:05Z"


def test_to_stamp_is_safe_for_file_names():
    assert to_stamp("2026-11-10T14:00:05Z") == "20261110T140005Z"


def test_fetch_pulls_stops_at_the_bookmark():
    pulls = [
        {"number": 3, "updated_at": "2026-11-10T00:00:00Z"},
        {"number": 2, "updated_at": "2026-11-05T00:00:00Z"},
        {"number": 1, "updated_at": "2026-10-01T00:00:00Z"},
    ]
    result = fetch_pulls(FakeClient(pulls), "pallets/flask", "2026-11-01T00:00:00Z")
    assert [pull["number"] for pull in result] == [3, 2]