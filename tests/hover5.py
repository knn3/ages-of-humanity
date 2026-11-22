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
        await pg.keyboard.press('Space')
        res = await pg.evaluate("""() => { const A = window.__aoh, out = [];
          const deps = A.W.elements.filter(e => ['copper','tin','iron','gold','coal','oil','uranium','silicon','lithium'].includes(e.type));
          out.push('deposits: ' + deps.map(e => e.type).join(','));
          const e = deps[0]; A.setZoom(1.6); A.V.cam = e.x - A.V.vw / 2; A.V.camTarget = null; A.V.camY = A.gy(e.x) + 56 - (document.querySelector("canvas").clientHeight / A.V.s) / 2; A.render();
          const dy = Math.min(A.W ? 99999 : 0, A.gy(e.x) + 56);
          const [sx, sy] = A.W2S(e.x, dy), [gx, gy0] = A.W2S(e.x, A.gy(e.x));
          const t = A.tipTarget(sx, sy); out.push(`deposit ${e.type} at screen ${sx|0},${sy|0} (ground at ${gy0|0}) -> ` + (t ? (t.el ? 'element ' + t.el.type : 'civ ' + t.civ.name) : 'nothing'));
          const t2 = A.tipTarget(sx, sy + 120); out.push('120px below the deposit -> ' + (t2 ? (t2.el ? 'element ' + t2.el.type : 'civ ' + t2.civ.name) : 'nothing'));
          const t3 = A.tipTarget(sx + 300, gy0 + 60); out.push('rock away from deposit -> ' + (t3 ? (t3.el ? 'element' : 'civ ' + t3.civ.name) : 'nothing'));
          const t4 = A.tipTarget(sx + 300, A.W2S(e.x + 300 / A.V.s, A.gy(e.x + 300 / A.V.s) - 30)[1]); out.push('just above ground nearby -> ' + (t4 ? (t4.el ? 'element ' + t4.el.type : 'civ ' + t4.civ.name) : 'nothing'));
          out.push('nearby: ' + A.W.elements.filter(o => Math.abs(o.x - e.x) < 260).map(o => o.type + '@' + Math.round(o.x - e.x)).join(', ') + ' s=' + A.V.s.toFixed(2)); return [out.join('\\n'), sx, sy]; }""")
        print(res[0])
        cv = await pg.evaluate("(() => { const r = document.querySelector('canvas').getBoundingClientRect(); return [r.left, r.top]; })()")
        await pg.mouse.move(cv[0] + res[1], cv[1] + res[2]); await pg.wait_for_timeout(150)
        await pg.mouse.click(cv[0] + res[1], cv[1] + res[2], button='right'); await pg.wait_for_timeout(150)
        print('tip:', (await pg.evaluate("document.querySelector('#tip').innerText")).replace('\n', ' | '))
        print('\n'.join(errs) or 'no errors')
        await b.close()
asyncio.run(main())
