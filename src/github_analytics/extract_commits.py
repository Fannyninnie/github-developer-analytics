import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path

from api_client import GitHubClient
from extract_repositories import read_repo_list, save_json

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "commits"
STATE_FILE = ROOT / "data" / "state" / "commit_watermarks.json"
INITIAL_LOAD_DAYS = 90


def to_iso(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def to_stamp(iso_string):
    return iso_string.replace("-", "").replace(":", "")


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state):
    save_json(STATE_FILE, state)


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    client = GitHubClient()
    state = load_state()

    run_started = datetime.now(UTC)
    first_load_start = (run_started - timedelta(days=INITIAL_LOAD_DAYS)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    default_since = to_iso(first_load_start)
    new_watermark = to_iso(run_started)

    total = 0
    for repo in read_repo_list():
        since = state.get(repo, default_since)
        commits = list(
            client.get_paginated(f"/repos/{repo}/commits", {"since": since})
        )

        if commits:
            file_name = f"since={to_stamp(since)}.json"
            save_json(
                RAW_DIR / f"repo={repo.replace('/', '__')}" / file_name,
                {
                    "repo": repo,
                    "since": since,
                    "extracted_at": new_watermark,
                    "commits": commits,
                },
            )

        state[repo] = new_watermark
        save_state(state)

        logger.info("%s: %s commits since %s", repo, len(commits), since)
        total += len(commits)

    logger.info("Done: %s commits across all repos", total)


if __name__ == "__main__":
    main()