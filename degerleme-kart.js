/* Değerleme formu gönderildikten sonra açılan kart: girilen bilgilerin özeti,
   fiyat-araligi.json'dan TAHMİNİ min–max aralık ve "danışman sizi arasın mı?" onayı.
   Talep form gönderilirken zaten bize düşer; onay/ret ayrıca not olarak iletilir.
   Kullanım: degerlemeKart(formData, 'satilik' | 'kiralik') */
(function(){
  var FORMSPREE = 'https://formspree.io/f/mdajqbgo';
  var tablo = null;
  fetch('fiyat-araligi.json?t=' + Date.now(), {cache:'no-store'})
    .then(function(r){ return r.json(); }).then(function(j){ tablo = j; }).catch(function(){});

  function yuvarla(x, adim){ return Math.round(x / adim) * adim; }
  function tl(x){ return x.toLocaleString('tr-TR') + ' ₺'; }
  function sayi(s){ var m = String(s || '').replace(',', '.').match(/\d+(\.\d+)?/); return m ? parseFloat(m[0]) : 0; }

  function aralik(data, tur){
    if(!tablo) return null;
    var site = data.get('site') || '';
    var g = tablo.gruplar[tablo.siteler[site] || 'diger'];
    var birim = g && g[tur === 'kiralik' ? 'kira' : 'satis'];
    if(!birim) return null;
    var m2 = sayi(data.get('brut_m2'));
    var tahmini = false;
    if(!(m2 >= 25 && m2 <= 1000)){ m2 = tablo.ortalama_m2[data.get('oda_sayisi')] || 100; tahmini = true; }
    var adim = tur === 'kiralik' ? 1000 : 250000;
    return { min: yuvarla(birim[0] * m2, adim), max: yuvarla(birim[1] * m2, adim), m2Tahmini: tahmini };
  }

  function el(id){ return document.getElementById(id); }
  function bilgiNot(data, tur, cevap){
    var f = new FormData();
    f.append('_subject', 'Değerleme arama onayı: ' + cevap + ' · ' + (data.get('ad_soyad') || ''));
    f.append('ad_soyad', data.get('ad_soyad') || '');
    f.append('telefon', data.get('telefon') || '');
    f.append('tur', tur);
    f.append('arama_onayi', cevap);
    f.append('nobetci', (window.NOBETCI_AD || ''));
    fetch(FORMSPREE, {method:'POST', headers:{'Accept':'application/json'}, body:f}).catch(function(){});
  }

  window.degerlemeKart = function(data, tur){
    var ozet = [data.get('site'), data.get('etap'), data.get('oda_sayisi'),
                sayi(data.get('brut_m2')) ? sayi(data.get('brut_m2')) + ' m²' : '', data.get('kat')]
               .filter(function(x){ return x && x !== 'Diğer (listede yok)'; });
    var ul = el('dkOzet'); ul.innerHTML = '';
    ozet.forEach(function(t){ var li = document.createElement('li'); li.textContent = t; ul.appendChild(li); });

    var a = aralik(data, tur);
    if(a){
      el('dkMin').textContent = tl(a.min);
      el('dkMax').textContent = tl(a.max);
      el('dkM2Not').hidden = !a.m2Tahmini;
      el('dkAralik').hidden = false;
    } else el('dkAralik').hidden = true;

    function bitir(cevap, kutu){
      el('dkSoru').hidden = true;
      el(kutu).hidden = false;
      bilgiNot(data, tur, cevap);
    }
    el('dkEvet').onclick = function(){ bitir('Evet, arasın', 'dkEvetSonuc'); };
    el('dkHayir').onclick = function(){ bitir('Şimdi değil', 'dkHayirSonuc'); };
  };
})();
