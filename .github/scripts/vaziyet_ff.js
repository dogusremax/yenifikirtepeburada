// Firefox: WebGL kapalıyken (yedek CSS 3D görünüm) ve açıkken 2. sahneyi Retina boyutunda çeker.
const pw = require('playwright');
const URL = process.argv[2], OUT = process.argv[3];
(async () => {
  for (const [ad, prefs] of [['webgl-acik', {}], ['webgl-kapali', { 'webgl.disabled': true }]]) {
    const b = await pw.firefox.launch({ headless: false, firefoxUserPrefs: prefs });
    const c = await b.newContext({ viewport: { width: 1440, height: 760 }, deviceScaleFactor: 2 });
    const p = await c.newPage(); const logs = []; p.on('console', m => logs.push(m.text())); p.on('pageerror', e => logs.push('ERR ' + e.message));
    await p.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 }); await p.waitForTimeout(10000);
    await p.evaluate(() => { const r = document.querySelector('.cerez button.red'); if (r) r.click(); });
    await p.click('.sc[data-k="2"]'); await p.waitForTimeout(9000);
    console.log(ad, JSON.stringify(await p.evaluate(() => ({ world: !!document.querySelector('.pnlm-world'), ua: navigator.userAgent, webkitApp: 'WebkitAppearance' in document.documentElement.style }))), logs.slice(0, 8).join(' | '));
    await p.screenshot({ path: `${OUT}/ff-${ad}.png` });
    await b.close();
  }
})().catch(e => { console.log('COKTU', e); process.exit(1); });
