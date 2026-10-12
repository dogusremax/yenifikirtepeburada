"""Önizlemeyi canlıya taşır (yalnızca Umut "canlıya al" dedikten sonra çalıştır):
vaziyet-plani-vr-onizleme.html -> vaziyet-plani.html (canlı sayfanın başlık/SEO/gtag kısmı korunur)
assets/vr/duzen-onizleme.json -> assets/vr/duzen.json"""
import pathlib, shutil
R = pathlib.Path(__file__).resolve().parents[2]
live = (R/'vaziyet-plani.html').read_text(); pre = (R/'vaziyet-plani-vr-onizleme.html').read_text()
seo = live[live.index('<title>'):live.index('<link rel="preconnect"')]
ga = live[live.index('<!-- Google tag (gtag.js) -->'):live.index('</script>', live.index("gtag('config'")) + len('</script>')]
a = pre.index('<meta name="robots"'); b = pre.index('<link rel="preconnect"')
new = pre[:a] + seo + pre[b:]
css = '<link rel="stylesheet" href="assets/vendor/pannellum/pannellum.css">'
assert new.count(css) == 1; new = new.replace(css, css + '\n' + ga)
for x, y in [('<a class="back" href="vaziyet-plani.html" aria-label="Vaziyet planına dön">', '<a class="back" href="index.html" aria-label="Ana sayfaya dön">'),
             ("fetch('assets/vr/duzen-onizleme.json?cb=", "fetch('assets/vr/duzen.json?cb=")]:
    assert new.count(x) == 1, x; new = new.replace(x, y)
assert 'noindex' not in new and new.count('G-ZNHG94R2JK') >= 1
(R/'vaziyet-plani.html').write_text(new)
shutil.copy(R/'assets/vr/duzen-onizleme.json', R/'assets/vr/duzen.json')
print('ok', len(new))
