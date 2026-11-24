# SV-06 settling down: a settled world's close-up shows night lights along its coasts on the dark side; there are more of them, and
# brighter, as the colony grows (log scale from a new colony to the 500 million a world can hold). They only ever switch on, never move.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

SETUP = r'''(pop) => { const A = window.__aoh; A.newWorld(313); for (let i = 0; i < 20; i++) A.step(0.1); const W = A.W; W.ships = []; W.lost = []; A.UI.paused = true;
  W.stars = [{ star: 5, civ: W.civs[0].id, name: 'Long Hope', pop, t0: 2410, sid: 50, world: 'Halcyon', log: [] }, { star: 9, civ: W.civs[1].id, name: 'Patience', pop, t0: 2500, sid: 51, world: 'Lumen', log: [] }]; scrollTo(0, 0); }'''

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        await ev(SETUP, 1e5)
        # where lights can be: on the planet, on land, on the night side; a fixed list per world, different between worlds
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, [s1, s2] = W.stars, L1 = A.worldLights(s1), L2 = A.worldLights(s2);
          return JSON.stringify({ n1: L1.length, n2: L2.length, same: JSON.stringify(L1) === JSON.stringify(A.worldLights({ ...s1 })), differ: JSON.stringify(L1.slice(0, 5)) !== JSON.stringify(L2.slice(0, 5)),
            inside: L1.every(q => Math.hypot(q.x, q.y) < .97), night: L1.every(q => A.worldNight(q.x, q.y)) }); }'''))
        check('each world has its own fixed set of light spots, all on the planet and on its night side', r['n1'] >= 200 and r['n2'] >= 200 and r['same'] and r['differ'] and r['inside'] and r['night'], str(r))
        # on land: inside one of the world's land shapes (the same ones the close-up draws), near its edge (a coast)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, st = A.W.stars[0], land = A.worldLand(st), L = A.worldLights(st);
          const inE = (q, [cx, cy, rx, ry, a], k) => { const dx = q.x - cx, dy = q.y - cy, u = dx * Math.cos(a) + dy * Math.sin(a), v = -dx * Math.sin(a) + dy * Math.cos(a); return (u / rx) ** 2 + (v / ry) ** 2 <= k * k; };
          return JSON.stringify({ tot: L.length, land: L.filter(q => land.some(e => inE(q, e, 1))).length, coast: L.filter(q => land.some(e => inE(q, e, .97) && !inE(q, e, .6))).length }); }'''))
        check('every light spot is on land, near a coast (outer part of a land shape)', r['land'] == r['tot'] and r['coast'] == r['tot'], str(r))
        # more lights and brighter as the colony grows; they only switch on (the list is a fixed order)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, st = A.W.stars[0], out = []; for (const pop of [1e3, 3e4, 1e5, 1e6, 1e7, 1e8, 5e8, 2e9]) { st.pop = pop; out.push([pop, A.worldLightCount(st), +A.worldLightK(st).toFixed(3)]); } return JSON.stringify(out); }'''))
        ns = [x[1] for x in r]; ks = [x[2] for x in r]
        check('the number of lights grows with the population (a few for a new colony, all at 500 million)', ns == sorted(ns) and 3 <= ns[1] <= 12 and ns[6] == ns[7] and ns[6] >= 200 and ns[3] < ns[5], str(r))
        check('brightness goes from 0 for the smallest colony to 1 at 500 million', ks[0] == 0 and ks[1] < .05 and ks[6] == 1 and ks == sorted(ks), str(ks))
        # drawn in the close-up: count the light dots drawn and their colour alpha, at three sizes
        DRAW = r'''async (pop) => { const A = window.__aoh, st = A.W.stars[0]; st.pop = pop; A.V.focus = null; A.shipFocus(50, true); await new Promise(r => setTimeout(r, 900));
          const c2 = document.querySelector('#world').getContext('2d'), F = A.V.focusBox, arcs = []; const arc = c2.arc, fill = c2.fill; let cur = []; c2.arc = function (x, y, rr, ...q) { cur.push([x, y, rr]); return arc.call(this, x, y, rr, ...q); };
          c2.fill = function (...q) { if (/rgba\(255,\s*226,\s*160/.test(this.fillStyle)) arcs.push({ col: String(this.fillStyle), pts: cur.slice() }); cur = []; return fill.apply(this, q); }; const bp = c2.beginPath; c2.beginPath = function () { cur = []; return bp.call(this); };
          A.render(); c2.arc = arc; c2.fill = fill; c2.beginPath = bp; const core = arcs[0] || { pts: [], col: '' }, L = A.worldLights(st), q0 = L[0], p0 = core.pts[0];
          return JSON.stringify({ n: core.pts.length, want: A.worldLightCount(st), col: core.col, at: p0 ? Math.hypot(p0[0] - (F.cx + q0.x * F.R), p0[1] - (F.cy + q0.y * F.R)) : -1 }); }'''
        got = {}
        for pop in [5e4, 3e6, 5e8]:
            got[pop] = json.loads(await ev(DRAW, pop))
        print('  drawn:', got)
        check('the close-up draws exactly that many lights, where the list says', all(g['n'] == g['want'] for g in got.values()) and all(g['at'] < .5 for g in got.values()), str({k: (v['n'], v['want'], round(v['at'], 2)) for k, v in got.items()}))
        al = [float(got[p]['col'].split(',')[-1].rstrip(')')) for p in [5e4, 3e6, 5e8]]
        check('and brighter as the colony grows', al == sorted(al) and al[0] < al[2], str(al))
        # the night side really gets brighter on screen as the colony grows (pixels, not just draw calls)
        lum = {}
        for pop in [5e4, 5e8]:
            lum[pop] = await ev(r'''async (pop) => { const A = window.__aoh, st = A.W.stars[0]; st.pop = pop; A.V.focus = null; A.shipFocus(50, true); await new Promise(r => setTimeout(r, 900)); A.render();
              const cv = document.querySelector('#world'), c2 = cv.getContext('2d'), F = A.V.focusBox, sx = cv.width / cv.clientWidth, L = A.worldLights(st); let s = 0;
              for (const q of L) { const px = Math.round((F.cx + q.x * F.R) * sx), py = Math.round((F.cy + q.y * F.R) * sx); if (px < 0 || py < 0 || px >= cv.width || py >= cv.height) continue; const d = c2.getImageData(px, py, 1, 1).data; s += d[0] + d[1] + d[2]; } return s; }''', pop)
        check('on screen, the night side glows far more at 500 million than for a new colony', lum[5e8] > 3 * lum[5e4], str(lum))
        # a colony grows in the simulation and its lights come on by themselves
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, st = W.stars[0]; st.pop = 4e4; A.UI.paused = false; const n0 = A.worldLightCount(st); for (let i = 0; i < 6000; i++) A.step(0.1); return JSON.stringify({ n0, n1: A.worldLightCount(st), pop: st.pop }); }'''))
        check('as the simulation runs, the colony grows and more lights come on', r['n1'] > r['n0'] and r['pop'] > 4e4, str(r))
        await (await pg.query_selector('#world')).screenshot(path=str(pathlib.Path(__file__).with_name('sv06.png')))
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
