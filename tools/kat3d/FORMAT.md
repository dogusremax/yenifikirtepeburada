# 3D kat planı geometri dosyası (tools/kat3d/plans/<id>.json)

Her plan, `kat-planlari/etapE-NN.jpg` görselinden (2000×1300 px) elle çıkarılan bir JSON dosyasıdır.
Tüm koordinatlar **o görseldeki piksel** koordinatlarıdır (x sağa, y aşağı). Ölçek otomatik hesaplanır:
odaların piksel alanları toplamı resmi m² toplamına oranlanır, bu yüzden oda poligonları doğru olmalı.

Örnek: `plans/11-y1.json` (görsel etap11-02.jpg). İlk iş onu ve `check_11-y1.png` çıktısını incele.

## Alanlar
```
id     "E-NN"   (etap-dosya no, iki haneli: "11-03", "5-12")
src    "etapE-NN.jpg"
etap   "11. Etap"   blok "E2 · D · E1 · F1 Blok"   oda "2+1"   tip "Tip Y2"
brut   "115,72"  net "74,04"      (görseldeki tablonun SAĞ sütunu: Satışa Esas Brüt / Net Alan)
rooms  [[id, ad, m2, tür, geometri, (ops.) etiket_noktası], ...]
doors  [[o, c, a, b, menteşe, yön, (ops.) 1=daire giriş kapısı], ...]
opens  [[o, c, a, b], ...]     kapısız geçiş (duvar yok)
wins   [[o, c, a, b], ...]     pencere / balkon kapısı (balkona bakan pencere otomatik yer seviyesine iner)
solid  [[x1, y1, x2, y2], ...] dolu şaft/kolon (tavana kadar dolu blok)
furn   [[tür, [x1, y1, x2, y2], (ops.) yön], ...]
extra  {"plants": [[x, y, ölçek~1.1], ...], "desks_chairs": [[x, y, açı°], ...], "chairrot": 0, "az0": -62}
```

### rooms
- m2: tablodaki **sağ sütun** değeri (net alan). Tablodaki her satır bir oda olur, tablo sırasıyla.
- id: `sal` salon, `mut` mutfak (birden fazlaysa `mut2`), `eb` ebeveyn yatak, `o1` `o2` `o3` odalar,
  `ba` banyo, `eba` ebeveyn banyo, `wc` misafir wc, `gh` giriş holü, `kor` koridor (`kor2`), `cn` çamaşır nişi/odası,
  `blk` balkon (`blk2`), `tr` teras, `gd` giyinme. **mut*, gh*, kor* id'leri döşeme seçimini etkiler.**
- tür: `wood` (parke: salon, odalar), `tile` (mutfak, hol, koridor, banyo, wc, çamaşır), `balk` (balkon/teras).
  Banyo/wc/çamaşır `tile` ise duvarlarına seramik kaplanır.
- geometri: dikdörtgen `[x1, y1, x2, y2]` ya da dik açılı poligon `[[x,y],...]` (yalnızca yatay/dikey kenarlar).
- Kenarlar **duvarın ortasından** geçer (duvar kalınlığının merkez çizgisi). Komşu odalar aynı çizgiyi paylaşır;
  ortak duvar için iki odada aynı koordinatı kullan. Duvar 17 cm kalınlığında otomatik üretilir.
  Amerikan mutfak tabloda ayrı satırsa, salondan bir sınırla ayır ve aradaki açıklığı `opens` ile aç.
- Oda kenarlarında kapı/pencere/geçiş olmayan her yer duvar olur. Balkon (`balk`) kenarları duvar yerine cam korkuluk olur.

### doors / opens / wins
- o: `h` yatay duvar üstünde (c = duvarın y'si, a..b = x aralığı), `v` dikey duvar üstünde (c = x, a..b = y aralığı).
- c, ilgili oda kenarının koordinatına eşit (±0.2 m tolerans) olmalı.
- menteşe: `a` (a ucunda) ya da `b`. yön: `h` kapıda +1 kanat aşağı (+y) açılır, -1 yukarı; `v` kapıda +1 sağa (+x), -1 sola.
  Görseldeki kapı yayına bak: menteşe yayın merkezi, kanadın açık hali yayın düz kenarı.

### furn (mobilya, piksel dikdörtgeni görseldeki eşyanın kapladığı alan)
`bed2` çift kişilik yatak, `bed1` tek kişilik — yön = başucunun dayandığı taraf `t`/`b`/`l`/`r`
`sofa` kanepe — yön = sırtın olduğu taraf. `ctab` orta sehpa, `rug` halı, `tv` TV ünitesi (duvara yaslı ince dikdörtgen)
`table` yemek masası (sandalyeler otomatik), `desk` çalışma masası, `chair` berjer/koltuk (balkonda da)
`counter` mutfak tezgâhı (her düz parça ayrı), `fridge` buzdolabı, `ward` gardırop/vestiyer/dolap, `wm` çamaşır makinesi
`wc` klozet, `sink` lavabo, `shower` duş teknesi (cam otomatik), `bath` küvet
Dolap, tezgâh, lavabo, klozet ve TV'nin hangi duvara yaslandığı otomatik bulunur.

## Kontrol
`python3 tools/kat3d/check.py <id> --render` alanları karşılaştırır (±12% üstü "KONTROL ET") ve
`tools/kat3d/check_<id>.png` üretir: solda orijinal üstüne çizimin, sağda hızlı tepeden render. Görsele bak,
duvarlar/kapılar/eşyalar orijinalle örtüşene ve tüm odalar ±12% içine girene kadar düzelt.
