import asyncio
from playwright.async_api import async_playwright
from PIL import Image
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
        await pg.goto(GAME); await pg.wait_for_timeout(800)
        await pg.keyboard.press('Space')
        r = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
        shots = []
        for z in [.02, .008, .003, .0008, .0004]:
            await pg.evaluate(f"window.__aoh.setZoom({z})"); await pg.wait_for_timeout(350)
            fn = f'sys{z}.png'; await pg.screenshot(path=fn, clip={'x': r[0], 'y': r[1], 'width': r[2], 'height': r[3]}); shots.append(fn)
            print(z, await pg.evaluate("document.querySelector('#alt').innerText.replace(/\\n/g, ' ')"), await pg.evaluate("(() => { const A = window.__aoh; const t0 = performance.now(); for (let i = 0; i < 10; i++) A.render(); return ((performance.now() - t0) / 10).toFixed(1) + 'ms'; })()"))
        # zoom back in with the wheel to the ground works
        await pg.evaluate("window.__aoh.setZoom(0.75)"); await pg.wait_for_timeout(300)
        print('back to ground, b =', await pg.evaluate("window.__aoh.V.b"))
        print('\n'.join(errs) or 'no errors'); await b.close()
    ims = [Image.open(f) for f in shots]; w = ims[0].width // 3; h = ims[0].height // 3
    out = Image.new('RGB', (w * 3 + 20, h * 2 + 10), (30, 30, 30))
    for k, im in enumerate(ims): out.paste(im.resize((w, h)), ((k % 3) * (w + 10), (k // 3) * (h + 10)))
    out.save('syscomp.png')
asyncio.run(main())
