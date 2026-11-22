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
        await pg.evaluate("() => { const A = window.__aoh; for (let i = 0; i < 4000; i++) A.step(0.1); }")
        await pg.keyboard.press('Space')
        cv = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top, r.width]; })()")
        vis = "getComputedStyle(document.querySelector('#tip')).display + ' | ' + document.querySelector('#tip').innerText.replace(/\\n+/g, ' / ').slice(0, 160)"
        for what in ['agent', 'building', 'element']:
            pos = await pg.evaluate("""(what) => { const A = window.__aoh; A.setZoom(1.8); const c = A.W.civs.filter(c => c.alive && c._.agents && c._.agents.length).sort((a, b) => b.era - a.era)[0];
              let x, y; if (what === 'agent') { const a = c._.agents.find(a => a.kind === 'walk') || c._.agents[0]; x = a.x; y = A.gy(a.x) - 6; }
              else if (what === 'building') { const b = c._.items.find(b => b.w > 14) || c._.items[0]; x = b.x + b.w / 2; y = b.base - b.h / 2; }
              else { const e = A.W.elements.find(e => e.type === 'forest' || e.type === 'herd'); x = e.x; y = A.gy(e.x) - 8; }
              A.V.cam = x - A.V.vw / 2; A.V.camTarget = null; A.V.camY = null; A.render(); return A.W2S(x, y); }""", what)
            await pg.mouse.click(cv[0] + pos[0], cv[1] + pos[1]); await pg.wait_for_timeout(200)
            print(what, 'left click ->', await pg.evaluate("getComputedStyle(document.querySelector('#tip')).display"))
            await pg.mouse.click(cv[0] + pos[0], cv[1] + pos[1], button='right'); await pg.wait_for_timeout(200)
            print(what, 'right click ->', await pg.evaluate(vis))
            await pg.mouse.click(cv[0] + cv[2] - 40, cv[1] + 60); await pg.wait_for_timeout(200)
            print('  empty click closes:', await pg.evaluate("getComputedStyle(document.querySelector('#tip')).display"))
        print('\n'.join(errs) or 'no errors'); await b.close()
asyncio.run(main())
