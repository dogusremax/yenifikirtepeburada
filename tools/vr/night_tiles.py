"""Gece karoları: night_tiles.py <gündüz-panorama.jpg> <gece-panorama.jpg> assets/vr/sNn
Gece panoraması yoksa önce night.py ile üretir. Karolar tiles.py ile aynı düzende (1-4 + fb3k)."""
import sys, os, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from cube import face, F
from night import night_eq
Image.MAX_IMAGE_PIXELS = None
src, nsrc, out = sys.argv[1:4]
if not os.path.exists(nsrc): night_eq(src, nsrc)
N, T = 4096, 512
eq = np.asarray(Image.open(nsrc).convert('RGB'))
for f in F:
    im = face(eq, f, N)
    for lv in (4, 3, 2, 1):
        s = T * 2 ** (lv - 1); x = im if s == N else im.resize((s, s), Image.LANCZOS)
        d = f'{out}/{lv}'; os.makedirs(d, exist_ok=True)
        for r in range(s // T):
            for c in range(s // T):
                x.crop((c*T, r*T, c*T+T, r*T+T)).save(f'{d}/{f}{r}_{c}.jpg', quality=78, optimize=True, progressive=True)
    os.makedirs(f'{out}/fb3k', exist_ok=True)
    im.resize((3072, 3072), Image.LANCZOS).save(f'{out}/fb3k/{f}.jpg', quality=80, optimize=True)
print('done', out)
