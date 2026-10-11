# 360° sanal tur (vr-tur-onizleme.html)

- Kaynak: `vr-panoramas` dalındaki 16384×8192 panoramalar (main'e alınmaz).
- `tiles.py <panorama.jpg> assets/vr/sN` → Pannellum multires karoları (yüz 4096 px, 512 px karo, 4 seviye + fallback).
- `thumb.py` → assets/vr/thumb (s = yuvarlak, w = geniş küçük resim).
- Sayfa `tur.tpl.html` şablonundan üretilir: `python3 tools/vr/build.py`. Etap/kamera verisi (INFO, POLY, LBL, PCAM, SC) vaziyet-plani.html'den okunur; orada değişirse yeniden üretin.
