import { ALLP } from "../lib/constants";
import { fmt } from "../lib/format";
import { activePicks, explain, reason, resYear } from "../lib/scoring";
import { useApp } from "../lib/store";
import type { Result } from "../lib/types";
import { CmpBtn, Delta, GradeLine, OrgPill } from "./bits";
import { Ic } from "./Icons";

/** The small school card that opens over the map or chart when a dot is clicked. */
export function Preview({ r, onClose }: { r: Result; onClose: () => void }) {
  const { D, P, F, home } = useApp();
  const s = r.s, y = resYear(s, P, F), t = s.m.teachers, res = y ? s.m["np" + y] : null, hp = s.sv?.parents?.sat;
  const act = activePicks(P, home);
  return (
    <div className="preview">
      <div className="pv-card">
        <div className="c-top">
          <div style={{ minWidth: 0 }}>
            <a className="c-name" href={"#school-" + s.id}>{s.name}</a>
            <div className="c-sub">{s.addr}{s.addr ? ", " : ""}{s.mun}</div>
          </div>
        </div>
        <div className="c-meta">
          <OrgPill s={s} />
          <span className="line"><GradeLine s={s} start={F.start} /><b>Years {s.grades}</b></span>
          {r.d != null && <span className="dist"><Ic n="pin" />{fmt(r.d, 1)} km</span>}
        </div>
        <dl className="figs">
          <div className="fig"><dt>Qualified teachers</dt><dd>{t?.v != null ? <><span className="v">{fmt(t.v)}%</span><Delta v={t.v} c={D.county.teachers} unit=" %" /></> : <span className="na">{reason(t?.st)}</span>}</dd></div>
          <div className="fig"><dt>{y ? "National tests, year " + y : "National tests"}</dt><dd>{res?.v != null ? <><span className="v">{fmt(res.v, 1)}</span><Delta v={res.v} c={D.county["np" + y]} d={1} /></> : <span className="na">{y ? reason(res?.st) : "Not tested"}</span>}</dd></div>
          <div className="fig"><dt>Parents satisfied</dt><dd>{hp ? <><span className="v">{hp.pos}%</span><Delta v={hp.pos} c={D.svMedian} unit=" %" /></> : <span className="na">No survey</span>}</dd></div>
        </dl>
        {act.length > 0 && (
          <div className="c-foot">
            <span className={"matchline" + (r.all ? " all" : "")}>{!r.fit ? "Misses a must-have" : r.all ? "Fits everything you picked" : `Fits ${r.met} of ${r.n}`}</span>
            {act.map(p => { const e = explain(p.k, s, D, P, F, home); const v = r.ev[p.k] ?? e.r; return <span key={p.k} className={"fit " + v} title={e.t}><Ic n={v === "yes" ? "check" : v === "no" ? "x" : "q"} />{ALLP.find(x => x.k === p.k)!.short}</span>; })}
          </div>
        )}
      </div>
      <div className="acts"><a className="btn primary sm" href={"#school-" + s.id}>See school details</a><CmpBtn s={s} /></div>
      <button className="btn ghost sm x" type="button" aria-label="Close preview" onClick={onClose}><Ic n="x" /></button>
    </div>
  );
}
