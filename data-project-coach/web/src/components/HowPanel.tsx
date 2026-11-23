import { fmt } from "../lib/format";
import { activePicks } from "../lib/scoring";
import { useApp } from "../lib/store";
import { prName } from "./Chips";
import { Ic } from "./Icons";

/** Light SQL highlighting for display only. */
export function SqlCode({ sql }: { sql: string }) {
  const parts = sql.split(/(--[^\n]*|'(?:[^']|'')*'|\b(?:with|as|select|from|where|and|or|not|case|when|then|else|end|group|by|order|desc|over|filter|max|median|count|list_contains|coalesce|is|null|true|false|union|all|join|left|using|on|limit)\b)/gi);
  return (
    <pre className="code">{parts.map((p, i) =>
      p.startsWith("--") ? <span key={i} className="cm">{p}</span>
        : p.startsWith("'") ? <span key={i} className="st">{p}</span>
        : /^[a-z_]+$/i.test(p) && i % 2 === 1 ? <span key={i} className="kw">{p}</span> : p)}</pre>
  );
}

export function HowPanel({ onClose }: { onClose: () => void }) {
  const { sql, sum, R, P, home, D } = useApp();
  const picks = activePicks(P, home);
  return (
    <section className="how" aria-label="How this is calculated">
      <div className="sec-h"><h3>How this is calculated</h3><button className="btn ghost sm" type="button" onClick={onClose} aria-label="Close"><Ic n="x" /></button></div>
      <div className="howgrid">
        <div>
          <ol>
            <li>Every school starts from one row in <code>school_card</code>, a dbt gold table built from Skolverket's register, statistics and survey, and from the reviewed website quotes.</li>
            <li>Filters (area, starting year, who runs it, name) keep or drop a school.</li>
            <li>Each priority gives a verdict per school: <b>yes</b>, <b>no</b>, or <b>not published</b>. {picks.length ? `You have ${picks.length}: ${picks.map(p => prName(p.k) + (p.m === 2 ? " (must)" : "")).join(", ")}.` : "You have not picked any yet."}</li>
            <li>A school that gets <b>no</b> on a must-have is left out. If a must-have is not published, the school stays but is shown faded.</li>
            <li>The dot fills by the share of priorities the school meets. Schools are never ranked against each other; "above" means above the county median ({fmt(D.county.teachers)} % qualified teachers, tests {fmt(D.county.np6, 1)} in year 6 and {fmt(D.county.np9, 1)} in year 9).</li>
            <li>Approaches are what a school says about itself on its own website, coded against the project's codebook. They are claims, not inspected practice.</li>
          </ol>
          <p className="stat" style={{ marginTop: 12 }}>This query ran in your browser with DuckDB-WASM in {fmt(sum.ms, 0)} ms and returned {fmt(R.size)} schools.</p>
          <p className="stat"><a href="#pipeline">See where each table comes from</a></p>
        </div>
        <div><SqlCode sql={sql} /></div>
      </div>
    </section>
  );
}
