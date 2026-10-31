/**
 * yenifikirtepeburada.com — Talep formu terk ölçümü (görünmez, sayfada hiçbir şey değişmez)
 * 31 Eki: satılık değerleme formunda 17 başlayandan 2'si gönderdi; kişinin
 * hangi alanda bıraktığı görülsün diye. Alan adı olay adının içinde, böylece
 * GA'da özel boyut tanımlamadan Etkinlikler raporunda okunur:
 *   form_hata_<alan>     gönder'e bastı ama bu alan eksik/hatalı olduğu için gitmedi
 *   form_birakti_<alan>  formu doldurmaya başladı, göndermeden sayfadan çıktı; <alan> en son dokunduğu alan
 */
(function () {
  var form = document.getElementById('formCard');
  if (!form) return;
  var ad = form.getAttribute('name') || '';
  var basladi = false, gitti = false, son = '', hatalar = {};

  function olay(n, p) {
    try { if (typeof gtag === 'function') gtag('event', n.slice(0, 40), Object.assign({ form_name: ad, transport_type: 'beacon' }, p || {})); } catch (e) {}
  }
  function alanAdi(el) { return (el && (el.name || el.id) || 'bilinmiyor').replace(/[^a-z0-9_]/gi, '_').toLowerCase(); }
  function dolu() {
    var n = 0;
    form.querySelectorAll('input:not([type=hidden]),select,textarea').forEach(function (el) {
      if (!el.name || el.name === 'bot-field') return;
      if ((el.type === 'checkbox' || el.type === 'radio') ? el.checked : el.value) n++;
    });
    return n;
  }

  ['focusin', 'change'].forEach(function (t) {
    form.addEventListener(t, function (e) {
      var el = e.target;
      if (!el || !el.name || el.type === 'hidden' || el.name === 'bot-field') return;
      basladi = true;
      son = alanAdi(el);
    });
  });

  // Tarayıcı zorunlu alanı geçirmediğinde (gönder'e basıldı, form gitmedi)
  form.addEventListener('invalid', function (e) {
    var a = alanAdi(e.target);
    if (hatalar[a]) return;
    hatalar[a] = 1;
    olay('form_hata_' + a, { dolu_alan: dolu() });
  }, true);

  form.addEventListener('submit', function () { gitti = true; }, true);

  function cikis() {
    if (!basladi || gitti) return;
    gitti = true; // bir kez
    olay('form_birakti_' + (son || 'bilinmiyor'), { dolu_alan: dolu() });
  }
  document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'hidden') cikis(); });
  window.addEventListener('pagehide', cikis);
})();
