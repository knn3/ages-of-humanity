# SIL-01 discovery of the ruins: when the Great Silence begins, the most advanced people's astronomers find 3-5 dead civilisations
# across the galaxy (named, a kind, how long dead), told in the chronicle (one line for the find, one per site) with a banner; once
# only; each is a crossed ring in the galaxy view that turns with the disc, right-click for its story; saved and sanitised.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))
SETUP = r'''() => { const A = window.__aoh; A.newWorld(6262); A.UI.random = false; for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1);
  const W = A.W; for (const a of [...W.fates.active]) A.endFate(a.id, 'faded'); W.fates.done = []; W.fates.ended = null; W.care = null; W.wars = []; W.sil = null;
  const cs = W.civs.filter(c => c.alive); cs.forEach((c, i) => { c.era = 11 + (i === 1 ? 2 : 0); c.machine = false; });
  W.fates.lastStart = -1e9; for (const id in W.fates.p) W.fates.p[id] = 0; scrollTo(0, 0); return cs[1].name; }'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        top = await ev(SETUP)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; A.startFate('silence', 'event'); const S = W.sil, H = W.hist, bq = A.V.banners.map(b => b.main).join(' ');
          return JSON.stringify({ n: S && S.sites.length, by: S && S.byName, main: H.filter(e => /The ruins among the stars/.test(e.h)).length, per: S ? S.sites.filter(t => H.some(e => e.h.toLowerCase().includes(t.name.toLowerCase() + ':'))).length : 0, banner: ((document.querySelector('#banner') || {}).innerText || '') + ' ' + bq }); }'''))
        check('when the Great Silence begins, astronomers find 3 to 5 dead civilisations', r['n'] is not None and 3 <= r['n'] <= 5, str(r))
        check('the most advanced people finds them; the chronicle tells the find and each site, with a banner', r['by'] == top and r['main'] == 1 and r['per'] == r['n'] and 'ruins among the stars' in r['banner'].lower(), str(r))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, s0 = JSON.stringify(W.sil.sites); A.endFate('silence', 'faded'); W.fates.done = []; W.fates.lastStart = -1e9; A.startFate('silence', 'event');
          return JSON.stringify({ same: JSON.stringify(W.sil.sites) === s0, main: W.hist.filter(e => /The ruins among the stars/.test(e.h)).length }); }'''))
        check('the ruins are found once: a later Great Silence remembers them', r['same'] and r['main'] == 1, str(r))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, S0 = W.sil, out = { n: {}, kinds: new Set(), near: 0, dup: 0, rr: [1, 0] };
          for (let i = 0; i < 300; i++) { W.sil = null; const S = A.silDiscover(); out.n[S.sites.length] = (out.n[S.sites.length] || 0) + 1; const nm = new Set();
            for (const t of S.sites) { out.kinds.add(t.kind); if (nm.has(t.name)) out.dup++; nm.add(t.name); out.rr = [Math.min(out.rr[0], t.r), Math.max(out.rr[1], t.r)];
              const dx = t.r * Math.cos(t.a) - .53 * Math.cos(Math.PI / 2), dy = t.r * Math.sin(t.a) - .53 * Math.sin(Math.PI / 2); if (Math.hypot(dx, dy) < .05) out.near++; } }
          W.sil = S0; W.hist = W.hist.slice(0, -1); return JSON.stringify({ n: out.n, kinds: out.kinds.size, near: out.near, dup: out.dup, rr: out.rr }); }'''))
        check('sites are spread across the disc, all kinds turn up, names never repeat in one find, never on top of home', set(r['n']) == {'3', '4', '5'} and r['kinds'] == 6 and r['dup'] == 0 and r['near'] == 0 and r['rr'][0] >= .18 and r['rr'][1] <= .92, str(r))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, V = A.V; V.focus = null; A.setZoom(.00002); A.render(); const p0 = V.orbPicks.filter(q => q.kind === 'deadciv').map(q => [q.x, q.y]);
          const g0 = V.galT; V.galT = (g0 || 0) + 40; A.render(); const p1 = V.orbPicks.filter(q => q.kind === 'deadciv').map(q => [q.x, q.y]); V.galT = g0; A.render();
          const moved = p0.length && p1.length ? Math.hypot(p0[0][0] - p1[0][0], p0[0][1] - p1[0][1]) : 0; A.setZoom(1); A.render(); const near = V.orbPicks.filter(q => q.kind === 'deadciv').length;
          return JSON.stringify({ shown: p0.length, n: W.sil.sites.length, moved, near }); }'''))
        check('in the galaxy view each ruin is marked, and the marks turn with the disc', r['shown'] >= 1 and r['shown'] <= r['n'] and r['moved'] > 1, str(r))
        check('the marks are not shown close to home', r['near'] == 0, str(r))
        tip = await ev(r'''() => { const A = window.__aoh, V = A.V; A.setZoom(.00002); A.render(); const q = V.orbPicks.find(q => q.kind === 'deadciv'), cv = document.querySelector('#world'), rc = cv.getBoundingClientRect();
          cv.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: rc.left + q.x, clientY: rc.top + q.y, button: 2 })); const t = document.querySelector('#tip'); return t && t.style.display !== 'none' ? t.innerText : 'hidden'; }''')
        check('right-clicking a ruin tells what is left, how long it has been dead, who found it and where', all(k in tip for k in ['What is left', 'Dead for', 'million years', 'Found', 'light years']), tip.replace('\n', ' | ')[:240])
        await ev("() => { const b = document.querySelector('#tipClose'); if (b) b.click(); window.__aoh.setZoom(1); }")
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; const d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d)));
          const bad = JSON.parse(JSON.stringify(d)); bad.sil.sites = [{ name: 'x'.repeat(50), kind: 'boom', r: 9, a: -3, dead: 'q' }, 7, ...bad.sil.sites]; const b2 = A.sanitizeWorld(bad);
          const b3 = JSON.parse(JSON.stringify(d)); b3.sil = { sites: [] }; const old = JSON.parse(JSON.stringify(d)); delete old.sil;
          A.loadWorld(d); const loaded = JSON.stringify(A.W.sil) === JSON.stringify(back.sil); A.W.fates.ended = 'collapse'; A.riseAgain();
          return JSON.stringify({ same: JSON.stringify(back.sil.sites) === JSON.stringify(W.sil.sites) && back.sil.by === W.sil.by, loaded, bad0: b2.sil.sites[0], badN: b2.sil.sites.length, empty: A.sanitizeWorld(b3).sil, old: A.sanitizeWorld(old).sil, cycle: A.W.sil }); }'''))
        check('the ruins are saved and loaded back; bad values clamped or dropped; old saves have none; a new cycle forgets them',
              r['same'] and r['loaded'] and r['bad0'] == {'name': 'x' * 30, 'kind': 'ring', 'r': 1, 'a': 0, 'dead': 100} and r['badN'] <= 5 and r['empty'] is None and r['old'] is None and r['cycle'] is None, str(r))
        print('errors:', errs[:3] if errs else 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
