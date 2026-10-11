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
    var sp = q('.sp'), tp = q('.tp'), cv = q('canvas'), cx = cv.getContext('2d'), DPR = Math.min(window.devicePixelRatio || 1, 2);
    var V = { pid: null, mode: null, frames: [], n: 0, p: 0, auto: true, drag: null, loaded: 0, hl: null, last: 0, on: false };

    function rect(el, iw, ih, z) {
      var W = el.clientWidth, H = el.clientHeight, s = Math.min(W / iw, H / ih) * (z && W < 600 ? z : 1), w = iw * s, h = ih * s;
      return { x: (W - w) / 2, y: (H - h) / 2, w: w, h: h, W: W };
    }
    function mkLabels(el) {
      el.innerHTML = ''; var o = {};
      (ROOMS[V.pid] || []).forEach(function (r) {
        var d = document.createElement('div'); d.className = 'lb3'; d.innerHTML = r[1] + '<i>' + fmt(r[2]) + '</i>'; el.appendChild(d); o[r[0]] = { el: d, m: r[2] };
      });
      return o;
    }
    function setLbl(L, pos, R) {
      var mob = R.W < 600;
      for (var k in L) {
        var p = pos && pos[k], l = L[k];
        if (!p || (mob && l.m < 5 && k !== V.hl)) { l.el.style.opacity = 0; continue; }
        l.el.style.opacity = 1; l.el.style.left = (R.x + p[0] * R.w) + 'px'; l.el.style.top = (R.y + p[1] * R.h) + 'px'; l.el.classList.toggle('hl', k === V.hl);
      }
    }
    function load(pid) {
      var D = K[pid]; if (!D) return false; if (V.pid === pid) return true;
      V.pid = pid; V.D = D; V.n = D.n; V.p = 0; V.auto = true; V.loaded = 0; V.frames = []; V.hl = null; q('.play').classList.add('on');
      V.L = mkLabels(sp.querySelector('.lbls')); V.TL = mkLabels(tp.querySelector('.lbls'));
      q('.ld').style.display = 'flex'; q('.ldb').style.width = '0%';
      // önce seyrek kareler: dönüş hemen başlayabilsin
      var order = []; [8, 4, 2, 1].forEach(function (s) { for (var i = 0; i < D.n; i += s) if (order.indexOf(i) < 0) order.push(i); });
      order.forEach(function (i) {
        var im = new Image(); im.decoding = 'async';
        im.onload = function () { V.loaded++; q('.ldb').style.width = (V.loaded / D.n * 100) + '%'; if (V.loaded >= D.n) q('.ld').style.display = 'none'; draw(); };
        im.src = D.dir + 'f' + (i < 10 ? '0' : '') + i + '.webp'; V.frames[i] = im;
      });
      var ti = tp.querySelector('img'); ti.onload = drawTop; ti.src = D.dir + 'top.webp';
      var svg = tp.querySelector('svg'); svg.innerHTML = '';
      (ROOMS[pid] || []).forEach(function (r) {
        var pts = D.top.polys[r[0]]; if (!pts) return;
        var e = document.createElementNS(NS, 'polygon'); e.setAttribute('points', pts.map(function (a) { return a[0] + ',' + a[1]; }).join(' '));
        e.setAttribute('data-r', r[0]); svg.appendChild(e);
      });
      return true;
    }
    function ready(i) { var f = V.frames[i]; return f && f.complete && f.naturalWidth; }
    function near(i) { if (ready(i)) return i; for (var d = 1; d < V.n; d++) { var a = (i + d) % V.n, b = (i - d + V.n) % V.n; if (ready(a)) return a; if (ready(b)) return b; } return -1; }
    function draw() {
      if (!V.on || V.mode !== 'spin' || !V.n) return;
      var W = sp.clientWidth, H = sp.clientHeight; if (!W) return;
      if (cv.width !== Math.round(W * DPR) || cv.height !== Math.round(H * DPR)) { cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR); }
      var i0 = Math.floor(V.p) % V.n, i1 = (i0 + 1) % V.n, fr = V.p - Math.floor(V.p), a = near(i0); if (a < 0) return;
      var im = V.frames[a], R = rect(sp, im.naturalWidth, im.naturalHeight, 1.32);
      cx.setTransform(DPR, 0, 0, DPR, 0, 0); cx.clearRect(0, 0, W, H); cx.globalAlpha = 1; cx.drawImage(im, R.x, R.y, R.w, R.h);
      var b = V.auto ? Math.max(0, (fr - 0.8) / 0.2) : 0; b = b * b * (3 - 2 * b);
      if (b > 0 && ready(i1)) { cx.globalAlpha = b; cx.drawImage(V.frames[i1], R.x, R.y, R.w, R.h); cx.globalAlpha = 1; }
      // karenin kenarında kesilen gölgeyi yumuşakça söndür
      cx.globalCompositeOperation = 'destination-out';
      [[R.x, 0, R.x + R.w * 0.07, 0], [R.x + R.w, 0, R.x + R.w * 0.93, 0], [0, R.y, 0, R.y + R.h * 0.08], [0, R.y + R.h, 0, R.y + R.h * 0.92]].forEach(function (g) {
        var gr = cx.createLinearGradient(g[0], g[1], g[2], g[3]); gr.addColorStop(0, 'rgba(0,0,0,1)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
        cx.fillStyle = gr; cx.fillRect(R.x, R.y, R.w, R.h);
      });
      cx.globalCompositeOperation = 'source-over';
      setLbl(V.L, V.D.labels[b > 0.5 && ready(i1) ? i1 : a], R);
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
      if (V.on && V.mode === 'spin' && V.n && V.auto && V.loaded >= V.n && !document.hidden) { V.p = (V.p + dt / (V.n > 30 ? 220 : 380)) % V.n; draw(); }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
    sp.addEventListener('pointerdown', function (e) {
      if (e.target.closest('.play')) return;
      V.drag = { x: e.clientX, p: V.p }; V.auto = false; q('.play').classList.remove('on'); V.p = Math.round(V.p) % V.n;
      try { sp.setPointerCapture(e.pointerId); } catch (_) {} q('.hint').style.opacity = 0;
    });
    sp.addEventListener('pointermove', function (e) {
      if (!V.drag) return; var step = Math.max(8, sp.clientWidth / 70);
      var p = Math.round(V.drag.p - (e.clientX - V.drag.x) / step); V.p = ((p % V.n) + V.n) % V.n; draw();
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
