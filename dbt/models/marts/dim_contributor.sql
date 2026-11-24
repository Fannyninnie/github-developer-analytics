with activity as (

    select author_login as contributor_login, committed_at as activity_at
    from {{ ref('stg_commits') }}
    where author_login is not null

    union all

    select author_login, created_at
    from {{ ref('stg_pull_requests') }}
    where author_login is not null

    union all

    select author_login, created_at
    from {{ ref('stg_issues') }}
    where author_login is not null

)

select
    contributor_login,
    min(activity_at) as first_seen_at,
    max(activity_at) as last_seen_at,
    ends_with(contributor_login, '[bot]') as is_bot
from activity
group by contributor_login
