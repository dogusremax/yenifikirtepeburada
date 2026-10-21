/* Dil seçici: Kıbrıs sayfasındakiyle aynı görünüm (bayraklı TR / EN / RU / FA / DE / PL).
   Sayfa metinleri Türkçe kalır; seçilen dilde dil/<kod>.json sözlüğündeki karşılıkla değiştirilir.
   Seçim ?lang= ile, sonra kayıtlı tercihle, sonra tarayıcı diliyle belirlenir; sayfalar arası hatırlanır.
   <script src="dil.js" defer></script> */
(function(){
  if (window.__dil) return; window.__dil = 1;
  var LANGS = ['tr','en','ru','fa','de','pl'];
  var ADI = {tr:'Türkçe',en:'English',ru:'Русский',fa:'فارسی',de:'Deutsch',pl:'Polski'};
  var KEY = 'fikirtepe_lang';
  var me = document.currentScript;
  var BASE = (me && me.src ? me.src.replace(/[^\/]*$/, '') : '') + 'dil/';
  var root = document.documentElement;

  function pick(){
    try { var q = (new URLSearchParams(location.search).get('lang') || '').toLowerCase(); if (LANGS.indexOf(q) > -1) return q; } catch(e){}
    try { var s = localStorage.getItem(KEY); if (LANGS.indexOf(s) > -1) return s; } catch(e){}
    if (/bot|crawl|spider|slurp|inspectiontool|lighthouse/i.test(navigator.userAgent || '')) return 'tr';
   var ls = navigator.languages || [navigator.language || ''];
    for (var i = 0; i < ls.length; i++) { var p = String(ls[i]).slice(0,2).toLowerCase(); if (LANGS.indexOf(p) > -1) return p; }
    return 'tr';
  }

  var FLAG = {
    tr:'%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 1200 800%22%3E%3Crect width=%221200%22 height=%22800%22 fill=%22%23E30A17%22/%3E%3Ccircle cx=%22425%22 cy=%22400%22 r=%22200%22 fill=%22%23fff%22/%3E%3Ccircle cx=%22475%22 cy=%22400%22 r=%22160%22 fill=%22%23E30A17%22/%3E%3Cpolygon fill=%22%23fff%22 points=%22475.0,400.0 544.1,377.5 544.1,304.9 586.8,363.7 655.9,341.2 613.2,400.0 655.9,458.8 586.8,436.3 544.1,495.1 544.1,422.5%22/%3E%3C/svg%3E',
    en:'%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 60 30%22%3E%3CclipPath id=%22s%22%3E%3Cpath d=%22M0,0v30h60V0z%22/%3E%3C/clipPath%3E%3CclipPath id=%22t%22%3E%3Cpath d=%22M30,15h30v15zv15H0zH0V0zV0h30z%22/%3E%3C/clipPath%3E%3Cg clip-path=%22url%28%23s%29%22%3E%3Cpath d=%22M0,0v30h60V0z%22 fill=%22%23012169%22/%3E%3Cpath d=%22M0,0L60,30M60,0L0,30%22 stroke=%22%23fff%22 stroke-width=%226%22/%3E%3Cpath d=%22M0,0L60,30M60,0L0,30%22 clip-path=%22url%28%23t%29%22 stroke=%22%23C8102E%22 stroke-width=%224%22/%3E%3Cpath d=%22M30,0v30M0,15h60%22 stroke=%22%23fff%22 stroke-width=%2210%22/%3E%3Cpath d=%22M30,0v30M0,15h60%22 stroke=%22%23C8102E%22 stroke-width=%226%22/%3E%3C/g%3E%3C/svg%3E',
    ru:'%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 9 6%22%3E%3Crect width=%229%22 height=%226%22 fill=%22%23fff%22/%3E%3Crect y=%222%22 width=%229%22 height=%224%22 fill=%22%230039A6%22/%3E%3Crect y=%224%22 width=%229%22 height=%222%22 fill=%22%23D52B1E%22/%3E%3C/svg%3E',
    fa:'%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 7 4%22%3E%3Crect width=%227%22 height=%224%22 fill=%22%23DA0000%22/%3E%3Crect width=%227%22 height=%222.67%22 fill=%22%23fff%22/%3E%3Crect width=%227%22 height=%221.33%22 fill=%22%23239F40%22/%3E%3C/svg%3E',
    de:'%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 5 3%22%3E%3Crect width=%225%22 height=%223%22 fill=%22%23FFCE00%22/%3E%3Crect width=%225%22 height=%222%22 fill=%22%23DD0000%22/%3E%3Crect width=%225%22 height=%221%22 fill=%22%23000%22/%3E%3C/svg%3E',
    pl:'%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 8 5%22%3E%3Crect width=%228%22 height=%225%22 fill=%22%23DC143C%22/%3E%3Crect width=%228%22 height=%222.5%22 fill=%22%23fff%22/%3E%3C/svg%3E'
  };

  var css = '.dil-sel{position:fixed;top:12px;inset-inline-end:12px;z-index:10050;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}' +
    '.dil-btn{display:flex;align-items:center;gap:8px;background:rgba(10,20,30,.55);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);color:#fff;border:1px solid rgba(255,255,255,.35);border-radius:999px;padding:6px 12px 6px 8px;font:700 .8rem ui-monospace,Menlo,Consolas,monospace;letter-spacing:.06em;cursor:pointer;box-shadow:0 6px 18px -8px rgba(0,0,0,.5)}' +
    '.dil-btn::after{content:"";width:6px;height:6px;border-right:2px solid currentColor;border-bottom:2px solid currentColor;transform:translateY(-2px) rotate(45deg);opacity:.8;margin-inline-start:2px}' +
    '.dil-btn[aria-expanded="true"]{background:rgba(10,20,30,.75)}' +
    '.dil-flag{display:inline-block;flex:0 0 auto;width:24px;height:16px;border-radius:3px;background-size:cover;background-position:center;box-shadow:0 0 0 1px rgba(0,0,0,.18)}' +
    '.dil-btn .dil-flag{width:22px;height:15px}' +
    '.dil-menu{position:absolute;inset-inline-end:0;top:calc(100% + 8px);list-style:none;margin:0;padding:6px;background:#fff;border:1px solid #D3E0E3;border-radius:14px;box-shadow:0 20px 40px -16px rgba(0,0,0,.45);min-width:180px}' +
    '.dil-menu[hidden]{display:none}' +
    '.dil-menu button{width:100%;display:flex;align-items:center;gap:12px;background:none;border:0;color:#0D2230;padding:10px 12px;border-radius:9px;font:600 .95rem system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;text-align:start;cursor:pointer}' +
    '.dil-menu button:hover,.dil-menu button[aria-selected="true"]{background:#DCEDF1}' +
    'html.dil-bekle body{opacity:0}' +
    'html[lang="fa"] body{font-family:"Vazirmatn",system-ui,sans-serif}' +
    'html[lang="fa"] *{letter-spacing:0!important}' +
    '.dil-sel.dil-yer{position:relative;top:auto;inset-inline-end:auto;pointer-events:auto;flex:0 0 auto}' +
    '.dil-sel.dil-nav{position:absolute;top:50%;transform:translateY(-50%);inset-inline-end:16px}' +
    '.navbar.dil-navbar .topnav{padding-inline:118px}' +
    '@media(max-width:760px){.dil-sel.dil-nav{top:20px;transform:none;inset-inline-end:70px}.navbar.dil-navbar .topnav{padding-inline:24px}}' +
    '@media print{.dil-sel{display:none}}';
  for (var k in FLAG) css += '.dil-flag-' + k + '{background-image:url("data:image/svg+xml,' + FLAG[k] + '")}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  var L = pick(), D = null, cache = {};
  if (L !== 'tr') root.classList.add('dil-bekle');
  var guard = setTimeout(function(){ root.classList.remove('dil-bekle'); }, 1500);

  /* Özgün (Türkçe) metinler saklanır; dil değişince hep özgünden çevrilir. */
  var ORIG = new WeakMap(), SET = new WeakMap(), ATTR = ['placeholder','title','aria-label','alt'];
  var SKIP = /^(SCRIPT|STYLE|NOSCRIPT|TEXTAREA|CODE|PRE)$/;
  var orgTitle = document.title, busy = false;

  function norm(s){ return s.replace(/\s+/g, ' ').trim(); }
  function tr(s){
    if (!D) return null;
    var n = norm(s); if (!n) return null;
    var t = D[n];
    if (t == null && D.__re) { /* sayılı/tarihli metinler: ["^(\\d+)\\. Etap$", "Phase $1"] */
      if (!D.__rc) D.__rc = D.__re.map(function(r){ return [new RegExp(r[0]), r[1]]; });
      for (var i = 0; i < D.__rc.length; i++) if (D.__rc[i][0].test(n)) { t = n.replace(D.__rc[i][0], D.__rc[i][1]); break; }
    }
    if (t == null || t === n) return null;
    var m = s.match(/^\s*/)[0], e = s.match(/\s*$/)[0];
    return m + t + e;
  }
  function skip(el){
    for (; el && el !== document.body; el = el.parentElement) {
      if (SKIP.test(el.tagName) || el.isContentEditable || (el.classList && el.classList.contains('dil-sel')) || (el.hasAttribute && el.hasAttribute('data-dil-yok'))) return true;
    }
    return false;
  }
  function doText(n){
    var cur = n.nodeValue;
    if (!ORIG.has(n) || SET.get(n) !== cur) ORIG.set(n, cur); /* sayfa metni kendisi değiştirdiyse yeni özgün odur */
    var o = ORIG.get(n), v = L === 'tr' ? o : (tr(o) || o);
    if (v !== cur) n.nodeValue = v;
    SET.set(n, v);
  }
  function doAttrs(el){
    if (!el.getAttribute) return;
    var store = el.__dilA || (el.__dilA = {});
    for (var i = 0; i < ATTR.length; i++) {
      var a = ATTR[i], cur = el.getAttribute(a);
      if (cur == null) continue;
      if (!store[a] || store[a].set !== cur) store[a] = {o: cur};
      var v = L === 'tr' ? store[a].o : (tr(store[a].o) || store[a].o);
      if (v !== cur) el.setAttribute(a, v);
      store[a].set = v;
    }
    if (el.tagName === 'INPUT' && /^(submit|button)$/i.test(el.type)) {
      var s2 = el.__dilV || (el.__dilV = {}), cv = el.value;
      if (!s2.o || s2.set !== cv) { s2.o = cv; }
      var vv = L === 'tr' ? s2.o : (tr(s2.o) || s2.o);
      if (vv !== cv) el.value = vv; s2.set = vv;
    }
  }
  function walk(rootNode){
    if (!rootNode) return;
    if (rootNode.nodeType === 3) { if (!skip(rootNode.parentElement)) doText(rootNode); return; }
    if (rootNode.nodeType !== 1 || skip(rootNode)) return;
    doAttrs(rootNode);
    var w = document.createTreeWalker(rootNode, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT, {
      acceptNode: function(x){ return (x.nodeType === 1 && (SKIP.test(x.tagName) || x.classList.contains('dil-sel'))) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT; }
    });
    var x; while ((x = w.nextNode())) { if (x.nodeType === 3) doText(x); else doAttrs(x); }
  }
  function all(){
    busy = true;
    walk(document.body);
    if (!ORIG.has(document) || SET.get(document) !== document.title) { orgTitle = document.title; ORIG.set(document, 1); }
    var tt = L === 'tr' ? orgTitle : (tr(orgTitle) || orgTitle);
    if (document.title !== tt) document.title = tt; SET.set(document, tt);
    busy = false;
  }

  var mo = new MutationObserver(function(list){
    if (busy) return;
    busy = true;
    for (var i = 0; i < list.length; i++) {
      var m = list[i];
      if (m.type === 'characterData') { if (SET.get(m.target) !== m.target.nodeValue && !skip(m.target.parentElement)) doText(m.target); }
      else if (m.type === 'attributes') { if (!skip(m.target)) doAttrs(m.target); }
      else for (var j = 0; j < m.addedNodes.length; j++) walk(m.addedNodes[j]);
    }
    busy = false;
  });

  function load(l, cb){
    if (l === 'tr') return cb({});
    if (cache[l]) return cb(cache[l]);
    fetch(BASE + l + '.json').then(function(r){ return r.json(); }).then(function(j){ cache[l] = j; cb(j); })
      .catch(function(){ cb(null); });
  }
  function fontFa(){
    if (document.getElementById('dil-vazir')) return;
    var l = document.createElement('link'); l.id = 'dil-vazir'; l.rel = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600;700&display=swap';
    document.head.appendChild(l);
  }

  var btn, menu, flag, code;
  function apply(l, user){
    load(l, function(d){
      if (d == null) { l = 'tr'; d = {}; }
      L = l; D = d;
      root.lang = l;
      root.dir = (l === 'fa' && !root.hasAttribute('data-dil-ltr')) ? 'rtl' : 'ltr'; /* data-dil-ltr: düzeni aynalanmayacak sayfalar */
      if (l === 'fa') fontFa();
      all();
      if (flag) { flag.className = 'dil-flag dil-flag-' + l; code.textContent = l.toUpperCase();
        menu.querySelectorAll('[data-lang]').forEach(function(b){ b.setAttribute('aria-selected', b.getAttribute('data-lang') === l); }); }
      clearTimeout(guard); root.classList.remove('dil-bekle');
      try { localStorage.setItem(KEY, l); } catch(e){}
      if (user) {
        try { var u = new URL(location.href); if (l === 'tr') u.searchParams.delete('lang'); else u.searchParams.set('lang', l); history.replaceState(history.state, '', u); } catch(e){}
        try { typeof gtag === 'function' && gtag('event', 'dil_secimi', {dil: l}); } catch(e){}
      }
    });
  }

  function build(){
    var box = document.createElement('div'); box.className = 'dil-sel'; box.setAttribute('translate', 'no');
    var items = '';
    for (var i = 0; i < LANGS.length; i++) items += '<li><button type="button" role="option" data-lang="' + LANGS[i] + '"><i class="dil-flag dil-flag-' + LANGS[i] + '"></i>' + ADI[LANGS[i]] + '</button></li>';
    box.innerHTML = '<button type="button" class="dil-btn" aria-haspopup="listbox" aria-expanded="false" aria-label="Dil / Language"><i class="dil-flag"></i><span>TR</span></button><ul class="dil-menu" role="listbox" hidden>' + items + '</ul>';
    /* Yer: sayfada data-dil-yer varsa oraya, menü çubuğu (.navbar) varsa onun sağına, yoksa sağ üst köşeye sabit */
    var yer = document.querySelector('[data-dil-yer]'), nav = document.querySelector('.navbar');
    if (yer) { box.classList.add('dil-yer'); yer.parentNode.replaceChild(box, yer); }
    else if (nav) { box.classList.add('dil-nav'); nav.classList.add('dil-navbar'); nav.appendChild(box); }
    else document.body.appendChild(box);
    btn = box.querySelector('.dil-btn'); menu = box.querySelector('.dil-menu'); flag = btn.querySelector('i'); code = btn.querySelector('span');
    function open(o){ menu.hidden = !o; btn.setAttribute('aria-expanded', o); }
    btn.addEventListener('click', function(e){ e.stopPropagation(); open(menu.hidden); });
    menu.querySelectorAll('[data-lang]').forEach(function(b){ b.addEventListener('click', function(){ open(false); var l = b.getAttribute('data-lang'); if (l !== L || !D) apply(l, true); }); });
    document.addEventListener('click', function(e){ if (!menu.hidden && !box.contains(e.target)) open(false); });
    document.addEventListener('keydown', function(e){ if (e.key === 'Escape' && !menu.hidden) { open(false); btn.focus(); } });
    /* Sayfa içi bağlantılara seçili dili taşı (localStorage kapalı tarayıcılar için) */
    document.addEventListener('click', function(e){
      var a = e.target.closest && e.target.closest('a[href]'); if (!a || L === 'tr') return;
      var h = a.getAttribute('href'); if (!/^[\w\-\/]+\.html(#.*)?$/.test(h)) return;
      try { var u = new URL(a.href); u.searchParams.set('lang', L); a.href = u.toString(); } catch(x){}
    }, true);
  }

  function start(){
    build();
    apply(L, false);
    mo.observe(document.body, {childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTR});
    new MutationObserver(function(){ if (!busy && document.title !== SET.get(document)) all(); })
      .observe(document.querySelector('title') || document.head, {childList: true, characterData: true, subtree: true});
  }
  if (document.body) start(); else document.addEventListener('DOMContentLoaded', start);
})();
