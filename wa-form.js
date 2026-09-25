/**
 * yenifikirtepeburada.com — Form → WhatsApp (0216 315 15 15) bağlantısı
 *
 * Kullanım: form bulunan 4 sayfanın </body> etiketinden hemen önce:
 *   <script src="wa-form.js" defer></script>
 *
 * Mevcut Formspree gönderimine dokunmaz. Gönder butonunun altına WhatsApp
 * bilgilendirme notu ekler; form gönderildiği anda aynı bilgileri
 * "dogus-gelen-kutusu" Apps Script'ine iletir ve 15 15'ten şablon mesaj gider.
 */
(function () {
  var GAS_URL = 'BURAYA_GELEN_KUTUSU_EXEC_ADRESI';

  var yol = location.pathname;
  var TALEP =
    /almak-istiyorum/.test(yol)     ? 'satın alma' :
    /kiralamak-istiyorum/.test(yol) ? 'kiralama' :
    /satilik-deger/.test(yol)       ? 'satılık değerleme' :
    /kiralik-deger/.test(yol)       ? 'kiralık değerleme' : '';

  // Sadece 4 ana formda çalışır; İletişim ve Kariyer formları mail ile devam eder.
  if (!TALEP) return;

  function etiketMetni(el) {
    var t = '';
    var grup = el.closest('.group');                       // sitedeki yapı: .group > label + alan
    var gl = grup && grup.querySelector('label:not(.radiobtn)');
    if (gl && !gl.contains(el)) t = gl.textContent;
    if (!t && el.id) {
      var l = document.querySelector('label[for="' + el.id + '"]');
      if (l) t = l.textContent;
    }
    if (!t && el.closest('label')) t = el.closest('label').textContent;
    if (!t) {
      var onceki = el.previousElementSibling;
      if (onceki && /LABEL|SPAN|P|DIV/.test(onceki.tagName)) t = onceki.textContent;
    }
    return (t || el.getAttribute('placeholder') || el.name || '').replace(/\s+/g, ' ').trim();
  }

  function telAlani(f) {
    return f.querySelector('input[type="tel"]') ||
      Array.prototype.find.call(f.querySelectorAll('input'), function (i) {
        return /tel|phone|gsm|cep/i.test(i.name + ' ' + i.id + ' ' + etiketMetni(i));
      });
  }

  function adAlani(f) {
    return Array.prototype.find.call(f.querySelectorAll('input[type="text"], input:not([type])'), function (i) {
      return /ad\s*soyad|adsoyad|ad_soyad|isim|full.?name|^name$|^ad$/i.test(i.name + ' ' + i.id + ' ' + etiketMetni(i));
    });
  }

  // Onay kutusu yok: gönder butonunun altına bilgilendirme notu eklenir.
  // Formu gönderen kişi bu notu görerek WhatsApp bilgilendirmesini kabul etmiş olur.
  function bilgiNotu(f) {
    var not = document.createElement('p');
    not.className = 'wa-bilgi';
    not.style.cssText = 'margin:10px 0 0;font-size:12.5px;line-height:1.45;color:#64748b;text-align:center';
    not.innerHTML = 'Talebinizi gönderdiğinizde, talebinizle ilgili bilgilendirme ' +
      '<b>RE/MAX Doğuş WhatsApp hattından (0216 315 15 15)</b> size iletilir.';
    var btn = f.querySelector('button[type="submit"], input[type="submit"]') ||
              Array.prototype.find.call(f.querySelectorAll('button'), function (b) { return b.type !== 'button'; });
    if (btn && btn.parentNode) btn.parentNode.insertBefore(not, btn.nextSibling);
    else f.appendChild(not);
  }

  function gonder(veri) {
    var govde = JSON.stringify(veri);
    try {
      if (navigator.sendBeacon && navigator.sendBeacon(GAS_URL, new Blob([govde], { type: 'text/plain;charset=UTF-8' }))) return;
    } catch (e) {}
    try {
      fetch(GAS_URL, { method: 'POST', mode: 'no-cors', keepalive: true, body: govde });
    } catch (e) {}
  }

  function bagla(f) {
    var tel = telAlani(f);
    if (!tel || f.dataset.waBagli) return;
    f.dataset.waBagli = '1';
    var ad = adAlani(f);
    bilgiNotu(f);
    var gonderildi = false;

    f.addEventListener('submit', function () {
      if (gonderildi) return;
      if (f.checkValidity && !f.checkValidity()) return;
      gonderildi = true;
      setTimeout(function () { gonderildi = false; }, 8000);

      var bot = '', detay = [];
      Array.prototype.forEach.call(f.elements, function (el) {
        if (!el.name || el.type === 'submit' || el.type === 'button') return;
        if (el.type === 'hidden') return;                  // form-name, _subject
        if (/_gotcha|honeypot|bot/i.test(el.name)) { bot = bot || el.value; return; }
        if (el === tel || el === ad) return;
        if ((el.type === 'radio' || el.type === 'checkbox') && !el.checked) return;
        var v = (el.value || '').trim();
        if (!v) return;
        detay.push(etiketMetni(el).replace(/\(opsiyonel\)/i, '').trim() + ': ' + v);
      });

      gonder({
        action: 'form',
        talep: TALEP,
        ad: ad ? ad.value.trim() : '',
        telefon: tel.value.trim(),
        onay: true,   // form altındaki bilgilendirme notu ile
        detay: detay.join('\n'),
        sayfa: location.href,
        bot: bot
      });
    }, true);
  }

  function basla() {
    Array.prototype.forEach.call(document.querySelectorAll('form'), bagla);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', basla);
  else basla();
})();
