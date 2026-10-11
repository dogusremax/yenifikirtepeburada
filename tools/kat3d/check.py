"""Plan geometrisi kontrolü: python3 check.py <plan_id> [--render]
- Her odanın çizilen alanını (ölçek tüm odalardan) resmi m² ile karşılaştırır.
- check_<id>.png: orijinal görsel üzerine odalar (renkli), duvar boşlukları (kapı mavi, pencere camgöbeği,
  geçiş yeşil) ve mobilyalar (turuncu) çizilir. --render ile yanına hızlı bir tepeden render eklenir."""
import json, math, os, sys, subprocess
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
pid = sys.argv[1]; P = json.load(open(os.path.join(HERE, 'plans', pid + '.json')))
def poly(g): return [[g[0], g[1]], [g[2], g[1]], [g[2], g[3]], [g[0], g[3]]] if isinstance(g[0], (int, float)) else g
def area(p): return abs(sum(p[i][0] * p[(i+1) % len(p)][1] - p[(i+1) % len(p)][0] * p[i][1] for i in range(len(p)))) / 2
sa = sum(area(poly(r[4])) for r in P['rooms']); sm = sum(r[2] for r in P['rooms']); ppm = math.sqrt(sa / sm)
print('ölçek: %.1f px/m' % ppm)
bad = 0
for r in P['rooms']:
    p = poly(r[4])
    for i in range(len(p)):
        a, b = p[i], p[(i+1) % len(p)]
        if a[0] != b[0] and a[1] != b[1]: print('  UYARI %s: kenar yatay/dikey değil %s-%s' % (r[0], a, b))
    m = area(p) / ppm ** 2; d = (m - r[2]) / r[2] * 100
    flag = '  <-- KONTROL ET' if abs(d) > 12 else ''
    if flag: bad += 1
    print('  %-5s %-22s resmi %6.2f  çizilen %6.2f  (%+.0f%%)%s' % (r[0], r[1], r[2], m, d, flag))
img = Image.open(os.path.join(HERE, '..', '..', 'kat-planlari', P['src'])).convert('RGB') if P.get('src') else None
if img:
    ov = img.copy(); d = ImageDraw.Draw(ov, 'RGBA')
    cols = [(220, 30, 40, 70), (30, 90, 220, 70), (30, 160, 60, 70), (200, 120, 0, 70), (140, 40, 200, 70), (0, 160, 160, 70)]
    for i, r in enumerate(P['rooms']):
        p = [tuple(q) for q in poly(r[4])]; d.polygon(p, fill=cols[i % len(cols)], outline=(0, 0, 0, 255))
        cx = sum(q[0] for q in p) / len(p); cy = sum(q[1] for q in p) / len(p); d.text((cx - 10, cy), r[0], fill=(0, 0, 0, 255))
    for k, col in (('doors', (0, 0, 255, 255)), ('wins', (0, 200, 220, 255)), ('opens', (0, 170, 0, 255))):
        for c in P.get(k, []):
            if c[0] == 'h': d.line([(c[2], c[1]), (c[3], c[1])], fill=col, width=7)
            else: d.line([(c[1], c[2]), (c[1], c[3])], fill=col, width=7)
    for f in P.get('furn', []):
        b = f[1]; d.rectangle(b, outline=(255, 120, 0, 255), width=3); d.text((b[0] + 3, b[1] + 3), f[0], fill=(160, 60, 0, 255))
    xs = [q[0] for r in P['rooms'] for q in poly(r[4])]; ys = [q[1] for r in P['rooms'] for q in poly(r[4])]
    box = (max(0, min(xs) - 60), max(0, min(ys) - 60), min(img.width, max(xs) + 60), min(img.height, max(ys) + 60))
    ov = ov.crop(box); out = ov
    if '--render' in sys.argv:
        tp = os.path.join(HERE, 'chk_' + pid + '.png')
        subprocess.run([sys.executable, os.path.join(HERE, 'build.py'), pid, 'top', tp, '520', '6'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(tp):
            t = Image.open(tp).convert('RGBA'); bg = Image.new('RGBA', t.size, (238, 241, 248, 255)); bg.alpha_composite(t)
            t = bg.convert('RGB'); t = t.resize((int(t.width * ov.height / t.height), ov.height))
            out = Image.new('RGB', (ov.width + t.width + 10, ov.height), 'white'); out.paste(ov, (0, 0)); out.paste(t, (ov.width + 10, 0))
        else: print('RENDER BAŞARISIZ')
    fn = os.path.join(HERE, 'check_' + pid + '.png'); out.save(fn); print('görsel:', fn)
print('sorunlu oda:', bad)
