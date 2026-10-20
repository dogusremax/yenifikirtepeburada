// Aynı pencere boyutunda Chrome/WebKit/Firefox'ta 5. sahneyi açıp ekran görüntüsü ve pin konumlarını kaydeder.
const pw = require('playwright');
const URL = process.argv[2], OUT = process.argv[3];
(async () => {
  for (const name of ['chromium', 'webkit', 'firefox']) for (const dpr of [1, 2]) {
    const b = await pw[name].launch({ headless: process.env.HEADED ? false : true });
    const c = await b.newContext({ viewport: { width: 1280, height: 748 }, deviceScaleFactor: dpr });
    const p = await c.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 }); await p.waitForTimeout(10000);
    await p.evaluate(() => { const r = document.querySelector('.cerez button.red'); if (r) r.click(); });
    await p.click('.sc[data-k="5"]'); await p.waitForTimeout(9000);
    const info = await p.evaluate(() => {
      const o = {}; document.querySelectorAll('.pnlm-hotspot-base').forEach(h => { const r = h.getBoundingClientRect(); const t = (h.textContent || '').trim().slice(0, 12); o[t] = [Math.round(r.x + r.width / 2), Math.round(r.y + r.height / 2)]; });
      const cv = document.querySelector('.pnlm-render-container canvas'); const g = cv && (cv.getContext('webgl') || cv.getContext('experimental-webgl'));
      return { pins: o, world: !!document.querySelector('.pnlm-world'), cw: cv && cv.width, kw: cv && cv.clientWidth, vp: g && [...g.getParameter(g.VIEWPORT)], bw: g && g.drawingBufferWidth, ua: navigator.userAgent };
    });
    console.log(name, 'dpr' + dpr, JSON.stringify(info), errs.join('|'));
    await p.screenshot({ path: `${OUT}/${name}-dpr${dpr}${process.env.HEADED ? '-ekranli' : ''}.png` });
    await b.close();
  }
})().catch(e => { console.log('COKTU', e); process.exit(1); });
