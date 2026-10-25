#!/usr/bin/env python3
"""Arama sayfaları üretici: fikirtepe-satilik-daire, fikirtepe-kiralik-daire ve her etap için
yeni-fikirtepe-N-etap.html. Görünüm etaplar.html'den alınır; rakamlar etaplar.html tablosu ve
teslim-takvimi.json'dan gelir. Çalıştır: python3 tools/seo_sayfalar.py (repo kökünden)."""
import json, re, html, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://yenifikirtepeburada.com/'
src = (ROOT / 'etaplar.html').read_text(encoding='utf8')

HEAD = src[:src.index('<div class="wrap">')]
TAIL = src[src.index('  <!-- WhatsApp sabit buton -->'):]
HEAD = HEAD.replace(' class="active"', '')

# etap tablosu
ETAP = []
for n, konut, tic, tip in re.findall(r'<tr><td class="ep">(?:<a [^>]*>)?(\d+)\. Etap(?:</a>)?</td><td>([^<]*)</td><td>([^<]*)</td><td>([^<]*)</td></tr>', src):
    ETAP.append(dict(n=int(n), konut=konut, tic=tic, tip=tip.replace('–', '–')))
TOPLAM = 10857
KAT = {2, 3, 4, 5, 11, 12, 19}  # kat-planlari.html'de planı olan etaplar
teslim = {e['id']: e for e in json.loads((ROOT / 'teslim-takvimi.json').read_text(encoding='utf8'))['etaplar']}
AY = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']

def tr_tarih(s):
    y, m, d = map(int, s.split('-'))
    return f'{d} {AY[m-1]} {y}'

def sayi(s):
    return int(s.replace('.', '')) if s.replace('.', '').isdigit() else None

def slug(n):
    return f'yeni-fikirtepe-{n}-etap.html'

EXTRA_CSS = '''<style>
  .stripstat .num,.stripstat .lbl{padding:0!important;border:0!important;min-width:0!important}
  .stripstat .lbl{margin-top:8px}
  .crumb{font-size:.85rem;color:var(--gray);margin-top:26px}
  .crumb a{text-decoration:none;color:var(--gray)} .crumb a:hover{color:var(--blue)}
  .txt p{font-size:1.03rem;color:#2c3543;margin-bottom:14px}
  .txt h2{font-size:1.4rem;color:var(--blue);font-weight:700;margin:8px 0 14px}
  .txt ul{margin:0 0 16px 20px;color:#2c3543} .txt li{margin-bottom:6px}
  .txt a{color:var(--blue);font-weight:600}
  .egrid{display:grid;grid-template-columns:repeat(6,1fr);gap:10px}
  .egrid a{display:block;text-align:center;text-decoration:none;border:1px solid var(--line);border-radius:12px;padding:12px 6px;font-weight:600;color:var(--blue);background:rgba(255,255,255,.8);transition:.18s}
  .egrid a:hover,.egrid a.cur{background:var(--blue);color:#fff;border-color:var(--blue)}
  .faq details{border:1px solid var(--line);border-radius:12px;padding:14px 18px;margin-bottom:10px;background:rgba(255,255,255,.85)}
  .faq summary{cursor:pointer;font-weight:600;color:var(--blue)}
  .faq details p{margin-top:10px;color:#2c3543}
  .tablewrap a{color:var(--blue);font-weight:600;text-decoration:none}
  @media(max-width:720px){.egrid{grid-template-columns:repeat(3,1fr)}}
</style>
'''

def head(title, desc, url):
    h = HEAD
    h = re.sub(r'<title>[^<]*</title>', f'<title>{html.escape(title)}</title>', h)
    h = re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")[^"]*"', lambda m: m.group(1) + html.escape(desc, quote=True) + '"', h)
    h = re.sub(r'(<meta (?:property|name)="(?:og:title|twitter:title)" content=")[^"]*"', lambda m: m.group(1) + html.escape(title, quote=True) + '"', h)
    h = h.replace('https://yenifikirtepeburada.com/etaplar.html', url)
    return h.replace('</head>', EXTRA_CSS + '</head>')

