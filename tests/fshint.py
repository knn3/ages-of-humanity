# Full screen leaves out the general hint bar (scroll/drag/Tools); a tool's own hint still shows; the page view keeps it
import asyncio, json
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        r = json.loads(await pg.evaluate(r'''async () => { const A = window.__aoh, vis = () => document.querySelector('#hint').offsetParent !== null && document.querySelector('#hint').getBoundingClientRect().height > 0, o = {};
          const feed = () => Math.round(document.querySelector('#stage').getBoundingClientRect().bottom - document.querySelector('#fschron').getBoundingClientRect().bottom);
          o.page = vis(); A.enterFS(); await new Promise(r => setTimeout(r, 100)); o.fsIdle = vis(); o.feedIdle = feed();
          A.setTool({ kind: 'el', type: 'river' }); await new Promise(r => setTimeout(r, 100)); o.fsTool = vis(); o.toolText = document.querySelector('#hint').textContent; o.feedTool = feed();
          A.setTool(null); await new Promise(r => setTimeout(r, 100)); o.fsAgain = vis(); A.exitFS(); await new Promise(r => setTimeout(r, 100)); o.pageAgain = vis(); return JSON.stringify(o); }'''))
        print(' ', r)
        check('page view keeps the hint bar', r['page'] and r['pageAgain'])
        check('full screen leaves the general hint out, and the chronicle feed drops into its place', not r['fsIdle'] and not r['fsAgain'] and r['feedIdle'] < r['feedTool'], str((r['feedIdle'], r['feedTool'])))
        check('a tool still shows its own hint in full screen', r['fsTool'] and 'Esc' in r['toolText'], r['toolText'])
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
