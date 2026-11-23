/**
 * Scoring runs as SQL in DuckDB-WASM against the gold table school_card.
 * buildScoreSQL() turns the parent's answers into one query; the same text is shown in
 * the "How this is calculated" panel, so what you read is exactly what ran.
 */
import { APRI, PRI, SHORT } from "./constants";
import { cap, fmt, km } from "./format";
import type { Data, Filters, Home, Prefs, Result, School, Summary, Verdict } from "./types";
import { query } from "./db";

const lit = (s: string) => `'${s.replace(/'/g, "''")}'`;
const num = (n: number) => (Number.isFinite(n) ? String(n) : "null");

export interface Pick { k: string; m: 1 | 2 }
export function activePicks(P: Prefs, home: Home | null): Pick[] {
  const out: Pick[] = [];
  for (const p of PRI) { const m = P[p.k as "teach"].m; if (m > 0 && !(p.k === "near" && !home)) out.push({ k: p.k, m: m as 1 | 2 }); }
  for (const a of APRI) { const m = P[a.k as `ap${number}`].m; if (m > 0) out.push({ k: a.k, m: m as 1 | 2 }); }
  return out;
}

/** The test year used for "Strong results" at one school. */
function resYearSQL(P: Prefs, F: Filters, pref: string = P.res.yr) {
  if (pref === "6" || pref === "9") return pref;
  const late = F.start !== "" && +F.start >= 7;
  return `case
        ${late ? "when list_contains(grades, 9) then 9\n        " : ""}when list_contains(grades, 6) and np6 is not null then 6
        when list_contains(grades, 9) and np9 is not null then 9
        when list_contains(grades, 6) then 6
        when list_contains(grades, 9) then 9
      end`;
}

function verdictSQL(k: string, P: Prefs, home: Home | null): string {
  switch (k) {
    case "teach":
      return `case when teachers is null then 'unk' when teachers >= ${num(P.teach.min)} then 'yes' else 'no' end`;
    case "res":
      return `case when res_year is null then 'unk'
              when not list_contains(grades, res_year) then 'no'
              when res_value is null then 'unk'
              when res_value > res_median then 'yes' else 'no' end`;
    case "happy":
      return `case when parents_satisfied_pct is null then 'unk' when parents_satisfied_pct >= ${num(P.happy.min)} then 'yes' else 'no' end`;
    case "green":
      return P.green.lvl === "greener"
        ? `case when green_level is null then 'unk' when green_level = 'greener than most' then 'yes' else 'no' end`
        : `case when green_level is null then 'unk' when green_level <> 'less green than most' then 'yes' else 'no' end`;
    case "near":
      return home ? `case when km is null then 'unk' when km <= ${num(P.near.km)} then 'yes' else 'no' end` : `'unk'`;
    default: {
      const a = APRI.find(x => x.k === k)!;
      return `case when list_contains(approach_categories, ${lit(a.cat!)}) then 'yes'
              when review_state = 'No usable public page' then 'unk' else 'no' end`;
    }
  }
}

export function buildScoreSQL(P: Prefs, F: Filters, home: Home | null): string {
  const picks = activePicks(P, home);
  const where: string[] = [];
  const q = F.q.trim().toLowerCase();
  if (q) where.push(`(strip_accents(lower(school_name)) like ${lit("%" + q.normalize("NFD").replace(/[̀-ͯ]/g, "") + "%")}
         or strip_accents(lower(address)) like ${lit("%" + q.normalize("NFD").replace(/[̀-ͯ]/g, "") + "%")})`);
  if (F.mun) where.push(`municipality_name = ${lit(F.mun)}`);
  if (F.start !== "") where.push(`list_contains(grades, ${num(+F.start)})`);
  if (F.stay9) where.push(`list_contains(grades, 9)`);
  if (F.org) where.push(`organizer_type = ${lit(F.org)}`);
  if (F.fritids) where.push(`fritidshem = 'yes'`);
  const dist = home
    ? `12742 * asin(sqrt(sin(radians(latitude - ${num(home.lat)}) / 2) ^ 2
           + cos(radians(${num(home.lat)})) * cos(radians(latitude)) * sin(radians(longitude - ${num(home.lon)}) / 2) ^ 2))`
    : "null::double";
  const ev = picks.map(p => `    ${verdictSQL(p.k, P, home)} as v_${p.k}`);
  const must = picks.filter(p => p.m === 2), nice = picks.filter(p => p.m === 1);
  const cnt = (ps: Pick[], v: string) => (ps.length ? ps.map(p => `(v_${p.k} = '${v}')::int`).join(" + ") : "0");
  return `-- Parents' answers -> one query over the dbt gold table school_card
with med as (            -- county medians from the gold model county_medians
  select max(county_median) filter (where metric_key = 'teachers') as m_teachers,
         max(county_median) filter (where metric_key = 'np6')      as m_np6,
         max(county_median) filter (where metric_key = 'np9')      as m_np9,
         (select median(parents_satisfied_pct) from school_card)   as m_happy
  from county_medians
),
base as (                -- filters: area, starting year, who runs it, name search
  select c.*, med.*,
    ${resYearSQL(P, F)} as res_year,
    ${dist} as km
  from school_card c, med
  ${where.length ? "where " + where.join("\n    and ") : "-- no filters"}
),
scored as (             -- one verdict per priority: 'yes', 'no' or 'unk' (not published)
  select *,
    case res_year when 6 then np6 when 9 then np9 end as res_value,
    case res_year when 6 then m_np6 when 9 then m_np9 end as res_median
  from base
),
verdicts as (
  select school_id, km,
${ev.length ? ev.join(",\n") + "," : ""}
    -- tie-break when two schools fit equally well: distance from the county median
    coalesce(list_avg(list_filter([ (teachers - m_teachers) / 15,
        (case ${resYearSQL(P, F, "auto").replace(/\n/g, "\n        ")} when 6 then np6 - m_np6 when 9 then np9 - m_np9 end) / 2,
        (parents_satisfied_pct - m_happy) / 10 ], lambda x: x is not null)), -1) as quality
  from scored
)
select *,
  ${must.length ? `(${cnt(must, "no")}) = 0` : "true"} as fits,          -- a school that misses a must-have is out
  ${must.length ? `(${cnt(must, "unk")}) > 0` : "false"} as unknown_must, -- must-have not published: kept, shown faded
  ${cnt(picks, "yes")} as met,                         -- how many priorities it meets
  ${nice.length} as nice_total,
  ${cnt(nice, "yes")} as nice_met
from verdicts
order by fits desc, unknown_must, met desc, nice_met desc, quality desc`;
}

