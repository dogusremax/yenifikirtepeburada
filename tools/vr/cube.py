import sys, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
# face -> function(a,b) giving direction (x,y,z); a,b in [-1,1], a = right, b = down
F={
 'f':lambda a,b:( a,-b, 1),
 'r':lambda a,b:( 1,-b,-a),
 'b':lambda a,b:(-a,-b,-1),
 'l':lambda a,b:(-1,-b, a),
 'u':lambda a,b:( a, 1, b),
 'd':lambda a,b:( a,-1,-b),
}
def face(eq,f,N,CH=512):
    return Image.fromarray(np.vstack([_face(eq,f,N,r,min(N,r+CH)) for r in range(0,N,CH)]))
def _face(eq,f,N,r0,r1):
    H,W=eq.shape[:2]
    t=(np.arange(N)+.5)/N*2-1
    a,b=np.meshgrid(t,t[r0:r1])
    x,y,z=F[f](a,b); x=np.broadcast_to(x,a.shape);y=np.broadcast_to(y,a.shape);z=np.broadcast_to(z,a.shape)
    lon=np.arctan2(x,z); lat=np.arctan2(y,np.hypot(x,z))
    u=(lon/(2*np.pi)+.5)*W-.5; v=(.5-lat/np.pi)*H-.5
    # bilinear
    u0=np.floor(u).astype(int); v0=np.floor(v).astype(int); du=(u-u0)[...,None]; dv=(v-v0)[...,None]
    u1=(u0+1)%W; u0%=W; v0=np.clip(v0,0,H-1); v1=np.clip(v0+1,0,H-1)
    eq=eq;g=lambda vv,uu:eq[vv,uu].astype(np.float32)
    out=(g(v0,u0)*(1-du)*(1-dv)+g(v0,u1)*du*(1-dv)+g(v1,u0)*(1-du)*dv+g(v1,u1)*du*dv)
    return np.clip(out+.5,0,255).astype(np.uint8)
if __name__=='__main__':
    src,N,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
    im=Image.open(src).convert('RGB')
    if len(sys.argv)>4: im=im.resize((int(sys.argv[4]),int(sys.argv[4])//2),Image.LANCZOS)
    eq=np.asarray(im)
    for f in F: face(eq,f,N).save(f'{out}_{f}.jpg',quality=85)
