# Fikirtepe Rehberi sayfalarını üretir: fikirtepe-rehberi.html (liste) + rehber-*.html (yazılar).
# Şablon devir-rehberi.html (üst menü, arka plan, WhatsApp düğmesi, alt betikler aynı kalır).
# Çalıştırma: python3 tools/rehber_uret.py   (depo kökünde)
import json, re, html

TARIH = '2026-10-28'
SITE = 'https://yenifikirtepeburada.com/'
src = open('devir-rehberi.html', encoding='utf-8').read()
HEAD_END = src.index('<style>')
STYLE_END = src.index('</style>') + len('</style>')
WRAP = src.index('  <div class="wrap">')
TAIL = src.index('<style>\n  .wa-fab')

CSS = '''
  /* Fikirtepe Rehberi */
  .crumb{display:inline-flex;align-items:center;gap:8px;text-decoration:none;color:var(--gray);font-size:.92rem;font-weight:500;margin-top:30px}
  .crumb:hover{color:var(--blue)}
  .eyebrow{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin-bottom:14px;font-size:.78rem;font-weight:600;letter-spacing:.08em;color:var(--gray);text-transform:uppercase}
  .eyebrow .tag{color:#fff;background:var(--red);padding:3px 10px;border-radius:999px;letter-spacing:.06em}
  .art h2{font-size:1.35rem;color:var(--blue);font-weight:700;margin:38px 0 14px;letter-spacing:-.01em;display:flex;align-items:center;gap:12px}
  .art h2::after{content:'';flex:1;height:1px;background:var(--line)}
  .art p.txt{color:#3a4453;font-weight:300;font-size:1.02rem;margin:0 0 14px}
  .kisaca{background:var(--blue);color:#fff;border-radius:18px;padding:22px 24px;margin:26px 0 8px}
  .kisaca b.h{display:block;font-size:.78rem;letter-spacing:.12em;color:#bcc8de;margin-bottom:8px}
  .kisaca ol{margin:0;padding-left:20px}
  .kisaca li{padding:4px 0;font-weight:400}
  .kisaca li::marker{color:var(--red);font-weight:700}
  .cant{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}
  .cant li{border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.85);padding:12px 14px 12px 40px;position:relative;color:#3a4453;font-weight:300;font-size:.95rem}
  .cant li::before{content:'';position:absolute;left:14px;top:15px;width:16px;height:16px;border-radius:5px;border:2px solid var(--blue)}
  .cant li b{color:var(--ink);font-weight:600}
  .zaman{position:relative;margin:0;padding:0 0 0 26px;list-style:none}
  .zaman::before{content:'';position:absolute;left:8px;top:6px;bottom:6px;width:2px;background:linear-gradient(var(--red),var(--blue))}
  .zaman>li{position:relative;margin-bottom:14px;border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.88);padding:16px 18px}
  .zaman>li::before{content:'';position:absolute;left:-24px;top:20px;width:14px;height:14px;border-radius:50%;background:#fff;border:3px solid var(--red)}
  .zaman .gun{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:.08em;color:var(--red);margin-bottom:4px;text-transform:uppercase}
  .zaman b.t{display:block;color:var(--blue);font-size:1.06rem;font-weight:700;margin-bottom:4px}
  .zaman p{color:var(--gray);font-weight:300;font-size:.97rem;margin:0}
  .zaman p+p{margin-top:6px}
  .hat{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
  .hat>div{border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.88);padding:16px 18px;border-top:4px solid var(--c,var(--blue))}
  .hat b.t{display:block;color:var(--blue);font-size:1.04rem;font-weight:700;margin-bottom:2px}
  .hat .rozet{display:inline-block;font-size:.7rem;font-weight:700;letter-spacing:.05em;color:#fff;background:var(--c,var(--blue));padding:2px 8px;border-radius:6px;margin:2px 4px 6px 0}
  .hat p{color:var(--gray);font-weight:300;font-size:.95rem;margin:0}
  .rota{border:1px solid var(--line);border-radius:14px;overflow:hidden;background:rgba(255,255,255,.88)}
  .rota>div{display:grid;grid-template-columns:minmax(120px,190px) 1fr;gap:14px;padding:13px 18px;border-bottom:1px solid var(--line);align-items:baseline}
  .rota>div:last-child{border-bottom:0}
  .rota b{color:var(--blue);font-weight:700;font-size:.97rem}
  .rota span{color:#3a4453;font-weight:300;font-size:.96rem}
  .rota i{font-style:normal;font-weight:600;color:var(--ink)}
  @media(max-width:560px){.rota>div{grid-template-columns:1fr;gap:2px}}
  .ilgili{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:10px 0 0}
  .ilgili a{display:block;text-decoration:none;border:1px solid var(--line);border-radius:12px;padding:14px 16px;background:rgba(255,255,255,.88);transition:.2s}
  .ilgili a:hover{border-color:rgba(10,42,94,.3);box-shadow:0 10px 24px rgba(10,42,94,.08);transform:translateY(-2px)}
  .ilgili small{display:block;font-size:.7rem;font-weight:700;letter-spacing:.08em;color:var(--red);text-transform:uppercase}
  .ilgili b{display:block;color:var(--blue);font-weight:700;line-height:1.35;margin-top:2px}
  /* liste sayfası */
  .kartlar{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin:30px 0 10px}
  .kart{display:flex;flex-direction:column;text-decoration:none;color:inherit;border:1px solid var(--line);border-radius:18px;background:rgba(255,255,255,.9);overflow:hidden;transition:.25s}
  .kart:hover{border-color:rgba(10,42,94,.28);box-shadow:0 16px 36px rgba(10,42,94,.1);transform:translateY(-3px)}
  .kart .ust{position:relative;height:118px;background:var(--blue);color:#fff;display:flex;align-items:flex-end;padding:16px 18px;overflow:hidden}
  .kart .ust .ik{position:absolute;right:-8px;top:-10px;font-size:5.4rem;font-weight:700;line-height:1;color:rgba(255,255,255,.1);letter-spacing:-.04em}
  .kart .ust small{position:relative;font-size:.74rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#bcc8de}
  .kart .ust small em{font-style:normal;color:#fff;background:var(--red);padding:2px 8px;border-radius:999px;margin-right:8px;letter-spacing:.06em}
  .kart .alt{padding:16px 18px 18px;display:flex;flex-direction:column;gap:8px;flex:1}
  .kart .alt b{color:var(--blue);font-size:1.12rem;font-weight:700;line-height:1.3}
  .kart .alt p{color:var(--gray);font-weight:300;font-size:.95rem;margin:0}
  .kart .alt span{margin-top:auto;color:var(--red);font-weight:600;font-size:.9rem}
  .kart.kucuk .ust{height:70px}
  .kart.kucuk .ust .ik{font-size:3.6rem}
</style>'''

