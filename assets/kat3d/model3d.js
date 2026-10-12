/* Gerçek zamanlı 3D kat planı: ışığı önceden (Cycles) pişirilmiş GLB modeli, mouse/parmakla her yönden çevirme ve yakınlaştırma.
   Kullanım: import('assets/kat3d/model3d.js').then(m => { var v = m.create(kutu); v.show('11-01'); v.hide(); }) */
import * as THREE from 'three';
import { OrbitControls } from '../vendor/three/OrbitControls.js';
import { GLTFLoader } from '../vendor/three/GLTFLoader.js';
import { MeshoptDecoder } from '../vendor/three/meshopt_decoder.module.js';

var css = '.m3d{position:relative;width:100%;height:100%;overflow:hidden;background:linear-gradient(180deg,#f7f8fc,#e9edf6);border-radius:14px;font-family:"Plus Jakarta Sans","Archivo",sans-serif;user-select:none;-webkit-user-select:none}' +
  '.m3d canvas{position:absolute;inset:0;width:100%;height:100%;display:block;touch-action:none;cursor:grab}.m3d canvas:active{cursor:grabbing}' +
  '.m3d .lbls{position:absolute;inset:0;pointer-events:none;overflow:hidden}' +
  '.m3d .lb3{position:absolute;left:0;top:0;text-align:center;white-space:nowrap;font-size:.72rem;font-weight:700;color:#050A30;background:rgba(255,255,255,.9);border-radius:8px;padding:3px 8px;line-height:1.25;box-shadow:0 2px 10px rgba(5,10,48,.14);transition:opacity .2s;will-change:transform}' +
  '.m3d .lb3 i{display:block;font-style:normal;font-weight:600;color:#DC1C2E;font-size:.68rem}' +
  '.m3d .ld{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none}' +
  '.m3d .ld>div{background:rgba(255,255,255,.94);border-radius:12px;padding:10px 14px;font-size:.8rem;font-weight:600;color:#050A30;box-shadow:0 4px 18px rgba(5,10,48,.1);text-align:center}' +
  '.m3d .ldt{height:4px;width:180px;background:#e4e7f1;border-radius:4px;margin-top:8px;overflow:hidden}.m3d .ldb{height:100%;width:0;background:#DC1C2E;transition:width .2s}' +
  '.m3d .hint{position:absolute;left:50%;transform:translateX(-50%);bottom:14px;white-space:nowrap;font-size:.75rem;color:#59607d;background:rgba(255,255,255,.88);padding:5px 10px;border-radius:8px;transition:opacity .4s;pointer-events:none}' +
  '.m3d .rst{position:absolute;right:12px;top:12px;font:inherit;font-weight:700;font-size:.78rem;border:none;background:rgba(255,255,255,.94);color:#050A30;padding:7px 11px;border-radius:10px;cursor:pointer;box-shadow:0 4px 14px rgba(5,10,48,.1)}' +
  '@media(max-width:600px){.m3d .lb3{font-size:.62rem;padding:2px 6px;border-radius:6px}.m3d .lb3 i{font-size:.6rem}.m3d .hint{font-size:.7rem}}';
var injected = false;
function fmt(n) { return n.toFixed(2).replace('.', ',') + ' m²'; }
function track(n, p) { try { if (typeof gtag === 'function') gtag('event', n, p || {}); } catch (e) {} }

