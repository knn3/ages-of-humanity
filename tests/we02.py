# WE-02 planet engines: while the Dying Sun runs, Future Age peoples build engines on their land; any war stalls the work and a
# people at war builds nothing; builders warm to each other and their wars end sooner; the Long Voyage needs every engine; the engines
# are drawn on the strip (tower + blue jet) and as blue jets on the globe; right-click info; saved and sanitised.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

SETUP = r'''() => { const A = window.__aoh; A.newWorld(5150); A.UI.random = false; for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1);
  const W = A.W; for (const a of [...W.fates.active]) A.endFate(a.id, 'faded'); W.fates.done = []; W.fates.ended = null; W.care = null; W.wars = [];
  const cs = W.civs.filter(c => c.alive); cs.forEach((c, i) => { c.era = i === cs.length - 1 ? 10 : 12; c.machine = false; });
  W.eng = null; W.sun = { k: 0, said: 0 }; W.fates.lastStart = -1e9; for (const id in W.fates.p) W.fates.p[id] = 0; A.startFate('wandering', 'event'); scrollTo(0, 0);
  return JSON.stringify({ civs: cs.map(c => [c.id, c.era]) }); }'''
TICK = r'''(n) => { const A = window.__aoh; for (let i = 0; i < n; i++) A.engTick(1); return JSON.stringify(Object.fromEntries(A.W.civs.filter(c => c.alive).map(c => [c.id, +A.engOf(c).toFixed(4)]))); }'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        s = json.loads(await ev(SETUP)); civs = s['civs']; low = civs[-1][0]; hi = [c for c, e in civs if e >= 11]
        T = (await ev("() => window.__aoh.ENG"))['ENG_TIME']
        r = json.loads(await ev(TICK, 1))
        lines = await ev("() => window.__aoh.W.hist.filter(e => /begin a planet engine/.test(e.h)).length")
        check('Future Age peoples begin engines as the Dying Sun runs, each told once', all(r[str(c)] > 0 for c in hi) and lines == len(hi), f'{r} lines {lines}')
        check('a people below the Future Age builds none', r[str(low)] == 0, str(r[str(low)]))
        r = json.loads(await ev(TICK, int(T / 2) - 1))
        check(f'at peace an engine takes about {T} sim seconds (half way at half time)', all(abs(r[str(c)] - .5) < .02 for c in hi), str(r))
        # war: the two at war build nothing, everyone else crawls; the stall is told, and the restart
        r = json.loads(await ev(r'''([a, b]) => { const A = window.__aoh, W = A.W, ca = W.civs.find(c => c.id === a), cb = W.civs.find(c => c.id === b); const before = Object.fromEntries(W.civs.map(c => [c.id, A.engOf(c)]));
          W.wars = [{ a, b, t: 0, adv: 0 }]; A.engTick(10); const after = Object.fromEntries(W.civs.map(c => [c.id, A.engOf(c)])); const stall = W.eng.stall, l1 = W.hist.filter(e => /Work on the planet engines stops/.test(e.h)).length;
          W.wars = []; A.engTick(1); const l2 = W.hist.filter(e => /work on the planet engines begins again/.test(e.h)).length;
          return JSON.stringify({ d: Object.fromEntries(Object.keys(after).map(k => [k, +(after[k] - before[k]).toFixed(5)])), stall, l1, l2, resumed: !W.eng.stall }); }''', [hi[0], hi[1]]))
        others = [c for c in hi[2:]]
        check('a people at war builds nothing', r['d'][str(hi[0])] == 0 and r['d'][str(hi[1])] == 0, str(r['d']))
        check('any war slows every other builder to a crawl', all(abs(r['d'][str(c)] - 10 * .08 / T) < 1e-4 for c in others) and len(others) > 0, str(r['d']))
        check('the chronicle tells when the work stops for war and when it begins again', r['stall'] and r['l1'] == 1 and r['l2'] == 1 and r['resumed'], str(r))
        # cooperation: builders' relations warm; their wars end sooner
        # (relations and treaty odds are checked statistically below with the game's own functions)
        r = json.loads(await ev(r'''([a, b]) => { const A = window.__aoh, W = A.W, out = {};
          const ca = W.civs.find(c => c.id === a), cb = W.civs.find(c => c.id === b);
          // treaty odds: the same 6-second-old war, stepped one sim second at a time, with and without the engine work
          const trial = on => { const keep = W.fates.active.slice(); if (!on) W.fates.active = W.fates.active.filter(x => x.id !== 'wandering'); let ended = 0, n = 0;
            for (let k = 0; k < 200; k++) { W.wars = [{ a, b, t: 7, adv: 0 }]; ca.pop = cb.pop = 1e9; for (let s = 0; s < 5; s++) { A.updateWars(1); if (!W.wars.some(w => (w.a === a && w.b === b) || (w.a === b && w.b === a))) { ended++; break; } } }
            W.fates.active = keep; W.wars = []; if (W.eng) W.eng.stall = false; return ended; };
          out.on = trial(true); out.off = trial(false); return JSON.stringify(out); }''', [hi[0], hi[1]]))
        check('while the engines are built, wars end in treaties far sooner', r['on'] > 2 * max(1, r['off']), str(r))
        # the verdict: no Long Voyage until every engine is finished; then it comes
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, F = W.fates, a = F.active.find(x => x.id === 'wandering'), sp = A.FATES.wandering.span; W.wars = [];
          for (const c of A.engBuilders()) W.eng.by[c.id] = .6; a.t0 = W.simTime - sp - 5; A.fateTick(1); const still = F.active.some(x => x.id === 'wandering') && !F.ended;
          const clock = (document.querySelector('#futures') && (A.updateUI(), document.querySelector('#futures').innerText)) || '';
          for (const c of A.engBuilders()) W.eng.by[c.id] = 1; A.engTick(1); const done = W.eng.done, line = W.hist.filter(e => /Every planet engine stands complete/.test(e.h)).length, fire = A.engFire(A.engBuilders()[0], 1);
          return JSON.stringify({ still, clock, done, line, fire }); }'''))
        check('past the verdict with engines unfinished, the world waits (no Long Voyage, no fading yet)', r['still'], str(r['still']))
        check('the Futures panel shows how far the engines are', 'engines 60%' in r['clock'], r['clock'].replace('\n', ' | ')[:200])
        check('when every engine is finished the chronicle says so and they fire at full power', r['done'] and r['line'] == 1 and r['fire'] > .8, str(r))
        # drawing: the strip and the globe
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, V = A.V, c = A.engBuilders()[0], x = A.engX(c); V.focus = null; A.setZoom(.55); V.cam = x - V.vw / 2; V.camY = null; V.dayT = .5; A.render(); A.render();
          A.setZoom(1.4); V.cam = x - V.vw / 2; A.render(); const pk = V.picks.filter(p => p.kind === 'engine'); A.setZoom(.55); V.cam = x - V.vw / 2; A.render(); A.render(); const cv = document.querySelector('#world'), k = cv.width / cv.clientWidth, [sx, sy] = A.W2S(x, A.gy(x) - A.engX && (40 + 150) + 0 - 60);
          let blue = 0; for (let dy = 0; dy < 60; dy += 4) { const [px, py] = A.W2S(x, A.gy(x) - 190 - 20 - dy); if (py < 0) continue; const d = cv.getContext('2d').getImageData(Math.round(px * k), Math.round(py * k), 1, 1).data; if (d[2] > d[0] + 40 && d[2] > 150) blue++; }
          return JSON.stringify({ picks: pk.length, pickCivs: [...new Set(pk.map(p => p.d.c.id))], blue }); }'''))
        check('on the strip each builder has its engine tower (right-clickable)', r['picks'] >= 1, str(r))
        check('a firing engine shows a blue jet above its tower', r['blue'] >= 5, str(r))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, V = A.V; let best = 0; for (const z of [.12, .08, .05, .03, .02]) { A.setZoom(z); A.render(); best = Math.max(best, V.orbPicks.filter(p => p.kind === 'enginejet').length); } return JSON.stringify({ jets: best }); }'''))
        check('on the globe the engines fire as blue jets out from the land', r['jets'] >= 1, str(r))
        # right-click info on an engine
        r = await ev(r'''() => { const A = window.__aoh, V = A.V, c = A.engBuilders()[0], x = A.engX(c); A.setZoom(1.6); V.cam = x - V.vw / 2; V.camY = null; A.render(); const q = V.picks.find(p => p.kind === 'engine'); if (!q) return 'none';
          const cv = document.querySelector('#world'), rc = cv.getBoundingClientRect(), [sx, sy] = A.W2S((q.x0 + q.x1) / 2, (q.y0 + q.y1) / 2 + 10);
          cv.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: rc.left + sx, clientY: rc.top + sy, button: 2 })); const t = document.querySelector('#tip'); return t.style.display !== 'none' ? t.innerText : 'hidden'; }''')
        check('right-clicking an engine tells what it is and how far it is built', 'Planet engine' in r and 'Built: 100%' in r and 'firing' in r, r.replace('\n', ' | ')[:220])
        await ev("() => { const b = document.querySelector('#tipClose'); if (b) b.click(); }")
        # the Long Voyage comes once the engines are ready
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; document.querySelector('#modal') && document.querySelector('#modal').classList.remove('open'); A.fateTick(1); return JSON.stringify({ ended: W.fates.ended }); }'''))
        check('with every engine ready after the verdict, the Long Voyage begins', r['ended'] == 'wandering', str(r))
        # saving, garbage, old saves, new cycle
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; W.eng = { by: { 3: .25, 7: 1 }, said: 1, stall: true, done: false }; const d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d)));
          const bad = JSON.parse(JSON.stringify(d)); bad.eng = { by: { 3: 5, x: .5, 9: 'q', 4: -1 }, said: 99, stall: 'yes', done: 0 }; const b2 = A.sanitizeWorld(bad);
          const b3 = A.sanitizeWorld(Object.assign(JSON.parse(JSON.stringify(d)), { eng: 'big' })); const old = JSON.parse(JSON.stringify(d)); delete old.eng; const o2 = A.sanitizeWorld(old);
          A.loadWorld(d); const loaded = A.W.eng; A.W.fates.ended = 'collapse'; A.riseAgain(); return JSON.stringify({ back: back.eng, bad: b2.eng, b3: b3.eng, old: o2.eng, loaded, cycle: A.W.eng }); }'''))
        check('engines are saved and loaded back', r['back'] == {'by': {'3': .25, '7': 1}, 'said': 1, 'stall': True, 'done': False} and r['loaded'] == r['back'], str(r['back']))
        check('bad values are dropped or clamped; old saves have no engines; a new cycle starts without them', r['bad'] == {'by': {'3': 1, '4': 0}, 'said': 15, 'stall': True, 'done': False} and r['b3'] is None and r['old'] is None and r['cycle'] is None, str(r))
        print('errors:', errs[:3] if errs else 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