def esc(s): return html.escape(s, quote=True)

def sayfa(dosya, baslik, aciklama, govde, ld):
    h = src[:HEAD_END]
    eski_t = re.search(r'<title>.*?</title>', h).group(0)
    h = h.replace(eski_t, '<title>' + esc(baslik) + '</title>')
    h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(aciklama), h)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + esc(aciklama), h)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + esc(baslik), h)
    h = h.replace(SITE + 'devir-rehberi.html', SITE + dosya)
    h = h.replace('<meta property="og:type" content="website">', '<meta property="og:type" content="' + ('article' if dosya.startswith('rehber-') else 'website') + '">')
    h += '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>\n'
    stil = src[HEAD_END:STYLE_END].replace('</style>', CSS)
    orta = src[STYLE_END:WRAP]
    orta = orta.replace('<a href="devir-rehberi.html" class="active">Devir Rehberi</a>', '<a href="devir-rehberi.html">Devir Rehberi</a>')
    orta = orta.replace('<a href="fikirtepe-rehberi.html">Fikirtepe Rehberi</a>', '<a href="fikirtepe-rehberi.html" class="active">Fikirtepe Rehberi</a>')
    out = h + stil + orta + '  <div class="wrap">\n' + govde + '\n  </div>\n\n' + src[TAIL:]
    open(dosya, 'w', encoding='utf-8').write(out)

