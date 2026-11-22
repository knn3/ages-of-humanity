import asyncio
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width':1400,'height':900}); errs=[]
        pg.on('pageerror', lambda e: errs.append('PAGEERR '+str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(800); await pg.keyboard.press('Space')
        await pg.click('#t-elements')
        print('space tools:', await pg.evaluate("[...document.querySelectorAll('[data-tool=\"el:helium3\"], [data-tool=\"el:asteroid\"], [data-tool=\"el:icemoon\"]')].map(b => b.innerText.trim()).join(', ')"))
        await pg.click('[data-tool="el:asteroid"]')
        cv = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left + r.width / 2, Math.min(r.top + r.height / 2, innerHeight - 100)]; })()")
        await pg.mouse.click(cv[0], cv[1]); await pg.wait_for_timeout(200)
        print('on land:', await pg.evaluate("document.querySelector('#toast').textContent"))
        await pg.evaluate("window.__aoh.setZoom(0.001)"); await pg.wait_for_timeout(300)
        n0 = await pg.evaluate("window.__aoh.W.spaceRes.length")
        await pg.mouse.click(cv[0], cv[1]); await pg.wait_for_timeout(200)
        print('in solar view:', await pg.evaluate("document.querySelector('#toast').textContent"), n0, '->', await pg.evaluate("window.__aoh.W.spaceRes.length"))
        ib = await pg.query_selector('.ibtn[data-info="el:asteroid"]'); await ib.hover(); await pg.wait_for_timeout(250)
        print('info:', (await pg.evaluate("document.querySelector('#pop').innerText")).replace('\n', ' | '))
        print('saved:', await pg.evaluate("window.__aoh.sanitizeWorld(window.__aoh.serialize()).spaceRes.length"))
        print('\n'.join(errs) or 'no errors'); await b.close()
asyncio.run(main())