def schema(objs):
    return ''.join('<script type="application/ld+json">\n' + json.dumps(o, ensure_ascii=False, indent=1) + '\n</script>\n' for o in objs)

def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

def faq_schema(qa):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in qa]}

def faq_html(qa):
    return '<section class="faq"><div class="shead">Sık Sorulanlar</div>' + ''.join(
        f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in qa) + '</section>'

def egrid(cur=None):
    return '<section><div class="shead">Tüm Etaplar</div><div class="egrid">' + ''.join(
        f'<a href="{slug(e["n"])}"{" class=\"cur\"" if e["n"] == cur else ""}>{e["n"]}. Etap</a>' for e in ETAP) + '</div></section>'

def cta(h2, p, links):
    return '<div class="cta"><h2>' + h2 + '</h2><p>' + p + '</p><div class="btns">' + ''.join(
        f'<a href="{u}" class="{c}">{t}</a>' for t, u, c in links) + '</div></div>'

def page(fname, title, desc, h1, lead, body, objs, crumb_items):
    url = SITE + fname
    crumb = ' › '.join(f'<a href="{u.replace(SITE, "") or "index.html"}">{n}</a>' for n, u in crumb_items[:-1]) + ' › ' + crumb_items[-1][0]
    out = head(title, desc, url).replace('</head>', schema(objs + [crumbs(crumb_items)]) + '</head>')
    out += f'''  <div class="wrap">
    <div class="crumb">{crumb}</div>
    <div class="phead">
      <h1>{h1}<span class="sq"></span></h1>
      <p class="lead">{lead}</p>
    </div>
{body}
  </div>
''' + TAIL
    (ROOT / fname).write_text(out, encoding='utf8')
    return fname

OFIS = ('RE/MAX Doğuş, Yeni Fikirtepe\'nin içinde, Nuhoğlu Yenitepe Sitesi 2. Etap A Blok\'taki ofisinden hizmet verir. '
        'Google\'da 150\'yi aşkın müşteri yorumu ve 4,9 puanla bölgeyi her gün sahada takip eden bir ekibiz.')

def etap_tablo(link_suffix=''):
    rows = ''.join(f'<tr><td class="ep"><a href="{slug(e["n"])}">{e["n"]}. Etap</a></td><td>{e["konut"]}</td><td>{e["tip"]}</td></tr>' for e in ETAP)
    return f'<div class="tablewrap"><table><thead><tr><th>Etap</th><th>Konut</th><th>Daire Tipleri</th></tr></thead><tbody>{rows}</tbody></table></div>'

made = []
hom = ('Anasayfa', SITE)

