# END-07: seed vaults and libraries change where the next cycle starts
import asyncio, json
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

# four peoples at an age; civ 0 gets a library, 1 a seed vault, 2 both, 3 nothing; then the world falls
FALL = r'''(era) => { const A = window.__aoh; A.newWorld(61); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
  A.W.elements = A.W.elements.filter(e => e.type !== 'library' && e.type !== 'seedvault');
  const cs = A.W.civs; for (const c of cs) { c.era = era; c.tech = 10; c.l = c.x - 300; c.r = c.x + 300; }
  const put = (c, t) => { for (let d = 20; d < 280; d += 15) for (const s of [1, -1]) { const x = c.x + s * d; const n = A.W.elements.length; A.placeElement(t, x); if (A.W.elements.length > n) return true; } return false; };
  const placed = [put(cs[0], 'library'), put(cs[1], 'seedvault'), put(cs[2], 'library'), put(cs[2], 'seedvault')];
  A.reachEnding('collapse'); A.riseAgain(); A.updateUI();
  return JSON.stringify({ placed, eras: cs.map(c => c.era), food: cs.map(c => Math.round(c.food)), tech: cs.map(c => Math.round(c.tech)), said: A.W.chron.filter(e => /begin again in the/.test(e.h)).length, cycle: A.W.fates.cycle }); }'''

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate

        r = await ev("() => ['seedvault', 'library'].map(t => !!document.querySelector(`#tab-elements [data-tool=\"el:${t}\"]`) && !!document.querySelector(`#tab-elements [data-info=\"el:${t}\"]`)).join(',')")
        check('END-07 Seed Vault and Great Library in the toolbox with an i', r == 'true,true', r)

        f = json.loads(await ev(FALL, 11))
        print('  Future Age fall:', f)
        check('END-07 both can be placed', all(f['placed']))
        check('END-07 no keepers: Stone Age as before', f['eras'][3] == 1, str(f['eras']))
        check('END-07 a library keeps knowledge: a later age', f['eras'][0] > f['eras'][3] and f['tech'][0] > f['tech'][3], str(f['eras']))
        check('END-07 a seed vault keeps crops: farmers with more food', f['eras'][1] >= 1 and f['food'][1] > f['food'][3], str(f['food']))
        check('END-07 both: the furthest start', f['eras'][2] > f['eras'][0] >= f['eras'][1], str(f['eras']))
        check('END-07 the chronicle tells how each began again', f['said'] == 3)
        g = json.loads(await ev(FALL, 5))
        print('  Classical Age fall:', g)
        check('END-07 an early people with a vault farms instead of hunting', g['eras'][3] == 0 and g['eras'][1] == 1, str(g['eras']))

        # the start follows the age reached when the world fell, not the age after the losses of the fall
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(62); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const c = A.W.civs[0]; c.era = 14; c.tech = 10; c.l = c.x - 300; c.r = c.x + 300; A.placeElement('library', c.x + 40); A.reachEnding('collapse'); const mid = c.era, fe = c.fallEra;
          const s1 = JSON.parse(JSON.stringify(A.serialize())), w = A.sanitizeWorld(s1); A.loadWorld(s1); const c2 = A.W.civs[0]; A.riseAgain(); return JSON.stringify({ mid, fe, saved: w.civs[0].fallEra, era: c2.era, after: c2.fallEra }); }'''))
        check('END-07 the age at the fall is remembered (and saved)', r['fe'] == 14 and r['saved'] == 14 and r['mid'] < 14, str(r))
        check('END-07 a Galactic library restarts in the Iron Age', r['era'] == 4 and r['after'] is None, str(r))

        # peoples build them on their own
        r = json.loads(await ev(r'''() => { const A = window.__aoh, out = { lib: 0, vault: 0, vaultDanger: 0 };
          for (let k = 0; k < 6; k++) { A.newWorld(700 + k); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); A.W.elements = A.W.elements.filter(e => e.type !== 'library' && e.type !== 'seedvault');
            for (const c of A.W.civs) { c.era = 6; c.culture = 80; } for (let i = 0; i < 3000; i++) { for (const c of A.W.civs) { c.culture = 80; c.tech = Math.min(c.tech, 50); } A.step(0.1); } out.lib += A.W.elements.filter(e => e.type === 'library').length; }
          for (const danger of [false, true]) for (let k = 0; k < 6; k++) { A.newWorld(800 + k); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); A.W.elements = A.W.elements.filter(e => e.type !== 'seedvault');
            for (const c of A.W.civs) c.era = 10; if (danger) A.startPandemic(A.W.civs[0]); for (let i = 0; i < 1500; i++) { for (const c of A.W.civs) c.tech = Math.min(c.tech, 50); A.step(0.1); } const n = A.W.elements.filter(e => e.type === 'seedvault').length; if (danger) out.vaultDanger += n; else out.vault += n; }
          out.said = A.W.chron.some(e => /seed vault into the frozen rock|vault deep in the holy mountain/.test(e.h)); return JSON.stringify(out); }'''))
        print('  built on their own:', r)
        check('END-07 learned peoples found libraries on their own', r['lib'] >= 3, str(r['lib']))
        check('END-07 seed vaults are built, far more when danger looms', r['vaultDanger'] > r['vault'] and r['vaultDanger'] >= 3 and r['said'], str(r))

        # epilogue lists what was kept; right click on the element; drawn
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(63); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const c = A.W.civs[0]; c.era = 10; const L = A.V.lands.find(L => c.x >= L.l && c.x <= L.r), lx = Math.round(L.l + 140); A.placeElement('library', lx); A.placeElement('seedvault', lx + 70);
          A.setZoom(1.6); A.V.cam = lx - A.V.vw / 2; A.V.camY = null; A.V.dayT = .42; A.render(); A.render();
          const e = A.W.elements.find(e => e.type === 'library'); let t = null, seen = []; for (const dy of [12, 16, 20, 24]) for (const dx of [-10, 0, 10]) { const s = A.W2S(e.x + dx, A.gy(e.x + dx) - dy), q = A.tipTarget(s[0], s[1]); seen.push(q ? Object.keys(q).filter(k => k !== 'key').join('') : '-'); if (q && q.el && q.el.type === 'library' && !t) t = q; }
          c.l = Math.min(c.l, lx - 60); A.reachEnding('collapse'); A.showEpilogue(); const card = document.querySelector('#dialog').innerText; document.querySelector('#dialog [data-close]').click();
          return JSON.stringify({ seen: seen.join(','), tip: t && t.el ? t.el.type : 'none', kept: /Kept safe/.test(card) && /library/.test(card) }); }'''))
        check('END-07 right click on a library shows its info', r['tip'] == 'library', r['tip'] + ' ' + r['seen'])
        check('END-07 the epilogue lists what was kept safe', r['kept'])
        await ev(r'''() => { const A = window.__aoh; A.riseAgain(); const c = A.W.civs[0]; A.V.banners.length = 0; A.setZoom(1.8); A.V.cam = c.x - A.V.vw / 2; A.V.camY = null; A.V.dayT = .9; }''')
        await pg.wait_for_timeout(600); await ev("() => window.scrollTo(0, 0)"); await (await pg.query_selector('#world')).screenshot(path='end07_keepers.png')
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
