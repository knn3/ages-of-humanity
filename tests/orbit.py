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
        await pg.goto(GAME); await pg.wait_for_timeout(800)
        await pg.keyboard.press('Space')
        await pg.evaluate("() => { const A = window.__aoh; A.W.civs.forEach((c, i) => { c.era = [12, 13, 11, 14][i % 4]; c.tech = 20; c.reached[c.era] = 2200; }); for (let i = 0; i < 20; i++) A.step(0.1); A.setZoom(0.05); }")
        await pg.wait_for_timeout(800)
        r = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
        await pg.screenshot(path='orbit1.png', clip={'x': r[0], 'y': r[1], 'width': r[2], 'height': r[3]})
        # debris: war between spacefaring peoples
        out = await pg.evaluate("""() => { const A = window.__aoh; const cs = A.W.civs.filter(c => c.alive); A.W.wars.push({ a: cs[0].id, b: cs[1].id, t: 0, adv: 0 }, { a: cs[1].id, b: cs[2].id, t: 0, adv: 0 }, { a: cs[0].id, b: cs[3].id, t: 0, adv: 0 });
          let t = 0, wl = []; for (let i = 0; i < 2000 && !A.W.kessler; i++) { A.step(0.1); t += 0.1; if (i % 100 === 0) wl.push(A.W.wars.length + ":" + (A.W.debris || 0).toFixed(2)); } return JSON.stringify({ debris: A.W.debris, kessler: !!A.W.kessler, after: Math.round(t), wl, log: A.W.chron.find(e => /Debris|collisions/.test(e.h)) ? 'logged' : 'none', saved: A.sanitizeWorld(A.serialize()).debris }); }""")
        print(out)
        await pg.wait_for_timeout(500)
        await pg.screenshot(path='orbit2.png', clip={'x': r[0], 'y': r[1], 'width': r[2], 'height': r[3]})
        t = await pg.evaluate("() => { const A = window.__aoh; const t0 = performance.now(); for (let i = 0; i < 30; i++) A.render(); return ((performance.now() - t0) / 30).toFixed(1); }")
        print('render ms at globe:', t)
        print('\n'.join(errs) or 'no errors'); await b.close()
asyncio.run(main())
