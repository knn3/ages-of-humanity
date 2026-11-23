# Right-click info on objects in orbit (satellites, telescopes, stations, ring habitats, space cylinders, space elevators) on the curved views
import asyncio, json
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
        pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        # a Stellar Age world with a space cylinder, seen from orbit; try zoom levels until each kind is on screen
        kinds = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(901); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          for (const c of A.W.civs) { c.era = 13; c.tech = 20; } A.W.megas = [{ type: 'cylinder', civ: A.W.civs[0].id, a: 1 }]; A.W.wars = [];
          window.scrollTo(0, 0); const seen = {};
          const cw = document.querySelector('#world').clientWidth, ch = document.querySelector('#world').clientHeight; for (const z of [.5, .42, .36, .3, .26, .22, .19, .16, .13, .11, .09, .075]) { A.setZoom(z); for (let f = 0; f < 150; f++) { A.V.t += 7.3; if (f % 10 === 9) A.V.cam += 997; A.render(); for (const q of A.V.orbPicks) if (!seen[q.kind] && q.x > 280 && q.x < cw - 30 && q.y > 70 && q.y < ch - 30) seen[q.kind] = { z, t: A.V.t, x: q.x, y: q.y }; } } seen.cw = [cw, ch];
          return JSON.stringify(seen); }'''))
        print('  orbit objects found:', {k: (v['z'], round(v['x']), round(v['y'])) if isinstance(v, dict) else v for k, v in kinds.items()})
        check('the orbit layer records every kind of object', all(k in kinds for k in ['sat', 'scope', 'station', 'ring', 'cylinder', 'elevator']), str(list(kinds)))

        # right-click each one with the real mouse; the tip names it
        names = {'sat': 'Satellite', 'scope': 'Space telescope', 'station': 'Space station', 'ring': 'Ring habitat', 'cylinder': 'Space cylinder', 'elevator': 'Space elevator station'}
        got = {}
        for k, want in names.items():
            if k not in kinds: continue
            v = kinds[k]
            got[k] = await ev(r'''([z, kind]) => { const A = window.__aoh; A.setZoom(z); const cv = document.querySelector('#world'), cw = cv.clientWidth, ch = cv.clientHeight, r = cv.getBoundingClientRect();
              for (let f = 0; f < 300; f++) { A.V.t += 7.3; A.render(); const q = A.V.orbPicks.find(q => q.kind === kind && q.x > 280 && q.x < cw - 30 && q.y > 70 && q.y < ch - 30 && !A.V.orbPicks.some(o => o !== q && Math.hypot(o.x - q.x, o.y - q.y) < 25));
                if (q) { cv.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: r.left + q.x, clientY: r.top + q.y, button: 2 })); const t = document.querySelector('#tip'); return t && t.style.display !== 'none' ? t.innerText.split('\n')[0] : 'no tip'; } } return 'gone'; }''', [v['z'], k])
            # it must stay open while the game runs on (UI updates, frames)
            await pg.wait_for_timeout(1500)
            stay = await ev("() => { const t = document.querySelector('#tip'); return t && t.style.display !== 'none' ? t.innerText.split('\\n')[0] : ''; }")
            if stay != got[k]: got[k] = 'closed: ' + got[k]
            await ev("() => { const b = document.querySelector('#tipClose'); if (b) b.click(); }")
            continue
            got[k] = await ev("() => { const t = document.querySelector('#tip'); return t && t.style.display !== 'none' ? t.innerText.split('\\n')[0] : ''; }")
            await ev("() => { const b = document.querySelector('#tipClose'); if (b) b.click(); }")
        print('  right-click tips:', got)
        check('right-clicking an object in orbit tells what it is (and who built it), and the tip stays open', all(names[k] in got.get(k, '') for k in names if k in kinds) and all('·' in got[k] for k in ['ring', 'cylinder', 'station'] if k in got), str(got))

        # unpause so the game really runs while a tip is open; leaving orbit closes it
        r = await ev(r'''async () => { const A = window.__aoh, cv = document.querySelector('#world'), r = cv.getBoundingClientRect(); if (A.UI.paused) document.querySelector('.js-pause').click(); A.setZoom(.22);
          for (let f = 0; f < 300; f++) { A.V.t += 7.3; A.render(); const q = A.V.orbPicks.find(q => q.kind === 'station' && q.x > 280 && q.x < cv.clientWidth - 30 && q.y > 70 && q.y < cv.clientHeight - 30); if (q) { cv.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: r.left + q.x, clientY: r.top + q.y, button: 2 })); break; } }
          await new Promise(res => setTimeout(res, 2000)); const open = document.querySelector('#tip').style.display !== 'none';
          A.setZoom(1.6); await new Promise(res => setTimeout(res, 1200)); const after = document.querySelector('#tip').style.display !== 'none'; return JSON.stringify({ open, after }); }''')
        r = json.loads(r)
        check('an orbit tip stays open as the game runs, and closes when you zoom back down to the ground', r['open'] and not r['after'], str(r))

        # out in the solar system: claims; out in the galaxy: a ship on its way, in its lens (opened from the chronicle); star colonies are
        # dots on the galaxy: right click tells what they are, left click (or their chronicle lines) opens the world, see sv01.py
        CLICK = r'''async ([z, kind, how]) => { const A = window.__aoh, cv = document.querySelector('#world'), r = cv.getBoundingClientRect(); A.V.focus = null; A.UI.day = false; A.V.galT = 0; A.V.lensShip = kind === 'voyage' ? { kind: 'ship', id: 7001 } : null; A.setZoom(z); await new Promise(res => setTimeout(res, 250));
          const q = A.V.orbPicks.find(q => q.kind === kind && q.x > 280 && q.x < cv.clientWidth - 30 && q.y > 70 && q.y < cv.clientHeight - 30); if (!q) return JSON.stringify({ none: true, kinds: [...new Set(A.V.orbPicks.map(q => q.kind))] });
          const o = { bubbles: true, cancelable: true, clientX: r.left + q.x, clientY: r.top + q.y, pointerId: 1, pointerType: 'mouse', isPrimary: true };
          if (how === 'left') { cv.dispatchEvent(new PointerEvent('pointerdown', { ...o, button: 0 })); cv.dispatchEvent(new PointerEvent('pointerup', { ...o, button: 0 })); } else cv.dispatchEvent(new MouseEvent('contextmenu', { ...o, button: 2 }));
          const t0 = document.querySelector('#tip').style.display !== 'none' ? document.querySelector('#tip').innerText.split('\n')[0] : '';
          await new Promise(res => setTimeout(res, 1500)); const t1 = document.querySelector('#tip').style.display !== 'none' ? document.querySelector('#tip').innerText : '';
          const b = document.querySelector('#tipClose'); if (b) b.click(); return JSON.stringify({ t0, stays: !!t1 && t1.startsWith(t0), body: t1.replace(/\n/g, ' | ').slice(0, 160), focus: A.V.focus && A.V.focus.body }); }'''
        await ev(r'''() => { const A = window.__aoh, c = A.W.civs[0], d = A.W.civs[1]; for (const r of A.W.spaceRes) r.owner = c.id;
          const far = A.XSTARS ? A.XSTARS.length - 1 : 6; A.W.ships = [{ id: 7001, civ: c.id, star: far, name: 'Far Hope I', t0: A.W.simTime - 750, dur: 900, crew: 1e5, y0: 3000, told: 0 }]; A.W.stars = [{ star: 9, civ: d.id, name: 'Wayfarer II', pop: 8e4, t0: 2900, sid: 7002, world: 'Lumen', log: [] }]; }''')
        res = {}
        for z in [.003, .002, .0012, .0008]:
            q = json.loads(await ev(CLICK, [z, 'claim', 'left']))
            if not q.get('none'): res['claim'] = q; break
        for kind in ['voyage', 'starcol']:
            for z in [.00012, .00008, .00005, .00003, .00002]:
                q = json.loads(await ev(CLICK, [z, kind, 'right']))
                if not q.get('none'): res[kind] = q; break
        for k, v in res.items(): print(f'  {k}:', v)
        cl, vo, sc = res.get('claim', {}), res.get('voyage', {}), res.get('starcol', {})
        check('a left click on a claim out in the solar system tells what it is (no zoom-in)', cl.get('stays') and any(n in cl.get('t0', '') for n in ['Asteroid Mine', 'Helium-3', 'Ice Moon']) and 'Mined by' in cl.get('body', '') and not cl.get('focus'), str(cl))
        check('a ship on its way, in its lens: name, destination, progress, crew', vo.get('stays') and 'Far Hope I' in vo.get('t0', '') and 'Bound for' in vo.get('body', ''), str(vo))
        check('a settled star (a dot on the galaxy), right click: star, founders, people, its world', sc.get('stays') and 'Founded by' in sc.get('body', '') and 'Wayfarer II' in sc.get('body', ''), str(sc))

        # empty space shows nothing; the ground still needs close zoom
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.setZoom(.3); A.render(); const far = A.tipTarget(5, 5); A.setZoom(.9); A.render(); const c = A.W.civs[0]; A.V.cam = c.x - A.V.vw / 2; A.render(); const s = A.W2S(c.x, A.gy(c.x) - 10); const low = A.tipTarget(s[0], s[1]);
          return JSON.stringify({ far: far, low: low ? Object.keys(low) : null }); }'''))
        check('empty space gives nothing; on the ground the close-zoom rule still holds', r['far'] is None and r['low'] is None, str(r))
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
