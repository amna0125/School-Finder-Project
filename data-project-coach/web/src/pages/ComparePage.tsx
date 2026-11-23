import { useState } from "react";
import { GradeLine, OrgPill } from "../components/bits";
import { Ic } from "../components/Icons";
import { ApproachGrid, Glance, SchoolKey, Facilities, SupportStaff, SurveyGrid, TrendBig } from "../components/CompareViz";
import { MAXCMP, SVWHO, col } from "../lib/constants";
import { fmt, km } from "../lib/format";
import { useApp } from "../lib/store";
import type { School } from "../lib/types";

function SubjBars({ sch, yr, county, period }: { sch: School[]; yr: "6" | "9"; county: Record<string, number>; period: string }) {
  const subs = [["ma", "Maths"], ["sv", "Swedish"], ["en", "English"]] as const;
  if (sch.every(s => !s.g.includes(+yr) || subs.every(([k]) => s.m[k + yr]?.v == null))) return <p className="note">None of these schools report year {yr} national tests.</p>;
  const W0 = 420, H0 = 190, top = 14, bot = 28, gw = W0 / 3, bw = Math.min(30, (gw - 28) / sch.length);
  const Y = (v: number) => top + (1 - v / 20) * (H0 - top - bot);
  return <>
    <svg viewBox={`0 0 ${W0} ${H0}`} style={{ width: "100%", maxWidth: 560, display: "block" }} role="img" aria-label={`National tests by subject, year ${yr}`}>
      {[5, 10, 15, 20].map(v => <g key={v}><line x1={0} x2={W0} y1={Y(v)} y2={Y(v)} stroke="var(--line)" /><text x={W0} y={Y(v) - 3} textAnchor="end" fontSize={9} fill="var(--muted)" fontFamily="var(--font)">{v}</text></g>)}
      {subs.map(([k, l], gi) => {
        const x0 = gi * gw + (gw - bw * sch.length) / 2, md = county[k + yr];
        return <g key={k}>
          {sch.map((s, i) => {
            const v = s.g.includes(+yr) ? s.m[k + yr]?.v : null, cx = x0 + i * bw + bw / 2;
            if (v == null) return <text key={s.id} x={cx} y={Y(0) - 4} textAnchor="middle" fontSize={10} fill="var(--muted)">–</text>;
            return <g key={s.id}><rect x={x0 + i * bw + 2} y={Y(v)} width={bw - 4} height={Y(0) - Y(v)} rx={3} fill={col(i)}><title>{s.name}: {fmt(v, 1)}</title></rect>
              <text x={cx} y={Y(v) - 4} textAnchor="middle" fontSize={9.5} fontWeight={700} fill="var(--ink)" fontFamily="var(--font)">{fmt(v, 1)}</text></g>;
          })}
          <line x1={x0 - 6} x2={x0 + bw * sch.length + 6} y1={Y(md)} y2={Y(md)} stroke="var(--ink)" strokeDasharray="3 3" opacity={0.55} />
          <text x={gi * gw + gw / 2} y={H0 - 8} textAnchor="middle" fontSize={12} fontWeight={600} fill="var(--ink)" fontFamily="var(--font)">{l}</text>
        </g>;
      })}
    </svg>
    <p className="note">Average grade points, A = 20 and F = 0. Dashed line is the county median. Tests {period}.</p>
  </>;
}

