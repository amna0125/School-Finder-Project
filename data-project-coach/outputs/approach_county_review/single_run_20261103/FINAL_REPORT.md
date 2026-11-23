# County approach review — single run, 2026-11-03

## Result
All 762 school units in the county now have a recorded outcome. Ledger: `county_progress_20261103_after_chunk19.csv`.

| Outcome | Schools |
|---|---|
| Reviewed claim (has codes) | 410 |
| No clear evidence in scoped review | 180 |
| Blocked - requires review | 87 |
| Uncertain evidence - requires review | 85 |
| **Total** | **762** |

Database totals: 669 evidence rows and 550 codes (405 Explicit/High, 145 Supported/Medium).

| Category | Schools coded |
|---|---|
| Support, inclusion, or wellbeing emphasis | 157 |
| Other stated profile | 120 |
| Language, international, or intercultural profile | 61 |
| Outdoor, nature, or place-based learning | 61 |
| Arts and creative learning | 57 |
| Alternative pedagogy | 41 |
| Project- or inquiry-based learning | 39 |

A school can have several categories.

## How it ran
- Batches 27–29 were loaded as they were. Review labels were then normalised to four outcomes (see `label_mapping.json`).
- The remaining 459 schools were reviewed in 19 chunks of up to 25 schools. Each chunk was validated (every quote checked against the saved page text), loaded through `append_batch`, and checked for exact staging/target match and preservation of earlier records.
- Saves went to the PC after every two chunks, with a database backup taken before each extract in `.state/backups_claude/`.
- Per instructions, inaccessible, no-website and terms cases were flagged only; no alternative pages were hunted for. One school (Maria Elementarskola) was re-fetched once after a temporary rate-limit error.

## Codebook rules applied
Public pages only; robots.txt and terms obeyed; no personal names; short faithful quotes; school claims are not verified practice; nothing inferred from a school's name; provider-only copy kept as Uncertain unless the unit page confirms it.

## Joint review list
`joint_review_list_20261103.csv` holds 187 rows with blank columns for the joint decision:
- Group 1, flagged (172): 87 Blocked and 85 Uncertain, by reason. Largest groups: source inaccessible (34), unit scope unclear (27), school-specific source not found (26), provider-level source only (26), isolated / generic claim (29).
- Group 2, reviewed with a caveat (15): coded schools from earlier batches whose notes say follow-ups or scope caveats remain.
- 52 Uncertain rows from batches 1–29 had no reason category in the ledger. Their reason is suggested from the note and marked `suggested from note` in `reason_source`.

Specific cases worth looking at together: Mullekojan unit check; Nya Enskede (registered URL redirects to Gamla Enskede); IES, RWS, Täby Friskola and Viktor Rydberg units with provider-only pages; Kevingeskolan and Resursskola Sjötorp (pages describe another unit at the same site).

## Limits
Outcomes describe what public school websites say, not observed teaching. "No clear evidence" means nothing distinctive was found on the pages collected, not that the school has no approach.

## Update: follow-up on blocked sources (2026-11-03, joint review step 1)
Amna approved one pass to find current official pages for 74 blocked schools with missing, broken or non-specific sources. Pages were found from municipal sitemaps, school listings and a few searches limited to municipal sites. robots.txt was obeyed throughout. Files are in `single_run_20261103/followup/`, and the ledger is `county_progress_20261103_after_followup_blocked.csv`.

- 72 schools were re-collected: 34 now Reviewed claim, 25 No clear evidence, 1 Uncertain, and 12 still Blocked.
- Nya Enskede skola now has its own page (new 7–9 school), which resolves the earlier redirect issue.
- County totals are now: Reviewed claim 444, No clear evidence 205, Blocked 27, Uncertain 86. The database holds 713 evidence rows and 594 codes.
- The joint review list now has 128 rows.
