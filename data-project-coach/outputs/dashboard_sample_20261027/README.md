# Provisional dashboard sample and availability — 27 October 2026

## Decision
Use five deliberately selected schools as a manageable first dashboard sample: Örjanskolan, Kristofferskolan, Pops Academy Stockholm, Karlslundsskolan and Rosenborgskolan. This is an analysis proposal, not a final user-approved sample. Selection uses reviewed explicit arts/music or named alternative-pedagogy evidence, not outcome values. It draws from the reviewed first batch plus the earlier pilot, not a systematic county-wide comparison. No county representativeness or quality judgement is claimed. Waldorf/music are overrepresented by the reviewed pool; do not generalise to all creative or alternative approaches. Five is an MVP feasibility choice, not a statistical sample-size result.

Keep schools with suppressed results in the sample: excluding them for missing outcomes would create avoidable selection bias. Multiple category labels are permitted. No academic-versus-creative binary or causal comparison.

## Park remaining questions, without forcing codes
Lilla Kulturama's 4–5 mapping, Lemshaga's current pedagogical applicability and Röllingby's substantive source remain open; targeted first-batch review is closed for now with explicit reopening criteria in `parked_cases.json`. This is not exhaustive website-review completion. Anne Frank and Lilla Akademien are reserve candidates pending earlier scope/identity conflicts. No new website requests were made in this analysis; existing source-access dates are retained. Collection permissions remain as documented in the source logs, not newly cleared.

## 2025/26 availability
| School | Pupils / teacher FTE | Teacher qualifications % | Year-9 merit | Vocational eligibility % |
|---|---:|---|---|---|
| Örjanskolan | 10.1 | Special exclusion flag (*) | Suppressed (..) | Suppressed (..) |
| Kristofferskolan | 10.4 | Special exclusion flag (*) | 276.3 | Rounded ~100 |
| Pops Academy Stockholm | 12.0 | 79.5 | 264.3 | Rounded ~100 |
| Karlslundsskolan | 13.1 | 61.3 | 252.8 | 86.6 |
| Rosenborgskolan | 12.7 | 71.3 | 236.9 | 87.2 |

Raw values, exact valueType flags, API links and reporting periods are preserved in `statistics_availability_2025_26.csv`. Numeric columns are populated only for EXISTS values; rounded, suppressed and special exclusions are not exact numbers or zero. No de-suppression or derived ranking. These are saved official observations, not freshly fetched current figures. Confirm official indicator definitions before final dashboard text: a common period alone does not ensure equal cohorts, contexts or denominators.

Register grades are recorded as GR years only: 1–9 for Örjanskolan, Kristofferskolan and Karlslund; 4–9 for Pops and Rosenborg. Absence of F in these GR arrays is not evidence that a school lacks preschool class. Rosenborg has another school form in the register; the statistics files use GR endpoints. Retain that distinction and verify each indicator's denominator before publication.

## Dashboard requirements to sketch next
1. School explorer: neutral school-name ordering; selected-sample notice, municipality/year-group filters once verified, approach labels with optional-pathway scope.
2. Evidence panel: exact short school quotation, actual title/access date, source link, project interpretation, confidence/review caveats. Reviewed is assistant source review, not verified practice.
3. Statistics panel: four indicators above, explicit period and scope, raw rounded notation, explanatory unavailable states. No best-school ranking or approach-effect claims.
4. Scope warning: whole-school statistics do not describe optional music participants; 2025/26 Pops statistics predate its announced autumn-2026 move. Shared school websites do not automatically establish every unit's approach.
5. No class-size chart: pupils per teacher FTE is not class size. No cross-school average or comparison of approach groups in this MVP.

## Next execution gates
- Confirm or adjust the provisional five-school sample with the user before treating it as final.
- Verify official definitions for merit value, teacher qualification flags, eligibility and pupils/teacher denominator; write display/missingness rules.
- Produce a low-fidelity dashboard sketch and choose BI versus React only after requirements are settled.
- Separately resolve database I/O, make a verified backup, reconcile existing pilot/staged IDs and evidence-type conventions, then use local Prefect/dlt for any approved load. Replacement snapshots must not be appended together. No DB accessed or changed here.
- Continue the requested county-wide collection/coding separately; it is not a prerequisite for the two-week dashboard.

## Audit
This analysis reuses immutable saved JSON and reviewed approach snapshots; it does not change original staged data or official files. `source_manifest.json` records hashes. `selected_approach_records.json` is a presentation subset, not a load file or new coding table. Ten inherited first-batch claims were not newly source-validated during the preceding follow-up; retain that provenance. The original evidence-type inconsistency is preserved, not silently normalised. Saved analysis outputs are in this directory only.
