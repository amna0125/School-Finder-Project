# dbt project: school_finder

Turns the pipeline database into the tables the website reads.

- **Sources**: `.state/schools.duckdb` (dlt load, attached read-only) and the saved register file.
- **Seeds**: municipalities, review labels, metric dictionary, survey themes and answer groups, approach categories.
- **Bronze** (`models/bronze`, views): raw as loaded. Staff names, e-mails and phone numbers in the register are not selected.
- **Silver** (`models/silver`, tables): typed and cleaned. Skolverket's symbols become a `value_status`
  (`..` few pupils, `~100` rounded, `*` teachers excluded, `.` not reported).
- **Gold** (`models/gold`, Parquet files in `web/public/data`): `school_card`, `fct_school_metrics`,
  `fct_metric_history`, `school_approach`, `school_survey`, `school_setting`, `county_medians`, `dim_metrics`,
  `dim_approach_categories`.

Rules: latest school year with a one-year fallback; county median (not mean, no ranking); combined national
test result = mean of maths, Swedish and English when at least two exist; survey shares re-based on those who answered.

## Run

From this folder, with the project venv active (`pip install dbt-duckdb`):

```
dbt build --profiles-dir .
python scripts/export_lineage.py
dbt docs generate --profiles-dir . && dbt docs serve --profiles-dir .   # optional: dbt's own lineage site
```

dbt writes its own working database to `.state/warehouse.duckdb`; the pipeline database is never changed.
Paths can be overridden with `DBT_RAW_DB`, `DBT_WAREHOUSE`, `DBT_EXPORT_DIR` and `DBT_REGISTER_FILE`.
