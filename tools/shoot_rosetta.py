import asyncio, sys
from playwright.async_api import async_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8794'
TAG=sys.argv[2] if len(sys.argv)>2 else 'local'
P='/modules/rosetta-logos/'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        for name,vp,mobile in [('desktop-1280',{'width':1280,'height':800},False),('desktop-1440',{'width':1440,'height':900},False),('mobile-390',{'width':390,'height':844},True)]:
            ctx=await b.new_context(viewport=vp,device_scale_factor=2 if mobile else 1,is_mobile=mobile,has_touch=mobile)
            pg=await ctx.new_page(); errs=[]
            pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
            pg.on('pageerror',lambda e: errs.append('PAGEERR '+str(e)))
            pg.on('requestfailed',lambda r: errs.append('FAIL '+r.url))
            r=await pg.goto(BASE+P,wait_until='networkidle'); await pg.wait_for_timeout(1200)
            robots=await pg.get_attribute('meta[name=robots]','content')
            pre=f'screenshots/rosetta-{TAG}-{name}'
            await pg.screenshot(path=pre+'-top.png')
            # canvas pixels change while rotating?
            sig='() => { const c=document.getElementById("cv"); const d=c.getContext("2d").getImageData(0,0,c.width,c.height).data; let s=0,n=0; for(let i=0;i<d.length;i+=97){s+=d[i]*(i%7+1); if(d[i]>40) n++;} return [c.width,c.height,s,n]; }'
            a=await pg.evaluate(sig); await pg.wait_for_timeout(700); bb=await pg.evaluate(sig)
            # drag rotate
            await pg.uncheck('#spin'); await pg.wait_for_timeout(200); c1=await pg.evaluate(sig)
            box=await pg.locator('#cv').bounding_box()
            await pg.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2); await pg.mouse.down()
            await pg.mouse.move(box['x']+box['width']/2+120,box['y']+box['height']/2+30,steps=8); await pg.mouse.up(); await pg.wait_for_timeout(300)
            c2=await pg.evaluate(sig)
            await pg.click('#stage button[data-s="2"]'); await pg.wait_for_timeout(500)
            await pg.screenshot(path=pre+'-chart-mean.png')
            res=[name,r.status,robots,'spin_changes',a[2]!=bb[2],'lit',a[3],'drag_changes',c1[2]!=c2[2]]
            for v in ['languages','concepts','root','world','findings']:
                await pg.click(f'nav.views a[href="#{v}"]'); await pg.wait_for_timeout(500)
                vis=await pg.is_visible(f'#v-{v}'); cur=await pg.get_attribute(f'nav.views a[href="#{v}"]','aria-current')
                res.append(f'{v}:{vis}/{cur}')
                if v in ('languages','root','findings'): await pg.screenshot(path=f'{pre}-{v}.png')
            chl=await pg.get_attribute('#chl-lab-nav a[href="/"]','aria-current')
            res.append('chlnav_academy_current='+str(chl))
            await pg.click('nav.views a[href="#chart"]'); await pg.wait_for_timeout(300)
            if mobile:
                await pg.evaluate('scrollTo(0,0)')
                await pg.click('label.chl-lab-nav__toggle'); await pg.wait_for_timeout(300)
                res.append('menu_open='+str(await pg.is_visible('#chl-lab-nav a[href="https://newz.codex-hive.com"]')))
                await pg.screenshot(path=pre+'-menu-open.png')
                await pg.click('label.chl-lab-nav__toggle')
            await pg.screenshot(path=pre+'-full.png',full_page=True)
            sw=await pg.evaluate('document.documentElement.scrollWidth')
            print(*res,'scrollWidth',sw,'errors',errs)
            await ctx.close()
        # home card
        ctx=await b.new_context(viewport={'width':1440,'height':900}); pg=await ctx.new_page(); errs=[]
        pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
        await pg.goto(BASE+'/',wait_until='networkidle')
        card=pg.locator('a.module'); await card.scroll_into_view_if_needed(); await pg.wait_for_timeout(300)
        await pg.screenshot(path=f'screenshots/rosetta-{TAG}-home-card-1440.png')
        await card.click(); await pg.wait_for_load_state('networkidle'); print('home card ->',pg.url,errs)
        ctx=await b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True); pg=await ctx.new_page()
        await pg.goto(BASE+'/',wait_until='networkidle'); card=pg.locator('a.module'); await card.scroll_into_view_if_needed(); await pg.wait_for_timeout(300)
        await pg.screenshot(path=f'screenshots/rosetta-{TAG}-home-card-390.png')
        await b.close()
asyncio.run(main())
