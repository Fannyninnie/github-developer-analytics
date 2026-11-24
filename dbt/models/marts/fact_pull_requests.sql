{{ config(
    partition_by={'field': 'created_date', 'data_type': 'date'},
    cluster_by=['repo']
) }}

select
    repo,
    pr_number,
    pr_id,
    date(created_at) as created_date,
    date(merged_at) as merged_date,
    author_login as contributor_login,
    title,
    state,
    is_draft,
    is_merged,
    base_branch,
    created_at,
    updated_at,
    closed_at,
    merged_at,
    hours_to_merge,
    hours_to_close,
    open_age_days
from {{ ref('int_pull_request_metrics') }}
