# Space resources (Helium-3 on the Moon, the asteroid mine in the belt, the ice moon of Jupiter) are there from the start but
# no one knows of them until a people reaches the Future Age: before that they are not drawn, not clickable and not listed in
# the Moon or Jupiter close-up, unless someone owns one or the player placed it. Placed ones survive save and load.
import asyncio, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(os.environ.get('GAME') or pathlib.Path(__file__).resolve().parents[1].joinpath('index.html')).resolve().as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

SEE = r'''(era) => { const A = window.__aoh; A.UI.paused = true; if (era != null) for (const c of A.W.civs) c.era = era;
  A.setZoom(.004); A.render(); A.render();
  const claims = A.V.orbPicks.filter(p => p.kind === 'claim').length;
  const lines = [...A.bodyLines('Moon'), ...A.bodyLines('Jupiter')].filter(l => /Helium-3|Ice Moon/.test(l)).length;
  return { claims, lines, max: Math.max(...A.W.civs.filter(c => c.alive).map(c => c.era)) }; }'''

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700)
        await pg.evaluate("() => { const A = window.__aoh; A.newWorld(4242); A.UI.random = false; for (let i = 0; i < 10; i++) A.step(0.1); window.scrollTo(0, 0); }")
        s0 = await pg.evaluate(SEE, 1)
        check('Stone Age: no space resources drawn or clickable in the solar system', s0['claims'] == 0, str(s0))
        check('Stone Age: the Moon and Jupiter close-ups do not list Helium-3 or the Ice Moon', s0['lines'] == 0, str(s0))
        s10 = await pg.evaluate(SEE, 10)
        check('Information Age: still unknown', s10['claims'] == 0 and s10['lines'] == 0, str(s10))
        s11 = await pg.evaluate(SEE, 11)
        check('Future Age: the three resources appear (unclaimed)', s11['claims'] == 3 and s11['lines'] == 2, str(s11))
        # a resource someone owns stays shown even if every space people later falls back
        own = await pg.evaluate("() => { const A = window.__aoh; const r = A.W.spaceRes[1]; r.owner = A.W.civs[0].id; return 1; }")
        s1 = await pg.evaluate(SEE, 1)
        check('an owned resource stays shown', s1['claims'] == 1, str(s1))
        # the player places one in the Stone Age: it shows, and keeps showing after save and load
        await pg.evaluate("() => { const A = window.__aoh; A.W.spaceRes[1].owner = null; A.setZoom(.004); A.render(); return A.placeSpace('asteroid'); }")
        s2 = await pg.evaluate(SEE, 1)
        check('a resource the player places shows in the Stone Age', s2['claims'] == 1, str(s2))
        rl = await pg.evaluate("() => { const A = window.__aoh; A.loadWorld(A.sanitizeWorld(JSON.parse(JSON.stringify(A.serialize())))); return A.W.spaceRes.filter(r => r.placed).length; }")
        s3 = await pg.evaluate(SEE, 1)
        check('after save and load the placed one is still shown, the seeded ones still hidden', rl == 1 and s3['claims'] == 1, f'placed {rl}, {s3}')
        old = await pg.evaluate("() => { const A = window.__aoh; const d = JSON.parse(JSON.stringify(A.serialize())); for (const r of d.spaceRes) delete r.placed; d.spaceRes.forEach(r => r.placed = 'yes'); const w = A.sanitizeWorld(d); return w.spaceRes.every(r => r.placed === undefined); }")
        check('saves: only placed: true is kept (old saves and junk load as not placed)', old, str(old))
        print('\n'.join(errs[:5]) or 'no errors')
        check('no page errors', not errs)
        await b.close()
    print(f'{sum(results)}/{len(results)} passed')
asyncio.run(main())