# ---------- Satılık ----------
qa_s = [
    ('Fikirtepe\'de satılık daire fiyatları ne kadar?', 'Fiyat; etaba, kata, cepheye, metrekareye ve dairenin teslim durumuna göre büyük fark gösterir. Aynı etapta bile iki daire arasında ciddi fark olabilir. Bütçenizi ve aradığınız daire tipini bırakın, o günkü gerçek satış verileriyle uygun seçenekleri size iletelim.'),
    ('Yeni Fikirtepe\'de hangi daire tipleri var?', 'Etaplara göre 1+1\'den 5+1\'e kadar daire tipleri bulunur. Hangi etapta hangi tiplerin olduğunu yukarıdaki tabloda görebilirsiniz.'),
    ('Emlak Konut dairesi satın alırken devir nasıl yapılır?', 'Tapusu verilmemiş dairelerde satış, Emlak Konut sözleşmesinin devriyle yapılır. Adımları ve gerekli belgeleri <a href="devir-rehberi.html">Devir Rehberi</a> sayfamızda anlattık.'),
    ('Satın alırken hangi masraflar çıkar?', 'Tapu harcı, döner sermaye, emlak hizmet bedeli ve varsa devir masrafları. Kalem kalem hesap için <a href="daire-satis-masraflari.html">Satış Masrafları</a> sayfasına bakın.'),
    ('Teslim tarihlerini nereden öğrenirim?', 'Emlak Konut\'un açıkladığı blok ve daire teslim programlarını <a href="teslim-takvimi.html">Teslim Takvimi</a> sayfamızda kapı numaranızla sorgulayabilirsiniz.'),
]
body = f'''    <section class="txt">
      <p>Fikirtepe\'de satılık daire arayanların büyük kısmı bugün Yeni Fikirtepe\'ye, yani Emlak Konut\'un 19 etaplık kentsel dönüşüm projesine bakıyor. Projede 10.857 konut var ve daireler 1+1\'den 5+1\'e uzanıyor. Etaplar teslim sürecinde olduğu için aynı sokakta hem tapulu hem devirli, hem boş hem kiracılı daire bulabilirsiniz.</p>
      <p>Doğru daireyi bulmak için önce etabı seçmek gerekir: etapların büyüklüğü, daire tipleri, teslim tarihi ve ticari yoğunluğu birbirinden farklı. Aşağıdaki tablodan etaba tıklayarak ayrıntılarına geçebilirsiniz.</p>
    </section>
    <section><div class="shead">Etaplara Göre Satılık Daire Seçenekleri</div>{etap_tablo()}</section>
    <section class="txt">
      <h2>Satın almadan önce bakmanız gerekenler</h2>
      <ul>
        <li><b>Tapu mu, devir mi?</b> Tapusu verilmemiş dairelerde işlem Emlak Konut sözleşme devriyle yapılır (<a href="devir-rehberi.html">Devir Rehberi</a>).</li>
        <li><b>Teslim durumu:</b> Dairenin anahtarı teslim edildi mi, hangi tarihte edilecek (<a href="teslim-takvimi.html">Teslim Takvimi</a>)?</li>
        <li><b>Kat planı ve cephe:</b> Aynı tipteki iki daire, cephe ve kata göre çok farklı değerde olabilir (<a href="kat-planlari.html">Kat Planları</a>, <a href="vaziyet-plani.html">Vaziyet Planı</a>).</li>
        <li><b>Masraflar:</b> Tapu harcı, hizmet bedeli ve devir giderleri (<a href="daire-satis-masraflari.html">Satış Masrafları</a>).</li>
      </ul>
      <h2>Neden RE/MAX Doğuş?</h2>
      <p>{OFIS} Portallarda gördüğünüz ilanların çoğu aynı daireyi farklı fiyatlarla gösterir; biz size yalnız gerçekten satılık olan, belgesi kontrol edilmiş daireleri sunarız.</p>
    </section>
    {cta('Aradığınız daireyi birlikte bulalım', 'Bütçenizi, etabınızı ve daire tipinizi bırakın; uygun daireler çıktıkça size ilk biz haber verelim.', [('Satılık daire arıyorum', 'almak-istiyorum.html', 'pri'), ('Dairemi satmak istiyorum', 'satilik-deger.html', 'sec')])}
    {faq_html(qa_s)}
    <section class="txt"><p>Kiralık mı bakıyorsunuz? <a href="fikirtepe-kiralik-daire.html">Fikirtepe kiralık daire</a> sayfamıza geçin.</p></section>'''
made.append(page('fikirtepe-satilik-daire.html',
    'Fikirtepe Satılık Daire | Yeni Fikirtepe Etap Etap Satılık Daireler – RE/MAX Doğuş',
    'Fikirtepe ve Yeni Fikirtepe\'de satılık daire: 19 etabın daire tipleri, teslim durumu, devir ve masraf bilgisi. Bütçenizi bırakın, uygun daireleri size iletelim.',
    'Fikirtepe Satılık Daire', 'Yeni Fikirtepe\'nin 19 etabında 1+1\'den 5+1\'e satılık daireler: etap etap bilgiler, devir ve masraf rehberi, güvenilir danışmanlık.',
    body, [faq_schema(qa_s)], [hom, ('Fikirtepe Satılık Daire', SITE + 'fikirtepe-satilik-daire.html')]))

