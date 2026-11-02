"""Fit pixel->lat/lon for a 12th Army Group sheet from control points (px,py,lon,lat).
Model: lat/lon projected to a local conformal conic plane, then an affine (or quadratic) fit."""
import json,math,sys
import numpy as np
def proj(lon,lat,lat0=49.0,lon0=0.0):
    # simple Lambert conformal conic, one standard parallel lat0
    p0=math.radians(lat0); n=math.sin(p0); R=6371.0
    F=math.cos(p0)*math.tan(math.pi/4+p0/2)**n/n
    rho=lambda p:R*F/math.tan(math.pi/4+p/2)**n
    r=rho(math.radians(lat)); th=n*math.radians(lon-lon0)
    return r*math.sin(th), rho(p0)-r*math.cos(th)
def unproj(x,y,lat0=49.0,lon0=0.0):
    p0=math.radians(lat0); n=math.sin(p0); R=6371.0
    F=math.cos(p0)*math.tan(math.pi/4+p0/2)**n/n; r0=R*F/math.tan(math.pi/4+p0/2)**n
    r=math.copysign(math.hypot(x,r0-y),n); th=math.atan2(x,r0-y)
    lat=2*math.atan((R*F/r)**(1/n))-math.pi/2
    return lon0+math.degrees(th/n), math.degrees(lat)
def design(px,py,order):
    px=np.asarray(px,float)/1000; py=np.asarray(py,float)/1000
    cols=[np.ones_like(px),px,py]
    if order==2: cols+=[px*px,px*py,py*py]
    return np.stack(cols,1)
class Fit:
    def __init__(s,pts,order=1):
        s.order=order; P=np.array(pts,float)
        xy=np.array([proj(lo,la) for lo,la in P[:,2:4]])
        A=design(P[:,0],P[:,1],order)
        s.cx,_,_,_=np.linalg.lstsq(A,xy[:,0],rcond=None); s.cy,_,_,_=np.linalg.lstsq(A,xy[:,1],rcond=None)
        pred=A@np.stack([s.cx,s.cy],1); s.res=np.hypot(*(pred-xy).T)
    def __call__(s,px,py):
        A=design([px],[py],s.order)[0]; return unproj(float(A@s.cx),float(A@s.cy))
    def inv(s,lon,lat):
        assert s.order==1
        x,y=proj(lon,lat); M=np.array([s.cx[1:],s.cy[1:]]); v=np.linalg.solve(M,[x-s.cx[0],y-s.cy[0]])*1000; return round(v[0]),round(v[1])
if __name__=='__main__':
    d=json.load(open(sys.argv[1])); f=Fit(d['control'],d.get('order',1))
    print('residuals km:',np.round(f.res,2),'rms',round(float(np.sqrt((f.res**2).mean())),2))
    for name,px,py in d.get('test',[]):
        lo,la=f(px,py); print(name,round(la,4),round(lo,4))
    for name,lo,la in d.get('towns',[]): print(name,f.inv(lo,la))

# ---- registration of a sheet to a reference scan of the same base sheet ----
def _gray(path):
    from PIL import Image
    return np.asarray(Image.open(path).convert('L'),float)
def _pc(a,b):
    A=np.fft.fft2(a-a.mean()); B=np.fft.fft2(b-b.mean()); R=A*np.conj(B); R/=np.abs(R)+1e-9
    r=np.fft.ifft2(R).real; i=np.unravel_index(np.argmax(r),r.shape); sh=[i[k] if i[k]<r.shape[k]/2 else i[k]-r.shape[k] for k in (0,1)]
    return sh, r.max()
def register(ref_path,sheet_path,patches=((1200,900),(5400,900),(1200,5000),(5400,5000),(3300,3000)),half=400):
    """Return list of (sheet_px,sheet_py,ref_px,ref_py) correspondences from phase correlation."""
    R=_gray(ref_path); S=_gray(sheet_path)
    # coarse global shift at 1/8
    sh,_=_pc(R[::8,::8],S[::8,::8]); dy,dx=sh[0]*8,sh[1]*8
    out=[]
    for cx,cy in patches:
        a=R[cy-half:cy+half,cx-half:cx+half]; b=S[cy-half-dy:cy+half-dy,cx-half-dx:cx+half-dx]
        if a.shape!=b.shape or a.size==0: continue
        (ey,ex),q=_pc(a,b); out.append((cx-dx-ex,cy-dy-ey,cx,cy,round(q,3)))
    return out
def affine2(pairs):
    P=np.array(pairs,float); A=np.c_[P[:,0],P[:,1],np.ones(len(P))]
    cx=np.linalg.lstsq(A,P[:,2],rcond=None)[0]; cy=np.linalg.lstsq(A,P[:,3],rcond=None)[0]
    res=np.hypot(A@cx-P[:,2],A@cy-P[:,3]); return cx,cy,res
