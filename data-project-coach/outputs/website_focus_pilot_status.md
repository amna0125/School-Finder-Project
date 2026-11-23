# Website focus collection: pilot status

Approved taxonomy (non-exclusive): explicit academic/subject-specialist profile; creative/visual/performing arts; music; Montessori; Waldorf; other explicitly named pedagogy; sport/physical activity; language/international; other explicit focus.

## Saved tables in .state/schools.sqlite
- school_focus_coverage: 762 school-unit records, including school_unit_code, school_name, registered source URL and collection_status. Eight units have no registered website. Only the three configured pilot units were attempted. Others remain not_reviewed or missing_registered_website.
- school_focus_evidence: four UNCONFIRMED candidate excerpts. review_status=candidate_needs_review. Each records the school ID/name, source URL, UTC retrieval date, proposed category, excerpt and school-self-description caveat.

Do not use candidate evidence as confirmed school labels. Keywords and headings alone are inadequate. No confirmed school-profile table has been produced yet. No county-wide website classification has been completed.

## Pilot findings
- 23498302 Anne Frank: registered landing page fetched; Montessori candidate is only a title. Unit-specific scope remains unresolved on a shared website.
- 98760751 Kristofferskolan: registered landing page fetched; arts/music/Waldorf candidates are headings. Need substantive profile-page excerpts.
- 36066067: collection stopped with ValueError (cross-host redirect/collection validation needs investigation). No bypass attempted. Database name is Lilla Akademien Musikgymnasium, inconsistent with intended grundskola sample label: verify the official unit identity before classification.
- Two school records have missing names; preserve missingness and reconcile against official discovery evidence.

## Technical implementation and validation
school_pipeline/website_focus.py: local Prefect pilot with robots.txt checks, conservative host-change stopping, bounded public GETs, dated saved text and dlt loading into separate tables. No login, challenge bypass or existing official-table replacement. Robots permission is not a complete terms/legal assessment. Terms have NOT yet been reviewed; wider collection requires that review and redirect/destination permission checks.

New tests: tests/test_website_focus.py. All 13 tests passed; log outputs/website_focus_tests.log. Flow Completed; log outputs/website_focus_run.log. SQLite integrity_check=ok after load; official counts unchanged: schools 762, statistics 45,868, surveys 84,610. Git metadata absent, so git diff inspection unavailable. No AGENTS.md found.

Pilot JSON and page text: outputs/website_focus_pilot/.

## Next steps
1. Resolve official unit identity, missing names and shared-site scope.
2. Review site terms and destination robots rules for approved redirects.
3. Collect a small number of relevant school-specific profile/pedagogy pages; retain substantive excerpts and exact final URLs.
4. Human-review categories and scope, recording confirmed/rejected/uncertain decisions. Never infer academic emphasis from grades or generic quality claims.
5. Expand in resumable domain-paced batches for the requested county scope; do not overwrite reviewed evidence with pilot reruns. Current pilot replaces its two pilot tables and is not yet a resumable county collector.

Absence of a keyword on one landing page is NOT absence of a school profile. No overall ranking or binary academic-versus-creative label is produced.