def ld_yazi(dosya, baslik, aciklama):
    return {"@context": "https://schema.org", "@type": "Article", "headline": baslik, "description": aciklama,
            "datePublished": TARIH, "dateModified": TARIH, "inLanguage": "tr",
            "mainEntityOfPage": SITE + dosya, "image": SITE + "og-image.png",
            "author": {"@type": "Organization", "name": "RE/MAX Doğuş Yeni Fikirtepe"},
            "publisher": {"@type": "Organization", "name": "RE/MAX Doğuş", "logo": {"@type": "ImageObject", "url": SITE + "favicon.png"}}}

WA = 'https://wa.me/902163151515'
YAZILAR = []

def yazi(dosya, kisa, etiket, sure, baslik, aciklama, lead, kisaca, govde, cta_h, cta_p, cta_link):
    YAZILAR.append((dosya, kisa, etiket, aciklama))
    g = '''    <a href="fikirtepe-rehberi.html" class="crumb">← Fikirtepe Rehberi</a>
    <article class="art">
    <div class="phead">
      <div class="eyebrow"><span class="tag">%s</span><span>%s okuma</span><span>28 Ekim 2026</span></div>
      <h1>%s<span class="sq"></span></h1>
      <p class="lead">%s</p>
    </div>
    <div class="kisaca"><b class="h">KISACA</b><ol>%s</ol></div>
%s
    </article>
    <h2 style="font-size:1.15rem;color:var(--blue);margin:40px 0 4px">Rehberden başka yazılar</h2>
    <div class="ilgili">@@ILGILI:%s@@</div>
    <div class="cta">
      <h2>%s</h2>
      <p>%s</p>
      %s
      <a href="%s?text=%s" target="_blank" rel="noopener">WhatsApp’tan yazın</a>
    </div>''' % (etiket, sure, baslik, lead, ''.join('<li>' + k + '</li>' for k in kisaca), govde, dosya, cta_h, cta_p, cta_link,
                WA, html.escape(__import__('urllib.parse').parse.quote('Merhaba, Fikirtepe Rehberi’ndeki “' + kisa + '” yazısını okudum, bilgi almak istiyorum.')))
    son = baslik.rsplit(' ', 1)
    g = g.replace('<h1>%s<span class="sq"></span></h1>' % baslik, '<h1>%s <span style="white-space:nowrap">%s<span class="sq"></span></span></h1>' % (son[0], son[1]), 1)
    return (dosya, baslik, aciklama, g)

