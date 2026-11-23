import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { ALLP, APD, APRI, PRI } from "../lib/constants";
import { fmt } from "../lib/format";
import { useApp } from "../lib/store";
import type { Mode, Prefs } from "../lib/types";
import { Ic } from "./Icons";

const NAME: Record<string, string> = { teach: "Qualified teachers", res: "Strong results", happy: "Happy parents", green: "Green surroundings", near: "Close to home" };
export const prName = (k: string) => NAME[k] ?? APRI.find(a => a.k === k)?.short ?? k;
const popNote = (m: number) => (m === 2 ? "Schools that miss this are hidden." : m === 1 ? "Schools that meet this rank higher." : "This is ignored.");
const get = (P: Prefs, k: string) => P[k as "teach"] as { m: Mode; min?: number; yr?: string; lvl?: string; km?: number };

function param(k: string, P: Prefs, hasHome: boolean) {
  if (k === "teach") return P.teach.min + "%+";
  if (k === "happy") return P.happy.min + "%+";
  if (k === "res") return P.res.yr === "auto" ? "" : "year " + P.res.yr;
  if (k === "green") return P.green.lvl === "greener" ? "greener than most" : "";
  if (k === "near") return hasHome ? "within " + P.near.km + " km" : "";
  return "";
}

/** Picked priorities as chips. Tapping a chip opens a small box: Nice to have / Must have, a filter, Remove. */
export function Chips({ onPickHome }: { onPickHome: () => void }) {
  const { P, setP, home, D } = useApp();
  const svMedian = D.svMedian;
  const [pop, setPop] = useState<{ k: string; el: HTMLElement } | null>(null);
  const on = [...APRI.filter(a => get(P, a.k).m > 0), ...PRI.filter(p => get(P, p.k).m > 0)];
  const boxRef = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState<{ left: number; top: number; sheet: boolean }>({ left: 0, top: 0, sheet: false });

  useLayoutEffect(() => {
    if (!pop || !boxRef.current) return;
    if (innerWidth < 640) { setPos({ left: 0, top: 0, sheet: true }); return; }
    const r = pop.el.getBoundingClientRect(), w = boxRef.current.offsetWidth;
    setPos({ left: Math.max(16, Math.min(innerWidth - w - 16, r.left)) + scrollX, top: r.bottom + scrollY + 8, sheet: false });
  }, [pop]);
  useEffect(() => {
    if (!pop) return;
    const f = (e: PointerEvent) => { const t = e.target as HTMLElement; if (!boxRef.current?.contains(t) && !t.closest(".chip")) setPop(null); };
    const k = (e: KeyboardEvent) => { if (e.key === "Escape") setPop(null); };
    document.addEventListener("pointerdown", f); document.addEventListener("keydown", k);
    return () => { document.removeEventListener("pointerdown", f); document.removeEventListener("keydown", k); };
  }, [pop]);

  const setMode = (k: string, m: Mode) => {
    setP(p => { get(p, k).m = m; return p; });
    if (k === "near" && m && !home) { setPop(null); onPickHome(); }
  };
  const setVal = (k: string, f: string, v: string | number) => setP(p => { const x = get(p, k) as Record<string, unknown>; x[f] = v; if (!x.m) x.m = 1; return p; });

  const k = pop?.k;
  const def = k ? ALLP.find(x => x.k === k) : null;
  const st = k && k !== "__add" ? get(P, k) : null;
  const desc = (k: string) => k.startsWith("ap") ? APD[APRI.find(a => a.k === k)!.cat!] + ". Based on what the school says on its own website."
    : k === "teach" ? `Share of teachers with a teaching degree. County median is ${fmt(D.county.teachers)} %.`
    : k === "res" ? "National test results above the county median. Schools without year 6 or 9 have no tests to compare."
    : k === "happy" ? `Parents who say they are satisfied with the school overall. County median is ${fmt(svMedian)} %.`
    : k === "green" ? "How much park, forest and grass there is within 300 m of the school, compared with other schools in the county."
    : "Straight-line distance from where you live.";

  return (
    <>
      <div className="chips" role="group" aria-labelledby="priH">
        {on.map(p => {
          const m = get(P, p.k).m, par = param(p.k, P, !!home), needHome = p.k === "near" && !home;
          return (
            <button key={p.k} className="chip" type="button" data-k={p.k} data-m={m} aria-haspopup="dialog"
              aria-label={`${prName(p.k)}: ${m === 2 ? "Must have" : "Nice to have"}`}
              onClick={e => setPop(pop?.k === p.k ? null : { k: p.k, el: e.currentTarget })}>
              <Ic n={p.ic} /><span>{prName(p.k)}{par && <> <span className="param">{par}</span></>}</span>
              <span className="state">{needHome ? "Add home" : m === 2 ? "Must" : "Nice"}</span>
            </button>
          );
        })}
        <button className="chip add" type="button" aria-haspopup="dialog" onClick={e => setPop(pop?.k === "__add" ? null : { k: "__add", el: e.currentTarget })}>
          <Ic n="plus" /><span>{on.length ? "Add" : "Add a priority"}</span>
        </button>
      </div>
      {pop && (
        <div id="pop" ref={boxRef} role="dialog" className={pos.sheet ? "sheet" : ""} style={pos.sheet ? undefined : { left: pos.left, top: pos.top }}>
          {k === "__add" ? (
            <>
              <h3><Ic n="plus" />Add a priority</h3>
              <div className="addlist">
                {PRI.some(p => !get(P, p.k).m) && <div className="addsub">Features</div>}
                {PRI.filter(p => !get(P, p.k).m).map(p => (
                  <button key={p.k} type="button" onClick={() => { setP(x => { get(x, p.k).m = 1; return x; }); setPop(null); if (p.k === "near" && !home) onPickHome(); }}>
                    <Ic n={p.ic} />{prName(p.k)}
                  </button>
                ))}
                {APRI.some(a => !get(P, a.k).m) && <div className="addsub">Teaching approach</div>}
                {APRI.filter(a => !get(P, a.k).m).map(a => (
                  <button key={a.k} type="button" onClick={() => { setP(x => { get(x, a.k).m = 1; return x; }); setPop(null); }}>
                    <Ic n="star" />{a.short}<small>{D.approachCounts[a.cat!] || 0} schools</small>
                  </button>
                ))}
              </div>
            </>
          ) : st && def ? (
            <>
              <h3><Ic n={def.ic} /><span>{prName(k!)}</span></h3>
              <p>{desc(k!)}</p>
              <div className="seg" role="group" aria-label="How much it matters">
                {([[1, "Nice to have"], [2, "Must have"]] as [Mode, string][]).map(([i, l]) => (
                  <button key={i} type="button" aria-pressed={st.m === i} onClick={() => setMode(k!, i)}>{l}</button>
                ))}
              </div>
              {(k === "teach" || k === "happy") && (
                <label className="field"><span>At least</span>
                  <div className="range"><input type="range" min={50} max={100} step={5} value={st.min} onChange={e => setVal(k, "min", +e.target.value)} /><output>{st.min} %</output></div>
                </label>
              )}
              {k === "res" && (
                <label className="field"><span>Which tests</span>
                  <select className="sel" value={P.res.yr} onChange={e => setVal(k, "yr", e.target.value)}>
                    <option value="auto">Year 6, or year 9 if the school has no year 6</option><option value="6">Year 6</option><option value="9">Year 9</option>
                  </select>
                </label>
              )}
              {k === "green" && (
                <label className="field"><span>How green</span>
                  <select className="sel" value={P.green.lvl} onChange={e => setVal(k, "lvl", e.target.value)}>
                    <option value="typical">Typical or greener</option><option value="greener">Greener than most</option>
                  </select>
                </label>
              )}
              {k === "near" && (
                <>
                  <label className="field"><span>Within</span>
                    <select className="sel" value={P.near.km} onChange={e => setVal(k, "km", +e.target.value)}>
                      {[1, 2, 3, 5, 10, 20].map(v => <option key={v} value={v}>{v} km</option>)}
                    </select>
                  </label>
                  {home ? <p>From {home.label}. Change it in "Where you live" above.</p>
                    : <button className="btn" type="button" onClick={() => { setPop(null); onPickHome(); }}><Ic n="home" />Click your home on the map</button>}
                </>
              )}
              <div className="pop-foot">
                <button className="linkbtn" type="button" onClick={() => { setP(p => { get(p, k!).m = 0; return p; }); setPop(null); }}>Remove</button>
                <span className="note" style={{ flex: 1 }}>{popNote(st.m)}</span>
                <button className="btn primary sm" type="button" onClick={() => setPop(null)}>Done</button>
              </div>
            </>
          ) : null}
        </div>
      )}
    </>
  );
}
