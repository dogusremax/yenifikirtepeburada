#!/usr/bin/env python3
"""Emlak Konut "Teslim İşlemleri" sayfasındaki Yeni Fikirtepe teslim
programlarını (PDF) okuyup teslim-takvimi.json dosyasını üretir.

- Sayfadaki her "Yeni Fikirtepe ... Teslim Programı" başlığı ve PDF linki bulunur.
- PDF, pdftotext -layout ile metne çevrilir; her satırdan blok, kapı no,
  teslim tarihi ve saati okunur.
- Okunamayan ya da şüpheli az satır çıkan etap için eski veri korunur.
- Veri değişmediyse dosyaya dokunulmaz (gereksiz commit olmaz).

Çıkış kodu: tüm etaplar okunduysa 0, en az biri okunamadıysa 2.
"""
import html, json, os, re, subprocess, sys, tempfile, urllib.request
from datetime import datetime, timezone, timedelta

SAYFA = "https://www.emlakkonut.com.tr/tr-TR/teslim-islemleri"
DOSYA = sys.argv[1] if len(sys.argv) > 1 else "teslim-takvimi.json"
UA = {"User-Agent": "Mozilla/5.0 (yenifikirtepeburada.com teslim takvimi)"}
AYLAR = {"ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "mayis": 5,
         "haziran": 6, "temmuz": 7, "ağustos": 8, "agustos": 8, "eylül": 9, "eylul": 9,
         "ekim": 10, "kasım": 11, "kasim": 11, "aralık": 12, "aralik": 12}


def indir(url, yol=None, deneme=4):
    son = None
    for i in range(deneme):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                veri = r.read()
            if yol:
                open(yol, "wb").write(veri)
            return veri
        except Exception as e:  # ağ hatası: kısa bekleyip tekrar dene
            son = e
            print(f"  indirme denemesi {i + 1} başarısız: {e}")
            import time; time.sleep(5 * (i + 1))
    raise son


def kucuk(s):
    return s.replace("İ", "i").replace("I", "ı").lower()


def programlari_bul(sayfa_html):
    """[(başlık, pdf_url)] — yalnız Fikirtepe teslim programları."""
    sonuc, gorulen, onceki = [], set(), 0
    for m in re.finditer(r'<a\b[^>]*href="([^"]+\.pdf)"', sayfa_html, re.I):
        bas, onceki = max(onceki, m.start() - 1500), m.end()
        url = html.unescape(m.group(1))
        if url.startswith("/"):
            url = "https://www.emlakkonut.com.tr" + url
        once = re.sub(r"<[^>]+>", "\n", sayfa_html[bas:m.start()])
        once = html.unescape(once)
        basliklar = [b.strip() for b in re.findall(r"[^\n]*Teslim\s+Program[ıi][^\n]*", once, re.I)]
        if not basliklar:
            continue
        baslik = re.sub(r"\s+", " ", basliklar[-1])
        if "fikirtepe" not in kucuk(baslik) or url in gorulen:
            continue
        gorulen.add(url)
        sonuc.append((baslik, url))
    return sonuc


def etap_kimligi(baslik):
    """'Yeni Fikirtepe-3. Etap 2. Kısım Teslim Programı' -> ('3-2', '3. Etap 2. Kısım')"""
    ad = re.sub(r"(?i)^.*?fik[iİı]rtepe\s*[-–]?\s*", "", baslik)
    ad = re.sub(r"(?i)\s*teslim\s+program[ıi].*$", "", ad).strip(" -–")
    if re.fullmatch(r"\d+", ad):
        ad = ad + ". Etap"
    sayilar = re.findall(r"\d+", ad)
    return ("-".join(sayilar) or kucuk(ad).replace(" ", "-")), ad


SATIR = re.compile(
    r"[İI]STANBUL\s+KADIK[ÖO]Y\s+(\d+)\s+([\d/-]+)\s+(\S+)\s+(\S+)\s+"
    r"(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(\d{4})"
    r"(?:\s+[A-Za-zÇĞİÖŞÜçğıöşü]+)?(?:\s+(\d{1,2})[:.](\d{2}))?")


