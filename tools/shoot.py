import asyncio, sys
from playwright.async_api import async_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8793'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        for name,vp,mobile in [('desktop-1440',{'width':1440,'height':900},False),('mobile-390',{'width':390,'height':844},True)]:
            ctx=await b.new_context(viewport=vp,device_scale_factor=2 if mobile else 1,is_mobile=mobile,has_touch=mobile)
            pg=await ctx.new_page(); errs=[]
            pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
            pg.on('requestfailed',lambda r: errs.append('FAIL '+r.url))
            r=await pg.goto(BASE+'/',wait_until='networkidle'); await pg.wait_for_timeout(600)
            await pg.screenshot(path=f'screenshots/{name}-top.png')
            await pg.screenshot(path=f'screenshots/{name}-full.png',full_page=True)
            if mobile:
                await pg.click('label.chl-lab-nav__toggle'); await pg.wait_for_timeout(300)
                await pg.screenshot(path=f'screenshots/{name}-menu-open.png')
            sw=await pg.evaluate('document.documentElement.scrollWidth')
            print(name,r.status,'scrollWidth',sw,'errors',errs)
        r=await pg.goto(BASE+'/nope'); print('404 status',r.status)
        await b.close()
asyncio.run(main())
