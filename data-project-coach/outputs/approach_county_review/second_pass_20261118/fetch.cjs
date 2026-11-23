// Second pass 18 Nov 2026: fetch every school's own pages in a real browser (scroll to bottom), robots.txt respected.
// Saves innerText per URL in text/<sha1>.json (resumable). Discovers up to 3 about/profile subpages per school on the same site section.
const { chromium } = require('playwright'); const fs = require('fs'); const crypto = require('crypto');
const plan = JSON.parse(fs.readFileSync('plan.json')); const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36';
const BOT = 'school-review-bot'; const robots = {}; const hostBusy = {}; const hostLast = {};
const h = u => crypto.createHash('sha1').update(u).digest('hex'); const file = u => `text/${h(u)}.json`;
const ABOUT = /(om-?oss|om-?skolan|om-|var-?skola|vår-?skola|profil|pedagog|arbetssatt|arbetssätt|verksamhet|about|var-undervisning|undervisning|inriktning|vision|grundskola)/i;
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function robotsOk(u) {
  const x = new URL(u); const base = x.origin;
  if (!(base in robots)) {
    try { const r = await fetch(base + '/robots.txt', { headers: { 'User-Agent': BOT }, signal: AbortSignal.timeout(15000) }); robots[base] = r.ok ? await r.text() : ''; } catch { robots[base] = ''; }
  }
  let applies = false, dis = [], al = [];
  for (const line of robots[base].split(/\r?\n/)) {
    const [k, ...v] = line.split(':'); const key = (k || '').trim().toLowerCase(); const val = v.join(':').trim();
    if (key === 'user-agent') applies = (val === '*' || BOT.toLowerCase().includes(val.toLowerCase()));
    else if (applies && key === 'disallow' && val) dis.push(val); else if (applies && key === 'allow' && val) al.push(val);
  }
  const path = x.pathname + x.search; const m = p => { const re = new RegExp('^' + p.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\\\$$/, '$')); return re.test(path); };
  const d = dis.filter(m).sort((a, b) => b.length - a.length)[0]; const a = al.filter(m).sort((a, b) => b.length - a.length)[0];
  return !d || (a && a.length >= d.length);
}
async function get(ctx, u) {
  if (fs.existsSync(file(u))) return JSON.parse(fs.readFileSync(file(u)));
  const host = new URL(u).host;
  while (hostBusy[host]) await sleep(200); hostBusy[host] = true;
  const wait = 1500 - (Date.now() - (hostLast[host] || 0)); if (wait > 0) await sleep(wait);
  let rec;
  try {
    if (!(await robotsOk(u))) rec = { url: u, status: 'robots' };
    else {
      const p = await ctx.newPage();
      try {
        const r = await p.goto(u, { waitUntil: 'domcontentloaded', timeout: 40000 }); await p.waitForTimeout(1500);
        for (let i = 0; i < 10; i++) { await p.mouse.wheel(0, 2500); await p.waitForTimeout(250); }
        const text = (await p.evaluate(() => document.body ? document.body.innerText : '')).replace(/\s+/g, ' ');
        const links = await p.$$eval('a[href]', as => as.map(a => [a.innerText.trim().slice(0, 60), a.href]));
        rec = { url: u, final: p.url(), status: r ? r.status() : 0, title: await p.title(), text, links, at: new Date().toISOString() };
      } catch (e) { rec = { url: u, status: 'error', err: String(e).slice(0, 120) }; } finally { await p.close(); }
    }
  } finally { hostLast[host] = Date.now(); hostBusy[host] = false; }
  fs.writeFileSync(file(u), JSON.stringify(rec)); return rec;
}
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ userAgent: UA, locale: 'sv-SE' });
  await ctx.route('**/*.{png,jpg,jpeg,gif,webp,svg,mp4,woff,woff2}', r => r.abort());
  const sids = Object.keys(plan); let i = 0, done = 0; const found = {};
  async function worker() {
    while (i < sids.length) {
      const sid = sids[i++]; const s = plan[sid]; found[sid] = [];
      for (const u of s.urls) {
        const rec = await get(ctx, u);
        // discover about/profile subpages under the same section (same host, path starts with this page's path)
        if (rec.links && rec.status === 200) {
          const base = new URL(rec.final || u); const prefix = base.pathname.replace(/\/[^/]*\.html?$/, '').replace(/\/$/, '');
          const cand = rec.links.map(l => l[1]).filter(x => { try { const y = new URL(x); return y.host === base.host && prefix.length > 1 && y.pathname.startsWith(prefix + '/') && ABOUT.test(y.pathname) && !/\.(pdf|docx?|jpg|png)$/i.test(y.pathname); } catch { return false; } });
          for (const c of [...new Set(cand.map(c => c.split('#')[0]))].filter(c => !s.urls.includes(c)).slice(0, 3)) { if (found[sid].length < 4) { found[sid].push(c); await get(ctx, c); } }
        }
      }
      done++; if (done % 25 === 0) console.log(new Date().toISOString(), 'schools done', done);
    }
  }
  await Promise.all([worker(), worker(), worker(), worker(), worker(), worker()]);
  fs.writeFileSync('discovered.json', JSON.stringify(found, null, 0)); await b.close(); console.log('finished', done);
})();
