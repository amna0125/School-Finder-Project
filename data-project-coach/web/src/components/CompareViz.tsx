/** Charts for the Compare page: at-a-glance ranks, trends, survey grid and approach grid. */
import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { CATS, SVT, SVWHO, col } from "../lib/constants";
import { fmt } from "../lib/format";
import { useApp } from "../lib/store";
import type { Fact, School } from "../lib/types";
import { HBar } from "./bits";
import { Ic } from "./Icons";

/** Dot in the school's colour. */
export const Badge = ({ i, sm = false }: { i: number; sm?: boolean }) =>
  <span className={"sbadge" + (sm ? " sm" : "")} style={{ background: col(i) }} aria-hidden="true" />;

/** Legend: number, colour and name for every school. */
export function SchoolKey({ sch }: { sch: School[] }) {
  return <div className="skey">{sch.map((s, i) => <span key={s.id}><Badge i={i} sm />{s.name}</span>)}</div>;
}

const short = (n: string, max = 20) => (n.length > max ? n.slice(0, max - 1).trimEnd() + "…" : n);

/* ------------------------------------------------------------------ */
/* At a glance: where each school ranks in the county on each measure */
/* ------------------------------------------------------------------ */

interface GDef { grp?: string; l: string; get: (s: School) => number | null | undefined; unit?: string; dec?: number; lower?: boolean; hint?: string }
const GLANCE: GDef[] = [
  { grp: "Teachers", l: "Qualified teachers", get: s => s.m.teachers?.v, unit: " %" },
  { l: "Pupils per teacher", get: s => s.m.ptr?.v, dec: 1, lower: true, hint: "fewer pupils per teacher ranks higher" },
  { grp: "Results", l: "National tests, year 6", get: s => (s.g.includes(6) ? s.m.np6?.v : null), dec: 1 },
  { l: "Passed all subjects, year 6", get: s => (s.g.includes(6) ? s.m.pass6?.v : null), unit: " %" },
  { l: "National tests, year 9", get: s => (s.g.includes(9) ? s.m.np9?.v : null), dec: 1 },
  { l: "Merit rating, year 9", get: s => (s.g.includes(9) ? s.m.merit9?.v : null) },
  { l: "Passed all subjects, year 9", get: s => (s.g.includes(9) ? s.m.pass9?.v : null), unit: " %" },
  { l: "Can start upper secondary", get: s => (s.g.includes(9) ? s.m.elig?.v : null), unit: " %" },
  { grp: "What families say", l: "Parents happy overall", get: s => s.sv?.parents?.sat?.pos, unit: " %" },
  { l: "Pupils feel safe, year 5", get: s => s.sv?.ak5?.safe?.pos, unit: " %" },
  { l: "Pupils feel safe, year 8", get: s => s.sv?.ak8?.safe?.pos, unit: " %" },
  { grp: "Setting", l: "Green within 300 m", get: s => s.set.greenPct, unit: " %" },
];

/** Share of county schools (that report the measure) this value beats. Ties count half. */
function rankOf(all: number[], v: number, lower = false) {
  let below = 0, eq = 0;
  for (const x of all) { if (x === v) eq++; else if (lower ? x > v : x < v) below++; }
  return ((below + eq / 2) / all.length) * 100;
}

