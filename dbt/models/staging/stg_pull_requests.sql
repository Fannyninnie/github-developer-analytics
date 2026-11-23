with source as (

    select * from {{ source('raw', 'pull_requests') }}

),

parsed as (

    select
        repo,
        number as pr_number,
        cast(json_value(payload, '$.id') as int64) as pr_id,
        json_value(payload, '$.title') as title,
        json_value(payload, '$.state') as state,
        safe_cast(json_value(payload, '$.draft') as bool) as is_draft,
        json_value(payload, '$.user.login') as author_login,
        json_value(payload, '$.base.ref') as base_branch,
        timestamp(json_value(payload, '$.created_at')) as created_at,
        timestamp(json_value(payload, '$.updated_at')) as updated_at,
        timestamp(json_value(payload, '$.closed_at')) as closed_at,
        timestamp(json_value(payload, '$.merged_at')) as merged_at,
        extracted_at
    from source

),

ranked as (

    select
        *,
        row_number() over (
            partition by repo, pr_number
            order by updated_at desc, extracted_at desc
        ) as row_num
    from parsed

)

select
    * except (row_num),
    merged_at is not null as is_merged
from ranked
where row_num = 1
