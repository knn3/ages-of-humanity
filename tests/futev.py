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
        await pg.click('#t-events')
        print('buttons:', await pg.evaluate("[...document.querySelectorAll('#tab-events [data-ev^=\"f_\"]')].map(b => b.innerText.trim() + (b.disabled ? '(locked)' : '')).join(', ')"))
        await pg.evaluate("() => { const A = window.__aoh; A.newWorld(777); for (let i = 0; i < 9000 && A.W.fates.edgeT == null; i++) A.step(0.1); A.render(); }")
        await pg.wait_for_timeout(400)
        print('locked after edge:', await pg.evaluate("[...document.querySelectorAll('#tab-events [data-ev^=\"f_\"]')].filter(b => b.disabled).length"))
        res = []
        for fid in ['threebody','agi','garden','threebody']:
            await pg.click(f'[data-ev="f_{fid}"]'); await pg.wait_for_timeout(250)
            res.append(fid + ':' + (await pg.evaluate("JSON.stringify(window.__aoh.W.fates.active.map(a => a.id))")) + ' toast=' + await pg.evaluate("document.querySelector('#toast').textContent"))
        print('\n'.join(res))
        ib = await pg.query_selector('.ibtn[data-info="ev:f_contact"]'); await ib.hover(); await pg.wait_for_timeout(300)
        print('info:', (await pg.evaluate("document.querySelector('#pop').innerText")).replace('\n',' | '))
        print('panel:', (await pg.evaluate("document.querySelector('#futures').innerText")).replace('\n',' | ')[:200])
        print('\n'.join(errs) or 'no errors'); await b.close()
asyncio.run(main())
