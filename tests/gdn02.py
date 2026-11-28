# GDN-02 the Garden ending: every living people far along the Garden path, no wars, forests and wild animals thriving, held for
# GDN_HOLD sim s, ends history in peace ('garden', a goal) with its own epilogue rows and story; the Garden future no longer ends with
# it on its drive alone (ready hook) and fades instead; the panel shows how many peoples are on the path; saved and sanitised.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))
SETUP = open(pathlib.Path(__file__).with_name('gdn01.py')).read().split("SETUP = r'''")[1].split("'''")[0]
ALL = r'''() => { const A = window.__aoh, W = A.W, V = A.V; W.wars = []; W.gdn = { on: {}, k: {}, said: {}, hold: 0, top: 4e9, end: null }; for (const c of W.civs.filter(c => c.alive)) { W.gdn.on[c.id] = 1; W.gdn.k[c.id] = 1; c.machine = false; }
  for (let i = 0; i < W.nat.f.length; i++) if (!V.seaCell[i]) { W.nat.f[i] = V.cap[i]; W.nat.w[i] = .95; } A.natureTick(.01); return JSON.stringify(V.planet); }'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        ids = {t: i for i, t in json.loads(await ev(SETUP))}
        pl = json.loads(await ev(ALL))
        r = json.loads(await ev(r'''(w) => { const A = window.__aoh, W = A.W, V = A.V, c = W.civs.find(c => c.id === w), o = { all: A.gdnAll() };
          W.gdn.on[w] = 0; o.off = A.gdnAll(); W.gdn.on[w] = 1; W.gdn.k[w] = .5; o.young = A.gdnAll(); W.gdn.k[w] = 1;
          const x = W.civs.find(x => x.alive && x !== c); W.wars = [{ a: c.id, b: x.id, t: 0, adv: 0 }]; o.war = A.gdnAll(); W.wars = [];
          const f = V.planet.forest; V.planet.forest = .5; o.bare = A.gdnAll(); V.planet.forest = f; const wl = V.planet.wild; V.planet.wild = .3; o.empty = A.gdnAll(); V.planet.wild = wl; return JSON.stringify(o); }''', ids['Warlike']))
        check('the Garden is complete only when every living people is far along the path, at peace, with forests and animals thriving', r['all'] and not (r['off'] or r['young'] or r['war'] or r['bare'] or r['empty']), str(r) + ' ' + str(pl))
        # the Garden future no longer ends with the Garden ending on its drive alone; it fades
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, F = W.fates; A.startFate('garden', 'event'); const a = F.active.find(a => a.id === 'garden'), sp = A.FATES.garden.span; W.gdn.on = {}; W.gdn.k = {};
          a.t0 = W.simTime - sp - 5; A.fateTick(1); const mid = { ended: F.ended, active: F.active.some(a => a.id === 'garden'), ready: A.FATES.garden.ready() };
          a.t0 = W.simTime - 2 * sp - 5; A.fateTick(1); const h = F.hist.filter(e => e.id === 'garden').pop(); return JSON.stringify({ mid, ended: F.ended, out: h && h.out }); }'''))
        check('the Garden future cannot end with the Garden ending before the world is ready, and fades in time', r['mid']['ended'] is None and r['mid']['active'] and not r['mid']['ready'] and r['ended'] is None and r['out'] == 'faded', str(r))
        await ev(r'''() => { const A = window.__aoh, W = A.W; W.fates.done = []; W.fates.lastStart = -1e9; A.startFate('garden', 'event'); }''')
        await ev(ALL)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; for (let i = 0; i < 20; i++) A.gdnEndTick(1); const h1 = W.gdn.hold, l = W.hist.filter(e => /The world holds its breath/.test(e.h)).length;
          A.updateUI(); const clock = document.querySelector('#futures').innerText; const c = W.civs.find(c => c.alive); W.gdn.on[c.id] = 0; A.gdnEndTick(1); const h2 = W.gdn.hold; W.gdn.on[c.id] = 1;
          return JSON.stringify({ h1, l, h2, ended: W.fates.ended, clock }); }'''))
        check('the world holds its breath (told once); a people that leaves the path breaks the wait', r['h1'] == 20 and r['l'] == 1 and r['h2'] == 0 and r['ended'] is None, str({k: v for k, v in r.items() if k != 'clock'}))
        check('the Futures panel shows how many peoples are on the path, the state of nature, and the waiting', 'of 4 peoples on the Garden path' in r['clock'] and 'nature' in r['clock'] and 'holds its breath' in r['clock'], r['clock'].replace('\n', ' | ')[:200])
        T = (await ev("() => window.__aoh.GDN"))['GDN_HOLD']
        r = json.loads(await ev(r'''(T) => { const A = window.__aoh, W = A.W, F = W.fates; for (let i = 0; i < T - 1; i++) A.gdnEndTick(1); const before = F.ended; A.gdnEndTick(1);
          const h = F.hist.filter(e => e.id === 'garden').pop(); return JSON.stringify({ before, ended: F.ended, kind: A.ENDINGS.garden.kind, out: h && h.out, end: W.gdn.end, wars: W.wars.length }); }''', T))
        check('held long enough, history ends in the Garden (a goal), through the Garden future', r['before'] is None and r['ended'] == 'garden' and r['kind'] == 'goal' and r['out'] == 'ending' and r['wars'] == 0, str({k: v for k, v in r.items() if k != 'end'}))
        e = r['end']
        check('the ending records the gardeners, the forests, the animals, the people against the peak, and the years of peace', e and len(e['peoples']) == 4 and e['f'] >= .7 and e['w'] >= .6 and e['peak'] >= 4e9 and e['peace'] >= 0, str(e))
        txt = await ev(r'''() => { const A = window.__aoh; A.showEpilogue(); const m = document.querySelector('#modal'); return m ? m.innerText : ''; }''')
        check('its own epilogue: the Garden World, the gardeners, forests, animals, people, years of peace, and its story', all(k in txt for k in ['The Garden World', 'Gardeners', 'Forests', 'Wild animals', 'down from', 'At peace for', 'under the trees']), txt.replace('\n', ' | ')[:260])
        await ev("() => { const b = document.querySelector('#modal [data-close]'); if (b) b.click(); }")
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; const d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d)));
          const bad = JSON.parse(JSON.stringify(d)); bad.gdn.hold = -5; bad.gdn.end = { y: 'x', f: 9, w: -1, pop: 'q', peoples: [1, 'A'.repeat(40)] }; const b2 = A.sanitizeWorld(bad); const b3 = JSON.parse(JSON.stringify(d)); b3.gdn.end = 7;
          const old = JSON.parse(JSON.stringify(d)); delete old.gdn.hold; delete old.gdn.end; delete old.gdn.top; const o2 = A.sanitizeWorld(old);
          return JSON.stringify({ same: JSON.stringify(back.gdn.end) === JSON.stringify(W.gdn.end), hold: back.gdn.hold, bad: b2.gdn, b3: A.sanitizeWorld(b3).gdn.end, old: [o2.gdn.hold, o2.gdn.end, o2.gdn.top], ended: back.fates.ended }); }'''))
        check('the ending is saved and loaded back; bad values clamped; old saves have none', r['same'] and r['ended'] == 'garden' and r['bad']['hold'] == 0 and r['bad']['end']['f'] == 1 and r['bad']['end']['w'] == 0 and r['bad']['end']['peoples'] == ['1', 'A' * 20] and r['b3'] is None and r['old'] == [0, None, 0], str(r))
        r = json.loads(await ev(r'''(w) => { const A = window.__aoh, W = A.W, R = Math.random, c = W.civs.find(c => c.id === w); W.fates.ended = null; W.wars = []; c.policy = 'protect'; c.stability = 70; A.natureTick(.01);
          const others = W.civs.filter(x => x.alive && x !== c); W.gdn.on = {}; W.gdn.k = {}; W.gdn.hold = 0; const lone = []; for (const x of others) { W.gdn.on[x.id] = 1; W.gdn.k[x.id] = .1; }
          W.fates.lastStart = -1e9; A.startFate('garden', 'event'); Math.random = () => .0099; A.gdnTick(1); const withFate = !!W.gdn.on[w]; delete W.gdn.on[w]; for (const a of [...W.fates.active]) A.endFate(a.id, 'faded'); A.gdnTick(1); const noFate = !!W.gdn.on[w];
          for (const x of others) delete W.gdn.on[x.id]; A.startFate('garden', 'event'); A.gdnTick(1); const alone = !!W.gdn.on[w]; Math.random = R; return JSON.stringify({ withFate, noFate, alone }); }''', ids['Warlike']))
        check('the example of the neighbours: while the Garden future runs, even a Warlike people may follow once most are gardeners, never alone', r['withFate'] and not r['noFate'] and not r['alone'], str(r))
        print('errors:', errs[:3] if errs else 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