# ---------- 1. Anahtar günü ----------
Y1 = yazi('rehber-anahtar-teslim-gunu.html', 'Anahtar günü hazırlığı', 'Teslim', '5 dk',
  'Anahtar Günü: Tutanağı İmzalamadan Önce Dairenizi Böyle Gezin',
  'Yeni Fikirtepe’de anahtar teslim randevusuna giderken yanınıza alacaklarınız, dairede oda oda yapacağınız 9 kontrol ve eksik bulursanız izleyeceğiniz yol.',
  'Teslim randevusu çoğu zaman kısa sürer; imzaladığınız tutanak ise dairenin o günkü hâlinin kaydı olur. Randevudan önce yapacağınız küçük bir hazırlık, sonradan yazışmalarla uğraşmanın önüne geçer.',
  ['Randevu saatinizi ve yanınızda olması istenen belgeleri teslim bildiriminizden teyit edin.',
   'Daireyi her odada aynı sırayla gezin: kapı-pencere, su, elektrik, zemin, duvar.',
   'Gördüğünüz her eksiği yeriyle birlikte fotoğraflayıp yazılı listeye geçirin; sayaç endekslerini kaydedin.'],
  '''    <h2>Çantanıza koyun</h2>
    <ul class="cant">
      <li><b>Kimlik kartınız.</b> Yerinize başkası gidecekse noterden düzenlenmiş vekâletname.</li>
      <li><b>Teslim bildirimi</b> ve elinizdeki sözleşmenin bir kopyası.</li>
      <li><b>Şarjı dolu telefon</b> ve taşınabilir şarj cihazı: fotoğraf, video ve fener için.</li>
      <li><b>Telefon şarj aleti</b> ya da küçük bir lamba: prizleri tek tek denemek için.</li>
      <li><b>Şerit metre, kâğıt bant ve kalem:</b> eksik noktaları yerinde işaretlemek için.</li>
      <li><b>Su terazisi uygulaması</b> (telefonda): tezgâh ve balkon eğimine bakmak için.</li>
    </ul>

    <h2>Dairede: oda oda 9 kontrol</h2>
    <div class="grp">
      <div class="step"><div class="snum">1</div><div class="sbody"><b>Giriş kapısı ve anahtar sayısı</b>
        <p>Kapı sürtmeden kapanıyor mu, kilit her anahtarla rahat dönüyor mu? Size kaç anahtar verildiğini sayın ve sayının tutanağa yazıldığından emin olun.</p></div></div>
      <div class="step"><div class="snum">2</div><div class="sbody"><b>Pencereler ve balkon kapıları</b>
        <p>Her kanadı hem açılır hem vasistas konumunda deneyin. Kollar, contalar ve camlardaki çizik ya da çatlaklara bakın.</p></div></div>
      <div class="step"><div class="snum">3</div><div class="sbody"><b>Banyo ve mutfakta su</b>
        <p>Bütün muslukları birkaç dakika açık bırakın: su basıncı, sıcak su, giderlerin hızla boşalması. Ardından lavabo ve tezgâh altına fenerle bakın; kuru bir kâğıt havlu küçük sızıntıları hemen gösterir.</p></div></div>
      <div class="step"><div class="snum">4</div><div class="sbody"><b>Prizler, anahtarlar ve sigorta panosu</b>
        <p>Her prizi şarj aletiyle deneyin, her lambanın anahtarını açıp kapatın. Panodaki sigorta etiketlerinin odalarla eşleşip eşleşmediğine bakın.</p></div></div>
      <div class="step"><div class="snum">5</div><div class="sbody"><b>Isıtma</b>
        <p>Dairenizde kombi mi yoksa ortak bir sistem mi olduğunu öğrenin. Peteklerin vanalarına ve bağlantı noktalarına bakın; sistemin ne zaman ve nasıl devreye alınacağını sorun.</p></div></div>
      <div class="step"><div class="snum">6</div><div class="sbody"><b>Zemin</b>
        <p>Parkede kabarma, aralık ya da basınca ses verme; seramikte kırık ve derz boşluğu. Seramiğe parmak eklemiyle hafifçe vurduğunuzda boş ses gelen yeri not edin.</p></div></div>
      <div class="step"><div class="snum">7</div><div class="sbody"><b>Duvar ve tavan</b>
        <p>Çatlak, boya akıntısı, leke ve nem izi. Dış cepheye bakan duvarları, pencere köşelerini ve banyo tavanını özellikle kontrol edin.</p></div></div>
      <div class="step"><div class="snum">8</div><div class="sbody"><b>Balkon ve teras</b>
        <p>Zemine bir bardak su dökün: su gidere doğru akmalı, ortada göllenmemeli. Korkuluğun sağlam olduğunu elinizle deneyin.</p></div></div>
      <div class="step"><div class="snum">9</div><div class="sbody"><b>Sayaçlar, depo ve otopark</b>
        <p>Elektrik ve su sayaçlarının numarasını ve o günkü endeksini fotoğraflayın; abonelik başvurusunda bu bilgiler işinize yarar. Size ayrılan depo ve otopark numarasının belgenizdekiyle aynı olduğuna bakın.</p></div></div>
    </div>

    <h2>Eksik bulursanız</h2>
    <p class="txt">Eksikleri genel ifadelerle değil, yeriyle birlikte yazın: <i>“Salon, balkon kapısı sağ kanat: conta yerinden çıkmış.”</i> Her maddenin yanına fotoğraf numarasını ekleyin.</p>
    <div class="notebox"><b>Listeyi kayda geçirin.</b> Eksik listesinin tutanağa eklenmesini ya da teslim görevlisiyle birlikte imzalanmasını isteyin ve bir kopyasını saklayın. Taşındıktan sonra fark ettiğiniz bir sorun için yazılı başvuru yapın; başvuru tarihini ve varsa numarasını not alın.</div>
    <div class="warn">Teslim usulü etaba göre değişebilir. Size gönderilen teslim bildirimindeki talimatlar her zaman önceliklidir.</div>''',
  'Teslim gününüz ne zaman?', 'Etabınızın blok blok teslim programını ve kalan günleri teslim takviminde görebilirsiniz.',
  '<a href="teslim-takvimi.html">Teslim takvimi</a>')

