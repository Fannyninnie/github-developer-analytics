import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path

from api_client import GitHubClient
from extract_commits import to_iso, to_stamp
from extract_repositories import read_repo_list, save_json

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
STATE_FILE = ROOT / "data" / "state" / "issue_pr_watermarks.json"
INITIAL_LOAD_DAYS = 90


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state):
    save_json(STATE_FILE, state)


def fetch_issues(client, repo, since):
    params = {"state": "all", "since": since}
    return list(client.get_paginated(f"/repos/{repo}/issues", params))


def fetch_pulls(client, repo, since):
    params = {"state": "all", "sort": "updated", "direction": "desc"}
    pulls = []
    for pull in client.get_paginated(f"/repos/{repo}/pulls", params):
        if pull["updated_at"] < since:
            break
        pulls.append(pull)
    return pulls


def save_batch(kind, repo, since, extracted_at, items):
    if not items:
        return
    path = (
        RAW_DIR
        / kind
        / f"repo={repo.replace('/', '__')}"
        / f"since={to_stamp(since)}.json"
    )
    save_json(
        path,
        {"repo": repo, "since": since, "extracted_at": extracted_at, kind: items},
    )


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

    for repo in read_repo_list():
        since = state.get(repo, default_since)

        issues = fetch_issues(client, repo, since)
        pulls = fetch_pulls(client, repo, since)

        save_batch("issues", repo, since, new_watermark, issues)
        save_batch("pulls", repo, since, new_watermark, pulls)

        state[repo] = new_watermark
        save_state(state)

        pr_items = sum(1 for item in issues if "pull_request" in item)
        logger.info(
            "%s: %s issue items (%s are PRs), %s pull requests since %s",
            repo, len(issues), pr_items, len(pulls), since,
        )


if __name__ == "__main__":
    main()