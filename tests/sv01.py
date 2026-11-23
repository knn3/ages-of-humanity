# SV-01 neighbourhood lens: a round inset beside the Sun in the galaxy view, showing the target stars on a log scale,
# only while a ship is in flight or a star is settled. The galaxy keeps only faint ticks; nothing is hidden under the Sun.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

SETUP = r'''([n, ns]) => { const A = window.__aoh; A.newWorld(4242); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); const cs = A.W.civs; for (const o of cs) o.era = 14;
  A.W.ships = []; A.W.stars = [];
  for (let i = 0; i < n; i++) A.W.stars.push({ star: i, civ: cs[i % cs.length].id, name: 'Col ' + i, pop: 1e5, t0: 3000 });
  for (let i = n; i < n + ns; i++) A.W.ships.push({ id: 9000 + i, civ: cs[i % cs.length].id, star: i, name: 'Ship ' + i, t0: A.W.simTime - 100, dur: 400, crew: 1e5, y0: 3000, told: 0 });
  window.scrollTo(0, 0); }'''
STATE = r'''(z) => { const A = window.__aoh, cv = document.querySelector('#world'); A.setZoom(z); A.render(); const L = A.V.lens, sun = A.V.orbPicks.find(q => q.kind === 'sungal'), sx = A.V.sunXY;
  const picks = A.V.orbPicks.filter(q => q.kind === 'voyage' || q.kind === 'starcol').map(q => ({ kind: q.kind, x: q.x, y: q.y, name: q.d.name }));
  return JSON.stringify({ on: !!L, L: L && { x: L.x, y: L.y, r: L.r }, labels: L ? L.labels : [], stars: L ? L.stars : [], picks, sun: sx, w: cv.clientWidth, h: cv.clientHeight }); }'''
TEXTS = r'''() => { const cv = document.querySelector('#world'), c2 = cv.getContext('2d'), got = []; const f = c2.fillText, sT = c2.strokeText; c2.fillText = function (t, ...a) { got.push(String(t)); return f.call(this, t, ...a); }; c2.strokeText = function (t, ...a) { got.push(String(t)); return sT.call(this, t, ...a); };
  let lines = 0; const st = c2.stroke; c2.stroke = function (...a) { lines++; return st.apply(this, a); };
  window.__aoh.render(); c2.fillText = f; c2.strokeText = sT; c2.stroke = st; return JSON.stringify(got); }'''

