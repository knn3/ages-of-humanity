# Full screen: the chronicle feed can be folded away and back; the choice is remembered; while folded it counts new lines
import asyncio, json
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))
STATE = "() => { const s = document.querySelector('#fschron'), b = document.querySelector('#fslogToggle'); return JSON.stringify({ shown: getComputedStyle(s).display !== 'none', btn: !!b.offsetParent, items: document.querySelectorAll('#fslog li').length, listShown: getComputedStyle(document.querySelector('#fslog')).display !== 'none', closed: s.classList.contains('closed'), expanded: b.getAttribute('aria-expanded'), badge: document.querySelector('#fslogNew').textContent }); }"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        ctx = await b.new_context(viewport={'width': 1300, 'height': 850}); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700)
        ev = pg.evaluate
        r = json.loads(await ev(STATE))
        check('outside full screen there is no feed and no toggle', not r['shown'] and not r['btn'], str(r))
        await ev("() => { const A = window.__aoh; A.newWorld(951); A.UI.random = true; for (let i = 0; i < 400; i++) A.step(0.1); A.enterFS(); }"); await pg.wait_for_timeout(400)
        r = json.loads(await ev(STATE))
        check('in full screen the feed shows the latest lines under a Chronicle toggle', r['shown'] and r['btn'] and r['items'] == 3 and r['listShown'] and r['expanded'] == 'true', str(r))
        await pg.click('#fslogToggle'); await pg.wait_for_timeout(150)
        r = json.loads(await ev(STATE))
        check('clicking it folds the feed away', r['closed'] and not r['listShown'] and r['expanded'] == 'false' and r['badge'] == '', str(r))
        await ev("() => { const A = window.__aoh; let n = 0; while (n < 400 && A.W.chron.length && A.W.chron[0] === A.W.chron[0] && !A.UI.__x) { A.step(0.1); n++; } }")
        r = json.loads(await ev(STATE))
        check('while folded it counts the new lines', r['closed'] and r['badge'].endswith('new'), str(r))
        # remembered after a reload
        await pg.reload(); await pg.wait_for_timeout(700); await ev("() => { const A = window.__aoh; A.newWorld(952); for (let i = 0; i < 200; i++) A.step(0.1); A.enterFS(); }"); await pg.wait_for_timeout(300)
        r = json.loads(await ev(STATE))
        check('the choice is remembered after a reload', r['closed'] and not r['listShown'], str(r))
        await pg.click('#fslogToggle'); await pg.wait_for_timeout(150)
        n = await ev('() => window.__aoh.W.chron.length')
        r = json.loads(await ev(STATE))
        check('clicking again opens it', not r['closed'] and r['listShown'] and r['items'] == min(3, n) and r['badge'] == '', str(r))
        await ev("() => { const s = document.querySelector('#stage'); s.scrollIntoView(); }")
        await (await pg.query_selector('#stage')).screenshot(path='fslog_open.png')
        await pg.click('#fslogToggle'); await pg.wait_for_timeout(100); await ev("() => { const A = window.__aoh; for (let i = 0; i < 300; i++) A.step(0.1); }"); await pg.wait_for_timeout(200)
        await (await pg.query_selector('#stage')).screenshot(path='fslog_closed.png')
        await pg.click('#fslogToggle')
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
