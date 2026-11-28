# ASC-01 mind upload: during the Great Upload, Future Age peoples move their minds into data centres at a speed set by character
# (the Devout refuse), never during their own war; their living population falls, their buildings go dark one by one in a fixed
# order (no lit windows), a data centre grows beside the capital; chronicle, card, panel and right-click info; saved and sanitised.
import asyncio, json, os, pathlib, re
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

SETUP = r'''() => { const A = window.__aoh; A.newWorld(6262); A.UI.random = false; for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1);
  const W = A.W; for (const a of [...W.fates.active]) A.endFate(a.id, 'faded'); W.fates.done = []; W.fates.ended = null; W.care = null; W.wars = []; W.asc = null;
  const cs = W.civs.filter(c => c.alive); const T = ['Curious', 'Mercantile', 'Warlike', 'Devout']; cs.forEach((c, i) => { c.era = 12; c.machine = false; c.trait = T[i % 4]; c.pop = 4e8; });
  W.fates.lastStart = -1e9; for (const id in W.fates.p) W.fates.p[id] = 0; A.startFate('ascension', 'event'); scrollTo(0, 0); return JSON.stringify(cs.map(c => [c.id, c.trait])); }'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        cs = json.loads(await ev(SETUP)); ids = {t: i for i, t in cs}
        T = (await ev("() => window.__aoh.ASC"))['ASC_TIME']
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; A.ascTick(1); A.ascTick(1); return JSON.stringify({ up: W.asc.up, begin: W.hist.filter(e => /begin to upload their minds/.test(e.h)).length, refuse: W.hist.filter(e => /refuse the upload/.test(e.h)).length }); }'''))
        dev = str(ids['Devout'])
        check('Future Age peoples begin to upload (told once each); the Devout refuse (told once)', r['begin'] == len(cs) - 1 and r['refuse'] == 1 and not r['up'].get(dev), str(r))
        r = json.loads(await ev(r'''(n) => { const A = window.__aoh, W = A.W; for (let i = 0; i < n; i++) A.ascTick(1); return JSON.stringify(W.asc.up); }''', 48))
        cu, me, wa = r[str(ids['Curious'])], r[str(ids['Mercantile'])], r[str(ids['Warlike'])]
        check('speed follows character: Curious fastest, then Mercantile, then Warlike', cu > me > wa > 0 and abs(me - 50 / T) < .01, f'{cu:.3f} {me:.3f} {wa:.3f}')
        # a people at war pauses
        r = json.loads(await ev(r'''([a, b]) => { const A = window.__aoh, W = A.W, u0 = W.asc.up[a]; W.wars = [{ a, b, t: 0, adv: 0 }]; for (let i = 0; i < 10; i++) A.ascTick(1); const u1 = W.asc.up[a]; W.wars = []; return JSON.stringify({ u0, u1 }); }''', [ids['Curious'], ids['Devout']]))
        check('a people at war stops uploading until the war ends', r['u0'] == r['u1'], str(r))
        # living population falls while minds move in; the Devout keep theirs
        r = json.loads(await ev(r'''([a, d]) => { const A = window.__aoh, W = A.W, ca = W.civs.find(c => c.id === a), cd = W.civs.find(c => c.id === d); const p0 = [ca.pop, cd.pop], m0 = A.ascMinds(ca);
          for (let i = 0; i < 60; i++) { for (const f of W.fates.active) f.t0 = W.simTime; for (const id in W.fates.p) W.fates.p[id] = 0; W.wars = []; A.step(1); } const u = W.asc.up[a]; A.step(.01); const K1 = ca._.K; W.asc.up[a] = 0; A.step(.01); const K0 = ca._.K; W.asc.up[a] = u;
          return JSON.stringify({ a: ca.pop / p0[0], d: cd.pop / p0[1], minds: A.ascMinds(ca) - m0, up: A.ascOf(ca), kr: K1 / K0 }); }''', [ids['Curious'], ids['Devout']]))
        check('the land feeds only the bodies left: an uploading people’s living numbers fall far behind, while its minds move into the machines', r['a'] < .5 * r['d'] and r['minds'] > 1e7 and abs(r['kr'] - (1 - .95 * r['up'])) < .03, str(r))
        lines = await ev(r'''() => window.__aoh.W.hist.filter(e => /Half of .* now live in the machines/.test(e.h)).length''')
        check('half way is told', lines >= 1, str(lines))
        # buildings go dark one by one in a fixed order, and lose their lights
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, V = A.V, c = W.civs.find(c => c.id === a); V.focus = null; A.setZoom(1.4); V.cam = c.x - V.vw / 2; V.camY = null; V.dayT = 0; A.render();
          const items = c._.items.filter(b => b.t !== 'field'), dark = u => { W.asc.up[a] = u; return items.filter(b => A.ascDark(c, b)).map(b => b.x); };
          const d3 = dark(.3), d6 = dark(.6), d0 = dark(0), d1 = dark(1); const sub = d3.every(x => d6.includes(x));
          const lights = u => { W.asc.up[a] = u; A.render(); return [...Array(Math.floor(window.__lt ? 0 : 0))].length; };
          return JSON.stringify({ n: items.length, d0: d0.length, d3: d3.length, d6: d6.length, d1: d1.length, sub }); }''', ids['Curious']))
        n = r['n']
        check('more buildings go dark as more upload, always the same ones first', r['d0'] == 0 and r['sub'] and abs(r['d3'] / n - .3) < .15 and abs(r['d6'] / n - .6) < .15 and r['d1'] == n, str(r))
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, V = A.V, c = W.civs.find(c => c.id === a), cv = document.querySelector('#world'), k = cv.width / cv.clientWidth, c2 = cv.getContext('2d');
          const lit = u => { W.asc.up[a] = u; V.dayT = 0; A.render(); const [x0] = A.W2S(c.l, 0), [x1] = A.W2S(c.r, 0), L = Math.max(0, Math.round(x0)), R = Math.min(cv.clientWidth, Math.round(x1)); if (R <= L) return -1;
            const d = c2.getImageData(Math.round(L * k), 0, Math.round((R - L) * k), cv.height).data; let n = 0; for (let i = 0; i < d.length; i += 4) if (d[i] > 230 && d[i + 1] > 180 && d[i + 2] < 150) n++; return n; };
          return JSON.stringify({ none: lit(0), all: lit(1) }); }''', ids['Curious']))
        check('at night an uploaded people’s town has almost no lit windows', r['none'] > 50 and r['all'] < r['none'] * .25, str(r))
        # the data centre
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, V = A.V, c = W.civs.find(c => c.id === a); V.dayT = .5; const wd = u => { W.asc.up[a] = u; A.render(); const q = V.picks.find(p => p.kind === 'datacentre' && p.d.c.id === a); return q ? q.x1 - q.x0 : 0; };
          return JSON.stringify({ w2: wd(.2), w9: wd(.9) }); }''', ids['Curious']))
        check('a data centre stands beside the capital and grows as minds move in', r['w2'] > 0 and r['w9'] > r['w2'] + 15, str(r))
        tip = await ev(r'''(a) => { const A = window.__aoh, V = A.V; A.render(); const q = V.picks.find(p => p.kind === 'datacentre' && p.d.c.id === a), cv = document.querySelector('#world'), rc = cv.getBoundingClientRect(), [sx, sy] = A.W2S((q.x0 + q.x1) / 2, (q.y0 + q.y1) / 2);
          cv.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: rc.left + sx, clientY: rc.top + sy, button: 2 })); const t = document.querySelector('#tip'); return t.style.display !== 'none' ? t.innerText : 'hidden'; }''', ids['Curious'])
        check('right-clicking the data centre tells whose minds are inside and how many', 'Data centre' in tip and 'Minds inside' in tip and 'Uploaded: 90%' in tip, tip.replace('\n', ' | ')[:200])
        await ev("() => { const b = document.querySelector('#tipClose'); if (b) b.click(); }")
        card = await ev(r'''([a, d]) => { const A = window.__aoh, W = A.W; return [A.tipBody({ civ: W.civs.find(c => c.id === a) })[1], A.tipBody({ civ: W.civs.find(c => c.id === d) })[1]].map(h => h.replace(/<[^>]+>/g, ' ')).join(' || '); }''', [ids['Curious'], ids['Devout']])
        check('the people’s card shows how much has uploaded, or that they refuse', re.search(r'Uploaded:\s*90%', card) and 'refuses the upload' in card, card[-200:])
        clock = await ev("() => { const A = window.__aoh; A.updateUI(); return document.querySelector('#futures').innerText; }")
        check('the Futures panel shows how much of humanity has uploaded', 'of humanity uploaded' in clock, clock.replace('\n', ' | ')[:160])
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W; W.asc.up[a] = .995; A.ascTick(1); return JSON.stringify({ last: W.hist.filter(e => /The last of .* have left their bodies/.test(e.h)).length, up: W.asc.up[a] }); }''', ids['Curious']))
        check('the last to leave are told', r['last'] == 1 and r['up'] == 1, str(r))
        # saving, garbage, old saves, a new cycle
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; W.asc = { up: { 5: .25 }, minds: { 5: 3e8 }, said: { 5: 3 }, pop: {} }; const d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d)));
          const bad = JSON.parse(JSON.stringify(d)); bad.asc = { up: { 5: 9, x: .2, 6: 'q' }, minds: { 5: -4 }, said: { 5: 99 } }; const b2 = A.sanitizeWorld(bad); const b3 = A.sanitizeWorld(Object.assign(JSON.parse(JSON.stringify(d)), { asc: 7 }));
          const old = JSON.parse(JSON.stringify(d)); delete old.asc; const o2 = A.sanitizeWorld(old); A.loadWorld(d); const loaded = A.W.asc; A.W.fates.ended = 'collapse'; A.riseAgain(); return JSON.stringify({ back: back.asc, loaded, bad: b2.asc, b3: b3.asc, old: o2.asc, cycle: A.W.asc }); }'''))
        check('the upload is saved and loaded back', r['back'] == {'up': {'5': .25}, 'minds': {'5': 3e8}, 'said': {'5': 3}, 'pop': {}, 'green': {}, 'hold': {}} and r['loaded'] == r['back'], str(r['back']))
        check('bad values are dropped or clamped; old saves have none; a new cycle starts without it', r['bad'] == {'up': {'5': 1}, 'minds': {'5': 0}, 'said': {'5': 63}, 'pop': {}, 'green': {}, 'hold': {}} and r['b3'] is None and r['old'] is None and r['cycle'] is None, str(r))
        print('errors:', errs[:3] if errs else 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
