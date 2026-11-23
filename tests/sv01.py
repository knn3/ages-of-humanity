# Star voyages: the neighbourhood lens is opened only from the chronicle (SV-01 as revised by the user):
# clicking a chronicle line about a ship on its way (or lost) zooms out to the galaxy and opens the lens beside the Sun, showing only the
# Sun, that ship and its destination; a ship that arrived opens a close-up of the world it settled. Esc, a click outside or zooming in
# closes the lens. The galaxy itself keeps only faint ticks for settled stars.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

# a world with 3 ships in flight (one just launched by the real launch code), 2 colonies and a lost ship
SETUP = r'''() => { const A = window.__aoh; A.newWorld(4242); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); const W = A.W, cs = W.civs; W.year = 2400; for (const o of cs) o.era = 12; cs[0].era = 13;
  W.ships = []; W.stars = []; W.lost = []; const R = Math.random; Math.random = () => 0; A.shipTick(1); Math.random = R;
  W.ships.push({ id: 9001, civ: cs[1].id, star: 9, name: 'Far Shore', t0: W.simTime - 400, dur: 1000, crew: 1e5, crew0: 1e5, y0: 2300, told: 1, log: [{ y: 2300, k: 'launch' }] });
  W.ships.push({ id: 9002, civ: cs[2].id, star: 12, name: 'Patience', t0: W.simTime - 700, dur: 1000, crew: 1e5, crew0: 1e5, y0: 2200, told: 2, log: [{ y: 2200, k: 'launch' }] });
  W.stars.push({ star: 4, civ: cs[1].id, name: 'Seedling', pop: 2e5, t0: 2350, sid: 8001, world: 'Verdance', log: [{ y: 2200, k: 'launch' }, { y: 2350, k: 'arrive' }] });
  W.stars.push({ star: 6, civ: cs[3].id, name: 'Morning', pop: 1e5, t0: 2380, sid: 8002, world: 'Lumen', log: [] });
  W.lost.push({ id: 7001, star: 10, civ: cs[2].id, f: .45, t: W.simTime - 2000, name: 'Lantern', log: [{ y: 2250, k: 'launch' }, { y: 2290, k: 'lost' }] });
  A.render(); scrollTo(0, 0); }'''
STATE = r'''() => { const A = window.__aoh, L = A.V.lens; A.render(); const cv = document.querySelector('#world');
  return JSON.stringify({ zoom: A.V.zoom, galK: A.V.zoom <= .00006, lensShip: A.V.lensShip, focus: A.V.focus && { body: A.V.focus.body, world: A.V.focus.st && A.V.focus.st.world }, lens: A.V.lens && { x: A.V.lens.x, y: A.V.lens.y, r: A.V.lens.r, kind: A.V.lens.kind, id: A.V.lens.id, labels: A.V.lens.labels, stars: A.V.lens.stars, ships: A.V.lens.ships },
    picks: A.V.orbPicks.filter(q => q.kind === 'voyage' || q.kind === 'starcol').map(q => ({ kind: q.kind, x: q.x, y: q.y, id: q.d.id })), sun: A.V.sunXY, w: cv.clientWidth, h: cv.clientHeight }); }'''
