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
        await pg.evaluate("() => { const A = window.__aoh; A.newWorld(4242); for (let i = 0; i < 9000 && A.W.fates.edgeT == null; i++) A.step(0.1); }")
        # natural ending: collapse with a nuclear war keeps pressure high past its span
        await pg.evaluate("() => { const A = window.__aoh; A.startFate('collapse', 'event'); A.W.fates.bias.collapse = 1.4; for (let i = 0; i < 1700 && !A.W.fates.ended; i++) { A.W.nukeT = A.W.simTime; A.step(0.1); } }")
        print('ended:', await pg.evaluate("window.__aoh.W.fates.ended"))
        await pg.wait_for_timeout(2800)
        print('card:', (await pg.evaluate("document.querySelector('#modal').classList.contains('open') && document.querySelector('#dialog').innerText")).replace('\n', ' | '))
        print('paused:', await pg.evaluate("document.querySelector('.js-pause').textContent"), 'filter:', await pg.evaluate("document.querySelector('#world').style.filter"))
        await pg.screenshot(path='epi.png')
        await pg.click('#epiRise'); await pg.wait_for_timeout(600)
        print('after rise:', await pg.evaluate("""() => { const A = window.__aoh; return JSON.stringify({ eras: A.W.civs.filter(c => c.alive).map(c => c.era), cycle: A.W.fates.cycle, ended: A.W.fates.ended, paused: document.querySelector('.js-pause').textContent, filter: document.querySelector('#world').style.filter, log: A.W.chron[0].h }); }"""))
        await pg.evaluate("() => { const A = window.__aoh; for (let i = 0; i < 1500; i++) A.step(0.1); }")
        print('cycle 2 progress:', await pg.evaluate("window.__aoh.W.chron.filter(e => e.k === 'era').slice(0, 2).map(e => e.h.replace(/<[^>]+>/g, '')).join(' || ')"))
        # galactic goal ending + keep watching + save roundtrip
        await pg.evaluate("() => { const A = window.__aoh; A.newWorld(99); for (const c of A.W.civs) { c.era = 14; c.tech = 99.9; } A.W.fates.edgeT = 1; for (let i = 0; i < 40; i++) A.step(0.1); }")
        await pg.wait_for_timeout(2800)
        print('galactic card:', (await pg.evaluate("document.querySelector('#dialog').innerText")).split('\n')[0:3])
        await pg.click('#dialog [data-close]'); await pg.wait_for_timeout(300)
        print('after keep watching paused:', await pg.evaluate("document.querySelector('.js-pause').textContent"), 'saved ended:', await pg.evaluate("window.__aoh.sanitizeWorld(window.__aoh.serialize()).fates.ended"))
        print('\n'.join(errs) or 'no errors'); await b.close()
asyncio.run(main())
