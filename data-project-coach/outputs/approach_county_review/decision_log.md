# County approach review: first decisions and current blocker

## Scope and audit
759 remaining official units were inventoried, excluding the three loaded pilot units. See collection_log.jsonl and saved_page_inventory.jsonl. There are 1,175 saved page records across 667 units; 84 units have prior collection failures and 8 lack registered websites. These are collection states, NOT completed reviews. 215 units have old keyword candidates; none was promoted automatically.

## Review method
Read saved source context rather than old category assignments. Check unit identity, age/year-group scope, whether statements describe an ongoing educational approach, faithful short quotations, actual source access date, and actual page title. First lines of saved text are title candidates, not independently confirmed HTML titles: the old parser did not separately capture title metadata. Obtain a verifiable title before loading new evidence. Where saved pages are insufficient, find official school-specific pages using om oss/about us; pedagogik/pedagogy; undervisning/teaching; utbildning/education; profil/profile; skapande/creative; estetisk/arts; lärande/learning; värdegrund/values. Check robots, terms and access restrictions before deeper collection. Preserve failures and permissions as separate flags. No negative profile finding without a defined school-specific scoped review.

## First contextual review: Örjanskolan grund, 10661388
Saved source: https://orjanskolan.se/grundskola ; snapshot outputs/website_county/10661388_1.txt. Source date recorded by original checkpoint: 2026-10-21 (text-save timestamp follows fetch; not a new access). First text line: Grundskolan; actual HTML title still requires verification. Source explicitly welcomes readers to the grundskola and describes a school also including gymnasium. Registered unit is Örjanskolan grund; no grade-specific implementation verified.

Candidate quotation: “På Örjanskolan arbetar vi utifrån de nationella läro- och kursplanerna LGR 22 och GY 11/GY 25, samt Waldorfskolans kompletterande dokument En väg till frihet.”
Proposed category: Alternative pedagogy; Waldorf/Steiner; Explicit/High. National curriculum text alone is not the reason: the named supplementary Waldorf framework is substantive.

Candidate quotation: “Teoretiska, praktiska och konstnärliga ämnen vävs samman och är lika viktiga.”
Proposed category: Arts and creative learning; Arts integration; Explicit/High. Describes integration, not merely a subject list.

Candidate quotation: “Skolan ligger nära skog, hav och trädgård där naturen används som en självklar del av undervisningen.”
Proposed category: Outdoor, nature, or place-based learning; Nature in teaching; Explicit/High. Actual use in teaching, not proximity alone. Interpretation must not imply a quantified outdoor-teaching frequency.

Do NOT add a wellbeing code from the generic statement about cooperation with the pupil-health team. Do NOT turn the page's self-reported 20–25 class-size statement into official class-size data.

Reviewer: assistant contextual review of saved text, not verification of practice. All proposals remain Requires review pending verified source title and complete metadata validation. No records loaded.

## Borderline observations
Lärande Grundskola Skapa (10063280): old arts excerpt explicitly describes fritidsverksamheten. Do not apply it unqualified to compulsory-school teaching. Read other substantive descriptions before deciding categories.
Lilla Kulturama (10311303): old candidates include gymnasium material and provider statements naming Hammarby Sjöstad and Sundbyberg. Unit mapping must be resolved; provider copy alone cannot establish the registered unit's present approach.
Söderbymalmsskolan (10035236): saved targets are general municipal pages and admissions instructions. Not a school-specific scoped review; cannot record no clear evidence found.

## Blocker and preserved state
Two SQLite reads failed with sqlite3.OperationalError: disk I/O error, including explicit read-only URI access. Cause not established; do not attribute it to a lock or corruption without evidence. No database writes or fresh web requests were performed during this review. No migration or collector was rerun. Existing tables were not intentionally changed. Do not delete WAL/SHM/journal files or overwrite the database to work around the error. Resolve filesystem/database access safely before backing up and loading new records through local Prefect/dlt.

County coding, fresh collection, permission review and the final load remain unfinished. This audit is a persisted starting queue, not a claim that all 759 schools have been reviewed.


