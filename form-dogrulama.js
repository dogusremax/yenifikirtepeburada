/**
 * yenifikirtepeburada.com — Form telefon doğrulama (WhatsApp kodu ile)
 *
 * Müşteri formu gönderince ofis servisi numarasına WhatsApp'tan 4 haneli bir
 * kod yollar, sayfada kod kartı açılır. Kod doğru girilince talep danışmana
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
      '.fd-alt button:disabled{text-decoration:none;cursor:default;opacity:.7}';
    document.head.appendChild(s);
  }

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
    k.innerHTML =
      '<h2>Telefonunuzu doğrulayın</h2>' +
      '<p><b class="fd-tel"></b> numarasına WhatsApp\'tan 4 haneli bir kod gönderdik. ' +
      'Kodu aşağıya yazın.</p>' +
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
        '<button type="button" class="fd-atla">WhatsApp kullanmıyorum, talebimi kodsuz gönder</button>' +
      '</div>';
    k.querySelector('.fd-tel').textContent = tel;
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
    setTimeout(function () { kutular[0].focus(); }, 300);

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

    if (c.ok) sayacBaslat();
    else {
      // Kod gönderilemedi (numarada WhatsApp yok ya da servis hatası)
      yaz('Bu numaraya WhatsApp\'tan kod gönderemedik. Numaranızı kontrol edin ya da talebinizi kodsuz gönderin.', true);
      tekrar.disabled = false;
      tekrar.textContent = 'Tekrar dene';
    }
  }

  window.FormDogrulama = { baslat: baslat };
})();
