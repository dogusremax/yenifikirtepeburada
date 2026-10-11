import sys, os, numpy as np
from PIL import Image
sys.path.insert(0,os.path.dirname(__file__))
from cube import face, F
Image.MAX_IMAGE_PIXELS=None
src,out=sys.argv[1],sys.argv[2]
N,T=4096,512
eq=np.asarray(Image.open(src).convert('RGB'))
for f in F:
    im=face(eq,f,N)
    lv=4
    while lv>=1:
        s=T*2**(lv-1); x=im if s==N else im.resize((s,s),Image.LANCZOS)
        d=f'{out}/{lv}'; os.makedirs(d,exist_ok=True)
        for r in range(s//T):
            for c in range(s//T):
                x.crop((c*T,r*T,c*T+T,r*T+T)).save(f'{d}/{f}{r}_{c}.jpg',quality=80,optimize=True,progressive=True)
        lv-=1
    os.makedirs(f'{out}/fallback',exist_ok=True)
    im.resize((1024,1024),Image.LANCZOS).save(f'{out}/fallback/{f}.jpg',quality=80,optimize=True)
print('done',out)
