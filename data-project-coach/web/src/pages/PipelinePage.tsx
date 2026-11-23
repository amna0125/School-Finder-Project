import { useEffect, useMemo, useState } from "react";
import { SqlCode } from "../components/HowPanel";
import { Ic } from "../components/Icons";
import { query } from "../lib/db";
import { fmt } from "../lib/format";

interface Node { id: string; name: string; layer: string; kind: string; materialized: string | null; description: string; depends_on: string[]; columns: number; rows: number | null; status: string | null; sql: string; path: string; source?: string }
interface Test { name: string; kind: string; column: string | null; on: string[]; status: string | null }
interface Lineage { generated: string; dbt_version: string; adapter: string; elapsed: number; nodes: Node[]; tests: Test[] }

const COLS = [
  { key: "in", title: "Sources and seeds" }, { key: "bronze", title: "Bronze" }, { key: "silver", title: "Silver" },
  { key: "gold", title: "Gold (Parquet)" }, { key: "web", title: "This website" },
];
const colOf = (n: Node) => (n.layer === "source" || n.layer === "seed" ? 0 : n.layer === "bronze" ? 1 : n.layer === "silver" ? 2 : n.layer === "gold" ? 3 : 4);
const WEB: Node = { id: "web", name: "DuckDB-WASM + React", layer: "web", kind: "app", materialized: null, description: "The gold Parquet files are read by DuckDB running in your browser. Filtering and scoring are SQL queries; React draws the result.", depends_on: [], columns: 0, rows: null, status: null, sql: "", path: "web/src/lib/db.ts" };

const EXAMPLES: [string, string][] = [
  ["Schools per approach", `select category, count(distinct school_id) as schools,\n       count(*) filter (where coding_level = 'E') as explicit_codes\nfrom school_approach\ngroup by category\norder by schools desc`],
  ["Teachers by municipality", `select municipality_name,\n       count(*) as schools,\n       round(median(teachers), 1) as median_qualified_teachers_pct\nfrom school_card\ngroup by 1\norder by 3 desc`],
  ["Value status of statistics", `select metric_key, value_status, count(*) as n\nfrom fct_school_metrics\ngroup by all\norder by metric_key, n desc`],
  ["Approach vs parent satisfaction", `-- Descriptive only: a school's stated approach is a claim, not a cause.\nselect a.category_short,\n       count(*) as schools_with_survey,\n       round(avg(c.parents_satisfied_pct), 1) as avg_parents_satisfied\nfrom school_approach a\njoin school_card c using (school_id)\nwhere c.parents_satisfied_pct is not null\ngroup by 1 order by 3 desc`],
];

