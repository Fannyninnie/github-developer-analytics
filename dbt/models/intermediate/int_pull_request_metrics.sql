select
    repo,
    pr_number,
    pr_id,
    title,
    state,
    is_draft,
    is_merged,
    author_login,
    base_branch,
    created_at,
    updated_at,
    closed_at,
    merged_at,
    case when is_merged then round(timestamp_diff(merged_at, created_at, minute) / 60, 2) end as hours_to_merge,
    case when closed_at is not null then round(timestamp_diff(closed_at, created_at, minute) / 60, 2) end as hours_to_close,
    case when state = 'open' then timestamp_diff(current_timestamp(), created_at, day) end as open_age_days
from {{ ref('stg_pull_requests') }}
