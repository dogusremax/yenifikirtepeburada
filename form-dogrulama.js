/**
 * yenifikirtepeburada.com — Form telefon doğrulama (SMS ya da WhatsApp kodu ile)
 *
 * Müşteri formu gönderince sayfada kod kartı açılır. 4 haneli kod WhatsApp'tan
 * gelir: kod şablonu onaylıysa servis doğrudan yollar; değilse müşteri
 * "WhatsApp'tan kodumu al" düğmesiyle 15 15'e hazır mesajı gönderir, kod aynı
 * sohbetten döner. Kod doğru girilince talep danışmana
 * gider ve "Talebiniz alındı" ekranı açılır.
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
  var TEKRAR_SN = 60;   // "Kodu tekrar gönder" bu kadar saniye sonra açılır

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
      '.fd-kart p{color:var(--gray,#6b7280);font-size:.96rem;line-height:1.55;margin:0 0 20px}' +
      '.fd-kart p b{color:var(--ink,#1a2230)}' +
      '.fd-kutular{display:flex;justify-content:center;gap:10px;margin-bottom:14px}' +
      '.fd-kutular input{width:56px;height:64px;text-align:center;font:inherit;font-size:1.8rem;font-weight:600;' +
        'color:var(--blue,#0a2a5e);border:1.5px solid var(--line,#e3e6ec);border-radius:12px;background:var(--soft,#f4f6f9);padding:0;outline:none}' +
      '.fd-kutular input:focus{border-color:var(--blue,#0a2a5e);background:#fff}' +
      '.fd-kart.hata .fd-kutular input{border-color:var(--red,#e2231a)}' +
      '.fd-mesaj{min-height:1.4em;font-size:.9rem;color:var(--red,#e2231a);margin-bottom:12px}' +
      '.fd-onay{width:100%;padding:15px;border:0;border-radius:12px;background:var(--blue,#0a2a5e);color:#fff;font:inherit;font-size:1.02rem;font-weight:600;cursor:pointer}' +
      '.fd-onay:disabled{opacity:.6;cursor:default}' +
      '.fd-alt{display:flex;flex-direction:column;align-items:center;gap:10px;margin-top:18px}' +
      '.fd-alt button{background:none;border:0;color:var(--gray,#6b7280);font:inherit;font-size:.88rem;text-decoration:underline;cursor:pointer;padding:2px}' +
      '.fd-alt button:disabled{text-decoration:none;cursor:default;opacity:.7}' +
      '.fd-wa{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:15px;margin-bottom:22px;border-radius:12px;background:#1fb855;color:#fff;font-size:1.02rem;font-weight:600;text-decoration:none}' +
      '.fd-wa:hover{background:#19a24a}' +
      '.fd-wa svg{width:22px;height:22px;fill:#fff;flex:none}';
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
      if (c && c.hata === 'sinir') { alert(c.mesaj); throw new Error('sinir'); }
      if (c && c.hata === 'numara') { alert('Lütfen telefon numaranızı 05XX XXX XX XX şeklinde yazın.'); throw new Error('numara'); }
      if (!c || (!c.ok && !c.token)) throw new Error((c && c.hata) || 'servis');
      goster(c, alanlar, o);
    }).catch(function (e) {
      var m = String(e && e.message);
      if (m === 'sinir' || m === 'numara') throw e;
      // Servise ulaşılamadı: talep eski yoldan, doğrulamasız gitsin, kaybolmasın.
      if (o.yedek) o.yedek();
      basari(o);
    });
  }

  function goster(c, alanlar, o) {
    var token = c.token;
    var tel = String(alanlar.tel || '').trim();
    var k = document.createElement('div');
    k.className = 'card fd-kart';
    k.id = 'fd-kart';
    var istek = c.yontem === 'istek';
    var sms = c.yontem === 'sms';
    var waLink = istek ? 'https://wa.me/' + c.numara + '?text=' +
      encodeURIComponent('Merhaba, onay kodumu almak istiyorum. Talep no: ' + c.istekNo) : '';
    k.innerHTML =
      '<h2>Telefonunuzu doğrulayın</h2>' +
      (istek
        ? '<p>Aşağıdaki düğmeye basın, WhatsApp açılınca hazır mesajı <b>gönderin</b>. ' +
          'Onay kodunuz WhatsApp\'tan hemen gelecek, kodu buraya yazın.</p>' +
          '<a class="fd-wa" href="' + waLink + '" target="_blank" rel="noopener">' + WA_SVG + 'WhatsApp\'tan kodumu al</a>'
        : '<p><b class="fd-tel"></b> numarasına ' + (sms ? 'SMS ile' : 'WhatsApp\'tan') + ' 4 haneli bir kod gönderdik. ' +
          'Kodu aşağıya yazın.</p>') +
      '<div class="fd-kutular">' +
        '<input inputmode="numeric" autocomplete="one-time-code" maxlength="4" aria-label="Kodun 1. hanesi">' +
        '<input inputmode="numeric" maxlength="1" aria-label="Kodun 2. hanesi">' +
        '<input inputmode="numeric" maxlength="1" aria-label="Kodun 3. hanesi">' +
        '<input inputmode="numeric" maxlength="1" aria-label="Kodun 4. hanesi">' +
      '</div>' +
      '<div class="fd-mesaj" role="alert"></div>' +
      '<button type="button" class="fd-onay">Onayla</button>' +
      '<div class="fd-alt">' +
        '<button type="button" class="fd-tekrar" disabled></button>' +
        '<button type="button" class="fd-atla">' + (sms ? 'Kod gelmedi, talebimi kodsuz gönder' : 'WhatsApp kullanmıyorum, talebimi kodsuz gönder') + '</button>' +
      '</div>';
    if (!istek) k.querySelector('.fd-tel').textContent = tel;
    o.formCard.style.display = 'none';
    o.formCard.parentNode.insertBefore(k, o.formCard.nextSibling);
    window.scrollTo({ top: 0, behavior: 'smooth' });

    var kutular = Array.prototype.slice.call(k.querySelectorAll('.fd-kutular input'));
    var mesaj = k.querySelector('.fd-mesaj');
    var onay = k.querySelector('.fd-onay');
    var tekrar = k.querySelector('.fd-tekrar');
    var atla = k.querySelector('.fd-atla');
    var bitti = false, sayac;

    function yaz(m, hata) { mesaj.textContent = m || ''; k.classList.toggle('hata', !!hata); }
    function kod() { return kutular.map(function (i) { return i.value; }).join(''); }
    function dagit(rakamlar, bas) {
      rakamlar.split('').forEach(function (r, j) { if (kutular[bas + j]) kutular[bas + j].value = r; });
      var sonraki = kutular[Math.min(bas + rakamlar.length, 3)];
      sonraki.focus();
      if (kod().length === 4) gonder();
    }
    kutular.forEach(function (inp, i) {
      inp.addEventListener('input', function () {
        var v = inp.value.replace(/\D/g, '');
        inp.value = '';
        if (v) dagit(v.slice(0, 4 - i), i);   // yapıştırma ve otomatik doldurma dahil
        yaz('');
      });
      inp.addEventListener('keydown', function (e) {
        if (e.key === 'Backspace' && !inp.value && i > 0) { kutular[i - 1].value = ''; kutular[i - 1].focus(); }
        if (e.key === 'Enter') gonder();
      });
    });
    if (!istek) setTimeout(function () { kutular[0].focus(); }, 300);

    function sayacBaslat() {
      var kalan = TEKRAR_SN;
      clearInterval(sayac);
      tekrar.disabled = true;
      function adim() {
        if (kalan <= 0) { clearInterval(sayac); tekrar.disabled = false; tekrar.textContent = 'Kod gelmedi, tekrar gönder'; return; }
        tekrar.textContent = 'Kodu tekrar gönder (' + kalan-- + ' sn)';
      }
      adim();
      sayac = setInterval(adim, 1000);
    }

    function bitir() { bitti = true; clearInterval(sayac); }

    function gonder() {
      if (bitti || onay.disabled) return;
      if (kod().length !== 4) { yaz('Lütfen 4 haneli kodu girin.', true); return; }
      onay.disabled = true;
      onay.textContent = 'Kontrol ediliyor...';
      cagir({ action: 'dogrulamaKontrol', token: token, kod: kod() }).then(function (d) {
        if (d && d.ok) { bitir(); basari(o); return; }
        onay.disabled = false;
        onay.textContent = 'Onayla';
        kutular.forEach(function (i) { i.value = ''; });
        kutular[0].focus();
        yaz((d && d.mesaj) || 'Kod hatalı, lütfen tekrar deneyin.', true);
        if (d && (d.hata === 'sure' || d.hata === 'hak')) { tekrar.disabled = false; tekrar.textContent = 'Yeni kod gönder'; }
      }).catch(function () {
        onay.disabled = false;
        onay.textContent = 'Onayla';
        yaz('Bağlantı hatası, lütfen tekrar deneyin.', true);
      });
    }
    onay.addEventListener('click', gonder);

    tekrar.addEventListener('click', function () {
      tekrar.disabled = true;
      tekrar.textContent = 'Gönderiliyor...';
      var istek = Object.assign({ action: 'dogrulamaBaslat' }, alanlar);
      if (o.deneme) istek.deneme = '1';
      cagir(istek).then(function (c2) {
        if (c2 && c2.token) token = c2.token;
        if (c2 && c2.ok) { yaz('Yeni kod gönderildi.'); sayacBaslat(); return; }
        yaz((c2 && c2.mesaj) || 'Kod gönderilemedi.', true);
        tekrar.disabled = false;
        tekrar.textContent = 'Tekrar dene';
      }).catch(function () {
        yaz('Bağlantı hatası, lütfen tekrar deneyin.', true);
        tekrar.disabled = false;
        tekrar.textContent = 'Tekrar dene';
      });
    });

    atla.addEventListener('click', function () {
      atla.disabled = true;
      atla.textContent = 'Gönderiliyor...';
      cagir({ action: 'dogrulamaAtla', token: token }).then(function (d) {
        if (d && d.ok) { bitir(); basari(o); return; }
        throw new Error('atla');
      }).catch(function () {
        bitir();
        if (o.yedek) o.yedek();
        basari(o);
      });
    });

    if (istek) tekrar.style.display = 'none';      // düğmeye tekrar basmak kodu yeniden getirir
    else if (c.ok) sayacBaslat();
    else {
      // Kod gönderilemedi (numarada WhatsApp yok ya da servis hatası)
      yaz('Bu numaraya kod gönderemedik. Numaranızı kontrol edin ya da talebinizi kodsuz gönderin.', true);
      tekrar.disabled = false;
      tekrar.textContent = 'Tekrar dene';
    }
  }

  window.FormDogrulama = { baslat: baslat };
})();
