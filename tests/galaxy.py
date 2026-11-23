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
        check('no name labels when zoomed out to the galaxy', all(len(texts[z]) == 0 for z in [.00004, .00002]), str({z: texts[z][:5] for z in texts}))
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
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
