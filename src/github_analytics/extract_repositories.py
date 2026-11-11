import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from api_client import GitHubClient

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
REPOS_FILE = ROOT / "repos.txt"
RAW_DIR = ROOT / "data" / "raw"


def read_repo_list(path=REPOS_FILE):
    lines = path.read_text().splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def build_snapshot(repo_data, snapshot_date):
    return {
        "repo_id": repo_data["id"],
        "repo": repo_data["full_name"],
        "snapshot_date": snapshot_date,
        "stars": repo_data["stargazers_count"],
        "forks": repo_data["forks_count"],
        "open_issues": repo_data["open_issues_count"],
        "watchers": repo_data.get("subscribers_count"),
    }


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    client = GitHubClient()
    now = datetime.now(UTC)
    today = now.date().isoformat()

    saved = 0
    skipped = []

    for repo in read_repo_list():
        response = client.get(f"/repos/{repo}")
        if response is None:
            skipped.append(repo)
            continue
        data = response.json()

        languages_response = client.get(f"/repos/{repo}/languages")
        languages = languages_response.json() if languages_response else {}

        file_name = repo.replace("/", "__") + ".json"

        save_json(
            RAW_DIR / "repositories" / f"extract_date={today}" / file_name,
            {"extracted_at": now.isoformat(), "repo": data, "languages": languages},
        )
        save_json(
            RAW_DIR / "repo_snapshots" / f"snapshot_date={today}" / file_name,
            build_snapshot(data, today),
        )

        logger.info("Saved %s (%s stars)", repo, data["stargazers_count"])
        saved += 1

    logger.info("Done: %s saved, %s skipped %s", saved, len(skipped), skipped)


if __name__ == "__main__":
    main()