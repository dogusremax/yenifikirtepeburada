"""Gerçekçi gece: panoramayı örtüşen yüzlere böl -> Gemini ile gece yap -> hizala -> panoramaya geri birleştir.

  python3 gece_ai.py split <sahne.jpg> <klasör>          # 6 yüz, 100° görüş, 2048 px (yuz_*.jpg)
  python3 gece_ai.py gen   <klasör> [model]              # GEMINI_API_KEY ile her yüzün gecesini üretir (gece_*.png)
  python3 gece_ai.py merge <sahne.jpg> <klasör> <çıkış.jpg>  # hizalar, gündüz netliğini ekler, 16384x8192 panorama

Yüzler: f r b l (yan), u (gök, yapay zekâya gönderilmez), d (aşağı).
"""
import sys, os, json, base64, time, numpy as np, cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
FOV = 100.0
S = 2048
# yüz yönleri (yaw, pitch) derece
FACES = {'f': (0, 0), 'r': (90, 0), 'b': (180, 0), 'l': (-90, 0), 'u': (0, 90), 'd': (0, -90)}

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

def gen(out, model='gemini-3-pro-image-preview'):
    import urllib.request
    key = os.environ['GEMINI_API_KEY']
    for f in 'frbld':
        dst = f'{out}/gece_{f}.png'
        if os.path.exists(dst): continue
        b64 = base64.b64encode(open(f'{out}/yuz_{f}.jpg', 'rb').read()).decode()
        body = {'contents': [{'parts': [{'text': PROMPT}, {'inline_data': {'mime_type': 'image/jpeg', 'data': b64}}]}],
                'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '1:1', 'imageSize': '2K'}}}
        req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
                                     json.dumps(body).encode(), {'Content-Type': 'application/json', 'x-goog-api-key': key})
        for t in range(3):
            try:
                r = json.load(urllib.request.urlopen(req, timeout=300)); break
            except Exception as e:
                print('hata', f, e); time.sleep(10 * (t + 1))
        else:
            raise SystemExit('üretilemedi: ' + f)
        parts = r['candidates'][0]['content']['parts']
        img = [p for p in parts if 'inlineData' in p or 'inline_data' in p][0]
        data = (img.get('inlineData') or img.get('inline_data'))['data']
        open(dst, 'wb').write(base64.b64decode(data)); print('gece', dst)

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

def sky(n):
    d = dirs('u', n); el = np.degrees(np.arctan2(d[..., 1], np.hypot(d[..., 0], d[..., 2])))
    t = np.clip((el - 45) / 45, 0, 1)[..., None]
    a = np.array([60, 30, 18.]); b = np.array([40, 16, 6.])  # BGR
    return (a * (1 - t) + b * t).astype(np.uint8)

def merge(src, out, dst, W=16384):
    H = W // 2; n = S
    eq = cv2.imread(src).astype(np.float32)
    acc = np.zeros((H, W, 3), np.float32); wsum = np.zeros((H, W), np.float32)
    lon = (np.arange(W) + .5) / W * 2 * np.pi - np.pi; lat = np.pi / 2 - (np.arange(H) + .5) / H * np.pi
    t = np.tan(np.radians(FOV / 2))
    for f in FACES:
        p = f'{out}/gece_{f}.png'
        day = cv2.imread(f'{out}/yuz_{f}.jpg')
        night = align(day, cv2.imread(p)) if os.path.exists(p) else (sky(n) if f == 'u' else None)
        if night is None: continue
        R = rot(*FACES[f])
        for r0 in range(0, H, 512):
            la = lat[r0:r0 + 512][:, None]; lo = lon[None, :]
            d = np.stack([np.cos(la) * np.sin(lo), np.sin(la) * np.ones_like(lo), np.cos(la) * np.cos(lo)], -1) @ R  # dünya -> yüz
            z = d[..., 2]; ok = z > 1e-3
            x = np.where(ok, d[..., 0] / np.maximum(z, 1e-3) / t, 9); y = np.where(ok, -d[..., 1] / np.maximum(z, 1e-3) / t, 9)
            inside = (np.abs(x) < 1) & (np.abs(y) < 1)
            w = np.clip((1 - np.maximum(np.abs(x), np.abs(y))) * 6, 0, 1) * inside  # kenarlarda yumuşak geçiş
            px = ((x + 1) / 2 * n - .5).astype(np.float32); py = ((y + 1) / 2 * n - .5).astype(np.float32)
            sm = cv2.remap(night, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
            acc[r0:r0 + 512] += sm * w[..., None]; wsum[r0:r0 + 512] += w
    night = acc / np.maximum(wsum, 1e-4)[..., None]
    # gündüz görüntüsünün netliğini (ince ayrıntıyı) gece görüntüsüne ekle: binalar keskin ve yerinde kalır
    if eq.shape[1] != W: eq = cv2.resize(eq, (W, H), interpolation=cv2.INTER_AREA)
    for r0 in range(0, H, 1024):
        a, b = max(0, r0 - 64), min(H, r0 + 1024 + 64)
        dd = eq[a:b]; hp = dd - cv2.GaussianBlur(dd, (0, 0), 3)
        nn = night[a:b]; lum = cv2.GaussianBlur(nn.mean(2), (0, 0), 3) / 255.0
        night[a:b] = nn + hp * np.clip(lum * 1.6, 0.08, 1)[..., None] * 0.9
    cv2.imwrite(dst, np.clip(night, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print('merge', dst)

if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'split': split(sys.argv[2], sys.argv[3])
    elif c == 'gen': gen(sys.argv[2], *(sys.argv[3:4]))
    elif c == 'merge': merge(sys.argv[2], sys.argv[3], sys.argv[4])
