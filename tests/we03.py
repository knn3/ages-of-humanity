# WE-03 the journey: with every engine ready after the verdict the world leaves its orbit instead of ending at once; the Sun falls
# behind and the light dims, the surface and seas freeze, peoples move into lit cities under the ice (harvests safe), Jupiter swells
# in the sky and its pull brings a crisis (worse with war), then the deep voyage and the Long Voyage ending; seen on the ground and
# from space; no other future begins meanwhile; saved and sanitised.
import asyncio, json, os, pathlib, math
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

SETUP = r'''() => { const A = window.__aoh; A.newWorld(5150); A.UI.random = false; for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1);
  const W = A.W; for (const a of [...W.fates.active]) A.endFate(a.id, 'faded'); W.fates.done = []; W.fates.ended = null; W.care = null; W.wars = []; W.voy = null; W.pollution = 0; W.tempShift = 0;
  const cs = W.civs.filter(c => c.alive); cs.forEach(c => { c.era = 12; c.machine = false; c.pop = 5e8; });
  W.fates.lastStart = -1e9; for (const id in W.fates.p) W.fates.p[id] = 0; A.startFate('wandering', 'event');
  W.eng = { by: Object.fromEntries(cs.map(c => [c.id, 1])), said: 1, stall: false, done: true }; W.sun = { k: 1, said: 15 }; scrollTo(0, 0); return cs.length; }'''
