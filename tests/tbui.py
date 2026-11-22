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
        await pg.evaluate("() => { const A = window.__aoh; A.newWorld(5284); for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1); const e0 = A.W.simTime; while (A.W.simTime - e0 < 150) A.step(0.1); }")
        await pg.keyboard.press('Space'); await pg.click('#t-events'); await pg.click('[data-ev="f_threebody"]'); await pg.wait_for_timeout(700)
        await pg.evaluate("scrollTo(0, 0)")
        btn = await pg.query_selector('#tbPick'); print('choose button shown:', bool(btn))
        await btn.click(); await pg.wait_for_timeout(200)
        names = await pg.evaluate("[...document.querySelectorAll('[data-tbc]')].map(b => b.textContent)"); print('choices:', names)
        await pg.click('[data-tbc]'); await pg.wait_for_timeout(300)
        print('chosen:', await pg.evaluate("JSON.stringify([window.__aoh.W.tb.strat, window.__aoh.W.tb.chosen, !!window.__aoh.W.tb.plan])"), '| button gone:', not await pg.query_selector('#tbPick'))
        await pg.evaluate("() => { const A = window.__aoh; for (let i = 0; i < 300; i++) A.step(0.1); }"); await pg.wait_for_timeout(600)
        print('card chips:', await pg.evaluate("[...document.querySelectorAll('#civs .chip')].map(c => c.textContent).filter(t => /ists|ers/.test(t)).slice(0, 6).join(', ')"))
        w = await pg.evaluate("() => { const A = window.__aoh; const t1 = JSON.stringify(A.W.tb); A.loadWorld(A.serialize()); return t1 === JSON.stringify(A.W.tb) ? 'tb state saved exactly' : 'DIFF ' + t1.slice(0, 120) + ' vs ' + JSON.stringify(A.W.tb).slice(0, 120); }")
        print(w)
        res = await pg.evaluate("() => { const A = window.__aoh; const c = A.W.civs.find(c => c.alive); const t0 = c.tech; c.tech = 99.5; A.step(0.1); const locked = c.tech; for (let i = 0; i < 5400; i++) A.step(0.1); return JSON.stringify({ capped: locked <= 99.9, tbAfter: A.W.tb, last: A.W.chron.filter(e => e.k === 'fate').slice(0, 3).map(e => e.h.replace(/<[^>]+>/g, '').slice(0, 100)) }); }")
        print(res)
        print('\n'.join(errs) or 'no errors'); await b.close()
asyncio.run(main())
