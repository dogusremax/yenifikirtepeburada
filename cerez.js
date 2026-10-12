/* Çerez onayı: küçük alt şerit (Kabul et / Reddet) + Google Consent Mode v2.
   Onay yokken Analytics çerez bırakmaz, yalnızca çerezsiz sinyal gönderir; "Kabul et" ile çerezler açılır.
   Seçim 12 ay hatırlanır. gtag config'inden ÖNCE, defer'sız yüklenmeli:
   <script src="cerez.js" data-ga="G-XXXX"></script> */
(function(){
  if (window.__cerez) return; window.__cerez = 1;
  var me = document.currentScript || {getAttribute:function(){return null;}};
  var GA = me.getAttribute('data-ga') || '';
  var POL = me.getAttribute('data-politika') || 'cerez-politikasi.html';
  var KEY = 'cerezOnay', YIL = 365*864e5;

  var M = {
    tr:{ga:'Ziyaretleri ölçmek için çerez kullanıyoruz.',
        yok:'Bu sayfa yalnızca çalışması için gerekli kayıtları (dil seçimi, hesap tercihleri) tutar. İsteğe bağlı ölçüm çerezleri yalnızca onayınızla çalışır.',
        pol:'Çerez Politikası',kabul:'Kabul et',red:'Reddet',ayar:'Çerez tercihleri'},
    en:{ga:'We use cookies to measure visits.',
        yok:'This page only stores what it needs to work (language, calculator settings). Optional analytics cookies only run with your consent.',
        pol:'Cookie Policy',kabul:'Accept',red:'Reject',ayar:'Cookie settings'},
    ru:{ga:'Мы используем файлы cookie Google Analytics, чтобы считать посещения и популярные страницы. Они работают только с вашего согласия.',
        yok:'Эта страница хранит только то, что нужно для работы (язык, настройки калькулятора). Необязательные аналитические cookie работают только с вашего согласия.',
        pol:'Политика cookie',kabul:'Принять',red:'Отклонить',ayar:'Настройки cookie'},
    fa:{ga:'ما از کوکی‌های Google Analytics برای سنجش بازدیدها و صفحات پربازدید استفاده می‌کنیم. این کوکی‌ها فقط با موافقت شما فعال می‌شوند.',
        yok:'این صفحه فقط داده‌های لازم برای کارکرد خود (زبان، تنظیمات ماشین‌حساب) را نگه می‌دارد. کوکی‌های اختیاری سنجش فقط با موافقت شما فعال می‌شوند.',
        pol:'سیاست کوکی',kabul:'می‌پذیرم',red:'رد می‌کنم',ayar:'تنظیمات کوکی'},
    de:{ga:'Wir verwenden Google-Analytics-Cookies, um Besuche und beliebte Seiten zu messen. Sie werden nur mit Ihrer Zustimmung aktiviert.',
        yok:'Diese Seite speichert nur, was sie zum Funktionieren braucht (Sprache, Rechner-Einstellungen). Optionale Analyse-Cookies laufen nur mit Ihrer Zustimmung.',
        pol:'Cookie-Richtlinie',kabul:'Akzeptieren',red:'Ablehnen',ayar:'Cookie-Einstellungen'},
    pl:{ga:'Używamy plików cookie Google Analytics, aby mierzyć odwiedziny i popularne strony. Działają tylko za Twoją zgodą.',
        yok:'Ta strona przechowuje tylko to, co potrzebne do działania (język, ustawienia kalkulatora). Opcjonalne analityczne pliki cookie działają tylko za Twoją zgodą.',
        pol:'Polityka cookies',kabul:'Akceptuję',red:'Odrzucam',ayar:'Ustawienia cookies'}
  };
  function dil(){ var l=(document.documentElement.lang||'tr').slice(0,2).toLowerCase(); return M[l]?l:'en'; }
  function T(){ return M[dil()]; }

  function oku(){ try{ var o=JSON.parse(localStorage.getItem(KEY)||'null'); if(o&&o.v&&Date.now()-o.t<YIL) return o.v; }catch(e){} return null; }
  function yaz(v){ try{ localStorage.setItem(KEY, JSON.stringify({v:v,t:Date.now()})); }catch(e){} }

  /* Consent Mode: varsayılan "reddedildi", sayfanın gtag('config') satırından önce */
  if (GA) {
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function(){ dataLayer.push(arguments); };
    var izin = oku() === 'kabul' ? 'granted' : 'denied';
    gtag('consent', 'default', {analytics_storage: izin, ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', wait_for_update: 500});
    var gs = document.createElement('script'); gs.async = true;
    gs.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA);
    document.head.appendChild(gs);
  }
  function gaIzin(v){ if (GA && window.gtag) gtag('consent', 'update', {analytics_storage: v ? 'granted' : 'denied'}); }
  function gaSil(){
    document.cookie.split(';').forEach(function(c){
      var ad = c.split('=')[0].trim(); if (!/^_ga|^_gid$|^_gat/.test(ad)) return;
      var h = location.hostname.replace(/^www\./,'');
      ['', 'domain='+h+';', 'domain=.'+h+';'].forEach(function(d){
        document.cookie = ad + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;' + d;
      });
    });
  }

  var serit = null;
  function css(){
    if (document.getElementById('cerezCss')) return;
    var st = document.createElement('style'); st.id = 'cerezCss';
    st.textContent =
      '.cerez{position:fixed;left:10px;right:10px;bottom:10px;z-index:2147483000;max-width:460px;margin:0 auto;box-sizing:border-box;' +
      'display:flex;align-items:center;gap:10px;padding:8px 8px 8px 14px;border-radius:14px;background:rgba(14,22,38,.92);color:#e6ebf3;' +
      '-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);box-shadow:0 10px 26px -10px rgba(0,0,0,.5),0 0 0 1px rgba(255,255,255,.07);' +
      'font:400 12px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;transform:translateY(140%);opacity:0;transition:transform .4s cubic-bezier(.2,.8,.2,1),opacity .3s}' +
      '.cerez.ac{transform:none;opacity:1}' +
      '.cerez p{margin:0;flex:1;min-width:0;text-align:start}' +
      '.cerez a{color:#9cc4ff;text-decoration:underline;text-underline-offset:2px;white-space:nowrap}' +
      '.cerez .cb{display:flex;gap:6px;flex:none}' +
      '.cerez button{height:32px;padding:0 12px;border-radius:9px;font:600 12px/1 inherit;font-family:inherit;cursor:pointer;border:0;white-space:nowrap}' +
      '.cerez .red{background:transparent;color:#e6ebf3;box-shadow:inset 0 0 0 1px rgba(255,255,255,.25)}' +
      '.cerez .kabul{background:#fff;color:#0e1626}' +
      '.cerez button:focus-visible{outline:2px solid #9cc4ff;outline-offset:2px}' +
      '@media(min-width:700px){.cerez{left:20px;right:auto;bottom:20px;margin:0;width:auto;max-width:520px}}' +
      '@media(prefers-reduced-motion:reduce){.cerez{transition:none}}' +
      '.cerez-ayar{color:inherit;text-decoration:underline;text-underline-offset:2px;cursor:pointer}';
    document.head.appendChild(st);
  }
  function metin(){
    if (!serit) return; var t = T();
    serit.setAttribute('dir', dil()==='fa' ? 'rtl' : 'ltr');
    serit.setAttribute('aria-label', t.ayar);
    serit.querySelector('p').innerHTML = (GA ? t.ga : t.yok) + ' <a href="' + POL + (POL.indexOf('?')<0 ? '?lang=' : '&lang=') + dil() + '">' + t.pol + '</a>';
    serit.querySelector('.red').textContent = t.red;
    serit.querySelector('.kabul').textContent = t.kabul;
  }
  function goster(){
    css();
    if (!serit) {
      serit = document.createElement('div'); serit.className = 'cerez'; serit.setAttribute('role','dialog');
      serit.innerHTML = '<p></p><div class="cb"><button type="button" class="red"></button><button type="button" class="kabul"></button></div>';
      serit.querySelector('.red').onclick = function(){ yaz('red'); gaIzin(false); gaSil(); kapat(); };
      serit.querySelector('.kabul').onclick = function(){ yaz('kabul'); gaIzin(true); kapat(); };
      document.body.appendChild(serit);
      /* Telefonda WhatsApp düğmesinin üstünü kapatmasın */
      var wa = document.querySelector('.wa-fab');
      if (wa && innerWidth < 700) { var r = wa.getBoundingClientRect(); if (r.height) serit.style.bottom = (innerHeight - r.top + 8) + 'px'; }
    }
    metin();
    requestAnimationFrame(function(){ requestAnimationFrame(function(){ serit.classList.add('ac'); }); });
  }
  function kapat(){ if (serit) serit.classList.remove('ac'); }
  window.cerezTercihleri = goster;

  /* Telif satırının sonuna "Çerez tercihleri" bağlantısı */
  function ayarLinki(){
    var yer = document.getElementById('telifSatiri') || document.querySelector('footer .telif');
    if (!yer || document.querySelector('.cerez-ayar')) return;
    var a = document.createElement('a'); a.className = 'cerez-ayar'; a.href = '#'; a.textContent = T().ayar;
    a.onclick = function(e){ e.preventDefault(); goster(); };
    /* Çok dilli sayfada telif metni dil değişince yeniden yazılıyor; bağlantıyı yanına koy */
    if (yer.id === 'telifSatiri') { yer.appendChild(document.createTextNode(' · ')); yer.appendChild(a); }
    else { var k = document.createElement('span'); k.className = yer.className; k.appendChild(a); yer.parentNode.insertBefore(k, yer.nextSibling); }
  }

  function basla(){
    css();
    var s = oku();
    if (!s) goster();
    ayarLinki(); setTimeout(ayarLinki, 600);
    /* Kıbrıs sayfasında dil değişince metni güncelle */
    if (window.MutationObserver) new MutationObserver(function(){
      metin(); var a = document.querySelector('.cerez-ayar'); if (a) a.textContent = T().ayar;
    }).observe(document.documentElement, {attributes:true, attributeFilter:['lang']});
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', basla); else basla();
})();
