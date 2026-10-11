import sys, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
src,yaw,pitch,fov,out,W,H=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]),sys.argv[5],int(sys.argv[6]),int(sys.argv[7])
eq=np.asarray(Image.open(src).reduce(4).convert('RGB'));Hh,Ww=eq.shape[:2]
f=W/2/np.tan(np.radians(fov)/2)
x,y=np.meshgrid(np.arange(W)-W/2+.5,H/2-np.arange(H)-.5)
z=np.full_like(x,f)
p=np.radians(pitch);yw=np.radians(yaw)
y2=y*np.cos(p)+z*np.sin(p); z2=-y*np.sin(p)+z*np.cos(p)
x3=x*np.cos(yw)+z2*np.sin(yw); z3=-x*np.sin(yw)+z2*np.cos(yw)
lon=np.arctan2(x3,z3); lat=np.arctan2(y2,np.hypot(x3,z3))
u=((lon/(2*np.pi)+.5)*Ww).astype(int)%Ww; v=np.clip(((.5-lat/np.pi)*Hh).astype(int),0,Hh-1)
Image.fromarray(eq[v,u]).save(out,quality=84)