export function Glance({ sch }: { sch: School[] }) {
  const { D } = useApp();
  const rows = useMemo(() => GLANCE.map(d => {
    const all = D.schools.map(d.get).filter((x): x is number => x != null && isFinite(x));
    const sorted = [...all].sort((a, b) => a - b), med = sorted.length ? sorted[sorted.length >> 1] : null;
    const pts = sch.map((s, i) => { const v = d.get(s); return v == null ? { i, s, v: null, r: null } : { i, s, v, r: rankOf(all, v, d.lower) }; });
    return { d, n: all.length, pts, med };
  }).filter(r => r.pts.some(p => p.v != null)), [D, sch]);
  // Track width in pixels, so markers that would overlap can be set side by side.
  const ref = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(900);
  useEffect(() => {
    const el = ref.current?.querySelector(".g-trk"); if (!el) return;
    const ro = new ResizeObserver(() => setW(el.clientWidth || 900)); ro.observe(el); return () => ro.disconnect();
  }, [rows.length]);
  const place = (pts: typeof rows[number]["pts"]) => {
    const on = pts.filter(p => p.r != null).map(p => ({ i: p.i, x: (p.r! / 100) * w })).sort((a, b) => a.x - b.x);
    const gap = w < 300 ? 14 : 18;
    for (let j = 1; j < on.length; j++) on[j].x = Math.max(on[j].x, on[j - 1].x + gap);
    const over = on.length ? on[on.length - 1].x - w : 0;
    if (over > 0) { on[on.length - 1].x -= over; for (let j = on.length - 2; j >= 0; j--) on[j].x = Math.min(on[j].x, on[j + 1].x - gap); }
    return Object.fromEntries(on.map(o => [o.i, o.x]));
  };

  return (
    <div className="glance" ref={ref}>
      <div className="g-axis" aria-hidden="true"><span /><div className="g-scale"><span style={{ left: 0 }}>Lowest in county</span><span style={{ left: "50%" }}>County median</span><span style={{ left: "100%" }}>Highest</span></div><span /></div>
      {rows.map(({ d, n, pts, med }) => { const px = place(pts); return (
        <div key={d.l}>
          {d.grp && <div className="g-grp">{d.grp}</div>}
          <div className="g-row">
            <div className="g-l">{d.l}{d.hint && <small>{d.hint}</small>}</div>
            <div className="g-trk" role="img" aria-label={d.l + ": " + pts.map(p => `${p.s.name} ${p.v == null ? "not reported" : `higher than ${Math.round(p.r!)} % of schools`}`).join("; ")}>
              <i className="q" style={{ left: "25%" }} /><i className="m" style={{ left: "50%" }} /><i className="q" style={{ left: "75%" }} />
              {pts.filter(p => p.r != null).map(p => (
                <span key={p.s.id} className="g-dot" tabIndex={0} style={{ left: px[p.i] + "px", background: col(p.i) }}>
                  <span className="vtip"><b>{fmt(p.v, d.dec ?? 0)}{d.unit ?? ""}</b> {p.s.name}<br /><span>Ranks above {Math.round(p.r!)} % of the {n} schools that report this. County median {fmt(med, d.dec ?? 0)}{d.unit ?? ""}.</span></span>
                </span>
              ))}
            </div>
            <div className="g-na">{pts.filter(p => p.v == null).map(p => <span key={p.s.id} title={p.s.name + ": not reported"}><Badge i={p.i} sm /></span>)}</div>
          </div>
        </div>
      ); })}
      <p className="note">Each marker is one school, placed by how it ranks among all Stockholm county schools that report the measure. Right is better. Markers with the same rank sit side by side. Small dots at the end of a row are schools that don't report that measure. Hover or tap a marker for the figure.</p>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Trends                                                              */
/* ------------------------------------------------------------------ */

function nice(lo: number, hi: number, n = 4) {
  const raw = (hi - lo) / n, mag = 10 ** Math.floor(Math.log10(raw)), st = [1, 2, 2.5, 5, 10].map(x => x * mag).find(x => x >= raw) ?? raw;
  const a = Math.floor(lo / st) * st, b = Math.ceil(hi / st) * st, t: number[] = [];
  for (let v = a; v <= b + st / 2; v += st) t.push(+v.toFixed(6));
  return { a, b, t };
}

export function TrendBig({ title, sch, k, unit, dec, county }: { title: string; sch: School[]; k: string; unit: string; dec: number; county?: number }) {
  const [hi, setHi] = useState<number | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const ser = sch.map(s => s.h[k] || null);
  const pers = [...new Set(ser.flatMap(x => (x ? Object.keys(x) : [])))].sort();
  if (ser.every(x => !x) || pers.length < 2) return null;
  const vals = [...ser.flatMap(x => (x ? Object.values(x) : [])), ...(county != null ? [county] : [])];
  const { a, b, t } = nice(Math.min(...vals), Math.max(...vals));
  const W = 560, H = 230, L = 40, R = 14, T = 12, B = 26;
  const X = (i: number) => L + (i / (pers.length - 1)) * (W - L - R), Y = (v: number) => T + (1 - (v - a) / (b - a || 1)) * (H - T - B);
  const move = (e: React.PointerEvent) => {
    const r = svgRef.current!.getBoundingClientRect(), x = ((e.clientX - r.left) / r.width) * W;
    let best = 0; pers.forEach((_, i) => { if (Math.abs(X(i) - x) < Math.abs(X(best) - x)) best = i; }); setHi(best);
  };
  const lab = (p: string) => `${p.slice(2, 4)}/${p.slice(5)}`;
  return (
    <div className="tbig">
      <div className="tt">{title}</div>
      <div className="tbox">
        <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={title + " over time, one line per school"} onPointerMove={move} onPointerLeave={() => setHi(null)}>
          {t.map(v => <g key={v}><line x1={L} x2={W - R} y1={Y(v)} y2={Y(v)} stroke="var(--line)" /><text x={L - 6} y={Y(v) + 3.5} textAnchor="end" fontSize={11} fill="var(--muted)" fontFamily="var(--font)">{fmt(v, v % 1 ? 1 : 0)}</text></g>)}
          {pers.map((p, i) => <text key={p} x={X(i)} y={H - 6} textAnchor="middle" fontSize={11} fill="var(--muted)" fontFamily="var(--font)">{lab(p)}</text>)}
          {county != null && <g><line x1={L} x2={W - R} y1={Y(county)} y2={Y(county)} stroke="var(--ink)" strokeDasharray="4 4" opacity={0.5} /></g>}
          {hi != null && <line x1={X(hi)} x2={X(hi)} y1={T} y2={H - B} stroke="var(--ink)" opacity={0.25} />}
          {ser.map((x, i) => {
            if (!x) return null;
            const pts = pers.map((p, j) => (x[p] != null ? [X(j), Y(x[p])] : null)).filter(Boolean) as number[][];
            return <g key={i}>
              <polyline points={pts.map(q => q.join(",")).join(" ")} fill="none" stroke={col(i)} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
              {pers.map((p, j) => x[p] != null && <circle key={p} cx={X(j)} cy={Y(x[p])} r={hi === j ? 5 : 3.5} fill={col(i)} stroke="var(--surface)" strokeWidth={2} />)}
            </g>;
          })}
        </svg>
        {hi != null && (
          <div className={"ttip " + (X(hi) > W / 2 ? "lft" : "rgt")} style={{ left: `${(X(hi) / W) * 100}%` }}>
            <div className="h">{pers[hi]}</div>
            {sch.map((s, i) => { const v = ser[i]?.[pers[hi]]; return <div key={s.id} className="r"><i style={{ background: col(i) }} /><b>{v == null ? "–" : fmt(v, dec) + unit}</b><span>{short(s.name, 22)}</span></div>; })}
            {county != null && <div className="r c"><i /><b>{fmt(county, dec)}{unit}</b><span>County median, latest year</span></div>}
          </div>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Survey grid                                                         */
/* ------------------------------------------------------------------ */

const bin = (p: number) => (p >= 90 ? 5 : p >= 80 ? 4 : p >= 70 ? 3 : p >= 60 ? 2 : 1);

export function SurveyGrid({ sch, who }: { sch: School[]; who: keyof typeof SVWHO }) {
  const { D } = useApp();
  const med = useMemo(() => Object.fromEntries(SVT.map(([k]) => {
    const v = D.schools.map(s => s.sv?.[who]?.[k]?.pos).filter((x): x is number => x != null).sort((a, b) => a - b);
    return [k, v.length ? v[v.length >> 1] : null];
  })), [D, who]);
  return (
    <div className="gridwrap">
      <table className="sgridt">
        <thead><tr><th />{sch.map(s => <th key={s.id} scope="col" title={s.name}><span className="nm">{short(s.name, 16)}</span></th>)}<th scope="col" className="cm">County median</th></tr></thead>
        <tbody>{SVT.map(([k, l]) => (
          <tr key={k}><th scope="row">{l}</th>
            {sch.map(s => { const d = s.sv?.[who]?.[k]; return d
              ? <td key={s.id} tabIndex={0} data-b={bin(d.pos)}><span className="pv">{d.pos}%</span>
                  <span className="vtip"><b>{d.pos} % agree</b> {s.name}<br /><span>{d.mid} % in between, {d.neg} % disagree{d.n ? `, ${d.n} answers` : ""}</span></span></td>
              : <td key={s.id} className="nd">–</td>; })}
            <td className="cm">{med[k] != null ? med[k] + "%" : "–"}</td>
          </tr>))}
        </tbody>
      </table>
      <div className="keyline sqkey"><span>Share who agree:</span>{["under 60", "60–69", "70–79", "80–89", "90+"].map((t, j) => <span key={t}><i data-b={j + 1} />{t} %</span>)}<span><i className="ndk">–</i>Not published</span></div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Approach grid                                                       */
/* ------------------------------------------------------------------ */

export function ApproachGrid({ sch }: { sch: School[] }) {
  const { D } = useApp();
  const cell = (s: School, cat: string): ReactNode => {
    const a = s.approach.filter(x => x.cat === cat);
    if (!a.length) return <span className="no" aria-label="No">·</span>;
    return <div className="apcell">{a.map((x, j) => (
      <details key={j}><summary><Ic n="check" />{x.sub || "Yes"}</summary>
        <blockquote lang="sv">{x.q}</blockquote>{x.url && <a href={x.url} target="_blank" rel="noopener">Source <Ic n="ext" /></a>}</details>))}</div>;
  };
  const none = sch.map(s => !s.approach.length);
  return (
    <div className="gridwrap">
      <table className="apgrid">
        <thead><tr><th />{sch.map(s => <th key={s.id} scope="col" title={s.name}><span className="nm">{short(s.name, 16)}</span></th>)}</tr></thead>
        <tbody>
          {CATS.map(([cat, l, desc]) => (
            <tr key={cat} className={sch.some(s => s.approach.some(x => x.cat === cat)) ? "" : "dim"}>
              <th scope="row" title={desc}>{l} <small>{D.approachCounts[cat] ?? 0} in county</small></th>
              {sch.map(s => { const on = s.approach.some(x => x.cat === cat); return <td key={s.id} className={on ? "on" : "e"}>{cell(s, cat)}</td>; })}
            </tr>))}
          {none.some(Boolean) && <tr className="nop"><th scope="row">No profile found</th>{sch.map((s, i) => <td key={s.id}>{none[i] ? <span className="note">{s.label === "No usable public page" ? "No usable website" : "Nothing particular described on its website"}</span> : null}</td>)}</tr>}
        </tbody>
      </table>
      <p className="note">What each school says about itself on its website. Open a tick to read the quote.</p>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Staff and facilities                                                */
/* ------------------------------------------------------------------ */

const FAC: [string, string, (f: Fact) => string | null][] = [
  ["fritidshem_registered", "Fritidshem (after-school care)", f => (f.v === "yes" ? "Yes" : f.v.startsWith("not applicable") ? "No years F–5" : "No")],
  ["facility_sports_hall", "Sports hall", () => "Yes"],
  ["facility_arts_or_science_rooms", "Arts or science rooms", () => "Yes"],
  ["food_cooked_on_site", "Food cooked on site", f => (f.v === "yes" ? "Yes" : "No")],
  ["food_sustainable_or_vegetarian_focus", "Vegetarian or sustainable food focus", () => "Yes"],
  ["premises_new_or_renovated", "New or renovated premises", () => "Yes"],
  ["schoolyard_described", "Schoolyard", f => (f.v === "green/natural" ? "Green, natural" : "Large or varied")],
  ["nature_nearby_stated", "Nature nearby", () => "Yes"],
];

export function SupportStaff({ sch }: { sch: School[] }) {
  const { D } = useApp();
  const spec = sch.map(s => s.m.spec?.v);
  return (
    <>
      <div>
        <div className="sub-h">Special educators<small>specialpedagoger, {D.periods.spec ?? ""}</small></div>
        <div className="nbars">{sch.map((s, i) => <div className="nbar" key={s.id}><span className="sbadge sm" style={{ background: col(i) }} /><HBar label={s.name} v={spec[i]} max={20} med={D.county.spec} unit="" dec={1} na={s.m.spec?.st === "few" ? "Too few to publish" : "Not reported"} color={col(i)} /></div>)}</div>
        <p className="note">Skolverket's figure for special educator posts at the school. County median {fmt(D.county.spec, 1)}.</p>
      </div>
      <div>
        <div className="sub-h">Special teachers<small>speciallärare, full-time posts</small></div>
        <div className="facts">{sch.map(s => { const m = s.m.stp; return (
          <div key={s.id}><span className="fn">{s.name}</span>
            <b className={m?.v == null ? "na" : ""}>{m?.v != null ? fmt(m.v, 1) : m?.st === "few" ? "Withheld by Skolverket (small number)" : "Not reported"}</b></div>); })}</div>
      </div>
    </>
  );
}

export function Facilities({ sch }: { sch: School[] }) {
  return (
      <div className="gridwrap">
        <table className="apgrid fac">
          <thead><tr><th />{sch.map(s => <th key={s.id} scope="col" title={s.name}><span className="nm">{short(s.name, 16)}</span></th>)}</tr></thead>
          <tbody>{FAC.map(([k, l, txt]) => {
            const f = sch.map(s => s.set[k] as Fact | undefined);
            return <tr key={k} className={f.some(Boolean) ? "" : "dim"}><th scope="row">{l}</th>
              {f.map((x, j) => { const t = x ? txt(x) : null, yes = t != null && t !== "No" && !t.startsWith("No ");
                return <td key={sch[j].id} className={yes ? "on" : "e"}>{t == null ? <span className="no">·</span>
                  : x?.q ? <div className="apcell"><details><summary>{yes && <Ic n="check" />}{t}</summary><blockquote lang="sv">{x.q}</blockquote></details></div>
                  : <span className="ft">{yes && <Ic n="check" />}{t}</span>}</td>; })}
            </tr>; })}</tbody>
        </table>
        <p className="note">Fritidshem is from the school register. The rest is what each school says on its website, so a dot means not mentioned, not necessarily missing. Open a tick to read the quote.</p>
      </div>
  );
}
