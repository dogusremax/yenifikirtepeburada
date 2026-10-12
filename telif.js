/* Telif uyarısı: her sayfanın en altına kısa bir satır ekler. */
(function(){
  if (document.getElementById('telifSatiri')) return;
  var yil = new Date().getFullYear();
  var st = document.createElement('style');
  st.textContent =
    '.telif{max-width:900px;margin:0 auto;padding:22px 16px 92px;text-align:center;font:400 11.5px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif;color:inherit;opacity:.62;position:relative;z-index:2}' +
    '.telif b{font-weight:600}' +
    '@media(min-width:700px){.telif{padding-bottom:28px}}';
  document.head.appendChild(st);
  var d = document.createElement('div');
  d.id = 'telifSatiri';
  d.className = 'telif';
  d.setAttribute('role', 'contentinfo');
  d.innerHTML = '© ' + yil + ' <b>UMT Group Gayrimenkul Yatırım Danışmanlık</b>. Tüm hakları saklıdır. ' +
    'Bu sitedeki tasarım, yazılım, metinler ve derlenen veriler izinsiz kopyalanamaz, çoğaltılamaz ve başka yerde kullanılamaz. ' +
    'Proje görselleri ve VR görüntüleri ilgili sahiplerine aittir.';
  document.body.appendChild(d);
})();