# ---------- Kiralık ----------
qa_k = [
    ('Fikirtepe\'de kiralık daire kiraları ne kadar?', 'Kira; etaba, daire tipine, eşyalı olup olmamasına ve kata göre değişir. Bütçenizi ve daire tipinizi bırakın, güncel seçenekleri size iletelim.'),
    ('Yeni Fikirtepe\'de eşyalı kiralık daire bulunur mu?', 'Evet, özellikle 1+1 ve 2+1 dairelerde eşyalı seçenekler çıkıyor. Formda eşyalı istediğinizi belirtmeniz yeterli.'),
    ('Kiralama süreci nasıl ilerliyor?', 'Daire gösterimi, sözleşme, depozito ve anahtar teslimine kadar her adımı <a href="kiralama-asamalari.html">Kiralama Aşamaları</a> sayfamızda anlattık.'),
    ('Dairemi kiraya vermek istiyorum, ne yapmalıyım?', '<a href="kiralik-deger.html">Kiralık değer</a> formunu doldurun; dairenizin güncel kira değerini hesaplayıp uygun kiracıyı bulalım.'),
]
body = f'''    <section class="txt">
      <p>Fikirtepe\'de kiralık daire arayanlar için en geniş seçenek Yeni Fikirtepe\'de: 19 etapta 10.857 konut teslim edildikçe kiralık daire sayısı da artıyor. Yeni bina, site içi güvenlik, sosyal alanlar ve Kadıköy\'e yakınlık bölgeyi hem öğrenciler hem aileler için cazip kılıyor.</p>
      <p>Etapların büyüklüğü ve daire tipleri farklı. Hangi etapta ne tür daire olduğunu aşağıdan görebilir, etaba tıklayarak ayrıntılara geçebilirsiniz.</p>
    </section>
    <section><div class="shead">Etaplara Göre Kiralık Daire Seçenekleri</div>{etap_tablo()}</section>
    <section class="txt">
      <h2>Kiralamadan önce bakmanız gerekenler</h2>
      <ul>
        <li><b>Aidat ve giderler:</b> Site aidatı etaba göre değişir, kiraya ek olarak hesaplayın.</li>
        <li><b>Eşya durumu:</b> Eşyalı, yarı eşyalı ya da boş.</li>
        <li><b>Sözleşme ve depozito:</b> Süreç adım adım <a href="kiralama-asamalari.html">Kiralama Aşamaları</a> sayfamızda.</li>
        <li><b>Konum:</b> Etabın ana caddeye, metrobüse ve okullara uzaklığı (<a href="vaziyet-plani.html">Vaziyet Planı</a>).</li>
      </ul>
      <h2>Neden RE/MAX Doğuş?</h2>
      <p>{OFIS} Ev sahibiyle kiracı arasındaki sözleşmeyi, demirbaş listesini ve teslim tutanağını biz hazırlarız.</p>
    </section>
    {cta('Size uygun kiralık daireyi bulalım', 'Bütçenizi ve daire tipinizi bırakın; uygun daire çıktığında hemen arayalım.', [('Kiralık daire arıyorum', 'kiralamak-istiyorum.html', 'pri'), ('Dairemi kiraya vermek istiyorum', 'kiralik-deger.html', 'sec')])}
    {faq_html(qa_k)}
    <section class="txt"><p>Satın almak mı istiyorsunuz? <a href="fikirtepe-satilik-daire.html">Fikirtepe satılık daire</a> sayfamıza geçin.</p></section>'''
made.append(page('fikirtepe-kiralik-daire.html',
    'Fikirtepe Kiralık Daire | Yeni Fikirtepe Kiralık Daireler – RE/MAX Doğuş',
    'Fikirtepe ve Yeni Fikirtepe\'de kiralık daire: etap etap daire tipleri, eşyalı seçenekler, kiralama süreci. Bütçenizi bırakın, uygun daireyi size bulalım.',
    'Fikirtepe Kiralık Daire', 'Yeni Fikirtepe\'de 1+1\'den 5+1\'e kiralık daireler: etap bilgileri, kiralama süreci ve güvenilir danışmanlık.',
    body, [faq_schema(qa_k)], [hom, ('Fikirtepe Kiralık Daire', SITE + 'fikirtepe-kiralik-daire.html')]))

