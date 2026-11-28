# GDN-01 the Garden path: peoples with healthy, protected land at peace (Industrial Age on) may choose to stay small, by character
# (Warlike never), far likelier while the Garden future runs; the land feeds fewer (K × 1 − GDN_K × k) so the population shrinks gently,
# nature regrows faster, stability rises, policy stays Protect; forests close in and roofs/fields turn to gardens; war or ruined
# land ends it; chronicle, card, Futures panel; saved and sanitised.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))
SETUP = r'''() => { const A = window.__aoh; A.newWorld(6262); A.UI.random = false; for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1);
  const W = A.W, V = A.V; for (const a of [...W.fates.active]) A.endFate(a.id, 'faded'); W.fates.done = []; W.fates.ended = null; W.care = null; W.wars = []; W.asc = null; W.gdn = null;
  const cs = W.civs.filter(c => c.alive); const T = ['Curious', 'Devout', 'Warlike', 'Mercantile']; cs.forEach((c, i) => { c.era = 10; c.machine = false; c.merged = false; c.trait = T[i % 4]; c.policy = 'protect'; c.tmpPol = null; c.stability = 60; c.pop = 3e8; });
  for (let i = 0; i < W.nat.f.length; i++) if (!V.seaCell[i]) { W.nat.f[i] = V.cap[i]; W.nat.w[i] = .9; } A.natureTick(.01);
  W.fates.lastStart = -1e9; for (const id in W.fates.p) W.fates.p[id] = 0; scrollTo(0, 0); return JSON.stringify(cs.map(c => [c.id, c.trait])); }'''
