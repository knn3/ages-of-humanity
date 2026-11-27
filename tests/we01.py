# WE-01 the dying Sun: the Sun swells and reddens on the Dying Sun future's countdown (started by its event, by pressure, or for
# certain by a far-future date); sky colour and temperature follow; seen from the ground, the globe, the solar system and its close-up.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

PIX = r'''([x, y]) => { const cv = document.querySelector('#world'), k = cv.width / cv.clientWidth, d = cv.getContext('2d').getImageData(Math.round(x * k), Math.round(y * k), 1, 1).data; return [d[0], d[1], d[2]]; }'''
# the reddest pixel over a disc (clouds drift across the Sun: white is never the reddest)
SUNPX = r'''([x, y, R]) => { const cv = document.querySelector('#world'), k = cv.width / cv.clientWidth, c2 = cv.getContext('2d'); let best = null;
  for (let i = 0; i < 40; i++) { const a = i * 2.4, r = R * .7 * Math.sqrt(i / 40), d = c2.getImageData(Math.round((x + r * Math.cos(a)) * k), Math.round((y + r * Math.sin(a)) * k), 1, 1).data; if (!best || d[0] - d[2] > best[0] - best[2]) best = [d[0], d[1], d[2]]; } return best; }'''
# the sky colour: the median of points along the top of the view (a cloud may cover a few)
SKYPX = r'''() => { const cv = document.querySelector('#world'), k = cv.width / cv.clientWidth, c2 = cv.getContext('2d'), out = [];
  for (let i = 0; i < 25; i++) { const d = c2.getImageData(Math.round(cv.clientWidth * (.04 + .92 * i / 24) * k), Math.round(5 * k), 1, 1).data; out.push([d[0], d[1], d[2]]); }
  const med = j => out.map(p => p[j]).sort((a, b) => a - b)[12]; return [med(0), med(1), med(2)]; }'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        # a world just past the edge of space, nothing random, no futures under way
        await ev(r'''() => { const A = window.__aoh; A.newWorld(4242); A.UI.random = false; for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1);
          const W = A.W; for (const a of [...W.fates.active]) A.endFate(a.id, 'faded'); W.fates.done = []; W.pollution = 0; W.tempShift = 0; W.hot = { on: false, acc: 0, t0: 0, nextMig: 0 }; W.seaRise = 0; W.sun = { k: 0, said: 0 }; W.fates.lastStart = -1e9; for (const id in W.fates.p) W.fates.p[id] = 0; scrollTo(0, 0); }''')
        r = json.loads(await ev("() => { const A = window.__aoh; return JSON.stringify({ k: A.sunK(), t: A.temp(), gh: A.tempGH() }); }"))
        check('before: the Sun is as it always was', r['k'] == 0 and abs(r['t'] - r['gh']) < 1e-9, str(r))
        # ground view by day: sample the Sun and the sky before
        GROUND = r'''() => { const A = window.__aoh, V = A.V; V.focus = null; A.setZoom(1.2); V.dayT = .5; A.render(); return JSON.stringify({ sun: V.flatSun, w: document.querySelector('#world').clientWidth }); }'''
        g0 = json.loads(await ev(GROUND)); s0 = await ev(SUNPX, g0['sun']); k0 = await ev(SKYPX)
        # the event starts the future; the Sun grows through its countdown
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, e = A.EVENTS.find(e => e.id === 'f_wandering'); A.applyEvent(e, W.civs[0].x); return JSON.stringify({ on: W.fates.active.map(a => a.id), ev: e.name }); }'''))
        check('the Sun Swells event starts the Dying Sun', 'wandering' in r['on'], str(r))
        span = await ev("() => window.__aoh.FATES.wandering.span")
        prog = json.loads(await ev(r'''(span) => { const A = window.__aoh, W = A.W, out = []; for (let i = 0; i < span; i++) { A.step(1); if (i % Math.round(span / 4) === Math.round(span / 4) - 1) out.push([+A.sunK().toFixed(3), +A.temp().toFixed(2), +A.tempGH().toFixed(2)]); } return JSON.stringify(out); }''', int(span * .5)))
        check('it swells steadily through the countdown (in step with the countdown)', len(prog) >= 2 and all(prog[i][0] < prog[i + 1][0] for i in range(len(prog) - 1)) and abs(prog[-1][0] - .375) < .03, str(prog))
        check('its heat raises the temperature, on top of the greenhouse', all(t - gh > 0 for _, t, gh in prog) and prog[-1][1] - prog[-1][2] > prog[0][1] - prog[0][2], str(prog))
        clock = await ev(r'''() => { const A = window.__aoh; A.updateUI(); return document.querySelector('#futures') ? document.querySelector('#futures').innerText : ''; }''')
        check('the Futures panel shows how wide the Sun has grown, and the verdict', 'of its old width' in clock and 'verdict in' in clock, clock.replace('\n', ' | ')[:200])
        r = json.loads(await ev(r'''(span) => { const A = window.__aoh, W = A.W; for (let i = 0; i < span * .55; i++) { W.fates.active.forEach(a => { if (a.id === 'wandering') a.t0 = Math.min(a.t0, W.simTime); }); A.step(1); if (!W.fates.active.some(a => a.id === 'wandering')) break; }
          const lines = W.hist.filter(e => e.k === 'nature' && /Sun/.test(e.h)).map(e => e.h); return JSON.stringify({ k: A.sunK(), heat: A.sunHeat(), hot: !!(W.hot && W.hot.on), lines, said: W.sun.said, banner: document.querySelector('#banner') ? document.querySelector('#banner').innerText : '' }); }''', span))
        check('by the verdict the Sun is fully swollen', r['k'] > .97, str(r['k']))
        check('four chronicle lines tell its swelling, in order, once each', r['said'] == 15 and len(r['lines']) == 4 and 'wider and a little redder' in r['lines'][0] and 'red disc' in r['lines'][3], str(r['lines'])[:300])
        check('the Sun\'s heat does not trip the greenhouse runaway by itself', not r['hot'] and r['heat'] > 2, str(r))
        # ground view after: bigger, redder Sun; amber sky
        await ev("() => { const W = window.__aoh.W; W.sun.k = 1; }")
        g1 = json.loads(await ev(GROUND)); s1 = await ev(SUNPX, g1['sun']); k1 = await ev(SKYPX)
        check('from the ground the Sun is over three times as wide', g1['sun'][2] > 3 * g0['sun'][2], f"{g0['sun'][2]} -> {g1['sun'][2]}")
        check('and red, not pale gold (the reddest spot of its disc)', s1[0] > 230 and s1[0] - s1[2] > s0[0] - s0[2] + 60, f'{s0} -> {s1}')
        check('the daytime sky turns from blue to amber', k1[0] > k0[0] + 30 and k1[2] < k0[2] - 20, f'{k0} -> {k1}')
        # from space: the globe and the solar system
        async def space(z, k):
            return json.loads(await ev(r'''([z, k]) => { const A = window.__aoh, V = A.V; A.W.sun.k = k; A.setZoom(z); A.render(); const cv = document.querySelector('#world'), kk = cv.width / cv.clientWidth, [x, y] = V.sunXY || [-99, -99], g = cv.getContext('2d').getImageData(Math.round((x - 6) * kk), Math.round((y - 6) * kk), Math.round(12 * kk), Math.round(12 * kk)).data, px = [0, 0, 0]; let n = 0; for (let i = 0; i < g.length; i += 4) { px[0] += g[i]; px[1] += g[i + 1]; px[2] += g[i + 2]; n++; } return JSON.stringify({ r: V.spaceSunR, xy: V.sunXY, on: x > 0 && y > 0 && x < cv.clientWidth && y < cv.clientHeight, px: px.map(v => Math.round(v / Math.max(1, n))) }); }''', [z, k]))
        out = {}
        a, c = await space(.05, 0), await space(.05, 1)
        check('from the globe view the Sun (beyond the edge of the view) is drawn bigger', c['r'] > 2 * a['r'], f"{a['r']:.1f} -> {c['r']:.1f}")
        a, c = await space(.0016, 0), await space(.0016, 1)
        check('from the solar system the Sun is bigger and redder', a['on'] and c['r'] > 2 * a['r'] and c['px'][2] < a['px'][2] - 50, f"{a['r']:.1f}/{a['px']} -> {c['r']:.1f}/{c['px']}")
        # the close-up says so
        r = await ev(r'''() => { const A = window.__aoh; A.W.sun.k = .8; return A.bodyLines('Sun').join(' / '); }''')
        check('the Sun\'s close-up tells how far it has swollen and how much it warms the Earth', 'dying' in r and '2.8 times' in r and '°C' in r, r[:200])
        # fading: the future ends quietly, the Sun settles back
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; A.endFate('wandering', 'faded'); const k0 = A.sunK(); for (let i = 0; i < 80; i++) A.step(1); const k1 = A.sunK(); for (let i = 0; i < 200; i++) A.step(1); return JSON.stringify({ k0, k1, k2: A.sunK(), said: W.sun.said }); }'''))
        check('if the future fades the Sun slowly settles back, and the lines can be told again', r['k0'] > r['k1'] > 0 and r['k2'] == 0 and r['said'] == 0, str(r))
        # the far-future date
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, D = A.SUN.SUN_DATE, F = W.fates; const out = {}; F.ended = null; F.endY = null; W.care = null;
          F.done = []; F.active = F.active.filter(a => a.id !== 'wandering'); const y = W.year; W.year = D - 10; A.sunTick(1); out.before = F.active.some(a => a.id === 'wandering');
          W.year = D + 1; A.sunTick(1); out.after = F.active.some(a => a.id === 'wandering'); out.why = (F.active.find(a => a.id === 'wandering') || {}).why; out.dbg = [F.edgeT != null, F.ended, F.done.join(), W.year, A.W.civs.filter(c => c.alive).length, !!W.care];
          A.endFate('wandering', 'faded'); A.sunTick(1); out.again = F.active.some(a => a.id === 'wandering');
          const e = F.edgeT; F.edgeT = null; F.done = []; A.sunTick(1); out.noEdge = F.active.some(a => a.id === 'wandering'); F.edgeT = e; W.year = y; return JSON.stringify(out); }'''))
        check('by the far-future date the Sun begins to swell for certain', not r['before'] and r['after'], str(r))
        check('only once, and only once someone has reached space', not r['again'] and not r['noEdge'], str(r))
        # saving
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; W.sun = { k: .4321, said: 3 }; const d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d)));
          const bad = JSON.parse(JSON.stringify(d)); bad.sun = { k: 5, said: 'x' }; const b2 = A.sanitizeWorld(bad); const bad2 = JSON.parse(JSON.stringify(d)); bad2.sun = 'hot'; const b3 = A.sanitizeWorld(bad2);
          const old = JSON.parse(JSON.stringify(d)); delete old.sun; const o2 = A.sanitizeWorld(old); A.loadWorld(d); return JSON.stringify({ back: back.sun, bad: b2.sun, bad2: b3.sun, old: o2.sun, loaded: A.W.sun, t: A.sunHeat() }); }'''))
        check('the Sun\'s state is saved and loaded back', r['back'] == {'k': .4321, 'said': 3} and r['loaded'] == {'k': .4321, 'said': 3} and r['t'] > 0, str(r))
        check('bad values are clamped; old saves have the old Sun', r['bad'] == {'k': 1, 'said': 0} and r['bad2'] == {'k': 0, 'said': 0} and r['old'] == {'k': 0, 'said': 0}, str(r))
        print('errors:', errs[:3] if errs else 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
