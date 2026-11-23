# Stockholm County grundskolor — source and feasibility audit

Audit date: 2026-10-19. Public sources only. Scope: active grundskole school units located in Stockholms län, municipal and independent. Two-week project; analysis before BI versus React/backend decision. Required ingestion stack: local dlt with local Prefect orchestration. DuckDB remains a recommendation.

## Executive decision
Proceed with a register-first extract and school-level statistics from Skolverket. These two official services are sufficient to start analysis without collecting 26 separate municipal datasets or scraping every school website. Full metric coverage has NOT been established. No production pipeline has been built in this audit.

## Verified directory snapshot
The register request in `register_stockholm_active_gr.json` returned **762 rows, 762 unique schoolUnitCode values, all status AKTIV**. Source extractDate: `2026-10-19T23:52:50.28+02:00`. This counts administrative school units, not necessarily unique campuses or school brands.

Filters: school_type=GR; status=AKTIV; municipality_code=0114,0115,0117,0120,0123,0125,0126,0127,0128,0136,0138,0139,0140,0160,0162,0163,0180,0181,0182,0183,0184,0186,0187,0188,0191,0192.

The geography support endpoint independently lists 26 MUNICIPALITY codes beginning 01. Their code set matches the requested scope. A separate reconciliation against SCB geography and per-municipality extracts is still recommended. Detailed records have NOT been retrieved for all 762 units, so geographical membership and ownership mix have not yet been independently validated row by row.

Directory export: `stockholm_active_grundskolor_directory.csv` (code, name, status only; municipality and grades require detail enrichment).

Municipalities: Botkyrka, Danderyd, Ekerö, Haninge, Huddinge, Järfälla, Lidingö, Nacka, Norrtälje, Nykvarn, Nynäshamn, Salem, Sigtuna, Sollentuna, Solna, Stockholm, Sundbyberg, Södertälje, Tyresö, Täby, Upplands Väsby, Upplands-Bro, Vallentuna, Vaxholm, Värmdö, Österåker.

## Source inventory

### S1 — Skolverket school-unit register (directory backbone)
Official explanation: https://www.skolverket.se/om-skolverket/oppna-data/api-for-skolenhetsregistret
Swagger: https://api.skolverket.se/skolenhetsregistret/swagger-ui/index.html
Schema: https://api.skolverket.se/skolenhetsregistret/skolenhetsregistret_v2_openapi.yaml
List: https://api.skolverket.se/skolenhetsregistret/v2/school-units
Details: https://api.skolverket.se/skolenhetsregistret/v2/school-units/{schoolUnitCode}

Verified: credential-free GET, HTTP 200 JSON; active API v2; daily updates; CC0 linked by official page. Available filters include school_type, status and municipality_code. GR is grundskola; GRAN is anpassad grundskola; active status is AKTIV. Closed, dormant and planned units also exist and must not be included accidentally. Null fields may be omitted entirely.

Primary key: eight-digit schoolUnitCode stored as string. Details expose municipalityCode, schoolTypes, GR grades, visiting address, coordinates, website, organizer organizationNumber/type and extract/modified metadata. A sampled detail record confirms these fields, not universal completeness. Do not retain headteacher names, email or telephone for the MVP: they are unnecessary for comparison.

One unit may offer GR, GRAN and other forms simultaneously. Include it once in the GR directory; use GR grade properties and GR statistics only. GRAN-only units are outside this first slice.

### S2 — Skolverket Planned Education (school-level statistics)
Official explanation: https://www.skolverket.se/om-skolverket/oppna-data/api-for-skolor-utbildningar-och-statistik-planned-education
Swagger: https://api.skolverket.se/planned-educations/swagger-ui/index.html
Live schema: https://api.skolverket.se/planned-educations/v3/api-docs/--v4-active
GR statistics: https://api.skolverket.se/planned-educations/v4/school-units/{schoolUnitCode}/statistics/gr
Geography support: https://api.skolverket.se/planned-educations/v4/support/municipality-schoolunit

