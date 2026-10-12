"""Gündüz panoramasından doğal gece görüntüsü üretir.
night(rgb uint8 HxWx3, elev derece HxW, seed) -> uint8
"""
import numpy as np, cv2

def _blur(x, s):
    return cv2.GaussianBlur(x, (0, 0), s, borderType=cv2.BORDER_REFLECT)

def night(img, elev, seed=1):
    rng = np.random.default_rng(seed)
    f = img.astype(np.float32) / 255.0
    lin = f ** 2.2
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    mx = f.max(2); mn = f.min(2); sat = (mx - mn) / (mx + 1e-4)
    H, W = L.shape

    # --- gökyüzü / deniz maskesi: mavi ve pürüzsüz
    blue = np.clip((B - R) * 6, 0, 1) * np.clip((B - G + .08) * 8, 0, 1)
    var = _blur(L * L, 3) - _blur(L, 3) ** 2
    smooth = np.clip(1 - np.sqrt(np.maximum(var, 0)) * 25, 0, 1)
    up = np.clip((elev + 1.0) / 2.0, 0, 1)            # ufkun üstü
    sky = np.clip(blue * 1.5 + 0.6, 0, 1) * np.clip(L * 3 - 0.6, 0, 1) * up
    sky = np.maximum(sky, np.clip((elev - 6) / 4, 0, 1))  # yukarısı her zaman gök
    sky = _blur(sky, 2)
    sea = blue * smooth * (1 - up)
    sea = _blur(np.clip(sea * 1.6, 0, 1), 4)

    detail = np.clip(np.sqrt(np.maximum(_blur(L * L, 2) - _blur(L, 2) ** 2, 0)) * 12, 0, 1)
    # --- zemin: ay ışığı + karanlık
    base = lin * 0.05
    moon = np.array([0.55, 0.68, 1.0], np.float32)
    lum = (0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2])[..., None]
    ground = base * 0.35 + (lum ** 0.85) * 0.13 * moon
    # sodyum sokak lambası yansıması: gri, doygun olmayan yüzeyler (yol, kaldırım)
    fb = _blur(f, 5); Lb = fb.mean(2); sb = (fb.max(2) - fb.min(2)) / (fb.max(2) + 1e-4)
    gray = np.clip(1 - sb * 6, 0, 1) * np.clip(1 - np.abs(Lb - .40) * 6, 0, 1) * (1 - sky)
    sodium = np.array([1.0, 0.55, 0.22], np.float32)
    ground += (_blur(gray, 2) * 0.13)[..., None] * sodium

    # --- pencere ışıkları: komşuluğuna göre koyu, dokulu yerler
    loc = _blur(L, 4)
    dark = np.clip((loc - L) / (loc + 1e-3) * 4, 0, 1)
    detail = np.clip(np.sqrt(np.maximum(_blur(L * L, 2) - _blur(L, 2) ** 2, 0)) * 12, 0, 1)
    green = np.clip((G - np.maximum(R, B)) * 15 + .1, 0, 1) * np.clip(1.2 - L * 2, 0, 1)
    build = (1 - sky) * (1 - sea) * (1 - green)
    # pencere ölçeğinde rastgele bloklar (bazı odalar yanık)
    cell = 5
    rnd = rng.random((H // cell + 2, W // cell + 2)).astype(np.float32)
    rnd = cv2.resize(rnd, (W + 2 * cell, H + 2 * cell), interpolation=cv2.INTER_NEAREST)
    oy, ox = rng.integers(0, cell, 2)
    rnd = rnd[oy:oy + H, ox:ox + W]
    on = np.clip((rnd - 0.89) * 15, 0, 1)
    win = np.clip(dark * 1.5 - .3, 0, 1) * np.clip(detail * 1.5 - .3, 0, 1) * build * on
    # ılık / beyaz ışık karışımı
    tint = rng.random((H // 7 + 2, W // 7 + 2)).astype(np.float32)
    tint = cv2.resize(tint, (W + 14, H + 14), interpolation=cv2.INTER_NEAREST)[3:3 + H, 3:3 + W][..., None]
    warm = np.array([1.0, 0.72, 0.38], np.float32); cool = np.array([1.0, 0.9, 0.75], np.float32)
    wcol = warm * tint + cool * (1 - tint)
    emit = win[..., None] * wcol * 0.7
    # uzaktaki şehir dokusu: küçük, yoğun ışık noktaları
    far = np.clip(1 - np.abs(elev) / 25, 0.15, 1)
    spark = (rng.random((H, W)).astype(np.float32) > 1 - 0.0018 * far) * detail * build * np.clip(dark * 3, 0, 1)
    emit += _blur(spark, 0.8)[..., None] * warm * 1.0
    # yollar/araçlar: parlak küçük noktalar (farlar)
    hi = np.clip((L - _blur(L, 3) - 0.3) * 6, 0, 1) * (1 - sky) * (1 - sea)
    emit += hi[..., None] * np.array([1.0, 0.85, 0.65], np.float32) * 0.3

    # --- gece göğü
    t = np.clip(elev / 35.0, 0, 1)[..., None]
    zen = np.array([0.004, 0.009, 0.040], np.float32)
    hor = np.array([0.07, 0.06, 0.085], np.float32)  # şehir ışığı halesi
    nsky = hor * (1 - t) ** 2 + zen * (1 - (1 - t) ** 2)
    stars = (rng.random((H, W)) > 0.9993).astype(np.float32) * np.clip((elev - 12) / 20, 0, 1)
    nsky += _blur(stars, 0.6)[..., None] * 0.35
    # deniz: koyu, gökyüzünü hafif yansıtır
    nsea = np.array([0.006, 0.009, 0.018], np.float32) + lum * 0.03

    out = ground + emit
    out = out * (1 - sea[..., None]) + (nsea + emit * 0.3) * sea[..., None]
    out = out * (1 - sky[..., None]) + nsky * sky[..., None]
    # ufuk sisi
    haze = np.exp(-np.abs(elev) / 3.0)[..., None] * 0.015 * np.array([1.0, 0.75, 0.6], np.float32)
    out += haze
    # parıltı (bloom)
    glow = _blur(emit, 3) * 0.6 + _blur(emit, 12) * 0.35 + _blur(emit, 40) * 0.5
    out += glow
    out = out / (1 + out * 0.25)                       # tonemap
    return (np.clip(out, 0, 1) ** (1 / 2.2) * 255 + .5).astype(np.uint8)

def night_eq(src, dst, strip=512, pad=96, seed=1):
    """Equirectangular panoramayı şeritler halinde işler (bellek için)."""
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    eq = np.asarray(Image.open(src).convert('RGB'))
    H, W = eq.shape[:2]
    out = np.empty_like(eq)
    for i, r0 in enumerate(range(0, H, strip)):
        r1 = min(H, r0 + strip); a = max(0, r0 - pad); b = min(H, r1 + pad)
        part = np.concatenate([eq[a:b, -pad:], eq[a:b], eq[a:b, :pad]], 1)
        rows = np.arange(a, b, dtype=np.float32)
        elev = (90 - (rows + .5) / H * 180)[:, None] * np.ones((1, part.shape[1]), np.float32)
        n = night(part, elev, seed * 1000 + i)
        out[r0:r1] = n[r0 - a:r0 - a + (r1 - r0), pad:pad + W]
    Image.fromarray(out).save(dst, quality=92)

if __name__ == '__main__':
    import sys
    night_eq(sys.argv[1], sys.argv[2])
