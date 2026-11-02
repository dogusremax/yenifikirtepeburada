/* Telefon menüsü: uzun tek sütun yerine gruplu, iki sütunlu, ikonlu ve tek ekrana sığan menü.
   Masaüstü menüye dokunmaz; yalnız 760px ve altı ekranlarda devreye girer.
   Linkler sayfadaki #mainNav'dan alınır (yeni link ekleyince GRUPLAR'a href'ini yaz).
   <script src="mobil-menu.js" defer></script> */
(function(){
  if (window.__mobilMenu) return; window.__mobilMenu = 1;
  var nav = document.getElementById('mainNav');
  if (!nav) return;

  var I = {
    ev:'<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>',
    etap:'<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    harita:'<polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/>',
    takvim:'<rect x="3" y="4" width="18" height="17" rx="3"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    plan:'<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 12h8v9"/><path d="M11 3v5"/><path d="M15 12h6"/>',
    video:'<rect x="2" y="5" width="15" height="14" rx="3"/><path d="M17 10l5-3v10l-5-3"/>',
    hesap:'<rect x="4" y="2" width="16" height="20" rx="3"/><rect x="7" y="5" width="10" height="4" rx="1"/><circle cx="8.5" cy="13" r=".8"/><circle cx="12" cy="13" r=".8"/><circle cx="15.5" cy="13" r=".8"/><circle cx="8.5" cy="17" r=".8"/><circle cx="12" cy="17" r=".8"/><circle cx="15.5" cy="17" r=".8"/>',
    para:'<circle cx="12" cy="12" r="9"/><path d="M15 9.5c-.6-1-1.7-1.5-3-1.5-1.7 0-3 .9-3 2s1.3 1.7 3 2 3 .9 3 2-1.3 2-3 2c-1.3 0-2.4-.5-3-1.5"/><line x1="12" y1="6" x2="12" y2="18"/>',
    anahtar:'<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9"/><path d="M17 6l3 3"/><path d="M15 8l2 2"/>',
    kitap:'<path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v18H6.5A2.5 2.5 0 0 0 4 22.5z"/><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>',
    kira:'<path d="M3 21h18"/><path d="M5 21V8l7-4 7 4v13"/><path d="M10 21v-5h4v5"/>',
    belge:'<path d="M6 2h9l5 5v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"/><polyline points="14 2 14 8 20 8"/><polyline points="9 15 11 17 15 13"/>',
    bilgi:'<circle cx="12" cy="12" r="9"/><line x1="12" y1="11" x2="12" y2="16"/><circle cx="12" cy="8" r=".6"/>',
    el:'<path d="M7 11l3-3 3 3 4-4"/><path d="M3 21h18"/><path d="M5 17V9"/><path d="M19 17V7"/>',
    ekip:'<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14.2a5 5 0 0 1 5.5 5.8"/>',
    kalp:'<path d="M12 21s-8-5.2-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 5.8-8 11-8 11z"/>',
    sosyal:'<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".8"/>',
    canta:'<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
    soru:'<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6v.6"/><circle cx="12" cy="17" r=".6"/>',
    tel:'<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>'
  };
  var IK = {
    'index.html':'ev','etaplar.html':'etap','vaziyet-plani.html':'harita','teslim-takvimi.html':'takvim','kat-planlari.html':'plan','videolar.html':'video',
    'hesaplama-araclari.html':'hesap','daire-satis-masraflari.html':'para','devir-rehberi.html':'anahtar','fikirtepe-rehberi.html':'kitap','kiralama-asamalari.html':'kira','ilan-rehberi.html':'belge',
    'hakkimizda.html':'bilgi','hizmetlerimiz.html':'el','ekibimiz.html':'ekip','satis-sonrasi.html':'kalp','sosyal-medya.html':'sosyal','kariyer.html':'canta',
    'sorulariniz.html':'soru','iletisim.html':'tel'
  };
  var GRUPLAR = [
    ['Proje', ['etaplar.html','vaziyet-plani.html','teslim-takvimi.html','kat-planlari.html','videolar.html']],
    ['Rehber ve Araçlar', ['hesaplama-araclari.html','daire-satis-masraflari.html','devir-rehberi.html','fikirtepe-rehberi.html','kiralama-asamalari.html','ilan-rehberi.html']],
    ['RE/MAX Doğuş', ['hakkimizda.html','hizmetlerimiz.html','ekibimiz.html','satis-sonrasi.html','sosyal-medya.html','kariyer.html']]
  ];
  var ALT = ['index.html','sorulariniz.html','iletisim.html'];
  var KISA = {'Sosyal Medya Hesaplarımız':'Sosyal Medya','Satış Sonrası Hizmetler':'Satış Sonrası'};

  var css =
  '.mm-ust,.mm-grup,.mm-alt{display:none}' +
  '@media(max-width:760px){' +
    '#mainNav.mm{display:block!important;padding:0 14px!important;max-height:0;overflow:hidden}' +
    '#mainNav.mm.open{max-height:calc(100vh - 64px)!important;max-height:calc(100dvh - 64px)!important;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:66px 14px 18px!important;overscroll-behavior:contain}' +
    '#mainNav.mm .mm-grup{display:block;margin:0 0 12px}' +
    '#mainNav.mm .mm-baslik{display:block;font:700 11px Arial,Helvetica,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:rgba(255,255,255,.55);margin:8px 2px 7px}' +
    '#mainNav.mm .mm-izgara{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:7px}' +
    '#mainNav.mm .mm-izgara a{display:flex!important;align-items:center;gap:9px;width:auto!important;min-width:0;min-height:46px;padding:8px 10px!important;margin:0!important;border:1px solid rgba(255,255,255,.12)!important;border-radius:13px!important;background:rgba(255,255,255,.06);font:700 13.5px/1.2 Arial,Helvetica,sans-serif!important;letter-spacing:0!important;color:#fff!important;opacity:1!important;text-align:left;box-shadow:none!important}' +
    '#mainNav.mm a svg{flex:none;width:19px;height:19px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;opacity:.9}' +
    '#mainNav.mm .mm-izgara a span{min-width:0;overflow:hidden;text-overflow:ellipsis}' +
    '#mainNav.mm a.active{background:#DC1C2E!important;border-color:#DC1C2E!important}' +
    '#mainNav.mm .mm-alt{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px;margin-top:4px;padding-top:12px;border-top:1px solid rgba(255,255,255,.12)}' +
    '#mainNav.mm .mm-alt a{display:flex!important;flex-direction:column;align-items:center;justify-content:center;gap:5px;width:auto!important;min-width:0;min-height:58px;padding:8px 4px!important;margin:0!important;border:1px solid rgba(255,255,255,.14)!important;border-radius:13px!important;background:rgba(255,255,255,.06);font:700 12.5px/1.15 Arial,Helvetica,sans-serif!important;color:#fff!important;opacity:1!important;text-align:center;box-shadow:none!important}' +
    '#mainNav.mm .mm-alt a[href="iletisim.html"]:not(.active){background:#fff!important;color:#0a2a5e!important;border-color:#fff!important}' +
    'body:has(#mainNav.mm.open) #dutyCard,body:has(#mainNav.mm.open) .wa-fab{visibility:hidden!important}' +
    '#mainNav.mm .mm-diger{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:7px;margin-bottom:12px}' +
  '}';
  var st = document.createElement('style'); st.id = 'mobil-menu-css'; st.textContent = css; document.head.appendChild(st);

  function svg(k){ return '<svg viewBox="0 0 24 24" aria-hidden="true">' + (I[k] || I.belge) + '</svg>'; }
  function yol(a){ return (a.getAttribute('href') || '').split('#')[0].split('?')[0].replace(/^\.?\//, ''); }

  var linkler = Array.prototype.slice.call(nav.querySelectorAll('a'));
  var bul = {}; linkler.forEach(function(a){ bul[yol(a)] = a; a.__mmAsil = a.innerHTML; });
  var grupta = {};
  GRUPLAR.forEach(function(g){ g[1].forEach(function(h){ grupta[h] = 1; }); });
  ALT.forEach(function(h){ grupta[h] = 1; });
  var diger = linkler.filter(function(a){ return !grupta[yol(a)]; });

  // kutular bir kez kurulur
  var kutular = [];
  function kutu(baslik, sinif){
    var k = document.createElement('div'); k.className = sinif || 'mm-grup';
    if (baslik) { var b = document.createElement('span'); b.className = 'mm-baslik'; b.textContent = baslik; k.appendChild(b); }
    var iz = k; if (!sinif) { iz = document.createElement('div'); iz.className = 'mm-izgara'; k.appendChild(iz); }
    kutular.push(k); return iz;
  }
  var yerlesim = [];
  GRUPLAR.forEach(function(g){
    var var_ = g[1].filter(function(h){ return bul[h]; }).map(function(h){ return bul[h]; });
    if (var_.length) yerlesim.push([kutu(g[0]), var_]);
  });
  if (diger.length) yerlesim.push([kutu(''), diger]);
  yerlesim.push([kutu('', 'mm-alt'), ALT.filter(function(h){ return bul[h]; }).map(function(h){ return bul[h]; })]);

  function telefon(a){
    var metin = a.textContent.replace(/\s+/g, ' ').trim();
    if (KISA[metin]) { a.setAttribute('title', metin); metin = KISA[metin]; }
    a.innerHTML = svg(IK[yol(a)]) + '<span>' + metin + '</span>';
  }
  var mq = window.matchMedia('(max-width:760px)');
  var mod = null;
  function uygula(){
    var tel = mq.matches;
    if (tel === mod) return; mod = tel;
    if (tel) {
      yerlesim.forEach(function(y){ y[1].forEach(function(a){ telefon(a); y[0].appendChild(a); }); });
      kutular.forEach(function(k){ nav.appendChild(k); });
      nav.classList.add('mm');
    } else {
      nav.classList.remove('mm');
      linkler.forEach(function(a){ a.innerHTML = a.__mmAsil; a.removeAttribute('title'); nav.appendChild(a); });
      kutular.forEach(function(k){ if (k.parentNode) k.parentNode.removeChild(k); });
    }
  }
  uygula();
  if (mq.addEventListener) mq.addEventListener('change', uygula); else if (mq.addListener) mq.addListener(uygula);

  // masaüstünde ikon görünmesin
  var st2 = document.createElement('style');
  st2.textContent = '@media(min-width:761px){#mainNav a svg{display:none}}';
  document.head.appendChild(st2);
})();
