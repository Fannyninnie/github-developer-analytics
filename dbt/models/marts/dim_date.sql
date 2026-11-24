select
    date_day,
    extract(year from date_day) as year,
    extract(month from date_day) as month,
    format_date('%B', date_day) as month_name,
    date_trunc(date_day, week(monday)) as week_start,
    extract(isoweek from date_day) as iso_week,
    format_date('%A', date_day) as day_name,
    extract(dayofweek from date_day) in (1, 7) as is_weekend
from unnest(generate_date_array('2026-01-01', '2027-12-31')) as date_day