# ---------- 2. İlk 30 gün ----------
Y2 = yazi('rehber-yeni-dairede-ilk-30-gun.html', 'Yeni dairede ilk 30 gün', 'Taşınma', '6 dk',
  'Yeni Dairede İlk 30 Gün: Deprem Sigortası, Abonelikler ve Adres Kaydı',
  'Anahtarı aldıktan sonraki ilk ay: DASK poliçesi, elektrik, su ve doğalgaz abonelikleri, site yönetimi kaydı, internet ve e-Devlet adres bildirimi hangi sırayla yapılır?',
  'Anahtarı aldıktan sonra yapılacak resmî işlerin mantıklı bir sırası var. Sırayı baştan doğru kurarsanız aynı başvuruyu iki kez yapmazsınız.',
  ['<b>Önce DASK:</b> elektrik, su ve doğalgaz aboneliğinde zorunlu deprem sigortası poliçesi istenir.',
   '<b>Sonra abonelikler</b> ve site yönetimi kaydı; internet kurulumunu taşınmadan önce ayarlayın.',
   '<b>Taşındıktan sonra adres kaydı:</b> e-Devlet’ten, taşınmayı izleyen 20 iş günü içinde.'],
  '''    <h2>Gün gün yol haritası</h2>
    <ol class="zaman">
      <li><span class="gun">1–3. gün</span><b class="t">Zorunlu Deprem Sigortası (DASK)</b>
        <p>DASK poliçesini sigorta şirketlerinden, acentelerden ya da bankalardan yaptırabilirsiniz. Poliçe için dairenizin <b>adres kodu</b> (UAVT) gerekir; bu kodu e-Devlet’teki adres sorgulama ekranından öğrenebilirsiniz.</p>
        <p>Poliçe önemli çünkü elektrik, su ve doğalgaz aboneliği açılırken geçerli bir DASK poliçesi aranır. İlk iş bunu bitirin.</p></li>
      <li><span class="gun">3–7. gün</span><b class="t">Elektrik</b>
        <p>Kadıköy’de elektrik perakende satışı Enerjisa İstanbul Anadolu Yakası tarafından yapılır. Aboneliği şirketin çevrim içi kanallarından, e-Devlet’ten ya da müşteri hizmetleri merkezinden açabilirsiniz. Kimlik, tapu ya da kira sözleşmesi, DASK poliçesi ve teslim günü kaydettiğiniz sayaç bilgileri hazır olsun.</p></li>
      <li><span class="gun">3–7. gün</span><b class="t">Su</b>
        <p>Su aboneliği İSKİ’den açılır. Başvuruyu İSKİ’nin çevrim içi işlemleri ya da şube üzerinden yapabilirsiniz; belgeler elektrikteki ile büyük ölçüde aynıdır.</p></li>
      <li><span class="gun">5–10. gün</span><b class="t">Doğalgaz</b>
        <p>Dairenizde bireysel kombi varsa İGDAŞ’tan abonelik açtırıp gaz açma randevusu alırsınız. Isınma ortak bir sistemle sağlanıyorsa bireysel abonelik gerekmeyebilir; bunu site yönetiminden öğrenin.</p></li>
      <li><span class="gun">7–15. gün</span><b class="t">Site yönetimi kaydı</b>
        <p>Malik bilgilerinizi bırakın, aidatın nasıl ödeneceğini, otopark ve giriş kartlarını, taşınma saatlerini ve yük asansörü kullanımını sorun. Nakliye günü asansörün korumaya alınması istenebilir; tarihi önceden bildirin.</p></li>
      <li><span class="gun">Taşınmadan önce</span><b class="t">İnternet</b>
        <p>Adres kodunuzla operatörlerin altyapı sorgulama ekranlarından hangi bağlantının geldiğine bakın. Kurulum randevusunu taşınma gününden önceye almak ilk günleri kolaylaştırır.</p></li>
      <li><span class="gun">Taşındıktan sonra · 20 iş günü içinde</span><b class="t">Adres kaydı</b>
        <p>Yerleşim yeri değişikliğini e-Devlet’teki “Adres Değişikliği Bildirimi” hizmetinden yapabilirsiniz. Elektrik, su ya da doğalgaz aboneliğinizin ya da tapunuzun sizin adınıza kayıtlı olması çevrim içi bildirimi kolaylaştırır.</p></li>
    </ol>

    <h2>İki küçük not</h2>
    <div class="notebox"><b>Kiraya verecekseniz:</b> aboneliklerin kiracının kendi adına açılması, sonradan devir işleriyle uğraşmanızı önler. Kiralama sürecini <a href="kiralama-asamalari.html">kiralama aşamaları</a> sayfamızda anlattık.</div>
    <div class="notebox"><b>DASK her şeyi karşılamaz:</b> yalnızca depremin ve depremin doğrudan yol açtığı hasarları belirli limitlere kadar karşılar. Su baskını, hırsızlık ya da cam kırılması gibi riskler için ayrıca konut sigortası düşünebilirsiniz.</div>
    <div class="warn">Kurumların başvuru kanalları ve istedikleri belgeler zaman zaman değişir. Başvurudan önce ilgili kurumun güncel duyurusuna bakmanızı öneririz.</div>''',
  'Taşınma işlerinde yanınızdayız', 'Abonelik, kiracı teslimi ya da site yönetimiyle ilgili sorularınızı danışmanlarımıza sorun.',
  '<a href="satis-sonrasi.html">Satış sonrası hizmetler</a>')

