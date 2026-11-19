from PIL import Image, ImageDraw, ImageFilter
import math
B='/workspace/hive-academy-site/assets/brand'
W,H=1200,630
img=Image.new('RGBA',(W,H),(17,18,22,255))
# warm radial glow
glow=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(glow)
d.ellipse((60,60,560,570),fill=(201,154,75,70)); glow=glow.filter(ImageFilter.GaussianBlur(110)); img.alpha_composite(glow)
# honeycomb lines
hc=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(hc); r=34
for row in range(-1,14):
    for col in range(-1,24):
        cx=col*r*1.732+(row%2)*r*0.866; cy=row*r*1.5
        pts=[(cx+r*math.cos(math.radians(60*k-30)),cy+r*math.sin(math.radians(60*k-30))) for k in range(6)]
        fade=max(0,min(1,(cx-650)/500))
        d.polygon(pts,outline=(201,154,75,int(10+40*fade)))
img.alpha_composite(hc)
ic=Image.open(f'{B}/academy-icon-512.png').resize((400,400),Image.LANCZOS)
img.alpha_composite(ic,(90,115))
wm=Image.open(f'{B}/academy-wordmark-dark-720.png')
s=560/wm.width; wm=wm.resize((560,int(wm.height*s)),Image.LANCZOS)
img.alpha_composite(wm,(560,int(H/2-wm.height/2)-20))
from PIL import ImageFont
f=ImageFont.truetype('/usr/share/fonts/truetype/sand-box/google/Montserrat/Montserrat-VariableFont_wght.ttf',26)
try: f.set_variation_by_axes([600])
except Exception: pass
ImageDraw.Draw(img).text((560+280,int(H/2+wm.height/2)+30),'COMING SOON  ·  PILOT IN DEVELOPMENT',font=f,fill=(201,154,75,255),anchor='mm')
img.convert('RGB').save('/workspace/hive-academy-site/assets/brand/og-image.jpg',quality=88,optimize=True,progressive=True)
print('ok')
