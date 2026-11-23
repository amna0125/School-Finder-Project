# To-do: county evidence review and dashboard preparation

Status: open. Saved at the user's request after the fresh collection pass. Work on demand; this is not a scheduled task.

## Current baseline
- 759 remaining units have refresh checkpoints: 574 with fresh pages, 170 inaccessible, 7 paused for terms review, 8 without registered websites.
- 1,061 fresh pages; 3 lack HTML titles.
- Live Approach_evidence and Approach_codes each contain only four pilot records across three schools. Collection is not completed coding.

## 1. Immediate priority: review and validate a 20–30-school batch
- [ ] Select varied providers and page types to test the wider-review workflow. This is not the dashboard sample.
- [ ] Confirm official school ID, unit identity, page scope and year groups.
- [ ] Read source statements in context against the seven-category codebook; use saved pages when sufficient.
- [ ] Record short faithful quotations, actual source URLs/titles/access dates and contextual interpretation in Approach_evidence.
- [ ] Record supported codes and evidence links in Approach_codes. Multiple categories are allowed; do not automatically promote keyword candidates.
- [ ] Exclude ordinary subject lists, generic promotion, isolated activities and compulsory policy wording as stand-alone approach evidence.
- [ ] Keep ambiguous evidence Requires review; identify the reviewer and unresolved issues. Reviewed does not verify teaching practice.
- [ ] Record borderline decisions; revise unclear definitions and re-code affected records if definitions materially change.

## 2. Continue county review and resolve collection gaps
- [ ] Extend contextual review across the 574 schools with fresh pages.
- [ ] Find current official URLs for 170 inaccessible units; use browser follow-up where appropriate without bypassing restrictions.
- [ ] Assess the 7 terms-review cases before further collection.
- [ ] Search attributable official school/provider pages for the 8 units without registered websites.
- [ ] Verify the 3 missing titles where possible; never invent titles or access dates.
- [ ] Maintain school-by-school collection and decision logs, including pages reviewed, permissions, exclusions, identity ambiguity and failures.
- [ ] Distinguish unvisited, missing website, inaccessible, and scoped review with no clear public evidence. Do not infer an approach from omission.

## 3. Validate and load reviewed batches
- [ ] Inspect current files and applicable project instructions before code changes; preserve unrelated work.
- [ ] Back up SQLite before each load.
- [ ] Validate quotations, metadata, school IDs, controlled values and evidence-to-code school agreement.
- [ ] Load through local Prefect/dlt, retaining only Approach_evidence and Approach_codes as live approach tables. Do not rerun legacy collectors that recreate deprecated tables.
- [ ] Independently check loaded records, joins, database integrity and unchanged official-data fingerprints/counts.
- [ ] Report reviewed, unresolved and not-yet-reviewed coverage separately; do not equate successful collection with completed coding.

## 4. Dashboard sample and analysis
- [ ] Explicitly select a sample prioritising creative, arts-based or alternative approaches, separately from county collection.
- [ ] Document inclusion criteria; do not claim county representativeness.
- [ ] Join by official school IDs to comparable outcomes, teacher qualifications and teacher-resource statistics.
- [ ] Assess missingness, suppression, reporting periods, year-group differences and definitions before choosing metrics or visualisations.
- [ ] Keep class/group size distinct from pupils per teacher and whole-school counts.
- [ ] Show school wording, project interpretation, quotes and source links alongside labels. No quality rankings or causal claims.
- [ ] Define dashboard requirements before choosing BI versus React/backend.

## Existing working artifacts
- outputs/approach_county_review/fresh/
- outputs/approach_county_review/refresh_coverage.csv
- outputs/approach_county_review/collection_log.jsonl
- outputs/approach_county_review/decision_log.md
- outputs/approach_redesign/completion_report.md

Recheck current database/file state when resuming; this to-do records the known baseline, not independent proof of later completion.
