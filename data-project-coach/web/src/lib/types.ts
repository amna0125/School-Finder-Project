export type Status = "ok" | "rounded" | "few" | "none";
export interface Metric { v: number | null; p: string | null; st: Status }
export interface Approach { cat: string; sub: string | null; lvl: "E" | "S"; q: string; url: string | null; date: string | null }
export interface Fact { v: string; q?: string | null; date?: string | null }
export interface SurveyTheme { pos: number; mid: number; neg: number; n: number | null }
export type SurveyGroup = Partial<Record<"sat" | "safe" | "sup" | "insp" | "calm", SurveyTheme>>;
export interface School {
  id: string; name: string; mun: string; addr: string;
  lat: number | null; lon: number | null;
  org: "municipal" | "independent"; orgName: string | null;
  grades: string; g: number[]; web: string | null; label: string | null;
  approach: Approach[];
  m: Record<string, Metric>;
  set: { green?: string; greenPct?: number } & Record<string, Fact | string | number | undefined>;
  h: Record<string, Record<string, number>>;
  sv?: Partial<Record<"parents" | "ak5" | "ak8", SurveyGroup>>;
}
export interface Data {
  schools: School[];
  byId: Map<string, School>;
  county: Record<string, number>;
  periods: Record<string, string>;
  svMedian: number;
  approachCounts: Record<string, number>;
  generated: string;
}
export type Mode = 0 | 1 | 2;
export interface Prefs {
  teach: { m: Mode; min: number };
  res: { m: Mode; yr: "auto" | "6" | "9" };
  happy: { m: Mode; min: number };
  green: { m: Mode; lvl: "typical" | "greener" };
  near: { m: Mode; km: number };
  [ap: `ap${number}`]: { m: Mode };
}
export interface Filters { q: string; mun: string; start: string; org: string; stay9: boolean; fritids: boolean }
export interface Home { lat: number; lon: number; label: string }
export type Verdict = "yes" | "no" | "unk";
export interface Result {
  s: School; ev: Record<string, Verdict>; fit: boolean; unk: boolean; met: number; n: number;
  frac: number; q: number; d: number | null; all: boolean;
}
export interface Summary { mustOut: number; scope: number; all: number; most: number; nearScope: boolean; ms: number }