TEXTS = r'''() => { const cv = document.querySelector('#world'), c2 = cv.getContext('2d'), got = []; const f = c2.fillText, sT = c2.strokeText; c2.fillText = function (t, ...a) { got.push(String(t)); return f.call(this, t, ...a); }; c2.strokeText = function (t, ...a) { got.push(String(t)); return sT.call(this, t, ...a); };
  window.__aoh.render(); c2.fillText = f; c2.strokeText = sT; return JSON.stringify(got); }'''

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        for vw, vh in [(1600, 1000), (1100, 760), (700, 900)]:
            pg = await b.new_page(viewport={'width': vw, 'height': vh}); errs = []
            pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
            await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
            await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
            ev = pg.evaluate; tag = f'{vw}x{vh}'
            await ev(SETUP)
            # 1. no lens on its own, even with ships and colonies out there; the galaxy draws no names and no ship picks
            await ev("() => { window.__aoh.setZoom(.00003); }")
            r = json.loads(await ev(STATE)); t = json.loads(await ev(TEXTS))
            check(f'{tag}: zoomed out with ships and colonies, no lens opens by itself; no names and no ship picks on the galaxy', not r['lens'] and not t and not [q for q in r['picks'] if q['kind'] == 'voyage'], str([bool(r['lens']), t[:3], len(r['picks'])]))
            # the settled stars are dots: a real left click on one opens its world, growing from the dot
            got = json.loads(await ev(r'''async () => { const A = window.__aoh, W = A.W; A.setZoom(.00011); A.render(); const q = A.V.orbPicks.find(q => q.kind === 'starcol' && q.d.sid === 8001); return JSON.stringify(q ? { x: q.x, y: q.y } : null); }'''))
            if got:
                box = await (await pg.query_selector('#world')).bounding_box(); await pg.mouse.click(box['x'] + got['x'], box['y'] + got['y']); await pg.wait_for_timeout(100)
                f = json.loads(await ev("() => JSON.stringify(window.__aoh.V.focus ? { body: window.__aoh.V.focus.body, world: window.__aoh.V.focus.st && window.__aoh.V.focus.st.world, x0: window.__aoh.V.focus.x0, y0: window.__aoh.V.focus.y0 } : null)"))
            check(f'{tag}: a left click on a settled star\'s dot opens its world close-up, growing from the dot', got and f and f['body'] == 'world' and f['world'] == 'Verdance' and abs(f['x0'] - got['x']) < 1 and abs(f['y0'] - got['y']) < 1, str([got, f if got else None]))
            await pg.keyboard.press('Escape')
            # 2. the launch line is a link in the chronicle; a real click zooms out (gliding) and opens the lens for that ship only
            await ev("() => { window.__aoh.setZoom(.4); window.__aoh.render(); scrollTo(0, 0); }")
            li = await ev(r'''() => { const li = document.querySelector('#log li.shiplink'); return li ? JSON.stringify({ sh: +li.dataset.sh, go: !!li.querySelector('.go'), cur: getComputedStyle(li).cursor, text: li.innerText.slice(0, 80) }) : 'null'; }''')
            li = json.loads(li); sid = await ev("() => window.__aoh.W.ships[0].id")
            check(f'{tag}: the launch line in the chronicle is a link (ship id, ⟶ mark, pointer)', li and li['sh'] == sid and li['go'] and li['cur'] == 'pointer', str(li))
            # sample the zoom every frame while the glide runs
            await ev("() => { window.__zs = []; const f = () => { window.__zs.push(window.__aoh.V.zoom); if (window.__zs.length < 400) requestAnimationFrame(f); }; requestAnimationFrame(f); }")
            await pg.locator(f'#log li.shiplink[data-sh="{sid}"]').first.scroll_into_view_if_needed(); await pg.locator(f'#log li.shiplink[data-sh="{sid}"]').first.click()
            await pg.wait_for_timeout(2400); await ev("() => scrollTo(0, 0)"); r = json.loads(await ev(STATE)); zs = await ev("() => window.__zs")
            between = len({round(z, 9) for z in zs if .00003 * 1.05 < z < .4 * .95})
            check(f'{tag}: the click glides out (many frames in between, not a jump) and ends in the galaxy with the lens open on that ship', between >= 5 and abs(r['zoom'] - .00003) < 1e-6 and r['lens'] and r['lens']['kind'] == 'ship' and r['lens']['id'] == sid, f"{between} frames between, end {r['zoom']:.6f} lens {r['lens'] and r['lens']['id']}")
            L = r['lens']; t = json.loads(await ev(TEXTS)); dest = await ev("() => window.__aoh.XSTARS[window.__aoh.W.ships[0].star][0]"); nm = await ev("() => window.__aoh.W.ships[0].name")
            check(f'{tag}: the lens shows only that ship and its destination (one ship, one star, one label, title is the ship)', len(L['ships']) == 1 and len(L['stars']) == 1 and [l['name'] for l in L['labels']] == [dest] and f'The {nm}' in t and len([x for x in t if x not in (f'The {nm}', dest, 'Esc or click outside to close')]) == 0, str(t))
            inside = L['x'] - L['r'] >= 0 and L['x'] + L['r'] <= r['w'] and L['y'] - L['r'] - 22 >= 0 and L['y'] + L['r'] + 20 <= r['h']
            check(f'{tag}: the lens and its title fit on screen, clear of the Sun', inside and ((r['sun'][0] - L['x']) ** 2 + (r['sun'][1] - L['y']) ** 2) ** .5 > L['r'] + 5, str([L['x'], L['y'], L['r'], r['sun']]))
            lab = L['labels'][0]; s0 = L['ships'][0]; d0 = L['stars'][0]
            hit = lambda q, x, y, m: q['x'] - m < x < q['x'] + q['w'] + m and q['y'] - m < y < q['y'] + q['h'] + m
            check(f'{tag}: the destination label is clear of the Sun and the ship', not hit(lab, L['x'], L['y'], 4) and not hit(lab, s0['x'], s0['y'], 4), str([lab, s0]))
            vp = [q for q in r['picks'] if q['kind'] == 'voyage']
            check(f'{tag}: only that ship can be picked as a ship, inside the lens', [q['id'] for q in vp] == [sid] and all(((q['x'] - L['x']) ** 2 + (q['y'] - L['y']) ** 2) ** .5 <= L['r'] for q in vp), str(vp))
            # 3. Esc closes it
            await pg.keyboard.press('Escape'); r = json.loads(await ev(STATE))
            check(f'{tag}: Esc closes the lens', not r['lens'] and not r['lensShip'], str(r['lensShip']))
            # 4. a mid-voyage ship (opened from See all) and a click outside closes it; a click on an empty spot inside does not
            await ev("() => { const A = window.__aoh; A.log('The Far Shore passes the halfway mark.', 'event', 9001); }")
            await ev("() => window.__aoh.openHistory()"); await pg.wait_for_timeout(200)
            await pg.locator('#modal li.shiplink[data-sh="9001"]').first.click(); await pg.wait_for_timeout(2300)
            r = json.loads(await ev(STATE)); modal = await ev("() => document.querySelector('#modal').classList.contains('open')")
            check(f'{tag}: a ship line in See all opens the lens (and the dialog closes)', r['lens'] and r['lens']['id'] == 9001 and not modal, str([r['lens'] and r['lens']['id'], modal]))
            L = r['lens']; box = await (await pg.query_selector('#world')).bounding_box(); await ev("() => scrollTo(0, 0)"); box = await (await pg.query_selector('#world')).bounding_box()
            await pg.mouse.click(box['x'] + L['x'] + L['r'] * .1, box['y'] + L['y'] - L['r'] * .93); r2 = json.loads(await ev(STATE))
            await pg.mouse.click(box['x'] + 20, box['y'] + box['height'] - 20); r3 = json.loads(await ev(STATE))
            check(f'{tag}: a click on an empty spot inside the lens keeps it; a click outside closes it', r2['lens'] and not r3['lens'], str([bool(r2['lens']), bool(r3['lens'])]))
            # 5. zooming back in closes it
            await ev("() => window.__aoh.shipFocus(9002, true)"); r = json.loads(await ev(STATE)); ok1 = r['lens'] and r['lens']['id'] == 9002
            await ev("() => { window.__aoh.setZoom(.003); window.__aoh.render(); window.__aoh.setZoom(.00003); window.__aoh.render(); }"); r = json.loads(await ev(STATE))
            check(f'{tag}: zooming back in to the solar system closes the lens (it does not come back on zooming out)', ok1 and not r['lens'], str(r['lensShip']))
            # 6. a lost ship: the lens shows its course up to where it went silent and its destination
            await ev("() => window.__aoh.shipFocus(7001, true)"); r = json.loads(await ev(STATE)); L = r['lens']
            check(f'{tag}: a lost ship opens the lens with its mark and destination ("The lost …")', L and L['kind'] == 'lost' and L['ships'][0].get('lost') and [l['name'] for l in L['labels']] == ['Kapteyn’s Star'], str(L and L['labels']))
            await pg.keyboard.press('Escape')
            # 7. a ship that arrived: its lines open a close-up of the world it settled
            await ev("() => { window.__aoh.setZoom(.4); window.__aoh.render(); }")
            await ev("() => window.__aoh.shipFocus(8001, true)"); await pg.wait_for_timeout(900); r = json.loads(await ev(STATE)); t = json.loads(await ev(TEXTS))
            check(f'{tag}: a settled ship opens a close-up of its world, titled with the world name', r['focus'] and r['focus']['body'] == 'world' and r['focus']['world'] == 'Verdance' and 'Verdance' in t and not r['lens'], str(r['focus']))
            body = ' '.join(t)
            check(f'{tag}: the close-up tells the star, the founding ship and people, the year, the population and the voyage', 'Epsilon Eridani' in body and 'Seedling' in body and '2350 CE' in body and '200k' in body and 'Leaves home' in body, body[:200])
            await pg.keyboard.press('Escape'); r = json.loads(await ev(STATE))
            check(f'{tag}: Esc closes the close-up', not r['focus'], str(r['focus']))
            # 8. a line whose ship is long gone shows a note instead
            await ev("() => { window.__aoh.shipFocus(424242, true); }"); toast = await ev("() => document.querySelector('#toast').textContent")
            check(f'{tag}: a line about a ship no longer anywhere shows a note', 'Nothing is left' in toast, toast)
            if vw == 1600:
                await ev("() => { window.__aoh.shipFocus(9001, true); window.__aoh.render(); }")
                await (await pg.query_selector('#world')).screenshot(path=str(pathlib.Path(__file__).with_name('sv01_lens.png')))
            print('\n'.join(errs) or 'no errors')
            await pg.close()
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
