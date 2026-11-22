# END-06: supervolcano and killer asteroid (countdown, deflection, impact, endings, saves)
import asyncio, json
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

# a hand-grown world: every people at an age, near its carrying capacity
GROW = r'''([seed, era]) => { const A = window.__aoh; A.newWorld(seed); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
  for (const c of A.W.civs) { c.era = era; c.tech = 5; c.pop = 1e7; c.food = 70; c.stability = 60; c.nuclear = false; }
  for (let i = 0; i < 200; i++) A.step(0.1); for (const c of A.W.civs) c.pop = c._.K * .9; A.step(0.1); }'''

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate

        # supervolcano: eruption, crater, volcanic winter, near peoples hit hardest; it can end the world or be survived
        sv = []
        for k in range(8):
            await ev(GROW, [300 + k, 6 if k % 2 else 10])
            sv.append(json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, v = W.elements.find(e => e.type === 'volcano');
              const cr0 = W.craters.length, p0 = W.civs.map(c => c.pop), ok = A.applyEvent(A.findEvent('supervolcano'), v.x);
              const near = W.civs.reduce((a, c) => Math.abs(c.x - v.x) < Math.abs(a.x - v.x) ? c : a), far = W.civs.reduce((a, c) => Math.abs(c.x - v.x) > Math.abs(a.x - v.x) ? c : a);
              const lossNear = 1 - near.pop / p0[W.civs.indexOf(near)], lossFar = 1 - far.pop / p0[W.civs.indexOf(far)];
              A.step(0.1); A.updateUI(); const meta = document.querySelector('#meta').textContent, kind = W.winter && W.winter.kind, again = A.applyEvent(A.findEvent('supervolcano'), v.x);
              for (let i = 0; i < 640 && !W.fates.ended; i++) A.step(0.1);
              return JSON.stringify({ ok, crater: W.craters.length > cr0, kind, meta: /volcanic winter/.test(meta), again, lossNear: +lossNear.toFixed(2), lossFar: +lossFar.toFixed(2), ended: W.fates.ended, settled: W.chron.some(e => /ash settles/.test(e.h)), winter: !!W.winter }); }''')))
        print('  supervolcano:', [(x['lossNear'], x['lossFar'], x['ended'] or ('survived' if x['settled'] else '?')) for x in sv])
        check('END-06 supervolcano erupts, leaves a caldera, starts a volcanic winter', all(x['ok'] and x['crater'] and x['kind'] == 'ash' and x['meta'] for x in sv))
        check('END-06 peoples near the eruption suffer most', all(x['lossNear'] >= x['lossFar'] for x in sv) and sum(x['lossNear'] for x in sv) / 8 > .4)
        check('END-06 only one dark sky at a time', all(x['again'] is False for x in sv))
        check('END-06 a supervolcano can end the world (The Ash Years)', any(x['ended'] == 'supervolcano' for x in sv), f"{sum(x['ended'] == 'supervolcano' for x in sv)} of 8")
        check('END-06 ... or be survived', any(x['settled'] for x in sv), f"{sum(x['settled'] for x in sv)} of 8")
        check('END-06 every volcanic winter ends', all(not x['winter'] for x in sv))

        # asteroid without space peoples: countdown, no deflection, impact, impact winter
        im = []
        for k in range(8):
            await ev(GROW, [400 + k, 10])
            im.append(json.loads(await ev(r'''(k) => { const A = window.__aoh, W = A.W; const cr0 = W.craters.length, p0 = W.civs.reduce((s, c) => s + c.pop, 0);
              A.startAsteroid(k < 4 ? .5 : 1); const r = W.rock, seen = r.seen, eta = r.eta; A.step(0.1); A.updateUI(); const meta = document.querySelector('#meta').textContent; A.render();
              let lo = p0; for (let i = 0; i < 1600 && W.rock; i++) { for (const c of W.civs) c.tech = Math.min(c.tech, 50); A.step(0.1); } const at = W.simTime;
              for (let i = 0; i < 1000 && !W.fates.ended && (W.winter || i < 5); i++) { A.step(0.1); lo = Math.min(lo, W.civs.filter(c => c.alive).reduce((s, c) => s + c.pop, 0)); }
              return JSON.stringify({ seen, meta: (meta.match(/asteroid: impact in [\d,]+ years/) || [''])[0], onTime: at >= eta && at - eta < 1.2, crater: W.craters.length > cr0, tries: r.tries, loss: +(1 - lo / p0).toFixed(2), ended: W.fates.ended, kind: W.chron.some(e => /strikes/.test(e.h)) }); }''', k)))
        print('  impacts (size .5 x4, 1 x4):', [(x['loss'], x['ended'] or 'survived') for x in im])
        check('END-06 asteroid found by telescopes, countdown shown', all(x['seen'] and x['meta'] for x in im), im[0]['meta'])
        check('END-06 no space peoples: no deflection, it strikes on time', all(x['tries'] == 0 and x['onTime'] and x['kind'] for x in im), str([(x['tries'], x['onTime']) for x in im]))
        check('END-06 impact leaves a crater and kills widely', all(x['crater'] for x in im) and min(x['loss'] for x in im) > .3)
        check('END-06 a big impact can end the world (The Great Impact)', any(x['ended'] == 'impact' for x in im[4:]), f"{sum(x['ended'] == 'impact' for x in im)} of 8")
        check('END-06 a smaller one can be survived', any(x['ended'] is None for x in im[:4]), f"{sum(x['ended'] is None for x in im[:4])} of 4")

        # deflection: space peoples try; more advanced peoples succeed more often; a try can fail
        de = json.loads(await ev(r'''() => { const A = window.__aoh, out = {};
          for (const era of [11, 13]) { let ok = 0, tries = 0, fails = 0; for (let k = 0; k < 20; k++) {
            A.newWorld(500 + k); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); for (const c of A.W.civs) { c.era = era; c.tech = 5; c.trait = 'Mercantile'; }
            A.startAsteroid(.75); const r = A.W.rock; for (let i = 0; i < 1500 && A.W.rock; i++) { A.step(0.1); if (A.W.fates.ended) break; }
            tries += r.tries; if (A.W.chron.some(e => /will miss the world/.test(e.h))) ok++; fails += A.W.chron.filter(e => /fails: the rock|breaks off a piece/.test(e.h)).length; }
            out[era] = { ok, tries, fails }; }
          A.newWorld(9); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); A.startAsteroid(.6); const pre = A.W.rock.seen; for (let i = 0; i < 1250 && A.W.rock && A.W.rock.eta - A.W.simTime > 5; i++) A.step(0.1); out.prehistoric = { pre, later: A.W.rock && A.W.rock.seen, sky: A.W.chron.some(e => /new star grows brighter/.test(e.h)) };
          return JSON.stringify(out); }'''))
        print('  deflection:', de)
        check('END-06 space peoples try to deflect it', de['11']['tries'] > 0 and de['13']['tries'] > 0)
        check('END-06 a deflection can succeed', de['11']['ok'] + de['13']['ok'] > 0, f"Future Age {de['11']['ok']}/20, Stellar Age {de['13']['ok']}/20")
        check('END-06 a deflection can fail', de['11']['fails'] + de['13']['fails'] > 0 and de['11']['ok'] < 20)
        check('END-06 more advanced peoples deflect more often', de['13']['ok'] > de['11']['ok'])
        check('END-06 without telescopes no one sees it until it is close', de['prehistoric']['pre'] is False and de['prehistoric']['later'] and de['prehistoric']['sky'])

        # saves mid-countdown and mid-winter, old saves, garbage
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(77); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); A.W.civs.forEach(c => c.era = 10);
          A.startAsteroid(.8); const v = A.W.elements.find(e => e.type === 'volcano'); A.applyEvent(A.findEvent('supervolcano'), v.x); for (let i = 0; i < 30; i++) A.step(0.1);
          const s1 = JSON.parse(JSON.stringify(A.serialize())), w = A.sanitizeWorld(JSON.parse(JSON.stringify(s1)));
          const same = k => JSON.stringify(s1[k]) === JSON.stringify(w[k]);
          const old = JSON.parse(JSON.stringify(s1)); delete old.rock; delete old.rockCycle; delete old.svCycle; delete old.winter.kind; delete old.winter.pop0;
          let oldOk = true; try { A.loadWorld(old); for (let i = 0; i < 30; i++) A.step(0.1); } catch (e) { oldOk = String(e); }
          const bad = JSON.parse(JSON.stringify(s1)); bad.rock = { size: 99, eta: 'x', name: { a: 1 } }; bad.winter.kind = '<b>'; bad.svCycle = -5;
          let badOk = true; try { A.loadWorld(bad); for (let i = 0; i < 30; i++) A.step(0.1); A.render(); } catch (e) { badOk = String(e); }
          return JSON.stringify({ rock: same('rock'), winter: same('winter'), cyc: same('rockCycle') && same('svCycle'), oldOk, badOk, oldKind: true, badSize: A.W.rock && A.W.rock.size }); }'''))
        check('saves: asteroid, volcanic winter and cycle marks round-trip', r['rock'] and r['winter'] and r['cyc'], str(r))
        check('saves: old saves and garbage still load', r['oldOk'] is True and r['badOk'] is True and (r['badSize'] is None or r['badSize'] <= 1), str(r))
        await ev(r'''() => { const A = window.__aoh; A.newWorld(78); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); A.W.civs.forEach(c => c.era = 10); A.startAsteroid(.8); A.W.rock.eta = A.W.simTime + 12; A.setZoom(.75); A.V.dayT = .9; A.V.cam = A.W.civs[0].x - A.V.vw / 2; A.V.camY = null; }''')
        await pg.wait_for_timeout(500); await ev("() => window.scrollTo(0, 0)"); await (await pg.query_selector('#world')).screenshot(path='end06_rock.png')
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