Verified: HTTP 200 and application/vnd.skolverket.plannededucations.api.v4.hal+json for two GR statistics samples. No credentials were supplied. Both join via the same school-unit code. Values carry value, valueType and timePeriod. History length differs by metric. Samples include 2025/26 staffing and year-9 results, but some year-6 measures only through 2024/25. This does NOT establish the latest period county-wide.

Version discrepancy: official explanation describes v3, while live Swagger lists v3 AND v4 active and defaults to v4. A v4 sample returned a self-link pointing to v3. Pin and test v4 routes rather than blindly following that self-link. Explicit v4 Accept header should be tested in the actual HTTP client; fetch_url tested default negotiation only. Official webpage warns changes may occur without notice. Save schemas and raw payloads; validate fields.

Official page links CC0 terms. Schools/education information is updated daily; statistics are described as appearing the day after publication-plan dates. Do not imply statistics themselves are daily measurements.

### S3 — Official variable dictionary
https://www.skolverket.se/download/18.10ca3e4c19b2c04f0f06255/1766060452967/Variabellista_aktuell_201214_extern.xlsx
Saved as statistics_variables.xlsx. Inspected Grundskola definitions and symbol explanations using standard-library XML/ZIP parsing. It uses some older terminology; treat live schema/payloads as the field availability authority and recheck definitions when discrepancies arise.

### S4 — Official statistics database (fallback/context)
https://www.skolverket.se/statistik-och-utvarderingar/statistik-om-forskola-och-skola/sok-statistik-om-forskola-skola-och-vuxenutbildning
https://statistikdatabasen.skolverket.se/PxWeb/pxweb/sv/Skolverkets_statistikdatabas/
Landing page fetched successfully. Individual tables, API access, school-level coverage and reuse conditions were not tested. Do not make this a pipeline dependency yet.

### S5 — Disclosure limitation
https://www.skolverket.se/om-skolverket/nyheter-och-pressmeddelanden/nyheter/nyheter/2025-12-10-forandringar-i-statistik-om-behorig-personal-per-amne-och-skola
Official notice says less information in parts of subject-level qualified-teacher statistics has been shown since spring 2025 because of confidentiality and applicable rules. Subject-level teacher comparisons are not an MVP commitment.

### Municipal and school websites
Deferred unless the extract exposes an important gap. Potential role: school profiles, admissions links and correction checks. No county-wide common municipal schema, website collection method, or reuse permission was verified. Do not infer reliable school identity from name similarity; manual matches require evidence and an explicit mapping table.

## Recommended minimum metrics

| Parent-facing item | Field/source | Interpretation and restriction |
|---|---|---|
| School name, municipality, organizer type, GR grades, website | Register details | Current directory metadata, not historical school characteristics |
| Approximate school size | totalNumberOfPupils | Preserve strings such as cirka 410; even valueType EXISTS does not guarantee exactness |
| Pupils per teacher FTE | studentsPerTeacherQuota | Not class size; compare same period |
| Certified and qualified teachers (%) | certifiedTeachersQuota | Qualification in at least one teaching subject, with exclusions in official definition; not subject-by-subject coverage |
| Year-9 vocational-program eligibility (%) | ratioOfPupils9thGradeEligibleForNationalProgramYR | Specific eligibility definition, not eligibility for every upper-secondary programme; only relevant to units serving year 9 |
| Average year-9 merit value | averageGradesMeritRating9thGrade | Official 16-best plus eligible language-choice calculation, maximum 340; dictionary says pupils without a pass in any subject are excluded from the mean |
| Year-6 all-subject pass share (secondary candidate) | ratioOfPupilsIn6thGradeWithAllSubjectsPassed | Confirm period and enough coverage first; compare only relevant units |

Do not commit to national-test comparisons, survey satisfaction, specialist staffing, SALSA or composite rankings within the first deliverable. Surveys could be useful later but require response-rate, cohort and survey-cycle checks.