def overl(a, b):
    return a['x'] < b['x'] + b['w'] and a['x'] + a['w'] > b['x'] and a['y'] < b['y'] + b['h'] and a['y'] + a['h'] > b['y']

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        for vw, vh in [(1600, 1000), (1100, 760), (700, 900)]:
            pg = await b.new_page(viewport={'width': vw, 'height': vh}); errs = []
            pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
            await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
            await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
            ev = pg.evaluate; tag = f'{vw}x{vh}'
            # nothing out there: no lens
            await ev(SETUP, [0, 0])
            r = json.loads(await ev(STATE, .00002))
            check(f'{tag}: no ships and no settled stars, no lens', not r['on'], str(r['on']))
            # one ship: the lens appears in the galaxy view only
            await ev(SETUP, [0, 1])
            r0 = json.loads(await ev(STATE, .0004)); r1 = json.loads(await ev(STATE, .00002))
            check(f'{tag}: a ship in flight shows the lens in the galaxy view, not in the solar system', r1['on'] and not r0['on'], str([r0['on'], r1['on']]))
            # every target star at once: 10 settled + 4 ships
            await ev(SETUP, [10, 4])
            for z in [.00004, .00002]:
                r = json.loads(await ev(STATE, z)); L = r['L']
                inside = L and L['x'] - L['r'] >= 0 and L['x'] + L['r'] <= r['w'] and L['y'] - L['r'] - 20 >= 0 and L['y'] + L['r'] <= r['h']
                check(f'{tag} z={z}: the lens is on screen (title too) and does not cover the Sun', bool(inside) and ((r['sun'][0] - L['x']) ** 2 + (r['sun'][1] - L['y']) ** 2) ** .5 > L['r'] + 5, str([L, r['sun']]))
                st = r['stars']; md = min(((a['x'] - c['x']) ** 2 + (a['y'] - c['y']) ** 2) ** .5 for i, a in enumerate(st) for c in st[i + 1:])
                lab = r['labels']; lo = [(a['name'], c['name']) for i, a in enumerate(lab) for c in lab[i + 1:] if overl(a, c)]
                dots = [{'x': s['x'] - 3, 'y': s['y'] - 3, 'w': 6, 'h': 6} for s in st]; ld = [(a['name']) for a in lab for d in dots if overl(a, d)]
                check(f'{tag} z={z}: all 14 target stars shown, at least 9 px apart', len(st) == 14 and md >= 9, f'n={len(st)} min={md:.1f}')
                check(f'{tag} z={z}: every target star labelled, no labels overlap each other or a star', len(lab) == 14 and not lo and not ld, str([lo, ld]))
                pin = all(((q['x'] - L['x']) ** 2 + (q['y'] - L['y']) ** 2) ** .5 <= L['r'] for q in r['picks'])
                sund = min(((q['x'] - r['sun'][0]) ** 2 + (q['y'] - r['sun'][1]) ** 2) ** .5 for q in r['picks'])
                check(f'{tag} z={z}: ships and colonies are picked in the lens only, none under the Sun', len(r['picks']) == 14 and pin and sund > 20, f'n={len(r["picks"])} in={pin} sun={sund:.0f}')
            # no labels on the galaxy itself: only the lens title and the target names are drawn
            t = json.loads(await ev(TEXTS)); names = set(json.loads(await ev("() => JSON.stringify(window.__aoh.XSTARS.map(s => s[0]))")))
            extra = [x for x in t if x not in names and x != 'The Sun’s neighbourhood']
            check(f'{tag}: the galaxy draws no labels of its own (only the lens title and its star names)', not extra and 'The Sun’s neighbourhood' in t, str(extra[:5]))
            # right click a ship and a settled star in the lens
            got = {}
            for kind in ['voyage', 'starcol']:
                got[kind] = await ev(r'''(kind) => { const A = window.__aoh, cv = document.querySelector('#world'), r = cv.getBoundingClientRect(); A.render(); const q = A.V.orbPicks.find(q => q.kind === kind); if (!q) return 'none';
                  cv.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: r.left + q.x, clientY: r.top + q.y, button: 2 }));
                  const t = document.querySelector('#tip'), txt = t.style.display !== 'none' ? t.innerText.replace(/\n/g, ' | ') : ''; const b = document.querySelector('#tipClose'); if (b) b.click(); return txt.slice(0, 600); }''', kind)
            check(f'{tag}: right click opens the ship and the settled star from the lens', 'Ship ' in got['voyage'] and 'Of the way' in got['voyage'] and 'Founded by' in got['starcol'], str(got))
            # an empty spot inside the lens opens nothing from the galaxy behind it
            e = await ev(r'''() => { const A = window.__aoh; A.render(); const L = A.V.lens; const cv = document.querySelector('#world'), r = cv.getBoundingClientRect();
              cv.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: r.left + L.x + L.r * .1, clientY: r.top + L.y - L.r * .97, button: 2 }));
              const t = document.querySelector('#tip'), txt = t.style.display !== 'none' ? t.innerText : ''; const b = document.querySelector('#tipClose'); if (b) b.click(); return txt.slice(0, 60); }''')
            check(f'{tag}: an empty spot in the lens opens nothing behind it', e == '', e)
            await ev("() => { window.__aoh.setZoom(.00002); window.__aoh.render(); }")
            # two colonies at one star (every star taken): each keeps its own spot to click
            d = await ev(r'''() => { const A = window.__aoh; A.W.stars.push({ star: 0, civ: A.W.civs[1].id, name: 'Twin', pop: 1e4, t0: 3100 }); A.setZoom(.00002); A.render();
              const q = A.V.orbPicks.filter(q => q.kind === 'starcol' && q.d.star === 0); A.W.stars.pop(); return q.length === 2 ? Math.hypot(q[0].x - q[1].x, q[0].y - q[1].y) : -1; }''')
            check(f'{tag}: two colonies at the same star can each be clicked', d >= 8, str(d))
            await (await pg.query_selector('#world')).screenshot(path=str(pathlib.Path(__file__).with_name(f'sv01_{tag}.png')))
            print('\n'.join(errs) or 'no errors')
            await pg.close()
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