export async function runScore(D: Data, P: Prefs, F: Filters, home: Home | null) {
  const sql = buildScoreSQL(P, F, home);
  const t0 = performance.now();
  const rows = await query<Record<string, unknown>>(sql);
  const ms = performance.now() - t0;
  const picks = activePicks(P, home);
  const R = new Map<string, Result>();
  const nearScope = !!(home && P.near.m === 2);
  let mustOut = 0, scope = 0, all = 0, most = 0;
  for (const r of rows) {
    const s = D.byId.get(r.school_id as string); if (!s) continue;
    const ev: Record<string, Verdict> = {};
    for (const p of picks) ev[p.k] = r["v_" + p.k] as Verdict;
    const fit = r.fits as boolean, met = r.met as number, n = picks.length;
    const d = (r.km as number | null) ?? km(home, s);
    const inScope = !nearScope || (d != null && d <= P.near.km);
    if (inScope) { scope++; if (fit && n && met === n) all++; else if (fit && n > 1 && met === n - 1) most++; }
    if (!fit && inScope) mustOut++;
    const niceT = r.nice_total as number;
    R.set(s.id, { s, ev, fit, unk: r.unknown_must as boolean, met, n, frac: niceT ? (r.nice_met as number) / niceT : n ? 1 : 0, q: r.quality as number, d, all: n > 0 && fit && met === n });
  }
  const list = [...R.values()].filter(r => r.fit);
  const sum: Summary = { mustOut, scope, all, most, nearScope, ms };
  return { R, list, sum, sql };
}

/* ---------- plain-language explanations of each verdict (shown in previews and on the school page) ---------- */
const reason = (st?: string) => (st === "few" ? "Too few pupils to publish" : "Not reported");
export { reason };
export function resYear(s: School, P: Prefs, F: Filters, pref: string = P.res.yr): "6" | "9" | null {
  if (pref === "6" || pref === "9") return pref;
  if (F.start !== "" && +F.start >= 7 && s.g.includes(9)) return "9";
  if (s.g.includes(6) && s.m.np6?.v != null) return "6";
  if (s.g.includes(9) && s.m.np9?.v != null) return "9";
  return s.g.includes(6) ? "6" : s.g.includes(9) ? "9" : null;
}
export function explain(k: string, s: School, D: Data, P: Prefs, F: Filters, home: Home | null): { r: Verdict; t: string } {
  if (k === "teach") { const m = s.m.teachers, v = m?.v; return v == null ? { r: "unk", t: reason(m?.st) } : { r: v >= P.teach.min ? "yes" : "no", t: fmt(v) + " % qualified" }; }
  if (k === "res") {
    const y = resYear(s, P, F); if (!y) return { r: "unk", t: "No year 6 or 9 tests here" };
    if (!s.g.includes(+y)) return { r: "no", t: "No year " + y + " at this school" };
    const m = s.m["np" + y], v = m?.v, c = D.county["np" + y];
    if (v == null) return { r: "unk", t: "Year " + y + " tests: " + reason(m?.st).toLowerCase() };
    return { r: v > c ? "yes" : "no", t: `Year ${y} tests ${fmt(v, 1)}, ${v > c ? "above" : "below"} county ${fmt(c, 1)}` };
  }
  if (k === "happy") { const d = s.sv?.parents?.sat; return d ? { r: d.pos >= P.happy.min ? "yes" : "no", t: d.pos + " % of parents satisfied" } : { r: "unk", t: "No parent survey published" }; }
  if (k === "green") {
    const g = s.set.green; if (!g) return { r: "unk", t: "No map data" };
    const ok = P.green.lvl === "greener" ? g === "greener than most" : g !== "less green than most";
    return { r: ok ? "yes" : "no", t: cap(g) + ` (${s.set.greenPct} % green)` };
  }
  if (k === "near") { if (!home) return { r: "unk", t: "Tell us where you live" }; const d = km(home, s); return d == null ? { r: "unk", t: "Not on the map" } : { r: d <= P.near.km ? "yes" : "no", t: fmt(d, 1) + " km away" }; }
  const a = APRI.find(x => x.k === k)!;
  const hit = s.approach.find(x => x.cat === a.cat);
  if (hit) return { r: "yes", t: SHORT[hit.cat] + (hit.sub ? ": " + hit.sub : "") };
  return s.label === "No usable public page" ? { r: "unk", t: "No usable website" } : { r: "no", t: "Not mentioned on its website" };
}
