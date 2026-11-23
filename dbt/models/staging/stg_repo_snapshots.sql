with source as (

    select * from {{ source('raw', 'repo_snapshots') }}

),

ranked as (

    select
        *,
        row_number() over (
            partition by repo, snapshot_date
            order by loaded_at desc
        ) as row_num
    from source

)

select
    repo_id,
    repo,
    snapshot_date,
    stars,
    forks,
    open_issues as open_issues_and_prs,
    watchers,
    loaded_at
from ranked
where row_num = 1
