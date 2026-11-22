# Data model

| Table | One row is... | Key |
|---|---|---|
| fact_commits | one commit | repo + sha |
| fact_pull_requests | one pull request | repo + number |
| fact_issues | one issue (pull requests excluded) | repo + number |
| fact_repo_daily | one repo on one day | repo + date |
| dim_repo | one repository | repo id |
| dim_contributor | one GitHub user | login |

## Layers

| Layer | What happens | Where |
|---|---|---|
| Raw | API responses stored as received, plus a load timestamp | BigQuery raw dataset |
| Staging | Rename, cast types, flatten nested fields, remove duplicates, separate PRs from issues | dbt staging models |
| Marts | Fact and dimension tables for analysis | dbt marts models |

## Why fact_repo_daily has one row per repo per day

GitHub's API only gives the star and fork counts as of right now. If the table had one row per repo, each daily run would overwrite the previous numbers and the history would be lost. With one row per repo per day, every snapshot is kept, so the dashboard can show how stars and forks grow over time. Growth is not stored in the table. It is calculated by comparing one day's total with the day before.

## Why raw keeps nulls

The raw layer stores data exactly as GitHub sent it, including empty values such as a commit author with a null login. Decisions about what to do with them, like replacing them with "unknown", happen in staging. That way the original data is never lost and the pipeline can be rebuilt from raw if something goes wrong.

## Raw tables in BigQuery

Dataset `raw`, location US. Every table is partitioned by day and clustered by `repo`.

| Table | One row is | Partitioned by |
|---|---|---|
| repo_snapshots | one repo on one day | snapshot_date |
| repositories | one repo as extracted | extracted_at |
| commits | one commit | extracted_at |
| issues | one issue item (PRs included) | extracted_at |
| pull_requests | one pull request | extracted_at |

Payload tables keep the original JSON in a `payload` column plus bookkeeping columns. `batch_id` lets a load replace one batch without duplicating rows.
## How loads stay idempotent

Each extract file is a batch, identified by `batch_id` (its path). Before loading, the loader deletes the rows of the batches it is about to insert, then inserts them. Re-running replaces the same batches instead of duplicating them, and new extract files add new batches. Snapshots use snapshot date plus repo as the batch key.

Known limitation: delete and insert are two steps, so a table is briefly empty during a reload, and a failure between them leaves it empty until the next run. A production version would load into a staging table and swap it in with a single MERGE.