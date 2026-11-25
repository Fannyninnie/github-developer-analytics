#!/usr/bin/env bash
# Daily run until Airflow takes over: extract, load, then build and test the dbt models.
set -euo pipefail

cd "$(dirname "$0")/.."
source .venv/bin/activate
set -a; source .env; set +a

python src/github_analytics/extract_repositories.py
python src/github_analytics/extract_commits.py
python src/github_analytics/extract_issues_prs.py
python src/github_analytics/load_to_bigquery.py

cd dbt
dbt build
