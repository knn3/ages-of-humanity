# SV-07 from star to star: a large, old star colony launches a ship of its own to the nearest free star; the lens draws that voyage
# from the colony's star; it arrives as a new colony settled from the old one (not from Earth); saved and sanitised.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        # a world with no home launches (all below the Stellar Age) and one colony at Proxima Centauri (star 0)
        SETUP = r'''([pop, age]) => { const A = window.__aoh; A.newWorld(717); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); const W = A.W; for (const o of W.civs) o.era = 12; W.year = 4000; W.ships = []; W.lost = [];
          W.stars = [{ star: 0, civ: W.civs[0].id, name: 'Long Hope', pop, t0: 4000 - age, forgot: false, log: [{ y: 3000, k: 'launch', f: 0 }, { y: 4000 - age, k: 'arrive', f: 1 }], sid: 50, world: 'Halcyon' }]; scrollTo(0, 0); }'''
        TICK = r'''(roll) => { const A = window.__aoh, R = Math.random; Math.random = () => roll; A.shipTick(1); Math.random = R; return JSON.stringify(A.W.ships); }'''
        C = await ev("() => window.__aoh.COL_SHIP")
        # rules: too small, too young, chance
        await ev(SETUP, [C['COL_SHIP_POP'] * .5, 1000]); n1 = len(json.loads(await ev(TICK, 0)))
        await ev(SETUP, [C['COL_SHIP_POP'] * 2, C['COL_SHIP_AGE'] * .5]); n2 = len(json.loads(await ev(TICK, 0)))
        await ev(SETUP, [C['COL_SHIP_POP'] * 2, 1000]); n3 = len(json.loads(await ev(TICK, .999)))
        check('a small colony, a young colony and an unlucky roll send no ship', n1 == 0 and n2 == 0 and n3 == 0, f'{n1} {n2} {n3}')
        r = json.loads(await ev(TICK, 0)); sh = r[0] if r else {}
        near = await ev(r'''() => { const A = window.__aoh, X = A.XSTARS, xy = i => [X[i][1] * Math.cos(X[i][2]), X[i][1] * Math.sin(X[i][2])], [x, y] = xy(0); let b = -1, bd = 1e9; for (let j = 1; j < X.length; j++) { const [u, v] = xy(j), d = Math.hypot(u - x, v - y); if (d < bd) { bd = d; b = j; } } return [b, bd]; }''')
        check('a large, old colony launches a ship of its own', len(r) == 1 and sh.get('from') == 0 and sh.get('fromW') == 'Halcyon', str(sh)[:200])
        check('it heads for the nearest free star to the colony', sh.get('star') == near[0], f"{sh.get('star')} vs {near}")
        check('the voyage time follows the distance from the colony, not from Earth', abs(sh.get('dur', 0) - (120 + near[1] * 1400 * .5)) < 1e-6, f"{sh.get('dur')}")
        civ0 = await ev("() => window.__aoh.W.civs[0].id")
        check('the ship belongs to the colony\'s people and logs its launch', sh.get('civ') == civ0 and sh.get('log', [{}])[0].get('k') == 'launch', '')
        line = await ev(r'''() => { const A = window.__aoh, id = A.W.ships[0].id, e = A.W.hist.filter(e => e.sh === id); return e.map(x => x.h.replace(/<[^>]+>/g, '')).join(' / '); }''')
        check('the chronicle tells it, linked to the ship', 'settlers of Halcyon' in line and 'generation ship' in line, line[:200])
        lis = await ev(r'''() => { const A = window.__aoh; A.updateUI(); const li = [...document.querySelectorAll('#log li')].find(l => /settlers of Halcyon/.test(l.innerText)); return li ? li.classList.contains('shiplink') : null; }''')
        check('its chronicle line is a link', lis is True, str(lis))
        n4 = len(json.loads(await ev(TICK, 0)))
        check('one ship at a time from each colony', n4 == 1, str(n4))
        # lens: drawn from the colony's star
        async def lens(f):
            return json.loads(await ev(r'''(f) => { const A = window.__aoh, W = A.W, V = A.V, sh = W.ships[0]; sh.t0 = W.simTime - f * sh.dur; A.shipFocus(sh.id, true); A.render(); return JSON.stringify(V.lens); }''', f))
        L0 = await lens(0); L1 = await lens(.999); Lm = await lens(.5)
        o = L0.get('from') or {}; s0 = L0['ships'][0]; s1 = L1['ships'][0]; d = L0['stars'][0]
        import math
        dist = lambda a, b: math.hypot(a['x'] - b['x'], a['y'] - b['y'])
        check('the lens shows the colony\'s star as the start', o.get('i') == 0 and math.hypot(o['x'] - L0['x'], o['y'] - L0['y']) > 10, str(o))
        check('the ship sets out from beside the colony\'s star, not the Sun', dist(s0, o) < 10 and dist(s0, o) < math.hypot(s0['x'] - L0['x'], s0['y'] - L0['y']), f"{dist(s0, o):.1f}")
        check('and ends on its destination', dist(s1, d) < 3, f"{dist(s1, d):.1f}")
        inside = await ev(r'''() => { const A = window.__aoh, sh = A.W.ships[0], cv = A.shipCurve(sh.star, sh.id, sh.from); let m = 0; for (let k = 0; k <= 100; k++) { const [x, y] = cv.p(k / 100); m = Math.max(m, Math.hypot(x, y)); } return m; }''')
        check('the whole course stays inside the lens', inside < .97, f'{inside:.3f}')
        labs = Lm['labels']; names = [l['name'] for l in labs]
        ov = any(a['x'] < b['x'] + b['w'] and a['x'] + a['w'] > b['x'] and a['y'] < b['y'] + b['h'] and a['y'] + a['h'] > b['y'] for i, a in enumerate(labs) for b in labs[i + 1:])
        dn = await ev("() => [window.__aoh.XSTARS[0][0], window.__aoh.XSTARS[window.__aoh.W.ships[0].star][0]]")
        check('both stars are labelled, without overlaps', dn[0] in names and dn[1] in names and not ov, str(names))
        # every colony-to-colony pair: courses stay in the lens and start beside their colony
        allin = await ev(r'''() => { const A = window.__aoh, X = A.XSTARS, bad = []; for (let i = 0; i < X.length; i++) for (let j = 0; j < X.length; j++) { if (i === j) continue; for (const id of [3, 8]) { const cv = A.shipCurve(j, id, i); let m = 0; for (let k = 0; k <= 60; k++) { const [x, y] = cv.p(k / 60); m = Math.max(m, Math.hypot(x, y)); } const [a, b] = A.lensXY(i), [x0, y0] = cv.p(0); if (m > .97 || Math.hypot(x0 - a, y0 - b) > .05) bad.push(i + '>' + j); } } return bad; }''')
        check('every star-to-star course stays inside and starts at its colony', not allin, str(allin[:6]))
        home = await ev(r'''() => { const A = window.__aoh, cv = A.shipCurve(5, 4), cv2 = A.shipCurve(5, 4, null), [x, y] = cv.p(0); return [Math.hypot(x, y), JSON.stringify(cv.p(.5)) === JSON.stringify(cv2.p(.5))]; }''')
        check('ships from the home world still start beside the Sun', abs(home[0] - .12) < 1e-9 and home[1], str(home))
        # the card
        tip = await ev(r'''() => { const A = window.__aoh, cv = document.querySelector('#world'), rc = cv.getBoundingClientRect(); A.render(); const q = A.V.orbPicks.find(q => q.kind === 'voyage'); if (!q) return 'none';
          cv.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: rc.left + q.x, clientY: rc.top + q.y, button: 2 })); return document.querySelector('#tip').innerText; }''')
        check('its card says where it was sent from', 'Sent from: Halcyon, around Proxima Centauri' in tip, tip.replace('\n', ' | ')[:240])
        await ev("() => { const b = document.querySelector('#tipClose'); if (b) b.click(); window.__aoh.V.lensShip = null; window.__aoh.setZoom(1); }")
        # save and load mid-voyage; garbage
        r = json.loads(await ev(r'''() => { const A = window.__aoh, d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d)));
          const bad = JSON.parse(JSON.stringify(d)), bs = bad.ships[0], out = {};
          for (const [k, v] of [['str', 'x'], ['neg', -1], ['big', 99], ['frac', 1.5], ['same', bs.star], ['nul', null], ['obj', {}]]) { bs.from = v; { const q = A.sanitizeWorld(JSON.parse(JSON.stringify(bad))).ships[0]; out[k] = q.from === undefined ? 'none' : q.from; } }
          const old = JSON.parse(JSON.stringify(d)); delete old.ships[0].from; delete old.ships[0].fromW; const o2 = A.sanitizeWorld(old).ships[0];
          const nw = JSON.parse(JSON.stringify(d)); delete nw.ships[0].fromW; const n2 = A.sanitizeWorld(nw).ships[0];
          return JSON.stringify({ from: back.ships[0].from, fromW: back.ships[0].fromW, bad: out, old: [o2.from, o2.fromW], noW: n2.fromW }); }'''))
        check('a voyage between stars is saved and loaded back', r['from'] == 0 and r['fromW'] == 'Halcyon', str(r))
        check('bad origins are dropped (text, out of range, fractions, its own star)', len(r['bad']) == 7 and all(v == 'none' for v in r['bad'].values()), str(r['bad']))
        check('old saves without an origin load as ships from the home world', r['old'] == [None, None], str(r['old']))
        check('a missing colony name falls back to the star\'s name', r['noW'] == 'Proxima Centauri', str(r['noW']))
        # loss: the mark keeps its origin, and its lens starts at the colony
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, d = A.serialize(), sh = W.ships[0]; sh.t0 = W.simTime - .3 * sh.dur; sh.told = 0; const R = Math.random; Math.random = () => .53; A.shipTick(.001); Math.random = R;
          const m = W.lost.find(x => x.id === sh.id); A.shipFocus(sh.id, true); A.render(); const L = A.V.lens; const back = A.sanitizeWorld(A.serialize()).lost.find(x => x.id === sh.id);
          const out = JSON.stringify({ m: m && m.from, L: L && L.from && L.from.i, kind: L && L.kind, saved: back && back.from }); A.V.lensShip = null; A.loadWorld(d); return out; }'''))
        check('a lost ship\'s mark keeps its origin, its lens starts at the colony, and it is saved', r['m'] == 0 and r['L'] == 0 and r['kind'] == 'lost' and r['saved'] == 0, str(r))
        # arrival: a new colony settled from the old one
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, sh = W.ships[0]; if (!sh) return '{}'; sh.t0 = W.simTime - sh.dur * 1.01; sh.told = 3; A.shipTick(.001); const st = W.stars.find(x => x.sid === sh.id);
          const line = W.hist.filter(e => e.sh === sh.id).map(e => e.h.replace(/<[^>]+>/g, '')).pop(); const wl = A.worldLines(st).join(' / ');
          const back = A.sanitizeWorld(A.serialize()).stars.find(x => x.sid === sh.id); A.shipFocus(sh.id, true); const f = A.V.focus;
          return JSON.stringify({ from: st && st.from, fromW: st && st.fromW, world: st && st.world, line, wl, saved: back && [back.from, back.fromW], focus: f && f.body }); }'''))
        check('on arrival the new colony records the colony it came from', r.get('from') == 0 and r.get('fromW') == 'Halcyon' and r.get('world') and r['world'] != 'Halcyon', str(r)[:200])
        check('the chronicle says it was settled from the old colony, not from Earth', 'from Halcyon and not from Earth' in (r.get('line') or ''), r.get('line'))
        check('the world\'s close-up says where its settlers came from', 'sent from Halcyon around Proxima Centauri' in (r.get('wl') or ''), (r.get('wl') or '')[:220])
        check('the new colony\'s origin is saved; its ship lines open its world', r.get('saved') == [0, 'Halcyon'] and r.get('focus') == 'world', str(r.get('saved')))
        # no free star: no launch; a dead people's colony still sends ships
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, X = A.XSTARS; W.ships = []; W.stars = X.map((s, i) => ({ star: i, civ: W.civs[0].id, name: 'S' + i, pop: 1e8, t0: 1000, forgot: false, log: [], sid: 900 + i, world: 'W' + i }));
          const R = Math.random; Math.random = () => 0; A.shipTick(1); const full = W.ships.length; W.stars = W.stars.slice(0, 2); W.civs[0].alive = false; A.shipTick(1); Math.random = R;
          return JSON.stringify({ full, dead: W.ships.length, lines: W.hist.slice(-2).map(e => e.h.replace(/<[^>]+>/g, '')) }); }'''))
        check('with every star held, no colony sends a ship', r['full'] == 0, str(r))
        check('a colony whose homeland is gone still sends its own ships', r['dead'] >= 1, str(r['lines'])[:200])
        # natural: from the real tick with real chance
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; W.civs[0].alive = true; W.ships = []; W.stars = [W.stars[0]]; W.stars[0].pop = 1e8; let t = 0, n = 0; for (let i = 0; i < 6000; i++) { const k = W.ships.length; A.shipTick(.5); if (W.ships.length > k) n++; if (W.ships.some(s => s.from === 0)) { t = i * .5; break; } } return JSON.stringify({ t, n }); }'''))
        check('with the real chance a big colony sends a ship now and then (mean 250 sim s)', 0 < r["t"] < 2500, str(r))
        print('errors:', errs[:3] if errs else 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
