# The strip map under the world is shown on the ground and hidden once the land bends into the globe and out into space
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
        for fs in [False, True]:
            r = json.loads(await pg.evaluate(r'''async (fs) => { const A = window.__aoh, m = document.querySelector('#mini'), o = {}, wait = () => new Promise(r => setTimeout(r, 450));
              const shown = () => getComputedStyle(m).visibility !== 'hidden' && +getComputedStyle(m).opacity > .5;
              if (fs) A.enterFS(); const h0 = document.querySelector('#world').getBoundingClientRect().height;
              for (const [k, z] of [['ground', .75], ['close', 3], ['globe', .06], ['system', .004], ['galaxy', .00002], ['back', .75]]) { A.setZoom(z); await wait(); o[k] = [shown(), +A.V.b.toFixed(2)]; }
              o.stillH = Math.abs(document.querySelector('#world').getBoundingClientRect().height - h0) < 1; if (fs) A.exitFS(); return JSON.stringify(o); }''', fs))
            tag = 'full screen' if fs else 'page'
            print(f'  {tag}:', r)
            check(f'{tag}: the strip map shows on the ground and close in', r['ground'][0] and r['close'][0] and r['back'][0])
            check(f'{tag}: hidden on the globe, in the solar system and the galaxy', not r['globe'][0] and not r['system'][0] and not r['galaxy'][0])
            check(f'{tag}: hiding it does not move the map', r['stillH'])
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
