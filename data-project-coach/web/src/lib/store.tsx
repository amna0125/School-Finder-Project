/** App state shared by every page: the parent's answers, home, compare list and the scored results. */
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { DEFAULT_P, MAXCMP } from "./constants";
import { store } from "./format";
import { runScore } from "./scoring";
import type { Data, Filters, Home, Prefs, Result, Summary } from "./types";

interface Ctx {
  D: Data;
  P: Prefs; setP: (f: (p: Prefs) => Prefs) => void;
  F: Filters; setF: (f: (p: Filters) => Filters) => void;
  home: Home | null; setHome: (h: Home | null) => void;
  cmp: string[]; toggleCmp: (id: string) => void; clearCmp: () => void;
  guided: boolean; setGuided: (b: boolean) => void;
  chartYr: "6" | "9"; setChartYr: (y: "6" | "9") => void;
  R: Map<string, Result>; list: Result[]; sum: Summary; sql: string; scoring: boolean;
  toast: (t: string) => void; toastMsg: string | null;
  picking: boolean; setPicking: (b: boolean) => void;
  focusId: string | null; setFocusId: (id: string | null) => void;
}
const C = createContext<Ctx | null>(null);
export const useApp = () => useContext(C)!;

export function AppProvider({ D, children }: { D: Data; children: ReactNode }) {
  const [P, setPState] = useState<Prefs>(() => ({ ...DEFAULT_P(), ...store.get("P", {}) }));
  const [F, setFState] = useState<Filters>(() => ({ mun: "", start: "", org: "", stay9: false, fritids: false, ...store.get("F", {}), q: "" }));
  const [home, setHomeState] = useState<Home | null>(() => store.get("home", null));
  const [cmp, setCmp] = useState<string[]>(() => store.get<string[]>("cmp", []).filter(id => D.byId.has(id)).slice(0, MAXCMP));
  const [guided, setGuidedState] = useState<boolean>(() => store.get("guided", false));
  const [chartYr, setChartYrState] = useState<"6" | "9">(() => store.get("chartYr", "6"));
  const [res, setRes] = useState<{ R: Map<string, Result>; list: Result[]; sum: Summary; sql: string }>({ R: new Map(), list: [], sum: { mustOut: 0, scope: 0, all: 0, most: 0, nearScope: false, ms: 0 }, sql: "" });
  const [scoring, setScoring] = useState(true);
  const [toastMsg, setToast] = useState<string | null>(null);
  const [picking, setPicking] = useState(false);
  const [focusId, setFocusId] = useState<string | null>(null);
  const tt = useRef<number>(0);

  const toast = useCallback((t: string) => { setToast(t); clearTimeout(tt.current); tt.current = window.setTimeout(() => setToast(null), 2600); }, []);
  const setP = useCallback((f: (p: Prefs) => Prefs) => setPState(p => f(structuredClone(p))), []);
  const setF = useCallback((f: (p: Filters) => Filters) => setFState(p => f({ ...p })), []);
  const setHome = useCallback((h: Home | null) => {
    setHomeState(h);
    setPState(p => {
      const n = structuredClone(p);
      if (h && !n.near.m) { n.near.m = 2; n.near.km = 3; }
      if (!h && n.near.m) n.near.m = 0;
      return n;
    });
  }, []);
  const toggleCmp = useCallback((id: string) => {
    setCmp(c => {
      const s = D.byId.get(id)!;
      if (c.includes(id)) { toast(`Removed ${s.name} from compare`); return c.filter(x => x !== id); }
      if (c.length >= MAXCMP) { toast(`You can compare up to ${MAXCMP} schools. Remove one to add another.`); return c; }
      const n = [...c, id];
      toast(n.length === 1 ? "Added. Pick another school to compare side by side." : `Added. ${n.length} schools ready to compare.`);
      return n;
    });
  }, [D, toast]);

  // Persist per-viewer conveniences.
  useEffect(() => { store.set("P", P); store.set("F", { ...F, q: "" }); store.set("home", home); store.set("cmp", cmp); store.set("guided", guided); store.set("chartYr", chartYr); }, [P, F, home, cmp, guided, chartYr]);

  // Re-score in DuckDB whenever an answer changes. Name search is debounced.
  useEffect(() => {
    let live = true;
    setScoring(true);
    const t = window.setTimeout(() => {
      runScore(D, P, F, home).then(r => { if (live) { setRes(r); setScoring(false); } }).catch(e => { console.error(e); setScoring(false); });
    }, F.q ? 120 : 0);
    return () => { live = false; clearTimeout(t); };
  }, [D, P, F, home]);

  const v = useMemo<Ctx>(() => ({
    D, P, setP, F, setF, home, setHome, cmp, toggleCmp, clearCmp: () => setCmp([]),
    guided, setGuided: setGuidedState, chartYr, setChartYr: setChartYrState,
    ...res, scoring, toast, toastMsg, picking, setPicking, focusId, setFocusId,
  }), [D, P, setP, F, setF, home, setHome, cmp, toggleCmp, guided, chartYr, res, scoring, toast, toastMsg, picking, focusId]);
  return <C.Provider value={v}>{children}</C.Provider>;
}

/** Hash routing: #find, #school-ID, #compare, #pipeline. */
export function useRoute() {
  const [h, setH] = useState(() => location.hash.slice(1));
  useEffect(() => { const f = () => setH(location.hash.slice(1)); addEventListener("hashchange", f); return () => removeEventListener("hashchange", f); }, []);
  if (h.startsWith("school-")) return { view: "school" as const, id: h.slice(7) };
  if (h === "compare") return { view: "compare" as const };
  if (h === "pipeline") return { view: "pipeline" as const };
  return { view: "find" as const };
}