# ---------- 3. Ulaşım ----------
Y3 = yazi('rehber-fikirtepe-ulasim.html', 'Arabasız Fikirtepe', 'Ulaşım', '5 dk',
  'Arabasız Fikirtepe: Metro, Marmaray, Metrobüs ve Vapurla Şehrin Her Yerine',
  'Yeni Fikirtepe’den raylı sistem ve deniz yoluyla nereye nasıl gidilir? Söğütlüçeşme, Ayrılık Çeşmesi, M4 metro, Kadıköy iskelesi ve havalimanı güzergâhları.',
  'Yeni Fikirtepe, Anadolu Yakası’nın en güçlü aktarma noktalarından birinin hemen yanında. Hangi hattın sizi nereye götürdüğünü, aktarmalarıyla birlikte bir araya getirdik.',
  ['<b>Söğütlüçeşme:</b> Marmaray ve Metrobüs aynı noktada.',
   '<b>M4 metrosu:</b> Kadıköy’den Sabiha Gökçen Havalimanı’na kadar tek hat.',
   '<b>Kadıköy iskelesi:</b> vapurla Karaköy, Eminönü ve Beşiktaş.'],
  '''    <h2>Yakındaki hatlar</h2>
    <div class="hat">
      <div style="--c:#0a2a5e"><b class="t">Söğütlüçeşme</b><span class="rozet">MARMARAY</span><span class="rozet" style="background:#e2231a">METROBÜS</span><span class="rozet" style="background:#5b6473">YHT</span>
        <p>Marmaray ile Boğaz’ın altından Avrupa Yakası’na geçilir; Metrobüs hattı da Anadolu Yakası’nda burada başlar. Bazı yüksek hızlı tren seferleri de bu istasyonda durur.</p></div>
      <div style="--c:#e2231a"><b class="t">Ayrılık Çeşmesi</b><span class="rozet" style="background:#e2231a">M4</span><span class="rozet">MARMARAY</span>
        <p>M4 metrosu ile Marmaray’ın kesiştiği aktarma istasyonu. Avrupa Yakası’ndan gelip havalimanına ya da Kadıköy’e geçmek için en kolay nokta.</p></div>
      <div style="--c:#e2231a"><b class="t">M4 · Acıbadem ve Ünalan</b><span class="rozet" style="background:#e2231a">M4</span>
        <p>M4 hattı Kadıköy’den Sabiha Gökçen Havalimanı’na uzanır. Ünalan istasyonunda Uzunçayır Metrobüs durağına aktarma yapılabilir.</p></div>
      <div style="--c:#143d82"><b class="t">Kadıköy İskelesi</b><span class="rozet" style="background:#143d82">VAPUR</span>
        <p>Karaköy, Eminönü ve Beşiktaş vapurları. Trafiğe takılmadan karşıya geçmenin en keyifli yolu.</p></div>
    </div>

    <h2>Nereye, nasıl?</h2>
    <div class="rota">
      <div><b>Sirkeci, Yenikapı</b><span><i>Marmaray</i> ile aktarmasız.</span></div>
      <div><b>Levent, Maslak</b><span><i>Marmaray</i> → Yenikapı’da <i>M2</i> metro. Alternatif: <i>Metrobüs</i> → Zincirlikuyu.</span></div>
      <div><b>Kadıköy merkez</b><span><i>M4</i> ile birkaç durak ya da kısa bir otobüs yolculuğu.</span></div>
      <div><b>Sabiha Gökçen Havalimanı</b><span><i>M4</i> ile aktarmasız.</span></div>
      <div><b>İstanbul Havalimanı</b><span><i>Marmaray</i> → Yenikapı’da <i>M2</i> → Gayrettepe’de <i>M11</i>.</span></div>
      <div><b>Ankara, Eskişehir</b><span>Söğütlüçeşme’den kalkan <i>yüksek hızlı tren</i> seferleri.</span></div>
    </div>

    <h2>Araçla</h2>
    <p class="txt">D-100 (E-5) karayolu bölgenin hemen yanından geçer; 15 Temmuz Şehitler ve Fatih Sultan Mehmet köprülerine D-100 bağlantılarıyla çıkılır. Avrasya Tüneli’nin Anadolu Yakası girişi de Göztepe’dedir.</p>
    <p class="txt">Etapların birbirine ve ana yollara göre konumunu <a href="vaziyet-plani.html">360° vaziyet planında</a> kendiniz gezerek görebilirsiniz.</p>
    <div class="warn">Yolculuk süreleri saate ve trafiğe göre değişir. Sefer saatleri ve hat çalışmaları için Metro İstanbul, İETT ve TCDD Taşımacılık’ın güncel duyurularına bakın.</div>''',
  'Ulaşımı size uygun daireyi birlikte bulalım', 'Okula, işe ya da havalimanına yakınlığınıza göre etap ve blok önerisi için danışmanlarımıza yazın.',
  '<a href="almak-istiyorum.html">Daire arıyorum</a>')

