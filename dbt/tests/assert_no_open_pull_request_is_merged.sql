-- A pull request cannot be both open and merged. Any row returned is a failure.
select *
from {{ ref('fact_pull_requests') }}
where state = 'open' and is_merged
