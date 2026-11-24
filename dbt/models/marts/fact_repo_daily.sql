{{ config(
    partition_by={'field': 'snapshot_date', 'data_type': 'date'},
    cluster_by=['repo']
) }}

select
    repo,
    snapshot_date,
    stars,
    forks,
    open_issues_and_prs,
    watchers,
    stars - lag(stars) over (partition by repo order by snapshot_date) as stars_change,
    forks - lag(forks) over (partition by repo order by snapshot_date) as forks_change
from {{ ref('stg_repo_snapshots') }}
