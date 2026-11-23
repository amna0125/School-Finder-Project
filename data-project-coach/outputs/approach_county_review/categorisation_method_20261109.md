# Categorisation method: Stockholm county approach review

Nov 9, 2026 · Amna

## Overview

All 762 registered school units in Stockholm county have a final label. 505 have at least one coded teaching approach, 239 show no clear evidence, and 18 have no usable public page. No school is left flagged for review.

- **Aim:** describe each school's stated teaching approach in a form parents can compare, using a fixed seven-category codebook.
- **Unit of analysis:** the school unit (skolenhet) as registered in Skolverket's school unit register, identified by its school unit code.
- **Evidence:** the school's own public web pages, or its provider's or municipality's pages about that school. Each code is backed by a short verbatim quote with its URL and access date.
- **What a code means:** a code records what the school *says* about itself. It is not a check that the approach happens in practice.
- **Who decided:** the assistant collected pages and proposed codes. Every rule for unclear cases was agreed in a joint review with Amna before it was applied. The last five schools were checked by hand by Amna.
- **Period:** the review ran from 27 October to 9 November 2026.

## The codebook

Each code has a category, a free-text subcategory, a coding level and a quote. A school can have several codes, one per approach.

### Seven categories

| Category | What counts | Example subcategories |
| --- | --- | --- |
| Arts and creative learning | Music, dance, drama or visual art as a profile, extra teaching or woven into teaching | Music profile; Optional music pathway; Dance/Ballet |
| Alternative pedagogy | A named pedagogy the school follows | Montessori; Waldorf; Reggio Emilia-inspired |
| Project- or inquiry-based learning | Thematic, cross-subject, project or inquiry work stated as how the school teaches | Thematic work; NTA; IB PYP/MYP |
| Outdoor, nature, or place-based learning | Teaching that happens outdoors or uses nature and the local area | I Ur och Skur; Nature used in teaching |
| Language, international, or intercultural profile | Bilingual or English-medium teaching, international curriculum, exchanges | Bilingual Swedish/English; Erasmus+ |
| Support, inclusion, or wellbeing emphasis | Resource schools, special groups, named wellbeing or anti-bullying programmes | Resource school (NPF); Trivselledare; PAX |
| Other stated profile | A clear profile that fits none of the above | Christian profile; Sport profile; Spetsmatte |

### Coding level

- **E = Explicit (confidence High):** the school states the approach plainly as its own, for example a named model, programme or profile.
- **S = Supported (confidence Medium):** the page supports the approach less firmly, for example hedged wording, an emphasis without a named model, or a programme run across the whole municipality.
- **Not coded:** wording too weak even for S, such as a single phrase, a belief, "when suitable" or only future plans. When in doubt between E and S we chose S. When in doubt between S and nothing we left it out and wrote why in the note.

### Ground rules

1. Use public information only, and obey robots.txt and site terms. No access controls were bypassed.
2. Record no names of staff, pupils or parents.
3. Quote short and word for word, one sentence where possible.
4. Treat a school's claim as a claim, not as verified practice.
5. Never infer an approach from the school's name. "Balettskolan" alone is not evidence of an arts profile.
6. Use provider pages with care. A provider-wide claim is applied to a unit only when the provider says it holds for all its schools (rule A below).
7. Leave out things every school must do by law, such as following Lgr22, having elevhälsa, giving extra support to pupils who need it, or teaching music and art as subjects.

## Review labels

Every school unit carries exactly one review label in the progress ledger. Blocked and Uncertain were working labels that sent a school to joint review. By the end, no school carries either of them.

| Label | Meaning | Final count |
| --- | --- | --- |
| Reviewed claim | The school's pages state an approach. It is quoted and coded, and only these schools have rows in the codes table. | 505 |
| No clear evidence in scoped review | The pages could be read but state nothing that fits the seven categories | 239 |
| No usable public page | No page about this specific school could be found or used, and none is expected. Added in step 4. | 18 |
| Blocked – requires review | No usable page for now because of an access problem (robots.txt, terms, unit identity, page not reached). Flagged. | 0 |
| Uncertain evidence – requires review | Pages were read, but the claim is too weak or vague to code without an agreed rule. Flagged. | 0 |

