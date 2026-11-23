import { useEffect, useState } from "react";
import { col } from "./lib/constants";
import { loadData } from "./lib/db";
import { AppProvider, useApp, useRoute } from "./lib/store";
import type { Data } from "./lib/types";
import { Ic, IconSprite } from "./components/Icons";
import { isDark, setTheme } from "./lib/theme";
import { FindPage } from "./pages/FindPage";
import { SchoolPage } from "./pages/SchoolPage";
import { ComparePage } from "./pages/ComparePage";
import { PipelinePage } from "./pages/PipelinePage";

export default function App() {
  const [D, setD] = useState<Data | null>(null);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => { loadData().then(setD).catch(e => { console.error(e); setErr(String(e?.message || e)); }); }, []);
  return (
    <>
      <IconSprite />
      {D ? <AppProvider D={D}><Shell /></AppProvider> : (
        <>
          <TopBar n={0} view="find" />
          <div className="loading">{err ? <div className="empty"><h3>The school data did not load</h3><p>{err}</p><p>Run <code>dbt build</code> so the Parquet files exist in web/public/data, then reload.</p></div>
            : <div><div className="spin" />Starting DuckDB in your browser and reading the school data…</div>}</div>
        </>
      )}
    </>
  );
}

function ThemeToggle() {
  const [dark, setDark] = useState(isDark);
  useEffect(() => { const f = () => setDark(isDark()); addEventListener("themechange", f); return () => removeEventListener("themechange", f); }, []);
  return (
    <button className="themebtn" type="button" onClick={() => setTheme(dark ? "light" : "dark")}
      aria-label={dark ? "Switch to light mode" : "Switch to dark mode"} title={dark ? "Switch to light mode" : "Switch to dark mode"}>
      <Ic n={dark ? "sun" : "moon"} />
    </button>
  );
}

function TopBar({ n, view }: { n: number; view: string }) {
  return (
    <header className="top"><div className="inner">
      <a className="brand" href="#find" aria-label="Stockholm School Finder, home">
        <svg width="34" height="34" viewBox="0 0 34 34" aria-hidden="true"><rect width="34" height="34" rx="9" fill="var(--brand)" /><path d="M7 21h20" stroke="var(--brand-ink)" strokeWidth="2.6" strokeLinecap="round" /><circle cx="9" cy="21" r="3.2" fill="var(--brand)" stroke="var(--brand-ink)" strokeWidth="2.2" /><circle cx="17" cy="21" r="2.2" fill="var(--brand-ink)" /><circle cx="25" cy="21" r="3.2" fill="var(--sun)" stroke="var(--brand-ink)" strokeWidth="2.2" /><path d="M12 13l5-3 5 3" stroke="var(--brand-ink)" strokeWidth="2.2" fill="none" strokeLinecap="round" strokeLinejoin="round" /></svg>
        <span>Stockholm School Finder<small>Compulsory schools, years F–9</small></span>
      </a>
      <nav className="nav" aria-label="Main">
        <a href="#find" aria-current={view === "find" || view === "school" ? "page" : undefined}><Ic n="search" /><span className="lbl-long">Find schools</span></a>
        <a href="#compare" aria-current={view === "compare" ? "page" : undefined} aria-label="Compare schools"><Ic n="cols" /><span className="lbl-mid">Compare</span><span className="count-badge" data-n={n}>{n}</span></a>
        <a href="#pipeline" aria-current={view === "pipeline" ? "page" : undefined} aria-label="Data pipeline"><Ic n="db" /><span className="lbl-mid">Data</span></a>
      </nav>
      <ThemeToggle />
    </div></header>
  );
}

function Shell() {
  const { D, cmp, toastMsg } = useApp();
  const r = useRoute();
  const school = r.view === "school" ? D.byId.get(r.id!) : undefined;
  const view = r.view === "school" && !school ? "find" : r.view;
  useEffect(() => {
    document.title = view === "school" && school ? `${school.name} · Stockholm School Finder` : view === "compare" ? "Compare · Stockholm School Finder" : view === "pipeline" ? "Data pipeline · Stockholm School Finder" : "Stockholm School Finder";
    if (view !== "find") scrollTo(0, 0);
  }, [view, school]);
  return (
    <>
      <TopBar n={cmp.length} view={view} />
      <main>
        {view === "find" && <FindPage />}
        {view === "school" && school && <SchoolPage s={school} />}
        {view === "compare" && <ComparePage />}
        {view === "pipeline" && <PipelinePage />}
      </main>
      {cmp.length > 0 && view !== "compare" && (
        <div id="tray"><div className="dots">{cmp.map((id, i) => <i key={id} style={{ background: col(i) }} />)}</div>
          <span className="t">{cmp.length === 1 ? "1 school picked. Add another" : `${cmp.length} schools picked`}</span>
          <a className="btn sm" href="#compare">Compare now</a></div>
      )}
      {toastMsg && <div id="toast" role="status">{toastMsg}</div>}
    </>
  );
}
