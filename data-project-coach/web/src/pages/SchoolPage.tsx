import { useState } from "react";
import { CmpBtn, Delta, GradeLine, HBar, OrgPill, Stack, SvKey, TrendChart } from "../components/bits";
import { prName } from "../components/Chips";
import { Ic } from "../components/Icons";
import { SHORT, SVT, SVWHO } from "../lib/constants";
import { cap, fmt, fmtDate, km } from "../lib/format";
import { activePicks, explain, reason } from "../lib/scoring";
import { useApp } from "../lib/store";
import type { Fact, School } from "../lib/types";

const fact = (s: School, k: string) => s.set[k] as Fact | undefined;
const FACTS: [string, (s: School) => { y?: boolean; t: string; q?: string | null } | null][] = [
  ["Fritidshem (after-school care)", s => { const v = fact(s, "fritidshem_registered")?.v; return v === "yes" ? { y: true, t: "Yes" } : v ? { t: v.startsWith("not applicable") ? "No years F–5 here" : "Not at this school" } : null; }],
  ["Green space within 300 m", s => (s.set.green ? { y: s.set.green === "greener than most", t: `${s.set.greenPct} %, ${s.set.green}` } : null)],
  ["Food cooked on site", s => { const f = fact(s, "food_cooked_on_site"); return f ? { y: f.v === "yes", t: f.v === "yes" ? "Yes" : "No", q: f.q } : null; }],
  ["Sustainable or vegetarian food focus", s => { const f = fact(s, "food_sustainable_or_vegetarian_focus"); return f ? { y: true, t: "Yes", q: f.q } : null; }],
  ["Sports hall", s => { const f = fact(s, "facility_sports_hall"); return f ? { y: true, t: "Yes", q: f.q } : null; }],
  ["Arts or science rooms", s => { const f = fact(s, "facility_arts_or_science_rooms"); return f ? { y: true, t: "Yes", q: f.q } : null; }],
  ["Nature close by", s => { const f = fact(s, "nature_nearby_stated"); return f ? { y: true, t: "Yes", q: f.q } : null; }],
  ["Schoolyard", s => { const f = fact(s, "schoolyard_described"); return f ? { y: true, t: cap(f.v.replace(/\//g, ", ")), q: f.q } : null; }],
  ["New or renovated building", s => { const f = fact(s, "premises_new_or_renovated"); return f ? { y: true, t: "Yes", q: f.q } : null; }],
];

export function SchoolPage({ s }: { s: School }) {
  const { D, P, F, home, setFocusId } = useApp();
  const [who, setWho] = useState<keyof typeof SVWHO>("parents");
  const d = km(home, s); const c = D.county;
  const t = s.m.teachers, ptr = s.m.ptr, n6 = s.m.np6, n9 = s.m.np9, m9 = s.m.merit9, sat = s.sv?.parents?.sat;
  const act = activePicks(P, home);
  const KF = ({ l, v, u, cv, dec, unit, why, has = true }: { l: string; v?: number | null; u: string; cv: number; dec: number; unit: string; why: string; has?: boolean }) => (
    <div className="kf"><div className="l">{l}</div>
      {v != null ? <><div className="v">{fmt(v, dec)}<small>{u}</small></div><div className="c">County median {fmt(cv, dec)}{unit} <Delta v={v} c={cv} d={dec} unit={unit} /></div></>
        : <div className="na">{has ? why : "Not offered here"}</div>}
    </div>
  );
  const resYear = (y: "6" | "9") => {
    const has = s.g.includes(+y), any = ["ma", "sv", "en"].some(k => s.m[k + y]?.v != null);
    return (
      <div><div className="sub-h">Year {y}</div>
        {!has ? <p className="note">This school has no year {y}.</p> : !any ? <p className="note">{reason(s.m["np" + y]?.st)}.</p>
          : ([["ma", "Maths"], ["sv", "Swedish"], ["en", "English"]] as const).map(([k, l]) => <HBar key={k} label={l} v={s.m[k + y]?.v} max={20} med={c[k + y]} unit="" dec={1} na={reason(s.m[k + y]?.st)} />)}
      </div>
    );
  };
  const svd = s.sv?.[who];
  const trends = [
    <TrendChart key="t" title="Qualified teachers" h={s.h.teachers} dec={0} countyV={c.teachers} unit=" %" />,
    <TrendChart key="6" title="National tests, year 6" h={s.h.np6} dec={1} countyV={c.np6} />,
    <TrendChart key="9" title="National tests, year 9" h={s.h.np9} dec={1} countyV={c.np9} />,
    <TrendChart key="m" title="Merit rating, year 9" h={s.h.merit9} dec={0} countyV={c.merit9} />,
    <TrendChart key="p" title="Passed all subjects, year 9" h={s.h.pass9} dec={0} countyV={c.pass9} unit=" %" />,
  ];
  const hasTrends = ["teachers", "np6", "np9", "merit9", "pass9"].some(k => s.h[k] && Object.keys(s.h[k]).length >= 2);
  return (
    <section id="v-school">
      <div className="inner crumb"><a href="#find"><Ic n="back" />Back to results</a></div>
      <div className="inner sh">
        <div style={{ minWidth: 0 }}><h1>{s.name}</h1>
          <div className="sub"><OrgPill s={s} /><span>{s.addr}{s.addr ? ", " : ""}{s.mun}</span>{d != null && <span className="dist"><Ic n="pin" />{fmt(d, 1)} km from {home?.label || "home"}</span>}</div>
          <div className="sub"><span className="line"><GradeLine s={s} w={220} labels start={F.start} /></span></div></div>
        <div className="acts">{s.web && <a className="btn" href={s.web} target="_blank" rel="noopener">School website <Ic n="ext" /></a>}<CmpBtn s={s} big /></div>
      </div>
      <div className="inner"><div className="keyfigs">
        <KF l="Qualified teachers" v={t?.v} u="%" cv={c.teachers} dec={0} unit=" %" why={reason(t?.st)} />
        <KF l="Pupils per teacher" v={ptr?.v} u="" cv={c.ptr} dec={1} unit="" why={reason(ptr?.st)} />
        <KF l="National tests, year 6" v={n6?.v} u="/20" cv={c.np6} dec={1} unit="" why={reason(n6?.st)} has={s.g.includes(6)} />
        <KF l="National tests, year 9" v={n9?.v} u="/20" cv={c.np9} dec={1} unit="" why={reason(n9?.st)} has={s.g.includes(9)} />
        <KF l="Parents satisfied" v={sat?.pos} u="%" cv={D.svMedian} dec={0} unit=" %" why="No parent survey" />
      </div></div>
      <div className="inner sgrid">
        <div className="stack" style={{ minWidth: 0 }}>
          <section className="sec"><div className="sec-h"><h2>Results</h2></div>
            <div className="twocol">{resYear("6")}{resYear("9")}</div>
            {(s.g.includes(6) || s.g.includes(9)) && <div><div className="sub-h">Outcomes</div>
              {s.g.includes(6) && <HBar label="Passed all, yr 6" v={s.m.pass6?.v} max={100} med={c.pass6} unit=" %" dec={0} na={reason(s.m.pass6?.st)} />}
              {s.g.includes(9) && <>
                <HBar label="Passed all, yr 9" v={s.m.pass9?.v} max={100} med={c.pass9} unit=" %" dec={0} na={reason(s.m.pass9?.st)} />
                <HBar label="Upper secondary" v={s.m.elig?.v} max={100} med={c.elig} unit=" %" dec={0} na={reason(s.m.elig?.st)} />
                <HBar label="Merit rating" v={m9?.v} max={340} med={c.merit9} unit="" dec={0} na={reason(m9?.st)} />
              </>}
            </div>}
            <div className="keyline"><span><i style={{ width: 2, height: 12, background: "var(--ink)", opacity: 0.55 }} />County median</span><span>Tests are average grade points, A = 20 and F = 0. Tests {D.periods.np6}, grades {D.periods.merit9}.</span></div>
          </section>
          {hasTrends && <section className="sec"><div className="sec-h"><h2>Over the years</h2><span className="note">Dashed line shows the county median today</span></div><div className="trends">{trends}</div></section>}
          <section className="sec"><div className="sec-h"><h2>What families say</h2>
            {s.sv && <div className="seg inline" role="group" aria-label="Whose answers">
              {(Object.keys(SVWHO) as (keyof typeof SVWHO)[]).map(k => <button key={k} type="button" aria-pressed={k === who} title={s.sv?.[k] ? undefined : "Not published for this school"} onClick={() => setWho(k)}>{SVWHO[k]}</button>)}
            </div>}</div>
            {!s.sv ? <p className="note">This school has no published survey answers from spring 2026. Smaller schools and schools that did not take part are not published.</p>
              : !svd ? <p className="note">No answers from {SVWHO[who].toLowerCase()} were published for this school.</p>
              : <><div className="svq">{SVT.map(([k, l]) => { const x = svd[k]; return x ? <div className="svr" key={k}><span className="q">{l}</span><Stack x={x} /><span className="p">{x.pos}%</span></div> : null; })}</div><SvKey n={Object.values(svd)[0]?.n} /></>}
            <p className="note">Skolverket school survey, spring 2026.</p>
          </section>
          <section className="sec"><div className="sec-h"><h2>Teaching profile</h2></div>
            <p className="note">How the school describes itself on its own website. Every quote links to its source.</p>
            {s.approach.length ? <div className="claims">{s.approach.map((a, i) => (
              <div className="claim" key={i}><div className="ch"><b>{a.sub || SHORT[a.cat]}</b><span className="tag">{SHORT[a.cat]}</span></div>
                <blockquote lang="sv">{a.q}</blockquote>
                <div className="src">From the school's website, in Swedish{a.date ? `, read ${fmtDate(a.date)}` : ""}{a.url && <>. <a href={a.url} target="_blank" rel="noopener">Open source <Ic n="ext" /></a></>}</div></div>
            ))}</div> : <p className="note">{s.label === "No usable public page" ? "We could not find a usable website for this school." : "The school's website does not describe a particular teaching profile."}</p>}
          </section>
          <section className="sec"><div className="sec-h"><h2>Building and everyday life</h2></div>
            <table className="facts"><tbody>{FACTS.map(([l, f]) => { const x = f(s); return <tr key={l}><th scope="row">{l}</th>{x ? <td className={x.y ? "y" : ""} title={x.q ?? undefined}>{x.t}</td> : <td className="ns">Not stated</td>}</tr>; })}</tbody></table>
            <p className="note">Not stated means the website does not mention it. The school may still have it.</p>
          </section>
        </div>
        <aside className="aside">
          <section className="sec"><h2>How it fits your priorities</h2><div>
            {act.length ? act.map(p => { const e = explain(p.k, s, D, P, F, home); return (
              <div key={p.k} className={"prow " + e.r}><span className="pi"><Ic n={e.r === "yes" ? "check" : e.r === "no" ? "x" : "q"} /></span>
                <div><b>{prName(p.k)}{p.m === 2 && <> <span className="pill" style={{ height: 18, fontSize: 11 }}>Must</span></>}</b><span>{e.t}</span></div></div>); })
              : <p className="note">Pick what matters to you on the search page to see how this school fits.</p>}
          </div></section>
          <section className="sec"><h2>Details</h2><dl className="kv">
            <div><dt>Run by</dt><dd>{cap((s.orgName || "").toLowerCase())}</dd></div>
            <div><dt>Address</dt><dd>{s.addr || "Not listed"}</dd></div>
            <div><dt>Years</dt><dd>{s.grades}</dd></div>
            {s.web && <div><dt>Website</dt><dd><a href={s.web} target="_blank" rel="noopener">{s.web.replace(/^https?:\/\/(www\.)?/, "").replace(/\/$/, "")}</a></dd></div>}
            <div><dt>School unit code</dt><dd>{s.id}</dd></div>
          </dl>
            {s.lat != null && <button className="btn sm" type="button" style={{ justifySelf: "start" }} onClick={() => { setFocusId(s.id); location.hash = "find"; }}><Ic n="map" />Show on map</button>}
          </section>
        </aside>
      </div>
    </section>
  );
}
