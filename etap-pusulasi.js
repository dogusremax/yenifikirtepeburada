/* Etap Pusulası: her sayfada sağ kenarda sabit sekme. Açılınca 18 etabın bugünkü teslim durumu
   (teslim-takvimi.json'dan, vaziyet planındaki renklerle), teslimi süren etapların ilerlemesi ve
   etap seçince 360° plan / teslim takvimi bağlantıları.
   <script src="etap-pusulasi.js" defer></script> */
(function(){
  if (window.__pusula) return; window.__pusula = 1;
  var me = document.currentScript;
  var BASE = me && me.src ? me.src.replace(/[^\/]*$/, '') : '';
  // [konut, daire tipleri] (vaziyet-plani.html ile aynı)
  var INFO = {2:[457,'1+1 – 4+1'],3:[1814,'1+1 – 4+1'],4:[194,'2+1 – 5+1'],5:[588,'1+1 – 3+1'],6:[677,'1+1 – 4+1'],
    7:[136,'2+1 – 5+1'],8:[686,'1+1 – 4+1'],9:[548,'1+1 – 5+1'],10:[282,'2+1 – 3+1'],11:[1296,'1+1 – 4+1'],
    12:[855,'2+1 – 4+1'],13:[1160,'1+1 – 3+1'],14:[252,'1+1 – 3+1'],15:[262,'1+1 – 4+1'],16:[760,'1+1 – 3+1'],
    17:[1097,'1+1 – 4+1'],18:[503,'Ofis'],19:[250,'2+1 – 5+1']};
  var TESLIM = [4,5,6,7,10,14,15,16,19];
  var KAT = [2,3,4,5,11,12,19];
  var ST = {ok:['Teslim edildi','#1fb855'], now:['Teslimde','#FB5160'], next:['Yaklaşıyor','#4d8dff'], soon:['Yakında','#f0a400']};
  var AY = ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'];
  var today = new Date(); today.setHours(0,0,0,0);
  function P(s){ var a = s.split('-'); return new Date(+a[0], +a[1]-1, +a[2]); }
  function fmt(d){ return d.getDate() + ' ' + AY[d.getMonth()]; }
  function tr(n){ return Number(n).toLocaleString('tr-TR'); }
  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function track(ev, p){ try { window.gtag && gtag('event', ev, p || {}); } catch(e){} }

  // bulunduğumuz etap sayfası (yeni-fikirtepe-6-etap.html) varsa o etap işaretli açılır
  var m = /yeni-fikirtepe-(\d+)-etap/.exec(location.pathname), HERE = m ? +m[1] : 0;

  var css = ''+
  '.ep-tab{position:fixed;right:0;top:50%;z-index:9990;transform:translateY(-50%);display:flex;flex-direction:column;align-items:center;gap:8px;'+
    'padding:12px 7px 14px 9px;border:0;border-radius:14px 0 0 14px;background:#0a2a5e;color:#fff;cursor:pointer;font:inherit;'+
    'box-shadow:-6px 8px 24px -8px rgba(5,10,48,.55),inset 0 0 0 1px rgba(255,255,255,.14);transition:padding .25s,background .25s}'+
  '.ep-tab:hover{background:#143d82;padding-right:11px}'+
  '.ep-tab .ep-ic{width:22px;height:22px;flex:none}'+
  '.ep-tab .ep-tx{writing-mode:vertical-rl;transform:rotate(180deg);font-size:12px;font-weight:700;letter-spacing:.14em}'+
  '.ep-tab .ep-live{position:relative;display:grid;place-items:center;min-width:20px;height:20px;padding:0 5px;border-radius:10px;background:#FB5160;font-size:11px;font-weight:800}'+
  '.ep-tab .ep-live::after{content:"";position:absolute;inset:-3px;border-radius:inherit;border:2px solid #FB5160;animation:epP 1.8s ease-out infinite}'+
  '@keyframes epP{0%{opacity:.9;transform:scale(.9)}100%{opacity:0;transform:scale(1.5)}}'+
  '.ep-scrim{position:fixed;inset:0;z-index:10001;background:rgba(5,10,48,.35);opacity:0;visibility:hidden;transition:opacity .3s,visibility .3s}'+
  '.ep-pan{position:fixed;right:0;top:50%;z-index:10002;width:min(372px,calc(100vw - 28px));max-height:calc(100% - 28px);overflow-y:auto;overscroll-behavior:contain;'+
    'transform:translate(calc(100% + 30px),-50%);background:#fff;color:#0f1722;border-radius:22px 0 0 22px;padding:18px 18px 16px;'+
    'box-shadow:-24px 0 60px -20px rgba(5,10,48,.55);visibility:hidden;transition:transform .45s cubic-bezier(.2,.9,.25,1),visibility 0s .45s;font-family:"Archivo","Plus Jakarta Sans",system-ui,sans-serif;line-height:1.35;text-align:left}'+
  '.ep-on .ep-scrim{opacity:1;visibility:visible}.ep-on .ep-pan{transform:translate(0,-50%);visibility:visible;transition-delay:0s}.ep-on .ep-tab{opacity:0;pointer-events:none}body:has(.topnav.open) .ep-tab,body:has(.menu-toggle.open) .ep-tab{opacity:0;pointer-events:none}'+
  '.ep-pan *{box-sizing:border-box}'+
  '.ep-hd{display:flex;align-items:flex-start;gap:10px;margin-bottom:12px}'+
  '.ep-hd .ep-ic{width:34px;height:34px;flex:none;color:#0a2a5e}'+
  '.ep-hd b{display:block;font-size:1.12rem;font-weight:800;color:#0a2a5e;letter-spacing:-.01em}'+
  '.ep-hd span{display:block;font-size:.78rem;color:#5b6473}'+
  '.ep-x{margin-left:auto;flex:none;width:34px;height:34px;border-radius:50%;border:0;background:#f5f7fb;color:#0a2a5e;font-size:1.3rem;line-height:1;cursor:pointer}'+
  '.ep-sum{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:12px}'+
  '.ep-sum button{border:0;border-radius:12px;padding:8px 6px 7px;background:color-mix(in srgb,var(--c) 11%,#fff);cursor:pointer;font:inherit;text-align:center;'+
    'box-shadow:inset 0 0 0 1.5px transparent;transition:box-shadow .2s}'+
  '.ep-sum button.on{box-shadow:inset 0 0 0 1.5px var(--c)}'+
  '.ep-sum b{display:block;font-size:1.3rem;font-weight:800;color:var(--c);font-variant-numeric:tabular-nums}'+
  '.ep-sum span{display:block;font-size:.68rem;font-weight:700;color:#3a4453;letter-spacing:.02em}'+
  '.ep-live-l{display:grid;gap:6px;margin-bottom:12px}'+
  '.ep-row{display:block;text-decoration:none;color:inherit;border-radius:12px;padding:9px 11px;background:#f5f7fb;border-left:4px solid var(--c)}'+
  '.ep-row .t{display:flex;justify-content:space-between;gap:8px;font-size:.86rem;font-weight:800;color:#0a2a5e}'+
  '.ep-row .t em{font-style:normal;font-size:.7rem;font-weight:800;color:var(--c);letter-spacing:.04em}'+
  '.ep-row p{margin:2px 0 6px;font-size:.76rem;color:#3a4453}'+
  '.ep-row .trk{height:5px;border-radius:5px;background:#e3e7ef;overflow:hidden}.ep-row .trk i{display:block;height:100%;border-radius:5px;background:linear-gradient(90deg,#DC1C2E,#FB5160)}'+
  '.ep-row .n{display:block;margin-top:4px;font-size:.66rem;font-weight:700;color:#5b6473}'+
  '.ep-cap{font-size:.7rem;font-weight:800;letter-spacing:.08em;color:#5b6473;margin:0 0 6px}'+
  '.ep-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:6px}'+
  '.ep-grid button{position:relative;aspect-ratio:1;border:0;border-radius:11px;background:#0a2a5e;color:#fff;font:inherit;font-size:.95rem;font-weight:800;cursor:pointer;'+
    'box-shadow:inset 0 -4px 0 var(--c);transition:transform .15s,opacity .25s,background .2s}'+
  '.ep-grid button:hover{transform:translateY(-2px)}'+
  '.ep-grid button.sel{background:#DC1C2E}'+
  '.ep-grid button.dim{opacity:.18}'+
  '.ep-grid button.here::after{content:"";position:absolute;top:4px;right:4px;width:6px;height:6px;border-radius:50%;background:#fff}'+
  '.ep-det{margin-top:10px;border-radius:14px;background:#f5f7fb;padding:11px 12px;font-size:.8rem;color:#3a4453}'+
  '.ep-det h4{margin:0 0 2px;font-size:.98rem;font-weight:800;color:#0a2a5e;display:flex;align-items:center;gap:8px}'+
  '.ep-det h4 i{font-style:normal;font-size:.62rem;font-weight:800;letter-spacing:.06em;color:var(--c);background:color-mix(in srgb,var(--c) 14%,#fff);padding:2px 8px;border-radius:999px}'+
  '.ep-det p{margin:0 0 9px}'+
  '.ep-go{display:grid;grid-template-columns:1fr 1fr;gap:6px}'+
  '.ep-go a{display:flex;align-items:center;justify-content:center;text-decoration:none;font-weight:700;font-size:.8rem;padding:10px 6px;border-radius:10px;background:#fff;color:#0a2a5e;box-shadow:inset 0 0 0 1px #e6e9ef}'+
  '.ep-go a.p{background:#DC1C2E;color:#fff;box-shadow:none}'+
  '.ep-ft{display:flex;gap:6px;margin-top:12px}'+
  '.ep-ft a{flex:1;display:flex;align-items:center;justify-content:center;gap:6px;text-decoration:none;font-weight:700;font-size:.8rem;padding:10px 6px;border-radius:10px}'+
  '.ep-ft .a{background:#0a2a5e;color:#fff}.ep-ft .w{background:#e9f9ef;color:#128c4a}'+
  '.ep-ft svg{width:16px;height:16px;fill:currentColor}'+
  '@media(max-width:600px){.ep-tab{top:auto;bottom:96px;transform:none;padding:9px 4px 10px 6px;gap:5px;border-radius:12px 0 0 12px}.ep-tab .ep-ic{width:17px;height:17px}.ep-tab .ep-tx{font-size:9.5px;letter-spacing:.12em}.ep-tab .ep-live{min-width:17px;height:17px;font-size:10px;padding:0 4px}'+
    '.ep-pan{top:auto;bottom:0;right:0;width:100%;max-height:86%;border-radius:22px 22px 0 0;transform:translateY(105%);padding-bottom:calc(16px + env(safe-area-inset-bottom))}'+
    '.ep-on .ep-pan{transform:none}}'+
  '@media(prefers-reduced-motion:reduce){.ep-tab .ep-live::after{animation:none}.ep-pan{transition:none}}';

  var IC = '<svg class="ep-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9.5"/><path d="M15.8 8.2l-2.2 5.4-5.4 2.2 2.2-5.4z" fill="currentColor" stroke="none"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2"/></svg>';
  var WA = 'M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.64.07-.3-.15-1.26-.46-2.39-1.47-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.61-.92-2.21-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.08c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.63.71.23 1.36.2 1.87.12.57-.09 1.76-.72 2.01-1.41.25-.69.25-1.29.17-1.41-.07-.12-.27-.2-.57-.35zM12.04 21.5a9.43 9.43 0 0 1-4.8-1.32l-.35-.21-3.57.94.95-3.48-.22-.36a9.4 9.4 0 0 1-1.44-5.02c0-5.2 4.23-9.43 9.44-9.43 2.52 0 4.89.98 6.67 2.77a9.37 9.37 0 0 1 2.76 6.67c0 5.2-4.24 9.44-9.43 9.44zm8.03-17.47A11.27 11.27 0 0 0 12.04.7C5.78.7.69 5.79.69 12.04c0 2 .52 3.95 1.52 5.67L.6 23.3l5.72-1.5a11.33 11.33 0 0 0 5.42 1.38c6.25 0 11.34-5.09 11.35-11.35 0-3.03-1.18-5.88-3.33-8.02z';

  var E = {}, filt = '', sel = HERE || 0, root, pan;

  function program(j){
    var bas = null, bit = null, top = 0, tes = 0, now = [], sir = null;
    j.bloklar.forEach(function(b){ var a = P(b.bas), z = P(b.bit); if (!bas || a < bas) bas = a; if (!bit || z > bit) bit = z; top += b.daire || 0;
      if (today > z) tes += b.daire || 0; else if (today >= a) now.push(b.b); else if (!sir || a < P(sir.bas)) sir = b; });
    return {id:j.id, ad:j.ad, bas:bas, bit:bit, top:top, tes:tes, now:now, sir:sir,
      st: today > bit ? 'ok' : today >= bas ? 'now' : 'next', ts: j.toprakSahibi && j.toprakSahibi.bas ? P(j.toprakSahibi.bas) : null};
  }
  function build(json){
    var prg = {};
    (json && json.etaplar || []).forEach(function(j){ var n = parseInt(j.id, 10); if (INFO[n] && j.bloklar && j.bloklar.length) prg[n] = program(j); });
    Object.keys(INFO).forEach(function(k){ var n = +k, p = prg[n]; E[n] = {n:n, p:p || null, st: p ? p.st : TESLIM.indexOf(n) >= 0 ? 'ok' : 'soon'}; });
    render();
  }
  function grp(st){ return st === 'next' ? 'soon' : st; }   // özet kutularında "Yaklaşıyor" da "Yakında"ya sayılır

  function render(){
    var c = {ok:0, now:0, soon:0}, live = [];
    Object.keys(E).forEach(function(k){ var e = E[k]; c[grp(e.st)]++; if (e.st === 'now' || e.st === 'next') live.push(e); });
    var tab = root.querySelector('.ep-tab');
    tab.innerHTML = IC + '<span class="ep-tx">ETAPLAR</span>' + (c.now ? '<span class="ep-live" title="Teslimi süren etap">' + c.now + '</span>' : '');
    tab.setAttribute('aria-label', 'Etap Pusulası: 18 etabın teslim durumu' + (c.now ? ', ' + c.now + ' etapta teslim sürüyor' : ''));

    var h = '<div class="ep-hd">' + IC + '<div><b>Etap Pusulası</b><span>Bugün ' + fmt(today) + ' · 18 etabın teslim durumu</span></div>' +
      '<button class="ep-x" type="button" aria-label="Kapat">&times;</button></div>';
    h += '<div class="ep-sum">' + ['ok','now','soon'].map(function(k){
      return '<button type="button" data-f="' + k + '" class="' + (filt === k ? 'on' : '') + '" style="--c:' + ST[k][1] + '"><b>' + c[k] + '</b><span>' + ST[k][0] + '</span></button>'; }).join('') + '</div>';
    if (live.length){
      h += '<p class="ep-cap">ŞU AN</p><div class="ep-live-l">';
      live.sort(function(a,b){ return a.p.bas - b.p.bas; }).forEach(function(e){
        var p = e.p, s, pct = p.top ? Math.round(p.tes / p.top * 100) : 0;
        if (e.st === 'now') s = p.now.length ? '<b>' + esc(p.now.join(', ')) + ' Blok</b> teslimde' + (p.sir ? ' · sırada ' + esc(p.sir.b) + ' Blok, ' + fmt(P(p.sir.bas)) : ' · son gün ' + fmt(p.bit))
          : p.sir ? 'Sıradaki blok: <b>' + esc(p.sir.b) + '</b>, ' + fmt(P(p.sir.bas)) : 'Son gün ' + fmt(p.bit);
        else s = 'Anahtar teslimi <b>' + fmt(p.bas) + '</b> tarihinde başlıyor';
        if (p.ts && today < p.ts) s += ' · toprak sahipleri ' + fmt(p.ts);
        h += '<a class="ep-row" style="--c:' + ST[e.st][1] + '" href="' + BASE + 'teslim-takvimi.html#etap-' + esc(p.id) + '" data-ev="' + e.n + '">' +
          '<div class="t">' + esc(p.ad) + '<em>' + ST[e.st][0].toLocaleUpperCase('tr-TR') + '</em></div><p>' + s + '</p>' +
          (p.top ? '<div class="trk"><i style="width:' + pct + '%"></i></div><span class="n">' + tr(p.tes) + ' / ' + tr(p.top) + ' daire teslim edildi</span>' : '') + '</a>';
      });
      h += '</div>';
    }
    h += '<p class="ep-cap">ETAP SEÇİN</p><div class="ep-grid">';
    Object.keys(E).forEach(function(k){ var e = E[k], cl = (sel === e.n ? 'sel ' : '') + (filt && grp(e.st) !== filt ? 'dim ' : '') + (HERE === e.n ? 'here' : '');
      h += '<button type="button" data-n="' + e.n + '" class="' + cl + '" style="--c:' + ST[e.st][1] + '" aria-label="' + e.n + '. Etap, ' + ST[e.st][0] + '">' + e.n + '</button>'; });
    h += '</div>';
    if (sel && E[sel]) h += det(E[sel]);
    h += '<div class="ep-ft"><a class="a" href="' + BASE + 'vaziyet-plani.html">360° vaziyet planı</a>' +
      '<a class="w" href="https://wa.me/902163151515?text=' + encodeURIComponent('Merhaba, Yeni Fikirtepe' + (sel ? ' ' + sel + '. Etap' : '') + ' hakkında bilgi almak istiyorum.') + '" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="' + WA + '"/></svg>Etabı sorun</a></div>';
    pan.innerHTML = h;
  }
  function det(e){
    var n = e.n, inf = INFO[n], p = e.p, s;
    if (e.st === 'ok') s = 'Anahtarlar sahiplerine teslim edildi.';
    else if (e.st === 'now') s = 'Anahtar teslimleri sürüyor' + (p && p.sir ? '; sırada ' + esc(p.sir.b) + ' Blok (' + fmt(P(p.sir.bas)) + ').' : '.');
    else if (e.st === 'next') s = 'Anahtar teslimi ' + fmt(p.bas) + ' tarihinde başlıyor.';
    else s = 'Teslim programı henüz açıklanmadı.';
    var info = n === 18 ? '503 ofis · ticari etap' : tr(inf[0]) + ' konut · ' + inf[1];
    return '<div class="ep-det" style="--c:' + ST[e.st][1] + '"><h4>' + n + '. Etap<i>' + ST[e.st][0].toLocaleUpperCase('tr-TR') + '</i></h4><p>' + info + '. ' + s + '</p>' +
      '<div class="ep-go"><a class="p" href="' + BASE + 'vaziyet-plani.html#etap-' + n + '">360°’de gör</a>' +
      (KAT.indexOf(n) >= 0 ? '<a href="' + BASE + 'kat-planlari.html#etap-' + n + '">Kat planları</a>' : '<a href="' + BASE + 'teslim-takvimi.html#etap-' + (p ? esc(p.id) : n) + '">Teslim bilgisi</a>') +
      '</div></div>';
  }

  function open(){ document.documentElement.classList.add('ep-on'); track('etap_pusulasi_ac'); setTimeout(function(){ var x = pan.querySelector('.ep-x'); x && x.focus({preventScroll:true}); }, 50); }
  function close(){ document.documentElement.classList.remove('ep-on'); }

  function init(){
    var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    root = document.createElement('div'); root.className = 'ep-root';
    root.innerHTML = '<button class="ep-tab" type="button"></button><div class="ep-scrim"></div><aside class="ep-pan" role="dialog" aria-label="Etap Pusulası"></aside>';
    document.body.appendChild(root); pan = root.querySelector('.ep-pan');
    root.querySelector('.ep-tab').onclick = open;
    root.querySelector('.ep-scrim').onclick = close;
    document.addEventListener('keydown', function(ev){ if (ev.key === 'Escape') close(); });
    pan.addEventListener('click', function(ev){
      var t = ev.target.closest('button,a'); if (!t) return;
      if (t.classList.contains('ep-x')) return close();
      if (t.dataset.f){ filt = filt === t.dataset.f ? '' : t.dataset.f; render(); return; }
      if (t.dataset.n){ var n = +t.dataset.n; sel = sel === n ? 0 : n; render(); track('etap_pusulasi_etap', {etap:n}); var d = pan.querySelector('.ep-det'); d && d.scrollIntoView({block:'nearest', behavior:'smooth'}); return; }
      if (t.dataset.ev) track('etap_pusulasi_teslim', {etap:+t.dataset.ev});
    });
    build({etaplar:[]});
    fetch(BASE + 'teslim-takvimi.json?cb=' + Math.floor(Date.now() / 6e5), {cache:'no-store'}).then(function(r){ if (!r.ok) throw 0; return r.json(); }).then(build).catch(function(){});
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
