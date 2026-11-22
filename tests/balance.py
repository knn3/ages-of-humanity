import asyncio, json, sys, collections
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
N = int(sys.argv[1]) if len(sys.argv) > 1 else 4
JS = r'''(seed) => {
  const A = window.__aoh; A.newWorld(seed); let t = 0;
  for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1);
  const e0 = A.W.simTime, eras = {};
  for (let i = 0; i < 26000; i++) { A.step(0.1); for (const c of A.W.civs) if (c.alive && c.era > 11 && !(c.era in eras)) eras[c.era] = Math.round(A.W.simTime - e0); if (A.W.fates.ended && !eras.end) eras.end = Math.round(A.W.simTime - e0); if (eras.end && A.W.simTime - e0 > eras.end + 1) break; }
  const F = A.W.fates;
  return JSON.stringify({ seed, edge: Math.round(e0), eras, started: F.hist.map(h => h.id), ended: F.ended, alive: A.W.civs.filter(c => c.alive).length });
}'''
async def worker(b, seeds, out):
    pg = await b.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(GAME); await pg.wait_for_timeout(600)
    await pg.keyboard.press('Space')
    for s in seeds: out.append(json.loads(await pg.evaluate(JS, s)))
    if errs: out.append({'errors': errs[:3]})
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        out = []
        seeds = [1000 + 37 * i for i in range(N * 6)]
        await asyncio.gather(*[worker(b, seeds[k::6], out) for k in range(6)])
        await b.close()
    st, en, gal = collections.Counter(), collections.Counter(), []
    for r in out:
        if 'errors' in r: print('ERR', r); continue
        st.update(r['started']); en[r['ended']] += 1
        print(r)
    print('worlds', len([r for r in out if 'seed' in r]))
    print('started:', dict(st.most_common())); print('endings:', dict(en.most_common()))
asyncio.run(main())