export function PipelinePage() {
  const [L, setL] = useState<Lineage | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [selId, setSelId] = useState<string | null>("model.school_finder.school_card");
  useEffect(() => { fetch(new URL("data/lineage.json", document.baseURI)).then(r => r.json()).then(setL).catch(e => setErr(String(e))); }, []);

  const layout = useMemo(() => {
    if (!L) return null;
    const nodes = [...L.nodes, { ...WEB, depends_on: L.nodes.filter(n => n.layer === "gold").map(n => n.id) }];
    const by = new Map(nodes.map(n => [n.id, n]));
    const cols: Node[][] = COLS.map(() => []);
    for (const n of nodes) cols[colOf(n)].push(n);
    // order: sources first then seeds; downstream columns ordered by the mean row of their parents
    cols[0].sort((a, b) => (a.layer === b.layer ? a.name.localeCompare(b.name) : a.layer === "source" ? -1 : 1));
    const pos = new Map<string, { x: number; y: number }>();
    const W = 196, H = 34, GX = 50, GY = 10, TOP = 40;
    cols.forEach((c, ci) => {
      if (ci > 0) {
        const rank = (n: Node) => { const ps = n.depends_on.map(d => pos.get(d)?.y).filter((v): v is number => v != null); return ps.length ? ps.reduce((a, b) => a + b) / ps.length : 1e9; };
        c.sort((a, b) => rank(a) - rank(b));
      }
      c.forEach((n, i) => pos.set(n.id, { x: 16 + ci * (W + GX), y: TOP + i * (H + GY) }));
    });
    const height = Math.max(...cols.map(c => c.length)) * (H + GY) + TOP + 10;
    // center shorter columns
    cols.forEach(c => { const off = (height - TOP - c.length * (H + GY)) / 2; c.forEach(n => { const p = pos.get(n.id)!; p.y += Math.max(0, off - 5) * (c === cols[4] ? 1 : 0.0); }); });
    return { nodes, by, pos, W, H, width: 16 * 2 + COLS.length * W + (COLS.length - 1) * GX, height };
  }, [L]);

  const related = useMemo(() => {
    if (!layout || !selId) return null;
    const up = new Set<string>(), down = new Set<string>();
    const walkUp = (id: string) => { for (const d of layout.by.get(id)?.depends_on ?? []) if (!up.has(d)) { up.add(d); walkUp(d); } };
    const walkDown = (id: string) => { for (const n of layout.nodes) if (n.depends_on.includes(id) && !down.has(n.id)) { down.add(n.id); walkDown(n.id); } };
    walkUp(selId); walkDown(selId);
    return new Set([selId, ...up, ...down]);
  }, [layout, selId]);

  if (err) return <div className="inner pipe"><p className="err">Could not load the lineage file: {err}</p></div>;
  if (!L || !layout) return <div className="loading"><div><div className="spin" />Loading pipeline…</div></div>;
  const sel = selId ? layout.by.get(selId) : null;
  const passed = L.tests.filter(t => t.status === "pass").length;
  const models = L.nodes.filter(n => n.kind === "model").length;
  const card = L.nodes.find(n => n.name === "school_card");
  const testsOn = sel ? L.tests.filter(t => t.on.includes(sel.id)) : [];
  const { pos, W, H } = layout;

  return (
    <section className="inner pipe">
      <div className="ch-head" style={{ paddingBottom: 0 }}><div><h1>How the data gets here</h1>
        <p>From public sources to this page: a dlt load into DuckDB, dbt models in three layers with tests, Parquet files, and DuckDB running in your browser.</p></div></div>

      <div className="kpis">
        <div className="kf"><div className="l">School units</div><div className="v">{fmt(card?.rows ?? 0)}</div><div className="c">Stockholm county, years F–9</div></div>
        <div className="kf"><div className="l">dbt models</div><div className="v">{models}</div><div className="c">bronze, silver and gold, plus {L.nodes.filter(n => n.kind === "seed").length} seeds</div></div>
        <div className="kf"><div className="l">Data tests</div><div className="v">{passed}<small>/{L.tests.length}</small></div><div className="c">passed in the last build</div></div>
        <div className="kf"><div className="l">Last build</div><div className="v" style={{ fontSize: 22 }}>{L.generated.slice(0, 10)}</div><div className="c">dbt {L.dbt_version} on {L.adapter}, {fmt(L.elapsed, 1)} s</div></div>
      </div>

      <section className="sec">
        <div className="sec-h"><h2>Lineage</h2><span className="note">Click a box to see its SQL, row count and tests. Highlighted boxes feed into it or depend on it.</span></div>
        <div className="layerkey">
          <span><b>Sources</b> Skolverket register, statistics and survey (loaded by dlt), and the reviewed approach and setting tables.</span>
          <span><b>Bronze</b> raw as loaded.</span><span><b>Silver</b> cleaned, typed, value status decoded.</span><span><b>Gold</b> what the site reads, written as Parquet.</span>
        </div>
        <div className="lineage">
          <svg width={layout.width} height={layout.height} role="img" aria-label="dbt lineage from sources to the website">
            {COLS.map((c, i) => <text key={c.key} className="colh" x={16 + i * (W + 50)} y={22}>{c.title}</text>)}
            {layout.nodes.flatMap(n => n.depends_on.map(d => {
              const a = pos.get(d), b = pos.get(n.id); if (!a || !b) return null;
              const x1 = a.x + W, y1 = a.y + H / 2, x2 = b.x, y2 = b.y + H / 2, mx = (x1 + x2) / 2;
              const on = related && related.has(d) && related.has(n.id);
              return <path key={d + n.id} className={"ed" + (on ? " on" : related ? " dim" : "")} d={`M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}`} />;
            }))}
            {layout.nodes.map(n => { const p = pos.get(n.id)!; const on = n.id === selId; return (
              <g key={n.id} className={"nd" + (on ? " on" : related && !related.has(n.id) ? " dim" : "")} transform={`translate(${p.x},${p.y})`} onClick={() => setSelId(n.id)}>
                <rect width={W} height={H} rx={8} style={n.layer === "gold" ? { fill: "var(--brand-soft)" } : n.layer === "web" ? { fill: "var(--sun-soft)" } : undefined} />
                <text x={10} y={15} fontSize={12.5} fontWeight={600}>{n.name.length > 26 ? n.name.slice(0, 25) + "…" : n.name}</text>
                <text x={10} y={28} fontSize={10.5} className="rows">{n.kind === "app" ? "in the browser" : `${n.kind}${n.rows != null ? " · " + fmt(n.rows) + " rows" : ""}`}</text>
              </g>); })}
          </svg>
        </div>
        {sel && <div className="howgrid">
          <div style={{ display: "grid", gap: 8, alignContent: "start" }}>
            <h3 style={{ fontSize: 17 }}>{sel.name}</h3>
            <p className="note">{sel.description || "No description."}</p>
            <dl className="kv">
              <div><dt>Layer</dt><dd>{sel.layer}{sel.materialized ? `, materialized as ${sel.materialized}` : ""}</dd></div>
              {sel.rows != null && <div><dt>Rows</dt><dd>{fmt(sel.rows)}</dd></div>}
              {sel.path && <div><dt>File</dt><dd><code>{sel.path}</code></dd></div>}
              {sel.depends_on.length > 0 && <div><dt>Reads from</dt><dd>{sel.depends_on.map(d => layout.by.get(d)?.name).filter(Boolean).join(", ")}</dd></div>}
            </dl>
            {testsOn.length > 0 && <><div className="sub-h">Tests on this model</div><div className="tests">{testsOn.map(t => <div key={t.name}><span className={t.status === "pass" ? "ok" : "bad"}>{t.status === "pass" ? "✓" : "✗"}</span><span title={t.name}>{t.kind}{t.column ? ` · ${t.column}` : ""}</span></div>)}</div></>}
          </div>
          <div>{sel.sql ? <SqlCode sql={sel.sql.trim()} /> : <p className="note">{sel.kind === "source" ? "A source table: loaded before dbt runs." : sel.kind === "seed" ? "A seed: a small CSV kept in the dbt project." : "Runs in the browser."}</p>}</div>
        </div>}
      </section>

      <SqlConsole />

      <section className="sec">
        <div className="sec-h"><h2>All tests</h2><span className="note">{passed} of {L.tests.length} passed</span></div>
        <div className="tests">{L.tests.map(t => <div key={t.name}><span className={t.status === "pass" ? "ok" : "bad"}>{t.status === "pass" ? "✓" : "✗"}</span><span title={t.name}>{t.name.replace(/_/g, " ")}</span></div>)}</div>
      </section>
    </section>
  );
}

