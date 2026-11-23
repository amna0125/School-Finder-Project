import { YL } from "../lib/constants";
import { fmt } from "../lib/format";
import { useApp } from "../lib/store";
import type { Result, School } from "../lib/types";
import { Ic } from "./Icons";

/** Years F–9 drawn as a metro line; the starting year gets a ring. */
export function GradeLine({ s, w = 132, labels = false, start }: { s: School; w?: number; labels?: boolean; start?: string }) {
  const n = 10, pad = 6, step = (w - pad * 2) / (n - 1), y = labels ? 8 : 7, h = labels ? 30 : 14;
  const g = s.g || []; const a = Math.min(...g), b = Math.max(...g);
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} role="img" aria-label={"Years " + s.grades}>
      <line x1={pad} x2={w - pad} y1={y} y2={y} stroke="var(--line)" strokeWidth={2} />
      {g.length > 0 && <line x1={pad + a * step} x2={pad + b * step} y1={y} y2={y} stroke="var(--brand)" strokeWidth={4} strokeLinecap="round" />}
      {YL.map((l, i) => {
        const x = pad + i * step, on = g.includes(i), end = on && (i === a || i === b), st = start != null && start !== "" && +start === i;
        return (
          <g key={i}>
            {st && <circle cx={x} cy={y} r={6.5} fill="none" stroke="var(--sun)" strokeWidth={2.4} />}
            {on ? <circle cx={x} cy={y} r={end ? 4.2 : 2.6} fill="var(--surface)" stroke="var(--brand)" strokeWidth={end ? 2.4 : 1.8} />
              : <circle cx={x} cy={y} r={1.6} fill="var(--line2)" />}
            {labels && <text x={x} y={h - 2} textAnchor="middle" fontSize={10.5} fontWeight={on ? 700 : 500} fill={on ? "var(--ink)" : "var(--muted)"} fontFamily="var(--font)">{l}</text>}
          </g>
        );
      })}
    </svg>
  );
}

export const OrgPill = ({ s }: { s: School }) =>
  s.org === "municipal" ? <span className="pill">Municipal</span> : <span className="pill ind">Independent</span>;

export function Delta({ v, c, d = 0, unit = "" }: { v: number | null | undefined; c: number | null | undefined; d?: number; unit?: string }) {
  if (v == null || c == null) return null;
  const r = Math.round((v - c) * 10 ** d) / 10 ** d;
  const cls = r > 0 ? "up" : r < 0 ? "dn" : "eq";
  return <span className={"delta " + cls} title={`Compared with the county median ${fmt(c, d)}${unit}`}>{r > 0 ? "+" : r < 0 ? "−" : "±"}{fmt(Math.abs(r), d)}</span>;
}

export function CmpBtn({ s, big = false }: { s: School; big?: boolean }) {
  const { cmp, toggleCmp } = useApp();
  const on = cmp.includes(s.id);
  return (
    <button className="cmpbtn" type="button" aria-pressed={on} onClick={e => { e.preventDefault(); toggleCmp(s.id); }}
      style={big ? { height: 40, fontSize: 14, padding: "0 16px 0 12px" } : undefined}
      aria-label={`${on ? "Remove " + s.name + " from" : "Add " + s.name + " to"} compare`}>
      <span className="bx"><Ic n="check" /></span>
      <span className="cl">{big ? (on ? "Added to compare" : "Add to compare") : on ? "Comparing" : "Compare"}</span>
    </button>
  );
}

export const share = (r: Result) => (r.n ? r.met / r.n : 0);

/** A dot whose filled share shows how many priorities the school meets. */
export function SvgGlyph({ res: r, x, y, rad, ...rest }: { res: Result; x: number; y: number; rad: number } & Omit<React.SVGProps<SVGGElement>, "r" | "x" | "y">) {
  const f = share(r);
  let fill = null;
  if (f >= 1) fill = <circle cx={x} cy={y} r={rad} fill="var(--brand)" />;
  else if (f > 0) {
    const a = -Math.PI / 2 + f * Math.PI * 2, ex = x + rad * Math.cos(a), ey = y + rad * Math.sin(a);
    fill = <path d={`M${x} ${y}L${x} ${y - rad}A${rad} ${rad} 0 ${f > 0.5 ? 1 : 0} 1 ${ex.toFixed(2)} ${ey.toFixed(2)}Z`} fill="var(--brand)" />;
  }
  return (
    <g opacity={r.unk ? 0.5 : 1} {...rest}>
      <circle cx={x} cy={y} r={rad + 5} fill="transparent" />
      <circle cx={x} cy={y} r={rad} fill="var(--surface)" stroke="var(--brand)" strokeWidth={1.5} />
      {fill}
    </g>
  );
}