PIN = "for (const f of W.fates.active) f.t0 = W.simTime; for (const id in W.fates.p) W.fates.p[id] = 0; W.wars = []; for (const k in W.rel) W.rel[k] = 60;"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        ids = {t: i for i, t in json.loads(await ev(SETUP))}
        cu, dv, wa, me = ids['Curious'], ids['Devout'], ids['Warlike'], ids['Mercantile']
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, c = W.civs.find(c => c.id === a), o = {};
          o.fit = A.gdnFit(c); c.policy = 'exploit'; o.exploit = A.gdnFit(c); c.policy = 'protect'; const f = c._.nat.fr; c._.nat.fr = .3; o.ruined = A.gdnFit(c); c._.nat.fr = f;
          const e = c.era; c.era = 6; o.old = A.gdnFit(c); c.era = e; const s = c.stability; c.stability = 20; o.unrest = A.gdnFit(c); c.stability = s; return JSON.stringify(o); }''', cu))
        check('only a people with healthy, protected land, in order, from the Industrial Age on may choose the Garden', r['fit'] and not (r['exploit'] or r['ruined'] or r['old'] or r['unrest']), str(r))
        r = json.loads(await ev(r'''(ids) => { const A = window.__aoh, W = A.W, R = Math.random; A.startFate('garden', 'event'); Math.random = () => 0; A.gdnTick(1); Math.random = R;
          return JSON.stringify({ on: W.gdn.on, lines: W.hist.filter(e => /choose the Garden path/.test(e.h)).length, fate: A.gdnOnF() }); }''', [cu, dv, wa, me]))
        on = r['on']
        check('peoples choose the Garden path by character: the Warlike never do', on.get(str(cu)) and on.get(str(dv)) and on.get(str(me)) and not on.get(str(wa)) and r['lines'] == 3, str(r))
        G = await ev("() => window.__aoh.GDN")
        check('it is far likelier while the Garden future runs (and Devout likeliest)', G['GDN_JOIN'] >= 10 * G['GDN_DRIFT'] and G['GDN_TRAIT']['Devout'] > G['GDN_TRAIT']['Curious'] > G['GDN_TRAIT']['Mercantile'] > 0 == G['GDN_TRAIT']['Warlike'], str(G))
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, c = W.civs.find(c => c.id === a); for (let i = 0; i < 59; i++) A.gdnTick(1); c.policy = 'exploit'; c.tmpPol = { p: 'exploit', until: W.simTime + 99 };
          const pol = A.policyOf(c); c.tmpPol = null; A.step(.01); const K1 = c._.K, k = A.gdnOf(c); W.gdn.k[a] = 0; A.step(.01); const K0 = c._.K; W.gdn.k[a] = k; return JSON.stringify({ k, pol, kr: K1 / K0 }); }''', cu))
        T = G['GDN_TIME']
        check('the choice takes hold over time; their land stays protected whatever else is decided', abs(r['k'] - 60 / T) < .02 and r['pol'] == 'protect', str(r))
        check('the land feeds fewer of them (carrying capacity scaled)', abs(r['kr'] - (1 - G['GDN_K'] * r['k'])) < .02, str(r))
        r = json.loads(await ev(r'''([a, w]) => { const A = window.__aoh, W = A.W, c = W.civs.find(c => c.id === a), x = W.civs.find(c => c.id === w); W.gdn.k[a] = 1; A.step(.01); c.pop = c._.K / (1 - A.GDN.GDN_K); x.pop = x._.K; const p0 = [c.pop, x.pop], s0 = c.stability; c.stability = 50;
          for (let i = 0; i < 80; i++) { ''' + PIN + r''' A.step(1); W.gdn.on[a] = 1; delete W.gdn.on[w]; delete W.gdn.k[w]; } return JSON.stringify({ g: c.pop / p0[0], x: x.pop / p0[1], st: c.stability, K: c.pop / c._.K }); }''', [cu, wa]))
        check('their population shrinks gently while others grow or hold', r['g'] < .85 and r['g'] > .3 and r['x'] > r['g'] * 1.15 and r['x'] > .8, str(r))
        check('stability rises on the Garden path', r['st'] > 62, str(r))
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, V = A.V, N = W.nat, ca = W.civs.find(c => c.id === a);
          const A1 = []; for (let i = Math.floor(ca.l / 100); i <= Math.floor(ca.r / 100); i++) if (!V.seaCell[i]) A1.push(i); const sv = A1.map(i => [i, N.f[i], N.w[i], N.s[i]]);
          const m = () => A1.reduce((s, i) => s + N.f[i] / Math.max(.05, V.cap[i]), 0) / A1.length;
          const run = k => { for (const [i] of sv) { N.f[i] = .08 * V.cap[i]; N.w[i] = .1; N.s[i] = .6; } W.gdn.k[a] = k; for (let t = 0; t < 40; t++) A.natureTick(1); return m(); };
          const g = run(1), z = run(0); for (const [i, f, ww, so] of sv) { N.f[i] = f; N.w[i] = ww; N.s[i] = so; } W.gdn.k[a] = 1; return JSON.stringify({ g, z }); }''', cu))
        check('forests come back faster on the same land once it is a Garden', r['g'] > 1.3 * r['z'], str(r))
        lines = json.loads(await ev(r'''() => { const W = window.__aoh.W, c = re => W.hist.filter(e => re.test(e.h)).length; return JSON.stringify([c(/shrunk to towns and villages among the trees/), c(/live as gardeners of their land/)]); }'''))
        check('the chronicle tells of towns among the trees, then of a people of gardeners', lines[0] >= 1 and lines[1] >= 1, str(lines))
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, V = A.V, N = W.nat, c = W.civs.find(c => c.id === a); V.focus = null; A.setZoom(1.6); V.cam = c.x - V.vw / 2; V.camY = null; V.dayT = .5; W.gdn.on[a] = 1;
          for (let i = Math.floor(c.l / 100); i <= Math.floor(c.r / 100); i++) if (!V.seaCell[i]) { N.f[i] = V.cap[i]; N.w[i] = 1; }
          const cv = document.querySelector('#world'), k = cv.width / cv.clientWidth, c2 = cv.getContext('2d');
          const look = g => { W.gdn.k[a] = g; c._.sig = null; A.render(); const t = V.picks.filter(p => p.kind === 'tree' && c._.sitesV.some(sx => Math.abs(sx - (p.x0 + p.x1) / 2) < 70 + c._.tierV * 22)).length;
            const [x0] = A.W2S(c.l, 0), [x1] = A.W2S(c.r, 0), L = Math.max(0, Math.round(x0)), R = Math.min(cv.clientWidth, Math.round(x1)); const d = c2.getImageData(Math.round(L * k), 0, Math.round((R - L) * k), cv.height).data;
            let gr = 0; for (let i = 0; i < d.length; i += 4) if (Math.abs(d[i] - 95) < 6 && Math.abs(d[i + 1] - 154) < 6 && Math.abs(d[i + 2] - 72) < 6) gr++; return { t, gr }; };
          const o = { off: look(0), on: look(1) }; W.gdn.k[a] = 1; return JSON.stringify(o); }''', cu))
        check('the land shows it: trees close in on the towns', r['on']['t'] > r['off']['t'] + 2, str(r))
        check('the land shows it: green roofs, terraces and garden rows', r['on']['gr'] > r['off']['gr'] * 3 + 100, str(r))
        r = await ev(r'''() => { const A = window.__aoh; A.updateUI(); return document.querySelector('#futures').innerText; }''')
        check('the Futures panel counts the peoples on the Garden path', 'on the Garden path' in r, r.replace('\n', ' | ')[:160])
        card = await ev(r'''(a) => { const A = window.__aoh, W = A.W; return A.tipBody({ civ: W.civs.find(c => c.id === a) })[1].replace(/<[^>]+>/g, ' '); }''', cu)
        check('the people’s card shows the Garden path', 'Garden path' in card and '100%' in card, card[-90:])
        r = json.loads(await ev(r'''([a, w]) => { const A = window.__aoh, W = A.W, c = W.civs.find(c => c.id === a), x = W.civs.find(c => c.id === w); const l0 = W.hist.filter(e => /leave the Garden path/.test(e.h)).length; A.startWar(x, c); A.gdnTick(1); const off = !W.gdn.on[a], k1 = A.gdnOf(c); A.gdnTick(10); const k2 = A.gdnOf(c);
          const l = W.hist.filter(e => /leave the Garden path/.test(e.h)).length - l0; W.wars = []; return JSON.stringify({ off, k1, k2, l }); }''', [dv, wa]))
        check('a war forced on them ends the Garden path, and the cities grow back', r['off'] and r['k2'] < r['k1'] and r['l'] >= 1, str(r))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; W.gdn = { on: { 5: 1 }, k: { 5: .4, 6: .2 }, said: { 5: 2 } }; const d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d)));
          const bad = JSON.parse(JSON.stringify(d)); bad.gdn = { on: { 5: 'x', 7: 3, q: 1 }, k: { 5: 4, 6: -1 }, said: { 5: 99 } }; const b2 = A.sanitizeWorld(bad);
          const old = JSON.parse(JSON.stringify(d)); delete old.gdn; const o2 = A.sanitizeWorld(old); A.loadWorld(d); const loaded = A.W.gdn; A.W.fates.ended = 'collapse'; A.riseAgain(); return JSON.stringify({ back: back.gdn, loaded, bad: b2.gdn, old: o2.gdn, cycle: A.W.gdn }); }'''))
        check('the Garden path is saved and loaded back', r['back'] == {'on': {'5': 1}, 'k': {'5': .4, '6': .2}, 'said': {'5': 2}, 'hold': 0, 'top': 0, 'end': None} and r['loaded'] == r['back'], str(r['back']))
        check('bad values are dropped or clamped; old saves have none; a new cycle starts without it', r['bad'] == {'on': {'7': 1}, 'k': {'5': 1, '6': 0}, 'said': {'5': 7}, 'hold': 0, 'top': 0, 'end': None} and r['old'] is None and r['cycle'] is None, str(r))
        print('errors:', errs[:3] if errs else 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
