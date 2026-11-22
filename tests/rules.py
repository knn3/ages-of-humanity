import asyncio
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width':1300,'height':900}); errs=[]
        pg.on('pageerror', lambda e: errs.append('PAGEERR '+str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(800)
        await pg.keyboard.press('Space')
        await pg.click('#t-rules')
        async def add(cond, fate=None, num=None, ev=None, once='1'):
            await pg.select_option('#rc', cond)
            if fate: await pg.select_option('#rvFate', fate)
            if num is not None: await pg.fill('#rvNum', str(num))
            await pg.select_option('#re', ev); await pg.select_option('#ro', once)
            await pg.click('#ruleForm [type=submit]'); await pg.wait_for_timeout(100)
        await pg.select_option('#rc', 'fateLeft')
        print('fate box shown:', await pg.evaluate("!document.querySelector('#rvFateBox').hidden"), 'num label:', await pg.evaluate("document.querySelector('#rvNumL').textContent"))
        await add('fateLeft', 'threebody', 50, 'peace')
        await add('fateBegin', 'agi', None, 'end:agi')
        await add('fateEnd', 'any', None, 'f_garden')
        await add('ending', None, None, 'trade')
        print('rules:', await pg.evaluate("[...document.querySelectorAll('#ruleList .t')].map(t => t.childNodes[0].textContent).slice(-4).join(' || ')"))
        out = await pg.evaluate("""() => { const A = window.__aoh; A.newWorld(2024); for (let i = 0; i < 9000 && A.W.fates.edgeT == null; i++) A.step(0.1);
          const log = () => A.W.chron.filter(e => e.k === 'rule').map(e => e.h.replace(/<[^>]+>/g, '')).reverse();
          A.startFate('agi', 'event'); for (let i = 0; i < 30; i++) A.step(0.1);
          const r1 = { agiActive: A.W.fates.active.some(a => a.id === 'agi'), garden: A.W.fates.active.some(a => a.id === 'garden') };
          A.startFate('threebody', 'event'); let fired = false, left = null; for (let i = 0; i < 3000 && !fired; i++) { A.step(0.1); fired = log().some(l => /has 50 years/.test(l)); const a = A.W.fates.active.find(a => a.id === 'threebody'); if (a) left = Math.round(A.fateYearsLeft ? A.fateYearsLeft(a) : 0); }
          A.reachEnding('collapse'); for (let i = 0; i < 30; i++) A.step(0.1);
          return JSON.stringify({ r1, fired, log: log() }); }""")
        print(out)
        print('sanitize keeps rules:', await pg.evaluate("() => { const r = JSON.parse(localStorage.getItem('aoh.custom.v1')).rules; return r.filter(x => x.fate || /^end:/.test(x.ev)).length; }"))
        print('\n'.join(errs) or 'no errors'); await b.close()
asyncio.run(main())
