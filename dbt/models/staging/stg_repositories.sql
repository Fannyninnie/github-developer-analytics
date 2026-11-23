with source as (

    select * from {{ source('raw', 'repositories') }}

),

ranked as (

    select
        *,
        row_number() over (
            partition by repo
            order by extracted_at desc
        ) as row_num
    from source

)

select
    cast(json_value(payload, '$.id') as int64) as repo_id,
    repo,
    json_value(payload, '$.name') as repo_name,
    json_value(payload, '$.owner.login') as owner_login,
    json_value(payload, '$.description') as description,
    json_value(payload, '$.language') as primary_language,
    json_value(payload, '$.license.spdx_id') as license,
    safe_cast(json_value(payload, '$.fork') as bool) as is_fork,
    safe_cast(json_value(payload, '$.archived') as bool) as is_archived,
    json_value(payload, '$.default_branch') as default_branch,
    timestamp(json_value(payload, '$.created_at')) as created_at,
    timestamp(json_value(payload, '$.pushed_at')) as last_pushed_at,
    languages as languages_json,
    extracted_at
from ranked
where row_num = 1
