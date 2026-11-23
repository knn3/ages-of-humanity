# SV-02 ship on its way: in the neighbourhood lens each ship in flight is an arrow in its people's colour on a gentle curve to its
# star, with a short fading trail; its target pulses; a lost ship leaves a fading mark where it went silent.
import asyncio, json, os, pathlib, math
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
        await ev(r'''() => { const A = window.__aoh; A.newWorld(777); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); for (const o of A.W.civs) o.era = 14; A.W.ships = []; A.W.stars = []; A.W.lost = []; scrollTo(0, 0); }''')
        # 1. one ship: its arrow follows the curve smoothly from the Sun to the star as progress goes 0 → 1
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, sh = { id: 501, civ: W.civs[0].id, star: 9, name: 'Test', t0: W.simTime, dur: 1000, crew: 1e5, y0: 3000, told: 3 }; W.ships = [sh];
          A.setZoom(.00003); const pts = []; for (let k = 0; k <= 20; k++) { sh.t0 = W.simTime - k * 50; A.render(); const s = A.V.lens.ships[0]; pts.push([s.x, s.y, s.f]); }
          const L = A.V.lens, st = L.stars.find(s => s.i === 9); return JSON.stringify({ pts, L: { x: L.x, y: L.y, r: L.r }, star: st }); }'''))
        pts, L, st = r['pts'], r['L'], r['star']
        steps = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(20)]
        d0 = math.hypot(pts[0][0] - L['x'], pts[0][1] - L['y']); d1 = math.hypot(pts[-1][0] - st['x'], pts[-1][1] - st['y'])
        check('the ship starts beside the Sun and ends on its star', d0 < 15 and d1 < 1.5, f'start {d0:.1f}px from Sun, end {d1:.1f}px from star')
        check('it moves smoothly (no jumps: every 5% step within 3× of the mean)', max(steps) < 3 * (sum(steps) / 20) and min(steps) > 0, f'{min(steps):.1f}..{max(steps):.1f}')
        dist = [math.hypot(x - L['x'], y - L['y']) for x, y, _ in pts]
        check('progress matches the voyage: further from the Sun as the voyage goes on', all(dist[i + 1] >= dist[i] - .5 for i in range(20)), str([round(d) for d in dist[::4]]))
        # off the straight line: a gentle curve
        mx, my = pts[10][0], pts[10][1]; ax, ay, bx, by = pts[0][0], pts[0][1], pts[-1][0], pts[-1][1]
        off = abs((bx - ax) * (ay - my) - (ax - mx) * (by - ay)) / math.hypot(bx - ax, by - ay); ln = math.hypot(bx - ax, by - ay)
        check('the course is a gentle curve (mid-point off the straight line by 5–25% of its length)', .05 * ln < off < .25 * ln, f'{off:.1f}px of {ln:.0f}px')
        # 2. the arrow points along the course; trail and no full course line
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, sh = W.ships[0]; sh.t0 = W.simTime - 500; A.render(); const a = A.V.lens.ships[0]; sh.t0 = W.simTime - 510; A.render(); const b = A.V.lens.ships[0];
          return JSON.stringify({ th: a.th, dir: Math.atan2(b.y - a.y, b.x - a.x) }); }'''))
        dth = abs(((r['th'] - r['dir']) + math.pi) % (2 * math.pi) - math.pi)
        check('the arrow points the way the ship is going', dth < .15, f'{dth:.3f} rad')
        # the trail: count strokes drawn in the ship's colour along the path behind it, and that nothing is drawn ahead of it
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, c = W.civs[0], cv = document.querySelector('#world'), c2 = cv.getContext('2d'); W.ships[0].t0 = W.simTime - 500; A.render(); const L = A.V.lens, s = L.ships[0];
          const segs = []; let cur = null; const mt = c2.moveTo, lt = c2.lineTo, sk = c2.stroke; c2.moveTo = function (x, y) { cur = [x, y]; return mt.call(this, x, y); }; c2.lineTo = function (x, y) { if (cur) segs.push([cur, [x, y], this.strokeStyle, this.globalAlpha]); cur = [x, y]; return lt.call(this, x, y); };
          A.render(); c2.moveTo = mt; c2.lineTo = lt; const col = c.color.toLowerCase(); const mine = segs.filter(q => String(q[2]).toLowerCase() === col && Math.hypot(q[1][0] - L.x, q[1][1] - L.y) < L.r);
          return JSON.stringify({ n: mine.length, alphas: mine.map(q => +q[3].toFixed(2)), far: Math.max(0, ...mine.map(q => Math.hypot(q[1][0] - s.x, q[1][1] - s.y))), lens: L.r }); }'''))
        print('  trail:', r)
        check('a short trail behind the ship that fades (rising alpha), not a full line to the star', r['n'] >= 6 and r['alphas'] == sorted(r['alphas']) and r['alphas'][0] < r['alphas'][-1] and r['far'] < r['lens'] * .45, str(r))
        # 3. the target star pulses while a ship is heading for it, and stops once it is not
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; A.render(); const on = A.V.lens.pulsing.slice(); W.stars = [{ star: 3, civ: W.civs[1].id, name: 'C', pop: 1e5, t0: 3000 }]; const keep = W.ships; W.ships = []; A.render(); const off = A.V.lens.pulsing.slice(); W.ships = keep; return JSON.stringify({ on, off }); }'''))
        check('the target star pulses while a ship heads for it; a settled star without one does not', r['on'] == [9] and r['off'] == [], str(r))
        # 4. a lost ship leaves a mark where it went silent, which fades and goes
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; W.stars = []; const sh = { id: 600, civ: W.civs[0].id, star: 12, name: 'Lost One', t0: W.simTime - 300, dur: 1000, crew: 1e5, y0: 3000, told: 0 }; W.ships = [sh];
          const R = Math.random; Math.random = () => .52; A.shipTick(.01); Math.random = R; const lost = (W.lost || []).slice(); A.render(); const on = A.lensOn();
          const save = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(save))); W.simTime += A.LOST_FADE + 1; A.shipTick(.01); A.render(); return JSON.stringify({ lost, on, saved: back.lost, after: (W.lost || []).length, lensAfter: A.lensOn(), chron: W.chron[0].h }); }'''))
        print('  lost:', r)
        m = r['lost'][0] if r['lost'] else {}
        check('a ship lost on the way leaves a mark at the point it went silent', len(r['lost']) == 1 and abs(m['f'] - .3) < .02 and m['star'] == 12 and 'falls silent' in r['chron'], str(r['lost']))
        check('the lens stays on to show the mark, and the mark is saved', r['on'] and r['saved'] and r['saved'][0]['star'] == 12, str(r['saved']))
        check('the mark fades away after a while (and the lens with it, when nothing else is out there)', r['after'] == 0 and not r['lensAfter'], str(r))
        # old saves without lost marks still load; garbage is cleaned
        r = json.loads(await ev(r'''() => { const A = window.__aoh, d = A.serialize(); delete d.lost; const a = A.sanitizeWorld(JSON.parse(JSON.stringify(d))); d.lost = [{ star: 99 }, null, 'x', { star: 2, f: 7, id: -3, civ: 1, t: 'q' }]; const b = A.sanitizeWorld(d); return JSON.stringify({ a: a.lost, b: b.lost }); }'''))
        check('old saves load with no lost marks; bad entries are dropped or clamped', r['a'] == [] and len(r['b']) == 1 and r['b'][0]['f'] == 1 and r['b'][0]['id'] == 0, str(r))
        # 5. several ships at once stay readable: 8 ships, incl. two to the same star at the same progress
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; W.lost = []; W.ships = []; const cs = W.civs;
          for (let i = 0; i < 8; i++) W.ships.push({ id: 700 + i, civ: cs[i % cs.length].id, star: [0, 4, 9, 9, 12, 5, 8, 13][i], name: 'S' + i, t0: W.simTime - 400, dur: 1000, crew: 1e5, y0: 3000, told: 3 });
          A.render(); const s = A.V.lens.ships; let md = 1e9; for (let i = 0; i < s.length; i++) for (let j = i + 1; j < s.length; j++) md = Math.min(md, Math.hypot(s[i].x - s[j].x, s[i].y - s[j].y)); return JSON.stringify({ n: s.length, md, same: Math.hypot(s[2].x - s[3].x, s[2].y - s[3].y) }); }'''))
        check('8 ships at once: all drawn, at least 8 px apart; two bound for the same star take different curves', r['n'] == 8 and r['md'] >= 8 and r['same'] >= 10, str(r))
        # ships launched together all start beside the Sun: still apart
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; const keep = W.ships, cs = W.civs; W.ships = [];
          for (let i = 0; i < 6; i++) W.ships.push({ id: 800 + i, civ: cs[i % cs.length].id, star: [0, 11, 4, 9, 1, 13][i], name: 'L' + i, t0: W.simTime - 15, dur: 1000, crew: 1e5, y0: 3000, told: 3 });
          A.render(); const s = A.V.lens.ships; let md = 1e9; for (let i = 0; i < s.length; i++) for (let j = i + 1; j < s.length; j++) md = Math.min(md, Math.hypot(s[i].x - s[j].x, s[i].y - s[j].y)); W.ships = keep; A.render(); return JSON.stringify({ n: s.length, md }); }'''))
        check('6 ships launched at once (all beside the Sun) are still at least 8 px apart', r['n'] == 6 and r['md'] >= 8, str(r))
        # right click still opens the ship card at its new place
        t = await ev(r'''() => { const A = window.__aoh, cv = document.querySelector('#world'), rc = cv.getBoundingClientRect(); A.render(); const q = A.V.orbPicks.find(q => q.kind === 'voyage');
          cv.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: rc.left + q.x, clientY: rc.top + q.y, button: 2 })); const t = document.querySelector('#tip'), x = t.style.display !== 'none' ? t.innerText : ''; const b = document.querySelector('#tipClose'); if (b) b.click(); return x.replace(/\n/g, ' | ').slice(0, 300); }''')
        check('right click on an arrow opens that ship', 'Of the way' in t and '40%' in t, t[:120])
        await (await pg.query_selector('#world')).screenshot(path=str(pathlib.Path(__file__).with_name('sv02.png')))
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
