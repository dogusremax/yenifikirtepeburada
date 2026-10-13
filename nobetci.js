/* Bugünün nöbetçi danışmanı (değerleme formlarının teşekkür ekranı için).
   Kaynak sırası ana sayfadakiyle aynı: nobet-bugun.json (her gece takvimden yazılır),
   olmazsa nöbet uygulamasından canlı okuma. Ofis nöbeti günü ya da bilgi yoksa kart gizli kalır.
   Kullanım: <div id="nobetciKart" class="nobetci" hidden>…</div> + <script src="nobetci.js" defer></script> */
(function(){
  var FOTO = {
    "Gamze Yetkin":      "1qQjf0VhmCwLywOD9yBsMguPlCMt7wJr9",
    "Gizem Gök":         "1ppuPVDhFcBZyY4QDBMHgL7acTy6SAQdR",
    "İrem Aleyna Tetik": "1K6kJuM3AnValMiy41pLuqN66WQmDXLjT",
    "Orhan Özazman":     "1JNN6eHt1Vy4YR-_taSkZxSQ7jrhDaxge",
    "Evşen Özazman":     "1-J0do4DhzN_AGC0PU1hi-fu-YPIvr9AE",
    "Özlem Varol":       "1ZcDqNhYVBJlARSUk46APolmWsyZLMexe",
    "Ayşegül Alpay":     "1OWki4Z752FukK9Yk2io9R4zVwdhovd8q"
  };
  var CANLI = 'https://script.google.com/macros/s/AKfycbzDMpgNZAhXFZfCbp3iuUxNAJwjq8pB2xt86eluuj2JPNU-J2sfeCHUsG1m0OrJjo7RvA/exec?action=today';

  var t = new Date();
  var key = t.getFullYear() + '-' + ('0'+(t.getMonth()+1)).slice(-2) + '-' + ('0'+t.getDate()).slice(-2);

  function json(r){ if(!r.ok) throw new Error(r.status); return r.json(); }
  function gecerli(j){ return j && j.date === key; }

  function ciz(name){
    var kart = document.getElementById('nobetciKart');
    if(!kart || !name || name === 'Ofis' || name === 'Ofis Nöbeti') return;
    kart.querySelector('.nobetci-ad').textContent = name;
    var av = kart.querySelector('.nobetci-foto');
    av.textContent = name.split(' ').map(function(p){ return p.charAt(0); }).join('').slice(0,2);
    if(FOTO[name]){
      var im = new Image();
      im.onload = function(){ av.textContent = ''; av.appendChild(im); };
      im.alt = name;
      im.src = 'https://drive.google.com/thumbnail?id=' + FOTO[name] + '&sz=w240';
    }
    var wa = kart.querySelector('.nobetci-wa');
    if(wa) wa.href = 'https://wa.me/902163151515?text=' +
      encodeURIComponent('Merhaba, değerleme talebim için nöbetçi danışman ' + name + ' ile görüşmek istiyorum.');
    kart.hidden = false;
  }

  function canliOku(){
    fetch(CANLI).then(json).then(function(j){ if(j && j.ok && gecerli(j)) ciz(j.name); }).catch(function(){});
  }

  function basla(){
    fetch('nobet-bugun.json?t=' + Date.now(), {cache:'no-store'})
      .then(json)
      .then(function(j){ if(gecerli(j)) ciz(j.name); else canliOku(); })
      .catch(canliOku);
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', basla); else basla();
})();
