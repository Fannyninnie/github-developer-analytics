with source as (

    select * from {{ source('raw', 'commits') }}

),

parsed as (

    select
        repo,
        sha,
        json_value(payload, '$.commit.author.name') as author_name,
        json_value(payload, '$.author.login') as author_login,
        json_value(payload, '$.committer.login') as committer_login,
        timestamp(json_value(payload, '$.commit.author.date')) as authored_at,
        timestamp(json_value(payload, '$.commit.committer.date')) as committed_at,
        split(json_value(payload, '$.commit.message'), '\n')[safe_offset(0)] as message_first_line,
        array_length(json_query_array(payload, '$.parents')) as parent_count,
        extracted_at
    from source

),

ranked as (

    select
        *,
        row_number() over (
            partition by repo, sha
            order by extracted_at desc
        ) as row_num
    from parsed

)

select
    repo,
    sha,
    author_name,
    author_login,
    author_login is not null as has_github_author,
    committer_login,
    authored_at,
    committed_at,
    message_first_line,
    parent_count,
    parent_count > 1 as is_merge_commit,
    extracted_at
from ranked
where row_num = 1
