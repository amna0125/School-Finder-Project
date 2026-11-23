/** Light / dark mode. With no saved choice the site follows the computer's setting. */
import { store } from "./format";

export type Theme = "light" | "dark";
const mq = () => matchMedia("(prefers-color-scheme: dark)");

export const savedTheme = (): Theme | null => store.get<Theme | null>("theme", null);
export const isDark = () => {
  const t = document.documentElement.dataset.theme;
  return t ? t === "dark" : mq().matches;
};

/** Set the theme, remember it, and tell canvases (the map) to redraw. */
export function setTheme(t: Theme) {
  document.documentElement.dataset.theme = t;
  store.set("theme", t);
  dispatchEvent(new Event("themechange"));
}

/** Call once at start-up: apply a saved choice, and pass on system changes when there is none. */
export function initTheme() {
  const t = savedTheme();
  if (t) document.documentElement.dataset.theme = t;
  mq().addEventListener?.("change", () => { if (!savedTheme()) dispatchEvent(new Event("themechange")); });
}
