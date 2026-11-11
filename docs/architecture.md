# Architecture

```mermaid
flowchart LR
    A[GitHub REST API] --> B[Python ingestion]
    B --> C[Raw JSON files]
    C --> D[(BigQuery raw dataset)]
    D --> E[dbt staging models]
    E --> F[dbt marts]
    F --> G[Looker Studio dashboard]
    H[Airflow] -. schedules .-> B
    H -. schedules .-> E
    I[GitHub Actions] -. tests .-> B
    I -. tests .-> E
```
## Why fact_repo_daily has one row per repo per day

GitHub's API only gives the star and fork counts as of right now. If the table had one row per repo, each daily run would overwrite the previous number and the history would be lost. One row per repo per day keeps every snapshot, so the dashboard can show how stars and forks grow over time.