ESKI = [('devir-rehberi.html', 'Devir', 'Emlak Konut Daire Devir Rehberi', 'Devir randevusundan önce hazırlamanız gereken belgeler, adım adım.'),
        ('daire-satis-masraflari.html', 'Satış', 'Daire Satarken Masraflar ve Vergiler', 'Satış bedelinden elinize net ne geçecek? Harç, vergi ve diğer kalemler.'),
        ('kiralama-asamalari.html', 'Kiralama', 'Dairenizi Kiraya Verme Süreci', 'Fotoğraftan sözleşmeye, kiracıya anahtar teslimine kadar aşamalar.'),
        ('sorulariniz.html', 'Sorular', 'Sık Sorulan Sorular', 'Kentsel dönüşüm ve Yeni Fikirtepe hakkında en çok sorulanlar.')]

def ilgili(haric):
    h = ''
    for d, kisa, et, ac in YAZILAR:
        if d != haric: h += '<a href="%s"><small>%s</small><b>%s</b></a>' % (d, et, esc(kisa))
    h += '<a href="devir-rehberi.html"><small>Devir</small><b>Emlak Konut daire devri</b></a>'
    return h

for dosya, baslik, aciklama, g in (Y1, Y2, Y3):
    g = re.sub(r'@@ILGILI:([^@]+)@@', lambda m: ilgili(m.group(1)), g)
    sayfa(dosya, baslik + ' | RE/MAX Doğuş', aciklama, g, ld_yazi(dosya, baslik, aciklama))

