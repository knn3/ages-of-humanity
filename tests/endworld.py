# End of the world (END-01..05): new cycles, ruins, nuclear winter, runaway warming, engineered plague
import asyncio, json
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}

# a world grown by hand to a given age, every people alive
SETUP = r'''(era) => { const A = window.__aoh; A.newWorld(777); for (let i = 0; i < 40; i++) A.step(0.1);
  for (const c of A.W.civs) { c.era = era; c.tech = 10; c.pop = 2e8; c.food = 70; c.stability = 60; c.nuclear = era >= 9; c.bunker = 0; }
  A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); return A.W.civs.filter(c => c.alive).length; }'''
RUN = r'''(sec) => { const A = window.__aoh; for (let i = 0; i < sec * 10; i++) A.step(0.1); }'''
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate

        # END-01 collapse -> the survivors begin again on their own; the counter shows the cycle
        await ev(SETUP, 10)
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.reachEnding('collapse'); const ra = A.W.fates.riseAt;
          for (let i = 0; i < 460; i++) A.step(0.1); A.render(); A.updateUI(); return JSON.stringify({ ra: ra != null, cycle: A.W.fates.cycle, ended: A.W.fates.ended, eras: A.W.civs.filter(c => c.alive).map(c => c.era), bomb: A.W.civs.some(c => c.alive && c.nuclear), era: document.querySelector('#eraName').textContent, ruins: A.W.ruins.length, kinds: [...new Set(A.W.ruins.map(r => r.k))].join(',') }); }'''))
        check('END-01 doom ending schedules a new cycle', r['ra'])
        check('END-01 survivors restart in the Prehistoric/Stone Age, second cycle', r['cycle'] == 2 and r['ended'] is None and all(e <= 1 for e in r['eras']), str(r['eras']))
        check('END-01 cycle counter on screen', 'Second rise' in r['era'], r['era'])
        check('END-01 nobody keeps the bomb into the new cycle', not r['bomb'])
        check('END-02 the old cities leave ruins', r['ruins'] >= 8, f"{r['ruins']} ruins: {r['kinds']}")
        check('END-02 modern ruins include towers and a highway', 'tower' in r['kinds'] and 'road' in r['kinds'], r['kinds'])
        # dead world: no survivors, no new cycle
        await ev(SETUP, 10)
        r = await ev(r'''() => { const A = window.__aoh; for (const c of A.W.civs) c.alive = false; A.reachEnding('collapse'); for (let i = 0; i < 460; i++) A.step(0.1); return A.W.fates.cycle + '|' + A.W.fates.ended; }''')
        check('END-01 no survivors: the world stays dead', r == '1|collapse', r)

        # END-02 ruins speed the early ages and grow over
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(31); A.UI.random = false; for (let i = 0; i < 30; i++) A.step(0.1);
          const c = A.W.civs[0]; c.era = 1; const before = A.ruinBonus(c);
          A.W.ruins.push({ x: Math.round(c.x), w: 30, h: 120, era: 10, k: 'tower', t0: A.W.simTime, by: 'Old' }, { x: Math.round(c.x) + 60, w: 300, h: 6, era: 10, k: 'road', t0: A.W.simTime, by: 'Old' });
          const fresh = A.ruinBonus(c); A.W.ruins.forEach(r => r.t0 -= 2000); const old = A.ruinBonus(c);
          A.step(0.1); const said = A.W.chron.some(e => /ruins of the old world/.test(e.h));
          return JSON.stringify({ before, fresh, old, said, mult: c._.mult }); }'''))
        check('END-02 scavenging speeds a younger people', r['before'] == 1 and r['fresh'] > 1.4, f"x{r['fresh']:.2f}")
        check('END-02 the bonus fades as nature covers the ruins', 1 < r['old'] < r['fresh'], f"x{r['old']:.2f}")
        check('END-02 chronicle tells the scavenging', r['said'])
        # visible on the strip (right click info) and on the globe
        r = json.loads(await ev(r'''() => { const A = window.__aoh; const c = A.W.civs[0]; A.W.ruins.forEach(r => r.t0 = A.W.simTime - 300);
          A.setZoom(1.6); A.V.cam = c.x - A.V.vw / 2; A.V.camY = null; A.render(); A.render();
          const pk = A.V.picks.filter(p => p.kind === 'ruin'); let tip = '';
          if (pk.length) { const p = pk[0], s = A.W2S((p.x0 + p.x1) / 2, (p.y0 * .3 + p.y1 * .7)); const t = A.tipTarget(s[0], s[1]); tip = t && t.p ? t.p.kind : (t ? 'other' : 'none'); }
          A.setZoom(.05); A.render(); A.render(); return JSON.stringify({ picks: pk.length, tip }); }'''))
        check('END-02 ruins drawn and right-clickable on the strip', r['picks'] >= 1 and r['tip'] == 'ruin', str(r))
        await pg.wait_for_timeout(200); await pg.screenshot(path='endworld_globe.png')

        # END-03 a full nuclear exchange without bunkers ends the cycle
        await ev(SETUP, 10)
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.nuclearWar('order'); const w = !!(A.W.winter && A.W.winter.full), k = A.winterK();
          for (let i = 0; i < 30; i++) A.step(0.1); A.render(); A.updateUI(); const k2 = A.winterK(), chip = document.querySelector('#meta').textContent;
          for (let i = 0; i < 700 && !A.W.fates.ended; i++) A.step(0.1);
          return JSON.stringify({ w, k2, chip, ended: A.W.fates.ended, alive: A.W.civs.filter(c => c.alive).length }); }'''))
        check('END-03 full exchange starts a nuclear winter', r['w'] and r['k2'] > .5 and 'nuclear winter' in r['chip'], r['chip'][-60:])
        check('END-03 too few bunkers: The Long Winter ends the cycle', r['ended'] == 'nuclearwinter', f"ended {r['ended']}, {r['alive']} alive")
        # with bunkers the world comes through
        await ev(SETUP, 10)
        r = json.loads(await ev(r'''() => { const A = window.__aoh; for (const c of A.W.civs) c.bunker = 1; const p0 = A.W.civs.map(c => c.pop);
          A.nuclearWar('order'); for (let i = 0; i < 760; i++) A.step(0.1);
          return JSON.stringify({ ended: A.W.fates.ended, winter: A.W.winter, alive: A.W.civs.filter(c => c.alive).length, lift: A.W.chron.some(e => /winter lifts/.test(e.h)) }); }'''))
        check('END-03 bunkers carry the world through', r['ended'] is None and r['lift'] and r['alive'] == 4, str(r))
        # bunkers are dug naturally when the doomsday clock is close
        await ev(SETUP, 10)
        r = json.loads(await ev(r'''() => { const A = window.__aoh; const cs = A.W.civs; cs[0].trait = 'Warlike'; A.W.wars.push({ a: cs[0].id, b: cs[1].id, t: 0, adv: 0 }, { a: cs[2].id, b: cs[3].id, t: 0, adv: 0 });
          for (const c of cs) for (const o of cs) if (c !== o) A.W.rel[c.id < o.id ? c.id + '-' + o.id : o.id + '-' + c.id] = -80;
          for (let i = 0; i < 500; i++) { A.W.wars.forEach(w => w.adv = 0); A.step(0.1); } A.render(); A.updateUI();
          return JSON.stringify({ b: cs.map(c => +c.bunker.toFixed(2)), said: A.W.chron.some(e => /bunkers under|deep vaults/.test(e.h)), card: [...document.querySelectorAll('#civs .chip')].some(x => /Bunkers|Deep vaults/.test(x.textContent)) }); }'''))
        check('END-03 peoples dig bunkers when the clock is near midnight', max(r['b']) >= .5 and r['said'] and r['card'], str(r['b']))
        # one nuclear power: a short smoke, no collapse
        await ev(SETUP, 10)
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.W.civs.forEach((c, i) => c.nuclear = i === 0); A.nuclearWar('order'); const full = A.W.winter.full; for (let i = 0; i < 400; i++) A.step(0.1); return JSON.stringify({ full, ended: A.W.fates.ended, winter: A.W.winter }); }'''))
        check('END-03 a one-sided strike only darkens the sky', r['full'] is False and r['ended'] is None and r['winter'] is None, str(r))

        # END-04 runaway warming: tipping point, rising seas, drowned coasts, stopped by dimming the Sun
        await ev(SETUP, 10)
        r = json.loads(await ev(r'''() => { const A = window.__aoh; const s0 = A.seaY(); A.W.pollution = 70; A.W.tempShift = 2.5;
          for (let i = 0; i < 140; i++) { A.W.pollution = Math.max(A.W.pollution, 60); A.step(0.1); } const on = A.W.hot.on; A.updateUI(); const meta = document.querySelector('#meta').textContent;
          for (let i = 0; i < 2200; i++) { A.W.pollution = Math.max(A.W.pollution, 60); A.step(0.1); } A.render(); A.updateUI();
          const dr = A.W.civs.filter(c => c.alive).map(c => +(c._.drown || 0).toFixed(2));
          const r1 = { on, rise: A.W.seaRise, ds: s0 - A.seaY(), dr, meta, meta2: document.querySelector('#meta').textContent, said: A.W.chron.some(e => /sea swallows/.test(e.h)), refugees: A.W.chron.some(e => /drowned coasts/.test(e.h)), temp: A.temp() };
          A.W.civs.forEach(c => c.era = 12); A.startFate('geo', 'event'); A.step(1.1); A.step(1.1); r1.stopped = !A.W.hot.on; const s1 = A.W.seaRise; for (let i = 0; i < 300; i++) A.step(0.1); r1.recede = A.W.seaRise < s1; return JSON.stringify(r1); }'''))
        check('END-04 heat past the tipping point feeds itself', r['on'] and r['temp'] > 3, f"temp {r['temp']:.1f}")
        check('END-04 the seas rise and drown the coasts', r['rise'] > 20 and r['ds'] > 20 and max(r['dr']) > .05 and r['said'], f"rise {r['rise']:.0f}px, drowned {r['dr']}")
        check('END-04 migrations from the drowned coasts', r['refugees'])
        check('END-04 shown in the world line', 'runaway warming' in r['meta'] and 'seas +' in r['meta2'], r['meta'][-40:] + ' / ' + r['meta2'][-30:])
        check('END-04 dimming the Sun stops it, the seas slowly recede', r['stopped'] and r['recede'])
        await ev(r'''() => { const A = window.__aoh; A.W.seaRise = 30; A.W.hot.on = true; A.endTick(1); const c = A.W.civs[1]; A.setZoom(.7); A.V.cam = c.l - 200; A.V.camY = null; A.render(); }''')
        await pg.wait_for_timeout(150); await pg.screenshot(path='endworld_sea.png')
        await ev(r'''() => { const A = window.__aoh; A.setZoom(.05); A.render(); A.render(); }''')
        await pg.wait_for_timeout(150); await pg.screenshot(path='endworld_sea_globe.png')

        # END-05 the engineered plague spreads along contacts; closed borders help; it can end the cycle
        out = json.loads(await ev(r'''() => { const A = window.__aoh, res = [];
          for (const mode of ['open', 'closed']) for (let k = 0; k < 6; k++) {
            A.newWorld(900 + k); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
            for (const c of A.W.civs) { c.era = 11; c.tech = 5; c.pop = 3e8; c.food = 70; c.stability = 60; c.trait = mode === 'open' ? 'Mercantile' : 'Devout'; }
            for (let i = 0; i < 300; i++) A.step(0.1); for (const c of A.W.civs) c.pop = c._.K * .95; A.step(0.1);
            const p0 = A.W.civs.reduce((s, c) => s + c.pop, 0), src = A.W.civs[0]; A.startPandemic(src);
            if (mode === 'open') A.W.tradeUntil = A.W.simTime + 200; else for (const c of A.W.civs) if (c !== src) c.closed = A.W.simTime + 200;
            let hit = 0, lo = p0; for (let i = 0; i < 1800 && A.W.pandemic; i++) { A.step(0.1); hit = Math.max(hit, Object.keys(A.W.pandemic ? A.W.pandemic.inf : {}).length + (A.W.pandemic ? A.W.pandemic.rec.length : 0)); lo = Math.min(lo, A.W.civs.filter(c => c.alive).reduce((s, c) => s + c.pop, 0)); }
            res.push({ mode, hit, lost: +(1 - lo / p0).toFixed(2), ended: A.W.fates.ended, over: !A.W.pandemic }); }
          return JSON.stringify(res); }'''))
        op = [x for x in out if x['mode'] == 'open']; cl = [x for x in out if x['mode'] == 'closed']
        avg = lambda a, k: sum(x[k] for x in a) / len(a)
        print('  open  :', [(x['hit'], x['lost'], x['ended']) for x in op]); print('  closed:', [(x['hit'], x['lost'], x['ended']) for x in cl])
        check('END-05 spreads along trade and contact', avg(op, 'hit') >= 3, f"{avg(op, 'hit'):.1f} peoples reached")
        check('END-05 far deadlier than natural plague', avg(op, 'lost') > .45, f"{avg(op, 'lost'):.0%} of humanity at the worst")
        check('END-05 closed borders fare better', avg(cl, 'lost') < avg(op, 'lost') - .15 and avg(cl, 'hit') < avg(op, 'hit'), f"closed lose {avg(cl, 'lost'):.0%}")
        check('END-05 can end a cycle (The Empty Cities)', any(x['ended'] == 'plague' for x in out), str(sum(x['ended'] == 'plague' for x in out)) + ' of 12')
        check('END-05 every outbreak resolves', all(x['over'] for x in out))
        r = await ev(r'''() => { const A = window.__aoh; A.newWorld(5); for (let i = 0; i < 20; i++) A.step(0.1); const ev = A.findEvent('bioplague'); const lock = A.applyEvent(ev, A.W.civs[0].x); A.W.civs.forEach(c => c.era = 11); const ok = A.applyEvent(ev, A.W.civs[0].x); const again = A.applyEvent(ev, A.W.civs[0].x); return [lock, ok, again].join(','); }''')
        check('END-05 event locked before the Future Age, once at a time', r == 'false,true,false', r)

        # saves: every new structure round-trips; old saves load
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(41); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          for (const c of A.W.civs) { c.era = 11; c.nuclear = true; c.bunker = .7; }
          A.startPandemic(A.W.civs[1]); A.W.civs[2].closed = A.W.simTime + 50; A.leaveRuins(A.W.civs[0], 4); A.startWinter(true); A.W.hot.on = true; A.W.seaRise = 12.5; A.reachEnding('plague');
          for (let i = 0; i < 30; i++) A.step(0.1);
          const s1 = JSON.parse(JSON.stringify(A.serialize())), w = A.sanitizeWorld(JSON.parse(JSON.stringify(s1)));
          const same = k => JSON.stringify(s1[k]) === JSON.stringify(w[k]);
          const civ = ['bunker', 'closed', 'scav'].every(k => w.civs.every((c, i) => Math.abs((c[k] || 0) - (s1.civs[i][k] || 0)) < 1e-6));
          const old = JSON.parse(JSON.stringify(s1)); for (const k of ['ruins', 'winter', 'hot', 'seaRise', 'pandemic', 'plagueCycle']) delete old[k]; old.civs.forEach(c => { delete c.bunker; delete c.closed; delete c.scav; }); delete old.fates.riseAt;
          let oldOk = true; try { A.loadWorld(old); for (let i = 0; i < 30; i++) A.step(0.1); A.render(); } catch (e) { oldOk = String(e); }
          const bad = JSON.parse(JSON.stringify(s1)); bad.ruins = [{ k: 'x' }, null, { k: 'tower', x: 'a', t0: 1e99 }]; bad.pandemic = { inf: { 999: 5, a: 1 }, rec: 'no' }; bad.winter = 7; bad.hot = null; bad.seaRise = 1e9;
          let badOk = true; try { A.loadWorld(bad); for (let i = 0; i < 30; i++) A.step(0.1); A.render(); } catch (e) { badOk = String(e); }
          return JSON.stringify({ ruins: same('ruins'), winter: same('winter'), hot: same('hot'), sea: same('seaRise'), pd: same('pandemic'), riseAt: s1.fates.riseAt === w.fates.riseAt, civ, oldOk, badOk, badSea: A.W.seaRise, badRuins: A.W.ruins.length }); }'''))
        check('saves: ruins, winter, warming, plague, riseAt and bunkers round-trip', all(r[k] for k in ['ruins', 'winter', 'hot', 'sea', 'pd', 'riseAt', 'civ']), str(r))
        check('saves: old saves and garbage still load', r['oldOk'] is True and r['badOk'] is True and r['badSea'] <= 34 and r['badRuins'] == 1, str(r))
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
