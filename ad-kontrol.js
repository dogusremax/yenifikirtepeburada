/* Ad Soyad kontrolü: formda "A K" gibi baş harf yazılmasın, en az iki kelime ve
   ad ile soyadın her biri en az 2 harf olsun. Uyarı sayfanın diline göre (dil.js, 6 dil).
   2026-10-21: bir müşteri formda yalnız "A K" yazdı, danışmana isimsiz talep düştü.
   <script src="ad-kontrol.js" defer></script> */
(function(){
  if (window.__adKontrol) return; window.__adKontrol = 1;
  var MESAJ = {
    tr: 'Size isminizle hitap edebilmemiz için lütfen adınızı ve soyadınızı tam yazın (örn. Ayşe Yılmaz).',
    en: 'So we can address you properly, please enter your full first and last name (e.g. Jane Smith).',
    ru: 'Чтобы мы могли обращаться к вам по имени, пожалуйста, укажите имя и фамилию полностью (например, Анна Иванова).',
    fa: 'لطفاً نام و نام خانوادگی خود را کامل بنویسید تا بتوانیم شما را با نامتان خطاب کنیم (مثلاً سارا احمدی).',
    de: 'Damit wir Sie persönlich ansprechen können, geben Sie bitte Ihren vollständigen Vor- und Nachnamen ein (z. B. Anna Schmidt).',
    pl: 'Abyśmy mogli zwracać się do Pana/Pani po imieniu, prosimy wpisać pełne imię i nazwisko (np. Anna Kowalska).'
  };
  var HARF;
  try { HARF = new RegExp('\\p{L}', 'gu'); } catch (e) { HARF = /[A-Za-zÀ-ɏͰ-ϿЀ-ӿ؀-ۿ]/g; }

  function harfSay(k){ return (k.match(HARF) || []).length; }
  function gecerli(v){
    var s = String(v || '').trim();
    if (!s || /\d/.test(s)) return false;
    var k = s.split(/\s+/).filter(function(x){ return harfSay(x) > 0; });
    // ad ve soyad (ilk ve son kelime) en az 2 harf; ortadaki baş harfe (Mehmet A. Yılmaz) izin var
    return k.length >= 2 && harfSay(k[0]) >= 2 && harfSay(k[k.length - 1]) >= 2;
  }
  function mesaj(){
    var l = String(document.documentElement.lang || 'tr').slice(0, 2).toLowerCase();
    return MESAJ[l] || MESAJ.tr;
  }

  function bagla(inp){
    var uyari = document.createElement('div');
    uyari.className = 'ad-uyari';
    uyari.setAttribute('data-dil-yok', '');
    uyari.setAttribute('role', 'alert');
    uyari.hidden = true;
    inp.insertAdjacentElement('afterend', uyari);
    var dokundu = false;

    function kontrol(goster){
      var ok = !inp.value.trim() || gecerli(inp.value);   // boşsa "required" kendi uyarısını verir
      inp.setCustomValidity(ok ? '' : mesaj());
      if (goster || dokundu) {
        uyari.textContent = ok ? '' : mesaj();
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
    document.querySelectorAll('input[name="ad_soyad"]').forEach(bagla);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', basla);
  else basla();
})();
