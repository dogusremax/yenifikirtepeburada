"""Gerçekçi gece: panoramayı örtüşen yüzlere böl -> Gemini ile gece yap -> hizala -> panoramaya geri birleştir.

  python3 gece_ai.py split <sahne.jpg> <klasör>          # 6 yüz, 100° görüş, 2048 px (yuz_*.jpg)
  python3 gece_ai.py gen   <klasör> [model]              # GEMINI_API_KEY ile her yüzün gecesini üretir (gece_*.png)
  python3 gece_ai.py merge <sahne.jpg> <klasör> <çıkış.jpg>  # hizalar, gündüz netliğini ekler, 16384x8192 panorama

Yüzler: f r b l (yan, 30° aşağı bakar: gök az, şehir çok), d (aşağı). Gök yapay zekâya gönderilmez:
ufkun üstü gündüz görüntüsünden çıkarılan gök maskesiyle tek parça yapay gece göğüyle değiştirilir (yüzler arası dikiş olmaz).
REF ortam değişkeni bir gece örneği gösterirse (Umut'un ChatGPT örneği) stil referansı olarak gönderilir.
"""
import sys, os, json, base64, time, numpy as np, cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
FOV = 110.0
S = 4096
# yüz yönleri (yaw, pitch) derece
FACES = {'f': (0, -30), 'r': (90, -30), 'b': (180, -30), 'l': (-90, -30), 'd': (0, -90)}

def rot(yaw, pitch):
    y, p = np.radians(yaw), np.radians(pitch)
    Ry = np.array([[np.cos(y), 0, np.sin(y)], [0, 1, 0], [-np.sin(y), 0, np.cos(y)]])
    Rx = np.array([[1, 0, 0], [0, np.cos(p), np.sin(p)], [0, -np.sin(p), np.cos(p)]])
    return Ry @ Rx

def dirs(face, n):
    t = np.tan(np.radians(FOV / 2))
    a = (np.arange(n) + .5) / n * 2 - 1
    x, y = np.meshgrid(a * t, -a * t)
    d = np.stack([x, y, np.ones_like(x)], -1)
    return d @ rot(*FACES[face]).T

def split(src, out, n=S):
    os.makedirs(out, exist_ok=True)
    eq = cv2.imread(src); H, W = eq.shape[:2]
    for f in FACES:
        d = dirs(f, n)
        lon = np.arctan2(d[..., 0], d[..., 2]); lat = np.arctan2(d[..., 1], np.hypot(d[..., 0], d[..., 2]))
        u = ((lon / (2 * np.pi) + .5) * W - .5).astype(np.float32); v = ((.5 - lat / np.pi) * H - .5).astype(np.float32)
        im = cv2.remap(eq, u, v, cv2.INTER_AREA if n < 4096 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        cv2.imwrite(f'{out}/yuz_{f}.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 93])
    print('split', out)

PROMPT = ("Turn this daytime aerial photo of an Istanbul city district into a realistic night photo taken shortly after sunset (blue hour / early night). "
          "Keep every building, road, tree and the camera angle exactly the same, do not add or remove anything, do not change the framing. "
          "Lit windows in warm and neutral white tones scattered naturally across the residential towers (not all windows), warm orange street lights "
          "along roads, car head/tail light streaks on the highways, softly lit parks and plazas, deep blue sky, dark sea with city reflections. "
          "Photorealistic, like a professional drone photo, natural exposure, no glow exaggeration.")

def _gen1(out, f, model, key, ref):
    import urllib.request
    dst = f'{out}/gece_{f}.png'
    if os.path.exists(dst): return
    parts = [{'text': PROMPT}, {'inline_data': {'mime_type': 'image/jpeg', 'data': base64.b64encode(open(f'{out}/yuz_{f}.jpg', 'rb').read()).decode()}}]
    if ref:
        parts += [{'text': 'Style reference for the night lighting mood and colours only (do not copy its content):'},
                  {'inline_data': {'mime_type': 'image/jpeg', 'data': ref}}]
    body = {'contents': [{'parts': parts}],
            'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '1:1', 'imageSize': '4K'}}}
    req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
                                 json.dumps(body).encode(), {'Content-Type': 'application/json', 'x-goog-api-key': key})
    for t in range(4):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=600))
            img = [p for p in r['candidates'][0]['content']['parts'] if 'inlineData' in p or 'inline_data' in p][0]
            break
        except Exception as e:
            print('hata', f, str(e)[:200]); time.sleep(15 * (t + 1))
    else:
        raise SystemExit('üretilemedi: ' + f)
    open(dst, 'wb').write(base64.b64decode((img.get('inlineData') or img.get('inline_data'))['data'])); print('gece', dst)