## Sample evidence
- Solfagraskolan, code 10225038, register municipality 0126, GR grades 1–6. Saved register and statistics payloads. 2025/26 pupils-per-teacher value 14,6 and certified-teacher share 82,0; approximate pupil count cirka 410. Empty year-9 arrays should not be labelled performance failure. Historical applicability still needs care if grade offerings changed.
- Mälarhöjdens skola, code 46165232: saved statistics payload. Year-9 merit 272,3 in 2025/26. Vocational eligibility ~100 with valueType ROUNDED_OFF_DUE_TO_FEW_PUPILS_NOT_ELIGIBLE. Must NOT be coerced to exact 100. Its detailed register record was not fetched in this audit.
- Sampled suppression: '..' with OMITTED_DUE_TO_BASED_ON_FEW_PUPILS. No attempt should be made to reconstruct suppressed counts.

Two samples establish access and parsing feasibility, not representativeness or county-wide coverage.

## Proposed analysis data contract (not implemented)
1. school_snapshot: school_unit_code + snapshot_date, name, municipality_code, organizer_type, GR grades, website, selected visiting-address coordinates, source metadata.
2. metric_observation: school_unit_code + metric_code + time_period + school_form (and population dimensions if introduced), raw_value, nullable numeric_value, source_value_type, interpretation_status, is_approximate, source_url, retrieved_at.
3. ingestion_run / request outcome: requested URL, response status, retries, timestamps, row counts, validation results; preserve raw response files.

Parse decimal commas only for exact numeric strings. Preserve ~100, '..' and cirka counts as raw values with explicit flags. Preserve original valueType independently of derived flags. An empty array, absent property, null value, suppressed observation, HTTP failure and genuinely inapplicable metric are different states. Do not manufacture a missingness reason without evidence.

Left-join metrics to the complete directory. Never drop a school because statistics are missing. Expose year labels per metric rather than one misleading global 'latest year'. Compare only common periods within each chart and compatible grade populations. Current grades alone are not proof of historical applicability. School outcomes describe cohorts and context, not causal teaching quality. Do not average percentages into county rates without valid denominators; do not weight by approximate whole-school enrolment for a year-9 cohort.

## First implementation milestone
1. Inspect/create project manifests and applicable AGENTS.md before coding. Workspace at audit start contained inbox/ and outputs/ only.
2. Implement dlt register ingestion and full detail enrichment for 762 codes, preserving raw snapshots and excluding unnecessary personal contact fields.
3. Reconcile the 26 municipal results against the combined request. Validate unique eight-digit codes, AKTIV status, GR membership and municipality scope; report municipal counts, grades and ownership categories.
4. Test statistics on a deliberately varied pilot (municipal/independent, early-years/year-9, large/small units), then retrieve GR statistics for every directory code using conservative bounded concurrency, retries/backoff and caching. Rate limits were not established in this audit; handle 429/5xx and avoid aggressive requests.
5. Orchestrate with a local Prefect flow: directory -> details -> statistics -> validation -> coverage report. dlt loads to proposed local DuckDB. Pin package versions only after checking compatible current releases. A full snapshot is simpler than incremental loading at this scale; later consider meta_modified_after for register updates.
6. Produce coverage by metric, period, municipality, owner type and grade group. Separate exact, approximate, suppressed, absent/inapplicable and fetch failures. Identify unmatched codes explicitly.
7. Choose final comparable metrics and UI only after inspecting that report. Trend charts require identifier/organization continuity checks.

Acceptance: no silently lost directory units; all fetch failures reported; one reproducible local run; idempotent rerun without duplicate observations; numeric/approximation handling tested; source and period traceability; grade-appropriate coverage denominators. Full pipeline and these checks remain pending.

## Audit validation and limitations
Successful public GETs: register page and v2 schema/config, filtered register lists, one register detail, v4 live statistics schema/config, geography lookup, two school statistics payloads and variable workbook. Locally computed row/unique/status checks and municipality-code inventory succeeded. An initial guessed /skolenhetsregistret/v3/api-docs endpoint returned 404; the actual schema was discovered through Swagger configuration instead. No production code, installed dependencies, dashboard, full detail crawl or full statistical missingness analysis was created. No tests or builds were run; local inspection scripts are not production pipeline validation.
