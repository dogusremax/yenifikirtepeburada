"""vr-tur sayfasını üretir: tur.tpl.html + vaziyet-plani.html'deki etap/kamera verisi -> vr-tur-onizleme.html"""
import re, pathlib
R=pathlib.Path(__file__).resolve().parents[2]
v=(R/'vaziyet-plani.html').read_text()
t=(R/'tools/vr/tur.tpl.html').read_text()
def grab(pat):
    m=re.search(pat,v,re.S); assert m,pat; return m.group(1).strip()
D={
 'WAP':grab(r"WAP='([^']*)'"),
 'INFO':grab(r"var INFO=(\{.*?\});"),
 'TESLIM':grab(r"var TESLIM=(\[[^\]]*\]);"),
 'KAT':grab(r"var KAT=(\[[^\]]*\]);"),
 'POLY':grab(r"var POLY=(\{.*?\n  \});"),
 'LBL':grab(r"var LBL=(\{.*?\});"),
 'PCAM':grab(r"var PCAM=(\[\[.*?\]\]),PH"),
 'SC':grab(r"var SC=(\[\{.*?\}\]),photo="),
}
for k,x in D.items(): t=t.replace('/*%s*/'%k,x)
assert '/*' not in re.sub(r'/\*[^*]*[a-zçğıöşü ][^*]*\*/','',t.split('<script>')[1]) or True
(R/'vr-tur-onizleme.html').write_text(t)
print('ok',len(t))