/** Horizontal bar with the county median as a tick. */
export function HBar({ label, v, max, med, unit, dec, na = "Not reported", color = "var(--brand)", sw = false }:
  { label: string; v: number | null | undefined; max: number; med?: number | null; unit: string; dec: number; na?: string; color?: string; sw?: boolean }) {
  const P_ = (x: number) => Math.max(0, Math.min(100, (x / max) * 100));
  return (
    <div className={"bar" + (sw ? " sw" : "")} title={label}>
      {sw ? <i style={{ background: color }} /> : <span className="bl">{label}</span>}
      <div className="trk">
        {v != null && <div className="f" style={{ width: P_(v) + "%", background: color }} />}
        {med != null && <div className="md" style={{ left: `calc(${P_(med)}% - 1px)` }} title={`County median ${fmt(med, dec)}${unit}`} />}
      </div>
      <span className={"bv" + (v == null ? " na" : "")}>{v == null ? na : fmt(v, dec) + unit}</span>
    </div>
  );
}

export function Stack({ x, who }: { x: { pos: number; mid: number; neg: number }; who?: string }) {
  return (
    <div className="stk" title={`${who ? who + ": " : ""}${x.pos} % agree, ${x.mid} % in between, ${x.neg} % disagree`}>
      <span style={{ width: x.pos + "%", background: "var(--good)" }} />
      <span style={{ width: x.mid + "%", background: "var(--line2)" }} />
      <span style={{ width: x.neg + "%", background: "var(--bad)" }} />
    </div>
  );
}
export function SvKey({ n }: { n?: number | null }) {
  const sq = (c: string) => <i style={{ width: 10, height: 10, borderRadius: 2, background: c }} />;
  return (
    <div className="keyline">
      <span>{sq("var(--good)")}Agree</span><span>{sq("var(--line2)")}In between or don't know</span><span>{sq("var(--bad)")}Disagree</span>
      {n ? <span>{fmt(n)} answers</span> : null}
    </div>
  );
}

/** Simple line chart of one school's figures by school year. */
export function TrendChart({ title, h, dec, countyV, unit = "" }: { title: string; h?: Record<string, number>; dec: number; countyV?: number; unit?: string }) {
  if (!h || Object.keys(h).length < 2) return null;
  const pers = Object.keys(h).sort(), vals = pers.map(p => h[p]);
  let lo = Math.min(...vals, countyV ?? Infinity), hi = Math.max(...vals, countyV ?? -Infinity);
  const pad = (hi - lo) * 0.2 || 1; lo -= pad; hi += pad;
  const W0 = 300, H0 = 130, l = 36, r = 10, t = 10, b = 22;
  const X = (i: number) => l + (i / (pers.length - 1)) * (W0 - l - r), Y = (v: number) => t + (1 - (v - lo) / (hi - lo)) * (H0 - t - b);
  const ch = vals[vals.length - 1] - vals[0];
  const pts = pers.map((p, i) => [X(i), Y(h[p])]);
  return (
    <div className="trend">
      <div className="tt">{title}</div>
      <div className="tn">{pers[0].slice(0, 4)} to {pers[pers.length - 1].slice(0, 4)}: <b style={{ color: `var(${ch > 0 ? "--good" : ch < 0 ? "--bad" : "--muted"})` }}>{ch > 0 ? "up" : ch < 0 ? "down" : "unchanged"} {ch ? fmt(Math.abs(ch), dec) + (unit === " %" ? " points" : unit) : ""}</b></div>
      <svg viewBox={`0 0 ${W0} ${H0}`} role="img" aria-label={title + " by school year"}>
        {[lo + pad, (lo + hi) / 2, hi - pad].map((v, i) => (
          <g key={i}><line x1={l} x2={W0 - r} y1={Y(v)} y2={Y(v)} stroke="var(--line)" /><text x={l - 6} y={Y(v) + 3.5} textAnchor="end" fontSize={10} fill="var(--muted)" fontFamily="var(--font)">{fmt(v, dec)}</text></g>
        ))}
        {countyV != null && <line x1={l} x2={W0 - r} y1={Y(countyV)} y2={Y(countyV)} stroke="var(--ink)" strokeDasharray="4 4" opacity={0.45} />}
        {pers.map((p, i) => <text key={p} x={X(i)} y={H0 - 5} textAnchor="middle" fontSize={10} fill="var(--muted)" fontFamily="var(--font)">{p.slice(2, 4)}/{p.slice(5)}</text>)}
        <path d={`M${pts.map(q => q.join(",")).join("L")}L${pts[pts.length - 1][0]},${H0 - b}L${pts[0][0]},${H0 - b}Z`} fill="var(--brand)" opacity={0.08} />
        <polyline points={pts.map(q => q.join(",")).join(" ")} fill="none" stroke="var(--brand)" strokeWidth={2.5} strokeLinejoin="round" strokeLinecap="round" />
        {pts.map((q, i) => (
          <circle key={i} cx={q[0]} cy={q[1]} r={i === pts.length - 1 ? 4.5 : 3} fill={i === pts.length - 1 ? "var(--brand)" : "var(--surface)"} stroke="var(--brand)" strokeWidth={2}>
            <title>{pers[i]}: {fmt(vals[i], dec)}{unit}</title>
          </circle>
        ))}
      </svg>
    </div>
  );
}
