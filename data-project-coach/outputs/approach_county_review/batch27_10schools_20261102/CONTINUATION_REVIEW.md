# Batch27 collection continuation — 2026-11-02

Status: collection/review in progress. No staging, load, replay or county-ledger checkpoint executed in this continuation. Batch28 not started. Do not start Batch29. Never rerun successful Batch23–26 mutations.

## Newly accessed sources
- franska_profile.html: https://www.franskaskolan.se/grundskolan/franska-profilen-spetsutbildning/ ; title `Franska profilen – Spetsutbildning – Franska Skolan`; HTTP200, same final URL, 100074 bytes. French specialization from year7, selective admission; retain year7–9 limitation. French-language exchanges and cultural visitor programme also described. Embedded named-pupil news not curated/followed.
- friberga_about.html: https://www.danderyd.se/skolor/fribergaskolan/om-oss/ ; title `Om oss – Danderyds kommun`; HTTP200 same final URL,38639 bytes. Years7–9. About page pupil count about560 differs from homepage about435: do not reconcile by assumption or treat either as comparable official statistic.
- friberga_idea.html: https://www.danderyd.se/skolor/fribergaskolan/om-oss/var-organisation/ ; title `Vår skolidé – Danderyds kommun`; HTTP200 same final URL,37330 bytes. Explicit strong international profile with Spain exchanges/Germany study trip. Choir at ceremonies alone does not establish sustained arts approach.
- friberga_health.html: https://www.danderyd.se/skolor/fribergaskolan/om-oss/motivation-och-halsa/ ; title `Motivation och Hälsa – Danderyds kommun`; HTTP200 same final URL,36503 bytes. Weekly Motivation och hälsa lesson uses Motivationslyftet; page says all pupils/staff/guardians. Effectiveness not verified.
- stper_platform.html: https://www.sigtuna.se/utbildning-och-barnomsorg/grundskola/grundskolor/st-pers-skola/arbetssatt-och-kvalitetsarbete/pedagogisk-plattform-barn-och-elever-1-16-ar.html ; title `Pedagogisk plattform barn och elever 1-16 år - Sigtuna kommun`; HTTP200 same final URL,66939 bytes. Municipal platform for all municipal schools/preschools; broad learner agency/creativity/accessible-learning principles not automatically a distinctive school-specific approach. Full concluding body still needs inspection if used.
- husby_browser_excerpt.json: ordinary browser_read(main) succeeded on registered URL; actual title and minimal literal teaching excerpts saved, no staff/children curated. Browser page current F–9, buildings F–3 and4–9. Keep husby.html original bytes as failed decoding, not usable quotation source. Saved JSON is an excerpt transcription, not raw HTML.

## Official metadata checked read-only
Official grades_json (no F in these arrays):
41955701 Järvastadens skola1–3;42149666 Husbygårdsskolan F-9 1–9;42179975 Farsta Strandskolan1–3;42202683 Kungsholmens friskola1–6;42215279 S:t Pers skola1–6;42328518 Franska Skolan/Ecole francaise1–9;42434583 Brunns skola1–9;42601396 Trångsundsskolan1–9;42912378 Vinsta grundskola östra1–6;42986451 Fribergaskolan7–9.

## Working decisions, not staged outcomes
- Järva: likely scoped no-clear; school-specific text must be fully checked before finalizing. Expansion future, not current middle-school scope.
- Husby: concrete school-wide flerlärarsystem/high staffing plus common lesson structure; consider Supported/Medium learning-environment emphasis with two excerpts, not verified staffing metric or effectiveness. Do not conflate high staffing with class size.
- Farsta: school-specific page thematic/interdisciplinary approach explicitly pervades operation, shaped by pupil questions/interests; supports inquiry category. Concrete arts integration described (theoretical and practical-aesthetic subjects within themes), assess whether separate arts category warranted rather than creative adjective alone. Preschool homepage project approach excluded. Target official1–3.
- Kungsholmen: preserve permission blocker, AI crawler disallow. No content retrieval, no code. Search discovery not evidence.
- S:t Per: generic municipal platform and work-methods wording insufficient for firm school-specific category so far. Need school body check before scoped-no-clear outcome.
- Franska: language/international profile candidate; French spets year7–9 only, selective, not all compulsory pupils. Avoid transfer from gymnasium. No outcome/news evidence.
- Brunn: literary themes across all subjects potentially Other stated profile/literacy emphasis; ordinary literacy duties alone insufficient. Inspect full context before final. KSU autism groups not school-wide inclusion profile; nearby nature not outdoor pedagogy.
- Trångsund: about section read. Broad health/movement/accessible instruction wording lacks concrete distinctive school-specific model so far. Municipal common school rules are not specific profile. Consider uncertain uncoded; do not infer sports profile.
- Vinsta: literal `Vi har ett tydligt fokus på kultur och kreativitet genom vårt arbete med Skapande skola.` follows `Vinsta grundskola består av två enheter. Årskurs 4–9 på Vinsta grundskola västra. Årskurs F–6 på Vinsta grundskola östra.` Shared-unit wording leaves applicability to east alone unresolved. Retain Uncertain/no firm arts code pending unit-scope clarification. Research participation not pedagogy.
- Friberga: explicit international profile plus named weekly wellbeing method candidates. Choir at ceremonies alone excluded from firm arts label. Pupil-count disagreement kept separate.

## Resume
Finish small text slices for Järva/S:t Per/Brunn and Farsta/Husby borderline decisions. Create new Batch27 builder only after inspecting applicable validation and collection fields; do not mechanically inherit prior narrative. Staging selection must be ten pending IDs from after_batch26 ledger. Build once, inspect all new code/diff, append/replay/test/checkpoint separately with exact incoming-ID parameterized target validation. Then Batch28. Björkhaga43238662 terms_review_required: no content fetching pending permission review.

The earlier user question about clear versus unclear scope still has no reconciled count. Approach outcome totals cannot answer it. County ledger remains273 documented/489 pending as last independently verified Batch26 checkpoint, not updated by this note.
