# The Moon follows real orbital rules (squeezed in distance like the rest of the solar system): it crosses the sky the
# same way as the Sun, laps it once per synodic month (new moon beside the Sun, full moon opposite), swings nearer and
# further with its eccentricity, keeps one face to Earth, and sits right beside Earth on its orbit at solar-system scale.
import asyncio, json, math, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(os.environ.get('GAME') or pathlib.Path(__file__).resolve().parents[1].joinpath('index.html')).resolve().as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

AT = r'''(a) => { const A = window.__aoh; A.UI.paused = true; A.V.dayT = a.day; A.V.moonD = a.md; A.setZoom(a.z); A.render();
  const m = A.V.bodyPos.Moon, s = A.V.sunXY; if (!m || !s) return null;
  const ang = (x, y) => Math.atan2(x - A.V.cx, -(y - A.V.cy));
  return { m: ang(m[0], m[1]), s: ang(s[0], s[1]), d: Math.hypot(m[0] - A.V.cx, m[1] - A.V.cy), r: m[2], Rb: A.V.Rb * A.V.s, M: A.MOON }; }'''
wrap = lambda a: (a + math.pi) % (2 * math.pi) - math.pi

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700)
        at = lambda day, md, z=.03: pg.evaluate(AT, {'day': day, 'md': md, 'z': z})
        M = (await at(.3, 0))['M']; syn, ano, e = M['MOON_SYN'], M['MOON_ANO'], M['MOON_E']
        # phases: elongation from the Sun grows 0 -> 2pi over a synodic month (equation of centre at most 2e)
        el = []
        for k in range(8):
            q = await at(.3, syn * k / 8)
            el.append(wrap(q['m'] - q['s']))
        exp = [wrap(2 * math.pi * k / 8 + 2 * e * math.sin(2 * math.pi * (syn * k / 8) / ano)) for k in range(8)]
        err = max(abs(wrap(a - b_)) for a, b_ in zip(el, exp))
        check('new moon beside the Sun, full moon opposite, one lap per synodic month', err < .02 and abs(el[0]) < .12 and abs(abs(el[4]) - math.pi) < .12, str([round(x, 2) for x in el]))
        # direction: over an hour of game day both the Sun and the Moon move the same way across the sky, the Moon a little slower
        a0, a1 = await at(.30, 5), await at(.31, 5 + .01)
        ds, dm = wrap(a1['s'] - a0['s']), wrap(a1['m'] - a0['m'])
        check('the Moon crosses the sky the same way as the Sun, lagging it by 1/29.5 of a lap a day', ds * dm > 0 and abs(dm / ds - (1 - 1 / syn)) < .08, str({'sun': round(ds, 4), 'moon': round(dm, 4), 'ratio': round(dm / ds, 3)}))
        # eccentricity: perigee and apogee distances differ by about 2e
        per, apo = await at(.3, 0), await at(.3, ano / 2)
        check('eccentric orbit: apogee about 11% further than perigee', abs(apo['d'] / per['d'] - (1 + e) / (1 - e)) < .01, str(round(apo['d'] / per['d'], 3)))
        check('Moon about 0.27 of Earth across', abs(per['r'] / per['Rb'] - .273) < .01, str(round(per['r'] / per['Rb'], 3)))
        # solar-system scale: the Moon sits right beside Earth, on Earth's orbit
        so = await at(.3, 5, .004)
        check('at solar-system scale the Moon hugs Earth (within 40 px)', so and so['d'] < 40, str(so and round(so['d'], 1)))
        # the clock drives it: running time moves the month on
        m0 = await pg.evaluate("() => window.__aoh.V.moonD")
        await pg.evaluate("() => { window.__aoh.UI.paused = false; }"); await pg.wait_for_timeout(1500)
        m1 = await pg.evaluate("() => window.__aoh.V.moonD")
        check('the month advances with the game day (1 day = 48 s)', 0 < m1 - m0 < .1, str(round(m1 - m0, 4)))
        # the planets keep the game's year (one season cycle) and Kepler's third law; they stand still while paused
        PL = r"""(t) => { const A = window.__aoh; A.UI.paused = true; A.W.simTime = t; A.setZoom(.0004); A.render(); const s = A.V.sunXY, o = {};
          for (const [n, q] of Object.entries(A.V.bodyPos)) if (n !== 'Moon') o[n] = Math.atan2(q[1] - s[1], q[0] - s[0]); return o; }"""
        Y = M and await pg.evaluate("() => window.__aoh.YEAR_SEC")
        t0 = 5000; p0 = await pg.evaluate(PL, t0); p1 = await pg.evaluate(PL, t0 + Y * .05)
        AU = {'Mercury': .39, 'Venus': .72, 'Mars': 1.52, 'Jupiter': 5.2, 'Saturn': 9.5}
        errs2 = {n: round(wrap(p1[n] - p0[n]) / (2 * math.pi * .05 / au ** 1.5), 3) for n, au in AU.items() if n in p0}
        check('planets go round once per au^1.5 game years (Jupiter 11.86), a game year being one season cycle', len(errs2) == 5 and all(abs(v - 1) < .01 for v in errs2.values()), str(errs2))
        jup = 2 * math.pi / (2 * math.pi / Y / 5.2 ** 1.5)
        check('Jupiter laps the Sun in about 712 s of sim time', abs(jup - 711.5) < 2, str(round(jup, 1)))
        q0 = await pg.evaluate("() => { const A = window.__aoh; A.UI.paused = true; A.render(); return A.V.bodyPos.Jupiter[0]; }"); await pg.wait_for_timeout(800)
        q1 = await pg.evaluate("() => { const A = window.__aoh; A.render(); return A.V.bodyPos.Jupiter[0]; }")
        check('paused: the planets stand still', abs(q1 - q0) < 1e-6, str([q0, q1]))
        print('\n'.join(errs[:5]) or 'no errors')
        await b.close()
    print(f'{sum(results)}/{len(results)} passed')
asyncio.run(main())
