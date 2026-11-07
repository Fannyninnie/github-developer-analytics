import os

import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

response = requests.get(
    "https://api.github.com/repos/pallets/flask",
    headers=headers,
    timeout=30,
)

print("Status code:", response.status_code)

data = response.json()
print("Name:", data["full_name"])
print("Stars:", data["stargazers_count"])
print("Forks:", data["forks_count"])
print("Language:", data["language"])

print("Requests remaining:", response.headers["X-RateLimit-Remaining"])
print("Hourly limit:", response.headers["X-RateLimit-Limit"])