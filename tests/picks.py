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
        for steps in [0, 5200]:
            print(await pg.evaluate("""(steps) => { const A = window.__aoh; for (let i = 0; i < steps; i++) A.step(0.1); if (steps) A.applyEvent(A.findEvent('meteor'), A.W.civs.find(c => c.alive).x + 400, {});
              A.setZoom(1.6); const seen = {};
              for (let x = 0; x < 12000; x += 500) { A.V.cam = x; A.V.camTarget = null; A.V.camY = null; A.render(); const r = document.querySelector('#world').getBoundingClientRect();
                for (let sx = 4; sx < r.width; sx += 7) for (let sy = 4; sy < r.height; sy += 7) { const t = A.tipTarget(sx, sy); if (!t) continue; const n = t.p ? t.p.kind + ':' + t.p.d.name : t.a ? 'agent' : t.b ? 'building' : 'el:' + t.el.type; seen[n] = (seen[n] || 0) + 1; } }
              return Object.keys(seen).sort().join(', '); }""", steps))
        # click a tree and a ship for real
        for kind in ['tree', 'animal', 'ship']:
            pos = await pg.evaluate("""(kind) => { const A = window.__aoh; for (let x = 0; x < 12000; x += 400) { A.V.cam = x; A.render(); const q = A.V.picks.find(q => q.kind === kind); if (q) { const [sx, sy] = A.W2S((q.x0 + q.x1) / 2, (q.y0 + q.y1) / 2); return [sx, sy]; } } return null; }""", kind)
            if not pos: print(kind, 'not on map'); continue
            cv = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top]; })()")
            await pg.mouse.click(cv[0] + pos[0], cv[1] + pos[1]); await pg.wait_for_timeout(200)
            print(kind, '->', (await pg.evaluate("getComputedStyle(document.querySelector('#tip')).display + ' | ' + document.querySelector('#tip').innerText.replace(/\\n+/g, ' / ')")))
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(100)
        print('\n'.join(errs) or 'no errors'); await b.close()
asyncio.run(main())
