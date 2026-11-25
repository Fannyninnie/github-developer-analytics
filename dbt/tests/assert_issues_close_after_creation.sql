-- An issue cannot be closed before it was created. Any row returned is a failure.
select *
from {{ ref('fact_issues') }}
where closed_at < created_at
