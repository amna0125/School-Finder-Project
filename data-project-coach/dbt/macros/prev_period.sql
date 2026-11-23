{# School years are written '2024/25'. Returns the year before, e.g. '2023/24'. #}
{% macro prev_period(col) -%}
  (cast(cast(left({{ col }}, 4) as integer) - 1 as varchar) || '/' || lpad(cast((cast(right({{ col }}, 2) as integer) + 99) % 100 as varchar), 2, '0'))
{%- endmacro %}
