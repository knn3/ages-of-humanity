# "Real data" runs for the End of the world epic: natural worlds (nothing forced) run for SECONDS of sim time,
# through endings and new cycles, counting every tipping point, nuclear winter, engineered plague, ending, cycle and ruin.
# usage: python endnat.py [N=12] [SECONDS=3000]
import asyncio, json, sys
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
SEC = float(sys.argv[2]) if len(sys.argv) > 2 else 3000
RUN = r'''([seed, sec]) => { const A = window.__aoh; A.newWorld(seed); const W = () => A.W;
  const o = { tips: 0, maxSea: 0, winters: 0, fullWinters: 0, plagues: 0, endings: [], cycles: 1, maxRuins: 0, scav: 0, bunkers: 0, deadWorld: false, maxTemp: 0, climateEv: 0, nukes: 0, supervolcanoes: 0, asteroids: 0, deflected: 0, impacts: 0, unseen: 0, libs: 0, vaults: 0, starts: [] };
  let hot = false, win = null, pd = null, ended = null, nk = null, rock = null;
  for (let i = 0; i < sec * 10; i++) { A.step(0.1); const w = W();
    if (w.hot.on && !hot) o.tips++; hot = w.hot.on; o.maxSea = Math.max(o.maxSea, w.seaRise); o.maxTemp = Math.max(o.maxTemp, A.temp());
    if (w.winter && w.winter !== win) { if (w.winter.kind === 'ash') o.supervolcanoes++; else if (w.winter.kind !== 'impact') { o.winters++; if (w.winter.full) o.fullWinters++; } } win = w.winter;
    if (w.rock && w.rock !== rock) { o.asteroids++; if (!w.rock.seen) o.unseen++; } if (!w.rock && rock) { if (w.chron.some(e => e.h.includes('will miss the world') && e.h.includes(rock.name))) o.deflected++; else o.impacts++; } rock = w.rock;
    if (w.pandemic && w.pandemic !== pd) o.plagues++; pd = w.pandemic;
    if (w.nukeT != null && w.nukeT !== nk) o.nukes++; nk = w.nukeT;
    if (w.fates.ended && w.fates.ended !== ended) o.endings.push(w.fates.ended + '@c' + w.fates.cycle); ended = w.fates.ended;
    if (w.fates.cycle > o.cycles) o.starts.push(w.civs.filter(c => c.alive).map(c => c.era).join('')); o.libs = Math.max(o.libs, w.elements.filter(e => e.type === 'library').length); o.vaults = Math.max(o.vaults, w.elements.filter(e => e.type === 'seedvault').length);
    o.cycles = w.fates.cycle; o.maxRuins = Math.max(o.maxRuins, (w.ruins || []).length);
    o.bunkers = Math.max(o.bunkers, w.civs.filter(c => c.alive && c.bunker >= .5).length); if (w.civs.some(c => c.alive && c._.scav)) o.scav = 1;
    if (!w.civs.some(c => c.alive)) { o.deadWorld = true; break; }
    if (ended && !w.fates.riseAt && !['doom'].includes(A.ENDINGS[ended].kind)) break; }
  o.climateEv = W().chron.filter(e => /Ice caps melt|climate begins to warm/.test(e.h)).length;
  o.t = Math.round(W().simTime); o.top = Math.max(0, ...W().civs.filter(c => c.alive).map(c => c.era)); o.maxSea = +o.maxSea.toFixed(1); o.maxTemp = +o.maxTemp.toFixed(1);
  const s1 = A.serialize(); let saveOk = true; try { A.loadWorld(JSON.parse(JSON.stringify(s1))); for (let i = 0; i < 20; i++) A.step(0.1); A.render(); } catch (e) { saveOk = String(e); } o.saveOk = saveOk;
  return JSON.stringify(o); }'''
async def worker(b, seeds, out, errs):
    pg = await b.new_page(viewport={'width': 1300, 'height': 850})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(GAME); await pg.wait_for_timeout(600); await pg.keyboard.press('Space')
    for s in seeds: out.append((s, json.loads(await pg.evaluate(RUN, [s, SEC]))))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH); out = []; errs = []
        seeds = [7000 + 53 * i for i in range(N)]
        await asyncio.gather(*[worker(b, seeds[k::6], out, errs) for k in range(min(6, N))])
        await b.close()
    out.sort()
    for s, o in out: print(f'seed {s}:', json.dumps(o))
    tot = lambda k: sum(1 for _, o in out if o[k])
    print(f"\nworlds {len(out)} | tipped {tot('tips')} | seas rose >10px {sum(1 for _, o in out if o['maxSea'] > 10)} | nuclear wars {sum(o['nukes'] for _, o in out)} | full winters {sum(o['fullWinters'] for _, o in out)} | bunkers dug {tot('bunkers')} | supervolcanoes {sum(o['supervolcanoes'] for _, o in out)} | asteroids {sum(o['asteroids'] for _, o in out)} (deflected {sum(o['deflected'] for _, o in out)}, struck {sum(o['impacts'] for _, o in out)}, unseen at first {sum(o['unseen'] for _, o in out)})"
          f" | plagues {sum(o['plagues'] for _, o in out)} | worlds with a 2nd cycle {sum(1 for _, o in out if o['cycles'] > 1)} | ruins {tot('maxRuins')} | scavenged {tot('scav')} | dead worlds {tot('deadWorld')} | save ok {sum(1 for _, o in out if o['saveOk'] is True)}")
    ends = {}
    for _, o in out:
        for e in o['endings']: k = e.split('@')[0]; ends[k] = ends.get(k, 0) + 1
    print('endings:', ends)
    st = [x for _, o in out for x in o['starts']]
    print(f"libraries built {sum(o['libs'] for _, o in out)} | seed vaults built {sum(o['vaults'] for _, o in out)} | new cycles {len(st)} | starting ages per cycle (one digit per people): {st} | cycles where someone started past the Stone Age {sum(1 for x in st if any(int(ch) > 1 for ch in x))}")
    print('\n'.join(errs[:5]) or 'no errors')
asyncio.run(main())