**Blocked** describes a problem with access and **Uncertain** describes a problem with content. Keeping them apart showed which schools needed more collecting and which needed a coding decision. Each flagged school also carried a flag reason, such as "permission / terms", "unit identity" or "isolated / generic claim". Schools were grouped by flag reason for joint review.

## Process

The review moved from a single automated run over all 762 schools to narrower passes over the flagged schools. Each pass had its own rule, and every pass was saved as a new ledger version.

1. **Pilot and batches (27 Oct – 2 Nov):** the codebook was tested on batches of 10 schools. Each batch was coded, checked against the quotes and loaded into the database.
2. **Single county run (3 Nov):** every remaining school got a first label in 20 chunks.
3. **Follow-up on blocked sources (3 Nov):** pages were collected again for Blocked schools, for example from a provider or municipality site, or from a page found in a different place.
4. **Joint review step 2 (3–4 Nov):** rules for provider pages and chain schools (A), shared pages (B), name mismatches (C) and weak claims (D). Step 2b applied rule B on its own.
5. **Joint review step 3 (4 Nov):** the Uncertain schools, in six themed groups (3a, 3b, 3c).
6. **School setting card (4 Nov):** a separate dataset that keeps setting features outside the seven approach categories.
7. **Joint review step 4 (4 Nov):** permissions checked again (A), the new label No usable public page (B), unit identity settled from Skolverket's register (C), and caveats checked again (D).
8. **Manual check by Amna (9 Nov):** the last five schools, coded by hand in an editable table and loaded with evidence type "Manual check by Amna".

### Counts after each step

| After | Reviewed claim | No clear evidence | No usable page | Blocked | Uncertain | Quotes in DB | Codes in DB |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Single run | 410 | 180 | – | 87 | 85 | 669 | 550 |
| Follow-up | 444 | 205 | – | 27 | 86 | 713 | 594 |
| Step 2 | 469 | 207 | – | 31 | 55 | 740 | 621 |
| Step 2b | 469 | 213 | – | 32 | 48 | 740 | 621 |
| Step 3a | 480 | 230 | – | 32 | 20 | 751 | 632 |
| Step 3b | 483 | 234 | – | 32 | 13 | 754 | 635 |
| Step 3c | 493 | 236 | – | 32 | 1 | 764 | 645 |
| Step 4 | 501 | 239 | 17 | 5 | 0 | 778 | 659 |
| Manual check | 505 | 239 | 18 | 0 | 0 | 783 | 664 |

The number of flagged schools fell from 172 after the single run to 0.

## Problems faced and decisions taken

Most of the hard cases came from websites that do not line up one to one with registered school units, and from claims too vague to code. Each problem below was settled by a rule agreed with Amna, then applied to every school it covered.

### Access and sources

- **Sites that do not allow automated reading.** Some sites disallow crawlers in robots.txt, or have terms that seem to forbid it.
  - Decision: we respected robots.txt and terms without exception. A school whose site was closed stayed Blocked. The last two (Kungliga Svenska Balettskolan and Kungsholmens friskola) were checked by hand by Amna.
  - Every "terms" flag was checked again in step 4. Several were false alarms that pointed to booking terms for sports halls or payment terms for memberships, so those pages were collected.
- **No page about the specific school.** Some schools have no website of their own, or a page with no real content, or only a municipal listing.
  - Decision: a new final label, *No usable public page* (step 4), instead of leaving the school Blocked forever. 18 schools carry it.
- **Status disagreements.** Runmarö school is active in Skolverket's register, but Värmdö municipality's page says it is dormant for 2026/27.
  - Decision: keep the register as the list of units, label it No usable public page, and record the conflict in the note.

### Matching websites to registered units

- **Chain schools and provider pages (rule A).** Providers such as AcadeMedia or Montessori groups describe their pedagogy once for all schools.
  - Decision: a provider claim is applied to a unit only when the provider says it holds for all its schools. It is coded at S with evidence type "Provider webpage".
- **Shared pages (rule B).** A page shared by several units sometimes described another unit's approach.
  - Decision: another unit's approach is never applied to the registered school. Six schools became No clear evidence and four went to step 3 on their own weaker claims. Lilla Kulturama was not given Kulturama Hammarby Sjöstad's arts profile, even though the two share an address and an organiser.
