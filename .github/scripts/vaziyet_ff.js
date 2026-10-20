// Firefox'u ekranlı açıp (Retina taklidi) başka uygulamaya geçip dönme; gerçek ekran görüntüsü + WebGL durumu.
const pw = require('playwright'); const { execSync } = require('child_process');
const URL = process.argv[2], OUT = process.argv[3];
const sh = c => { try { return execSync(c).toString().trim(); } catch (e) { return 'ERR ' + e.message; } };
const ST = () => { const c = document.querySelector('.pnlm-render-container canvas'); if (!c) return { err: 'canvas yok' };
  const g = c.getContext('webgl') || c.getContext('experimental-webgl');
  return { cw: c.width, ch: c.height, kw: c.clientWidth, kh: c.clientHeight, dpr: devicePixelRatio, vp: g && [...g.getParameter(g.VIEWPORT)],
    bw: g && g.drawingBufferWidth, bh: g && g.drawingBufferHeight, maxvp: g && [...g.getParameter(g.MAX_VIEWPORT_DIMS)], maxrb: g && g.getParameter(g.MAX_RENDERBUFFER_SIZE),
    lost: g && g.isContextLost(), duz: window.__vpDuzeltme || 0, kur: window.__vzKurulum || 0, focus: document.hasFocus(), hidden: document.hidden }; };
(async () => {
  for (const [w, h] of [[1280, 748], [1728, 1000]]) {
    const b = await pw.firefox.launch({ headless: false });
    const c = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2 });
    const p = await c.newPage(); const logs = [];
    p.on('console', m => logs.push(m.text())); p.on('pageerror', e => logs.push('PAGEERROR ' + e.message));
    await p.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 }); await p.waitForTimeout(10000);
    await p.evaluate(() => { const r = document.querySelector('.cerez button.red'); if (r) r.click(); });
    await p.click('.sc[data-k="2"]'); await p.waitForTimeout(8000);
    const tag = `${w}`; console.log(tag, 'acilis', JSON.stringify(await p.evaluate(ST)));
    sh(`screencapture -x ${OUT}/ff${tag}-0.png`);
    for (let i = 0; i < 3; i++) {
      sh(`osascript -e 'tell application "Finder" to activate' -e 'tell application "Finder" to make new Finder window'`);
      await p.waitForTimeout(i === 2 ? 20000 : 4000);
      console.log(tag, 'arkada' + i, JSON.stringify(await p.evaluate(ST)));
      sh(`screencapture -x ${OUT}/ff${tag}-arka${i}.png`);
      await p.bringToFront(); sh(`osascript -e 'tell application "System Events" to set frontmost of (first process whose name contains "irefox" or name contains "ightly" or name contains "uggler") to true'`);
      await p.mouse.click(w / 2, h / 2);   // pencereye tıklayarak dön
      await p.waitForTimeout(4000);
      console.log(tag, 'donus' + i, JSON.stringify(await p.evaluate(ST)));
      sh(`screencapture -x ${OUT}/ff${tag}-donus${i}.png`);
    }
    console.log(tag, 'LOG', logs.filter(l => !/collect|gtag/.test(l)).slice(0, 30).join(' || '));
    await b.close();
  }
  console.log(sh('ps aux | grep -i -E "firefox|nightly|juggler" | head -3'));
})().catch(e => { console.log('COKTU', e); process.exit(1); });
