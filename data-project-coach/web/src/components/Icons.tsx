export function Ic({ n, className = "" }: { n: string; className?: string }) {
  return <svg className={"ic " + className} aria-hidden="true"><use href={"#i-" + n} /></svg>;
}

export function IconSprite() {
  return (
    <svg width="0" height="0" style={{ position: "absolute" }} aria-hidden="true">
      <symbol id="i-search" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" /><path d="M20 20l-4-4" /></symbol>
      <symbol id="i-cols" viewBox="0 0 24 24"><rect x="3" y="4" width="7" height="16" rx="1.5" /><rect x="14" y="4" width="7" height="16" rx="1.5" /></symbol>
      <symbol id="i-home" viewBox="0 0 24 24"><path d="M3.5 11L12 4l8.5 7" /><path d="M6 9.5V20h12V9.5" /><path d="M10 20v-5h4v5" /></symbol>
      <symbol id="i-map" viewBox="0 0 24 24"><path d="M9 4L3 6.5v13L9 17l6 2.5 6-2.5v-13L15 6.5z" /><path d="M9 4v13M15 6.5v13" /></symbol>
      <symbol id="i-scatter" viewBox="0 0 24 24"><path d="M3.5 3.5v17h17" /><circle cx="9" cy="14" r="1.6" /><circle cx="13" cy="10" r="1.6" /><circle cx="17.5" cy="6.5" r="1.6" /><circle cx="16" cy="13" r="1.6" /></symbol>
      <symbol id="i-fit" viewBox="0 0 24 24"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" /></symbol>
      <symbol id="i-cap" viewBox="0 0 24 24"><path d="M2 9.5L12 5l10 4.5L12 14z" /><path d="M6 11.5v4.5c3.5 2.3 8.5 2.3 12 0v-4.5" /></symbol>
      <symbol id="i-chart" viewBox="0 0 24 24"><path d="M4 20V11M10 20V5M16 20v-6M2.5 20h19" /></symbol>
      <symbol id="i-chat" viewBox="0 0 24 24"><path d="M4 5h16v11H10l-6 4z" /><path d="M8.5 10.5h.01M12 10.5h.01M15.5 10.5h.01" /></symbol>
      <symbol id="i-leaf" viewBox="0 0 24 24"><path d="M5 19C5 10 11 5 20 5c0 9-5.5 14.5-14 14.5" /><path d="M5 19.5l8-8" /></symbol>
      <symbol id="i-pin" viewBox="0 0 24 24"><path d="M12 21s7-6.2 7-11.5a7 7 0 10-14 0C5 14.8 12 21 12 21z" /><circle cx="12" cy="9.5" r="2.5" /></symbol>
      <symbol id="i-star" viewBox="0 0 24 24"><path d="M12 3.5l2.5 5.3 5.8.7-4.3 4 1.1 5.8L12 16.4l-5.1 2.9 1.1-5.8-4.3-4 5.8-.7z" /></symbol>
      <symbol id="i-check" viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" /></symbol>
      <symbol id="i-x" viewBox="0 0 24 24"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" /></symbol>
      <symbol id="i-q" viewBox="0 0 24 24"><path d="M9.5 9a2.6 2.6 0 015 1c0 1.8-2.5 2.2-2.5 4M12 17.5h.01" /></symbol>
      <symbol id="i-back" viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7" /></symbol>
      <symbol id="i-ext" viewBox="0 0 24 24"><path d="M14 4h6v6M20 4l-9 9M18 14v6H4V6h6" /></symbol>
      <symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" /></symbol>
      <symbol id="i-db" viewBox="0 0 24 24"><ellipse cx="12" cy="5.5" rx="7.5" ry="2.8" /><path d="M4.5 5.5v13c0 1.5 3.4 2.8 7.5 2.8s7.5-1.3 7.5-2.8v-13" /><path d="M4.5 12c0 1.5 3.4 2.8 7.5 2.8s7.5-1.3 7.5-2.8" /></symbol>
      <symbol id="i-sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4" /><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6" /></symbol>
      <symbol id="i-moon" viewBox="0 0 24 24"><path d="M20 14.5A8 8 0 019.5 4a8 8 0 1010.5 10.5z" /></symbol>
      <symbol id="i-code" viewBox="0 0 24 24"><path d="M8.5 7L3.5 12l5 5M15.5 7l5 5-5 5" /></symbol>
    </svg>
  );
}
