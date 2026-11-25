# Real orbit physics, measured on screen through window.__aoh: seen from above the north pole every prograde motion is
# anticlockwise (the planets and the Earth round the Sun, the Earth's spin, the Moon round the Earth, the satellites and
# stations round the globe), and the planets' angular speeds follow their real sidereal periods (Kepler's third law) on one
# shared clock, the game year (YEAR_SEC of sim time). Up close the view turns with the Earth (the Sun crosses the sky once a
# day, clockwise); at solar-system scale it does not turn, so the screen shows the true Sun-centred motion.
import asyncio, math, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(os.environ.get('GAME') or pathlib.Path(__file__).resolve().parents[1].joinpath('index.html')).resolve().as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))
wrap = lambda a: (a + math.pi) % (2 * math.pi) - math.pi
REAL = {'Mercury': .2408, 'Venus': .6152, 'Earth': 1, 'Mars': 1.8809, 'Jupiter': 11.862, 'Saturn': 29.457, 'Uranus': 84.02, 'Neptune': 164.8}

# one paused render at a given time of day, sim time and zoom; angles are anticlockwise-positive on screen (y flipped)
SNAP = r'''(a) => { const A = window.__aoh; A.UI.paused = true; if (a.day != null) A.V.dayT = a.day; if (a.t != null) A.W.simTime = a.t;
  if (a.md != null) A.V.moonD = a.md; if (a.z != null) A.setZoom(a.z); for (let i = 0; i < (a.n || 1); i++) A.render();
  const s = A.V.sunXY, e = [A.V.cx, A.V.cy], ccw = (p, c) => Math.atan2(-(p[1] - c[1]), p[0] - c[0]), o = { rot: A.V.sysRot || 0, sky: A.skyPh ? A.skyPh() : NaN, sun: A.sunPh ? A.sunPh() : NaN, dayV: A.V.dayV, dayT: A.V.dayT };
  if (A.V.b > 0) { const xc = A.V.cam + A.V.vw / 2; o.land = ccw(A.W2S(xc, 372), e); } o.G = A.V.skyG;
  if (s) { o.sunFromEarth = ccw(s, e); o.Earth = ccw(e, s); for (const [n, q] of Object.entries(A.V.bodyPos)) o[n] = n === 'Moon' ? ccw(q, e) : ccw(q, s); }
  return o; }'''

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700)
        snap = lambda **a: pg.evaluate(SNAP, a)
        Y = await pg.evaluate('() => window.__aoh.YEAR_SEC')
        rows = await pg.evaluate('() => window.__aoh.PLANETS') or []
        PL = {r[0]: r[4] for r in rows if len(r) > 4}; au = {r[0]: r[1] for r in rows}
        check('every planet has its real sidereal period (within 0.1%)', len(PL) == 8 and all(abs(PL[n] / T - 1) < 1e-3 for n, T in REAL.items()), str(PL))
        check("Kepler's third law: T^2 = a^3 for every planet (within 1%)", len(PL) == 8 and all(abs(PL[n] ** 2 / au[n] ** 3 - 1) < .01 for n in PL), str({n: round(PL[n] ** 2 / au[n] ** 3, 4) for n in PL}))

        # 1. solar-system scale: true motion on screen. Time runs as in play: the day clock moves on too (1 day = 48 s),
        # which must not turn the picture any more.
        ZS, t0, dt = .0004, 5000.0, .5
        await snap(day=.3, t=t0, z=ZS, n=2)
        a = await snap(day=.3, t=t0)
        bq = await snap(day=.3 + dt / 48, t=t0 + dt)
        w = {n: wrap(bq[n] - a[n]) / dt for n in REAL if n in a and n in bq}
        check('solar view: all eight planets and the Earth on screen', len(w) == 8, str(sorted(w)))
        check('solar view: every planet, the Earth included, goes round the Sun anticlockwise', w and all(v > 0 for v in w.values()), str({n: f'{v:+.5f}' for n, v in w.items()}))
        wE = w.get('Earth', 0)
        check('solar view: the Earth laps the Sun once a game year (YEAR_SEC of sim time)', abs(wE / (2 * math.pi / Y) - 1) < .005, f'{wE:.5f} vs {2 * math.pi / Y:.5f}')
        rat = {n: round(w[n] / wE * REAL[n], 4) for n in w}
        check('solar view: speed ratios match the real periods (w/w_Earth = 1/T, within 0.5%)', all(abs(v - 1) < .005 for v in rat.values()), str(rat))
        per = {n: round(2 * math.pi / w[n] / Y, 3) for n in w}
        print('   periods in game years:', per)
        check('solar view: the Sun drifts round the Earth once a year (not once a day)', abs(wrap(bq['sunFromEarth'] - a['sunFromEarth']) / dt / (2 * math.pi / Y) - 1) < .005, str(round(wrap(bq['sunFromEarth'] - a['sunFromEarth']) / dt, 5)))
        dm = await snap(md=5, day=.3, t=t0); dm2 = await snap(md=5.5, day=.8, t=t0)
        check('solar view: the Moon goes round the Earth anticlockwise', 'Moon' in dm and wrap(dm2['Moon'] - dm['Moon']) > 0, str(round(wrap(dm2.get('Moon', 0) - dm.get('Moon', 0)), 4)))

        # 2. close up (globe): the same view as the solar system. The Earth stays put; the Sun drifts round it anticlockwise
        # once a game year and the Moon goes round anticlockwise. Zooming between the globe and the solar system moves nothing.
        ZC = .03
        g0 = await snap(day=.30, t=t0, md=5, z=ZC, n=2)
        g1 = await snap(day=.30 + dt / 48, t=t0 + dt, md=5 + dt / 48)
        so = await snap(z=ZS)
        g0b = await snap(day=.30, t=t0, md=5); g1b = await snap(day=.30 + dt / 48, t=t0 + dt, md=5 + dt / 48)
        dS, dM = wrap(g1['sunFromEarth'] - g0['sunFromEarth']), wrap(g1['Moon'] - g0['Moon'])
        check('close up: the Sun drifts round the Earth anticlockwise once a game year, as in the solar view', abs(dS / dt / (2 * math.pi / Y) - 1) < .005, f'{dS / dt:.5f} vs {2 * math.pi / Y:.5f}')
        check('close up: the Moon goes round the Earth anticlockwise', dM > 0, f'{dM:+.5f}')
        check('close up and solar view show the Sun and the Moon in the same place and moving the same way', abs(wrap(so['sunFromEarth'] - g1['sunFromEarth'])) < 1e-6 and abs(wrap(so['Moon'] - g1['Moon'])) < 1e-6
              and abs(wrap((g1b['sunFromEarth'] - g0b['sunFromEarth']) - dS)) < 1e-6 and abs(wrap((g1b['Moon'] - g0b['Moon']) - dM)) < 1e-6,
              f"Sun {wrap(so['sunFromEarth'] - g1['sunFromEarth']):.1e}, Moon {wrap(so['Moon'] - g1['Moon']):.1e}")
        h0 = await snap(day=.30, t=t0, md=5, z=ZC, n=2); h1 = await snap(day=.31, t=t0 + 60 * .01 / 48 * 0)
        dL = wrap(h1['land'] - h0['land'])
        check('close up: the Earth stays put (its land does not move on screen as the day goes by)', abs(dL) < 1e-9 and h0['land'] is not None, f'{dL:+.2e}')
        nn = await snap(day=.5)
        check('close up: the globe is lit from the drawn Sun (noon on the side facing it)', abs(math.cos(2 * math.pi * nn['dayV'] + (math.pi / 2 - nn['sunFromEarth'])) + 1) < 1e-6, str(round(nn['dayV'], 4)))
        syn = await pg.evaluate('() => window.__aoh.MOON.MOON_SYN')
        el = []
        for k in range(5):
            q = await snap(day=.3, md=5 + syn * k / 4)
            el.append(wrap(q['Moon'] - q['sunFromEarth']))
        lap = [round(wrap(el[k + 1] - el[k]), 3) for k in range(4)]
        check('close up: relative to the Sun the Moon moves anticlockwise, one lap per synodic month (29.53 days)', all(1.2 < d < 1.95 for d in lap) and abs(sum(lap) - 2 * math.pi) < .05, str(lap))
        sid = 1 / (1 / syn + 1 / 365.256)
        check('Moon: sidereal month from the synodic month and a 365.256-day year is 27.32 days', abs(sid - 27.32) < .01, f'{sid:.3f}')
        k0 = await snap(day=.3, t=t0, z=.01, n=2); k1 = await snap(day=.3, t=t0 + dt)
        wi = {n: (wrap((k1[n] + k1['rot']) - (k0[n] + k0['rot']))) / dt for n in REAL if n in k0 and n in k1}
        rc = {n: round(wi[n] / (2 * math.pi / Y) * REAL[n], 4) for n in wi}
        check('close up (z .01): every planet keeps its real anticlockwise period', len(rc) >= 7 and all(abs(v - 1) < .005 for v in rc.values()), str(rc))

        # 2b. the flat map is the view from the ground: the Sun crosses the sky clockwise (left to right), once a day
        f0 = await snap(day=.30, z=1, n=2); f1 = await snap(day=.31)
        check('flat map: the sky is the ground view (Sun at its time of day, no roll)', abs(wrap(f0['sky'] - f0['sun'])) < 1e-9 and f0['G'] == 0, str(f0['sky'] - f0['sun']))
        check('flat map: the Sun crosses the sky clockwise, one lap a day', abs(wrap(f1['sky'] - f0['sky']) / (2 * math.pi * .01) - 1) < .01, f"{wrap(f1['sky'] - f0['sky']):+.5f}")

        # 3. zooming: from the globe out to the solar system nothing moves; between the flat map and the globe the whole scene
        # sky rolls smoothly, and back on the flat map the Sun is at its time of day
        await snap(day=.37, t=t0, md=8, z=.05, n=2)
        zs = [.05 * (ZS / .05) ** (i / 40) for i in range(41)]
        seen = []
        for z in zs + zs[::-1]:
            q = await snap(z=z); seen.append((q['sky'], q.get('Moon'), q.get('sunFromEarth')))
        dsky = max(abs(wrap(s_[0] - seen[0][0])) for s_ in seen)
        mo = [s_[1] for s_ in seen if s_[1] is not None]; su = [s_[2] for s_ in seen if s_[2] is not None]
        check('zooming alone between the globe and the solar system never moves the Sun or the Moon', dsky < 1e-9 and len(mo) > 20 and max(abs(wrap(m - mo[0])) for m in mo) < 1e-6 and max(abs(wrap(x - su[0])) for x in su) < 1e-6,
              f'sky {dsky:.2e}, Moon seen {len(mo)}x, Sun seen {len(su)}x')
        out1 = await snap(z=ZS, n=2); out2 = await snap(t=t0 + Y / 4, day=.9, md=9)
        back = await snap(z=.05)
        check('time passing at solar scale moves the Sun a quarter lap round the Earth (a quarter year), anticlockwise', abs(wrap(out2['sunFromEarth'] - out1['sunFromEarth']) - math.pi / 2) < 1e-3, f"{wrap(out2['sunFromEarth'] - out1['sunFromEarth']):.4f}")
        check('back on the globe the Sun and the Moon are exactly where the solar view left them', abs(wrap(back['sunFromEarth'] - out2['sunFromEarth'])) < 1e-6 and abs(wrap(back['Moon'] - out2['Moon'])) < 1e-6,
              f"Sun {wrap(back['sunFromEarth'] - out2['sunFromEarth']):.2e}, Moon {wrap(back['Moon'] - out2['Moon']):.2e}")
        async def sweep(N):
            zs = [.05 * (1 / .05) ** (i / N) for i in range(N + 1)]
            r0 = await snap(day=.62, t=t0, z=.05, n=2)
            for k in range(1, 5):   # let some of the year pass on the globe until the scene is well rolled
                if abs(r0['G']) > .5: break
                r0 = await snap(t=t0 + Y * .3 * k)
            prev, jumps, q = None, [], None
            for z in zs:
                q = await snap(z=z)
                if prev is not None: jumps.append(abs(wrap(q['sky'] - prev)))
                prev = q['sky']
            return max(jumps), q if abs(r0['G']) > .5 else None
        j1, _ = await sweep(60); j2, fl = await sweep(120)
        check('zooming from the globe down to the flat map rolls the scene smoothly (half the step, about half the biggest move)', j2 < .2 and j2 < .65 * j1, f'{j1:.4f} at 60 steps, {j2:.4f} at 120')
        check('back on the flat map the Sun is at its time of day again (after a roll of more than 0.5 rad)', fl is not None and abs(wrap(fl['sky'] - fl['sun'])) < 1e-9 and fl['G'] == 0, str(fl and fl['sky'] - fl['sun']))

        # 3b. the flat map shows the Sun and the Moon where the globe and the solar system have them (same angle from straight
        # up, mapped onto the flat sky's arc), so a new Moon sits by the Sun and a full Moon rises as the Sun sets
        FM = r"""(a) => { const A = window.__aoh; A.UI.paused = true; A.V.dayT = a.day; A.V.moonD = a.md; A.setZoom(1); A.render(); A.render();
          const f = A.V.flatMoon, fa = f ? (f[2] * .56 - .28) * 6.2832 : null, fs = (A.V.dayT - .22) / .56;
          A.setZoom(.03); A.render(); A.render(); const m = A.V.bodyPos.Moon, g = m ? Math.atan2(m[0] - A.V.cx, -(m[1] - A.V.cy)) : null;
          return { flat: fa, globe: g, sunX: fs, moonX: f ? f[2] : null }; }"""
        agree, cases = [], [(.4, 0), (.45, 3), (.5, 7), (.6, 10), (.7, 14.8), (.3, 22), (.35, 26), (.9, 16), (.15, 18)]
        for day, md in cases:
            r = await pg.evaluate(FM, {'day': day, 'md': md})
            if r['flat'] is not None and r['globe'] is not None: agree.append(abs(wrap(r['flat'] - r['globe'])))
        check('flat map: the Moon is at the same place in the sky as on the globe', len(agree) >= 5 and max(agree) < 1e-4, f'{len(agree)} cases, max diff {max(agree) if agree else None}')
        nm = await pg.evaluate(FM, {'day': .45, 'md': .3}); fm = await pg.evaluate(FM, {'day': .5, 'md': syn / 2})
        check('flat map: a new Moon sits beside the Sun; a full Moon is below the horizon at noon', nm['moonX'] is not None and abs(nm['moonX'] - nm['sunX']) < .05 and fm['moonX'] is None, f"new {nm['moonX']} vs Sun {nm['sunX']:.3f}, full at noon {fm['moonX']}")

        # 4. the orbit layer round the curved globe: satellites, telescopes and stations go round anticlockwise
        OL = r'''(dt) => { const A = window.__aoh; A.UI.paused = true; A.setZoom(.05); A.V.dayT = .3; A.render();
          const pick = () => Object.fromEntries(A.V.orbPicks.filter(p => ['sat', 'scope', 'station'].includes(p.kind)).map(p => [p.kind + (p.c ? p.c.id : '') + ':' + p.i, Math.atan2(-(p.y - A.V.cy), p.x - A.V.cx)]));
          const a = pick(); A.V.t += dt; A.render(); const b = pick(), out = {};
          for (const k in a) if (k in b) out[k] = ((b[k] - a[k] + 3 * Math.PI) % (2 * Math.PI)) - Math.PI; return out; }'''
        await pg.evaluate("() => { const A = window.__aoh; A.W.civs.forEach((c, i) => { c.era = [12, 11, 10, 12][i % 4]; c.tech = 20; c.reached[c.era] = 2200; }); for (let i = 0; i < 10; i++) A.step(0.1); window.scrollTo(0, 0); }")
        om = await pg.evaluate(OL, .5)
        check('curved globe: satellites, telescopes and stations orbit anticlockwise', len(om) >= 3 and all(v > 0 for v in om.values()), f'{len(om)} objects, min {min(om.values()) if om else None}')

        print('\n'.join(errs[:5]) or 'no errors')
        check('no page errors', not errs)
        await b.close()
    print(f'{sum(results)}/{len(results)} passed')
asyncio.run(main())
