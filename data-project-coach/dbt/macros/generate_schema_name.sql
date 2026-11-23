{# Use the layer name (bronze / silver / gold / seeds) as the schema, without the target prefix. #}
{% macro generate_schema_name(custom_schema_name, node) -%}
  {{ custom_schema_name if custom_schema_name is not none else target.schema }}
{%- endmacro %}
