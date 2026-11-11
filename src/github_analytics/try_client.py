import logging

from api_client import GitHubClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

client = GitHubClient()

print("--- 1. A repo that exists ---")
response = client.get("/repos/pallets/flask")
print(response.json()["full_name"], response.json()["stargazers_count"])

print("--- 2. A repo that does not exist ---")
response = client.get("/repos/pallets/not-a-real-repo")
print("Result:", response)

print("--- 3. Pagination (2 pages of 100 commits) ---")
commits = list(client.get_paginated("/repos/pallets/flask/commits", max_pages=2))
print("Commits fetched:", len(commits))