export function create(host) {
  if (!injected) { var s = document.createElement('style'); s.textContent = css; document.head.appendChild(s); injected = true; }
  host.classList.add('m3d');
  host.innerHTML = '<canvas></canvas><div class="lbls"></div><div class="ld"><div><span>3D model yükleniyor</span><div class="ldt"><div class="ldb"></div></div></div></div>' +
    '<button type="button" class="rst">Başa dön</button><div class="hint">' + (matchMedia('(pointer:coarse)').matches ? 'Parmağınızla çevirin · iki parmakla yakınlaştırın' : 'Sürükleyerek her yöne çevirin · tekerlekle yakınlaştırın') + '</div>';
  var q = function (s) { return host.querySelector(s); };
  var cv = q('canvas'), L = q('.lbls');
  var R = new THREE.WebGLRenderer({ canvas: cv, antialias: true, alpha: true });
  R.setPixelRatio(Math.min(window.devicePixelRatio || 1, matchMedia('(pointer:coarse)').matches ? 1.5 : 2)); R.outputColorSpace = THREE.SRGBColorSpace;
  var scene = new THREE.Scene(), cam = new THREE.PerspectiveCamera(35, 1, 0.1, 300);
  var ctl = new OrbitControls(cam, cv);
  ctl.enableDamping = true; ctl.dampingFactor = 0.09; ctl.rotateSpeed = 0.75; ctl.enablePan = false;
  ctl.minPolarAngle = 0; ctl.maxPolarAngle = Math.PI * 0.42;   // zeminin altına inmesin
  var st = { rest: false, occ: false, still: 0, pid: null, root: null, labels: [], on: false, home: null, dirty: true, moved: false };
  var loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder), v3 = new THREE.Vector3(), ray = new THREE.Raycaster(), occT = 0;

  function size() {
    var w = host.clientWidth, h = host.clientHeight; if (!w || !h) return;
    R.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix(); st.dirty = true;
  }
  function frame(box) {
    var c = box.getCenter(new THREE.Vector3()), s = box.getSize(new THREE.Vector3()), r = Math.hypot(s.x, s.z) / 2;
    var fov = cam.fov * Math.PI / 180, fh = 2 * Math.atan(Math.tan(fov / 2) * Math.min(1, cam.aspect));
    var d = r / Math.sin(fh / 2) * 1.02;
    ctl.target.set(c.x, 0.4, c.z);
    var el = 0.95, az = -0.85;   // açılışta fotoğraflardaki gibi eğik kuş bakışı
    cam.position.set(c.x + d * Math.cos(el) * Math.sin(az), d * Math.sin(el), c.z + d * Math.cos(el) * Math.cos(az));
    ctl.minDistance = d * 0.35; ctl.maxDistance = d * 1.8; ctl.update();
    st.home = { p: cam.position.clone(), t: ctl.target.clone() };
  }
  function place() {
    var w = host.clientWidth, h = host.clientHeight, mob = w < 600, shown = [], now = performance.now();
    // duvarın arkasında kalan odanın etiketini gizle (ışın testi pahalı: en fazla 5 kez/sn)
    if (st.root && st.rest && !st.occ) {
      st.occ = true; st.rest = false; occT = now;
      st.labels.forEach(function (l) {
        var dir = v3.copy(l.p).sub(cam.position), d = dir.length(); ray.set(cam.position, dir.normalize()); ray.far = d - 0.05;
        l.hid = ray.intersectObject(st.root, true).some(function (x) { return !x.object.material.transparent; });
      });
    }
    st.labels.forEach(function (l) { v3.copy(l.p).project(cam); l.x = (v3.x + 1) / 2 * w; l.y = (1 - v3.y) / 2 * h; l.ok = v3.z < 1; });
    st.labels.slice().sort(function (a, b) { return b.m - a.m; }).forEach(function (l) {
      var lw = l.w || (l.w = l.el.offsetWidth), lh = l.h || (l.h = l.el.offsetHeight);
      var hit = !l.ok || l.hid || (mob && l.m < 5) || shown.some(function (o) { return Math.abs(o.x - l.x) < (o.w + lw) / 2 + 2 && Math.abs(o.y - l.y) < (o.h + lh) / 2 + 2; });
      l.el.style.opacity = hit ? 0 : 1; l.el.style.transform = 'translate(' + (l.x - lw / 2).toFixed(1) + 'px,' + (l.y - lh / 2).toFixed(1) + 'px)';
      if (!hit) shown.push(l);
    });
  }
  function loop() {
    requestAnimationFrame(loop);
    if (!st.on) return;
    var moved = ctl.update();
    if (moved) st.occ = false;
    // parmak/mouse bırakılınca en fazla 2.5 kez/sn duvar arkası etiket testi (sürüklerken yapılmaz: telefonda takılmasın)
    if (!st.occ && !st.drag && performance.now() - occT > 400) { st.rest = true; st.dirty = true; }
    if (moved || st.dirty) { st.dirty = false; R.render(scene, cam); place(); }
  }
  ctl.addEventListener('change', function () { st.dirty = true; });
  ctl.addEventListener('end', function () { st.drag = false; });
  ctl.addEventListener('start', function () { st.drag = true; q('.hint').style.opacity = 0; if (!st.moved) { st.moved = true; track('kat_plani3d_model_cevir', { plan: st.pid }); } });
  q('.rst').onclick = function () { if (!st.home) return; cam.position.copy(st.home.p); ctl.target.copy(st.home.t); ctl.update(); st.dirty = true; };
  window.addEventListener('resize', size);
  if (window.ResizeObserver) new ResizeObserver(size).observe(host);
  requestAnimationFrame(loop);

  function load(pid) {
    if (st.pid === pid) return;
    st.pid = pid; st.moved = false; st.rest = false; st.occ = false; st.still = 0; q('.hint').style.opacity = 1;
    if (st.root) { scene.remove(st.root); st.root.traverse(function (o) { if (o.isMesh) { o.geometry.dispose(); if (o.material.map) o.material.map.dispose(); o.material.dispose(); } }); st.root = null; }
    L.innerHTML = ''; st.labels = []; q('.ld').style.display = 'flex'; q('.ldb').style.width = '0%';
    var dir = 'assets/kat3d/' + pid + '/';
    fetch(dir + 'model.json').then(function (r) { return r.json(); }).then(function (j) {
      if (st.pid !== pid) return;
      st.labels = j.rooms.map(function (r) {
        var d = document.createElement('div'); d.className = 'lb3'; d.innerHTML = r[1] + '<i>' + fmt(r[2]) + '</i>'; L.appendChild(d);
        return { el: d, m: r[2], p: new THREE.Vector3(r[3][0], r[3][1], r[3][2]) };
      });
      st.dirty = true;
    }).catch(function () {});
    loader.load(dir + 'model.glb', function (g) {
      if (st.pid !== pid) return;
      var aniso = R.capabilities.getMaxAnisotropy();
      g.scene.traverse(function (o) {
        if (!o.isMesh) return;
        var m = o.material, glass = /glass/.test(m.name || '');
        // ışık dokuya pişmiş: ek ışık hesaplanmaz, gölge yoktur; görüntü render ile aynı
        if (glass) o.material = new THREE.MeshBasicMaterial({ color: 0xdde8f2, transparent: true, opacity: 0.16, depthWrite: false });
        else { if (m.map) { m.map.anisotropy = aniso; m.map.colorSpace = THREE.SRGBColorSpace; } o.material = new THREE.MeshBasicMaterial({ map: m.map || null }); }
        if (m !== o.material) m.dispose();
      });
      st.root = g.scene; scene.add(g.scene); size();
      frame(new THREE.Box3().setFromObject(g.scene));
      q('.ld').style.display = 'none'; st.dirty = true; window.__m3dReady = pid;
    }, function (e) { if (e.total) q('.ldb').style.width = (e.loaded / e.total * 100) + '%'; });
  }
  return {
    show: function (pid) { host.style.display = 'block'; st.on = true; size(); load(pid); st.dirty = true; track('kat_plani3d_mod', { plan: pid, mod: 'model' }); },
    hide: function () { st.on = false; host.style.display = 'none'; }
  };
}
