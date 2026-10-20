// Vaziyet planı (vaziyet-plani.html) görüntü testi.
// Safari/Chrome'da, Retina (2x) ekran ve telefon boyutunda sayfayı açar; gündüz/gece ve sahne geçişlerinden sonra
// 360° görüntünün ekrana tam oturduğunu (2 kat büyüyüp kaymadığını) denetler. Hatayı bilerek tetikleyip
// sayfanın kendini düzelttiğini de dener. Kullanım: node vaziyet_test.js [adres] [chromium,webkit]
const pw = require('playwright');
const URL = process.argv[2] || 'https://yenifikirtepeburada.com/vaziyet-plani.html';
const BROWSERS = (process.argv[3] || 'chromium,webkit').split(',');
const SHOTS = process.env.SHOTS || '';
const sleep = ms => new Promise(r => setTimeout(r, ms));
let fail = 0;
const bad = (m) => { fail++; console.log('  HATA: ' + m); };
const ok = (m) => console.log('  tamam: ' + m);

// pannellum.viewer örneğini yakala (test için window.__v)
const HOOK = () => { let pv; Object.defineProperty(window, 'pannellum', { configurable: true,
  set(x) { pv = x; const o = x.viewer; x.viewer = function () { const r = o.apply(this, arguments); window.__v = r; return r; }; },
  get() { return pv; } }); };

// tuval ekranla ve WebGL görüş alanı tuvalle aynı mı
const STATE = () => { const v = window.__v; if (!v) return { err: 'viewer yok' };
  const r = v.getRenderer(); if (!r) return { err: 'renderer yok' }; const c = r.getCanvas(), d = window.devicePixelRatio || 1;
  const g = c.getContext('webgl') || c.getContext('experimental-webgl'); if (!g) return { err: 'webgl yok' };
  const q = g.getParameter(g.VIEWPORT);
  return { cw: c.width, ch: c.height, kw: c.clientWidth, kh: c.clientHeight, d, vp: [...q], bw: g.drawingBufferWidth, bh: g.drawingBufferHeight,
    ff: /Firefox\//.test(navigator.userAgent) && !/Mobile|Android/.test(navigator.userAgent), d0: window.__dpr0 || 1, pins: document.querySelectorAll('.pin').length, duz: window.__vpDuzeltme || 0 }; };

function check(s, label) {
  if (s.err) return bad(label + ': ' + s.err);
  const tuval = Math.abs(s.cw - s.kw * s.d) <= 2 && Math.abs(s.ch - s.kh * s.d) <= 2;
  if (s.ff && s.d0 > 1 && s.cw > s.kw + 2) bad(label + ': Firefox tuvali 1x değil (' + s.cw + ' / ' + s.kw + ')');
  const vp = s.vp[0] === 0 && s.vp[1] === 0 && s.vp[2] === s.bw && s.vp[3] === s.bh;
  if (tuval && vp) ok(label); else bad(label + ' ' + JSON.stringify(s));
}

(async () => {
  for (const name of BROWSERS) {
    const b = await pw[name].launch();
    for (const [dev, opt] of [['masaüstü 2x', { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 }],
                              ['telefon', name === 'webkit' ? pw.devices['iPhone 13'] : { ...pw.devices['iPhone 13'], defaultBrowserType: undefined }]]) {
      console.log(`[${name} · ${dev}]`);
      const o = { ...opt }; delete o.defaultBrowserType; if (name === 'firefox') delete o.isMobile;
      const c = await b.newContext(o); const p = await c.newPage(); const errs = [];
      p.on('pageerror', e => errs.push(e.message));
      await p.addInitScript(HOOK);
      await p.goto(URL + (URL.includes('?') ? '&' : '?') + 'test=' + Date.now(), { waitUntil: 'domcontentloaded', timeout: 60000 });
      await sleep(9000);
      await p.evaluate(() => { const r = document.querySelector('.cerez button.red'); if (r) r.click(); });
      let s = await p.evaluate(STATE); check(s, 'açılış');
      if (!s.err && s.pins < 10) bad('etap numaraları eksik: ' + s.pins);
      if (!s.err && s.duz) bad('normal açılışta düzeltme gerekti (' + s.duz + ')');
      for (const [sel, label, w] of [['#tgl', 'gece', 6000], ['#tgl', 'gündüz', 6000], ['.sc[data-k="3"]', 'sahne 3', 6000], ['.sc[data-k="7"]', 'tepeden', 6000]]) {
        await p.click(sel); await sleep(w); check(await p.evaluate(STATE), label + ' sonrası');
      }
      // başka pencereye geçip dönme
      await p.evaluate(() => { dispatchEvent(new Event('blur')); });
      await sleep(800);
      await p.evaluate(() => { window.__k0 = window.__vzKurulum || 0; dispatchEvent(new Event('focus')); });
      await sleep(4000); check(await p.evaluate(STATE), 'pencere değişip dönünce');
      if (!(await p.evaluate(() => (window.__vzKurulum || 0) > window.__k0))) bad('pencereye dönünce çizim belleği yeniden kurulmadı');
      else ok('pencereye dönünce çizim belleği yeniden kuruldu');
      const pz = await p.evaluate(() => document.querySelectorAll('.pin').length); if (pz < 5) bad('dönüşten sonra etap numaraları eksik: ' + pz);
      if (SHOTS) await p.screenshot({ path: `${SHOTS}/${name}-${dev.replace(/\W+/g, '')}.png` });
      // hatayı taklit et: görüş alanı 2 kat; sonraki çizimde düzelmeli
      await p.evaluate(() => { const g = __v.getRenderer().getCanvas().getContext('webgl'); g.viewport(0, 0, g.drawingBufferWidth * 2, g.drawingBufferHeight * 2); __v.setYaw(__v.getYaw() + 0.5, false); });
      await sleep(1500); check(await p.evaluate(STATE), 'bozulup çizilince kendini düzeltti');
      // boştayken bozulursa bekçi düzeltmeli
      await p.evaluate(() => { const g = __v.getRenderer().getCanvas().getContext('webgl'); g.viewport(0, 0, g.drawingBufferWidth * 2, g.drawingBufferHeight * 2); });
      await sleep(3500); check(await p.evaluate(STATE), 'boştayken bozulunca bekçi düzeltti');
      // ekran kartı bağlamı düşerse sayfa aynı bakışla kendini yeniden açmalı
      await p.evaluate(() => { const e = __v.getRenderer().getCanvas().getContext('webgl').getExtension('WEBGL_lose_context'); if (e) { e.loseContext(); setTimeout(() => e.restoreContext(), 800); } });
      await sleep(10000); check(await p.evaluate(STATE), 'ekran kartı bağlamı düşünce toparlandı');
      if (errs.length) bad('sayfa hatası: ' + errs.join(' | ')); else ok('sayfa hatası yok');
      await c.close();
    }
    await b.close();
  }
  console.log(fail ? `\n${fail} HATA` : '\nTÜM TESTLER GEÇTİ');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.log('TEST ÇÖKTÜ', e); process.exit(2); });
