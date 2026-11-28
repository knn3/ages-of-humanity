# Long-run error hunt: N natural worlds run from the start to SECONDS after reaching space, drawn at every zoom (ground, globe,
# solar system, galaxy, a planet close-up, a ship's lens) every 100 sim seconds, saved and loaded back half way, with every
# page error and console error caught. Prints one line per world and the errors with where they happened.
import asyncio, json, os, sys, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
N, AFTER = int(sys.argv[1]) if len(sys.argv) > 1 else 12, float(sys.argv[2]) if len(sys.argv) > 2 else 6000
RUN = r'''async ([seed, after]) => { const A = window.__aoh, V = A.V; A.newWorld(seed); window.__where = 'grow';
  for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1);
  const e0 = A.W.simTime, ZS = [1.4, .6, .2, .05, .0016, .00011, .00003]; let k = 0, saved = false;
  while (A.W.simTime - e0 < after) {
    for (let i = 0; i < 1000; i++) A.step(0.1);
    const m = document.querySelector('#modal'); if (m && m.classList.contains('open')) { const r = document.querySelector('#epiRise'); if (r && Math.random() < .5) r.click(); else { const c = document.querySelector('#dialog [data-close]'); if (c) c.click(); else m.classList.remove('open'); } }
    for (const z of ZS) { window.__where = 'zoom ' + z + ' @' + Math.round(A.W.simTime - e0); V.focus = null; A.setZoom(z); A.render(); }
    window.__where = 'focus'; for (const b of ['Sun', 'Jupiter', 'Mars']) { A.setZoom(.0016); A.render(); if (A.focusBody(b)) { A.render(); V.focus = null; } }
    const sh = (A.W.ships || [])[0]; if (sh) { window.__where = 'lens'; A.shipFocus(sh.id, true); A.render(); V.lensShip = null; }
    const st = (A.W.stars || [])[0]; if (st && st.sid != null) { window.__where = 'world close-up'; A.shipFocus(st.sid, true); A.render(); V.focus = null; }
    window.__where = 'ui'; A.updateUI();
    if (!saved && A.W.simTime - e0 > after / 2) { saved = true; window.__where = 'save/load'; const d = A.serialize(); A.loadWorld(JSON.parse(JSON.stringify(d))); A.render(); }
    k++; await new Promise(r => setTimeout(r, 0)); }
  A.setZoom(1); const F = A.W.fates; return JSON.stringify({ t: Math.round(A.W.simTime - e0), year: Math.round(A.W.year), cycle: F.cycle, ended: F.ended, fut: F.hist.map(e => e.id).join(','), voy: A.W.voy ? A.W.voy.out || 'flying' : null, alive: A.W.civs.filter(c => c.alive).length, hist: A.W.hist.length }); }'''
async def worker(b, seeds, out, errs):
    pg = await b.new_page(viewport={'width': 1300, 'height': 850})
    cur = {'seed': None}
    async def where(): 
        try: return await pg.evaluate('window.__where')
        except Exception: return '?'
    pg.on('pageerror', lambda e: errs.append((cur['seed'], 'PAGEERR', str(e)[:300])))
    pg.on('console', lambda m: errs.append((cur['seed'], 'CONSOLE', m.text[:300])) if m.type == 'error' and 'net::' not in m.text and 'Failed to load resource' not in m.text else None)
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(GAME); await pg.wait_for_timeout(600); await pg.keyboard.press('Space')
    for s in seeds:
        cur['seed'] = s
        try: res = await pg.evaluate(RUN, [s, AFTER]); out.append(f'seed {s}: {res}')
        except Exception as e: out.append(f'seed {s}: EXCEPTION at {await where()}: {str(e)[:400]}')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        out, errs = [], []
        seeds = [int(x) for x in os.environ['SEEDS'].split(',')] if os.environ.get('SEEDS') else [13000 + 97 * i for i in range(N)]
        await asyncio.gather(*[worker(b, seeds[k::6], out, errs) for k in range(min(6, len(seeds)))])
        await b.close()
    print('\n'.join(sorted(out)))
    print(f'errors: {len(errs)}')
    for e in errs[:30]: print('  ', e)
asyncio.run(main())
