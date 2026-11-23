import { useLayoutEffect, useRef, useState } from "react";
import { CC } from "../lib/constants";
import { fmt } from "../lib/format";
import { useApp } from "../lib/store";
import type { Result } from "../lib/types";
import { SvgGlyph } from "./bits";

const CX = { x0: 30, x1: 100 }, CY = { y0: 7, y1: 18 };

export function chartPoints(R: Map<string, Result>, yr: "6" | "9", county: Record<string, number>) {
  const out: { r: Result; t: number; y: number; strong: boolean }[] = []; let missing = 0;
  for (const r of R.values()) {
    const t = r.s.m.teachers?.v, y = r.s.g.includes(+yr) ? r.s.m["np" + yr]?.v : null;
    if (t == null || y == null) { if (r.fit) missing++; continue; }
    out.push({ r, t, y, strong: t > county.teachers && y > county["np" + yr] });
  }
  return { pts: out, missing };
}

/** Scatter of qualified teachers against national tests; the top-right box is "strong on both". */
export function ChartPanel({ hover, sel, onHover, onSelect }: { hover: string | null; sel: string | null; onHover: (id: string | null) => void; onSelect: (id: string | null) => void }) {
  const { R, D, cmp, chartYr } = useApp();
  const ref = useRef<SVGSVGElement>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });
  useLayoutEffect(() => {
    const el = ref.current!; const ro = new ResizeObserver(() => setSize({ w: el.clientWidth, h: el.clientHeight }));
    ro.observe(el); return () => ro.disconnect();
  }, []);
  const { w, h } = size;
  const m = { l: 52, r: 16, t: 20, b: 46 };
  const X = (v: number) => m.l + ((Math.max(CX.x0, Math.min(CX.x1, v)) - CX.x0) / (CX.x1 - CX.x0)) * (w - m.l - m.r);
  const Y = (v: number) => m.t + (1 - (Math.max(CY.y0, Math.min(CY.y1, v)) - CY.y0) / (CY.y1 - CY.y0)) * (h - m.t - m.b);
  const { pts } = chartPoints(R, chartYr, D.county);
  const fp = pts.filter(p => p.r.fit).sort((a, b) => a.r.met - b.r.met);
  const mx = X(D.county.teachers), my = Y(D.county["np" + chartYr]);
  const hp = hover ? fp.find(q => q.r.s.id === hover) : null;
  const xt: number[] = []; for (let v = CX.x0; v <= CX.x1; v += 10) xt.push(v);
  const yt: number[] = []; for (let v = 8; v <= CY.y1; v += 2) yt.push(v);
  return (
    <>
      <svg id="chart" ref={ref} viewBox={`0 0 ${w || 1} ${h || 1}`} role="img" aria-label="Chart of qualified teachers against national test results for matching schools"
        onPointerMove={e => { const g = (e.target as Element).closest(".pt") as SVGGElement | null; onHover(g ? g.dataset.id! : null); }}
        onPointerLeave={() => onHover(null)}
        onClick={e => { const g = (e.target as Element).closest(".pt") as SVGGElement | null; onSelect(g ? g.dataset.id! : null); }}>
        {w > 0 && <>
          <rect x={mx} y={m.t} width={Math.max(0, w - m.r - mx)} height={Math.max(0, my - m.t)} fill="var(--quad)" />
          <g className="axis">
            {xt.map(v => <g key={v}><line x1={X(v)} x2={X(v)} y1={m.t} y2={h - m.b} opacity={0.5} /><text x={X(v)} y={h - m.b + 16} textAnchor="middle">{v}%</text></g>)}
            {yt.map(v => <g key={v}><line x1={m.l} x2={w - m.r} y1={Y(v)} y2={Y(v)} opacity={0.5} /><text x={m.l - 8} y={Y(v) + 4} textAnchor="end">{v}</text></g>)}
            <text x={(m.l + w - m.r) / 2} y={h - 8} textAnchor="middle" style={{ fontWeight: 600, fill: "var(--ink2)" }}>Qualified teachers</text>
            <text transform={`translate(14 ${(m.t + h - m.b) / 2}) rotate(-90)`} textAnchor="middle" style={{ fontWeight: 600, fill: "var(--ink2)" }}>National tests, year {chartYr} (grade points)</text>
          </g>
          <line x1={mx} x2={mx} y1={m.t} y2={h - m.b} stroke="var(--ink)" strokeDasharray="4 4" opacity={0.4} />
          <line x1={m.l} x2={w - m.r} y1={my} y2={my} stroke="var(--ink)" strokeDasharray="4 4" opacity={0.4} />
          <text x={w - m.r - 8} y={m.t + 16} textAnchor="end" style={{ font: "700 12px var(--font)", fill: "var(--brand)" }}>Strong on both</text>
          <text x={m.l + 8} y={m.t + 16} style={{ font: "600 11px var(--font)", fill: "var(--muted)" }}>Higher results</text>
          <text x={w - m.r - 8} y={h - m.b - 8} textAnchor="end" style={{ font: "600 11px var(--font)", fill: "var(--muted)" }}>More qualified teachers</text>
          {pts.filter(p => !p.r.fit).map(p => <circle key={p.r.s.id} cx={X(p.t)} cy={Y(p.y)} r={2} fill="var(--line2)" />)}
          {fp.map(p => <SvgGlyph key={p.r.s.id} res={p.r} x={+X(p.t).toFixed(1)} y={+Y(p.y).toFixed(1)} rad={5} className="pt" data-id={p.r.s.id} />)}
          {cmp.map((id, i) => { const p = fp.find(q => q.r.s.id === id); return p ? <circle key={id} cx={X(p.t)} cy={Y(p.y)} r={9.5} fill="none" stroke={`var(${CC[i]})`} strokeWidth={3} pointerEvents="none" /> : null; })}
          {[hover, sel].map((id, j) => { const p = id && fp.find(q => q.r.s.id === id); return p ? <circle key={j} cx={X(p.t)} cy={Y(p.y)} r={cmp.includes(id!) ? 13 : 9} fill="none" stroke="var(--ink)" strokeWidth={2.2} pointerEvents="none" /> : null; })}
        </>}
      </svg>
      {hp && hover !== sel && <div className="maptip" style={{ left: Math.max(90, Math.min(w - 90, X(hp.t))), top: Y(hp.y) }}>{hp.r.s.name}</div>}
    </>
  );
}
export const chartFoot = (R: Map<string, Result>, yr: "6" | "9", county: Record<string, number>) => {
  const { pts, missing } = chartPoints(R, yr, county);
  const fits = pts.filter(p => p.r.fit), strong = fits.filter(p => p.strong);
  return `${fits.length ? `${strong.length} of the ${fits.length} matching schools shown are strong on both. ` : ""}Dashed lines are county medians: teachers ${fmt(county.teachers)} %, tests ${fmt(county["np" + yr], 1)}.${missing ? ` ${missing} matching schools are not shown because they have no year ${yr} or no figures.` : ""}`;
};
