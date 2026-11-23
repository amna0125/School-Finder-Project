# Reviewed school-focus pilot — 21 October 2026

Saved `school_focus_profiles` in `.state/schools.sqlite`: four reviewed website claims covering three official school-unit IDs. These are assistant-reviewed school self-descriptions, not human approval or independently verified classroom practice. Multi-label records use (school_unit_code, category) as the merge key. Original candidate/coverage tables remain unchanged and describe the earlier automated pilot, not this follow-up review.

| Official GR directory name | ID | Category |
|---|---|---|
| Kristofferskolan, gr | 98760751 | Waldorf |
| Kristofferskolan, gr | 98760751 | Creative arts |
| Stockholms Montessoriskola Anne Frank | 23498302 | Montessori |
| Musikskolan Lilla Akademien | 36066067 | Music |

Sources, excerpts, dates and scope notes: `outputs/focus_review/reviewed_profiles.csv` and `.json`, also stored in the new database table. Saved raw public page responses are in the same folder. Note: `kristofferskolan_pedagogy.json` contains HTML despite its extension.

## Identity and scope
The live active GR directory for municipality 0180 names 36066067 Musikskolan Lilla Akademien. The existing database detail-derived name is Lilla Akademien Musikgymnasium. This is an unresolved discrepancy between sources, not evidence that the GR directory ID was wrong. Both names are retained in the profile table; the official `schools` table was not edited. Grundskola-specific evidence comes from https://lillaakademien.se/grundskola.

Anne Frank's shared homepage explicitly names two units (Anne Frank 4–6 and Färgargårdstorget F–3) and says the school uses Montessori pedagogy. The profile statement is shared; the prior register/website grade-range discrepancy remains unresolved. No historical cohort matching is implied.

Kristofferskolan's pedagogical page describes Waldorf and arts integration. It is shared across grundskola/gymnasium; not classroom-level evidence. Music as a distinct school focus was not assigned merely because the site lists music as a subject. Generic academic quality claims at any of these schools were not treated as an academic-specialist profile.

## Permissions and collection
Target hosts' robots.txt checked: Kristofferskolan allows these paths; Lilla Akademien's Squarespace exclusions do not exclude /grundskola; Anne Frank returns 404 for robots.txt. No login or access control bypass. Public page lookup and a small follow-up collection only. Full terms/legal assessment remains pending before bulk automation; robots is not legal permission. No county-wide crawl was performed.

## Execution and validation
Follow-up evidence was fetched with public fetch_url calls, exact excerpts checked locally against saved page text, and records merged using dlt. This follow-up merge was run directly, NOT as a new Prefect flow; the existing automated candidate pilot remains Prefect-orchestrated. A reproducible Prefect review-import workflow still needs implementation before routine county processing.

SQLite integrity_check: ok. No orphan profile IDs. Official row counts unchanged: schools 762; statistics 45,868; survey_observations 84,610. No source code changes or new unit tests in this follow-up.

## Remaining work
- Add resumable per-domain collection and a Prefect-orchestrated review import before expanding.
- Resolve remaining official-source name and year-range discrepancies.
- Review site terms, shared-unit scope and substantive evidence for further schools in batches.
- Keep unvisited sites not_reviewed; no explicit focus found requires actual scoped review.

Inspect using DB Browser for SQLite, Browse Data → school_focus_profiles, or:

```sql
SELECT school_name, school_unit_code, category, supporting_excerpt,
       source_url, retrieved_at, review_status, scope_note
FROM school_focus_profiles
ORDER BY school_name, category;
```
