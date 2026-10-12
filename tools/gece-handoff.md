# Gerçekçi gece — devir notu (12 Ekim 2026)

Umut: ilk gece denemesi (tools/vr/night.py filtresi) "çok kötü", reddedildi. Önizlemeden gece düğmesi kaldırıldı.
Hedef kalite: Umut'un ChatGPT ile yaptığı örnek → /mnt/project-files/vaziyet-plani/gece-referans-chatgpt.png
Karar: Gemini ile üret (Umut "Gemini anahtarı" seçti, GEMINI_API_KEY ortam değişkeni olarak eklendi).

## Hazır araç: tools/vr/gece_ai.py
1. `split <sahneN.jpg> <klasör>` → 6 yüz (100° görüş, 2048 px): yuz_f/r/b/l/u/d.jpg
2. `gen <klasör> [model]` → GEMINI_API_KEY ile f r b l d yüzlerinin gecesi (gece_*.png). u (gök) gönderilmez, yapay gece göğü konur.
   Model adı varsayılan gemini-3-pro-image-preview; önce `GET /v1beta/models` ile mevcut görüntü modellerini kontrol et.
3. `merge <sahneN.jpg> <klasör> <çıkış.jpg>` → hizalama (kenar haritasında ECC, test edildi), yumuşak yüz birleştirme,
   gündüz netliği eklenir, 16384x8192 gece panoraması.
4. `night_tiles.py <sahneN.jpg> <geceN.jpg> assets/vr/sNn` karoları üretir (night_tiles önce night_eq çağırır: gece dosyası varsa onu kullanır).
5. Önizlemede gece düğmesi kodu duruyor (setNight, sid()), sadece düğme HTML'i ve `night` başlangıcı kaldırıldı (commit 5b13000'u geri al).

Panoramalar: `vr-panoramas` dalı, vr-panoramas/panoramalar/sahneN_360_16384x8192.jpg
Önce tek sahnede (s1) dene, Umut'a göster; beğenirse 7 sahne. Eski filtre karoları assets/vr/sNn yenileriyle değişir.
Kural: canlı vaziyet-plani.html'e "canlıya al" demeden dokunma; Türkçe, kısa.
