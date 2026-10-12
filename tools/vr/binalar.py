"""Her bakış noktasında binaların sınırlarını MobileSAM ile önceden çıkarır -> assets/vr/binalar/sK.json
Düzenleme sayfası (vaziyet-duzenle.html) dokunulan noktayı içeren en küçük makul şekli seçer.

  MOBILE_SAM=/yol/MobileSAM python3 binalar.py <sahne no 1-7> <panorama.jpg> <çıkış.json>
MobileSAM kodu ve ağırlığı: github.com/ChaoningZhang/MobileSAM (mobile_sam/ + mobile_sam.pt aynı klasörde)
Açılış bakışının çevresi (110°x80°, 3072x2048 düz görüntü) 1024'lük örtüşen 12 parçayla taranır.
Çıktı: [[alan_px, [yaw, pitch, yaw, pitch, ...]], ...] (derece)
"""
import sys, os, json, re, numpy as np, cv2, torch
sys.path.insert(0, os.environ.get('MOBILE_SAM', '.'))
from mobile_sam import sam_model_registry, SamAutomaticMaskGenerator
torch.set_num_threads(os.cpu_count())
cv2.setNumThreads(os.cpu_count())
T = 1024

def rot(yaw, pitch):
    y, p = np.radians(yaw), np.radians(pitch)
    Ry = np.array([[np.cos(y), 0, np.sin(y)], [0, 1, 0], [-np.sin(y), 0, np.cos(y)]])
    Rx = np.array([[1, 0, 0], [0, np.cos(p), np.sin(p)], [0, -np.sin(p), np.cos(p)]])
    return Ry @ Rx

def view(eq, yaw, pitch, hf, vf, W, H):
    """Açılış bakışı çevresinin düz (perspektif) görüntüsü + her pikselin yönü (derece)."""
    th, tv = np.tan(np.radians(hf / 2)), np.tan(np.radians(vf / 2))
    x, y = np.meshgrid(((np.arange(W) + .5) / W * 2 - 1) * th, -((np.arange(H) + .5) / H * 2 - 1) * tv)
    d = np.stack([x, y, np.ones_like(x)], -1) @ rot(yaw, pitch).T
    lon = np.arctan2(d[..., 0], d[..., 2]); lat = np.arctan2(d[..., 1], np.hypot(d[..., 0], d[..., 2]))
    Eh, Ew = eq.shape[:2]
    u = ((lon / (2 * np.pi) + .5) * Ew - .5).astype(np.float32); v = ((.5 - lat / np.pi) * Eh - .5).astype(np.float32)
    return cv2.remap(eq, u, v, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP), np.degrees(lon), np.degrees(lat)

def iou_dup(gb, s, kept):
    bx, by, bw, bh = gb
    for kb, (ky, kx, km) in kept:
        ix = max(0, min(bx + bw, kb[0] + kb[2]) - max(bx, kb[0])); iy = max(0, min(by + bh, kb[1] + kb[3]) - max(by, kb[1]))
        if ix * iy < .5 * min(bw * bh, kb[2] * kb[3]): continue
        X0, Y0 = min(bx, kb[0]), min(by, kb[1]); X1, Y1 = max(bx + bw, kb[0] + kb[2]), max(by + bh, kb[1] + kb[3])
        A = np.zeros((Y1 - Y0 + 1, X1 - X0 + 1), bool); B = A.copy()
        A[by - Y0:by - Y0 + s.shape[0], bx - X0:bx - X0 + s.shape[1]] = s
        B[ky - Y0:ky - Y0 + km.shape[0], kx - X0:kx - X0 + km.shape[1]] = km
        if (A & B).sum() / max(1, (A | B).sum()) > .7: return True
    return False

def main(k, pano, out, pps=24):
    html = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../vaziyet-plani-vr-onizleme.html')).read()
    SC = json.loads(re.search(r'var SC=(\[.*?\]);\n', html).group(1))[k - 1]
    sam = sam_model_registry['vit_t'](checkpoint=os.path.join(os.environ.get('MOBILE_SAM', '.'), 'mobile_sam.pt')); sam.eval()
    gen = SamAutomaticMaskGenerator(sam, points_per_side=pps, pred_iou_thresh=0.86, stability_score_thresh=0.9, min_mask_region_area=120)
    eq = np.ascontiguousarray(cv2.imread(pano)[..., ::-1])
    W, H = 3072, 2048
    img, LON, LAT = view(eq, SC['y'], max(-89.9, SC['p']), 110, 80, W, H)
    shapes, kept = [], []
    xs, ys = [0, 768, 1536, W - T], [0, 768, H - T]
    print(f'sahne {k}: {len(xs) * len(ys)} parça', flush=True)
    for ty in ys:
        for tx in xs:
            crop = np.ascontiguousarray(img[ty:ty + T, tx:tx + T]); h, w = crop.shape[:2]
            with torch.no_grad(): ms = gen.generate(crop)
            for m in ms:
                s = m['segmentation']; a = m['area']
                if a < 150 or a > .35 * h * w: continue
                bx, by, bw, bh = m['bbox']
                # parça kenarına değen (kesik) şekiller komşu parçada bütün bulunur
                if (bx <= 1 and tx > 0) or (by <= 1 and ty > 0) or (bx + bw >= w - 2 and tx + T < W) or (by + bh >= h - 2 and ty + T < H): continue
                sub = s[by:by + bh + 1, bx:bx + bw + 1]; gb = (tx + bx, ty + by, sub.shape[1], sub.shape[0])
                if iou_dup(gb, sub, kept): continue
                kept.append((gb, (ty + by, tx + bx, sub.copy())))
                cs, _ = cv2.findContours(s.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                c = cv2.approxPolyDP(max(cs, key=cv2.contourArea), 1.5, True)[:, 0]
                if len(c) < 3: continue
                poly = []
                for px, py in c:
                    gx, gy = min(W - 1, tx + px), min(H - 1, ty + py)
                    poly += [round(float(LON[gy, gx]), 3), round(float(LAT[gy, gx]), 3)]
                shapes.append([int(a), poly])
            print(f'  parça {tx},{ty}: toplam {len(shapes)} şekil', flush=True)
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    json.dump(shapes, open(out, 'w'), separators=(',', ':'))
    print('bitti', out, len(shapes), os.path.getsize(out) // 1000, 'KB')

if __name__ == '__main__':
    main(int(sys.argv[1]), sys.argv[2], sys.argv[3])
