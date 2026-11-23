# The galaxy view: the Milky Way (bar, arms, Orion Spur) with the Sun where it really is; no name labels; click the Sun or the centre
import asyncio, json, math
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1600, 'height': 1000}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        # geometry: the Sun about 26,000 ly out (of a 50,000 ly disc), between the Sagittarius and Perseus arms, the bar's near end ~27° from the Sun's line
        r = json.loads(await ev(r'''() => { const A = window.__aoh, G = A.GAL_INFO(); return JSON.stringify(G); }'''))
        print('  geometry:', r)
        check('the Sun sits about 26,000 light years from the centre', abs(r['sunLy'] - 26500) < 1500, str(r['sunLy']))
        check('the Sun lies between the Sagittarius arm (inside) and the Perseus arm (outside)', r['sag'] < r['sunR'] < r['per'], str(r))
        check('the bar is about 30,000 ly long and its near end points ~27° from the Sun', 26000 < r['barLy'] < 34000 and abs(r['barSunDeg'] - 27) < 3, str(r))
        check('the major arms start at the ends of the bar', r['armStartErr'] < .02, str(r['armStartErr']))
        # a world with ships and colonies; zoom all the way out
        await ev(r'''() => { const A = window.__aoh; A.newWorld(961); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); const [c, d] = A.W.civs; for (const o of A.W.civs) o.era = 14;
          A.W.ships = [{ id: 7101, civ: c.id, star: 6, name: 'Far Hope II', t0: A.W.simTime - 200, dur: 900, crew: 1e5, y0: 3000, told: 0 }]; A.W.stars = [{ star: 3, civ: d.id, name: 'Wayfarer IX', pop: 8e4, t0: 2900 }, { star: 9, civ: c.id, name: 'Wayfarer X', pop: 5e4, t0: 3100 }]; window.scrollTo(0, 0); }''')
        texts = {}
        for z in [.0002, .00008, .00004, .00002]:
            await ev(f"() => {{ const A = window.__aoh; A.setZoom({z}); A.render(); }}"); await pg.wait_for_timeout(300)
            # catch every text drawn on the map canvas this frame
            n = await ev(r'''() => { const cv = document.querySelector('#world'), c2 = cv.getContext('2d'), got = []; const f = c2.fillText, sT = c2.strokeText; c2.fillText = function (t, ...a) { got.push(String(t)); return f.call(this, t, ...a); }; c2.strokeText = function (t, ...a) { got.push(String(t)); return sT.call(this, t, ...a); };
              window.__aoh.render(); c2.fillText = f; c2.strokeText = sT; return JSON.stringify(got); }''')
            texts[z] = json.loads(n)
            await (await pg.query_selector('#world')).screenshot(path=f'galaxy_{z}.png')
        print('  text drawn per zoom:', {z: t[:6] for z, t in texts.items()})
        lensT = set(json.loads(await ev("() => JSON.stringify(window.__aoh.XSTARS.map(s => s[0]))"))) | {'The Sun’s neighbourhood'}  # the SV-01 lens is the one place names show
        check('no name labels when zoomed out to the galaxy (only the neighbourhood lens)', all(not [t for t in texts[z] if t not in lensT] for z in [.00004, .00002]), str({z: texts[z][:5] for z in texts}))
        # the solar system (planets, swarm, claims, the Moon) is not drawn on top of the galaxy; colonies right on the Sun merge into its marker
        await ev(r'''() => { const A = window.__aoh; for (const o of A.W.civs) { A.foundBase(o, 'mars'); A.foundBase(o, 'moon'); } A.W.dyson = { by: { [A.W.civs[0].id]: 300 }, total: 300, mark: 0 }; for (const r of A.W.spaceRes) r.owner = A.W.civs[0].id; A.W.stars.push({ star: 0, civ: A.W.civs[2].id, name: 'Near', pop: 1e4, t0: 3000 }); }''')
        r = {}
        for z in [.00015, .00008, .00003]:
            r[z] = json.loads(await ev(f'''() => {{ const A = window.__aoh; A.setZoom({z}); A.render(); const sun = A.V.orbPicks.find(q => q.kind === 'sungal'); return JSON.stringify({{ bodies: Object.keys(A.V.bodyPos || {{}}), claims: A.V.orbPicks.filter(q => q.kind === 'claim').length, onSun: sun ? A.V.orbPicks.filter(q => (q.kind === 'starcol' || q.kind === 'voyage') && Math.hypot(q.x - sun.x, q.y - sun.y) < 14).length : 0 }}); }}'''))
        check('no solar-system cluster at galaxy scale (no planets, Moon or claims; nothing piled on the Sun)', all(not v['bodies'] and v['claims'] == 0 and v['onSun'] == 0 for v in r.values()), str(r))

        # at full zoom-out the galaxy is centred and the Sun is off to one side, below the centre
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.setZoom(.00002); A.render(); const cv = document.querySelector('#world'), sun = A.V.orbPicks.find(q => q.kind === 'sungal'), core = A.V.orbPicks.find(q => q.kind === 'gcore');
          return JSON.stringify({ sun: sun && [sun.x, sun.y], core: core && [core.x, core.y], w: cv.clientWidth, h: cv.clientHeight }); }'''))
        check('zoomed out, the centre is in the middle and the Sun below it', r['core'] and abs(r['core'][0] - r['w'] / 2) < r['w'] * .1 and r['sun'][1] > r['core'][1], str(r))
        # click the Sun and the centre for what they are
        got = {}
        for kind, how in [('sungal', 'left'), ('gcore', 'right')]:
            got[kind] = await ev(r'''([kind, how]) => { const A = window.__aoh, cv = document.querySelector('#world'), r = cv.getBoundingClientRect(); A.render(); const q = A.V.orbPicks.find(q => q.kind === kind); if (!q) return 'none';
              const o = { bubbles: true, cancelable: true, clientX: r.left + q.x, clientY: r.top + q.y, pointerId: 1, pointerType: 'mouse', isPrimary: true, button: how === 'left' ? 0 : 2 };
              if (how === 'left') { cv.dispatchEvent(new PointerEvent('pointerdown', o)); cv.dispatchEvent(new PointerEvent('pointerup', o)); } else cv.dispatchEvent(new MouseEvent('contextmenu', o));
              const t = document.querySelector('#tip'), txt = t.style.display !== 'none' ? t.innerText.replace(/\n/g, ' | ') : ''; const b = document.querySelector('#tipClose'); if (b) b.click(); return txt.slice(0, 120); }''', [kind, how])
        print('  clicks:', got)
        check('click the Sun: home, on the Orion Spur; click the centre: the bar and Sagittarius A*', 'Orion Spur' in got['sungal'] and 'Sagittarius A' in got['gcore'], str(got))
        # the galaxy turns like a real disc galaxy (flat rotation curve, a faster bar, arms as density waves), and stops when paused
        r = json.loads(await ev(r'''() => JSON.stringify({ paused: window.__aoh.UI.paused, t0: window.__aoh.V.galT || 0 })'''))
        await pg.wait_for_timeout(1200)
        r2 = json.loads(await ev(r'''() => JSON.stringify({ t1: window.__aoh.V.galT || 0, paused: window.__aoh.UI.paused })'''))
        await pg.keyboard.press('Space'); await pg.wait_for_timeout(1200)
        r3 = json.loads(await ev(r'''() => JSON.stringify({ t2: window.__aoh.V.galT || 0, paused: window.__aoh.UI.paused })'''))
        await pg.keyboard.press('Space')
        moved = (r3['t2'] - r2['t1']) if not r3['paused'] else (r2['t1'] - r['t0'])
        still = (r2['t1'] - r['t0']) if r2['paused'] else (r3['t2'] - r2['t1'])
        check('the galaxy turns while the game runs and stands still when paused', moved > .8 and still < .05, str([r, r2, r3]))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, V = A.V, Ws = A.gOmega(.53), v = r => A.gOmega(r) * r, per = r => 6.2832 / A.gOmega(r);
          V.galT = 0; const s0 = A.sunG(); V.galT = A.GYEAR / 4; const s1 = A.sunG(); const ang = (Math.atan2(s1[1], s1[0]) - Math.atan2(s0[1], s0[0]) + 6.2832) % 6.2832;
          A.setZoom(.00002); A.render(); const cv = document.querySelector('#world'), core = V.orbPicks.find(q => q.kind === 'gcore'), sun = V.orbPicks.find(q => q.kind === 'sungal');
          const spread = T => { let s = 0, n = 0; for (const st of A.GAL) { if (st[4] !== 'a') continue; const af = (T / st[7] + st[8]) % 1; s += Math.abs((st[9] - A.GARM_W * Ws) * af * st[7]); n++; } return +(s / n).toFixed(3); };
          const shear = (A.gOmega(.25) - A.gOmega(.8)) * A.GYEAR; V.galT = 0;
          return JSON.stringify({ quarter: +ang.toFixed(3), flat: +(v(.9) / v(.4)).toFixed(3), inner: +(v(.02) / v(.4)).toFixed(3), perSun: +per(.53).toFixed(1), perCore: +per(.05).toFixed(1), perEdge: +per(1).toFixed(1), bar: A.GBAR_W, arms: A.GARM_W,
            centred: !!core && Math.abs(core.x - cv.clientWidth / 2) < cv.clientWidth * .1, sunR: core && sun ? Math.round(Math.hypot(sun.x - core.x, sun.y - core.y)) : 0, s1: spread(A.GYEAR), s50: spread(50 * A.GYEAR), shear: +shear.toFixed(2) }); }'''))
        print('  rotation:', r)
        check('the Sun goes round the centre once per galactic year (a quarter turn in a quarter year), and the centre stays in the middle', abs(r['quarter'] - 1.5708) < .01 and r['centred'] and r['sunR'] > 50, str(r))
        check('a flat rotation curve: outer stars move at about the same speed, the core turns like a wheel, inner stars go round faster', abs(r['flat'] - 1) < .1 and r['inner'] < .5 and r['perCore'] < r['perSun'] < r['perEdge'], str(r))
        check('the bar turns faster than the Sun and the arms just slower (the Sun near corotation); the disc shears', r['bar'] > 1.2 and .85 < r['arms'] < 1 and r['shear'] > 3, str(r))
        check('young stars are born in the arms and drift out as they age, so the arms never wind up', r['s1'] < .3 and abs(r['s50'] - r['s1']) < .08, str(r))
        for i, T in enumerate([0, 40, 80]):
            await ev(f"() => {{ const A = window.__aoh; A.V.galT = {T}; A.setZoom(.00002); A.render(); }}")
            await pg.screenshot(path=str(pathlib.Path(__file__).with_name(f'galaxy_turn{i}.png')))
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