function SqlConsole() {
  const [sql, setSql] = useState(EXAMPLES[0][1]);
  const [rows, setRows] = useState<Record<string, unknown>[] | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [ms, setMs] = useState(0);
  const run = async (q = sql) => {
    setErr(null);
    const t0 = performance.now();
    try { const r = await query(q); setRows(r.slice(0, 500)); setMs(performance.now() - t0); } catch (e) { setErr(String((e as Error).message || e)); setRows(null); }
  };
  useEffect(() => { run(); }, []);
  const cols = rows && rows.length ? Object.keys(rows[0]) : [];
  return (
    <section className="sec console">
      <div className="sec-h"><h2><Ic n="db" /> Ask the data yourself</h2><span className="note">SQL runs in your browser against the gold tables: school_card, fct_school_metrics, fct_metric_history, school_approach, school_survey, school_setting, county_medians.</span></div>
      <div className="acts">{EXAMPLES.map(([l, q]) => <button key={l} className="btn sm" type="button" onClick={() => { setSql(q); run(q); }}>{l}</button>)}</div>
      <textarea value={sql} onChange={e => setSql(e.target.value)} spellCheck={false} aria-label="SQL query"
        onKeyDown={e => { if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); run(); } }} />
      <div className="acts"><button className="btn primary sm" type="button" onClick={() => run()}>Run query</button><span className="note">Ctrl + Enter also runs it. {rows ? `${fmt(rows.length)} rows in ${fmt(ms)} ms.` : ""}</span></div>
      {err && <p className="err">{err}</p>}
      {rows && rows.length > 0 && <div className="rtable"><table><thead><tr>{cols.map(c => <th key={c}>{c}</th>)}</tr></thead>
        <tbody>{rows.map((r, i) => <tr key={i}>{cols.map(c => <td key={c}>{fmtCell(r[c])}</td>)}</tr>)}</tbody></table></div>}
    </section>
  );
}
const fmtCell = (v: unknown) => (v == null ? "" : Array.isArray(v) ? v.join(", ") : typeof v === "number" ? (Number.isInteger(v) ? String(v) : v.toFixed(2)) : String(v));
