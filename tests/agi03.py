# AGI-03: the caretaker ending. The machines take charge: no wars, no progress, stability and nature rise; holdouts stay outside
import asyncio, json
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

# a Future Age world at war and polluted; civ 0 is Devout with few machines (a holdout); the machines then end the world
SETUP = r'''(seed) => { const A = window.__aoh; A.newWorld(seed); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
  const cs = A.W.civs; for (const c of cs) { c.era = 11; c.tech = 30; c.trait = 'Curious'; c.mach = 80; c.stability = 40; c.military = 60; }
  cs[0].trait = 'Devout'; cs[0].mach = 10; A.W.pollution = 60; A.W.wars = [];
  A.W.wars.push({ a: cs[1].id, b: cs[2].id, t: 0, adv: 0 }); A.W.wars.push({ a: cs[0].id, b: cs[3].id, t: 0, adv: 0 });
  A.startFate('agi'); return cs.length; }'''

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate

        await ev(SETUP, 301)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, cs = W.civs; A.endFate('agi', 'ending');
          const K = W.care, first = W.chron.slice(0, 8).map(e => e.h.replace(/<[^>]+>/g, ''));
          return JSON.stringify({ ended: W.fates.ended, care: !!K, free: K ? K.free : null, kept: cs.filter(A.careOf).length, n: cs.length, wars: W.wars.length, active: W.fates.active.length,
            took: first.some(l => /machines take charge of/.test(l)), refuse: first.some(l => /refuse the care of the machines/.test(l)) }); }'''))
        check('AGI-03 the Waking Machines end the world as the caretakers', r['ended'] == 'agi' and r['care'] and r['active'] == 0, str(r))
        check('AGI-03 everyone with machines is taken into care; a Devout people with few machines stays outside', r['kept'] == r['n'] - 1 and len(r['free']) == 1, str(r))
        check('AGI-03 the chronicle tells of the takeover and the holdout', r['took'] and r['refuse'], str(r))

        # run on: the world under the caretakers
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, cs = W.civs, kept = cs.filter(A.careOf), out = cs.filter(c => !A.careOf(c));
          const N = W.nat; const fk = () => { let a = 0, n = 0; for (const c of kept) for (let i = Math.max(0, Math.floor(c.l / 100)); i <= Math.floor(c.r / 100); i++) { a += N.f[i]; n++; } return n ? a / n : 0; };
          for (const c of kept) for (let i = Math.max(0, Math.floor(c.l / 100)); i <= Math.floor(c.r / 100); i++) N.f[i] *= .35;
          const t0 = kept.map(c => c.era * 100 + c.tech), e0 = kept.map(c => c.era), fr0 = fk(), p0 = W.pollution, s0 = kept.map(c => c.stability), h0 = out.map(c => c.era * 100 + c.tech);
          for (const c of out) c.mach = 0;
          let tried = 0; for (let i = 0; i < 3000; i++) { if (i % 300 === 0) { A.applyEvent(A.findEvent('war'), kept[0].x); tried++; } A.step(0.1); }
          const warsKept = W.wars.filter(w => kept.some(c => c.id === w.a || c.id === w.b)).length;
          return JSON.stringify({ tech: kept.map((c, i) => +(c.era * 100 + c.tech - t0[i]).toFixed(1)), era: kept.every((c, i) => c.era === e0[i]), stab0: s0.map(Math.round), stab: kept.map(c => Math.round(c.stability)), food: kept.map(c => Math.round(c.food)), mil: kept.map(c => Math.round(c.military)),
            fr0: +fr0.toFixed(3), fr: +fk().toFixed(3), p0: Math.round(p0), p: Math.round(W.pollution), warsKept, tried, hold: out.map((c, i) => +(c.era * 100 + c.tech - h0[i]).toFixed(1)),
            lines: W.chron.filter(e => /caretakers|machines let the forests|history lessons end|no decision of any weight|Nothing new has been invented|armies of/.test(e.h)).length }); }'''))
        print('  under the caretakers:', r)
        check('AGI-03 no war among peoples in care, even when a war is ordered', r['warsKept'] == 0 and r['tried'] >= 5, str(r))
        check('AGI-03 progress halts: no new age, no tech', r['era'] and max(r['tech']) <= 0, str(r['tech']))
        check('AGI-03 stability and food rise, armies shrink', min(r['stab']) >= 80 and min(r['food']) >= 75 and max(r['mil']) <= 15, str(r))
        check('AGI-03 nature returns and pollution falls', r['fr'] > r['fr0'] and r['p'] < r['p0'] - 20, str(r))
        check('AGI-03 the holdouts still make their own history', max(r['hold']) > 20, str(r['hold']))
        check('AGI-03 chronicle lines from the caretakers', r['lines'] >= 3, str(r['lines']))

        # holdouts who let their machines grow give in; peoples in care make no choices
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, h = W.civs.find(c => c.alive && !A.careOf(c)); if (!h) return JSON.stringify({ none: true });
          const k = W.civs.find(c => A.careOf(c)); const n0 = W.chron.length; k.lastReact = -99; A.doReaction(k, 'threat'); const reacted = k.lastReact !== -99;
          h.mach = 65; A.careTick(0.1); return JSON.stringify({ joined: A.careOf(h), said: W.chron.some(e => /give in at last/.test(e.h)), reacted }); }'''))
        check('AGI-03 a holdout gives in once its machines reach 60', r.get('joined') and r.get('said'), str(r))
        check('AGI-03 peoples in care make no choices of their own', r.get('reacted') is False, str(r))

        # epilogue: its own rows and story
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.showEpilogue(); const t = document.querySelector('#dialog').innerText; document.querySelector('#dialog [data-close]').click();
          return JSON.stringify({ name: /The Quiet Takeover/.test(t), care: /In the machines’ care/.test(t), out: /Outside it/.test(t), last: /Last human decision/.test(t), story: /caretakers keep the peace/.test(t), rise: /Begin again/.test(t) }); }'''))
        check('AGI-03 its own epilogue: who is in care, who is outside, the last human decision', r['name'] and r['care'] and r['out'] and r['last'] and r['story'] and not r['rise'], str(r))

        # card chip and next line
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.updateUI(); const c = A.W.civs.find(A.careOf), el = document.querySelector(`#civs .civ[data-id="${c.id}"]`).innerText;
          return JSON.stringify({ chip: /In the machines’ care/.test(el), next: /No new age will come/.test(el) }); }'''))
        check('AGI-03 the people card shows the care', r['chip'] and r['next'], str(r))

        # saves keep it; bad values sanitised; an old save that ended in the takeover gets the caretakers
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; W.care.free = [W.civs[0].id]; const s = JSON.parse(JSON.stringify(A.serialize())); const w = A.sanitizeWorld(s);
          const s2 = JSON.parse(JSON.stringify(s)); s2.care = { t0: 'x', free: [9999, 'a', s2.civs[0].id], said: -5, era: { '9999': 3, 'zz': 1 } }; const bad = A.sanitizeWorld(s2);
          const s3 = JSON.parse(JSON.stringify(s)); delete s3.care; const old = A.sanitizeWorld(s3);
          const s4 = JSON.parse(JSON.stringify(s)); s4.fates.ended = null; const none = A.sanitizeWorld(s4);
          A.loadWorld(s); for (let i = 0; i < 30; i++) A.step(0.1); A.render();
          return JSON.stringify({ kept: w.care && w.care.free.length === 1, badFree: bad.care.free, badSaid: bad.care.said, badEra: Object.keys(bad.care.era), old: !!old.care && old.care.free.length === 0, none: none.care, loaded: !!A.W.care }); }'''))
        check('AGI-03 the caretakers are saved and sanitised; old saves get them', r['kept'] and len(r['badFree']) == 1 and r['badSaid'] == 0 and r['badEra'] == [] and r['old'] and r['none'] is None and r['loaded'], str(r))

        # a new world has none
        r = await ev("() => { const A = window.__aoh; A.newWorld(302); return A.W.care === null && !A.careOf(A.W.civs[0]); }")
        check('AGI-03 a new world starts without caretakers', r)

        # look at it
        await ev(SETUP, 303)
        await ev(r'''() => { const A = window.__aoh; A.endFate('agi', 'ending'); for (let i = 0; i < 400; i++) A.step(0.1); const c = A.W.civs.find(A.careOf); A.V.banners.length = 0; A.setZoom(1.5); A.V.cam = c.x - A.V.vw / 2; A.V.camY = null; A.V.dayT = .85; const d = document.querySelector('#dialog [data-close]'); if (d) d.click(); }''')
        await pg.wait_for_timeout(2600); await ev("() => { const d = document.querySelector('#modal.open [data-close]'); if (d) d.click(); window.scrollTo(0, 0); }"); await pg.wait_for_timeout(500)
        await (await pg.query_selector('#world')).screenshot(path='agi03_care.png')
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
