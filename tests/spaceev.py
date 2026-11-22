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
        await pg.goto(GAME); await pg.wait_for_timeout(800); await pg.keyboard.press('Space')
        await pg.click('#t-events')
        print('before space, locked:', await pg.evaluate("['flare','cstrike','lsfail','debris','comet'].map(id => id + ':' + document.querySelector(`[data-ev=\"${id}\"]`).disabled).join(' ')"))
        await pg.click('[data-ev="comet"]'); await pg.wait_for_timeout(200)
        print('early comet:', await pg.evaluate("window.__aoh.W.chron[0].h"))
        await pg.evaluate("() => { const A = window.__aoh; A.newWorld(5213); for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1); const e0 = A.W.simTime; while (A.W.simTime - e0 < 300) A.step(0.1); A.render(); }")
        await pg.wait_for_timeout(400)
        for ev in ['flare', 'cstrike', 'lsfail', 'debris', 'comet']:
            n0 = await pg.evaluate("window.__aoh.W.chron[0].h")
            if await pg.evaluate(f"document.querySelector('[data-ev=\"{ev}\"]').disabled"): print(ev, 'locked in this world (no people in the needed age)'); continue
            await pg.click(f'[data-ev="{ev}"]'); await pg.wait_for_timeout(150)
            await pg.evaluate("() => { const A = window.__aoh; for (let i = 0; i < 20; i++) A.step(0.1); }")
            new = await pg.evaluate("(h0) => { const c = window.__aoh.W.chron, i = c.findIndex(e => e.h === h0); return c.slice(0, i < 0 ? 3 : i).map(e => e.h.replace(/<[^>]+>/g, '').slice(0, 90)).reverse().slice(0, 2).join(' || '); }", n0)
            print(ev, '->', new or ('toast: ' + await pg.evaluate("document.querySelector('#toast').textContent")))
        print('kessler after debris:', await pg.evaluate("!!window.__aoh.W.kessler"))
        ib = await pg.query_selector('.ibtn[data-info="ev:flare"]'); await ib.hover(); await pg.wait_for_timeout(250)
        print('info:', (await pg.evaluate("document.querySelector('#pop').innerText")).replace('\n', ' | ')[:200])
        print('\n'.join(errs) or 'no errors'); await b.close()
asyncio.run(main())
