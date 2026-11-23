# Selected-school pipeline — SQLite setup

Updated 20 October 2026. Stack: Python 3.11+, dlt 1.31.0 with SQLAlchemy destination, Prefect 3.8.8, SQLite. No Docker, ClickHouse, database password, cloud service or scheduled deployment is required.

## Separate databases
- School data: `.state/schools.sqlite`. dlt uses SQLite's `main` dataset so tables are directly accessible in this file.
- Prefect orchestration state: `.state/prefect/prefect.db` by default.
- Offline smoke-test data: `.state/smoke/schools.sqlite` (not the production sample).

SQLite is suitable for this small single-user pilot. Avoid concurrent loads. Prefect settings already present in the environment take precedence over code defaults, including `PREFECT_API_URL` and its database URL. Both databases and local pipeline state are ignored by version control. `compose.yaml` is retained as a clearly labelled legacy ClickHouse reference, not part of the current setup. No existing ClickHouse data was migrated or deleted.

## Setup in a WSL terminal
1. `python3 -m venv .venv`
2. `.venv/bin/python -m pip install -e .`
3. Run tests: `.venv/bin/python -m unittest discover -s tests -v`
4. Check dlt without a Prefect server: `.venv/bin/python -m school_pipeline.smoke_sqlite --direct`
5. Check orchestration with saved fixtures: `.venv/bin/python -m school_pipeline.smoke_sqlite`
6. Extract live sample: `.venv/bin/python -m school_pipeline.flow --extract-only`
7. Inspect the printed run directory's `manifest.json`, `coverage.json` and JSONL files.
8. Load that reviewed extract: `.venv/bin/python -m school_pipeline.flow --replay outputs/runs/<run-id>`

Do not proceed past a failed check as though it succeeded. The smoke command uses saved public fixtures and deliberately marks provenance as test-only; it does not establish fresh retrieval dates or full three-school coverage.

## Scope and sources
`config/schools.json` selects the three-school pilot; it is neither county-wide ingestion nor a representative sample. Per school, the flow requests the Skolverket school-unit register v2, Planned Education v4 `/statistics/gr`, parent `/nestedsurveys/custodiansgr` and pupil `/nestedsurveys/pupilsgr` endpoints. These are official survey aggregates, not review-platform free text. Parent and pupil results retain respondent and year-group context and must not be pooled.

Tables: `schools`, `statistics`, `survey_observations`, `source_coverage`, plus dlt internal tables. Sources carry URLs, timestamps and response hashes in the normal live pipeline. Register contact fields are removed before snapshot persistence; their hash identifies original response bytes, not sanitized file contents. Statistics preserve raw values, suppression/approximation flags, empty arrays and periods. `docLinks` is metadata, retained in raw snapshots rather than treated as a metric. Plain numeric statistics are parsed only when marked `EXISTS`. Pupils per teacher and whole-school counts are not class size. Survey `-` symbols remain unresolved, not zero; scales require review before display.

Loads replace the dedicated selected-sample snapshot. Missing endpoint coverage and empty normalized tables block loading. Multi-table replacement is not guaranteed atomic: inspect all counts after a load and replay the complete snapshot if necessary. Source history stays in local run folders. Unexpected structures and mismatched identifiers fail validation.

## Validation on 20 October 2026
- Required packages were already available in the execution environment; no new installation was needed there. This does not prove the user's `.venv` is configured.
- All six unit tests passed on the final rerun, including the `docLinks` regression adjustment.
- Direct saved-fixture smoke passed twice without duplicate accumulation: schools 1, statistics 84, survey observations 149, coverage 1. SQLite integrity check returned `ok`. Evidence: `outputs/sqlite_smoke_result.json`.
- Prefect orchestration now verified: diagnostic run, normal retry, and final post-change smoke all completed successfully. Final evidence: `outputs/prefect_fix_smoke.log` and `outputs/sqlite_smoke_result.json` (`prefect_orchestrated: true`). Both SQLite load tasks completed; counts and integrity check passed.
- Prefect database integrity returned `ok`. The earlier timeout did not recur; its exact cause remains unconfirmed. The previous startup allowance was 20 seconds; `flow.py` now defaults to 90 seconds for slow local/WSL starts, preserving explicit environment overrides. No state was deleted or relocated. Debug evidence: `outputs/prefect_startup_debug.log`. Final six-test evidence: `outputs/prefect_fix_tests.log`.
- No fresh three-school extraction/load has been demonstrated.
- The workspace has no Git metadata; `git status` failed. Changes were reviewed directly, not by Git diff.

## Remaining gates
1. Run and review a fresh three-school extract, then load the reviewed snapshot. Prefect startup and offline orchestration are now verified; this does not establish live-source coverage.
2. Implement school-website collection as a core source: permissions/technical assessment, URLs, retrieval dates, excerpts, school-unit scope and explicit school-self-description labels. This is not yet part of the flow. Resolve Anne Frank's unit/grade discrepancy before attributing claims.
3. Review survey coverage, symbol definitions, scales and reporting periods before analysis. Do not infer causal effects or rank schools overall.

## References
- https://dlthub.com/docs/dlt-ecosystem/destinations/sqlalchemy (SQLite support; consulted 20 October 2026)
- https://api.skolverket.se/planned-educations/swagger-ui/index.html
- https://api.skolverket.se/skolenhetsregistret/swagger-ui/index.html
