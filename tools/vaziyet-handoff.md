# Vaziyet planı 360° — devir notu (12 Ekim 2026)

## Kurallar (Umut)
- Her zaman Türkçe yaz, kısa tut.
- **Bana göstermeden siteyi canlı yapma.** Önce önizlemede göster, "canlıya al" demeden `vaziyet-plani.html`'e dokunma.
- Etap sınırlarını kendin çizme. Emlak Konut VR sayfasını (https://fikirtepe.emlakkonut.com.tr/tr/vr) bire bir kullan, bize uyarla.
- Kat planları için: "ötekileri bozma". Sadece eksikler eklenir, var olan 49 plana dokunulmaz.

## Yapılanlar
- Önizleme: `vaziyet-plani-vr-onizleme.html` (noindex), adresi https://yenifikirtepeburada.com/vaziyet-plani-vr-onizleme.html
  - Pannellum (`assets/vendor/pannellum`) ile 7 sahne, `assets/vr/s1..s7` karoları (4096 küp, 4 seviye).
  - Sahne açıları, sahne geçişleri ve etap pinleri resmi `vr.js`'ten birebir alındı (`SC` dizisi, derece; Marzipano pitch işareti ters çevrildi).
    Pinler resmi sitedeki görünür konumla piksel piksel aynı: Pannellum öğeyi ortalar, `.pin` `margin:25px 0 0 20px` ile resmi görünüme kaydırılır.
  - Etaba dokununca `zoomTo()` yakınlaşır. Etap kartın dışındaki boş alanın ortasına gelir, kart kapanınca `home()` ile geri döner.
  - Kart, canlı `vaziyet-plani.html` kartıyla aynı mantıkta: `teslim-takvimi.json` (yedek: `YEDEK`), sayaçlar, ilerleme çubuğu, butonlar. Pinler teslim durumuna göre renkli.
  - Son istek üzerine kart çok küçültüldü: telefonda yaklaşık 175 px yükseklikte, bilgisayarda sağ altta 280 px genişlikte.
  - WebGL olmayan tarayıcılar için `assets/vr/sN/fb3k/` (3072 px küp yüzleri) eklendi. Eski `fallback/` ve `vr-tur-onizleme.html` değişmedi.
- Ekran görüntüleri Umut'un bilgisayarında: `remax-dogus-crm/ekran-goruntuleri/vaziyet-vr-onizleme/`.

## Açık işler
1. Umut'un son kart küçültmesine verdiği tepki bekleniyor. Beğenirse "canlıya al" der, o zaman `vaziyet-plani.html` bu sayfayla değiştirilir (onay şart).
2. Görüntü kalitesi: Bizim karolar 4096'da (resmi siteyle aynı seviye 4). Resmi sitede bir de 8192 (seviye 5) var. Gerekirse eklenebilir ama site boyutu yüzlerce MB büyür. Önce Umut'a sor.
3. Kat planları 5-17 ve 5-18 (5. Etap, A Blok 3+1) hâlâ eksik. `tools/kat3d/plans/5-17.json` ve `5-18.json` hazır (`ready: true`).
   `tools/kat3d/render_queue.py` (bpy + Pillow) ile render edilip yayımlanacak. Umut onay verdi ("tamamla", "ötekileri bozma").

## Kaynak notları
- Resmi sahne verisi: https://fikirtepe.emlakkonut.com.tr/js/vr/vr.js?v=1650364625 (scenes: initialViewParameters, linkHotspots, infoHotspots; vurgu görselleri dizisi boş).
- Panoramalar: `vr-panoramas` dalı (16384×8192), karo üretimi `tools/vr/tiles.py`.
