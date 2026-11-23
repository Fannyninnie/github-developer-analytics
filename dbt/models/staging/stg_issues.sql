with source as (

    select *
    from {{ source('raw', 'issues') }}
    where json_query(payload, '$.pull_request') is null

),

parsed as (

    select
        repo,
        number as issue_number,
        cast(json_value(payload, '$.id') as int64) as issue_id,
        json_value(payload, '$.title') as title,
        json_value(payload, '$.state') as state,
        json_value(payload, '$.user.login') as author_login,
        cast(json_value(payload, '$.comments') as int64) as comment_count,
        array_length(json_query_array(payload, '$.labels')) as label_count,
        timestamp(json_value(payload, '$.created_at')) as created_at,
        timestamp(json_value(payload, '$.updated_at')) as updated_at,
        timestamp(json_value(payload, '$.closed_at')) as closed_at,
        extracted_at
    from source

),

ranked as (

    select
        *,
        row_number() over (
            partition by repo, issue_number
            order by updated_at desc, extracted_at desc
        ) as row_num
    from parsed

)

select * except (row_num)
from ranked
where row_num = 1
