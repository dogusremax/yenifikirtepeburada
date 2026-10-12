# 360° sanal tur (vr-tur-onizleme.html)

- Kaynak: `vr-panoramas` dalındaki 16384×8192 panoramalar (main'e alınmaz).
- `tiles.py <panorama.jpg> assets/vr/sN` → Pannellum multires karoları (yüz 4096 px, 512 px karo, 4 seviye + fallback).
- `thumb.py` → assets/vr/thumb (s = yuvarlak, w = geniş küçük resim).
- Sayfa `tur.tpl.html` şablonundan üretilir: `python3 tools/vr/build.py`. Etap/kamera verisi (INFO, POLY, LBL, PCAM, SC) vaziyet-plani-eski.html'den (eski canlı sayfa) okunur; orada değişirse yeniden üretin.

## Gece görünümü (vaziyet-plani-vr-onizleme.html)
- `night.py` gündüz panoramasından gece hali üretir (mavi saat göğü, ay ışığı, pencere/sokak ışıkları, parıltı). Emlak Konut'ta gece versiyonu yok, bu yüzden görüntü işleme ile üretiliyor.
- `night_tiles.py <sahneN.jpg> <geceN.jpg> assets/vr/sNn` → gece karoları (1-4 + fb3k), sahne başına ~18 MB.
- Sayfada Gündüz/Gece düğmesi aynı bakış açısında `sN` ↔ `sNn` sahnesine geçer; `?gece=1` gece açar.
