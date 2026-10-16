/**
 * yenifikirtepeburada.com — Form telefon doğrulama (WhatsApp ile, ücretsiz)
 *
 * Müşteri formu gönderince 4 haneli bir onay kodu alınır ve "WhatsApp ile
 * onayla" düğmesi çıkar. Düğme WhatsApp'ı 0216 315 15 15'e kod yazılı olarak
 * açar; müşteri Gönder'e basınca ofis servisi numarayı doğrulamış olur, talep
 * danışmana o zaman gider ve ekranda "Talebiniz ulaştı" açılır.
 * Servis: dogusremax/apps-script → dogus-whatsapp-service/Dogrulama.js
 *
 * Kullanım:
 *   FormDogrulama.baslat(params, {
 *     formCard: el, successCard: el, deneme: false,
 *     yedek: function () { ... eski talepBildir gönderimi ... }  // servis cevap vermezse
 *   });
 */
(function () {
  var GAS_URL = 'https://script.google.com/macros/s/AKfycbwqxxXftJ_b1TrF_GFYfus6dtBe6lp4gDWTZVl9QuXAjYxjHfSvl2Ni_X3mJKm6zAss_w/exec';
  var SORGU_MS = 3000;
  var SURE_MS = 30 * 60 * 1000;

  function cagir(alanlar) {
    var p = new URLSearchParams();
    Object.keys(alanlar).forEach(function (k) { p.append(k, alanlar[k] == null ? '' : alanlar[k]); });
    return fetch(GAS_URL, { method: 'POST', body: p }).then(function (r) { return r.json(); });
  }

  function stilEkle() {
    if (document.getElementById('fd-stil')) return;
    var s = document.createElement('style');
    s.id = 'fd-stil';
    s.textContent =
      '.fd-kart{text-align:center}' +
      '.fd-kart h2{color:var(--blue,#0a2a5e);font-size:1.35rem;font-weight:600;margin-bottom:10px}' +
      '.fd-kart p{color:var(--gray,#6b7280);font-size:.96rem;line-height:1.55;margin:0 0 18px}' +
      '.fd-kod{display:inline-block;font-size:2rem;font-weight:700;letter-spacing:.35em;padding:8px 10px 8px 18px;border:1.5px dashed #c9d2e3;border-radius:10px;color:var(--blue,#0a2a5e);margin-bottom:20px}' +
      '.fd-wa{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:16px;border-radius:12px;background:#1fb855;color:#fff;font-size:1.05rem;font-weight:600;text-decoration:none;box-shadow:0 10px 24px -10px rgba(18,140,126,.7)}' +
      '.fd-wa:hover{background:#19a24a}' +
      '.fd-wa svg{width:24px;height:24px;fill:#fff;flex:none}' +
      '.fd-durum{display:flex;align-items:center;justify-content:center;gap:10px;margin-top:18px;font-size:.92rem;color:var(--gray,#6b7280)}' +
      '.fd-donen{width:16px;height:16px;border-radius:50%;border:2px solid #c9d2e3;border-top-color:#1fb855;animation:fdDon 1s linear infinite}' +
      '@keyframes fdDon{to{transform:rotate(360deg)}}' +
      '.fd-atla{display:inline-block;margin-top:22px;background:none;border:0;color:var(--gray,#6b7280);font:inherit;font-size:.86rem;text-decoration:underline;cursor:pointer}' +
      '@media(prefers-reduced-motion:reduce){.fd-donen{animation:none}}';
    document.head.appendChild(s);
  }

  var WA_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.64.07-.3-.15-1.26-.46-2.39-1.47-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.61-.92-2.21-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.08c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.63.71.23 1.36.2 1.87.12.57-.09 1.76-.72 2.01-1.41.25-.69.25-1.29.17-1.41-.07-.12-.27-.2-.57-.35zM12.04 21.5a9.43 9.43 0 0 1-4.8-1.32l-.35-.21-3.57.94.95-3.48-.22-.36a9.4 9.4 0 0 1-1.44-5.02c0-5.2 4.23-9.43 9.44-9.43 2.52 0 4.89.98 6.67 2.77a9.37 9.37 0 0 1 2.76 6.67c0 5.2-4.24 9.44-9.43 9.44zm8.03-17.47A11.27 11.27 0 0 0 12.04.7C5.78.7.69 5.79.69 12.04c0 2 .52 3.95 1.52 5.67L.6 23.3l5.72-1.5a11.33 11.33 0 0 0 5.42 1.38c6.25 0 11.34-5.09 11.35-11.35 0-3.03-1.18-5.88-3.33-8.02z"/></svg>';

  function basari(o) {
    var k = document.getElementById('fd-kart');
    if (k) k.style.display = 'none';
    o.formCard.style.display = 'none';
    o.successCard.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function baslat(alanlar, o) {
    stilEkle();
    var istek = Object.assign({ action: 'dogrulamaBaslat' }, alanlar);
    if (o.deneme) istek.deneme = '1';

    return cagir(istek).then(function (c) {
      if (!c || !c.ok) {
        if (c && c.hata === 'sinir') { alert(c.mesaj); throw new Error('sinir'); }
        throw new Error((c && c.hata) || 'servis');
      }
      goster(c, o);
    }).catch(function (e) {
      // Servise ulaşılamadı: talep eski yoldan, doğrulamasız gitsin, kaybolmasın.
      if (String(e && e.message) === 'sinir') throw e;
      if (o.yedek) o.yedek();
      basari(o);
    });
  }

  function goster(c, o) {
    var metin = 'Merhaba, talebimi onaylıyorum. Onay kodu: ' + c.kod;
    var link = 'https://wa.me/' + c.numara + '?text=' + encodeURIComponent(metin);

    var k = document.createElement('div');
    k.className = 'card fd-kart';
    k.id = 'fd-kart';
    k.innerHTML =
      '<h2>Son adım: numaranızı onaylayın</h2>' +
      '<p>Aşağıdaki düğmeye basın. WhatsApp açılacak ve mesajınız hazır yazılı olacak, ' +
      'sadece <b>Gönder</b>\'e basmanız yeterli. Ardından bu sayfaya geri dönün.</p>' +
      '<div class="fd-kod" aria-label="Onay kodu">' + c.kod + '</div>' +
      '<a class="fd-wa" href="' + link + '" target="_blank" rel="noopener">' + WA_SVG + 'WhatsApp ile onayla</a>' +
      '<div class="fd-durum" role="status"><span class="fd-donen"></span><span>WhatsApp mesajınız bekleniyor...</span></div>' +
      '<button type="button" class="fd-atla">WhatsApp kullanmıyorum, talebimi bu şekilde gönder</button>';
    o.formCard.style.display = 'none';
    o.formCard.parentNode.insertBefore(k, o.formCard.nextSibling);
    window.scrollTo({ top: 0, behavior: 'smooth' });

    var bitti = false, bas = Date.now(), zaman;
    function bitir() { bitti = true; clearTimeout(zaman); document.removeEventListener('visibilitychange', sor); }
    function sor() {
      if (bitti) return;
      clearTimeout(zaman);
      if (Date.now() - bas > SURE_MS) {
        bitir();
        k.querySelector('.fd-durum').textContent = 'Onay süresi doldu. Lütfen formu tekrar gönderin.';
        return;
      }
      cagir({ action: 'dogrulamaDurum', token: c.token }).then(function (d) {
        if (bitti) return;
        if (d && (d.durum === 'onaylandi' || d.durum === 'atlandi')) { bitir(); basari(o); return; }
        zaman = setTimeout(sor, SORGU_MS);
      }).catch(function () { if (!bitti) zaman = setTimeout(sor, SORGU_MS * 2); });
    }
    document.addEventListener('visibilitychange', sor);   // WhatsApp'tan dönünce hemen sor
    zaman = setTimeout(sor, SORGU_MS);

    var atla = k.querySelector('.fd-atla');
    atla.addEventListener('click', function () {
      atla.disabled = true;
      atla.textContent = 'Gönderiliyor...';
      cagir({ action: 'dogrulamaAtla', token: c.token }).then(function (d) {
        if (d && d.ok) { bitir(); basari(o); return; }
        throw new Error('atla');
      }).catch(function () {
        bitir();
        if (o.yedek) o.yedek();
        basari(o);
      });
    });
  }

  window.FormDogrulama = { baslat: baslat };
})();