export function ComparePage() {
  const { D, cmp, toggleCmp, clearCmp, home } = useApp();
  const [who, setWho] = useState<keyof typeof SVWHO>("parents");
  const [yr, setYr] = useState<"6" | "9">("6");
  const sch = cmp.map(id => D.byId.get(id)).filter((s): s is School => !!s);
  const c = D.county;
  if (!sch.length) return (
    <section id="v-cmp">
      <div className="inner ch-head"><div><h1>Compare schools</h1><p>Pick up to {MAXCMP} schools to see them side by side.</p></div></div>
      <div className="inner" style={{ paddingBottom: 100 }}><div className="empty"><h3>No schools picked yet</h3><p>Click a dot on the map or chart, then tick Compare, or add it from a school's page. Teachers, results, trends and what families say then line up here next to each other.</p><a className="btn primary" href="#find">Find schools</a></div></div>
    </section>
  );
  const has = sch.map(s => s.sv?.[who]);
  const yrs = (["6", "9"] as const).filter(y => sch.some(s => s.g.includes(+y)));
  const cy = yrs.includes(yr) ? yr : yrs[0];
  return (
    <section id="v-cmp">
      <div className="inner ch-head"><div><h1>Compare schools</h1><p>{sch.length === 1 ? "Add one more school to see them side by side." : `${sch.length} schools side by side. Each school keeps its colour in every chart.`}</p></div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>{sch.length < MAXCMP && <a className="btn" href="#find"><Ic n="plus" />Add a school</a>}<button className="btn ghost" type="button" onClick={clearCmp}>Clear all</button></div></div>
      <div className="inner" style={{ paddingBottom: 110 }}>
        <div className="ccards">
          {sch.map((s, i) => { const d = km(home, s); return (
            <div className="ccard" key={s.id} style={{ ["--c" as string]: col(i) }}>
              <a className="nm" href={"#school-" + s.id}>{s.name}</a>
              <div className="m">{s.addr || s.mun}{d != null ? `, ${fmt(d, 1)} km away` : ""}</div>
              <div className="row"><OrgPill s={s} /><span className="line"><GradeLine s={s} w={110} /><b>{s.grades}</b></span></div>
              <div className="row">{s.web ? <a href={s.web} target="_blank" rel="noopener" style={{ fontWeight: 600 }}>Website <Ic n="ext" /></a> : <span />}<button className="btn ghost sm" type="button" onClick={() => toggleCmp(s.id)}><Ic n="x" />Remove</button></div>
            </div>); })}
          {sch.length < MAXCMP && <a className="ccard add" href="#find"><Ic n="plus" /><span>Add a school</span></a>}
        </div>
        <div className="dgrid">
          <section className="sec wide"><div className="sec-h"><h2>At a glance</h2><span className="note">Where each school ranks in Stockholm county. Hover a dot for the figure.</span></div>
            <SchoolKey sch={sch} /><Glance sch={sch} /></section>
          {yrs.length > 0 && <section className="sec"><div className="sec-h"><h2>National tests by subject</h2>{yrs.length > 1 && <div className="seg inline" role="group" aria-label="Results for">
            {yrs.map(y => <button key={y} type="button" aria-pressed={cy === y} onClick={() => setYr(y)}>Year {y}</button>)}</div>}</div>
            <SchoolKey sch={sch} />
            <SubjBars sch={sch} yr={cy} county={c} period={D.periods["np" + cy]} /></section>}
          <section className="sec"><div className="sec-h"><h2>Support staff</h2></div><SupportStaff sch={sch} /></section>
          <section className="sec wide"><div className="sec-h"><h2>Over the years</h2><span className="note">Is each school getting better or worse? Hover a year to read every school's figure.</span></div>
            <div className="keyline trendkey"><SchoolKey sch={sch} /><span><i style={{ width: 16, borderTop: "2px dashed var(--ink)", opacity: 0.5 }} />County median, latest year</span></div>
            <div className="tbigs">
              <TrendBig title="Qualified teachers (%)" sch={sch} k="teachers" unit=" %" dec={0} county={c.teachers} />
              <TrendBig title="National tests, year 6" sch={sch} k="np6" unit="" dec={1} county={c.np6} />
              <TrendBig title="National tests, year 9" sch={sch} k="np9" unit="" dec={1} county={c.np9} />
              <TrendBig title="Merit rating, year 9" sch={sch} k="merit9" unit="" dec={0} county={c.merit9} />
            </div></section>
          <section className="sec"><div className="sec-h"><h2>What families say</h2><div className="seg inline" role="group" aria-label="Whose answers">
            {(Object.keys(SVWHO) as (keyof typeof SVWHO)[]).map(k => <button key={k} type="button" aria-pressed={k === who} onClick={() => setWho(k)}>{SVWHO[k]}</button>)}</div></div>
            {has.every(x => !x) ? <p className="note">No answers from {SVWHO[who].toLowerCase()} were published for these schools in spring 2026.</p> : <>
              <SurveyGrid sch={sch} who={who} />
              <p className="note">Skolverket school survey, spring 2026. Share of those who answered. Hover or tap a cell for the full split.</p></>}
          </section>
          <section className="sec"><div className="sec-h"><h2>Facilities</h2></div>
            <Facilities sch={sch} />
          </section>
          <section className="sec wide"><div className="sec-h"><h2>Teaching profile</h2></div>
            <ApproachGrid sch={sch} />
          </section>
        </div>
      </div>
    </section>
  );
}
