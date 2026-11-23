# natural worlds, no forcing: run from the start to a time after the first people reaches space, then summarise
import asyncio, json, sys
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
N, AFTER, SUMMARY = int(sys.argv[1]), float(sys.argv[2]), open(sys.argv[3]).read()
RUN = r'''([seed, after]) => { const A = window.__aoh; A.newWorld(seed);
  for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1);
  const e0 = A.W.simTime; for (let i = 0; i < after * 10 && A.W.simTime - e0 < after; i++) A.step(0.1); A.render(); return Math.round(A.W.simTime - e0); }'''
async def worker(b, seeds, out):
    pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(GAME); await pg.wait_for_timeout(600); await pg.keyboard.press('Space')
    for s in seeds:
        t = await pg.evaluate(RUN, [s, AFTER]); res = await pg.evaluate(SUMMARY)
        out.append(f'seed {s} (+{t}s after space): {res}')
    if errs: out.append('ERRORS ' + ' | '.join(errs[:3]))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        out = []; seeds = [int(x) for x in os.environ['SEEDS'].split(',')] if os.environ.get('SEEDS') else [5000 + 71 * i for i in range(N)]  # SEEDS=5000,6207 re-runs chosen worlds
        await asyncio.gather(*[worker(b, seeds[k::6], out) for k in range(min(6, N))])
        await b.close()
    print('\n'.join(out))
asyncio.run(main())
