# Educational approach codebook and replacement plan — version 1 draft

Status: proposed framework; not yet piloted under this version or loaded into SQLite. Replaces keyword-led focus classification. Scope remains the 762 previously requested official school units; county directory inclusion is the collection selection rationale, not evidence of a profile or a representative dashboard sample. Select the dashboard sample separately and transparently.

## Controlled framework
Use the following exact category values. Categories are non-exclusive descriptions of public school statements, never quality ratings.

| Category | Include | Exclude / caution |
|---|---|---|
| Arts and creative learning | Explicit arts profile or concrete description of arts integration or sustained creative learning; subcategories music, visual arts, drama, dance, design, arts integration | Ordinary subject list, occasional performance or promotional word creative alone |
| Alternative pedagogy | Explicit named model, or clearly attributed inspired adaptation; subcategories Montessori, Waldorf/Steiner, Reggio Emilia-inspired, Freinet, other named model | School name alone; infer neither fidelity nor implementation; preserve inspired qualifier |
| Project- or inquiry-based learning | Sustained inquiry, interdisciplinary projects or problem-based learning described as an approach | Single project/event or generic curiosity language |
| Outdoor, nature, or place-based learning | Structured outdoor/environmental education or local-setting learning as an approach | Playground, nearby park or occasional excursion alone |
| Language, international, or intercultural profile | Explicit bilingual/international/language/intercultural emphasis; record particular language/model when stated | Ordinary language subjects or diverse intake alone |
| Support, inclusion, or wellbeing emphasis | Explicitly stated approach with concrete practices, routines or model and an identifiable emphasis | Generic safe-school promises, mandatory policy wording or ordinary statutory duties alone; no inference about diagnosed needs |
| Other stated profile | Clearly described profile outside the above; subcategory must name it, e.g. subject specialization or sport | Generic academic quality/results claims; do not infer approach from statistics |

## Evidence level and review status
- Explicit / High: direct school statement of the approach or named pedagogy, with sufficiently clear unit applicability and context. High measures support for the public statement, not effectiveness or truth in practice.
- Supported / Medium: multiple concrete descriptions jointly support a category but no explicit self-label. An isolated mention is insufficient. Record every supporting excerpt; represent multiple evidence links as repeated code rows with distinct code_id and the same school/category/subcategory, and explain the shared coding decision in coder_note. Deduplicate labels when displaying or counting schools.
- Unclear / Low: broad, promotional, outdated or ambiguous unit scope. Treat as a note, not a firm dashboard label. Do not automatically promote to Supported.
- Reviewed: substantive coding and scope review completed under this codebook; identify assistant review versus human review in coder_note. Requires review: provisional or unresolved. Never equate reviewed with independently verified practice.
- Default firm-label display: Reviewed AND coding_level in Explicit/Supported. Show quotations, source links, source date and project interpretation. Unclear and Requires review are separate notes/queues.

## Exact requested SQLite schemas
Approach_evidence:
- evidence_id TEXT PRIMARY KEY
- school_id TEXT NOT NULL (official schools.school_unit_code join key)
- source_url TEXT NOT NULL (exact page/document URL)
- page_title TEXT (actual source title; NULL with explanation if unavailable, not invented)
- accessed_date TEXT NOT NULL (ISO date of actual source access, not re-coding date)
- quoted_text TEXT NOT NULL (short faithful excerpt; normally 1–3 sentences)
- evidence_type TEXT NOT NULL (School webpage / Provider webpage / Policy document / Prospectus / Other public document)
- interpretation_note TEXT NOT NULL (context, source attribution, school-unit applicability and project interpretation)

Approach_codes:
- code_id TEXT PRIMARY KEY
- school_id TEXT NOT NULL
- category TEXT NOT NULL (controlled category above)
- subcategory TEXT NULL
- coding_level TEXT NOT NULL CHECK IN (Explicit, Supported, Unclear)
- confidence TEXT NOT NULL CHECK IN (High, Medium, Low)
- evidence_id TEXT NOT NULL REFERENCES Approach_evidence(evidence_id)
- coder_note TEXT NOT NULL (reasoning, caveats, codebook version, coding date and reviewer identity/type)
- review_status TEXT NOT NULL CHECK IN (Reviewed, Requires review)

Enforce matching school_id between code and evidence with a composite unique key/foreign key or validation; a code must not borrow another unit's evidence. Enforce level/confidence pairs. Confirm official school key uniqueness before selecting foreign-key enforcement strategy; do not change the official school table to satisfy migration.

No school-name field is added: join school_id to schools.school_unit_code for display and record official-source name discrepancies in notes/log. Retain IDs as text. No invented evidence rows for failed/no-evidence collections. No clear public evidence found is a scoped collection-log outcome, NOT an approach category. Unvisited, inaccessible and no clear evidence remain distinct.

## Structured collection protocol
For every unit, log official registered URL, selection rationale, actual reviewed URL, source title, actual access date, permission/terms assessment, outcome, scope, ambiguities and exclusions. Search consistent Swedish/English concepts: om skolan, om oss, pedagogik, undervisning, utbildning, profil, inriktning, skapande, konst, musik, lärande, värdegrund; about us, pedagogy, education, profile, creative, arts, learning, values. Prioritise school/provider sources and attributable dated public documents. Do not automatically follow links across school units. Record document publication date in interpretation_note where available and distinguish it from access date.

Maintain collection_log.jsonl and decision_log.md as file artifacts so the replacement consists of exactly two new application tables. Include failed requests, broken links, no clear public evidence after scoped review, exclusions, terms/access restrictions and unit identity questions. Avoid named personal data in quotations/logs. Prefer short quotations and links over additional full-page copies.

## Pilot and consistency review
Re-code Anne Frank, Lilla Akademien grundskola and Kristofferskolan from source context, not old category names. Check title and original retrieval provenance; prior export timestamp was assigned during merge and must not be blindly treated as a verified source access timestamp. Re-fetch public sources only after applicable permissions checks if provenance is inadequate. Document unresolved unit name/year-range and shared-site issues. Run a second consistency pass, log borderline decisions, revise codebook if needed, then re-code affected pilot rows. No county keyword candidate is automatically migrated into a reviewed code.

## Migration safeguards and validation
1. Resolve current SQLite disk I/O error; do not delete journal/SHM files or force a repair.
2. Inventory exact old focus table names, including dlt child tables, counts, references and metadata. Read existing code before disabling old collection entry points so they cannot silently recreate deprecated tables.
3. Create a consistent SQLite backup with backup API and validate it; preserve old exports outside the live replacement tables. Report archive path and rollback procedure.
4. Preview exact DROP list and new table definitions; confirm destructive replacement before execution. Never use a wildcard DROP routine and never drop shared dlt metadata or official data.
5. Transactionally create the two requested tables, load reviewed pilot evidence via local dlt with Prefect orchestration while preserving constraints, and remove only approved old focus tables. Verify actual loader behavior before production migration.
6. Validate integrity, keys, joins, allowed category/level/confidence values, school agreement, duplicate labels, evidence completeness and unchanged official counts. Save validation results. A completed flow alone does not prove correct data.
7. Extend evidence review in auditable batches across the remaining units. Automatic suggestions may assist discovery, not replace interpretation/review.

## Ethics and dashboard caveats
Public information only; obey applicable terms, copyright, robots and access restrictions. Do not bypass login, certificate failures or access controls. Robots allowance is not legal clearance. Do not collect named children, families or individual employees. Quote minimally and attribute faithfully. Labels describe website claims, not verified teaching, quality or causal effects. Display reporting periods and differences in statistical cohorts/definitions; statistics must not be used alone or as a best-school ranking.
