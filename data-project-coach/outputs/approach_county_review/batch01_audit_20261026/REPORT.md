# Batch 01 — scoped evidence review and validation

Review date: 26 October 2026. Reviewer: assistant (not independent human verification).

## Scope and selection
Retained the existing reproducible selection: first 20 refreshed official units by school ID. This is a workflow-validation batch, not a representative county sample or the dashboard sample. Reviewed contextual teaching/profile material from a 40-page saved-source inventory. Navigation, contact information and broad news aggregations are not evidence of approach; the long Kunskapsskolan news aggregation was excluded from firm claims. This is not an exhaustive reading or discovery review of each website. No fresh web requests or database load occurred. Evidence access dates remain 21 October 2026, not the review date.

## Results
- 20 school-level decisions documented; none marked exhaustive website review complete.
- 15 staged evidence records linked to 15 codes.
- 10 Reviewed claims across six schools; five Requires review claims are uncertain notes, not firm labels.
- Six schools have reviewed claims with coverage limits; four need school-specific source discovery; six have unresolved identity/unit scope; two have dated-source issues; two have no clear evidence in the scoped pages only.

| School | Reviewed school-stated approach / interpreted category | Important scope |
|---|---|---|
| Lärande Grundskola Skapa | Interdisciplinary assignments — Project- or inquiry-based learning | Illustrative school-day example, not observed practice; exclude fritids arts |
| Örjanskolan grund | Waldorf; arts integration; nature used in teaching | Explicit grundskola source; no inference about frequency or effectiveness |
| Karlslundsskolan | Music — Arts and creative learning | Optional pathway years 4–9, not all pupils |
| Kunskapsskolan Saltsjöbaden | Personalised learning/coaching — Other stated profile | Individual goals and personal tutor; not a named alternative pedagogy |
| Rosenborgskolan | Music; sport; theoretical/leadership pathways | Years 7–9, not universal provision; sports club membership required for sport |
| Vittra Östertälje | Real-world projects/themes — Project- or inquiry-based learning | Provider concept explicitly presented on this school's landing page |

Five uncertain notes: Pops Academy Stockholm (provider/unit applicability), Akers Friskola (dated Olweus wording), Brage (current resource-school versus registered name/scope), IES Solna and IES Täby (shared provider page, no established unit applicability). All are Unclear/Low and Requires review. No firm label should be displayed from these records.

## Validation executed
`validation.json` records the current checks, not inherited claims:
- Exact quotes and source URL/title/access-date agreement with saved collection metadata: pass for all 15.
- Official directory IDs, same-school evidence links, unique record IDs and seven-category controlled values: pass.
- Level/confidence consistency and uncertain-claim safeguards: pass.
- SQLite read-only quick_check: ok.
- Live counts: 762 schools; 45,868 statistics; 84,610 survey observations; 3,048 source coverage; four Approach_evidence; four Approach_codes.
- Database main-file SHA-256 unchanged before/after validation. No writes were made to it.

## Artifacts
All files are in `outputs/approach_county_review/batch01_audit_20261026/`:
- `review_log.csv`: 20 decisions, exclusions and next actions.
- `pages_reviewed.csv`: 40 saved page records, URLs, actual titles/access dates, text hashes and carried-forward permissions/robots metadata.
- `Approach_evidence.staged.json` and `Approach_codes.staged.json`: 15 linked records each.
- `selection.json`: preserved selection.
- `decision_log.md`: school-level boundary decisions.
- `validation.json`: executed checks and database baseline.

Previous `batch01/` triage and historical source snapshots remain untouched. No pipeline code or official data changed. Git revision/diff was unavailable in the command environment; this is an artifact-only audit with source hashes rather than a code revision review.

## Next gate
Do not bulk-load this entire stage as confirmed labels. First resolve uncertain claims or keep them as notes; follow the per-school discovery tasks; review permission terms where unresolved. Before eventual loading, back up the database and validate the selected reviewed records through Prefect/dlt. The 10 Reviewed records have passed saved-source validation but still carry the documented coverage limits. No implementation or educational-quality claim is independently verified.

Robots records do not constitute legal reuse permission. Only short quotations and source links are retained. Two no-clear-evidence outcomes apply only to the scoped saved pages, not to the school as a whole. Website omission is never evidence of absence.
