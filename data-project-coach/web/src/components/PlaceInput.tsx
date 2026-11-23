import { useMemo, useState } from "react";
import { fold } from "../lib/format";
import { useApp } from "../lib/store";
import type { School } from "../lib/types";
import { Ic } from "./Icons";

interface Place { label: string; type: string; lat: number; lon: number; n: number; f: string; rank: number }

/** Places are built from the school register: municipalities, areas and streets, each at the mean position of its schools. */
function buildPlaces(S: School[]): Place[] {
  const agg = new Map<string, { label: string; type: string; lat: number; lon: number; n: number }>();
  const add = (key: string, label: string, type: string, s: School) => {
    let a = agg.get(key); if (!a) { a = { label, type, lat: 0, lon: 0, n: 0 }; agg.set(key, a); }
    a.lat += s.lat!; a.lon += s.lon!; a.n++;
  };
  for (const s of S) {
    if (s.lat == null) continue;
    add("m:" + s.mun, s.mun, "Municipality", s);
    const parts = (s.addr || "").split(",").map(x => x.trim()); const town = parts[parts.length - 1];
    if (parts.length > 1 && town && town !== s.mun) add("t:" + town, town, `Area in ${s.mun}`, s);
    const street = parts[0].replace(/\s+\d.*$/, "").trim();
    if (street && parts.length > 1) add("s:" + street + "|" + town, street, `Street, ${town}`, s);
  }
  return [...agg.values()].map(a => ({ ...a, lat: a.lat / a.n, lon: a.lon / a.n, f: fold(a.label), rank: a.type === "Municipality" ? 1 : a.type.startsWith("Area") ? 0 : 2 }));
}
function findPlaces(P: Place[], q: string) {
  q = fold(q).trim(); if (q.length < 2) return [];
  const sc = (p: Place) => (p.f.startsWith(q) ? 0 : p.f.split(/[\s-]/).some(w => w.startsWith(q)) ? 1 : p.f.includes(q) ? 2 : 9);
  return P.map(p => ({ p, s: sc(p) })).filter(x => x.s < 9)
    .sort((a, b) => a.s - b.s || a.p.rank - b.p.rank || b.p.n - a.p.n || a.p.label.localeCompare(b.p.label, "sv"))
    .slice(0, 8).map(x => x.p);
}

export function PlaceInput({ id }: { id: string }) {
  const { D, home, setHome, toast, guided } = useApp();
  const places = useMemo(() => buildPlaces(D.schools), [D]);
  const [text, setText] = useState<string | null>(null);
  const [idx, setIdx] = useState(-1);
  const [open, setOpen] = useState(false);
  const items = text != null ? findPlaces(places, text) : [];
  const choose = (p: Place) => { setText(null); setOpen(false); setHome({ lat: p.lat, lon: p.lon, label: p.label }); if (guided) toast(`Showing schools near ${p.label}`); };
  return (
    <div className={"placewrap" + (home ? " set" : "")}>
      <Ic n="home" />
      <input className="txt" id={id} type="text" role="combobox" aria-autocomplete="list" aria-expanded={open && items.length > 0}
        aria-controls={id + "-list"} aria-label="Where you live" placeholder="e.g. Vällingby, Täby or Kirunagatan" autoComplete="off"
        value={text ?? (home ? home.label : "")}
        onChange={e => { setText(e.target.value); setIdx(0); setOpen(true); }}
        onFocus={() => { if (text == null && home) setText(home.label); }}
        onBlur={() => setTimeout(() => { setOpen(false); setText(null); }, 150)}
        onKeyDown={e => {
          if (!open) return;
          if (e.key === "ArrowDown") { setIdx(i => Math.min(items.length - 1, i + 1)); e.preventDefault(); }
          else if (e.key === "ArrowUp") { setIdx(i => Math.max(0, i - 1)); e.preventDefault(); }
          else if (e.key === "Enter" && idx >= 0 && items[idx]) { choose(items[idx]); (e.target as HTMLInputElement).blur(); e.preventDefault(); }
          else if (e.key === "Escape") setOpen(false);
        }} />
      {home && <button className="clr" type="button" aria-label="Clear where you live" onClick={() => { setHome(null); setText(null); }}><Ic n="x" /></button>}
      {open && text != null && text.trim().length >= 2 && (
        <ul className="plist" id={id + "-list"} role="listbox">
          {items.length ? items.map((p, i) => (
            <li key={p.label + p.type} role="option" aria-selected={i === idx} onPointerDown={e => { e.preventDefault(); choose(p); }}>
              {p.label}<span>{p.type}</span>
            </li>
          )) : <li className="none">No match. Try a nearby town, or click your home on the map.</li>}
        </ul>
      )}
    </div>
  );
}
