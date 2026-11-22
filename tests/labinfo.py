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
        await pg.evaluate("() => { const A = window.__aoh; for (let i = 0; i < 3000; i++) A.step(0.1); const c = A.W.civs.find(c => c.alive); A.V.cam = c.x - A.V.vw / 2; A.V.camTarget = null; }")
        await pg.wait_for_timeout(500)
        n = await pg.evaluate("[...document.querySelectorAll('#labInfo .ibtn')].filter(b => !b.hidden).length")
        print('visible label buttons:', n)
        ib = await pg.query_selector('#labInfo .ibtn:not([hidden])')
        await ib.hover(); await pg.wait_for_timeout(300)
        print('civ pop:', (await pg.evaluate("document.querySelector('#pop').classList.contains('show') ? document.querySelector('#pop').innerText : 'NOT SHOWN'")).replace('\n', ' | ')[:300])
        await ib.click(); await pg.wait_for_timeout(200)
        r = await ib.bounding_box(); await pg.screenshot(path='lab.png', clip={'x': max(0, r['x'] - 260), 'y': max(0, r['y'] - 60), 'width': 640, 'height': 300})
        await pg.keyboard.press('Escape')
        print('pop after esc:', await pg.evaluate("document.querySelector('#pop').classList.contains('show')"))
        # zoomed in: buildings no tip; element tip appears then disappears right after leaving
        res = await pg.evaluate("""() => { const A = window.__aoh; A.setZoom(1.8); const c = A.W.civs.find(c => c.alive); A.V.cam = c.x - A.V.vw / 2; A.V.camTarget = null; A.V.camY = null; A.render();
          const b = c._.items[0]; const [bx, by] = A.W2S(b.x + b.w / 2, b.base - b.h / 2); const e = A.W.elements.find(e => e.type === 'forest' || e.type === 'herd');
          A.V.cam = e.x - A.V.vw / 2; A.render(); const [ex, ey] = A.W2S(e.x, A.gy(e.x) - 8); const [ox, oy] = A.W2S(e.x + 70, A.gy(e.x + 70) - 8);
          return [!!A.tipTarget(bx, by), e.type, ex, ey, ox, oy]; }""")
        print('building hover returns:', res[0])
        cv = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top]; })()")
        await pg.mouse.move(cv[0] + res[2], cv[1] + res[3]); await pg.wait_for_timeout(150)
        print(res[1], 'tip on:', await pg.evaluate("getComputedStyle(document.querySelector('#tip')).display"))
        await pg.mouse.move(cv[0] + res[4], cv[1] + res[5]); await pg.wait_for_timeout(250)
        print('tip after leaving:', await pg.evaluate("getComputedStyle(document.querySelector('#tip')).display"))
        await pg.evaluate("window.__aoh.setZoom(0.06)"); await pg.wait_for_timeout(400)
        print('globe label buttons visible:', await pg.evaluate("[...document.querySelectorAll('#labInfo .ibtn')].filter(b => !b.hidden).length"))
        print('\n'.join(errs) or 'no errors'); await b.close()
asyncio.run(main())
