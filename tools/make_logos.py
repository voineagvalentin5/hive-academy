"""Build web-ready Hive Academy logo assets from the official files.
- icon: already transparent; trim to content, export sizes, favicon, apple-touch, og.
- lockup: official file is RGB on white with a charcoal wordmark that disappears on
  dark backgrounds. We (1) key out the white, (2) recolor the charcoal wordmark to a
  light silver, keep gold as gold, (3) swap in the clean transparent icon.
"""
from PIL import Image, ImageFilter, ImageDraw
import numpy as np, os
SRC='/workspace/hive-academy/official'
OUT='/workspace/hive-academy-site/assets/brand'
os.makedirs(OUT,exist_ok=True)
BG=(17,18,22)

icon=Image.open(f'{SRC}/hive-academy-icon.png').convert('RGBA')
a=np.array(icon)
# clear near-invisible alpha dust so trim is tight
a[...,3]=np.where(a[...,3]<6,0,a[...,3]); icon=Image.fromarray(a)
icon=icon.crop(icon.getbbox())
w,h=icon.size; s=max(w,h); pad=int(s*0.04)
sq=Image.new('RGBA',(s+2*pad,s+2*pad),(0,0,0,0)); sq.paste(icon,((s-w)//2+pad,(s-h)//2+pad),icon)
icon_sq=sq
for px in (64,128,256,512):
    im=icon_sq.resize((px,px),Image.LANCZOS)
    im.save(f'{OUT}/academy-icon-{px}.png',optimize=True)
    im.save(f'{OUT}/academy-icon-{px}.webp',quality=90,method=6)
# favicon (ico multi-size) + svg-free png favicon
icon_sq.resize((256,256),Image.LANCZOS).save(f'{OUT}/../../favicon.ico',sizes=[(16,16),(32,32),(48,48),(64,64)])
icon_sq.resize((32,32),Image.LANCZOS).save(f'{OUT}/favicon-32.png',optimize=True)
# apple touch: opaque dark bg (iOS fills transparency with black anyway; control it)
at=Image.new('RGBA',(180,180),BG+(255,)); ic=icon_sq.resize((150,150),Image.LANCZOS); at.alpha_composite(ic,(15,15))
at.convert('RGB').save(f'{OUT}/apple-touch-icon.png',optimize=True)

# ---- lockup ----
L=np.array(Image.open(f'{SRC}/hive-academy-lockup.png').convert('RGB')).astype(float)
word=L[690:910, 80:1370]   # wordmark + tagline + rules
mn=word.min(-1); mx=word.max(-1)
alpha=np.clip((250-mn)/110,0,1)          # white -> 0, ink -> 1
sat=mx-mn
# un-premultiply against white
col=(word-(1-alpha[...,None])*255)/np.maximum(alpha[...,None],1e-3)
col=np.clip(col,0,255)
lum=col.mean(-1)
isgold=(sat>45)|((col[...,0]-col[...,2])>35)
# charcoal -> light silver, keep subtle gradient
silver=np.stack([236-lum*0.25,234-lum*0.25,230-lum*0.25],-1)
# soft blend between gold and silver to avoid fringes
g=np.clip(((col[...,0]-col[...,2])-20)/30,0,1)
# letters' bottom bevels are grey; keep them with the gold letters (no silver underline)
gm=Image.fromarray((g>0.5).astype(np.uint8)*255).filter(ImageFilter.MaxFilter(9))
g=np.maximum(g,np.array(gm)/255.0)
# darken grey bevels inside gold letters toward bronze
region=np.zeros_like(sat,dtype=bool); region[:135,:445]=True   # 'HIVE' letters only
g=np.where(region,g,np.clip(((col[...,0]-col[...,2])-20)/30,0,1))
bev=(np.array(gm)>0)&(sat<45)&region
col[bev]=col[bev]*np.array([0.85,0.68,0.45])
g=g[...,None]
out=col*g+silver*(1-g)
rgba=np.dstack([out,alpha*255]).astype(np.uint8)
wm=Image.fromarray(rgba,'RGBA'); wm=wm.crop(wm.getbbox())
# compose: icon on top, wordmark below
ih=560
ic=icon.resize((int(icon.width*ih/icon.height),ih),Image.LANCZOS)
gap=70
W=max(wm.width,ic.width)+40; H=ic.height+gap+wm.height+40
lock=Image.new('RGBA',(W,H),(0,0,0,0))
lock.alpha_composite(ic,((W-ic.width)//2,20)); lock.alpha_composite(wm,((W-wm.width)//2,20+ic.height+gap))
lock.save(f'{OUT}/academy-lockup-dark-full.png',optimize=True)
for wpx in (480,960):
    r=lock.resize((wpx,int(H*wpx/W)),Image.LANCZOS)
    r.save(f'{OUT}/academy-lockup-dark-{wpx}.png',optimize=True); r.save(f'{OUT}/academy-lockup-dark-{wpx}.webp',quality=90,method=6)
# wordmark only (horizontal use)
for wpx in (360,720):
    r=wm.resize((wpx,int(wm.height*wpx/wm.width)),Image.LANCZOS)
    r.save(f'{OUT}/academy-wordmark-dark-{wpx}.png',optimize=True); r.save(f'{OUT}/academy-wordmark-dark-{wpx}.webp',quality=90,method=6)
# previews on dark
for name in ('academy-lockup-dark-960.png','academy-icon-128.png','academy-wordmark-dark-720.png'):
    im=Image.open(f'{OUT}/{name}'); bg=Image.new('RGBA',im.size,BG+(255,)); bg.alpha_composite(im)
    bg.convert('RGB').save(f'/workspace/hive-academy-site/work/preview-{name}')
print('ok', lock.size, wm.size)
