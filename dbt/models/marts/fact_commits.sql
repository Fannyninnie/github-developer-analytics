{{ config(
    partition_by={'field': 'committed_date', 'data_type': 'date'},
    cluster_by=['repo']
) }}

select
    repo,
    sha,
    date(committed_at) as committed_date,
    committed_at,
    authored_at,
    author_login as contributor_login,
    author_name,
    has_github_author,
    is_merge_commit,
    message_first_line
from {{ ref('stg_commits') }}
