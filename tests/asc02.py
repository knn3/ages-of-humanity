# ASC-02 nature reclaims: on uploaded land forests and animals come back fast (regrowth × (1 + ASC_REGROW × up), the footprint
# shrinks with the bodies left); W.asc.green climbs at the pace of the upload and keeps climbing after the future ends; trees and
# animals close in on the empty towns (no stumps), dark buildings grow over one by one; chronicle lines; building info; saved.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

SETUP = r'''() => { const A = window.__aoh; A.newWorld(6262); A.UI.random = false; for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1);
  const W = A.W; for (const a of [...W.fates.active]) A.endFate(a.id, 'faded'); W.fates.done = []; W.fates.ended = null; W.care = null; W.wars = []; W.asc = null;
  const cs = W.civs.filter(c => c.alive); cs.forEach(c => { c.era = 12; c.machine = false; c.trait = 'Curious'; c.policy = 'balance'; c.tmpPol = null; c.pop = 4e8; });
  W.fates.lastStart = -1e9; for (const id in W.fates.p) W.fates.p[id] = 0; A.startFate('ascension', 'event'); scrollTo(0, 0);
  const big = [...cs].sort((a, b) => (b.r - b.l) - (a.r - a.l)); return JSON.stringify([big[0].id, big[1].id]); }'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        a, z = json.loads(await ev(SETUP))
        # nature: the same cleared land comes back much faster where the people uploaded
        r = json.loads(await ev(r'''([a, z]) => { const A = window.__aoh, W = A.W, V = A.V, N = W.nat, ca = W.civs.find(c => c.id === a), cz = W.civs.find(c => c.id === z);
          W.asc = { up: { [a]: 1, [z]: 0 }, minds: {}, said: { [a]: 7 }, pop: {}, green: {} };
          const cells = c => { const o = []; for (let i = Math.floor(c.l / 100); i <= Math.floor(c.r / 100); i++) if (!V.seaCell[i]) o.push(i); return o; };
          const A1 = cells(ca), Z1 = cells(cz); for (const i of [...A1, ...Z1]) { N.f[i] = .08 * V.cap[i]; N.w[i] = .1; }
          const m = (cs, k) => cs.reduce((s, i) => s + (k === 'f' ? N.f[i] / Math.max(.05, V.cap[i]) : N.w[i]), 0) / cs.length;
          for (let t = 0; t < 80; t++) { W.wars = []; A.natureTick(1); }
          return JSON.stringify({ fa: m(A1, 'f'), fz: m(Z1, 'f'), wa: m(A1, 'w'), wz: m(Z1, 'w') }); }''', [a, z]))
        check('forests grow back far faster on uploaded land than on a living people’s land', r['fa'] > .6 and r['fa'] > 2 * r['fz'], f"{r['fa']:.2f} vs {r['fz']:.2f}")
        check('wild animals come back too', r['wa'] > .55 and r['wa'] > 1.5 * r['wz'], f"{r['wa']:.2f} vs {r['wz']:.2f}")
        T = (await ev("() => window.__aoh.ASC"))['ASC_GREEN']
        # green climbs at the pace of the upload; lines at 30% and 80%
        r = json.loads(await ev(r'''([a, z]) => { const A = window.__aoh, W = A.W; W.asc.up[a] = .5; W.asc.green = {}; for (let i = 0; i < 60; i++) A.ascGreenTick(1); const g1 = A.ascGreen(W.civs.find(c => c.id === a));
          W.asc.up[a] = 1; for (let i = 0; i < 200; i++) A.ascGreenTick(1); const g2 = A.ascGreen(W.civs.find(c => c.id === a)), cnt = re => W.hist.filter(e => re.test(e.h)).length;
          return JSON.stringify({ g1, g2, gz: A.ascGreen(W.civs.find(c => c.id === z)), sap: cnt(/Saplings push up through the empty streets/), sink: cnt(/are sinking under forest/) }); }''', [a, z]))
        check('the green climbs at the pace of the upload (half uploaded, half as fast); none where no one uploaded', abs(r['g1'] - 30 / T) < .01 and r['g2'] == 1 and r['gz'] == 0, str(r))
        check('the chronicle tells of saplings in the streets, then of cities sinking under forest (once each)', r['sap'] == 1 and r['sink'] == 1, str(r))
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W; W.asc.green[a] = .4; A.endFate('ascension', 'faded'); const on = A.ascOn(); A.ascTick(10); return JSON.stringify({ on, g: W.asc.green[a] }); }''', a))
        check('nature keeps reclaiming after the future has ended', not r['on'] and r['g'] > .4 + 9 / T, str(r))
        # dark buildings grow over one by one, the same ones first; lit buildings never
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, V = A.V, c0 = W.civs.find(c => c.id === a); V.focus = null; A.setZoom(1.6); V.cam = c0.x - V.vw / 2; A.render(); const c = c0, items = c._.items.filter(b => b.t !== 'field');
          const ov = (u, g) => { W.asc.up[a] = u; W.asc.green[a] = g; return items.map(b => A.ascOver(c, b)); };
          const o3 = ov(1, .3), o7 = ov(1, .7), o0 = ov(1, 0), lit = ov(.4, 1), litOn = items.filter((b, i) => !A.ascDark(c, b)).length;
          return JSON.stringify({ n: items.length, s3: o3.filter(v => v > 0).length, s7: o7.filter(v => v > 0).length, f7: o7.filter(v => v >= 1).length, mono: o3.every((v, i) => v <= o7[i]), zero: o0.every(v => v === 0), litOver: items.filter((b, i) => !A.ascDark(c, b) && lit[i] > 0).length, litOn }); }''', a))
        check('dark buildings grow over one by one as the green climbs, never shrinking back', r['zero'] and r['mono'] and 0 < r['s3'] < r['s7'] and r['f7'] > 0, str(r))
        check('buildings still lit are never overgrown', r['litOn'] > 0 and r['litOver'] == 0, str(r))
        # on screen: trees and animals close in on the empty town, no stumps
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, V = A.V, N = W.nat, c = W.civs.find(c => c.id === a); V.focus = null; A.setZoom(1.6); V.cam = c.x - V.vw / 2; V.camY = null; V.dayT = .5;
          for (let i = Math.floor(c.l / 100); i <= Math.floor(c.r / 100); i++) if (!V.seaCell[i]) { N.f[i] = V.cap[i]; N.w[i] = 1; }
          const near = (kind, g) => { W.asc.up[a] = 1; W.asc.green[a] = g; A.render(); return V.picks.filter(p => p.kind === kind && c._.sitesV.some(sx => Math.abs(sx - (p.x0 + p.x1) / 2) < 70 + c._.tierV * 22)).length; };
          return JSON.stringify({ t0: near('tree', 0), t1: near('tree', 1), a0: near('animal', 0), a1: near('animal', 1) }); }''', a))
        check('trees grow into the empty town', r['t1'] > r['t0'] + 3, str(r))
        check('animals walk into it', r['a1'] > r['a0'], str(r))
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, V = A.V, c = W.civs.find(c => c.id === a); W.asc.up[a] = .15; W.asc.green[a] = 1; A.render(); const t = V.picks.filter(p => p.kind === 'tree' && c._.sitesV.some(sx => Math.abs(sx - (p.x0 + p.x1) / 2) < 70 + c._.tierV * 22)).length, wild = A.ascWild(c); W.asc.up[a] = 1; return JSON.stringify({ wild, t }); }''', a))
        check('a mostly living town stays cleared, however long ago its few left', r['wild'] == .15 and r['t'] <= 2, str(r))
        # building info
        tip = await ev(r'''(a) => { const A = window.__aoh, W = A.W, c = W.civs.find(c => c.id === a); W.asc.green[a] = 1; const b = c._.items.find(b => b.t !== 'field' && A.ascDark(c, b)); return A.tipBody({ b, civ: c })[1].replace(/<[^>]+>/g, ' '); }''', a)
        check('right-click info on an empty building says its people uploaded and how overgrown it is', 'Empty' in tip and 'Overgrown' in tip, tip[-120:])
        # saving, garbage, old saves
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; W.asc = { up: { 5: 1 }, minds: { 5: 3e8 }, said: { 5: 55 }, pop: {}, green: { 5: .42 } }; const d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d)));
          const bad = JSON.parse(JSON.stringify(d)); bad.asc.green = { 5: 7, x: .3, 6: 'q' }; const b2 = A.sanitizeWorld(bad); const old = JSON.parse(JSON.stringify(d)); delete old.asc.green; const o2 = A.sanitizeWorld(old);
          return JSON.stringify({ back: back.asc, bad: b2.asc.green, old: o2.asc.green }); }'''))
        check('the green is saved and loaded back; bad values clamped; saves from before have none', r['back']['green'] == {'5': .42} and r['back']['said'] == {'5': 55} and r['bad'] == {'5': 1} and r['old'] == {}, str(r))
        print('errors:', errs[:3] if errs else 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
