/**
 * DuckDB running in the browser (WebAssembly). The dbt gold models are Parquet files in
 * public/data/; they are registered here as views, so every figure on the site is read with SQL.
 */
import * as duckdb from "@duckdb/duckdb-wasm";
import mvpWasm from "@duckdb/duckdb-wasm/dist/duckdb-mvp.wasm?url";
import mvpWorker from "@duckdb/duckdb-wasm/dist/duckdb-browser-mvp.worker.js?url";
import ehWasm from "@duckdb/duckdb-wasm/dist/duckdb-eh.wasm?url";
import ehWorker from "@duckdb/duckdb-wasm/dist/duckdb-browser-eh.worker.js?url";
import type { Approach, Data, Metric, School, Status } from "./types";

export const GOLD_TABLES = [
  "school_card", "fct_school_metrics", "fct_metric_history", "school_approach",
  "school_survey", "school_setting", "county_medians", "dim_metrics", "dim_approach_categories",
] as const;

let conn: duckdb.AsyncDuckDBConnection | null = null;
let ready: Promise<duckdb.AsyncDuckDBConnection> | null = null;

export function connect() {
  if (ready) return ready;
  ready = (async () => {
    const bundle = await duckdb.selectBundle({
      mvp: { mainModule: mvpWasm, mainWorker: mvpWorker },
      eh: { mainModule: ehWasm, mainWorker: ehWorker },
    });
    const worker = new Worker(bundle.mainWorker!);
    const db = new duckdb.AsyncDuckDB(new duckdb.ConsoleLogger(duckdb.LogLevel.WARNING), worker);
    await db.instantiate(bundle.mainModule, bundle.pthreadWorker);
    const c = await db.connect();
    for (const t of GOLD_TABLES) {
      const url = new URL(`data/${t}.parquet`, document.baseURI).href;
      await db.registerFileURL(`${t}.parquet`, url, duckdb.DuckDBDataProtocol.HTTP, false);
      await c.query(`create or replace view ${t} as select * from read_parquet('${t}.parquet')`);
    }
    conn = c;
    return c;
  })();
  return ready;
}

/** Run SQL and return plain JS rows (BigInt turned into Number, lists into arrays). */
export async function query<T = Record<string, unknown>>(sql: string): Promise<T[]> {
  const c = conn ?? (await connect());
  const res = await c.query(sql);
  return res.toArray().map(r => plain(r.toJSON()) as T);
}
function plain(v: unknown): unknown {
  if (typeof v === "bigint") return Number(v);
  if (v && typeof v === "object") {
    if (Array.isArray(v)) return v.map(plain);
    if (typeof (v as { toArray?: unknown }).toArray === "function" && !(v instanceof Date)) {
      return Array.from((v as { toArray(): ArrayLike<unknown> }).toArray(), plain);
    }
    const o: Record<string, unknown> = {};
    for (const [k, x] of Object.entries(v)) o[k] = plain(x);
    return o;
  }
  return v;
}

const statusOf = (s: string | null): Status =>
  s === "reported" || s === "reported_previous_year" || s === "estimate" ? "ok"
    : s === "few_pupils" ? "few" : s === "rounded" ? "rounded" : "none";

/** Build one record per school for the UI from the gold tables. */
export async function loadData(): Promise<Data> {
  type Card = { school_id: string; school_name: string; municipality_name: string; address: string; latitude: number | null; longitude: number | null; organizer_type: "municipal" | "independent"; organizer_name: string | null; grades: number[]; grades_label: string; website: string | null; review_state: string | null };
  const [cards, metrics, hist, ap, sv, set, med, apn] = await Promise.all([
    query<Card>(`select school_id, school_name, municipality_name, address, latitude, longitude, organizer_type, organizer_name,
                        grades, grades_label, website, review_state from school_card order by school_name`),
    query<{ school_id: string; metric_key: string; value: number | null; period: string | null; value_status: string }>(
      `select school_id, metric_key, value, period, value_status from fct_school_metrics`),
    query<{ school_id: string; metric_key: string; period: string; value: number }>(
      `select school_id, metric_key, period, value from fct_metric_history order by period`),
    query<{ school_id: string; category: string; subcategory: string | null; coding_level: "E" | "S"; quoted_text: string; source_url: string | null; d: string | null }>(
      `select school_id, category, subcategory, coding_level, quoted_text, source_url, strftime(accessed_date, '%Y-%m-%d') as d
       from school_approach order by school_id, coding_level`),
    query<{ school_id: string; respondent_group: "parents" | "ak5" | "ak8"; theme_key: "sat"; positive_pct: number; middle_pct: number; negative_pct: number; answers: number | null }>(
      `select * from school_survey`),
    query<{ school_id: string; feature: string; value: string; green_pct: number | null; quoted_text: string | null; d: string | null }>(
      `select school_id, feature, value, green_pct, quoted_text, strftime(accessed_date, '%Y-%m-%d') as d from school_setting`),
    query<{ metric_key: string; county_median: number; latest_period: string }>(`select * from county_medians`),
    query<{ category: string; schools: number }>(`select category, schools from dim_approach_categories`),
  ]);
  const byId = new Map<string, School>();
  const schools: School[] = cards.map(c => {
    const s: School = {
      id: c.school_id, name: c.school_name, mun: c.municipality_name, addr: c.address,
      lat: c.latitude, lon: c.longitude, org: c.organizer_type, orgName: c.organizer_name,
      grades: c.grades_label, g: c.grades ?? [], web: c.website, label: c.review_state,
      approach: [], m: {}, set: {}, h: {},
    };
    byId.set(s.id, s);
    return s;
  });
  for (const r of metrics) {
    const s = byId.get(r.school_id); if (!s) continue;
    s.m[r.metric_key] = { v: r.value, p: r.period, st: r.value == null ? statusOf(r.value_status) : "ok" } as Metric;
  }
  for (const r of hist) { const s = byId.get(r.school_id); if (s) (s.h[r.metric_key] ??= {})[r.period] = r.value; }
  for (const r of ap) {
    byId.get(r.school_id)?.approach.push({ cat: r.category, sub: r.subcategory, lvl: r.coding_level, q: r.quoted_text, url: r.source_url, date: r.d } as Approach);
  }
  for (const r of sv) {
    const s = byId.get(r.school_id); if (!s) continue;
    ((s.sv ??= {})[r.respondent_group] ??= {})[r.theme_key] = { pos: r.positive_pct, mid: r.middle_pct, neg: r.negative_pct, n: r.answers };
  }
  for (const r of set) {
    const s = byId.get(r.school_id); if (!s) continue;
    if (r.feature === "green_space_300m") { s.set.green = r.value; s.set.greenPct = r.green_pct ?? undefined; }
    else s.set[r.feature] = r.quoted_text ? { v: r.value, q: r.quoted_text, date: r.d } : { v: r.value };
  }
  const county = Object.fromEntries(med.map(m => [m.metric_key, m.county_median]));
  const periods = Object.fromEntries(med.map(m => [m.metric_key, m.latest_period]));
  const sats = schools.map(s => s.sv?.parents?.sat?.pos).filter((v): v is number => v != null).sort((a, b) => a - b);
  return {
    schools, byId, county, periods,
    svMedian: sats[sats.length >> 1] ?? 0,
    approachCounts: Object.fromEntries(apn.map(a => [a.category, a.schools])),
    generated: new Date().toISOString().slice(0, 10),
  };
}
