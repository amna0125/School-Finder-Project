# Three-school website pilot

Retrieval date: 2026-10-20 (Europe/Stockholm; session began 19 October). Public sources only. This is a manual, bounded collection feasibility pilot, not a running ingestion pipeline.

## Selection and scope
Purposeful feasibility sample: active GR school units in Stockholms län whose own websites explicitly describe a creative, arts-based or alternative pedagogical approach; choose three distinct stated approaches and check identity against the official register. Selected: Kristofferskolan (Waldorf), Musikskolan Lilla Akademien (music), Stockholms Montessoriskola Anne Frank (Montessori). All three happen to be independent schools in Stockholm municipality. This is NOT representative of the county, municipalities or organizer types; no claims about prevalence or which approach is better are supported. Website accessibility influenced feasibility selection. Tags are non-exclusive, not an academic-versus-creative classification.

## Verified identities
| Code (string) | Register display name | Municipality | Register GR grades | Website scope | Status |
|---|---|---|---|---|---|
|98760751|Kristofferskolan, gr|0180|1–9|Pedagogy page describes school-wide Waldorf principles; website also includes upper-secondary content|Active; identity matched by register URL|
|36066067|Musikskolan Lilla Akademien|0180|1–9|Grundskola page explicitly F–9|Active; identity matched by register URL and Norrtullsgatan address|
|23498302|Stockholms Montessoriskola Anne Frank|0180|1–6|Homepage identifies Anne Frank as years 4–6 at Klippgatan 19B|Active; URL/address match; grade discrepancy OPEN|

Register detail URLs: https://api.skolverket.se/skolenhetsregistret/v2/school-units/98760751 ; https://api.skolverket.se/skolenhetsregistret/v2/school-units/36066067 ; https://api.skolverket.se/skolenhetsregistret/v2/school-units/23498302 . Raw responses saved in outputs/pilot_register_*.json. Preserve both grade descriptions for Anne Frank; do not overwrite the official value or assume historical statistics use the current website scope. Register orientationType is ALLMAN for Lilla Akademien and Anne Frank despite their explicit website profiles: this field is insufficient as the approach taxonomy.

## Website evidence
All excerpts below are school self-description, not independent verification of classroom practice. Page publication/update dates were not established; retrieval date is not a publication date. Keep source scope when displaying evidence.

### E01 — Kristofferskolan
- URL: https://kristofferskolan.se/waldorfpedagogik/pedagogiken-som-konst/
- Stated approach: Waldorf; creative learning.
- Excerpt: “Waldorfpedagogik bygger på en helhetssyn på världen och människan.”
- Supporting excerpt: “Skolan ska även främja ett livslångt lärande, väcka elevernas nyfikenhet och utveckla deras fantasi genom konst, lek och utforskande.”
- Scope: general Waldorf principles on the school's website; not a year-specific activity-frequency claim.
- Class/group pupil count: not found in inspected page; not proof that no other page publishes it.

### E02 — Musikskolan Lilla Akademien
- URL: https://lillaakademien.se/grundskola
- Stated approach: music integrated with compulsory-school subjects; individual instrument teaching; creative subjects.
- Excerpt: “Alla elever spelar ett instrument och får individuell undervisning på instrumentet varje vecka.”
- Supporting excerpt: “För att ytterligare förstärka den konstnärliga prägeln får alla elever undervisning i skapande ämnen som dans och konst, i syfte att ge fördjupad kontakt med andra kreativa uttrycksformer.”
- Group-structure excerpt: “Lilla Akademien erbjuder utbildning från förskoleklass till årskurs nio, med en klass per årskurs.”
- Scope: F–9 page. One class per year is NOT pupils per class. No numeric pupil count per class found in inspected pages.
- Context-only page https://lillaakademien.se/lilla-akademien states 450 pupils across grundskola, gymnasium and pre-college. Do NOT use that as the GR pupil count or divide it by year groups. Its promotional outcome ranking is not imported as an official metric.

### E03 — Stockholms Montessoriskola Anne Frank
- URL: https://www.stockholmsmontessoriskola.se/
- Stated approach: Montessori; mixed-age working; creative activities; nature studies.
- Excerpt: “Skolan bedriver Montessoripedagogik där även fritidshemmets verksamhet genomsyras av denna pedagogik.”
- Supporting excerpts: “Vi arbetar åldersblandat med barnet i centrum.”; “Naturstudier och skapande verksamhet är viktiga inslag i vår utbildning.”
- Scope: shared school-brand homepage covering BOTH Anne Frank and Färgargårdstorget units. These are shared descriptions, not separately observed unit-level practice. Annotate shared scope on every exported claim.
- Unit mapping corroboration: https://www.stockholmsmontessoriskola.se/skolan/4-6-klippgatan ; register address Klippgatan 19 B matches. Website explicitly separates F–3 at Färgargårdstorget and 4–6 at Anne Frank.
- Class/group pupil count: not found in inspected pages. Mixed-age working does not establish group size.

## Collection permissions and technical assessment
All inspected content pages returned HTTP 200 with public HTML and extractable text; no login, CAPTCHA or access-control bypass used. Static HTTP extraction appears feasible for these pages, but has not been implemented or scheduled. Navigation text must be stripped; scope must be reviewed manually.

Robots checks (saved raw responses):
- https://kristofferskolan.se/robots.txt — HTTP 200; User-agent * with empty Disallow. Inspected content path not disallowed.
- https://lillaakademien.se/robots.txt — HTTP 200; Squarespace rules covering * and several named crawlers restrict config/search/account/API and parameterized paths. /grundskola and /lilla-akademien are not among those restrictions. Re-parse current rules for the actual pipeline user agent before each collection.
- https://www.stockholmsmontessoriskola.se/robots.txt — HTTP 404 HTML, not a valid robots policy. This is not affirmative permission; recheck before automated collection.

No explicit content reuse licence or applicable collection terms have been established. Robots availability/non-blocking rules do not confer copyright permission. Limit dashboard content to short attributed excerpts and source links; assess terms before broader collection or republication. No contact details or pupil-level information belong in the analytical dataset. Raw register responses contain public staff contact fields; exclude those from downstream tables and published exports. Raw saved page files contain original HTML despite .txt suffixes; do not treat as already-cleaned text.

Proposed automated collection safeguards: URL allowlist, one request at a time, at least 2 seconds between requests per domain, cache raw responses, bounded retries only for transient errors, stop on 401/403/429 or challenges, never rotate identity to evade restrictions, no portal/login/search scraping. These are design requirements, not implemented features.

## Outcome and next milestone
Website evidence is usable for this small pilot. Numeric class sizes remain unavailable in inspected pages. Anne Frank grades need reconciliation. Do not compare its outcomes to year-9 schools or infer performance from missing year-9 data.

Next: retrieve statistics for these same three codes, produce metric/period/availability coverage, then implement local dlt ingestion under Prefect orchestration. Preserve raw values, approximation/suppression flags, reporting periods and source scope. Choose local storage explicitly before implementation (DuckDB remains a proposal). Defer dashboard technology until the coverage report is available.

Suggested tables: selected_school (official and website grades separate, mapping status); website_evidence (evidence_id, code, source_url, retrieval timestamp, page date nullable, excerpt, tags, self_report flag, scope); official_metric (code, metric, period, raw_value, parsed_value nullable, value_type, availability); collection_log (URL, retrieval timestamp, HTTP status, robots/terms assessment, raw-file reference). Multi-label tags require human review; do not automatically translate marketing into verified practice.

This memo supersedes the earlier source audit's recommendation to defer school website collection. That historical audit remains unchanged as a record of the previous scope.
