import asyncio
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width':1400,'height':900})
        errs=[]
        pg.on('pageerror', lambda e: errs.append('PAGEERR '+str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME)
        await pg.wait_for_timeout(1000)
        await pg.evaluate("() => { const A = window.__aoh; for (let i = 0; i < 1500; i++) A.step(0.1); A.render(); }")
        scan = """(z) => { const A = window.__aoh; if (z) A.setZoom(z); A.render(); const cv = document.querySelector('canvas'), r = cv.getBoundingClientRect(); let civ = 0, el = 0, n = 0, sky = 0;
          for (let sx = 10; sx < r.width; sx += 15) for (let sy = 10; sy < r.height; sy += 15) { n++; const t = A.tipTarget(sx, sy); if (t) { if (t.el) el++; else civ++; if (sy < r.height * .2) sky++; } }
          return { zoom: +A.V.zoom.toFixed(3), b: +A.V.b.toFixed(2), n, civ, el, topFifthHits: sky }; }"""
        for z in [None, 1.4, 0.6, 0.5, 0.45, 0.2, 0.06, 0.02]:
            print(await pg.evaluate(scan, z))
        # real mouse at globe zoom: no tip anywhere
        await pg.evaluate("window.__aoh.setZoom(0.08)")
        shown = 0
        for fx in range(5, 100, 6):
            for fy in range(5, 100, 8):
                await pg.mouse.move(14 + 13.7 * fx, 60 + 6 * fy)
                if await pg.evaluate("getComputedStyle(document.querySelector('#tip')).display") == 'block': shown += 1
        print('globe mouse sweep tips shown:', shown)
        print('\n'.join(errs) or 'no errors')
        await b.close()
asyncio.run(main())
