with date_spine as (
  select dateadd(day, seq4(), '2016-01-01'::date) as date_day
  from table(generator(rowcount => 3650))
)
select
  date_day,
  extract(year from date_day) as year,
  extract(month from date_day) as month,
  extract(day from date_day) as day,
  extract(quarter from date_day) as quarter,
  dayname(date_day) as day_name
from date_spine
