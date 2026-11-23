# County-wide school website collection — 21 October 2026

## Outcome
A bounded website collection was attempted for all 762 active grundskola units in the existing Stockholm County register. Two Prefect runs completed; the second retried unresolved robots responses with safe bounded redirect handling. Each school has a durable checkpoint. dlt merged separate county tables into `.state/schools.sqlite`.

| Status | School units |
|---|---:|
| Pages fetched; category candidates require review |216|
| Pages fetched; no candidate detected, review still required |454|
| Collection failed or permission handling needs follow-up |84|
| Missing registered website |8|
| Total |762|

1,183 page retrieval records (not necessarily unique URLs) and 345 unique candidate excerpts. These are NOT 345 confirmed focus classifications. No candidate detected is NOT no explicit focus found. No school was assigned that negative conclusion automatically.

## Tables and exports
- `school_focus_county_coverage`: 762 school-unit records including ID, official database name, registered URL, status, page metadata and errors. Nested lists may be represented by dlt child tables; full nested records are also in coverage.json.
- `school_focus_county_candidates`: 345 unique suggestions with ID, school name, category, excerpt, exact source URL, retrieval time, self-description claim type, and candidate review status.
- `school_focus_profiles`: existing four reviewed profile claims across three schools; untouched.
- `outputs/website_county/coverage.csv`: easy-to-open overview.
- `outputs/website_county/candidate_evidence.csv`: evidence review queue.
- `outputs/website_county/validation.json`: validation and failure details.
- `outputs/website_county_run.log` and `outputs/website_county_tests.log`: execution evidence.

Use DB Browser for SQLite → Browse Data → the relevant table. Example:

```sql
SELECT school_unit_code, school_name, category, supporting_excerpt,
       source_url, retrieved_at, review_status
FROM school_focus_county_candidates
ORDER BY school_name, category;
```

## Collection method and permissions
Public HTTP(S) only, no authentication or access-control bypass. DNS public-address checks, standard ports only, bounded redirects, response-size and time limits, TLS verification. Target paths checked against robots before page requests. robots redirects followed with validated public destinations; missing robots (404) recorded rather than treated as legal clearance. Explicit crawl delays were deferred for manual scheduling; disallowed targets not fetched. Per-host serialization with a 0.6-second minimum interval and eight worker threads across hosts. At most the registered landing page and two relevant internal pages per unit. Deep municipal paths scoped to descendants to reduce cross-school collection.

Terms-link detection is rudimentary, NOT a complete legal assessment: detected terms links paused follow-up crawling beyond the landing page, while no detected link is not permission. Review terms and shared-unit scope before deeper collection or publishing claims. Text snapshots and robots responses are saved. First-attempt failed checkpoints retained under first_attempt/.

## Limitations and review work
- Candidate regex terms can refer to ordinary curriculum subjects, another school on a shared site, or historical content. Review substantive self-description and unit applicability before promotion.
- Narrow academic-specialist matching found only one candidate; this is not evidence that only one school has such a profile. Generic academic success language deliberately does not qualify.
- The ninth category, other explicit focus, requires contextual manual discovery; there is no exhaustive automatic detector. Other categories also have language/wording coverage gaps.
- Existing extractor keeps the first matching line per category per page and suppresses very short matches. Relevant content elsewhere may be missed. Limited pages and JavaScript-rendered content can also hide evidence.
- 454 fetched units without candidates remain needs_review. Do not label them mainstream/no focus.
- 84 failed units: 41 HTTP 404; 12 malformed/unsafe registered URLs; 11 unresolved robots; remaining DNS, timeout, TLS, redirect, crawl-delay or disallow issues. Registered URLs may be stale. No certificate bypass was attempted.
- Two existing official school names are null; missing names have not been invented or silently corrected. Identity reconciliation remains a separate step.
- No county candidate has been promoted to a reviewed profile in this run. School self-descriptions are not independently verified teaching practice, and categories are non-exclusive, not rankings or causal explanations.

## Validation
17 unit tests passed, including four new tests for link scope, terms detection, external-link exclusion and no automatic redirects. Tests are not exhaustive production security/permission validation. No Git metadata exists, so no Git diff was available; changes were confined to new county runner and tests, plus output artifacts. Localized follow-up edits added bounded robots redirect handling and evidence-ID deduplication; tests rerun successfully afterward.

SQLite integrity_check = ok; no orphan county coverage/candidate IDs. Exact counts matched saved JSON: coverage 762, unique candidates 345. Preserved counts: schools 762; statistics 45,868; survey_observations 84,610; source_coverage 3,048; reviewed school_focus_profiles 4.

## Re-run
`python3 -m school_pipeline.website_county`

Existing per-unit checkpoints are skipped; aggregates are rebuilt and merged by primary key. This is a resumable collection, not an automatic freshness refresh. Retire/checkpoint a failed unit deliberately before retrying it; preserve previous attempts for audit. Review and import workflow for confirmed claims still needs implementation under Prefect.
