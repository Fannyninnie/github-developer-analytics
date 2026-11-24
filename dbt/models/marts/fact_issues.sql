{{ config(
    partition_by={'field': 'created_date', 'data_type': 'date'},
    cluster_by=['repo']
) }}

select
    repo,
    issue_number,
    issue_id,
    date(created_at) as created_date,
    date(closed_at) as closed_date,
    author_login as contributor_login,
    title,
    state,
    comment_count,
    label_count,
    created_at,
    updated_at,
    closed_at,
    hours_to_close,
    open_age_days
from {{ ref('int_issue_metrics') }}
