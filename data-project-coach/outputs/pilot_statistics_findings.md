# Three-school official-statistics pilot

Retrieved 20 October 2026. Public Skolverket Planned Education v4 GR endpoints; all three returned HTTP 200 and status OK. This is a bounded extraction and analysis pilot, not a dlt/Prefect pipeline. Website evidence remains in `website_pilot_findings.md`; no new website collection was performed here.

## Comparable-period snapshot: 2025/26

| Measure | Kristofferskolan | Musikskolan Lilla Akademien | Anne Frank |
|---|---|---|---|
| GR pupils, approximate | cirka 560 | cirka 250 | cirka 50 |
| Pupils per teacher FTE | 10.4 | 11.3 | 14.6 |
| Certified and qualified teachers (%) | * — special exclusion flag | 67.2 | 63.1 |
| Average year-9 merit value | 276.3 | 303.4 | No observation; no current year 9 |
| Year-9 vocational-program eligibility (%) | ~100 — rounded | 100.0 | No observation; no current year 9 |
| Pupils per class/group | Not found in inspected website pages | Not found in inspected website pages | Not found in inspected website pages |

Kristofferskolan qualification valueType is `TEACHERS_EXCLUDED_DUE_TO_NO_REQUIRED_LEGITIMATION`. Do not show this as zero, as an ordinary missing percentage, or as evidence of unqualified teaching. The precise applicability of the exclusion needs confirmation against current official definitions before a parent-facing explanation is finalized.

Kristofferskolan eligibility valueType is `ROUNDED_OFF_DUE_TO_FEW_PUPILS_NOT_ELIGIBLE`. Preserve ~100; do not convert it to exact 100 or infer the underlying count.

## Year-6 coverage check

Latest dated all-subject pass-share observations returned for Lilla Akademien and Anne Frank are 2024/25: Lilla Akademien 100.0%; Anne Frank `..` with `OMITTED_DUE_TO_BASED_ON_FEW_PUPILS`. Kristofferskolan returns a null value with MISSING and no period, not a dated zero. There is no usable three-school numeric comparison on this metric. Keep it secondary or exclude it from the initial comparison chart. Do not reconstruct suppressed results.

## Interpretation and dashboard requirements

- The sample is purposeful, small and non-representative; all three are independent schools in Stockholm municipality. It supports exploration, not county-wide conclusions or causal claims about pedagogy.
- Educational approaches are school self-descriptions. Preserve supporting excerpts, retrieval dates, URLs and scope from the website pilot; do not infer an approach from scores.
- Pupils per teacher FTE is not class size. Whole-school GR pupil totals are approximate and cannot be divided by year groups to estimate class sizes. The school-wide 450-pupil website claim for Lilla Akademien covers other educational stages and is not comparable to this GR statistic.
- Keep reporting period visible beside each metric. Year-6 2024/25 measures must not silently appear as 2025/26.
- Anne Frank has an unresolved register (1–6) versus website (4–6) grade discrepancy. The current school-unit code matches, but historical cohort scope is not established. Empty year-9 arrays are retained as empty-source status; current grade evidence explains non-applicability, not historical performance.
- Teacher qualification means certified and qualified in at least one teaching subject under the official definition, not qualification in every subject taught. Confirm detailed exclusions before public display.
- Merit values and eligibility describe cohorts and may reflect admissions, pupil composition and other contextual differences. These data do not identify teaching effectiveness or show one approach is better.
- Use side-by-side school cards with evidence links, period labels and explicit status badges; no overall ranking or composite score. For numeric plots, exclude flagged/rounded observations from exact-value calculations rather than silently coercing them.

## Deliverables and validation

- `pilot_statistics_kristofferskolan.json`, `pilot_statistics_lillaakademien.json`, `pilot_statistics_annefrank.json`: raw responses.
- `pilot_metrics_long.csv`: selected six metrics, all returned periods, plus explicit empty-array rows. Raw value, numeric value where exact, valueType, source URL and retrieval date retained.
- `pilot_comparison_2025_26.csv`: same-period snapshot with source statuses; class-size gaps explicit. Website evidence is not yet joined into this CSV.
- Local checks passed: response status and school-unit identity; unique school/metric/period keys; non-EXISTS flags cannot acquire numeric values; approximate pupil counts and ~100 stay nonnumeric; CSV write/read row-count round trips. These checks validate extraction structure, not the truth of source measurements or official metric definitions.

## Next implementation milestone

Build the local dlt extraction and Prefect flow for this allowlisted three-school sample, including website evidence as a core dataset. Before code changes, inspect project instructions and manifests; choose a local destination (DuckDB is proposed, not confirmed). Preserve raw snapshots, normalize metrics with statuses, export scoped website evidence, join only by verified school-unit mappings, and test missingness/rounding and scope handling. Recheck robots and applicable terms before automated website requests. Do not expand to full-county ingestion or choose the dashboard UI yet.

## Public sources

- https://api.skolverket.se/planned-educations/v4/school-units/98760751/statistics/gr
- https://api.skolverket.se/planned-educations/v4/school-units/36066067/statistics/gr
- https://api.skolverket.se/planned-educations/v4/school-units/23498302/statistics/gr
- Metric-definition source previously inspected: https://www.skolverket.se/download/18.10ca3e4c19b2c04f0f06255/1766060452967/Variabellista_aktuell_201214_extern.xlsx (older terminology; recheck exceptions before publication).
