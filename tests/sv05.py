# SV-05 events marked on the path: in a ship's lens, each mutiny, plague and forgetting is marked where on the course it happened,
# with its year; a lost ship's lens marks where it went silent. Old logs without positions get them from the order of events.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))
def overl(a, b, m=0):
    return a['x'] - m < b['x'] + b['w'] and a['x'] + a['w'] + m > b['x'] and a['y'] - m < b['y'] + b['h'] and a['y'] + a['h'] + m > b['y']

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        # a real launch, then the real event code at each quarter of the way: mutiny, plague, forgetting
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(313); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); const W = A.W; W.year = 2400; for (const o of W.civs) o.era = 12; W.civs[0].era = 13; W.ships = []; W.stars = []; W.lost = [];
          const R = Math.random; Math.random = () => 0; A.shipTick(1); Math.random = R; const sh = W.ships[0];
          for (const [q, roll] of [[.26, .1], [.51, .3], [.76, .45]]) { sh.t0 = W.simTime - q * sh.dur; W.year += 30; Math.random = () => roll; A.shipTick(.001); Math.random = R; }
          sh.t0 = W.simTime - .9 * sh.dur; scrollTo(0, 0); A.shipFocus(sh.id, true); A.render();
          const L = A.V.lens, cv = A.shipCurve(sh.star, sh.id), at = f => { const [u, v] = cv.p(f); return [L.x + u * L.r, L.y + v * L.r]; };
          return JSON.stringify({ log: sh.log, L: { x: L.x, y: L.y, r: L.r }, marks: L.marks, want: L.marks.map(m => at(m.f)), labels: L.labels, ships: L.ships, star: L.stars[0], w: document.querySelector('#world').clientWidth, h: document.querySelector('#world').clientHeight }); }'''))
        lg = r['log']
        check('each event is logged with where on the voyage it happened (0 = launch, quarters for events)', [e['k'] for e in lg] == ['launch', 'mutiny', 'plague', 'forgot'] and lg[0]['f'] == 0 and all(abs(e['f'] - q) < .02 for e, q in zip(lg[1:], [.26, .51, .76])), str(lg))
        mk = r['marks']
        check('the lens marks mutiny, plague and forgetting', [m['k'] for m in mk] == ['mutiny', 'plague', 'forgot'], str([m['k'] for m in mk]))
        off = max(((m['x'] - w[0]) ** 2 + (m['y'] - w[1]) ** 2) ** .5 for m, w in zip(mk, r['want']))
        check('each mark sits on the ship\'s course at the point it happened', off < .5, f'{off:.2f}px')
        dS = [((m['x'] - r['L']['x']) ** 2 + (m['y'] - r['L']['y']) ** 2) ** .5 for m in mk]; sh = r['ships'][0]
        check('marks run in order from the Sun, behind the ship', dS == sorted(dS) and dS[-1] < ((sh['x'] - r['L']['x']) ** 2 + (sh['y'] - r['L']['y']) ** 2) ** .5, str([round(d) for d in dS]))
        labs = r['labels']; names = [l['name'] for l in labs]; yrs = [e['y'] for e in lg[1:]]
        check('each mark is labelled with its event and year', all(any(n.startswith(t) and f'{y} CE' in n for n in names) for t, y in zip(['Mutiny', 'Plague', 'Forgotten'], yrs)), str(names))
        dots = [{'x': d[0] - 4, 'y': d[1] - 4, 'w': 8, 'h': 8} for d in [(r['L']['x'], r['L']['y']), (r['star']['x'], r['star']['y']), (sh['x'], sh['y'])] + [(m['x'], m['y']) for m in mk]]
        lo = [(a['name'], c['name']) for i, a in enumerate(labs) for c in labs[i + 1:] if overl(a, c)]; ld = [a['name'] for a in labs for d in dots if overl(a, d)]
        check('labels overlap no other label, mark, star, the Sun or the ship', not lo and not ld, str([lo, ld]))
        check('labels stay on screen', all(l['x'] >= 0 and l['y'] >= 0 and l['x'] + l['w'] <= r['w'] and l['y'] + l['h'] <= r['h'] for l in labs), str(labs))
        # draws: the three glyph shapes (diamond = 4 lineTo, dots = arcs) in the event colours
        cols = json.loads(await ev(r'''() => { const A = window.__aoh, c2 = document.querySelector('#world').getContext('2d'), got = new Set(); const fl = c2.fill; c2.fill = function (...a) { got.add(String(this.fillStyle).toLowerCase()); return fl.apply(this, a); }; A.render(); c2.fill = fl; return JSON.stringify([...got]); }'''))
        check('marks are drawn in their own colours (mutiny red, plague green)', '#e0664f' in cols and '#9bc45a' in cols, str(cols))
        # a lost ship: its marks before the place it went silent, labelled
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, sh = { id: 6200, civ: W.civs[0].id, star: 9, name: 'Lantern', t0: 0, dur: 1000, crew: 1e5, crew0: 1e5, y0: 2450, told: 0, log: [{ y: 2450, k: 'launch', f: 0 }] }; W.ships.push(sh); sh.t0 = W.simTime - .3 * sh.dur; const R = Math.random; Math.random = () => .1; A.shipTick(.001); sh.t0 = W.simTime - .55 * sh.dur; Math.random = () => .53; A.shipTick(.001); Math.random = R;
          const m = W.lost[W.lost.length - 1]; A.shipFocus(m.id, true); A.render(); const L = A.V.lens; return JSON.stringify({ kind: L.kind, marks: L.marks.map(x => [x.k, x.f]), labels: L.labels.map(l => l.name), lostF: m.f, log: m.log.map(e => [e.k, e.f]) }); }'''))
        check('a lost ship\'s lens shows its marks and where it went silent, labelled with the year', r['kind'] == 'lost' and any(k == 'mutiny' for k, _ in r['marks']) and any(n.startswith('Silent · ') and 'CE' in n for n in r['labels']) and max(f for _, f in r['marks']) <= r['lostF'] + 1e-6, str(r))
        await ev("() => { window.__aoh.V.lensShip = null; }")
        # a ship with nothing on the way yet: no marks
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; W.ships.push({ id: 6100, civ: W.civs[1].id, star: 4, name: 'Quiet', t0: W.simTime - 100, dur: 1000, crew: 1e5, crew0: 1e5, y0: 2500, told: 0, log: [{ y: 2500, k: 'launch', f: 0 }] }); A.shipFocus(6100, true); A.render(); return JSON.stringify({ marks: A.V.lens.marks.length, labels: A.V.lens.labels.map(l => l.name) }); }'''))
        check('a ship with nothing on the way yet has no marks, only its destination', r['marks'] == 0 and r['labels'] == ['Epsilon Eridani'], str(r))
        # saves: positions are kept; old logs without them get them from the order of events; bad values are clamped
        r = json.loads(await ev(r'''() => { const A = window.__aoh, d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d)));
          const old = JSON.parse(JSON.stringify(d)); old.ships = [{ id: 1, civ: 1, star: 3, name: 'Old', t0: 0, dur: 500, crew: 1, y0: 2000, told: 3, log: [{ y: 2000, k: 'launch' }, { y: 2050, k: 'plague' }, { y: 2100, k: 'mutiny' }, { y: 2150, k: 'forgot' }] }];
          old.stars = [{ star: 2, civ: 1, name: 'S', pop: 1, t0: 2200, sid: 1, world: 'X', log: [{ y: 2000, k: 'launch' }, { y: 2100, k: 'mutiny', f: 7 }, { y: 2200, k: 'arrive' }] }]; const o = A.sanitizeWorld(old);
          return JSON.stringify({ same: JSON.stringify(back.lost.map(m => m.log)) === JSON.stringify(A.W.lost.map(m => m.log)), oldShip: o.ships[0].log.map(e => [e.k, e.f]), oldStar: o.stars[0].log.map(e => [e.k, e.f]) }); }'''))
        check('positions are saved and loaded unchanged', r['same'], str(r))
        check('old logs get positions from the order of events (launch 0, then each quarter)', r['oldShip'] == [['launch', 0], ['plague', .26], ['mutiny', .51], ['forgot', .76]], str(r['oldShip']))
        check('bad positions are clamped; arrival is at the end', r['oldStar'] == [['launch', 0], ['mutiny', 1], ['arrive', 1]], str(r['oldStar']))
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
