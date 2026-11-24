select
    repo,
    repo_id,
    repo_name,
    owner_login,
    description,
    primary_language,
    license,
    is_fork,
    is_archived,
    default_branch,
    created_at as repo_created_at,
    last_pushed_at
from {{ ref('stg_repositories') }}
