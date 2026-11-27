# WE-04 arrival or loss: at the end of the voyage the world reaches a new star (its own light, the thaw, the peoples climbing out,
# then A New Sun) or is lost (the engines fail, dark and frozen for ever, Lost in the Dark); the chance of loss follows the Jupiter pass,
# war and engines; both endings have their own epilogue; saved and sanitised.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

SETUP = open(pathlib.Path(__file__).with_name('we03.py')).read().split("SETUP = r'''")[1].split("'''")[0]
# run the voyage to its end with a fixed roll for the outcome
TOEND = r'''(roll) => { const A = window.__aoh, W = A.W; A.voyBegin(); W.voy.said = 127; W.voy.jup = { wars: 0, out: 'clear' }; W.voy.t0 = W.simTime - A.VOY.VOY_SPAN - .1; const R = Math.random; Math.random = () => roll; A.voyTick(.001); Math.random = R;
  return JSON.stringify({ out: W.voy.out, dest: W.voy.dest, ended: W.fates.ended, k: A.sunK() }); }'''
ARR = r'''(a) => { const A = window.__aoh, W = A.W; W.voy.t1 = W.simTime - a * A.VOY.VOY_ARRIVE; A.voyTick(.001); return JSON.stringify({ a: A.voyA(), far: A.voyFar(), cold: A.voyCold(), under: A.voyUnder(), t: A.temp(), ended: W.fates.ended }); }'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        await ev(SETUP)
        # the odds
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, cs = W.civs.filter(c => c.alive); A.voyBegin(); const o = {};
          W.voy.jup = { wars: 0, out: 'clear' }; o.clear = A.voyLossChance(); W.voy.jup.out = 'scarred'; o.scar = A.voyLossChance(); W.wars = [{ a: cs[0].id, b: cs[1].id, t: 0, adv: 0 }]; o.war = A.voyLossChance(); W.wars = []; W.voy = null; return JSON.stringify(o); }'''))
        check('the world is likelier lost if Jupiter scarred it, and likelier still with war at the end', .08 <= r['clear'] < .3 and r['scar'] > r['clear'] + .3 and r['war'] > r['scar'] + .1, str(r))
        # arrival
        r = json.loads(await ev(TOEND, .99))
        line = await ev("() => window.__aoh.W.hist.filter(e => /A new star brightens ahead/.test(e.h)).map(e => e.h.replace(/<[^>]+>/g, '')).join('')")
        check('at the end of the voyage a new star brightens ahead, named, and the old Sun is left behind', r['out'] == 'arrive' and r['ended'] is None and r['k'] == 0 and 'A new star brightens ahead' in line, f'{r} {line[:120]}')
        s = [json.loads(await ev(ARR, a)) for a in (.1, .4, .8, .95)]
        check('the new star comes near: the dark lifts as the world slows into its orbit', s[0]['far'] > s[1]['far'] > s[2]['far'] and s[2]['far'] < .05, str([round(x['far'], 2) for x in s]))
        check('the ice thaws: from deep cold back to mild', s[0]['t'] < -30 and s[3]['t'] > -2, str([round(x['t'], 1) for x in s]))
        check('the peoples stay under the ice until the thaw, then climb out', s[1]['under'] and not s[2]['under'], str([x['under'] for x in s]))
        lines = await ev("() => window.__aoh.W.hist.filter(e => /Warm light falls on the ice|climb out of the caverns/.test(e.h)).map(e => e.h.slice(0, 30))")
        check('the thaw and the climb out are told, in order', len(lines) == 2 and 'Warm' in lines[0] and 'climb' in lines[1], str(lines))
        clock = await ev("() => { const A = window.__aoh; A.updateUI(); return document.querySelector('#futures').innerText; }")
        check('the Futures panel follows the arrival', 'Arriving at' in clock, clock.replace('\n', ' | ')[:160])
        # the new sun's own light, from the ground
        r = json.loads(await ev(r'''() => { const A = window.__aoh, V = A.V, W = A.W, cv = document.querySelector('#world'), k = cv.width / cv.clientWidth, c2 = cv.getContext('2d'), c = W.civs.find(c => c.alive);
          const shot = () => { V.focus = null; A.setZoom(1.2); V.cam = c.x - V.vw / 2; V.camY = null; V.dayT = .62; A.render(); const [x, y, R] = V.flatSun; let best = null;
            for (let i = 0; i < 40; i++) { const a = i * 2.4, r = R * .7 * Math.sqrt(i / 40), d = c2.getImageData(Math.round((x + r * Math.cos(a)) * k), Math.round((y + r * Math.sin(a)) * k), 1, 1).data; if (!best || d[0] - d[2] > best[0] - best[2]) best = [d[0], d[1], d[2]]; } return best; };
          const ns = A.newSun(), now = shot(); const keep = W.voy; W.voy = null; const old = shot(); W.voy = keep; return JSON.stringify({ ns, now, old }); }'''))
        exp = r['ns'][1]
        check('from the ground the new sun shines in its own colour', abs(r['now'][1] - r['old'][1]) > 25 or abs(r['now'][2] - r['old'][2]) > 25, f"{r['ns'][0]} {exp}: {r['old']} -> {r['now']}")
        r = json.loads(await ev(ARR, 1.0))
        await pg.wait_for_timeout(2600)
        epi = await ev("() => document.querySelector('#modal').classList.contains('open') ? document.querySelector('#dialog').innerText : ''")
        check('then comes A New Sun, with its own epilogue', r['ended'] == 'arrival' and 'A New Sun' in epi, f"{r['ended']} {epi[:120]!r}")
        # loss
        await ev("() => { const m = document.querySelector('#modal'); if (m) m.classList.remove('open'); }")
        await ev(SETUP)
        r = json.loads(await ev(TOEND, 0))
        r2 = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; for (let i = 0; i < 60; i++) A.step(1); return JSON.stringify({ far: A.voyFar(), t: A.temp(), under: A.voyUnder(), fire: A.engBuilders().map(c => A.engFire(c, 1)), line: W.hist.filter(e => /last blue jet gutters/.test(e.h)).length }); }'''))
        check('or the engines fail and the world is lost: told, and Lost in the Dark ends the story', r['out'] == 'lost' and r['ended'] == 'lost' and r2['line'] == 1, f'{r} {r2}')
        check('a lost world stays dark and frozen, its peoples under the ice, its engines dead', r2['far'] > .99 and r2['t'] < -30 and r2['under'] and all(f == 0 for f in r2['fire']), str(r2))
        await pg.wait_for_timeout(2600)
        epi = await ev("() => document.querySelector('#modal').classList.contains('open') ? document.querySelector('#dialog').innerText : ''")
        check('with its own epilogue', 'Lost in the Dark' in epi, repr(epi[:120]))
        await ev("() => { const m = document.querySelector('#modal'); if (m) m.classList.remove('open'); }")
        # natural odds over many voyages (the real roll)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; let lost = 0, n = 400; for (let i = 0; i < n; i++) { W.fates.ended = null; W.voy = null; A.voyBegin(); W.voy.said = 127; W.voy.jup = { wars: 0, out: 'clear' }; W.voy.t0 = W.simTime - A.VOY.VOY_SPAN - .1; A.voyTick(.001); if (W.voy.out === 'lost') lost++; }
          const p = A.voyLossChance(); W.voy = null; W.fates.ended = null; return JSON.stringify({ share: lost / n, p }); }'''))
        check('the roll matches the odds over many voyages', abs(r['share'] - r['p']) < .07, str(r))
        # saving
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; W.voy = { t0: 10, y0: 40000, said: 300, done: false, jup: { wars: 0, out: 'clear' }, out: 'arrive', dest: 2, t1: 50.5 }; const d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d)));
          const bad = JSON.parse(JSON.stringify(d)); bad.voy.out = 'eaten'; bad.voy.dest = 77; bad.voy.t1 = 'soon'; const b2 = A.sanitizeWorld(bad); A.loadWorld(d); return JSON.stringify({ back: back.voy, loaded: A.W.voy, bad: b2.voy, ns: A.newSun() && A.newSun()[0] }); }'''))
        check('arrival state is saved and loaded back, and the new sun with it', r['back']['out'] == 'arrive' and r['back']['dest'] == 2 and r['back']['t1'] == 50.5 and r['loaded'] == r['back'] and r['ns'] == 'Epsilon Eridani', str(r['back']))
        check('bad values are dropped or clamped', r['bad']['out'] is None and r['bad']['dest'] == 4 and r['bad']['t1'] is None, str(r['bad']))
        print('errors:', errs[:3] if errs else 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
