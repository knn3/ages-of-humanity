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
        await pg.evaluate("() => { const A = window.__aoh; A.newWorld(5355); for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1); const e0 = A.W.simTime; while (A.W.simTime - e0 < 120) A.step(0.1); }")
        await pg.click('#t-events')
        await pg.click('[data-ev="broadcast"]'); await pg.wait_for_timeout(200)
        print('broadcast without the signal:', await pg.evaluate("document.querySelector('#toast').textContent"))
        await pg.click('[data-ev="f_threebody"]')
        await pg.evaluate("() => { const A = window.__aoh; for (let i = 0; i < 30000 && A.W.tb && !A.W.tb.deter; i++) A.step(0.1); }")
        print('panel during deterrence:', (await pg.evaluate("document.querySelector('#futures').innerText")).replace('\n', ' | ')[:160])
        await pg.click('[data-ev="broadcast"]'); await pg.wait_for_timeout(300)
        print('after broadcast:', await pg.evaluate("JSON.stringify({ strike: !!window.__aoh.W.tb.strikeT })"), (await pg.evaluate("document.querySelector('#futures').innerText")).replace('\n', ' | ')[:120])
        await pg.evaluate("window.__aoh.setZoom(0.03)")
        await pg.evaluate("() => { const A = window.__aoh; for (let i = 0; i < 30000 && A.W.tb; i++) A.step(0.1); }")
        await pg.evaluate("scrollTo(0, 0)")
        r = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top, r.width, Math.min(r.height, 900 - r.top)]; })()")
        shots = []
        for t in [1500, 3500, 6500]:
            await pg.wait_for_timeout(t - (sum([0]) if not shots else 0) if not shots else 2000 if t == 3500 else 3000)
            await pg.screenshot(path=f'flat{t}.png', clip={'x': r[0], 'y': r[1], 'width': r[2], 'height': r[3]}); shots.append(f'flat{t}.png')
        await pg.wait_for_timeout(1200)
        print('ended:', await pg.evaluate("window.__aoh.W.fates.ended"), '| zoom now:', await pg.evaluate("window.__aoh.V.zoom.toFixed(2)"), '| epilogue:', await pg.evaluate("document.querySelector('#modal').classList.contains('open') && document.querySelector('#dialog').innerText.replace(/\\n+/g, ' | ').slice(0, 260)"))
        print('\n'.join(errs) or 'no errors'); await b.close()
    ims = [Image.open(f) for f in shots]; w = ims[0].width // 3; h = ims[0].height // 3
    out = Image.new('RGB', (w * 3 + 20, h), (30, 30, 30))
    for k, im in enumerate(ims): out.paste(im.resize((w, h)), (k * (w + 10), 0))
    out.save('flatcomp.png')
asyncio.run(main())