## Batch15 recovery and checkpoint, 29 October 2026
Recovered saved source/draft artifacts from interrupted run, validated exact quotes and next-ID ordering, appended15 evidence/14 codes with backups and duplicate-safe replay. See batch15_10schools_20261029/decision_log.md for scope decisions. Majtorp Requires review; do not transfer Rosenborg7–9 profiles. 163 documented outcomes,599 pending; not all resolved.


## Rule E: support groups at the school, 17 November 2026 (agreed with Amna)
Trigger: Amna's manual check of Fjällenskolan (15080815). Its Järfälla page says "Fjällenskolan har kommungemensamma integrerade grupper inom resursskoleklass", but the school was labelled No clear evidence under rule B. The codebook lists resource schools and special groups under Support, while reviews had also required a whole-school profile; that was stricter than the codebook.
Decision: code Support, inclusion, or wellbeing emphasis at S when the school's own page, or a shared page that names this school, states that the school has a resource group or class (resursgrupp, resursklass), a special teaching group (särskild undervisningsgrupp), small groups for pupils with special needs, or an NPF or autism group. Groups run by the municipality and hosted at the school count; the subcategory says so (e.g. "Resource group (municipality-run)"). Explicit stays for schools whose whole profile is support (e.g. a resource school).
Not counted: student health, a special educator on staff, extra adaptations and särskilt stöd in general, since every school must provide them by law.
Rule B still holds: a group at another unit on the same page is not applied to this school.
Process: keyword scan of saved page text for all 762 schools, candidates with quotes reviewed by Amna (yes/no) before anything is coded; then load, rebuild dbt.

### Rule E tightened, 18 November 2026 (agreed with Amna)
Basis: skollagen chapter 3 requires every school to give extra adaptations and special support. Under 3 kap. 11 § the principal may decide, for each pupil, that support is given one to one or in a special teaching group, which may be at another school. So every school must be able to give support in a smaller group, but no school is required to run a standing group.
- Explicit (E): the whole school is a resursskola, or the unit itself is the group (it only admits pupils who need special support).
- Supported (S): the school's own page, or a shared page sentence about this school, names a standing group or class at this school for pupils who need support (resursklass, särskild undervisningsgrupp, KSU/KÖSU/RSU, autism or language-disorder group, a named studio or small setting for pupils who need a smaller context). A staff role title naming the group on the school's own page counts; staff names are never stored.
- Not counted: support "in small groups or individually when needed"; extra adaptations; elevhälsa; special educators; generally small classes; flexible or mixed-age groups; two-teacher or multi-teacher staffing; differentiated, structured or visual-support teaching for all pupils; staff NPF training or a low-arousal approach; "access to" a group elsewhere; anpassad grundskola (a separate school form); groups for newly arrived pupils; a group whose purpose is not stated.
- Wellbeing programmes (Trivselledare, Olweus, PAX, IBIS and similar) are outside Rule E and unchanged.
- Existing Support codes for groups and teaching were re-checked against the same line (review workbook, sheet "Already coded").

## Second pass over every school's pages, 18 November 2026

- Fetched 2,324 pages for all 762 schools in a real browser (scrolled to the bottom; robots.txt respected), then searched for codebook terms and named programmes the school was not yet coded for: 367 hits at 269 schools. Pre-sorted into 97 review rows (doc "Second pass: missed approaches"); Amna reviewed them.
- Loaded 90 codes at 85 schools (ac_sp_*). 21 schools moved to Reviewed. Changes: second_pass_20261118/changes_20261118_sp.csv.
- Rules agreed:
  - A website saying staff are *trained* in a model (e.g. "personalen fortbildar sig inom PBS") is not the school's approach (Djurö not coded).
  - Grön Flagg / Skola för hållbar utveckling certificates count as Other stated profile, Supported. Munkmora's Grön Flagg code moved from Outdoor to Other stated profile.
  - Waldorf/Freinet schools that state cross-subject or thematic teaching get a Project code (Supported) in addition to Alternative pedagogy.
  - Named wellbeing programmes (PAX, Olweus, MVP, Trivselledare, Tåget, IBIS, Friends, PBS) count as Support even when the school already has a different Support code.
- Known limit: the crawl followed at most 3 subpages per school.
