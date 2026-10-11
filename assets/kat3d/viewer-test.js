/* Fotogerçekçi 3D kat planı görüntüleyici: önceden render edilmiş 360° kareler ve kuş bakışı.
   Kullanım: var v = Kat3D.create(kutu); v.show('11-c1', 'spin' | 'top'); v.hide();  */
(function () {
  var K = window.KAT3D || {};
  // Oda adları ve net alanlar (resmi satış planlarından)
  var ROOMS = {
    '11-c1': [['sal', 'Salon', 28.42], ['mut', 'Mutfak', 9.94], ['eb', 'Ebeveyn Y. Odası', 13.84], ['o1', 'Oda 1', 10.10], ['o2', 'Oda 2', 10.29],
      ['eba', 'Ebeveyn Banyo', 4.29], ['ba', 'Banyo', 4.46], ['gh', 'Giriş Holü', 6.28], ['kor', 'Koridor', 5.35], ['cn', 'Çamaşır Nişi', 1.65], ['blk', 'Balkon', 7.45]],
    '11-y1': [['sal', 'Salon + Mutfak', 23.82], ['eb', 'Ebeveyn Y. Odası', 14.44], ['o', 'Oda', 9.42], ['ba', 'Banyo', 4.02], ['eba', 'Ebeveyn Banyo', 3.07],
      ['gh', 'Giriş Holü', 3.75], ['kor', 'Koridor', 4.10], ['blk', 'Balkon', 3.64]]
  };
  function rooms(pid) { return (K[pid] && K[pid].rooms) || ROOMS[pid] || []; }
  var NS = 'http://www.w3.org/2000/svg';
  var css = '.k3d{position:relative;width:100%;height:100%;overflow:hidden;background:linear-gradient(180deg,#f7f8fc,#e9edf6);border-radius:14px;font-family:"Plus Jakarta Sans","Archivo",sans-serif;user-select:none;-webkit-user-select:none}' +
    '.k3d .sp,.k3d .tp{position:absolute;inset:0;display:none}' +
    '.k3d .sp{cursor:grab;touch-action:pan-y}.k3d .sp:active{cursor:grabbing}' +
    '.k3d canvas{position:absolute;inset:0;width:100%;height:100%;display:block}' +
    '.k3d .lbls{position:absolute;inset:0;pointer-events:none;overflow:hidden}' +
    '.k3d .lb3{position:absolute;transform:translate(-50%,-50%);text-align:center;white-space:nowrap;font-size:.72rem;font-weight:700;color:#050A30;background:rgba(255,255,255,.9);border-radius:8px;padding:3px 8px;line-height:1.25;box-shadow:0 2px 10px rgba(5,10,48,.14);transition:opacity .25s,background .2s}' +
    '.k3d .lb3 i{display:block;font-style:normal;font-weight:600;color:#DC1C2E;font-size:.68rem}' +
    '.k3d .lb3.hl{background:#050A30;color:#fff}.k3d .lb3.hl i{color:#ffb3b9}' +
    '.k3d .tbox{position:absolute}.k3d .tbox img{position:absolute;inset:0;width:100%;height:100%;display:block}' +
    '.k3d .tbox svg{position:absolute;inset:0;width:100%;height:100%}' +
    '.k3d polygon{fill:transparent;cursor:pointer;transition:fill .2s}.k3d polygon:hover{fill:rgba(251,81,96,.12)}.k3d polygon.on{fill:rgba(251,81,96,.3)}' +
    '.k3d .ld{position:absolute;inset:0;display:none;align-items:center;justify-content:center;pointer-events:none}' +
    '.k3d .ld>div{background:rgba(255,255,255,.94);border-radius:12px;padding:10px 14px;font-size:.8rem;font-weight:600;color:#050A30;box-shadow:0 4px 18px rgba(5,10,48,.1);text-align:center}' +
    '.k3d .ldt{height:4px;width:180px;background:#e4e7f1;border-radius:4px;margin-top:8px;overflow:hidden}.k3d .ldb{height:100%;width:0;background:#DC1C2E;transition:width .2s}' +
    '.k3d .play{position:absolute;left:12px;bottom:12px;display:flex;align-items:center;gap:6px;font:inherit;font-weight:700;font-size:.8rem;border:none;background:rgba(255,255,255,.94);color:#050A30;padding:8px 12px;border-radius:10px;cursor:pointer;box-shadow:0 4px 14px rgba(5,10,48,.1)}' +
    '.k3d .play svg{width:16px;height:16px}.k3d .play.on{background:#050A30;color:#fff}' +
    '.k3d .hint{position:absolute;right:12px;bottom:14px;font-size:.75rem;color:#59607d;background:rgba(255,255,255,.85);padding:5px 10px;border-radius:8px;transition:opacity .4s;pointer-events:none}' +
    '@media(max-width:600px){.k3d .lb3{font-size:.62rem;padding:2px 6px;border-radius:6px}.k3d .lb3 i{font-size:.6rem}.k3d .hint{display:none}.k3d .play{top:12px;bottom:auto}}';
  var injected = false;
  function fmt(n) { return n.toFixed(2).replace('.', ',') + ' m²'; }
  function track(n, p) { try { if (typeof gtag === 'function') gtag('event', n, p || {}); } catch (e) {} }

  function create(host) {
    if (!injected) { var s = document.createElement('style'); s.textContent = css; document.head.appendChild(s); injected = true; }
    host.classList.add('k3d');
    host.innerHTML = '<div class="sp"><canvas></canvas><div class="lbls"></div><div class="ld"><div><span>Fotogerçekçi görüntü yükleniyor</span><div class="ldt"><div class="ldb"></div></div></div></div>' +
      '<button type="button" class="play on" aria-label="Otomatik döndür"><svg viewBox="0 0 24 24"><path d="M12 5a7 7 0 1 1-6.6 4.7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><path d="M3.5 5.5l2 4.2 4.1-1.9" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg><span>360°</span></button>' +
      '<div class="hint">Sağa sola sürükleyerek çevirin</div></div>' +
      '<div class="tp"><div class="tbox"><img alt="Kuş bakışı kat planı"><svg viewBox="0 0 1 1" preserveAspectRatio="none"></svg></div><div class="lbls"></div></div>';
    var q = function (s) { return host.querySelector(s); };
    var sp = q('.sp'), tp = q('.tp'), cv = q('canvas'), cx = cv.getContext('2d'), DPR = 1, DPR0 = Math.min(window.devicePixelRatio || 1, 2);
    var V = { pid: null, mode: null, frames: [], n: 0, p: 0, auto: true, drag: null, loaded: 0, hl: null, last: 0, on: false };

    function rect(el, iw, ih, z) {
      var W = el.clientWidth, H = el.clientHeight, s = Math.min(W / iw, H / ih) * (z && W < 600 ? z : 1), w = iw * s, h = ih * s;
      return { x: (W - w) / 2, y: (H - h) / 2, w: w, h: h, W: W };
    }
    function mkLabels(el) {
      el.innerHTML = ''; var o = {};
      rooms(V.pid).forEach(function (r) {
        var d = document.createElement('div'); d.className = 'lb3'; d.innerHTML = r[1] + '<i>' + fmt(r[2]) + '</i>'; el.appendChild(d); o[r[0]] = { el: d, m: r[2] };
      });
      return o;
    }
    function setLbl(L, pos, R) {
      var mob = R.W < 600;
      for (var k in L) {
        var p = pos && pos[k], l = L[k];
        if (!p || (mob && l.m < 5 && k !== V.hl)) { l.el.style.opacity = 0; continue; }
        l.el.style.left = (R.x + p[0] * R.w) + 'px'; l.el.style.top = (R.y + p[1] * R.h) + 'px'; l.el.classList.toggle('hl', k === V.hl);
        l.x = R.x + p[0] * R.w; l.y = R.y + p[1] * R.h; l.w = l.w || l.el.offsetWidth; l.h = l.h || l.el.offsetHeight; l.v = 1;
      }
      // üst üste binen etiketlerde küçük odanınkini gizle (seçili oda her zaman görünür)
      var ks = Object.keys(L).filter(function (k) { return L[k].v; }).sort(function (a, b) { return (b === V.hl) - (a === V.hl) || L[b].m - L[a].m; }), shown = [];
      ks.forEach(function (k) {
        var l = L[k], hit = shown.some(function (o) { return Math.abs(o.x - l.x) < (o.w + l.w) / 2 + 2 && Math.abs(o.y - l.y) < (o.h + l.h) / 2 + 2; });
        l.el.style.opacity = hit ? 0 : 1; if (!hit) shown.push(l);
      });
      for (var k2 in L) L[k2].v = 0;
    }
    function load(pid) {
      var D = K[pid]; if (!D) return false; if (V.pid === pid) return true;
      V.pid = pid; V.D = D; V.A = {}; V.n = D.n; V.S = 1; V.lab = D.labels; V.p = 0; V.auto = true; V.loaded = 0; V.frames = []; V.hl = null; q('.play').classList.add('on');
      V.L = mkLabels(sp.querySelector('.lbls')); V.TL = mkLabels(tp.querySelector('.lbls'));
      q('.ld').style.display = 'flex'; q('.ldb').style.width = '0%';
      // önce seyrek kareler: dönüş hemen başlayabilsin
      var order = []; [8, 4, 2, 1].forEach(function (s) { for (var i = 0; i < D.n; i += s) if (order.indexOf(i) < 0) order.push(i); });
      order.forEach(function (i) {
        var im = new Image(); im.decoding = 'async';
        im.onload = function () { if (V.D !== D) return; var c = soft(im); V.frames[i] = c; if (window.createImageBitmap) createImageBitmap(c).then(function (bm) { if (V.D === D) V.frames[i] = bm; }, function () {}); V.loaded++; q('.ldb').style.width = (V.loaded / D.n * 100) + '%'; if (V.loaded >= D.n) { q('.ld').style.display = 'none'; extra(D); } draw(); };
        im.src = D.dir + 'f' + (i < 10 ? '0' : '') + i + '.webp';
      });
      var ti = tp.querySelector('img'); ti.onload = drawTop; ti.src = D.dir + 'top.webp';
      var svg = tp.querySelector('svg'); svg.innerHTML = '';
      rooms(pid).forEach(function (r) {
        var pts = D.top.polys[r[0]]; if (!pts) return;
        var e = document.createElementNS(NS, 'polygon'); e.setAttribute('points', pts.map(function (a) { return a[0] + ',' + a[1]; }).join(' '));
        e.setAttribute('data-r', r[0]); svg.appendChild(e);
      });
      return true;
    }
    // ana kareler 12° arayla; aralarına önceden üretilmiş ara kareler (fNN-1, fNN-2) varsa onları da yükle: dönüş zıplamadan akar
    function extra(D) {
      var t = new Image();
      t.onload = function () {
        if (V.D !== D || V.S > 1) return;
        var S = 3, n = D.n, f = [], lab = [];
        for (var i = 0; i < n; i++) {
          f[i * S] = V.frames[i];
          for (var s = 0; s < S; s++) {
            var m = s ? mix(D.labels[i], D.labels[(i + 1) % n], s / S) : D.labels[i], o = {};
            for (var k in m) if (m[k]) o[k] = m[k];
            lab[i * S + s] = o;
          }
        }
        V.frames = f; V.lab = lab; V.A = {}; V.S = S; V.p *= S; V.n = n * S; if (V.drag) V.drag.p *= S;
        for (var j = 0; j < n; j++) for (var s2 = 1; s2 < S; s2++) (function (j, s2) {
          var im = new Image(); im.decoding = 'async';
          im.onload = function () { if (V.D !== D) return; var c = soft(im); V.frames[j * S + s2] = c; if (window.createImageBitmap) createImageBitmap(c).then(function (bm) { if (V.D === D) V.frames[j * S + s2] = bm; }, function () {}); };
          im.src = D.dir + 'f' + (j < 10 ? '0' : '') + j + '-' + s2 + '.webp';
        })(j, s2);
      };
      t.src = D.dir + 'f00-1.webp';
    }
    // karenin kenarlarını görüntünün kendisinde yumuşat: bükülen karenin sınırı ve kesilen gölge görünmesin
    function soft(im) {
      var w = im.naturalWidth, h = im.naturalHeight, c = document.createElement('canvas'); c.width = w; c.height = h;
      var g = c.getContext('2d'); g.drawImage(im, 0, 0); g.globalCompositeOperation = 'destination-out';
      [[0, 0, w * 0.1, 0], [w, 0, w * 0.9, 0], [0, 0, 0, h * 0.1], [0, h, 0, h * 0.9]].forEach(function (a) {
        var gr = g.createLinearGradient(a[0], a[1], a[2], a[3]); gr.addColorStop(0, 'rgba(0,0,0,1)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
      });
      return c;
    }
    function ready(i) { return !!V.frames[i]; }
    function near(i) { if (ready(i)) return i; for (var d = 1; d < V.n; d++) { var a = (i + d) % V.n, b = (i - d + V.n) % V.n; if (ready(a)) return a; if (ready(b)) return b; } return -1; }
    // kare i'deki etiket noktalarını kare j'dekilere taşıyan 2B afin dönüşüm (en küçük kareler); zemin düzleminde neredeyse tam oturur
    function aff(i, j) {
      var key = i + '>' + j; V.A = V.A || {}; if (V.A[key] !== undefined) return V.A[key];
      var P = V.lab[i], Q = V.lab[j], S = [0, 0, 0, 0, 0, 0, 0, 0, 0], X = [0, 0, 0], Y = [0, 0, 0], c = 0;
      for (var k in P) { var p = P[k], q = Q[k]; if (!q) continue; c++;
        var r = [p[0], p[1], 1]; for (var m = 0; m < 3; m++) { X[m] += r[m] * q[0]; Y[m] += r[m] * q[1]; for (var l = 0; l < 3; l++) S[m * 3 + l] += r[m] * r[l]; } }
      var M = null;
      if (c >= 3) {
        var d = S[0] * (S[4] * S[8] - S[5] * S[7]) - S[1] * (S[3] * S[8] - S[5] * S[6]) + S[2] * (S[3] * S[7] - S[4] * S[6]);
        if (Math.abs(d) > 1e-12) {
          var inv = [S[4] * S[8] - S[5] * S[7], S[2] * S[7] - S[1] * S[8], S[1] * S[5] - S[2] * S[4], S[5] * S[6] - S[3] * S[8], S[0] * S[8] - S[2] * S[6], S[2] * S[3] - S[0] * S[5], S[3] * S[7] - S[4] * S[6], S[1] * S[6] - S[0] * S[7], S[0] * S[4] - S[1] * S[3]].map(function (v) { return v / d; });
          var sol = function (B) { return [0, 1, 2].map(function (m) { return inv[m * 3] * B[0] + inv[m * 3 + 1] * B[1] + inv[m * 3 + 2] * B[2]; }); };
          var u = sol(X), v = sol(Y); M = [u[0], u[1], u[2], v[0], v[1], v[2]];
        }
      }
      return (V.A[key] = M);
    }
    // kareyi t oranında hedef konuma doğru bükerek alfa ile çiz (normalize koordinatlar R içinde)
    function warp(im, M, t, al, R) {
      if (al <= 0) return;
      var a = 1, b = 0, c = 0, d = 0, e = 1, f = 0;
      if (M) { a = 1 + t * (M[0] - 1); b = t * M[1]; c = t * M[2]; d = t * M[3]; e = 1 + t * (M[4] - 1); f = t * M[5]; }
      // ekran = R.xy + R.wh * (A * uv); uv = (piksel - R.xy) / R.wh
      cx.setTransform(DPR * a, DPR * d * R.h / R.w, DPR * b * R.w / R.h, DPR * e, DPR * (R.x + R.w * c - a * R.x - b * R.w / R.h * R.y), DPR * (R.y + R.h * f - d * R.h / R.w * R.x - e * R.y));
      cx.globalAlpha = al; cx.drawImage(im, R.x, R.y, R.w, R.h);
      cx.setTransform(DPR, 0, 0, DPR, 0, 0); cx.globalAlpha = 1;
    }
    function mix(A, B, t) { var o = {}; for (var k in A) { var p = A[k], q = B[k]; o[k] = q ? [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t] : (t < 0.5 ? p : null); } for (var k2 in B) if (!A[k2] && t >= 0.5) o[k2] = B[k2]; return o; }
    function draw() {
      if (!V.on || V.mode !== 'spin' || !V.n) return;
      var W = sp.clientWidth, H = sp.clientHeight; if (!W) return;
      var i0 = Math.floor(V.p) % V.n, i1 = (i0 + 1) % V.n, fr = V.p - Math.floor(V.p), a = near(i0); if (a < 0) return;
      var im = V.frames[a], R = rect(sp, im.width, im.height, 1.32);
      // tuval çözünürlüğü karenin kendi çözünürlüğünü aşmasın: retina ekranda boşuna 4 kat piksel çizip takılmasın
      DPR = Math.max(1, Math.min(DPR0, im.width * 1.15 / R.w));
      if (cv.width !== Math.round(W * DPR) || cv.height !== Math.round(H * DPR)) { cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR); }
      cx.setTransform(DPR, 0, 0, DPR, 0, 0); cx.clearRect(0, 0, W, H); cx.globalAlpha = 1;
      var both = a === i0 && ready(i1) && fr > 0.001, b = both ? fr : 0;
      if (!both) cx.drawImage(im, R.x, R.y, R.w, R.h);
      else {
        // ara kare: iki kareyi üst üste karıştırmak duvarları çift gösteriyordu (şaşı görüntü).
        // Bunun yerine her an tek kare çizilir: yakın kare zemin düzlemine göre komşusuna doğru hafifçe bükülür, yarı yolda diğerine geçilir.
        // Ara kareler yüklüyse kareler çok yakın: geçiş anında çok kısa bir karıştırma, kalan küçük sıçramayı da yumuşatır.
        var w = V.S > 1 ? Math.min(1, Math.max(0, (fr - 0.35) / 0.3)) : (fr < 0.5 ? 0 : 1); w = w * w * (3 - 2 * w);
        if (w > 0 && w < 1) cx.globalCompositeOperation = 'lighter';
        if (w < 1) warp(V.frames[i0], aff(i0, i1), fr, 1 - w, R);
        if (w > 0) warp(V.frames[i1], aff(i1, i0), 1 - fr, w, R);
        cx.globalCompositeOperation = 'source-over';
      }
      setLbl(V.L, b ? mix(V.lab[i0], V.lab[i1], b) : V.lab[a], R);
    }
    function drawTop() {
      if (!V.on || V.mode !== 'top' || !V.D) return;
      var D = V.D.top, W = tp.clientWidth, H = tp.clientHeight - 16, s = Math.min(W / D.w, H / D.h), w = D.w * s, h = D.h * s;
      var R = { x: (W - w) / 2, y: 8 + (H - h) / 2, w: w, h: h, W: W }, box = tp.querySelector('.tbox');
      box.style.left = R.x + 'px'; box.style.top = R.y + 'px'; box.style.width = R.w + 'px'; box.style.height = R.h + 'px';
      setLbl(V.TL, D.labels, R);
      [].forEach.call(tp.querySelectorAll('polygon'), function (e) { e.classList.toggle('on', e.getAttribute('data-r') === V.hl); });
    }
    function tick(t) {
      var dt = Math.min(64, t - (V.last || t)); V.last = t;
      if (V.on && V.mode === 'spin' && V.n && V.auto && V.loaded >= V.D.n && !document.hidden) { V.p = (V.p + dt * V.n / 26000) % V.n; draw(); }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
    sp.addEventListener('pointerdown', function (e) {
      if (e.target.closest('.play')) return;
      V.drag = { x: e.clientX, p: V.p }; V.auto = false; q('.play').classList.remove('on');
      try { sp.setPointerCapture(e.pointerId); } catch (_) {} q('.hint').style.opacity = 0;
    });
    sp.addEventListener('pointermove', function (e) {
      if (!V.drag) return; var step = Math.max(8, sp.clientWidth / 70) / V.S;
      var p = V.drag.p - (e.clientX - V.drag.x) / step; V.p = ((p % V.n) + V.n) % V.n; draw();
    });
    function up() { if (V.drag) { V.drag = null; track('kat_plani3d_cevir', { plan: V.pid }); } }
    sp.addEventListener('pointerup', up); sp.addEventListener('pointercancel', up);
    q('.play').onclick = function () { V.auto = !V.auto; this.classList.toggle('on', V.auto); };
    tp.querySelector('svg').addEventListener('click', function (e) {
      var p = e.target.closest('polygon'); if (!p) return; var r = p.getAttribute('data-r'); V.hl = V.hl === r ? null : r; drawTop();
      track('kat_plani3d_oda', { plan: V.pid, oda: r });
    });
    window.addEventListener('resize', function () { draw(); drawTop(); });

    return {
      show: function (pid, mode) {
        if (!load(pid)) return false;
        V.on = true; V.mode = mode; host.style.display = 'block';
        sp.style.display = mode === 'spin' ? 'block' : 'none'; tp.style.display = mode === 'top' ? 'block' : 'none';
        draw(); drawTop(); track('kat_plani3d_mod', { plan: pid, mod: mode });
        return true;
      },
      hide: function () { V.on = false; host.style.display = 'none'; }
    };
  }
  window.Kat3D = { has: function (pid) { return !!K[pid]; }, create: create };
})();
