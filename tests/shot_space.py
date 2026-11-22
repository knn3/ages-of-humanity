import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
ZS = [float(z) for z in sys.argv[2].split(',')]; AFTER = float(sys.argv[1]); OUT = sys.argv[3]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width':1400,'height':900}); errs=[]
        pg.on('pageerror', lambda e: errs.append('PAGEERR '+str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(800); await pg.keyboard.press('Space')
        await pg.evaluate("(after) => { const A = window.__aoh; A.newWorld(5213); for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1); const e0 = A.W.simTime; while (A.W.simTime - e0 < after) A.step(0.1); }", AFTER)
        if await pg.evaluate("document.querySelector('#modal').classList.contains('open')"): await pg.click('#dialog [data-close]'); await pg.keyboard.press('Space')
        await pg.wait_for_timeout(7000)
        if await pg.evaluate("document.querySelector('#modal').classList.contains('open')"): await pg.click('#dialog [data-close]')
        await pg.evaluate("() => { if (document.querySelector('.js-pause').textContent.trim() === 'Pause') document.querySelector('.js-pause').click(); document.querySelector('#futToggle').click(); }")
        r = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
        ims = []
        for z in ZS:
            await pg.evaluate(f"window.__aoh.setZoom({z})"); await pg.wait_for_timeout(400)
            await pg.screenshot(path='tmp.png', clip={'x': r[0], 'y': r[1], 'width': r[2], 'height': r[3]}); ims.append(Image.open('tmp.png').copy())
        w = ims[0].width // 2; h = ims[0].height // 2; out = Image.new('RGB', (w * len(ims) + 10 * (len(ims) - 1), h), (30, 30, 30))
        for k, im in enumerate(ims): out.paste(im.resize((w, h)), (k * (w + 10), 0))
        out.save(OUT); print('\n'.join(errs) or 'no errors'); await b.close()
asyncio.run(main())