AT = r'''(u) => { const A = window.__aoh, W = A.W; W.voy.t0 = W.simTime - u * A.VOY.VOY_SPAN; A.voyTick(.001); return JSON.stringify({ u: A.voyU(), far: A.voyFar(), cold: A.voyCold(), under: A.voyUnder(), jup: A.voyJup(), t: A.temp(), said: W.voy.said, ended: W.fates.ended }); }'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        n = await ev(SETUP)
        k0 = json.loads(await ev("() => { const A = window.__aoh; A.step(.1); return JSON.stringify(A.W.civs.filter(c => c.alive).map(c => c._.K)); }"))
        # the verdict with every engine ready: the voyage begins, not the ending
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, F = W.fates, a = F.active.find(x => x.id === 'wandering'); a.t0 = W.simTime - A.FATES.wandering.span - 2; A.fateTick(1); A.voyTick(.001);
          return JSON.stringify({ voy: !!W.voy, active: F.active.some(x => x.id === 'wandering'), ended: F.ended, line: W.hist.filter(e => /engines fire as one. Slowly/.test(e.h)).length }); }'''))
        check('with every engine ready at the verdict, the world leaves its orbit (no ending yet)', r['voy'] and r['active'] and r['ended'] is None and r['line'] == 1, str(r))
        a = json.loads(await ev(AT, .1)); b1 = json.loads(await ev(AT, .2)); c3 = json.loads(await ev(AT, .4))
        check('the Sun falls behind as the voyage goes on', a['far'] < b1['far'] < c3['far'] and c3['far'] > .5, f"{a['far']:.2f} {b1['far']:.2f} {c3['far']:.2f}")
        check('the surface freezes: far below zero by the time Jupiter nears', c3['t'] < -25 and a['t'] > c3['t'], f"{a['t']:.1f} -> {c3['t']:.1f}")
        check('peoples move underground from early in the voyage', not a['under'] and b1['under'], f"{a['under']} {b1['under']}")
        lines = await ev(r'''() => window.__aoh.W.hist.filter(e => /move underground|seas freeze|Jupiter grows/.test(e.h)).map(e => e.h.slice(0, 40))''')
        check('the chronicle tells the move underground, then the seas freezing, in order', len(lines) == 2 and 'Frost' in lines[0] and 'freeze' in lines[1], str(lines))
        k1 = json.loads(await ev("() => { const A = window.__aoh; A.step(.1); return JSON.stringify(A.W.civs.filter(c => c.alive).map(c => c._.K)); }"))
        check('harvests are safe underground: what the land can feed hardly changes in the cold', all(.9 < x / y < 1.3 for x, y in zip(k1, k0)), f'{[round(x / y, 2) for x, y in zip(k1, k0)]}')
        # no other future begins during the voyage
        r = json.loads(await ev(r'''() => { const A = window.__aoh, F = A.W.fates; F.p.agi = 3; F.lastStart = -1e9; A.fateTick(1); return JSON.stringify(F.active.map(a => a.id)); }'''))
        check('no other future begins during the voyage', r == ['wandering'], str(r))
        await ev("() => { window.__aoh.W.fates.p.agi = 0; }")
        clock = await ev("() => { const A = window.__aoh; A.updateUI(); return document.querySelector('#futures').innerText; }")
        check('the Futures panel follows the voyage', 'The voyage 40%' in clock and 'frozen, under the ice' in clock, clock.replace('\n', ' | ')[:160])
        # other futures fade when the voyage begins; only a disaster may end the world before the Long Voyage
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, F = W.fates, keep = W.voy; W.voy = null; A.startFate('immortal', 'event'); A.voyBegin(); const act = F.active.map(a => a.id);
          const g = A.reachEnding('galactic'); const e1 = F.ended; F.ended = null; W.voy.t0 = keep.t0; W.voy.said = keep.said; return JSON.stringify({ act, g, e1 }); }'''))
        check('when the voyage begins any other future fades, and no other kind of ending can come before the Long Voyage', r['act'] == ['wandering'] and r['g'] is False and r['e1'] is None, str(r))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, F = W.fates, keep = W.voy; W.voy = null; F.active.push({ id: 'threebody', t0: W.simTime, y0: 0, why: 'event' }); W.tb = W.tb || {}; A.voyBegin();
          const out = { act: F.active.map(a => a.id), line: W.hist.filter(e => /Hevari fleet will reach an empty orbit/.test(e.h)).length, tb: W.tb }; W.voy.t0 = keep.t0; W.voy.said = keep.said; return JSON.stringify(out); }'''))
        check('a world fleeing the Hevari leaves their fleet an empty orbit (the Three-Sun story ends)', r['act'] == ['wandering'] and r['line'] == 1 and r['tb'] is None, str(r))
        # the ground: a small far Sun, a dim day, an iced sea, the cities under the ice
        r = json.loads(await ev(r'''() => { const A = window.__aoh, V = A.V, W = A.W, c = W.civs.find(c => c.alive); V.focus = null; A.setZoom(1.4); V.cam = c.x - V.vw / 2; V.camY = null; V.dayT = .62; A.render();
          return JSON.stringify({ sun: V.flatSun, L: V.L, under: V.picks.filter(p => p.kind === 'undercity').length }); }'''))
        check('from the ground the Sun is a small far disc and the day is dim', r['sun'] and r['sun'][2] < 15 and r['L'] < .6, str(r))
        check('each people has a city under the ice (right-clickable)', r['under'] >= 1, str(r))
        tip = await ev(r'''() => { const A = window.__aoh, V = A.V, q = V.picks.find(p => p.kind === 'undercity'), cv = document.querySelector('#world'), rc = cv.getBoundingClientRect(), [sx, sy] = A.W2S((q.x0 + q.x1) / 2, (q.y0 + q.y1) / 2);
          cv.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: rc.left + sx, clientY: rc.top + sy, button: 2 })); const t = document.querySelector('#tip'); return t.style.display !== 'none' ? t.innerText : 'hidden'; }''')
        check('right-clicking a city under the ice tells who lives there', 'City under the ice' in tip and 'People' in tip and '°C' in tip, tip.replace('\n', ' | ')[:200])
        await ev("() => { const b = document.querySelector('#tipClose'); if (b) b.click(); }")
        r = json.loads(await ev(r'''() => { const A = window.__aoh, V = A.V, W = A.W, cv = document.querySelector('#world'), k = cv.width / cv.clientWidth, c2 = cv.getContext('2d'); A.setZoom(.6); V.dayT = .5;
          const seaPx = () => { let x0 = null; for (let x = 0; x < A.gy.length || x < 9000; x += 20) { if (A.gy(x) > A.seaY() + 20) { x0 = x; break; } } if (x0 == null) return null; V.cam = x0 - V.vw / 2; V.camY = null; A.render(); const [sx, sy] = A.W2S(x0, A.seaY() + 4); const d = c2.getImageData(Math.round(sx * k), Math.round(sy * k), 1, 1).data; return [d[0], d[1], d[2]]; };
          const cold = seaPx(); const keep = W.voy; W.voy = null; const warm = seaPx(); W.voy = keep; A.render(); return JSON.stringify({ cold, warm }); }'''))
        check('the seas freeze white', r['cold'] and r['warm'] and sum(r['cold']) > sum(r['warm']) + 120, str(r))
        # from space: the Sun far off; Jupiter swings close at the pass
        r = json.loads(await ev(r'''() => { const A = window.__aoh, V = A.V, W = A.W; A.setZoom(.0016); A.render(); const d1 = Math.hypot(V.sunXY[0] - V.cx, V.sunXY[1] - V.cy); const keep = W.voy; W.voy = null; A.render(); const d0 = Math.hypot(V.sunXY[0] - V.cx, V.sunXY[1] - V.cy); W.voy = keep; return JSON.stringify({ d0, d1 }); }'''))
        check('from the solar system the Sun is left far behind', r['d1'] > 3 * r['d0'], str(r))
        # Jupiter's pass and its crisis
        pop0 = await ev("() => window.__aoh.W.civs.filter(c => c.alive).reduce((a, c) => a + c.pop, 0)")
        r = json.loads(await ev(AT, .48))
        r2 = json.loads(await ev(r'''() => { const A = window.__aoh, V = A.V, W = A.W; A.setZoom(1.4); V.dayT = .62; A.render(); const fj = V.flatJup; A.setZoom(.0016); A.render(); const J = V.bodyPos.Jupiter, dJ = J ? Math.hypot(J[0] - V.cx, J[1] - V.cy) : -1;
          return JSON.stringify({ fj, dJ, pop: W.civs.filter(c => c.alive).reduce((a, c) => a + c.pop, 0), line: W.hist.filter(e => /Jupiter’s pull/.test(e.h)).length, grows: W.hist.filter(e => /Jupiter grows/.test(e.h)).length, jup: W.voy.jup }); }'''))
        check('at the pass Jupiter fills the sky from the ground and swings close in the solar system', r2['fj'] and r2['fj'][2] > 100 and 0 <= r2['dJ'] < 250, str(r2)[:160])
        check('Jupiter grows in the sky, then its pull brings a crisis that costs lives, told in the chronicle', r2['grows'] == 1 and r2['line'] == 1 and r2['pop'] < pop0 * .93, f"{r2['pop'] / pop0:.3f} line {r2['line']}")
        r = json.loads(await ev(AT, .61)); out = await ev("() => JSON.stringify(window.__aoh.W.voy.jup)")
        check('at peace the engines drag the world clear of Jupiter', json.loads(out)['out'] == 'clear', out)
        # with war during the pass it goes worse
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, cs = W.civs.filter(c => c.alive); W.voy.said = 0b1111; W.voy.jup = null; W.wars = [{ a: cs[0].id, b: cs[1].id, t: 0, adv: 0 }]; const p0 = cs.reduce((a, c) => a + c.pop, 0);
          W.voy.t0 = W.simTime - .48 * A.VOY.VOY_SPAN; A.voyTick(.001); W.voy.t0 = W.simTime - .61 * A.VOY.VOY_SPAN; A.voyTick(.001); W.wars = []; return JSON.stringify({ out: W.voy.jup.out, left: cs.reduce((a, c) => a + c.pop, 0) / p0 }); }'''))
        check('with war during the pass the world is scarred and loses far more', r['out'] == 'scarred' and r['left'] < .7, str(r))
        # the deep voyage, then the Long Voyage ending
        r = json.loads(await ev(AT, .8)); r = json.loads(await ev(AT, 1.0))
        txt = await ev("() => { const A = window.__aoh; return [A.W.hist.filter(e => /Children are born in the caverns/.test(e.h)).length, A.ENDINGS.wandering.text]; }")
        check('the deep voyage is told, and at its end comes the Long Voyage', r['ended'] == 'wandering' and txt[0] == 1 and 'caverns' in txt[1], str(r) + ' ' + str(txt))
        await ev("() => { const m = document.querySelector('#modal'); if (m) m.classList.remove('open'); }")
        # saving, garbage, old saves, a new cycle
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; W.voy = { t0: 123.5, y0: 40100, said: 7, done: false, jup: { wars: 1, out: 'clear' } }; const d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d)));
          const bad = JSON.parse(JSON.stringify(d)); bad.voy = { t0: 'x' }; const b1 = A.sanitizeWorld(bad); const bad2 = JSON.parse(JSON.stringify(d)); bad2.voy = { t0: 5, said: 999, jup: { out: 'boom', wars: -3 } }; const b2 = A.sanitizeWorld(bad2);
          const old = JSON.parse(JSON.stringify(d)); delete old.voy; const o2 = A.sanitizeWorld(old); A.loadWorld(d); const loaded = A.W.voy; A.W.fates.ended = 'collapse'; A.riseAgain(); return JSON.stringify({ back: back.voy, loaded, b1: b1.voy, b2: b2.voy, old: o2.voy, cycle: A.W.voy }); }'''))
        check('the voyage is saved and loaded back', r['back'] == {'t0': 123.5, 'y0': 40100, 'said': 7, 'done': False, 'jup': {'wars': 1, 'out': 'clear'}} and r['loaded'] == r['back'], str(r['back']))
        check('bad values are dropped or clamped; old saves have no voyage; a new cycle starts without it', r['b1'] is None and r['b2'] == {'t0': 5, 'y0': 0, 'said': 127, 'done': False, 'jup': {'wars': 0, 'out': None}} and r['old'] is None and r['cycle'] is None, str(r))
        print('errors:', errs[:3] if errs else 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