# ---------- liste sayfası ----------
IK = {'Teslim': '⌂', 'Taşınma': '30', 'Ulaşım': 'M4'}
k = ''
basliklar = {Y1[0]: Y1[1], Y2[0]: Y2[1], Y3[0]: Y3[1]}
for d, kisa, et, ac in YAZILAR:
    k += '''      <a class="kart" href="%s"><div class="ust"><span class="ik">%s</span><small><em>YENİ</em>%s</small></div>
        <div class="alt"><b>%s</b><p>%s</p><span>Oku →</span></div></a>\n''' % (d, IK[et], et, esc(basliklar[d]), esc(ac))
e = ''
for d, et, b, ac in ESKI:
    e += '''      <a class="kart kucuk" href="%s"><div class="ust"><span class="ik">%s</span><small>%s</small></div>
        <div class="alt"><b>%s</b><p>%s</p><span>Oku →</span></div></a>\n''' % (d, et[0], et, b, ac)
liste = '''    <a href="index.html" class="back">← Ana sayfa</a>
    <div class="phead">
      <h1>Fikirtepe Rehberi<span class="sq"></span></h1>
      <p class="lead">Fikirtepe’de oturanların ve buraya taşınmayı düşünenlerin günlük sorularına kısa ve uygulanabilir cevaplar. Anahtar gününden ilk aya, ulaşımdan devire kadar.</p>
    </div>
    <div class="kartlar">
%s    </div>
    <div class="gtitle" style="margin-top:34px">Diğer rehberlerimiz</div>
    <div class="kartlar" style="margin-top:0">
%s    </div>
    <div class="cta">
      <h2>Aradığınız konu burada yok mu?</h2>
      <p>Sorunuzu yazın; cevabını hem size iletelim hem de rehbere ekleyelim.</p>
      <a href="iletisim.html">Bize ulaşın</a>
      <a href="%s" target="_blank" rel="noopener">WhatsApp’tan yazın</a>
    </div>''' % (k, e, WA)
ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Fikirtepe Rehberi", "url": SITE + "fikirtepe-rehberi.html", "inLanguage": "tr",
      "hasPart": [{"@type": "Article", "headline": basliklar[d], "url": SITE + d} for d, *_ in YAZILAR]}
sayfa('fikirtepe-rehberi.html', 'Fikirtepe Rehberi: Teslim, Taşınma ve Ulaşım | RE/MAX Doğuş',
      'Yeni Fikirtepe’de anahtar teslim günü, yeni dairede ilk 30 gün, ulaşım ve daire devri üzerine RE/MAX Doğuş rehber yazıları.', liste, ld)
print('tamam:', [y[0] for y in YAZILAR])
