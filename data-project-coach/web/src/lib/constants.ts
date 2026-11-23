import type { Prefs } from "./types";

export const YL = ["F", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
export const CC = ["--c1", "--c2", "--c3", "--c4"];
export const col = (i: number) => `var(${CC[i]})`;
export const MAXCMP = 4;

/** The seven codebook categories, in the order parents see them. */
export const CATS: [string, string, string][] = [
  ["Arts and creative learning", "Arts and creative", "Music, dance, theatre or art as a profile"],
  ["Outdoor, nature, or place-based learning", "Outdoor learning", "Regular teaching outdoors, in nature or the local area"],
  ["Alternative pedagogy", "Alternative pedagogy", "Montessori, Waldorf, Reggio Emilia and similar"],
  ["Project- or inquiry-based learning", "Projects and inquiry", "Learning through projects and themes across subjects"],
  ["Language, international, or intercultural profile", "Languages and international", "Bilingual, international or extra language focus"],
  ["Support, inclusion, or wellbeing emphasis", "Support and wellbeing", "Small groups, inclusion, calm and wellbeing as a stated focus"],
  ["Other stated profile", "Other profile", "Other profiles, such as sports, maths or science"],
];
export const SHORT: Record<string, string> = Object.fromEntries(CATS.map(c => [c[0], c[1]]));
export const APD: Record<string, string> = Object.fromEntries(CATS.map(c => [c[0], c[2]]));

export type FeatureKey = "teach" | "res" | "happy" | "green" | "near";
export interface PriDef { k: string; ic: string; short: string; cat?: string }
export const PRI: PriDef[] = [
  { k: "teach", ic: "cap", short: "Teachers" },
  { k: "res", ic: "chart", short: "Results" },
  { k: "happy", ic: "chat", short: "Parents" },
  { k: "green", ic: "leaf", short: "Green" },
  { k: "near", ic: "pin", short: "Near" },
];
export const APRI: PriDef[] = CATS.map(([c, l], i) => ({ k: "ap" + i, cat: c, ic: "star", short: l }));
export const ALLP = [...PRI, ...APRI];

export const DEFAULT_P = (): Prefs => ({
  teach: { m: 1, min: 80 }, res: { m: 1, yr: "auto" }, happy: { m: 1, min: 80 },
  green: { m: 0, lvl: "typical" }, near: { m: 0, km: 3 },
  ...Object.fromEntries(CATS.map((_, i) => ["ap" + i, { m: 0 }])),
} as Prefs);

export const MODE = ["Don't mind", "Nice to have", "Must have"];
export const SVT: [("sat" | "safe" | "sup" | "insp" | "calm"), string][] = [
  ["sat", "Happy with the school overall"], ["safe", "Feels safe at school"], ["sup", "Gets the help they need"],
  ["insp", "Teachers make lessons interesting"], ["calm", "Calm in lessons"],
];
export const SVWHO = { parents: "Parents", ak5: "Pupils, year 5", ak8: "Pupils, year 8" } as const;
