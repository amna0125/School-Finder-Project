/**
 * Map of schools: MapLibre draws free OpenStreetMap-based tiles (OpenFreeMap, no key needed);
 * our own canvas on top draws the school dots, so a dot can show how many priorities it meets.
 */
import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";

maplibregl.setWorkerUrl(workerUrl);
import { useEffect, useRef } from "react";
import { cssVar } from "../lib/format";
import { isDark } from "../lib/theme";
import { CC } from "../lib/constants";
import { useApp } from "../lib/store";
import type { Result } from "../lib/types";
import { share } from "./bits";
import { Ic } from "./Icons";

const STYLE_LIGHT = "https://tiles.openfreemap.org/styles/positron";
const STYLE_DARK = "https://tiles.openfreemap.org/styles/dark";

/** OpenFreeMap's dark style is near-black with water and land the same shade and very dim labels.
 *  Recolour it to the site's dark palette so water, land, roads and place names are readable. */
const DARK_PAINT: [RegExp, string, string][] = [
  [/^background$/, "background-color", "#1A2531"],
  [/^water$/, "fill-color", "#0A131C"],
  [/^waterway$/, "line-color", "#0A131C"],
  [/^landcover_wood$|^landuse_park$/, "fill-color", "#1C2C2A"],
  [/^landuse_residential$/, "fill-color", "#223040"],
  [/^building$/, "fill-color", "#202D3A"],
  [/^highway_(minor|path)$/, "line-color", "#2A3846"],
  [/^highway_major_(inner|subtle)$/, "line-color", "#33424F"],
  [/^highway_motorway_(inner|subtle)$/, "line-color", "#3D4C5A"],
  [/_casing$/, "line-color", "#2A3846"],
  [/^railway/, "line-color", "#2A3846"],
  [/^boundary/, "line-color", "#45566A"],
  [/^place_/, "text-color", "#A9B7C4"],
  [/^place_/, "text-halo-color", "#0E151C"],
  [/^water_name$/, "text-color", "#6F8BA6"],
  [/^water_name$/, "text-halo-color", "#0A131C"],
  [/^highway_name/, "text-color", "#7F8E9B"],
  [/^highway_name/, "text-halo-color", "#1A2531"],
];
/** Kommun (municipality) borders for Stockholm county, drawn under the place names. */
const KOMMUNER = () => new URL("data/kommuner.geojson", document.baseURI).href;
function addKommuner(m: maplibregl.Map) {
  if (m.getSource("kommuner")) return;
  const firstLabel = m.getStyle().layers?.find(l => l.type === "symbol")?.id;
  m.addSource("kommuner", { type: "geojson", data: KOMMUNER() });
  m.addLayer({
    id: "kommun-lines", type: "line", source: "kommuner",
    paint: { "line-color": isDark() ? "#7C8DA0" : "#5D6E7F", "line-width": ["interpolate", ["linear"], ["zoom"], 7, 0.8, 12, 1.6], "line-opacity": 0.7 },
  }, firstLabel);
}

function tuneDark(m: maplibregl.Map) {
  if (!isDark()) return;
  for (const l of m.getStyle().layers ?? []) {
    for (const [re, prop, v] of DARK_PAINT) {
      if (!re.test(l.id)) continue;
      try { m.setPaintProperty(l.id, prop as Parameters<typeof m.setPaintProperty>[1], v); } catch { /* layer lacks this property */ }
    }
  }
}

