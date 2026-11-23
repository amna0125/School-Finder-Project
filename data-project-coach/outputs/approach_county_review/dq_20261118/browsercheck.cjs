const { chromium } = require('playwright'); const fs = require('fs');
const d = JSON.parse(fs.readFileSync('quotecheck_retry2.json')).filter(o => o.status3 !== 'present');
const norm = s => s.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ userAgent: 'Mozilla/5.0 (compatible; school-review-bot)' });
  const cache = {}; const out = [];
  for (const o of d) {
    if (!(o.url in cache)) {
      try { const r = await p.goto(o.url, { waitUntil: 'networkidle', timeout: 45000 }); await p.waitForTimeout(1500);
        cache[o.url] = { st: r ? r.status() : 0, title: await p.title(), text: norm(await p.evaluate(() => document.body ? document.body.innerText : '')) };
      } catch (e) { cache[o.url] = { st: 'ERR', title: String(e).slice(0, 60), text: '' }; }
      await p.waitForTimeout(2000);
    }
    const c = cache[o.url]; const q = norm(o.quote); const w = q.split(' '); const gr = []; for (let i = 0; i < Math.max(1, w.length - 4); i++) gr.push(w.slice(i, i + 5).join(' '));
    const ov = gr.filter(g => c.text.includes(g)).length / gr.length;
    out.push({ ...o, http: c.st, btitle: c.title, overlap: ov });
    console.log(`${c.st} ${(ov * 100).toFixed(0)}% | ${o.school_id} ${o.name.slice(0, 28)} | ${c.title.slice(0, 50)}`);
  }
  fs.writeFileSync('browsercheck.json', JSON.stringify(out, null, 1)); await b.close();
})();
