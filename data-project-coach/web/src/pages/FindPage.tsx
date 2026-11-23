import { useMemo, useState } from "react";
import { ApproachDropdown } from "../components/Approach";
import { ChartPanel, chartFoot } from "../components/ChartPanel";
import { Chips } from "../components/Chips";
import { HowPanel } from "../components/HowPanel";
import { Ic } from "../components/Icons";
import { MapPanel } from "../components/MapPanel";
import { PlaceInput } from "../components/PlaceInput";
import { Preview } from "../components/Preview";
import { APRI, PRI, YL } from "../lib/constants";
import { cap, fmt } from "../lib/format";
import { activePicks } from "../lib/scoring";
import { useApp } from "../lib/store";
import type { Mode } from "../lib/types";

const FEATURE_NAME: Record<string, string> = { teach: "Qualified teachers", res: "Strong results", happy: "Happy parents", green: "Green surroundings" };

export function FindPage() {
  const app = useApp();
  const { D, P, setP, F, setF, home, guided, setGuided, chartYr, setChartYr, R, list, sum, setPicking } = app;
  const [hover, setHover] = useState<string | null>(null);
  const [sel, setSel] = useState<{ id: string; where: "map" | "chart" } | null>(null);
  const [fitKey, setFitKey] = useState(0);
  const [how, setHow] = useState(false);
  const guideOpen = !guided;
  const act = activePicks(P, home);
  const muns = useMemo(() => [...new Set(D.schools.map(s => s.mun))].sort((a, b) => a.localeCompare(b, "sv")), [D]);
  const pickHome = () => { setPicking(true); document.getElementById("panel")?.scrollIntoView({ behavior: "smooth", block: "center" }); };
  const m = (k: string) => P[k as "teach"].m;

  // Answer headline
  const where = sum.nearScope ? `within ${P.near.km} km of ${home?.label || "your home"}` : F.mun ? `in ${F.mun}` : "in Stockholm county";
  const sc = sum.scope === 1 ? "1 school" : `${fmt(sum.scope)} schools`;
  let ah: string, ap: string;
  if (!act.length) { ah = `${cap(sc)} ${where}.`; ap = "Pick what matters to you to see which ones fit."; }
  else if (!sum.scope) { ah = `There are no schools ${where} with these filters.`; ap = "Try a wider distance or a different starting year."; }
  else if (sum.all) { ah = `Of ${sc} ${where}, ${sum.all === 1 ? "1 fits" : fmt(sum.all) + " fit"} everything you picked.`; ap = (sum.most ? `${fmt(sum.most)} more fit all but one. ` : "") + "Full dots on the map and chart fit everything."; }
  else { ah = `Of ${sc} ${where}, none fit everything you picked yet.`; ap = sum.most ? `${fmt(sum.most)} fit all but one. Try turning a must-have into a nice to have.` : "Try fewer priorities or a lower threshold."; }
  if (sum.mustOut && act.some(x => x.m === 2 && x.k !== "near")) ap += ` ${fmt(sum.mustOut)} that miss a must-have are hidden.`;
  const anyMust = act.some(x => x.m === 2);

  const selR = sel ? R.get(sel.id) : undefined;
  const select = (where: "map" | "chart") => (id: string | null) => setSel(id ? { id, where } : null);

  return (
    <section id="v-find">
      <div className="band"><div className="inner">
        <div className="bandhead">
          <div>
            <h1>Find the right school for your child</h1>
            <p className="lede">Compare {fmt(D.schools.length)} compulsory schools across Stockholm county on teachers, test results, what families say and how each school describes itself.</p>
          </div>
          {!guideOpen && <button className="linkbtn" type="button" onClick={() => setGuided(false)}>Start again with four questions</button>}
        </div>

        {guideOpen ? (
          <div>
            <ol className="steps">
              <li className={"step" + (home ? " done" : "")}><span className="sn">1</span><h3>Where do you live?</h3><p className="hint">A neighbourhood, town or street</p>
                <div><PlaceInput id="place1" /><div style={{ marginTop: 8 }}><button className="linkbtn" type="button" onClick={pickHome}>Or click your home on the map</button></div></div></li>
              <li className={"step" + (F.start !== "" ? " done" : "")}><span className="sn">2</span><h3>Which year does your child start in?</h3><p className="hint">We'll only show schools that have that year</p>
                <div className="yrs">
                  {YL.map((l, i) => <button key={i} className="yr" type="button" aria-pressed={String(i) === F.start} aria-label={i ? "Year " + l : "Förskoleklass"}
                    onClick={() => { setF(f => ({ ...f, start: String(i) })); if (i >= 7) setChartYr("9"); }}>{l}</button>)}
                  <button className="yr wide" type="button" aria-pressed={F.start === ""} onClick={() => setF(f => ({ ...f, start: "" }))}>Not sure yet</button>
                </div></li>
              <li className={"step" + (APRI.some(a => m(a.k)) ? " done" : "")}><span className="sn">3</span><h3>Which teaching approach would you like?</h3><p className="hint">Pick as many as you like, or skip.</p>
                <div><ApproachDropdown /></div></li>
              <li className={"step" + (PRI.some(p => p.k !== "near" && m(p.k)) ? " done" : "")}><span className="sn">4</span><h3>What else matters to you?</h3><p className="hint">Pick one or more, or skip.</p>
                <div className="gpicks">
                  {PRI.filter(p => p.k !== "near").map(p => (
                    <button key={p.k} className="gpick" type="button" aria-pressed={m(p.k) > 0}
                      onClick={() => setP(x => { const o = x[p.k as "teach"]; o.m = (o.m ? 0 : 1) as Mode; return x; })}>
                      <Ic n={p.ic} />{FEATURE_NAME[p.k]}
                    </button>
                  ))}
                </div></li>
            </ol>
            <div className="guide-foot" style={{ marginTop: 14 }}>
              <button className="btn primary lg" type="button" onClick={() => { setGuided(true); requestAnimationFrame(() => document.querySelector(".explore")?.scrollIntoView({ behavior: "smooth", block: "start" })); }}>Show my matches</button>
              <button className="btn ghost" type="button" onClick={() => setGuided(true)}>Skip and browse all schools</button>
              <p className="note" aria-live="polite">{act.length ? (sum.all ? `Right now: ${ah}` : `Right now: ${fmt(list.length)} schools to look through.`) : ""}</p>
            </div>
          </div>
        ) : (
          <div className="searchgrid">
            <div className="field f-place"><span>Where you live</span><PlaceInput id="place2" /></div>
            <label className="field f-q"><span>School name</span><div className="qwrap"><Ic n="search" /><input className="txt" type="search" placeholder="e.g. Vasa or Bromma" autoComplete="off" value={F.q} onChange={e => setF(f => ({ ...f, q: e.target.value }))} /></div></label>
            <label className="field"><span>Area</span>
              <select className="sel" value={F.mun} onChange={e => { setF(f => ({ ...f, mun: e.target.value })); setTimeout(() => setFitKey(k => k + 1), 50); }}>
                <option value="">All of Stockholm county</option>{muns.map(x => <option key={x}>{x}</option>)}
              </select></label>
            <label className="field"><span>Your child starts in</span>
              <select className="sel" value={F.start} onChange={e => { const v = e.target.value; setF(f => ({ ...f, start: v })); if (v !== "" && +v >= 7) setChartYr("9"); }}>
                <option value="">Any year</option>{YL.map((l, i) => <option key={i} value={i}>{i === 0 ? "Förskoleklass (F)" : "Year " + l}</option>)}
              </select></label>
            <div className="field f-ap"><span>Teaching approach</span><div className="aprowf"><ApproachDropdown /></div></div>
          </div>
        )}
      </div></div>

      {!guideOpen && (
        <div className="pri"><div className="inner">
          <h2 id="priH">Your priorities <span className="aphint">tap one to set Must have or Nice to have</span></h2>
          <Chips onPickHome={pickHome} />
          <div className="morefilters">
            <select className="sel" aria-label="Who runs the school" value={F.org} onChange={e => setF(f => ({ ...f, org: e.target.value }))}>
              <option value="">Municipal and independent</option><option value="municipal">Municipal only</option><option value="independent">Independent only</option>
            </select>
            <label className="check"><input type="checkbox" checked={F.stay9} onChange={e => setF(f => ({ ...f, stay9: e.target.checked }))} /> Can stay until year 9</label>
            <label className="check"><input type="checkbox" checked={F.fritids} onChange={e => setF(f => ({ ...f, fritids: e.target.checked }))} /> Has fritidshem</label>
          </div>
        </div></div>
      )}

      <div className="inner explore">
        <div className="answer">
          <div aria-live="polite"><h2>{ah}</h2><p>{ap.trim()}</p></div>
          <div className="rtools">
            {anyMust && !sum.all && <button className="btn sm" type="button" onClick={() => setP(p => { for (const x of [...PRI, ...APRI]) { const o = p[x.k as "teach"]; if (o.m === 2) o.m = 1; } return p; })}>Make every must-have a nice to have</button>}
            <button className="btn sm howbtn" type="button" aria-expanded={how} onClick={() => setHow(h => !h)}><Ic n="code" />How this is calculated</button>
          </div>
        </div>
        {how && <HowPanel onClose={() => setHow(false)} />}
        <section className="panel" id="panel" aria-label="Map of schools">
          <div className="phead"><h3 className="ptitle"><Ic n="map" />Where they are</h3>
            <div className="legend"><span><i style={{ background: "var(--brand)" }} />Fits everything</span><span><i style={{ background: "var(--surface)", border: "2px solid var(--brand)" }} />Fits some (filled share)</span><span><i style={{ background: "var(--dot-out)", width: 7, height: 7 }} />Filtered out</span><span><i style={{ width: 14, height: 0, borderTop: "1.5px solid var(--muted)", borderRadius: 0 }} />Kommun border</span></div></div>
          <div className="pbody" id="mapBody">
            <MapPanel hover={hover} sel={sel?.where === "map" ? sel.id : null} onHover={setHover} onSelect={select("map")} fitKey={fitKey} />
            {selR && sel?.where === "map" && <Preview r={selR} onClose={() => setSel(null)} />}
          </div>
          <div className="pfoot">{home ? `Dashed circle: ${P.near.km} km from ${home.label || "your home"}. Drag to move, scroll or pinch to zoom.` : "Drag to move, scroll or pinch to zoom. Click a dot to preview the school."}</div>
        </section>
        <section className="panel" id="cpanel" aria-label="Teachers and results chart">
          <div className="phead"><h3 className="ptitle"><Ic n="scatter" />Teachers and results</h3>
            <div className="seg inline" role="group" aria-label="Results for">
              {(["6", "9"] as const).map(y => <button key={y} type="button" aria-pressed={chartYr === y} onClick={() => setChartYr(y)}>Year {y}</button>)}
            </div></div>
          <div className="pbody" id="chartBody">
            <ChartPanel hover={hover} sel={sel?.where === "chart" ? sel.id : null} onHover={setHover} onSelect={select("chart")} />
            {selR && sel?.where === "chart" && <Preview r={selR} onClose={() => setSel(null)} />}
          </div>
          <div className="pfoot">{chartFoot(R, chartYr, D.county)}</div>
        </section>
      </div>

      <footer className="about"><div className="inner">
        <div><h2>About the data</h2><p className="note" style={{ marginTop: 6 }}>Figures are the latest published for each school. Every number on this page is read with SQL from the project's dbt models. <a href="#pipeline">See the data pipeline</a>.</p></div>
        <dl>
          <div><dt>Teachers and pupils</dt><dd>Skolverket statistics, {D.periods.teachers}. Qualified teachers means teachers with a teaching degree.</dd></div>
          <div><dt>National tests</dt><dd>Skolverket, {D.periods.np6}. Average grade points in maths, Swedish and English (A = 20, F = 0). Year 9 merit rating runs 0–340.</dd></div>
          <div><dt>What families say</dt><dd>Skolverket school survey, spring 2026. Not every school took part; small schools are not published.</dd></div>
          <div><dt>Profile and setting</dt><dd>What each school says on its own website, reviewed November 2026, with quotes and links. Green share is measured within 300 m on map data.</dd></div>
          <div><dt>Where you live</dt><dd>Place search matches the towns, neighbourhoods and streets in the school register. Distances are straight-line. Map © OpenStreetMap contributors, tiles by OpenFreeMap.</dd></div>
        </dl>
      </div></footer>
    </section>
  );
}
