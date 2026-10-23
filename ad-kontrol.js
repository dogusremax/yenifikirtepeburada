/* Ad Soyad kontrolü: formda "A K" gibi baş harf yazılmasın. Ad ve Soyad ayrı kutularsa her biri
   en az 2 harf; gizli ad_soyad alanına birleşik yazılır. Tek kutuda en az iki kelime, ad ve soyad 2+ harf. Uyarı sayfanın diline göre (dil.js, 6 dil).
   2026-10-21: bir müşteri formda yalnız "A K" yazdı, danışmana isimsiz talep düştü.
   <script src="ad-kontrol.js" defer></script> */
(function(){
  if (window.__adKontrol) return; window.__adKontrol = 1;
  var MESAJ = {   // [tek kutu (ad soyad), ad, soyad]
    tr: ['Lütfen adınızı ve soyadınızı eksiksiz giriniz.', 'Lütfen adınızı eksiksiz giriniz.', 'Lütfen soyadınızı eksiksiz giriniz.'],
    en: ['Please enter your full first and last name.', 'Please enter your full first name.', 'Please enter your full last name.'],
    ru: ['Пожалуйста, укажите полностью имя и фамилию.', 'Пожалуйста, укажите имя полностью.', 'Пожалуйста, укажите фамилию полностью.'],
    fa: ['لطفاً نام و نام خانوادگی خود را به‌طور کامل وارد کنید.', 'لطفاً نام خود را به‌طور کامل وارد کنید.', 'لطفاً نام خانوادگی خود را به‌طور کامل وارد کنید.'],
    de: ['Bitte geben Sie Ihren vollständigen Vor- und Nachnamen ein.', 'Bitte geben Sie Ihren vollständigen Vornamen ein.', 'Bitte geben Sie Ihren vollständigen Nachnamen ein.'],
    pl: ['Prosimy podać pełne imię i nazwisko.', 'Prosimy podać pełne imię.', 'Prosimy podać pełne nazwisko.']
  };
  var HARF;
  try { HARF = new RegExp('\\p{L}', 'gu'); } catch (e) { HARF = /[A-Za-zÀ-ɏͰ-ϿЀ-ӿ؀-ۿ]/g; }

  function harfSay(k){ return (k.match(HARF) || []).length; }
  function gecerli(v){          // tek kutu: en az iki kelime, ad ve soyad en az 2 harf
    var s = String(v || '').trim();
    if (!s || /\d/.test(s)) return false;
    var k = s.split(/\s+/).filter(function(x){ return harfSay(x) > 0; });
    // ad ve soyad (ilk ve son kelime) en az 2 harf; ortadaki baş harfe (Mehmet A. Yılmaz) izin var
    return k.length >= 2 && harfSay(k[0]) >= 2 && harfSay(k[k.length - 1]) >= 2;
  }
  function parcaGecerli(v){     // ayrı kutu (ad ya da soyad): en az 2 harfli bir kelime
    var s = String(v || '').trim();
    if (!s || /\d/.test(s)) return false;
    return s.split(/\s+/).some(function(x){ return harfSay(x) >= 2; });
  }
  // Baş harf büyük (23 Eki 2026, Umut): her kelimenin ilk harfi yazarken büyür; Türkçe sayfada i→İ, ı→I.
  // Yalnız ilk harf değişir, kalanına dokunulmaz; imleç yerinde kalır.
  function buyut(h){
    var l = String(document.documentElement.lang || 'tr').slice(0, 2).toLowerCase();
    if (l === 'tr' && h === 'i') return 'İ';   // tarayıcı yerel ayarına güvenmeden
    if (h === 'ı') return 'I';
    return h.toUpperCase();
  }
  function basHarf(v){
    return String(v || '').replace(/(^|[\s\-'’.])([^\s\-'’.])/g, function(m, a, h){
      var b = buyut(h); return a + (b.length === h.length ? b : h);
    });
  }
  function basHarfBagla(inp){
    function duzelt(){
      var v = inp.value, y = basHarf(v);
      if (y === v) return;
      var bas = inp.selectionStart, son = inp.selectionEnd;
      inp.value = y;
      try { if (document.activeElement === inp) inp.setSelectionRange(bas, son); } catch (e) {}
    }
    inp.addEventListener('input', duzelt);
    inp.addEventListener('change', duzelt);
    inp.__basHarf = duzelt;
    inp.setAttribute('autocapitalize', 'words');
    duzelt();
  }
  function mesaj(i){
    var l = String(document.documentElement.lang || 'tr').slice(0, 2).toLowerCase();
    return (MESAJ[l] || MESAJ.tr)[i];
  }

  function bagla(inp, kural, i){
    var uyari = document.createElement('div');
    uyari.className = 'ad-uyari';
    uyari.setAttribute('data-dil-yok', '');
    uyari.setAttribute('role', 'alert');
    uyari.hidden = true;
    inp.insertAdjacentElement('afterend', uyari);
    var dokundu = false;

    function kontrol(goster){
      var ok = !inp.value.trim() || kural(inp.value);   // boşsa "required" kendi uyarısını verir
      inp.setCustomValidity(ok ? '' : mesaj(i));
      if (goster || dokundu) {
        uyari.textContent = ok ? '' : mesaj(i);
        uyari.hidden = ok;
        inp.classList.toggle('ad-hatali', !ok);
      }
      return ok;
    }
    inp.addEventListener('input', function(){ kontrol(false); });
    inp.addEventListener('blur', function(){ if (inp.value.trim()) dokundu = true; kontrol(false); });
    inp.addEventListener('invalid', function(){ dokundu = true; kontrol(true); });
    kontrol(false);
  }

  function basla(){
    var st = document.createElement('style');
    st.textContent = '.ad-uyari{color:#C62828;font-size:.85rem;line-height:1.35;margin-top:6px}' +
      'input.ad-hatali{border-color:#C62828!important}';
    document.head.appendChild(st);
    document.querySelectorAll('form').forEach(function(f){
      var tam = f.querySelector('input[name="ad_soyad"]');
      var ad = f.querySelector('input[name="ad"]'), soyad = f.querySelector('input[name="soyad"]');
      [ad, soyad, tam].forEach(function(x){ if (x && x.type !== 'hidden') basHarfBagla(x); });
      if (ad && soyad) {
        // Ad ve Soyad ayrı kutu (21 Eki 2026, Umut); servis ve Formspree için ad_soyad (gizli) birleşik gider
        bagla(ad, parcaGecerli, 1); bagla(soyad, parcaGecerli, 2);
        var birlestir = function(){ if (ad.__basHarf) { ad.__basHarf(); soyad.__basHarf(); } if (tam) tam.value = (ad.value.trim() + ' ' + soyad.value.trim()).trim(); };
        ad.addEventListener('input', birlestir); soyad.addEventListener('input', birlestir);
        f.addEventListener('submit', birlestir, true);
        birlestir();
      } else if (tam && tam.type !== 'hidden') bagla(tam, gecerli, 0);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', basla);
  else basla();
})();
