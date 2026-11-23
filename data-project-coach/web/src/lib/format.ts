export const fmt = (v: number | null | undefined, d = 0) =>
  v == null || !isFinite(v) ? "–" : Number(v).toLocaleString("en-GB", { minimumFractionDigits: d, maximumFractionDigits: d });
export const cap = (s: string | null | undefined) => (s ? s[0].toUpperCase() + s.slice(1) : s ?? "");
export const fold = (s: string | null | undefined) => String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
export const fmtDate = (d: string | null | undefined) => {
  if (!d) return "";
  try { return new Date(d + "T12:00:00").toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" }); } catch { return d; }
};
export function km(a: { lat: number; lon: number } | null, b: { lat: number | null; lon: number | null }) {
  if (!a || b.lat == null || b.lon == null) return null;
  const t = Math.PI / 180, dl = (b.lat - a.lat) * t, dn = (b.lon - a.lon) * t;
  const x = Math.sin(dl / 2) ** 2 + Math.cos(a.lat * t) * Math.cos(b.lat * t) * Math.sin(dn / 2) ** 2;
  return 12742 * Math.asin(Math.sqrt(x));
}
export const store = {
  get<T>(k: string, d: T): T { try { const v = localStorage.getItem("ssf.web." + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
  set(k: string, v: unknown) { try { localStorage.setItem("ssf.web." + k, JSON.stringify(v)); } catch { /* private mode */ } },
};
export const cssVar = (v: string) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