interface Props {
  hover: string | null; sel: string | null;
  onHover: (id: string | null) => void; onSelect: (id: string | null) => void;
  fitKey: number;
}
export function MapPanel({ hover, sel, onHover, onSelect, fitKey }: Props) {
  const { D, R, list, cmp, home, P, picking, setPicking, setHome, focusId, setFocusId } = useApp();
  const wrap = useRef<HTMLDivElement>(null), cv = useRef<HTMLCanvasElement>(null), tip = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const state = useRef({ R, cmp, home, P, hover, sel, picking });
  state.current = { R, cmp, home, P, hover, sel, picking };
  const draw = useRef<() => void>(() => {});
  const onHoverRef = useRef(onHover); onHoverRef.current = onHover;
  const onSelectRef = useRef(onSelect); onSelectRef.current = onSelect;

  // Create the map once.
  useEffect(() => {
    const MS = D.schools.filter(s => s.lat != null);
    const b = new maplibregl.LngLatBounds();
    MS.forEach(s => b.extend([s.lon!, s.lat!]));
    const m = new maplibregl.Map({
      container: wrap.current!, style: isDark() ? STYLE_DARK : STYLE_LIGHT, bounds: b,
      fitBoundsOptions: { padding: 30 }, attributionControl: { compact: true }, dragRotate: false, pitchWithRotate: false,
      maxBounds: [[15.5, 58.3], [20.6, 60.7]],
    });
    m.touchZoomRotate.disableRotation();
    map.current = m;
    m.on("style.load", () => { tuneDark(m); addKommuner(m); });
    const c = cv.current!;
    const resize = () => { const r = c.getBoundingClientRect(), dpr = devicePixelRatio || 1; c.width = r.width * dpr; c.height = r.height * dpr; };
    draw.current = () => {
      const { R, cmp, home, P, hover, sel } = state.current;
      const ctx = c.getContext("2d"); if (!ctx) return;
      const dpr = devicePixelRatio || 1, W = c.width / dpr, H = c.height / dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
      const C = { line: cssVar("--dot-out"), brand: cssVar("--brand"), surface: cssVar("--surface"), ink: cssVar("--ink") };
      const pt = (lat: number, lon: number) => m.project([lon, lat]);
      const inView = (p: { x: number; y: number }) => p.x > -20 && p.y > -20 && p.x < W + 20 && p.y < H + 20;
      const z = m.getZoom(), rad = Math.min(8, Math.max(4, 2 + (z - 8) * 1.1));
      // Schools outside the answers (missing a must-have or a filter) as small grey dots.
      ctx.fillStyle = C.line;
      for (const s of MS) { const r = R.get(s.id); if (r && r.fit) continue; const p = pt(s.lat!, s.lon!); if (!inView(p)) continue; ctx.beginPath(); ctx.arc(p.x, p.y, 1.9, 0, 7); ctx.fill(); }
      if (home && P.near.m) {
        const p = pt(home.lat, home.lon), q = pt(home.lat + P.near.km / 111.2, home.lon), ry = Math.abs(p.y - q.y);
        ctx.strokeStyle = C.brand; ctx.globalAlpha = 0.6; ctx.setLineDash([5, 5]); ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(p.x, p.y, ry, 0, 7); ctx.stroke(); ctx.setLineDash([]); ctx.globalAlpha = 1;
      }
      const fits = [...R.values()].filter(r => r.fit && r.s.lat != null).sort((a, b) => a.met - b.met);
      for (const r of fits) { const p = pt(r.s.lat!, r.s.lon!); if (inView(p)) glyph(ctx, p.x, p.y, rad, r, C); }
      cmp.forEach((id, i) => { const s = D.byId.get(id); if (s?.lat == null) return; const p = pt(s.lat, s.lon!); ctx.strokeStyle = cssVar(CC[i]); ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(p.x, p.y, rad + 4, 0, 7); ctx.stroke(); });
      for (const id of [hover, sel]) { if (!id) continue; const s = D.byId.get(id); if (s?.lat == null) continue; const p = pt(s.lat, s.lon!); ctx.strokeStyle = C.ink; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.arc(p.x, p.y, rad + (cmp.includes(id) ? 8 : 4), 0, 7); ctx.stroke(); }
      if (home) {
        const p = pt(home.lat, home.lon);
        ctx.fillStyle = C.ink; ctx.beginPath(); ctx.arc(p.x, p.y, 11, 0, 7); ctx.fill();
        ctx.strokeStyle = C.surface; ctx.lineWidth = 2; ctx.beginPath();
        ctx.moveTo(p.x - 5.5, p.y + 0.5); ctx.lineTo(p.x, p.y - 5); ctx.lineTo(p.x + 5.5, p.y + 0.5);
        ctx.moveTo(p.x - 3.5, p.y - 1); ctx.lineTo(p.x - 3.5, p.y + 5); ctx.lineTo(p.x + 3.5, p.y + 5); ctx.lineTo(p.x + 3.5, p.y - 1); ctx.stroke();
      }
      // Name tip for the hovered school.
      const t = tip.current!;
      const hs = hover && D.byId.get(hover);
      if (hs && hs.lat != null && hover !== sel) { const p = pt(hs.lat, hs.lon!); t.textContent = hs.name; t.hidden = false; t.style.left = Math.max(90, Math.min(W - 90, p.x)) + "px"; t.style.top = p.y + "px"; }
      else t.hidden = true;
    };
    const hit = (x: number, y: number) => {
      let best: string | null = null, bd = 14 * 14;
      for (const r of state.current.R.values()) { if (!r.fit || r.s.lat == null) continue; const p = m.project([r.s.lon!, r.s.lat]); const d = (p.x - x) ** 2 + (p.y - y) ** 2; if (d < bd) { bd = d; best = r.s.id; } }
      return best;
    };
    m.on("move", () => draw.current());
    m.on("resize", () => { resize(); draw.current(); });
    m.on("load", () => { resize(); draw.current(); });
    m.on("mousemove", e => { if (state.current.picking) return; const h = hit(e.point.x, e.point.y); onHoverRef.current(h); m.getCanvas().style.cursor = h ? "pointer" : ""; });
    m.on("mouseout", () => onHoverRef.current(null));
    m.on("click", e => {
      if (state.current.picking) { setPicking(false); setHome({ lat: e.lngLat.lat, lon: e.lngLat.lng, label: "your home" }); return; }
      onSelectRef.current(hit(e.point.x, e.point.y));
    });
    const ro = new ResizeObserver(() => { m.resize(); });
    ro.observe(wrap.current!);
    resize();
    // Swap the base map and redraw the school dots in the new colours when the theme changes.
    const theme = () => { m.setStyle(isDark() ? STYLE_DARK : STYLE_LIGHT); draw.current(); };
    addEventListener("themechange", theme);
    return () => { ro.disconnect(); removeEventListener("themechange", theme); m.remove(); map.current = null; };
  }, [D]);

  // Redraw dots when anything they show changes.
  useEffect(() => { draw.current(); }, [R, cmp, home, P, hover, sel]);

  // Fit to the results, or to the home circle.
  const fit = (toHome = false) => {
    const m = map.current; if (!m) return;
    const b = new maplibregl.LngLatBounds();
    if (toHome && home && P.near.m) { const dy = P.near.km / 111.2, dx = dy / Math.cos(home.lat * Math.PI / 180); b.extend([home.lon - dx, home.lat - dy]); b.extend([home.lon + dx, home.lat + dy]); }
    else { list.forEach(r => { if (r.s.lat != null) b.extend([r.s.lon!, r.s.lat]); }); if (home) b.extend([home.lon, home.lat]); }
    if (!b.isEmpty()) m.fitBounds(b, { padding: 40, maxZoom: 15, duration: 600 });
  };
  const lastHome = useRef(home);
  useEffect(() => { if (home && home !== lastHome.current) fit(true); lastHome.current = home; }, [home, P.near.km]);
  useEffect(() => { if (fitKey) fit(); }, [fitKey]);
  useEffect(() => {
    if (!focusId || !map.current) return;
    const s = D.byId.get(focusId); setFocusId(null);
    if (s?.lat != null) { map.current.flyTo({ center: [s.lon!, s.lat], zoom: Math.max(map.current.getZoom(), 13) }); onSelect(s.id); wrap.current?.closest(".panel")?.scrollIntoView({ block: "center" }); }
  }, [focusId]);

  return (
    <div className={"mapwrap" + (picking ? " picking" : "")}>
      <div ref={wrap} style={{ position: "absolute", inset: 0 }} aria-label="Map of matching schools" />
      <canvas id="dots" ref={cv} />
      <div className="mapctl">
        <button aria-label="Zoom in" onClick={() => map.current?.zoomIn()}>+</button>
        <button aria-label="Zoom out" onClick={() => map.current?.zoomOut()}>−</button>
        <button aria-label="Fit to results" onClick={() => fit()}><Ic n="fit" /></button>
      </div>
      {picking && <div className="picknote">Click where you live <button type="button" onClick={() => setPicking(false)}>Cancel</button></div>}
      <div className="maptip" ref={tip} hidden />
    </div>
  );
}

function glyph(c: CanvasRenderingContext2D, x: number, y: number, rad: number, r: Result, C: { brand: string; surface: string }) {
  const f = share(r); c.globalAlpha = r.unk ? 0.5 : 1;
  c.fillStyle = C.surface; c.beginPath(); c.arc(x, y, rad, 0, 7); c.fill();
  if (f >= 1) { c.fillStyle = C.brand; c.beginPath(); c.arc(x, y, rad, 0, 7); c.fill(); }
  else if (f > 0) { c.fillStyle = C.brand; c.beginPath(); c.moveTo(x, y); c.arc(x, y, rad, -Math.PI / 2, -Math.PI / 2 + f * Math.PI * 2); c.closePath(); c.fill(); }
  c.strokeStyle = C.brand; c.lineWidth = 1.6; c.beginPath(); c.arc(x, y, rad, 0, 7); c.stroke(); c.globalAlpha = 1;
}
