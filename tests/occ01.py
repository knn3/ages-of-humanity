# OCC-01 the landing and the seed towers: when the Hevari fleet arrives (TB-08), or from the Landing event, seed towers land on the
# richest land and grow into alien colony cities (outpost, colony, city) with their own look; chronicle, panel, right-click info,
# the globe; if the resistance wins they stand empty; saved and sanitised; old saves and a new cycle have none.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

SETUP = r'''(seed) => { const A = window.__aoh; A.newWorld(seed); A.UI.random = false; for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1);
  const W = A.W; for (const a of [...W.fates.active]) A.endFate(a.id, 'faded'); W.fates.done = []; W.fates.ended = null; W.care = null; W.wars = []; W.occ = null; W.tb = null;
  for (const c of W.civs.filter(c => c.alive)) { c.era = Math.max(c.era, 12); c.machine = false; } W.fates.lastStart = -1e9; for (const id in W.fates.p) W.fates.p[id] = 0; scrollTo(0, 0); return W.civs.filter(c => c.alive).length; }'''
# the fleet arrives the natural way: the Three-Sun Signal runs, deterrence never holds, the span passes
ARRIVE = r'''() => { const A = window.__aoh, W = A.W; A.startFate('threebody', 'event'); const T = W.tb, a = W.fates.active.find(a => a.id === 'threebody');
  T.probe = true; T.deterTried = true; T.deter = null; a.t0 = W.simTime - A.FATES.threebody.span - 1; A.tbAdvanced(a, .1); return JSON.stringify({ occ: W.occ, tbOcc: !!T.occ }); }'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        n = await ev(SETUP, 7311)
        K = await ev("() => window.__aoh.OCC")
        # where they land
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, V = A.V, xs = A.occSites(6), N = W.nat, CELL = 100;
          const fert = x => { const i = Math.floor(x / CELL); return N.s[i] * (.4 + V.cap[i]); }, land = []; for (let i = 0; i < N.s.length; i++) if (!V.seaCell[i]) land.push(N.s[i] * (.4 + V.cap[i])); land.sort((a, b) => a - b);
          const wd = (a, b) => { const d = Math.abs(a - b) % 12000; return Math.min(d, 12000 - d); }; let gap = 1e9; for (const a of xs) for (const b of xs) if (a !== b) gap = Math.min(gap, wd(a, b));
          return JSON.stringify({ n: xs.length, gap, land: xs.every(x => A.isLand(x)), cap: Math.min(...xs.map(x => Math.min(...W.civs.filter(c => c.alive).map(c => wd(c.x, x))))), fert: xs.map(fert), median: land[land.length >> 1] }); }'''))
        check('seed towers go to the richest land: spaced apart, on land, clear of every capital, far above the median soil', r['n'] >= 3 and r['gap'] >= K['OCC_GAP'] and r['land'] and r['cap'] >= 140 and min(r['fert']) > r['median'], str(r))
        r = json.loads(await ev(ARRIVE))
        o = r['occ']
        check('the fleet arriving plants seed towers (3 to 6, by the number of peoples), named, growing, from TB-08', r['tbOcc'] and o and o['src'] == 'tb' and 3 <= len(o['towers']) <= K['OCC_MAX'] and len(o['towers']) == min(K['OCC_MAX'], max(3, 3 + n // 2)) and all(t['g'] == 0 and t['state'] == 'grow' and t['name'] for t in o['towers']) and len({t['name'] for t in o['towers']}) == len(o['towers']), f"n={n} towers={len(o['towers']) if o else 0}")
        lines = await ev(r'''() => window.__aoh.W.hist.filter(e => /plant \d+ seed towers|seed towers? rises?/.test(e.h)).map(e => e.h.replace(/<[^>]+>/g, '').slice(0, 90))''')
        check('the landing is told, and each people with a tower on its land hears of it', len(lines) >= 2 and 'plant' in lines[0], ' | '.join(lines)[:220])
        # growth: seed tower, outpost, colony, colony city
        r = json.loads(await ev(r'''(G) => { const A = window.__aoh, W = A.W, t = W.occ.towers[0], seen = []; for (let i = 0; i < G * 1.1; i++) { A.occTick(1); const s = A.occStage(t); if (seen[seen.length - 1] !== s) seen.push(s); }
          const h = W.hist.map(e => e.h); return JSON.stringify({ seen, g: W.occ.towers.map(t => t.g), out: h.filter(x => /splits into an outpost/.test(x)).length, col: h.filter(x => /is a Hevari colony now/.test(x)).length, city: h.filter(x => /grown into a colony city/.test(x)).length, pop: A.occPop(t), pop0: A.occPop({ g: .05, state: 'grow' }), nt: W.occ.towers.length }); }''', K['OCC_GROW']))
        check('each tower grows through the four stages in order and reaches a full city in about OCC_GROW sim seconds', r['seen'] == [0, 1, 2, 3] and all(g == 1 for g in r['g']), str(r['seen']))
        check('the first outpost and the first colony are told once; every colony city is told', r['out'] == 1 and r['col'] == 1 and r['city'] == r['nt'], str(r))
        check('colonists grow with the colony', r['pop'] > 50 * r['pop0'] and r['pop'] > 5e6, f"{r['pop0']} -> {r['pop']}")
        # on screen: picks grow with the colony
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, V = A.V, t = W.occ.towers[0]; V.focus = null; A.setZoom(1.4); V.cam = t.x - V.vw / 2; V.camY = null; V.dayT = .5;
          const at = g => { t.g = g; A.render(); const ps = V.picks.filter(p => p.kind === 'occtower' && p.d.t === t); return { n: ps.length, top: ps.length ? Math.min(...ps.map(p => p.y0)) : 0, w: ps.length ? Math.max(...ps.map(p => p.x1)) - Math.min(...ps.map(p => p.x0)) : 0, craft: V.picks.filter(p => p.kind === 'occcraft' && p.d.t === t).length }; };
          const a = at(.1), m = at(.6), z = at(1); return JSON.stringify({ a, m, z, gy: A.gy(t.x) }); }'''))
        a, m, z = r['a'], r['m'], r['z']
        check('on the strip: one spire at first; more spires, domes and craft as it grows; taller and wider', a['n'] == 1 and a['craft'] == 0 and m['n'] > a['n'] and z['n'] > m['n'] and z['craft'] == 3 and z['w'] > a['w'] + 100 and (r['gy'] - z['top']) > 2 * (r['gy'] - a['top']), str(r))
        px = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, V = A.V, t = W.occ.towers[0], cv = document.querySelector('#world'), k = cv.width / cv.clientWidth, c2 = cv.getContext('2d');
          const cnt = g => { if (W.occ) W.occ.towers.forEach(q => q.g = g); A.render(); const [sx] = A.W2S(t.x, 0), [, sy0] = A.W2S(t.x, A.gy(t.x) - 230), [, sy1] = A.W2S(t.x, A.gy(t.x)); const x0 = Math.max(0, Math.round((sx - 120) * k)), y0 = Math.max(0, Math.round(sy0 * k));
            const d = c2.getImageData(x0, y0, Math.round(240 * k), Math.max(1, Math.round((sy1 - sy0) * k))).data; let n = 0; for (let i = 0; i < d.length; i += 4) if (d[i] > 190 && d[i + 2] > 205 && d[i + 2] >= d[i + 1] + 6) n++; return n; };
          const on = cnt(1); const save = W.occ; W.occ = null; const off = cnt(0); W.occ = save; cnt(1); return JSON.stringify({ on, off }); }'''))
        check('the colony city shows on screen in pale violet-white (pixels)', px['on'] > 600 and px['on'] > 5 * (px['off'] + 1), str(px))
        tip = await ev(r'''() => { const A = window.__aoh, V = A.V, t = A.W.occ.towers[0]; A.render(); const q = V.picks.find(p => p.kind === 'occtower' && p.d.t === t && p.x1 - p.x0 > 20), cv = document.querySelector('#world'), rc = cv.getBoundingClientRect(), [sx, sy] = A.W2S((q.x0 + q.x1) / 2, q.y0 + (q.y1 - q.y0) * .6);
          cv.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: rc.left + sx, clientY: rc.top + sy, button: 2 })); const el = document.querySelector('#tip'); return el.style.display !== 'none' ? el.innerText : 'hidden'; }''')
        check('right-clicking a colony tells its name, stage, colonists, landing year and land', 'Colony city' in tip and 'Hevari colonists' in tip and 'Landed' in tip and 'three suns' in tip, tip.replace('\n', ' | ')[:220])
        await ev("() => { const b = document.querySelector('#tipClose'); if (b) b.click(); }")
        tip2 = await ev(r'''() => { const A = window.__aoh, V = A.V; A.render(); const q = V.picks.find(p => p.kind === 'occcraft'); return q ? A.tipBody({ p: q }).join(' ').replace(/<[^>]+>/g, ' ') : 'none'; }''')
        check('a Hevari craft has its own info', 'Hevari craft' in tip2 and 'Serves' in tip2, tip2[:120])
        # the globe
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, t = W.occ.towers[0], T = A.TEX; A.buildTex(); const c = Math.round(t.x / 12000 * T.tw); let idx = -1; for (let r = 0; r < 6; r++) if (T.land[r * T.tw + c]) { idx = r * T.tw + c; break; }
          A.buildTex(); const on = [T.col[idx * 3], T.col[idx * 3 + 1], T.col[idx * 3 + 2]], L1 = T.lgt[idx]; const s = W.occ; W.occ = null; A.buildTex(); const off = [T.col[idx * 3], T.col[idx * 3 + 1], T.col[idx * 3 + 2]], L0 = T.lgt[idx]; W.occ = s; A.buildTex(); return JSON.stringify({ idx, on, off, L0, L1 }); }'''))
        on, off = r['on'], r['off']
        check('on the globe a colony is a pale violet patch with lights of its own', r['idx'] >= 0 and on[2] > off[2] + 30 and on[2] > on[1] and r['L1'] > r['L0'], str(r))
        clock = await ev("() => { const A = window.__aoh; A.updateUI(); return document.querySelector('#futures').innerText; }")
        check('the Futures panel counts the Hevari colonies', 'Hevari colonies' in clock, clock.replace('\n', ' | ')[:180])
        # the resistance wins: the colonies stand empty
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, T = W.tb, a = W.fates.active.find(a => a.id === 'threebody'); W.occ.towers.forEach(t => t.g = .5); T.occ.res = 1e6; T.occ.t0 = W.simTime - 121; A.tbAdvanced(a, .1);
          const g0 = W.occ.towers.map(t => t.g); for (let i = 0; i < 20; i++) A.occTick(1); A.render(); const q = A.V.picks.find(p => p.kind === 'occtower'), tb = q ? A.tipBody({ p: q })[1].replace(/<[^>]+>/g, ' ') : '';
          return JSON.stringify({ st: W.occ.towers.map(t => t.state), same: W.occ.towers.every((t, i) => t.g === g0[i]), told: W.hist.filter(e => /leave their colonies behind/.test(e.h)).length, tb: !!W.tb, live: A.occLive(), craft: A.V.picks.filter(p => p.kind === 'occcraft').length, tip: tb }); }'''))
        check('if the resistance wins, the colonies stand empty: no growth, no craft, told once, info says so', all(s == 'empty' for s in r['st']) and r['same'] and r['told'] == 1 and not r['tb'] and not r['live'] and r['craft'] == 0 and 'left behind' in r['tip'], str({k: r[k] for k in r if k != 'tip'}))
        # the occupation ending keeps them
        n2 = await ev(SETUP, 7311)
        r = json.loads(await ev(ARRIVE))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, T = W.tb, a = W.fates.active.find(a => a.id === 'threebody'); T.occ.res = 0; T.occ.foe = 1e9; T.occ.t0 = W.simTime - 121; A.tbAdvanced(a, .1); return JSON.stringify({ ended: W.fates.ended, live: A.occLive() }); }'''))
        check('if the occupation holds (The Reservation), the colonies stay and keep growing', r['ended'] == 'occupation' and r['live'], str(r))
        # the Landing event
        await ev(SETUP, 8123)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, ev = A.findEvent('landing'), ok = A.applyEvent(ev, null), again = A.applyEvent(ev, null);
          return JSON.stringify({ ok, again, tb: !!(W.tb && W.tb.occ), active: W.fates.active.map(a => a.id), src: W.occ && W.occ.src, n: W.occ ? W.occ.towers.length : 0, line: W.hist.some(e => /drops out of the dark centuries/.test(e.h)), info: A.infoContent('ev:landing') ? A.infoContent('ev:landing')[1].replace(/<[^>]+>/g, ' ').slice(0, 120) : '' }); }'''))
        check('the Landing event starts the Three-Sun Signal at the fleet’s arrival and plants the towers; not twice', r['ok'] and not r['again'] and r['tb'] and 'threebody' in r['active'] and r['src'] == 'event' and r['n'] >= 3 and r['line'], str(r))
        check('the Landing event has an info text and sits in the Futures tab', 'seed towers' in r['info'] and await ev("() => window.__aoh.findEvent('landing').cat === 'Futures'"), r['info'])
        # natural growth through the real step
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, g0 = W.occ.towers[0].g; for (let i = 0; i < 300; i++) { W.wars = []; A.step(.1); } return JSON.stringify({ g0, g1: W.occ.towers[0].g }); }'''))
        check('the towers grow in the running simulation', r['g1'] > r['g0'] + .15, str(r))
        # saving
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; const d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d)));
          const bad = JSON.parse(JSON.stringify(d)); bad.occ = { towers: [{ x: 99999, g: 7, name: '<b>x</b>'.repeat(9), state: 'zz', s: -4 }, 5, { y: 2 }], src: 'q', said: 99 }; const b2 = A.sanitizeWorld(bad);
          const b3 = A.sanitizeWorld(Object.assign(JSON.parse(JSON.stringify(d)), { occ: 7 })), b4 = A.sanitizeWorld(Object.assign(JSON.parse(JSON.stringify(d)), { occ: { towers: [] } }));
          const old = JSON.parse(JSON.stringify(d)); delete old.occ; const o2 = A.sanitizeWorld(old); A.loadWorld(d); const loaded = JSON.parse(JSON.stringify(A.W.occ)); A.W.fates.ended = 'collapse'; A.riseAgain();
          return JSON.stringify({ same: JSON.stringify(back.occ) === JSON.stringify(d.occ), loaded: JSON.stringify(loaded) === JSON.stringify(d.occ), bad: b2.occ, b3: b3.occ, b4: b4.occ, old: o2.occ, cycle: A.W.occ }); }'''))
        bt = r['bad']['towers'] if r['bad'] else []
        check('the colonies are saved and loaded back exactly', r['same'] and r['loaded'], str(r)[:160])
        check('bad values are dropped or clamped; old saves have none; a new cycle starts without them', len(bt) == 1 and bt[0]['x'] == 11999 and bt[0]['g'] == 1 and bt[0]['state'] == 'grow' and len(bt[0]['name']) <= 24 and r['bad']['src'] == 'tb' and r['bad']['said'] == 15 and r['b3'] is None and r['b4'] is None and r['old'] is None and r['cycle'] is None, str(r['bad'])[:200])
        print('errors:', errs[:3] if errs else 'no errors'); results.append(not errs)
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