- **Name mismatches (rules C and step 4C).** Our school table first stored only the formal name in the register. Some schools trade under a different name, for example "Montessoriskolan i Norrtälje".
  - Decision: the display name and address from Skolverket's register were fetched for all 762 units. A website is accepted when its name matches the register. This settled the three Futuraskolan units, the Martinskolan resource school and Älta resursskola.
  - Montessoriskolan Vigelsjö was confirmed by hand as Lunden F–4 ("Lunden (tidigare Vigelsjö) åk F-4" on the Gustafslund page). It was coded separately from Gustafslund, years 5–9, because both are registered units.

### Deciding what counts as an approach

- **Generic or isolated claims (rule D, step 3).** Many schools mention a method only once, or only as something they do sometimes.
  - Decision: these were split into themed groups. Each group got its own rule. A single phrase, a hedge, or a plan for the future is not coded. A stated, regular practice is coded at S.
- **Things every school must do.** Small-group support, elevhälsa, Lgr22, music and art lessons, ICT tools.
  - Decision: not coded, because the Education Act (skollagen) or the curriculum requires them. Small groups are coded only when they are the school's stated way of working for everyone, for example a stated class-size limit, a permanent small group or two teachers per class.
- **Arts partnerships.** Is a partnership with the kulturskola an arts profile?
  - Decision: only when the school says the partnership is part of its own teaching. Bergshamra was coded No clear evidence and Carlssons skola Arts S.
- **Concrete organisation without a named model.** Katarina Norra and Kista International describe how they organise support but name no programme.
  - Decision (Amna): code Support, inclusion, or wellbeing emphasis at S.
- **Nearby nature and green schoolyards.** Many schools mention a forest or a park nearby.
  - Decision: nature is coded as Outdoor learning only when the school says it is used in teaching (10 schools coded S, 2 not coded). Proximity, schoolyards, food and facilities moved to a separate **School setting** card, so they don't inflate the approach categories.
- **Recorded caveats.** 15 coded schools carried a note with a reservation.
  - Decision: all 15 pages were fetched again and every quote was found on the live page, so the flags were cleared.

### Working method

- **Questions before decisions.** Amna asked to understand each group before agreeing a rule, so each step began with an explanation and a list of examples, and ended with her decision.
- **Traceable changes.** Each step wrote a new ledger file and appended to the database without overwriting earlier rows. The database was copied to Amna's PC with a hash check after every step.

## Data storage and reproducibility

Codes and quotes are stored in a DuckDB database. Labels are stored in a CSV ledger, so every result can be traced back to a page and a decision.

| Store | Contents | Size now |
| --- | --- | --- |
| `Approach_evidence` (DuckDB) | One row per quote: school ID, URL, page title, access date, quote, evidence type, interpretation note | 783 rows |
| `Approach_codes` (DuckDB) | One row per code: category, subcategory, level, confidence, link to its quote, coder note | 664 rows, Reviewed claim schools only |
| `schools` (DuckDB) | Skolverket register extract: name, municipality, status, grades, website | 762 units |
| `School_setting` (DuckDB) | Setting features kept apart from the approach (fritidshem, green space, water, food, facilities) | Separate card |
| Progress ledger (CSV) | Label, flag, flag reason and note for every unit; one file per step | county_progress_20261103_after_manual.csv |

- Each load is validated before it is written. The checks require unique IDs, an allowed category and level, a quote for every code, and no duplicate code for a school.
- After each step a check confirms that every Reviewed claim school has codes and that no other school does.
- Evidence type records where a quote came from: "School webpage", "Provider webpage", or "Manual check by Amna; school webpage".
- The working log is CURRENT_WORKFLOW.md, which has one dated entry per step.

## Limitations

- **Self-description only.** Codes show what schools say about themselves on the web, which can be out of date or marketing.
- **Uneven websites.** A school with a short website is more likely to get No clear evidence. That label is not proof that the school has no approach.
- **Judgement in borderline cases.** E versus S, and S versus not coded, are judgements. They were made consistent through agreed rules, but another coder could place some schools differently.
- **A snapshot in time.** Pages were read between 27 October and 9 November 2026. Each quote stores its access date.
- **Manual rows.** Two hand-checked schools (Balettskolan and Kungsholmens friskola) could not be checked again automatically, because their robots.txt does not allow it.