# ---------- Etaplar ----------
for e in ETAP:
    n = e['n']; k = sayi(e['konut']); ofis = k is None
    tes = teslim.get(str(n)) or (teslim.get('3-2') if n == 3 else None)
    if ofis:
        lead = f'Yeni Fikirtepe {n}. Etap, projenin ofis etabıdır: {e["tic"]} bulunur.'
        strip = f'<div class="stripstat"><div><div class="num">{e["tic"].split()[0]}</div><div class="lbl">Ofis</div></div><div><div class="num">{n}.</div><div class="lbl">Etap</div></div></div>'
        para = f'<p>{n}. Etap konut değil, ofis etabı olarak planlandı. Yeni Fikirtepe\'de iş yeri, ofis ya da yatırım amaçlı ticari alan arayanlar için bölgenin en büyük ofis stoğunu oluşturuyor.</p>'
    else:
        pay = k / TOPLAM * 100
        sira = sorted([x for x in ETAP if sayi(x['konut'])], key=lambda x: -sayi(x['konut'])).index(e) + 1
        lead = f'Yeni Fikirtepe {n}. Etap\'ta {e["konut"]} konut ve {e["tic"]} ticari ünite var; daire tipleri {e["tip"]}.'
        strip = (f'<div class="stripstat"><div><div class="num">{e["konut"]}</div><div class="lbl">Konut</div></div>'
                 f'<div><div class="num">{e["tic"]}</div><div class="lbl">Ticari ünite</div></div>'
                 f'<div><div class="num">{e["tip"]}</div><div class="lbl">Daire tipleri</div></div>'
                 f'<div><div class="num">%{pay:.1f}</div><div class="lbl">Projedeki payı</div></div></div>').replace(f'%{pay:.1f}', '%' + f'{pay:.1f}'.replace('.', ','))
        boy = 'büyük' if sira <= 6 else ('orta büyüklükteki' if sira <= 12 else 'küçük')
        pay_s = f'{pay:.1f}'.replace('.', ',')
        para = (f'<p>{n}. Etap, Yeni Fikirtepe\'nin etapları arasında konut sayısına göre {sira}. sırada; projedeki 10.857 konut içindeki payı yaklaşık %{pay_s}.'
                f' {e["tip"]} arası daire tipleriyle {boy} etaplardan biri. Etapta satılık ve kiralık daireler teslim süreciyle birlikte el değiştiriyor.</p>')
    tes_html = ''
    if tes:
        bloklar = ', '.join(b['b'] for b in tes['bloklar'])
        bas, bit = tr_tarih(tes['bloklar'][0]['bas']), tr_tarih(max(b['bit'] for b in tes['bloklar']))
        tes_html = (f'<h2>{tes["ad"]} teslim takvimi</h2><p>Emlak Konut\'un programına göre {tes["ad"]}\'ta {tes["daire"]} dairenin anahtar teslimi '
                    f'{bas} ile {bit} arasında, {bloklar} bloklarında yapılıyor. Kapı numaranızla randevu gün ve saatinizi <a href="teslim-takvimi.html">Teslim Takvimi</a> sayfasında öğrenebilirsiniz.</p>')
    kat_html = (f'<p>{n}. Etap\'ın daire planlarını <a href="kat-planlari.html#etap-{n}">Kat Planları</a> sayfamızda 3D olarak inceleyebilirsiniz.</p>' if n in KAT
                else f'<p>{n}. Etap\'ın kat planları Emlak Konut tarafından yayımlandığında <a href="kat-planlari.html">Kat Planları</a> sayfamıza eklenecek.</p>')
    qa = []
    if not ofis:
        qa.append((f'Yeni Fikirtepe {n}. Etap\'ta kaç konut var?', f'{n}. Etap\'ta {e["konut"]} konut ve {e["tic"]} ticari ünite bulunuyor.'))
        qa.append((f'{n}. Etap\'ta hangi daire tipleri var?', f'{n}. Etap\'ta daire tipleri {e["tip"]} arasındadır.'))
    else:
        qa.append((f'Yeni Fikirtepe {n}. Etap konut mu, ofis mi?', f'{n}. Etap ofis etabıdır ve {e["tic"]} bulunur.'))
    if tes:
        qa.append((f'{n}. Etap teslimleri ne zaman?', f'Program {bas} ile {bit} arasını kapsıyor. Kendi randevunuzu Teslim Takvimi sayfamızda kapı numaranızla sorgulayabilirsiniz.'))
    else:
        qa.append((f'{n}. Etap teslim tarihi belli mi?', 'Emlak Konut teslim programını açıkladığında Teslim Takvimi sayfamızda blok ve kapı numarasına göre yayımlıyoruz.'))
    qa.append((f'{n}. Etap\'ta satılık veya kiralık daire nasıl bulurum?', f'Aradığınız daire tipini ve bütçenizi formumuza bırakın; {n}. Etap\'ta uygun daire çıktığında RE/MAX Doğuş danışmanı sizi arasın.'))
    qa.append((f'{n}. Etap\'taki dairemin değeri ne kadar?', 'Satılık veya kiralık değer formunu doldurun; güncel satış ve kira verileriyle dairenize özel değerleme yapalım.'))
    body = f'''    <section>{strip}</section>
    <section class="txt">
      {para}
      {tes_html}
      {kat_html}
      <p>Ortak alanlar: 7/24 güvenlik, açık ve kapalı sosyal alanlar, çocuk oyun ve spor alanları, otopark ve tüm etapları birbirine bağlayan 1,6 km\'lik yeşil koridor. Etabın projedeki yerini <a href="vaziyet-plani.html">Vaziyet Planı</a>\'nda görebilirsiniz.</p>
    </section>
    {cta(f'{n}. Etap\'ta daire mi arıyorsunuz?', f'{n}. Etap\'ta satılık ya da kiralık daire arıyorsanız ya da dairenizi satmak, kiraya vermek istiyorsanız bize yazın.', [('Satılık arıyorum', 'almak-istiyorum.html', 'pri'), ('Kiralık arıyorum', 'kiralamak-istiyorum.html', 'sec'), ('Dairemin değeri', 'satilik-deger.html', 'sec')])}
    {faq_html(qa)}
    {egrid(n)}
    <section class="txt"><p>Genel bilgi: <a href="fikirtepe-satilik-daire.html">Fikirtepe satılık daire</a> · <a href="fikirtepe-kiralik-daire.html">Fikirtepe kiralık daire</a> · <a href="etaplar.html">Tüm etaplar</a></p></section>'''
    ttl = (f'Yeni Fikirtepe {n}. Etap | Ofis Etabı – RE/MAX Doğuş' if ofis else
           f'Yeni Fikirtepe {n}. Etap | Satılık & Kiralık Daire, {e["konut"]} Konut, {e["tip"]}')
    dsc = (f'Yeni Fikirtepe {n}. Etap: ' + (f'{e["tic"]}, ofis ve ticari alanlar.' if ofis else
           f'{e["konut"]} konut, {e["tic"]} ticari ünite, {e["tip"]} daire tipleri') +
           (' Teslim takvimi,' if tes else '') + ' kat planları, satılık ve kiralık daireler.')
    made.append(page(slug(n), ttl, dsc, f'Yeni Fikirtepe {n}. Etap', lead, body, [faq_schema(qa)],
                     [hom, ('Etaplar', SITE + 'etaplar.html'), (f'{n}. Etap', SITE + slug(n))]))

# Umut 25 Eki: sitenin kendi sayfalarından bu sayfalara bağlantı verilmez (yalnız Google'dan gelinir).
assert len(ETAP) == 18, len(ETAP)

# sitemap
sm = (ROOT / 'sitemap.xml').read_text(encoding='utf8')
today = datetime.date.today().isoformat()
add = ''.join(f'  <url><loc>{SITE}{f}</loc><lastmod>{today}</lastmod></url>\n' for f in made if f'{SITE}{f}<' not in sm)
sm = sm.replace('</urlset>', add + '</urlset>')
(ROOT / 'sitemap.xml').write_text(sm, encoding='utf8')
print('\n'.join(made))
