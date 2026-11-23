# Free panning at galaxy scale: real mouse drags, the wheel (zoom toward the cursor, sideways scroll pans), arrow keys,
# limits, and the pan forgotten once you zoom back in to the globe (where a drag still turns the planet)
import asyncio, json
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(os.environ.get('GAME') or pathlib.Path(__file__).resolve().parents[1].joinpath('index.html')).resolve().as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

CORE = r'''() => { const A = window.__aoh; A.render(); const r = document.querySelector('#world').getBoundingClientRect(), c = A.V.orbPicks.find(q => q.kind === 'gcore'), s = A.V.orbPicks.find(q => q.kind === 'sungal');
  return JSON.stringify({ core: c ? [r.left + c.x, r.top + c.y] : null, sun: s ? [r.left + s.x, r.top + s.y] : null, pan: A.V.pan, z: A.V.zoom, cam: A.V.cam, cx: A.V.cx, cw: r.width, ch: r.height, left: r.left, top: r.top }); }'''

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700)
        ev = pg.evaluate
        # pause, so the galaxy stands still; zoom all the way out
        await ev("() => { const A = window.__aoh; window.scrollTo(0, 0); if (!A.UI.paused) document.querySelector('#pauseBtn, [data-act=pause]') ; }")
        await ev("() => { const A = window.__aoh; if (!A.UI.paused) { const b = [...document.querySelectorAll('button')].find(b => /^(Pause|Resume)$/.test(b.textContent.trim())); if (b) b.click(); } A.V.galT = 0; A.setZoom(.00002); }")
        a = json.loads(await ev(CORE))
        mx, my = a['left'] + a['cw'] * .55, a['top'] + a['ch'] * .5
        await pg.mouse.move(mx, my); await pg.mouse.down(); await pg.mouse.move(mx + 100, my + 40, steps=5); await pg.mouse.move(mx + 200, my + 80, steps=5); await pg.mouse.up()
        await pg.wait_for_timeout(100)
        b1 = json.loads(await ev(CORE))
        d = [b1['core'][0] - a['core'][0], b1['core'][1] - a['core'][1]]
        check('a mouse drag at galaxy scale moves the galaxy with the pointer, in both directions', abs(d[0] - 200) < 6 and abs(d[1] - 80) < 6 and abs(b1['cam'] - a['cam']) < 1, str({'moved': d, 'pan': b1['pan']}))
        tip = await ev("() => { const t = document.querySelector('#tip'); return t && t.style.display !== 'none' ? t.innerText : ''; }")
        check('a drag is not a click (no info opens)', tip == '', tip[:60])

        # zooming in after roaming glides back home as part of the scroll: each notch brings the view closer to the solar system,
        # it never moves on its own, zooming out does not undo it, and once the galaxy is gone you are home
        P = r"""() => JSON.stringify({ pan: window.__aoh.V.pan, z: window.__aoh.V.zoom })"""
        await pg.mouse.move(a['left'] + 120, a['top'] + 120)
        for _ in range(3): await pg.mouse.wheel(0, -120); await pg.wait_for_timeout(60)
        p1 = json.loads(await ev(P)); await pg.wait_for_timeout(1200); p2 = json.loads(await ev(P))
        await pg.mouse.wheel(0, 120); await pg.wait_for_timeout(60); p3 = json.loads(await ev(P))
        steps = []
        for _ in range(16):
            await pg.mouse.wheel(0, -120); await pg.wait_for_timeout(50); q = json.loads(await ev(P)); steps.append(None if q['pan'] is None else round(q['pan'][0] / b1['pan'][0], 3))
        c1 = json.loads(await ev(CORE))
        ref = json.loads(await ev("() => { const A = window.__aoh; const p = A.V.pan; A.V.pan = null; const r = JSON.parse((" + CORE + ")()); A.V.pan = p; return JSON.stringify(r); }"))
        f1 = p1['pan'][0] / b1['pan'][0] if p1['pan'] else None
        mono = all(x is None or y is None or y <= x + 1e-6 for x, y in zip(steps, steps[1:]))
        check('zooming in glides back to the solar system as part of the scroll (partly after a few notches, home once the galaxy is gone)', f1 is not None and 0.3 < f1 < 0.99 and mono and steps[-1] is None and c1['pan'] is None and abs(c1['cx'] - ref['cx']) < 1, str({'after 3 notches': round(f1 or -1, 3), 'per notch': steps}))
        check('the glide never moves on its own, and zooming out does not undo it', p2['pan'] == p1['pan'] and p3['pan'] == p1['pan'], str([p1['pan'], p2['pan'], p3['pan']]))
        # and keeps zooming in from there, to the Sun and the solar system
        for _ in range(14): await pg.mouse.wheel(0, -120); await pg.wait_for_timeout(40)
        await pg.wait_for_timeout(600)
        z2 = json.loads(await ev("() => { const A = window.__aoh; A.render(); const r = document.querySelector('#world').getBoundingClientRect(); return JSON.stringify({ z: A.V.zoom, pan: A.V.pan, sys: Object.keys(A.V.bodyPos || {}), sun: A.V.sunXY, cw: r.width, ch: r.height }); }"))
        check('it keeps zooming in to the solar system', z2['z'] > 4e-4 and z2['pan'] is None and 'Sun' in ''.join(z2['sys'] or []) or (z2['z'] > 4e-4 and z2['pan'] is None and z2['sun'] and 0 < z2['sun'][0] < z2['cw']), str(z2))
        # zooming out again from the solar system: the galaxy comes in centred, as before
        for _ in range(24): await pg.mouse.wheel(0, 120); await pg.wait_for_timeout(30)
        o = json.loads(await ev(CORE))
        check('zooming out from the solar system brings the galaxy in centred', o['pan'] is None and o['core'] and abs(o['core'][0] - (o['left'] + o['cw'] / 2)) < o['cw'] * .1, str({'z': o['z'], 'core': o['core'], 'pan': o['pan']}))
        await ev("() => { const A = window.__aoh; A.setZoom(.00004); }")
        c1 = json.loads(await ev(CORE))

        # drag also works zoomed in among the arms
        m2 = [c1['left'] + c1['cw'] * .5, c1['top'] + c1['ch'] * .5]
        await pg.mouse.move(*m2); await pg.mouse.down(); await pg.mouse.move(m2[0] - 150, m2[1] - 60, steps=8); await pg.mouse.up()
        c2 = json.loads(await ev(CORE))
        check('dragging still pans when zoomed in among the arms', c2['core'] and abs(c2['core'][0] - c1['core'][0] + 150) < 6 and abs(c2['core'][1] - c1['core'][1] + 60) < 6, str([c1['core'], c2['core']]))

        # sideways scroll (trackpad) and the arrow keys pan too
        await ev("() => window.__aoh.setZoom(.00002)")
        e0 = json.loads(await ev(CORE)); await pg.mouse.move(m2[0], m2[1]); await pg.mouse.wheel(-90, 0); await pg.wait_for_timeout(80)
        e1 = json.loads(await ev(CORE))
        await pg.keyboard.press('ArrowUp'); await pg.wait_for_timeout(80)
        e2 = json.loads(await ev(CORE))
        check('a sideways scroll and the arrow keys pan the galaxy', e1['core'][0] - e0['core'][0] > 60 and e2['core'][1] - e1['core'][1] > 40, str([e0['core'], e1['core'], e2['core']]))

        # it cannot be lost: a huge drag keeps the centre within reach
        await pg.mouse.move(m2[0], m2[1]); await pg.mouse.down()
        for k in range(1, 30): await pg.mouse.move(m2[0] + k * 200, m2[1] + k * 120)
        await pg.mouse.up()
        f = json.loads(await ev(r'''() => { const A = window.__aoh; return JSON.stringify({ pan: A.V.pan, lim: 1.4 * 1.2e7, s: A.V.s, cw: document.querySelector('#world').clientWidth }); }'''))
        check('the pan has limits, so the galaxy cannot be lost', abs(f['pan'][0]) <= f['lim'] + 1 and abs(f['pan'][1]) <= f['lim'] + 1 and abs(f['pan'][0]) > f['lim'] * .9, str(f))

        # Reset clears it; zooming back to the globe forgets it, and there a drag still turns the planet
        await ev("() => { const b = [...document.querySelectorAll('button')].find(b => b.textContent.trim() === 'Reset'); b.click(); }")
        g = json.loads(await ev(r'''() => JSON.stringify({ pan: window.__aoh.V.pan })'''))
        await ev("() => { const A = window.__aoh; A.setZoom(.00002); }")
        await pg.mouse.move(m2[0], m2[1]); await pg.mouse.down(); await pg.mouse.move(m2[0] + 120, m2[1], steps=5); await pg.mouse.up()
        await ev("() => { const A = window.__aoh; A.setZoom(.03); A.render(); }")
        h = json.loads(await ev(CORE))
        await pg.mouse.move(m2[0], m2[1]); await pg.mouse.down(); await pg.mouse.move(m2[0] + 120, m2[1], steps=5); await pg.mouse.up()
        h2 = json.loads(await ev(CORE))
        check('Reset clears the pan; on the globe it is forgotten and a drag still turns the planet', g['pan'] is None and h['pan'] is None and abs(h['cx'] - h['cw'] / 2) < 2 and abs(h2['cam'] - h['cam']) > 1, str({'reset': g, 'globe': [h['pan'], h['cx'], h['cw']], 'cam': [h['cam'], h2['cam']]}))

        # a click on the Sun after panning still opens its info
        await ev("() => { const A = window.__aoh; A.setZoom(.00002); A.setPan(-3e6, 2e6); }")
        s = json.loads(await ev(CORE))
        await pg.mouse.click(s['sun'][0], s['sun'][1]); await pg.wait_for_timeout(200)
        tip = await ev("() => { const t = document.querySelector('#tip'); return t && t.style.display !== 'none' ? t.innerText : ''; }")
        check('after panning, a click on the Sun still tells what it is', 'The Sun' in tip, tip[:60])
        await pg.screenshot(path=str(pathlib.Path(__file__).with_name('galpan.png')))

        print('\n'.join(errs[:5]) or 'no errors')
        await b.close()
    print(f'{sum(results)}/{len(results)} passed')
asyncio.run(main())