def gen(out, model='gemini-3-pro-image'):
    from concurrent.futures import ThreadPoolExecutor
    key = os.environ['GEMINI_API_KEY']; ref = None
    if os.environ.get('REF'):
        im = cv2.imread(os.environ['REF']); ok, buf = cv2.imencode('.jpg', cv2.resize(im, (1536, int(1536 * im.shape[0] / im.shape[1]))), [cv2.IMWRITE_JPEG_QUALITY, 90])
        ref = base64.b64encode(buf.tobytes()).decode()
    with ThreadPoolExecutor(5) as ex:
        list(ex.map(lambda f: _gen1(out, f, model, key, ref), FACES))

def _edges(im, n):
    g = cv2.cvtColor(cv2.resize(im, (n, n), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
    g = cv2.GaussianBlur(g, (0, 0), 1.5)
    m = cv2.magnitude(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1))
    return m / (cv2.GaussianBlur(m, (0, 0), 8) + 1e-3)          # yerel olarak normalize: gece/gündüz parlaklık farkı önemsiz

def _score(day, im):
    a = _edges(day, 512); b = _edges(im, 512)
    return float(np.corrcoef(a.ravel(), b.ravel())[0, 1])

def align(day, night):
    """Gece görüntüsünü gündüze hizala (yapay zekâ küçük kaymalar yapabilir): kenar haritalarında kaba-ince ECC."""
    night = cv2.resize(night, (day.shape[1], day.shape[0]), interpolation=cv2.INTER_CUBIC)
    N = day.shape[1]; warp = np.eye(3, dtype=np.float32)
    for n in (256, 512, 1024):
        sc = n / N; S_ = np.diag([sc, sc, 1]).astype(np.float32); w = S_ @ warp @ np.linalg.inv(S_)
        try:
            _, w = cv2.findTransformECC(_edges(day, n), _edges(night, n), w, cv2.MOTION_HOMOGRAPHY,
                                        (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 150, 1e-6), None, 3)
            warp = np.linalg.inv(S_) @ w @ S_
        except cv2.error:
            pass
    out = cv2.warpPerspective(night, warp, (N, N), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
    s0, s1 = _score(day, night), _score(day, out)
    print('hizalama: benzerlik %.3f -> %.3f' % (s0, s1))
    return out if s1 > s0 else night

def sky_mask(eq):
    """Gündüz panoramasında gök maskesi (1 = gök). Her sütunda yukarıdan aşağı ilk belirgin kenara (siluet) kadar gök sayılır."""
    H, W = eq.shape[:2]; h, w = 2048, 4096
    sm = cv2.resize(eq, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32)
    g = cv2.GaussianBlur(sm.mean(2), (0, 0), 1.2)
    m = cv2.magnitude(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1))
    m[:int(h * .30)] = 0                                   # tepe gürültüsü yok sayılır (ufuk ~%50'de)
    hit = m > float(os.environ.get('SKY_T', 14))
    first = np.where(hit.any(0), hit.argmax(0), int(h * .5))
    first = np.minimum(first, int(h * .52))                # ufuk çizgisinin çok altına inmez
    first = np.minimum.reduce([np.roll(first, k) for k in range(-2, 3)])  # ince kuleler korunur
    rows = np.arange(h)[:, None]
    mask = (rows < first[None, :] - 1).astype(np.float32)
    mask = cv2.GaussianBlur(mask, (0, 0), 1.0)
    return cv2.resize(mask, (W, H), interpolation=cv2.INTER_LINEAR)

def night_sky(H, W, hor):
    """Tek parça gece göğü: ufukta şehir ışığı yansıyan sıcak pus, tepeye doğru koyu lacivert. hor: ufuk rengi (BGR)."""
    lat = 90 - (np.arange(H) + .5) / H * 180
    t = np.clip(lat / 35, 0, 1) ** .55
    zen = np.array([62, 24, 10.]); mid = np.array([115, 60, 30.])  # mavi saat: tepe koyu lacivert
    col = np.where(t[:, None] < .25, hor * (1 - t[:, None] / .25) + mid * (t[:, None] / .25),
                   mid * (1 - (t[:, None] - .25) / .75) + zen * ((t[:, None] - .25) / .75))
    sky = np.repeat(col[:, None, :], W, 1).astype(np.float32)
    rng = np.random.default_rng(1); noise = cv2.resize(rng.normal(0, 1, (H // 64, W // 64)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    return sky * (1 + noise[..., None] * .025)            # çok hafif bulut/pus dokusu, düz bant görünmesin

def _project(night, f, W, H, n, r0=0, r1=None):
    """Yüz görüntüsünü eşdikdörtgen panoramanın r0:r1 satırlarına yansıt; (görüntü, ağırlık) döndürür."""
    r1 = H if r1 is None else r1
    lon = (np.arange(W) + .5) / W * 2 * np.pi - np.pi; la = (np.pi / 2 - (np.arange(r0, r1) + .5) / H * np.pi)[:, None]
    t = np.tan(np.radians(FOV / 2)); lo = lon[None, :]
    d = np.stack([np.cos(la) * np.sin(lo), np.sin(la) * np.ones_like(lo), np.cos(la) * np.cos(lo)], -1) @ rot(*FACES[f])  # dünya -> yüz
    z = d[..., 2]; ok = z > 1e-3
    x = np.where(ok, d[..., 0] / np.maximum(z, 1e-3) / t, 9); y = np.where(ok, -d[..., 1] / np.maximum(z, 1e-3) / t, 9)
    w = np.clip(1 - np.maximum(np.abs(x), np.abs(y)), 0, 1)              # tüm örtüşme boyunca yumuşak geçiş
    px = ((x + 1) / 2 * n - .5).astype(np.float32); py = ((y + 1) / 2 * n - .5).astype(np.float32)
    return cv2.remap(night, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32), w.astype(np.float32)

def _gains(nights, n, ground):
    """Yüzler arası renk/parlaklık farkını gider: örtüşmelerde kanal başına kazanç (panorama dikiş yöntemi)."""
    W, H = 1024, 512; fs = list(nights); P = {f: _project(cv2.resize(nights[f], (256, 256), interpolation=cv2.INTER_AREA), f, W, H, 256) for f in fs}
    k = len(fs); g = np.ones((k, 3))
    for c in range(3):
        A = np.eye(k) * 50.; bb = np.ones(k) * 50.        # kazançlar 1'e yakın kalsın
        for i in range(k):
            for j in range(i + 1, k):
                m = (P[fs[i]][1] > .05) & (P[fs[j]][1] > .05) & ground
                if m.sum() < 50: continue
                Ii = P[fs[i]][0][..., c][m].mean(); Ij = P[fs[j]][0][..., c][m].mean(); N = m.sum() / 1000.
                A[i, i] += N * Ii * Ii / 1e3; A[j, j] += N * Ij * Ij / 1e3; A[i, j] -= N * Ii * Ij / 1e3; A[j, i] -= N * Ii * Ij / 1e3
        g[:, c] = np.linalg.solve(A, bb)
    print('kazançlar', {f: np.round(g[i], 3).tolist() for i, f in enumerate(fs)})
    return {f: g[i] for i, f in enumerate(fs)}

def _up(G, W, H, r0, r1):
    gh, gw = G.shape[:2]
    x = np.tile(((np.arange(W) + .5) * gw / W - .5).astype(np.float32), (r1 - r0, 1))
    y = np.repeat(((np.arange(r0, r1) + .5) * gh / H - .5).astype(np.float32)[:, None], W, 1)
    return cv2.remap(G, x, y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)

def _blurw(a, sg):
    """Yatayda sarmalı (360°) Gauss bulanıklığı."""
    p = int(sg * 3); w = a.shape[1]
    b = cv2.GaussianBlur(np.concatenate([a[:, -p:], a, a[:, :p]], 1), (0, 0), sg, borderType=cv2.BORDER_REFLECT)
    return b[:, p:p + w]

def _gain_fields(bands, n, ground, gw=1024):
    """Yerel renk eşitleme: örtüşmelerde her yüzü ortak renge çeken, yüz içine yumuşakça yayılan kazanç alanı."""
    gh = gw // 2; P = {f: _project(cv2.resize(low, (256, 256), interpolation=cv2.INTER_AREA), f, gw, gh, 256) for f, (low, _) in bands.items()}
    ws = sum(w for _, w in P.values()); M = sum(L * w[..., None] for L, w in P.values()) / np.maximum(ws, 1e-6)[..., None]
    G = {}
    for f, (L, w) in P.items():
        other = ws - w; c = (w * np.clip(other * 4, 0, 1) * ground).astype(np.float32)
        R = np.clip(M / np.maximum(L, 4), .4, 2.5).astype(np.float32)
        num = _blurw(R * c[..., None], gw / 40)
        den = _blurw(c, gw / 40)[..., None]
        k = np.clip(den / .02, 0, 1)
        G[f] = (num / np.maximum(den, 1e-6) * k + (1 - k)).astype(np.float32)
    return G

def merge(src, out, dst, W=16384):
    H = W // 2; n = cv2.imread(f'{out}/yuz_f.jpg').shape[0]
    eq = cv2.imread(src)
    if eq.shape[1] != W: eq = cv2.resize(eq, (W, H), interpolation=cv2.INTER_AREA)
    mask = sky_mask(eq)
    if os.environ.get('SKYONLY') and os.path.exists(f'{out}/_res.npy'):
        res = np.load(f'{out}/_res.npy'); return _sky(res, eq, mask, dst)
    nights = {f: align(cv2.imread(f'{out}/yuz_{f}.jpg'), cv2.imread(f'{out}/gece_{f}.png')) for f in FACES if os.path.exists(f'{out}/gece_{f}.png')}
    gains = _gains(nights, n, cv2.resize(mask, (1024, 512)) < .5)
    # iki bantlı birleştirme: renk (alçak frekans) geniş geçişle, ayrıntı dar geçişle -> renk farkı dikiş yapmaz
    bands = {}
    for f, night in nights.items():
        night = np.clip(night.astype(np.float32) * gains[f][None, None, :], 0, 255)
        low = cv2.GaussianBlur(night, (0, 0), night.shape[0] / 60); bands[f] = (low, night - low)
    del nights
    G = _gain_fields(bands, n, (cv2.resize(mask, (1024, 512)) < .5).astype(np.float32))
    res = np.zeros((H, W, 3), np.uint8); hpk = float(os.environ.get('HP', .35)); B = 512
    for r0 in range(0, H, B):
        r1 = min(H, r0 + B); lo = np.zeros((r1 - r0, W, 3), np.float32); hi = np.zeros_like(lo)
        lw = np.zeros((r1 - r0, W), np.float32); hw = np.zeros_like(lw)
        for f, (low, high) in bands.items():
            sl, w = _project(low, f, W, H, n, r0, r1); sh, _ = _project(high, f, W, H, n, r0, r1)
            g = _up(G[f], W, H, r0, r1); sl *= g; sh *= g
            lo += sl * w[..., None]; lw += w; w2 = w ** 4; hi += sh * w2[..., None]; hw += w2
        nn = lo / np.maximum(lw, 1e-6)[..., None] + hi / np.maximum(hw, 1e-8)[..., None]
        # gündüz görüntüsünün netliğini (ince ayrıntıyı) ekle: binalar keskin ve yerinde kalır
        a, b = max(0, r0 - 32), min(H, r1 + 32)
        dd = eq[a:b].astype(np.float32).mean(2); hp = (dd - cv2.GaussianBlur(dd, (0, 0), 2))[r0 - a:r0 - a + (r1 - r0)]
        lum = cv2.GaussianBlur(nn.mean(2), (0, 0), 3) / 255.0
        nn += (np.clip(hp, -40, 40) * np.clip(lum * 1.6, .08, 1) * hpk)[..., None]
        res[r0:r1] = np.clip(nn, 0, 255).astype(np.uint8)
    del bands
    np.save(f'{out}/_res.npy', res)                                           # gök ayarı denemeleri için ara sonuç
    _sky(res, eq, mask, dst)

def _sky(res, eq, mask, dst):
    H, W = res.shape[:2]
    # gök: maskeyle tek parça yapay gece göğü; ufuk rengi sütun sütun alttaki şehirden alınır (şerit kalmaz)
    h, w = 2048, 4096; ms = cv2.resize(mask, (w, h), interpolation=cv2.INTER_AREA); ns = cv2.resize(res, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32)
    sk = (ms > .5).sum(0)                                                     # her sütunda siluet satırı
    med = np.median(np.lib.stride_tricks.sliding_window_view(np.concatenate([sk[-75:], sk, sk[:75]]), 151), 1)
    sk = np.maximum(sk, med)                                                  # kuleler yok sayılır: genel ufuk çizgisi
    sk = np.convolve(np.concatenate([sk[-200:], sk, sk[:200]]), np.ones(401) / 401, 'same')[200:-200].astype(int)  # yumuşak: gökte dikey bant olmaz
    rows = np.arange(h)[:, None]; below = (rows >= sk[None] + 3) & (rows < sk[None] + 25)
    C = np.stack([(ns[..., c] * below).sum(0) / np.maximum(below.sum(0), 1) for c in range(3)], -1)
    C = np.stack([np.convolve(np.tile(C[:, c], 3), np.ones(301) / 301, 'same')[w:2 * w] for c in range(3)], -1)
    C = C * .85 + np.array([150, 105, 80.]) * .15
    base = night_sky(h, w, C.mean(0))
    up = np.clip((sk[None] - rows) / (h / 180 * 9), 0, 1) ** .7            # siluetten 9° yukarıya kadar ufuk rengi söner
    sky = (C[None] * (1 - up[..., None]) + base * up[..., None]).astype(np.float32)
    top = int(H * .56)                                                        # gök yalnızca üst kısımda
    sky = cv2.resize(sky, (W, H), interpolation=cv2.INTER_LINEAR)[:top]
    m3 = cv2.GaussianBlur(mask[:top], (0, 0), 3)[..., None]
    part = res[:top].astype(np.float32); day = eq[:top].astype(np.float32)
    # ufkun üstüne taşan kuleler (yapay zekâ çizmemiş olabilir): çevresindeki gök piksel piksel ayrılır, kule gündüzden koyu siluet
    skf = cv2.resize(sk[None].astype(np.float32), (W, 1), interpolation=cv2.INTER_LINEAR)[0] * H / h
    above = np.arange(top)[:, None] < skf[None] - 2
    tall = (mask[:top] < .5) & above
    if tall.any():
        mk = mask[:top].copy()
        for r in np.unique(np.nonzero(tall)[0]):
            row = day[r]; sky_px = mask[r] > .5
            sp = sky_px.astype(np.float32)[None]                             # yakındaki gök rengi (ufuk pusu yatayda değişir)
            ref = _blurw(row[None] * sp[..., None], 250)[0] / np.maximum(_blurw(sp, 250)[0], 1e-3)[:, None]
            dist = np.abs(row - ref).max(1); t = tall[r]
            mk[r, t] = np.clip((22 - dist[t]) / 10, 0, 1)                    # göğe benzeyen piksel = gök
        sil = tall & (mk < .5)
        part[sil] = part[sil] * .3 + day[sil] * np.array([.40, .32, .28]) * .7
        near = cv2.dilate(tall.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
        m3 = np.where(near[..., None], cv2.GaussianBlur(mk, (0, 0), 1.2)[..., None], m3)
    res[:top] = np.clip(part * (1 - m3) + sky * m3, 0, 255).astype(np.uint8)
    cv2.imwrite(dst, res, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print('merge', dst)

if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'split': split(sys.argv[2], sys.argv[3])
    elif c == 'gen': gen(sys.argv[2], *(sys.argv[3:4]))
    elif c == 'merge': merge(sys.argv[2], sys.argv[3], sys.argv[4])
