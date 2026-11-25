select
    repo,
    issue_number,
    issue_id,
    title,
    state,
    author_login,
    comment_count,
    label_count,
    created_at,
    updated_at,
    closed_at,
    case when closed_at is not null then round(timestamp_diff(closed_at, created_at, minute) / 60, 2) end as hours_to_close,
    case when state = 'open' then timestamp_diff(current_timestamp(), created_at, day) end as open_age_days
from {{ ref('stg_issues') }}