def pdf_oku(url):
    with tempfile.TemporaryDirectory() as d:
        pdf = os.path.join(d, "p.pdf")
        indir(url, pdf)
        metin = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
    satirlar = []
    for m in SATIR.finditer(metin):
        ada, parsel, blok, kapi, gun, ay, yil, ss, dd = m.groups()
        ayno = AYLAR.get(kucuk(ay))
        if not ayno:
            continue
        tarih = f"{yil}-{ayno:02d}-{int(gun):02d}"
        saat = f"{int(ss):02d}:{dd}" if ss else None
        satirlar.append((blok.upper(), kapi, tarih, saat))
    print(f"  {len(satirlar)} daire okundu ({len(metin)} karakter metin)")
    if not satirlar:
        print("  --- PDF metninden örnek ---\n" + metin[:1500] + "\n  ---")
    return satirlar


def kapi_sirasi(k):
    m = re.match(r"(\d+)(.*)", k)
    return (int(m.group(1)), m.group(2)) if m else (10**9, k)


def etap_verisi(satirlar):
    bloklar, randevu = {}, []
    for blok, kapi, tarih, saat in satirlar:
        b = bloklar.setdefault(blok, {"b": blok, "bas": tarih, "bit": tarih, "daire": 0})
        b["bas"], b["bit"] = min(b["bas"], tarih), max(b["bit"], tarih)
        b["daire"] += 1
    # Ardışık kapı numaralarını aynı gün/saatte tek kayıtta birleştir: [blok, ilk, son, tarih, saat]
    for blok in bloklar:
        liste = sorted({(k, t, s) for b, k, t, s in satirlar if b == blok}, key=lambda x: kapi_sirasi(x[0]))
        for k, t, s in liste:
            son = randevu[-1] if randevu else None
            if (son and son[0] == blok and son[3] == t and son[4] == s and k.isdigit()
                    and isinstance(son[2], int) and int(k) == son[2] + 1):
                son[2] = int(k)
            else:
                v = int(k) if k.isdigit() else k
                randevu.append([blok, v, v, t, s])
    sirali = sorted(bloklar.values(), key=lambda b: (b["bas"], b["bit"], b["b"]))
    return sirali, randevu


def main():
    try:
        eski = json.load(open(DOSYA, encoding="utf-8"))
    except FileNotFoundError:
        eski = {"etaplar": []}
    eskiler = {e["id"]: e for e in eski.get("etaplar", [])}

    print("Teslim İşlemleri sayfası okunuyor…")
    sayfa = indir(SAYFA).decode("utf-8", "replace")
    programlar = programlari_bul(sayfa)
    print(f"{len(programlar)} Fikirtepe teslim programı bulundu")
    if not programlar:
        print("Sayfada program bulunamadı; mevcut veri korunuyor.")
        return 2

    hata, yeni, simdi = False, [], datetime.now(timezone(timedelta(hours=3))).strftime("%Y-%m-%d")
    for baslik, url in programlar:
        eid, ad = etap_kimligi(baslik)
        print(f"- {baslik} [{eid}] {url}")
        e_eski = eskiler.pop(eid, None)
        try:
            satirlar = pdf_oku(url)
        except Exception as ex:
            print(f"  PDF okunamadı: {ex}")
            satirlar = []
        eski_sayi = sum(b.get("daire", 0) for b in (e_eski or {}).get("bloklar", []))
        if not satirlar or (eski_sayi and len(satirlar) < eski_sayi * 0.5):
            print("  Okuma başarısız ya da şüpheli; eski veri korunuyor.")
            hata = True
            if e_eski:
                yeni.append(e_eski)
            continue
        bloklar, randevu = etap_verisi(satirlar)
        e = {"id": eid, "ad": ad, "baslik": baslik, "pdf": url, "daire": len(satirlar),
             "bloklar": bloklar, "randevu": randevu}
        icerik = lambda x: {k: v for k, v in (x or {}).items() if k != "guncelleme"}
        e["guncelleme"] = e_eski.get("guncelleme", simdi) if icerik(e_eski) == icerik(e) else simdi
        yeni.append(e)
    # Sayfadan kalkan etapları silme, olduğu gibi tut
    yeni.extend(eskiler.values())

    cikti = {"kaynak": SAYFA, "etaplar": yeni}
    if cikti != {k: v for k, v in eski.items() if k in ("kaynak", "etaplar")}:
        with open(DOSYA, "w", encoding="utf-8") as f:
            json.dump(cikti, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
        print(f"{DOSYA} güncellendi")
    else:
        print("Değişiklik yok")
    return 2 if hata else 0


if __name__ == "__main__":
    sys.exit(main())
