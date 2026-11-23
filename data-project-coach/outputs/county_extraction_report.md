# Stockholm County extraction — 20 October 2026

## Result
The live local Prefect → dlt → SQLite flow completed successfully. Destination: `.state/schools.sqlite` (dataset `main`). The runner reuses `school_pipeline.flow` retrieval, preparation, transformations and destination; county discovery/checkpointing is in `school_pipeline/county.py`. The three-school configuration remains unchanged.

| Table | Rows |
|---|---:|
| schools | 762 |
| statistics | 45,868 |
| survey_observations | 84,610 |
| source_coverage | 3,048 |

762 distinct active GR school-unit codes across all 26 municipalities. School units are register entities, not necessarily distinct physical campuses. This is county-wide background data, not a representative selected dashboard sample or a ranking.

## Source coverage
| Source | Fetched | HTTP 404 / unavailable |
|---|---:|---:|
| Register details | 762 | 0 |
| GR statistics | 744 | 18 |
| Parent surveys | 732 | 30 |
| Pupil surveys | 664 | 98 |

No failed requests remained at load time. HTTP 404 means unavailable from that endpoint, not zero performance, no pupils or confirmed non-participation. Fetched survey data can still contain nulls or unresolved symbols. Parent observations: 38,064; pupil observations: 46,546. Do not pool respondent types or year groups.

Statistics preserve per-observation periods (2021/22–2025/26 where returned, with null periods retained), raw strings, rounding, suppression, missingness and source flags. Row counts include flagged and empty-array placeholder observations, not only numeric results. Teacher exclusions and unresolved survey scales remain interpretation limitations. Pupils per teacher and whole-school counts are not class sizes.

## Validation
- All nine unit tests passed after the shared retrieval header change.
- SQLite `PRAGMA integrity_check`: `ok`.
- Table counts exactly match normalized extraction counts.
- 762 unique schools, 26 distinct municipality codes.
- No statistics or survey observations without a matching school.
- Prefect flow finished `Completed`; dlt returned `LOADED`.
- SQLite lock warnings occurred during the load; automatic retries completed successfully. Independent final count and integrity checks passed.

No existing production database was present at load time; this run created the file at the agreed existing destination path. The runner backs up an existing database before subsequent replacements. Loading is whole-county snapshot replacement, not per-school replacement or append. A failed load is not guaranteed atomic across all tables; inspect validation and restore the pre-load backup if necessary.

## Diagnostics and changes
The initial detail extraction failed with `RemoteDisconnected`. A controlled comparison showed the old User-Agent value failed while the updated descriptive county-project value returned HTTP 200. The shared retriever was updated; register, statistics, parent and pupil probes then succeeded. Failed requests were retried using the saved county discovery manifest. The upstream/network reason for the header sensitivity is unknown.

Added `school_pipeline/county.py` and `tests/test_county.py`; changed only the User-Agent value in `school_pipeline/flow.py`. No AGENTS.md was found. Git metadata was unavailable, so a Git diff check could not run; new files were directly reviewed and syntax/test checks executed.

## Evidence and reproducibility
- Run: `outputs/runs/county_20261020T172656950841Z/`
- Source URLs and retrieval timestamps: `manifest.json` and `discovery_*.json` in the run directory.
- Sanitized register responses, statistics and survey JSON, normalized JSONL, `coverage.json`, `load_result.json`, `validation.json`: same directory.
- Final flow log: `outputs/county_resume.log`.
- Initial failed-run log: `outputs/county_run.log`.
- Tests: `outputs/county_tests.log`.
- Independent validation: `outputs/county_validation.json`.

Run with a Python environment containing the pinned pyproject dependencies:

```text
python -m school_pipeline.county
```

Resume a checkpoint (retries failed sources, reuses successful/unavailable ones):

```text
python -m school_pipeline.county --resume outputs/runs/county_20261020T172656950841Z
```

The workspace `.venv` lacked dependencies; this execution used the runtime-managed Python environment. Public network access may require runtime approval in another execution environment.

## Official sources
- Register: https://api.skolverket.se/skolenhetsregistret/v2/school-units
- Filter example: https://api.skolverket.se/skolenhetsregistret/v2/school-units?school_type=GR&status=AKTIV&municipality_code=0180
- Statistics and survey API documentation: https://api.skolverket.se/planned-educations/swagger-ui/index.html

This run did not collect school websites or third-party free-text reviews. Dated, sourced school-website evidence remains a core requirement for the selected parent-facing dashboard sample and must distinguish self-description from verified practice.
