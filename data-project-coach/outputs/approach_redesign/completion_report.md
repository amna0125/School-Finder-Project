# Approach-table replacement — completed 21 October 2026

## Result
Prefect flow `sticky-gazelle` completed. dlt staging load `1792591232.8176596` succeeded; staged records were compared exactly with the prepared pilot JSON, then copied in a SQLite transaction into the requested constrained tables.

- `Approach_evidence`: 4 records, exactly the eight requested fields.
- `Approach_codes`: 4 records, exactly the ten requested fields.
- Three pilot schools: Anne Frank (Montessori), Lilla Akademien (music), Kristofferskolan (Waldorf/Steiner and arts integration).
- 759 directory units have not been re-coded under this framework. Absence from Approach_codes is not a negative finding.
- Nine approved legacy focus tables removed. Their records, including 345 keyword candidates and historical coverage, remain in the backup.

## Safeguards and validation
Backup: `outputs/approach_redesign/migration_20261021T140032Z/schools_before_replacement.sqlite`.

Full row-content SHA-256 fingerprints and counts matched before/after for schools (762), statistics (45,868), survey_observations (84,610), source_coverage (3,048). Integrity check: `ok`; foreign_key_check: no violations. Official schema unchanged. The existing schools.school_unit_code column lacks a declared unique constraint, so school-ID membership is validated by the migration rather than a database foreign key. The codes-to-evidence composite foreign key enforces matching school IDs when foreign_keys is enabled.

All 17 existing tests passed in the tool-managed Python environment before migration. The workspace .venv lacked dependencies; its initial test attempt failed and is not counted as a pass. First migration rolled back because of the official-table foreign-key incompatibility. A later staging attempt failed on a filesystem rename permission error before live changes. The final fresh-run retry completed. Execution logs are retained.

## Evidence and review limitations
Codebook v1 was piloted on the three purposively selected schools; see `codebook_v1_draft.md` and `decision_log.md`. No material definition revision was required for these four direct-statement claims. This pilot does not test all seven categories or exhaust possible approaches at the pilot schools.

All quotations and actual page titles were checked against saved source snapshots; actual source access dates were confirmed in county checkpoints. No fresh source requests occurred during migration. Reviewed means assistant source-context and consistency review, not independent verification of practice. Shared-site, grade-range and Lilla Akademien identity caveats remain in the records. Terms reviews remain incomplete; accessibility is not reuse permission.

## Next county work
Use the seven-category codebook for scoped school-by-school review, keeping a separate collection log and decision log. The historical candidates are discovery aids only, not reviewed codes. Review official about/pedagogy/profile/education/value pages with Swedish and English concepts; record URLs, titles, source access times, permissions, scope and exclusions. Distinguish unvisited, missing website, inaccessible, and scoped review without clear evidence. Check permissions before deeper collection. Dashboard sample selection remains separate from county collection.

Do not rerun legacy website_focus/website_county loading commands: they can recreate deprecated tables. The new migration is deliberately one-off and refuses to rerun after replacement.

## Viewing and rollback
Open `.state/schools.sqlite` in DB Browser and choose either Approach table. Join school_id to schools.school_unit_code for names; the official Lilla Akademien name conflict is intentionally not silently changed.

Rollback is available by restoring the verified full backup only after closing database applications and backing up the current database. Restoring the full backup also restores the previous database state; it would discard any subsequent writes, so do not overwrite casually.

Machine-readable validation: `latest_validation.json`. Code review artifact: `migration.diff`; no Git metadata was present. Only one new source module was added: `school_pipeline/approach_migration.py`.
