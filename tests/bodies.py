# Solar-system view: left click the Sun, the Moon or a planet to zoom in on it (close-up + what is going on); click, Esc or scroll to zoom out; Earth goes back to the globe
import asyncio, json
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

SETUP = r'''() => { const A = window.__aoh; A.newWorld(911); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
  const [a, b] = A.W.civs; for (const c of A.W.civs) { c.era = 13; c.tech = 20; } A.W.wars = [];
  A.foundBase(a, 'mars'); A.foundBase(b, 'mars'); A.foundBase(a, 'moon'); A.W.bases[0].pop = 4e6;
  A.W.colonies = [{ id: 999, name: 'Ares', color: '#d98c5f', trait: 'Curious', body: 'mars', base: 'Olympus', pop: 2e6, parent: a.id, free: false, tension: .4, war: null, era: 12, tech: 0, born: 2100 }];
  for (const r of A.W.spaceRes) r.owner = a.id; A.W.dyson = { by: { [a.id]: 300, [b.id]: 100 }, total: 400, mark: 0 };
  window.scrollTo(0, 0); A.setZoom(.0025); A.render(); A.render(); return 1; }'''
POS = r'''(n) => { const A = window.__aoh, cv = document.querySelector('#world'), r = cv.getBoundingClientRect(); A.render();
  const q = n === 'Sun' ? A.V.sunXY : n === 'Earth' ? [A.V.cx, A.V.cy] : A.V.bodyPos[n]; if (!q) return 'null';
  return JSON.stringify({ x: r.left + q[0], y: r.top + q[1], inView: q[0] > 10 && q[0] < cv.clientWidth - 10 && q[1] > 10 && q[1] < cv.clientHeight - 10, hit: A.bodyAt(q[0], q[1]) }); }'''

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        await ev(SETUP)
        # every body can be found under the pointer
        hits = {}
        for n in ['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn']:
            q = json.loads(await ev(POS, n)); hits[n] = q and q['hit']
        check('each body of the solar system can be picked', all(hits[n] == n for n in hits), str(hits))

        # click Mars with the real mouse: close-up of Mars with its bases and colony
        async def click(n):
            q = json.loads(await ev(POS, n))
            z = await ev("() => window.__aoh.V.zoom")
            while (not q or not q['inView']) and z > .0004:
                z *= .8; await ev("(z) => window.__aoh.setZoom(z)", z); q = json.loads(await ev(POS, n))
            await pg.mouse.click(q['x'], q['y']); await pg.wait_for_timeout(800)
            return q
        q = await click('Mars')
        r = json.loads(await ev("() => { const A = window.__aoh; return JSON.stringify({ focus: A.V.focus && A.V.focus.body, lines: A.bodyLines('Mars') }); }"))
        print('  Mars:', r)
        check('left click on Mars zooms in on it', r['focus'] == 'Mars', str(r))
        check('the close-up tells what is going on: bases with their people, the colony', sum('a base of the' in l for l in r['lines']) == 2 and any('The Ares' in l and 'colony of the' in l for l in r['lines']), str(r['lines']))
        await (await pg.query_selector('#world')).screenshot(path='bodies_mars.png')
        await pg.mouse.click(200, 200); await pg.wait_for_timeout(200)
        r = await ev("() => window.__aoh.V.focus")
        check('a click anywhere zooms back out', r is None, str(r))

        # the Sun: the swarm and who built it; Esc zooms out
        await click('Sun')
        r = json.loads(await ev("() => { const A = window.__aoh; return JSON.stringify({ focus: A.V.focus && A.V.focus.body, lines: A.bodyLines('Sun') }); }"))
        check('the Sun close-up shows the swarm and who built it', r['focus'] == 'Sun' and any('swarm' in l for l in r['lines']) and any('75% of the swarm' in l for l in r['lines']), str(r))
        await (await pg.query_selector('#world')).screenshot(path='bodies_sun.png')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(100)
        check('Esc zooms back out', await ev("() => window.__aoh.V.focus") is None)

        # Jupiter: the ice moons and who mines them; the wheel zooms out
        await click('Jupiter')
        r = json.loads(await ev("() => { const A = window.__aoh; return JSON.stringify({ focus: A.V.focus && A.V.focus.body, lines: A.bodyLines('Jupiter') }); }"))
        check('Jupiter close-up: the ice moon and who mines it', r['focus'] == 'Jupiter' and any('Ice Moon: mined by the' in l for l in r['lines']), str(r))
        z0 = await ev("() => window.__aoh.V.zoom")
        await pg.mouse.move(600, 300); await pg.mouse.wheel(0, 200); await pg.wait_for_timeout(100)
        r = json.loads(await ev("() => JSON.stringify({ f: window.__aoh.V.focus, z: window.__aoh.V.zoom })"))
        check('scrolling zooms back out (without jumping the zoom)', r['f'] is None and abs(r['z'] - z0) < 1e-9, str(r))

        # an empty world: Saturn
        r = await ev("() => window.__aoh.bodyLines('Saturn').join(' ')")
        check('a world no one has reached says so', 'No one has settled here' in r, r)

        # Earth: back down to the globe
        await click('Earth')
        r = json.loads(await ev("() => JSON.stringify({ f: window.__aoh.V.focus, z: window.__aoh.V.zoom })"))
        check('clicking Earth zooms back down to the globe', r['f'] is None and r['z'] > .02, str(r))

        # with a tool selected, a click still uses the tool (no zoom)
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.setZoom(.0025); A.render(); A.setTool({ kind: 'el', type: 'helium3' }); return JSON.stringify(A.UI.tool); }'''))
        q = json.loads(await ev(POS, 'Mars')); n0 = await ev("() => window.__aoh.W.spaceRes.length")
        await pg.mouse.click(q['x'], q['y']); await pg.wait_for_timeout(200)
        r = json.loads(await ev("(n0) => JSON.stringify({ f: window.__aoh.V.focus, placed: window.__aoh.W.spaceRes.length - n0 })", n0))
        check('with a space tool selected, a click places it instead of zooming in', r['f'] is None and r['placed'] == 1, str(r))
        await ev("() => window.__aoh.setTool(null)")
        # the text card never covers the body, its rings, swarm or moons, on wide and narrow screens
        bad = []
        for vw, vh in [(2000, 1000), (1300, 850), (900, 700), (640, 800)]:
            await pg.set_viewport_size({'width': vw, 'height': vh}); await pg.wait_for_timeout(300)
            for n in ['Sun', 'Saturn', 'Jupiter', 'Mars']:
                fb = json.loads(await ev(r'''async (n) => { const A = window.__aoh; A.V.focus = null; A.setZoom(.0015); A.render(); A.focusBody(n); A.V.focus.t0 -= 2000; await new Promise(r => setTimeout(r, 120)); A.render(); return JSON.stringify(A.V.focusBox); }''', n))
                ext = fb['R'] * fb['reach']
                clear = (fb['cx'] + ext <= fb['cardX'] + 1) if fb['side'] else (fb['cy'] + min(fb['reach'], 1.2) * fb['R'] <= fb['cardY'] + 1)
                ov = json.loads(await ev(r'''() => { const cb = document.querySelector('#world').getBoundingClientRect(), b = window.__aoh.V.focusBox, hit = el => { if (!el || el.offsetParent === null) return false; const q = el.getBoundingClientRect(); if (!q.width) return false; const l = q.left - cb.left, r = q.right - cb.left, t = q.top - cb.top, bt = q.bottom - cb.top; return l < b.cardX + b.cardW && r > b.cardX && t < b.cardY + b.cardH && bt > b.cardY; }; return JSON.stringify({ alt: hit(document.querySelector('#alt')), hint: hit(document.querySelector('#hint')) }); }'''))
                if ov['alt'] or ov['hint']: clear = False
                if not clear or fb['R'] < 30: bad.append((vw, n, round(fb['cx'] + ext), round(fb['cardX']), round(fb['R'])))
                if (vw, n) in [(2000, 'Saturn'), (2000, 'Sun'), (640, 'Saturn')]:
                    await (await pg.query_selector('#world')).screenshot(path=f'bodies_{n.lower()}_{vw}.png')
            await ev("() => { window.__aoh.V.focus = null; }")
        check('the text card never covers the body, its rings, swarm or moons, nor the hint bar or altitude box (2000, 1300, 900, 640 wide)', not bad, str(bad))
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
