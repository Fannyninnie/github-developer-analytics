import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.github.com"
OUT_DIR = Path("data/raw/samples")
OUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get(path, params=None):
    response = requests.get(
        f"{BASE_URL}{path}", headers=HEADERS, params=params, timeout=30
    )
    print(path, "->", response.status_code)
    response.raise_for_status()
    return response


def save(name, data):
    (OUT_DIR / f"{name}.json").write_text(json.dumps(data, indent=2))
    print("Saved", name)


repo = "pallets/flask"

save("repo", get(f"/repos/{repo}").json())
save("languages", get(f"/repos/{repo}/languages").json())
save("commits", get(f"/repos/{repo}/commits", {"per_page": 5}).json())
save("issues", get(f"/repos/{repo}/issues", {"per_page": 5, "state": "all"}).json())
save("pulls", get(f"/repos/{repo}/pulls", {"per_page": 5, "state": "all"}).json())

# --- Pagination demo ---
response = get(f"/repos/{repo}/commits", {"per_page": 5})
print("Link header:", response.headers.get("Link"))
print("Parsed links:", list(response.links.keys()))

url = f"{BASE_URL}/repos/{repo}/commits"
params = {"per_page": 100}
pages = 0
total = 0

while url and pages < 3:
    page = requests.get(url, headers=HEADERS, params=params, timeout=30)
    page.raise_for_status()
    total += len(page.json())
    pages += 1
    print(f"Page {pages}: {len(page.json())} commits")
    url = page.links.get("next", {}).get("url")
    params = None  # the next URL already includes the settings

print("Total commits fetched:", total)

# --- Pagination demo ---
response = get(f"/repos/{repo}/commits", {"per_page": 5})
print("Link header:", response.headers.get("Link"))
print("Parsed links:", list(response.links.keys()))

url = f"{BASE_URL}/repos/{repo}/commits"
params = {"per_page": 100}
pages = 0
total = 0

while url and pages < 3:
    page = requests.get(url, headers=HEADERS, params=params, timeout=30)
    page.raise_for_status()
    total += len(page.json())
    pages += 1
    print(f"Page {pages}: {len(page.json())} commits")
    url = page.links.get("next", {}).get("url")
    params = None  # the next URL already includes the settings

print("Total commits fetched:", total)


# Filter by date
save("commits_recent", get(f"/repos/{repo}/commits", {"per_page": 5, "since": "2026-10-01T00:00:00Z"}).json())

