import { useEffect, useRef, useState } from "react";
import { APD, APRI } from "../lib/constants";
import { useApp } from "../lib/store";

/** Multi-select dropdown for teaching approaches. Picked ones become chips with their own Nice/Must setting. */
export function ApproachDropdown() {
  const { P, setP, D } = useApp();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const sel = APRI.filter(a => P[a.k as `ap${number}`].m > 0);
  useEffect(() => {
    if (!open) return;
    const f = (e: PointerEvent) => { if (!ref.current?.contains(e.target as Node)) setOpen(false); };
    const k = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("pointerdown", f); document.addEventListener("keydown", k);
    return () => { document.removeEventListener("pointerdown", f); document.removeEventListener("keydown", k); };
  }, [open]);
  return (
    <div className="apdd" ref={ref}>
      <button className="apbtn" type="button" aria-haspopup="listbox" aria-expanded={open} onClick={() => setOpen(o => !o)}>
        <span className={"lb" + (sel.length ? "" : " ph")}>{sel.length ? sel.map(a => a.short).join(", ") : "No preference"}</span>
        {sel.length > 1 && <span className="ct">{sel.length}</span>}
      </button>
      {open && (
        <div className="appanel" role="listbox" aria-multiselectable="true">
          {APRI.map(a => {
            const on = P[a.k as `ap${number}`].m > 0;
            return (
              <div key={a.k} className={"apopt" + (on ? " on" : "")} role="option" aria-selected={on}
                onClick={() => setP(p => { const x = p[a.k as `ap${number}`]; x.m = x.m ? 0 : 1; return p; })}>
                <input type="checkbox" tabIndex={-1} checked={on} readOnly />
                <b>{a.short}</b><span className="n">{D.approachCounts[a.cat!] || 0} schools</span>
                <small>{APD[a.cat!]}</small>
              </div>
            );
          })}
          <div className="apfoot">
            <button className="linkbtn" type="button" onClick={() => setP(p => { for (const a of APRI) p[a.k as `ap${number}`].m = 0; return p; })}>No preference</button>
            <button className="btn primary sm" type="button" onClick={() => setOpen(false)}>Done</button>
          </div>
        </div>
      )}
    </div>
  );
}
