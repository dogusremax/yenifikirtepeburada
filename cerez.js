/* Çerez onayı: alt şerit (Kabul et / Reddet). Ölçüm çerezleri (Google Analytics)
   yalnızca "Kabul et" seçilirse yüklenir. Seçim 12 ay hatırlanır.
   Kullanım: <script src="cerez.js" data-ga="G-XXXX" data-politika="cerez-politikasi.html" defer></script>
   data-ga yoksa sayfada ölçüm çerezi yoktur; şerit yalnızca bilgilendirir. */
(function(){
  if (window.__cerez) return; window.__cerez = 1;
  var me = document.currentScript || {getAttribute:function(){return null;}};
  var GA = me.getAttribute('data-ga') || '';
  var POL = me.getAttribute('data-politika') || 'cerez-politikasi.html';
  var KEY = 'cerezOnay', YIL = 365*864e5;

  var M = {
    tr:{ga:'Ziyaret sayısını ve hangi sayfaların ilgi gördüğünü ölçmek için Google Analytics çerezleri kullanıyoruz. Bu çerezler yalnızca onay verirseniz çalışır.',
        yok:'Bu sayfa yalnızca çalışması için gerekli kayıtları (dil seçimi, hesap tercihleri) tutar. İsteğe bağlı ölçüm çerezleri yalnızca onayınızla çalışır.',
        pol:'Çerez Politikası',kabul:'Kabul et',red:'Reddet',ayar:'Çerez tercihleri'},
    en:{ga:'We use Google Analytics cookies to measure visits and which pages are popular. They only run if you accept.',
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

  var gaYuklendi = false;
  function gaYukle(){
    if (!GA || gaYuklendi) return; gaYuklendi = true;
    window.dataLayer = window.dataLayer || [];
    if (typeof window.gtag !== 'function') {
      window.gtag = function(){ dataLayer.push(arguments); };
      gtag('js', new Date()); gtag('config', GA);
    }
    var s = document.createElement('script'); s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA);
    document.head.appendChild(s);
  }
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
      '.cerez{position:fixed;left:12px;right:12px;bottom:12px;z-index:2147483000;max-width:560px;margin:0 auto;box-sizing:border-box;' +
      'padding:14px 16px 14px;border-radius:16px;background:rgba(14,22,38,.96);color:#eef2f8;-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);' +
      'box-shadow:0 18px 40px -12px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.08);font:400 13.5px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;' +
      'transform:translateY(130%);opacity:0;transition:transform .45s cubic-bezier(.2,.8,.2,1),opacity .3s}' +
      '.cerez.ac{transform:none;opacity:1}' +
      '.cerez p{margin:0 0 12px;text-align:start}' +
      '.cerez a{color:#9cc4ff;text-decoration:underline;text-underline-offset:2px}' +
      '.cerez .cb{display:flex;gap:10px}' +
      '.cerez button{flex:1;min-height:44px;border-radius:11px;font:600 14.5px/1 inherit;font-family:inherit;cursor:pointer;border:0}' +
      '.cerez .red{background:rgba(255,255,255,.1);color:#fff;box-shadow:inset 0 0 0 1px rgba(255,255,255,.22)}' +
      '.cerez .kabul{background:#fff;color:#0e1626}' +
      '.cerez button:focus-visible{outline:2px solid #9cc4ff;outline-offset:2px}' +
      '@media(min-width:700px){.cerez{left:50%;right:auto;width:640px;margin:0;transform:translate(-50%,130%);bottom:20px;display:flex;align-items:center;gap:16px}' +
      '.cerez.ac{transform:translate(-50%,0)}.cerez p{margin:0;flex:1}.cerez .cb{flex:none}.cerez button{min-width:104px;flex:none}}' +
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
      serit.querySelector('.red').onclick = function(){ yaz('red'); gaSil(); kapat(); };
      serit.querySelector('.kabul').onclick = function(){ yaz('kabul'); gaYukle(); kapat(); };
      document.body.appendChild(serit);
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
    if (s === 'kabul') gaYukle(); else if (!s) goster();
    ayarLinki(); setTimeout(ayarLinki, 600);
    /* Kıbrıs sayfasında dil değişince metni güncelle */
    if (window.MutationObserver) new MutationObserver(function(){
      metin(); var a = document.querySelector('.cerez-ayar'); if (a) a.textContent = T().ayar;
    }).observe(document.documentElement, {attributes:true, attributeFilter:['lang']});
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', basla); else basla();
})();
