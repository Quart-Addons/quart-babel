.. _jinja_filters:

==============
Jinja Filters
==============

Several commonly used formatters are added as jinja template filters after
calling `init_app().` For dates and times, these are:

- `<datetime>|datetimeformat` -> `format_datetime`
- `<date>|dateformat` -> `format_date`
- `<time>|timeformat` -> `format_time`
- `<timedelta>|timedeltaformat` -> `format_timedelta`

And for numbers, these are:

- `<number>|numberformat` -> `format_number`
- `<number>|decimalformat` -> `format_decimal`
- `<number>|currencyformat` -> `format_currency`
- `<number>|percentformat` -> `format_percent`
- `<number>|scientificformat` -> `format_scientific`
