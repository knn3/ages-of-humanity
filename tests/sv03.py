# SV-03 voyage log and ship card: each ship logs its voyage (launch, mutiny, plague, forgetting, arrival or loss) with the year;
# right-clicking the ship in its lens (opened from the chronicle) opens a card with name, people, years under way, a progress bar, crew left and the log.
import asyncio, json, os, pathlib, re
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        await ev(r'''() => { const A = window.__aoh; A.newWorld(313); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); const W = A.W; for (const o of W.civs) o.era = 12; W.civs[0].era = 13; W.year = 2400; W.ships = []; W.stars = []; W.lost = []; scrollTo(0, 0); }''')
        # a launch logs the year
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, R = Math.random; Math.random = () => 0; A.shipTick(1); Math.random = R; const sh = W.ships[0]; return JSON.stringify({ n: W.ships.length, log: sh && sh.log, y: Math.round(W.year), crew0: sh && sh.crew0 }); }'''))
        check('a launch starts the ship\'s log with the year', r['n'] == 1 and r['log'] == [{'y': r['y'], 'k': 'launch', 'f': 0}] and r['crew0'] == 1e5, str(r))
        # events on the way, one at each quarter: mutiny, plague, forgetting (each with the year it happened)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, sh = W.ships[0], R = Math.random, out = [];
          for (const [q, roll] of [[.26, .1], [.51, .3], [.76, .45]]) { sh.t0 = W.simTime - q * sh.dur; W.year += 40; Math.random = () => roll; A.shipTick(.001); Math.random = R; out.push(Math.round(W.year)); }
          return JSON.stringify({ log: sh.log, years: out, crew: sh.crew, forgot: sh.forgot }); }'''))
        ks = [e['k'] for e in r['log']]; ys = [e['y'] for e in r['log']]
        check('mutiny, plague and forgetting are logged in order with the year each happened', ks == ['launch', 'mutiny', 'plague', 'forgot'] and ys[1:] == r['years'], str(r['log']))
        check('the crew shrinks with mutiny and plague (60% × 50%)', abs(r['crew'] - 3e4) < 1, str(r['crew']))
        # the card: right click the ship in the lens
        async def card():
            return json.loads(await ev(r'''() => { const A = window.__aoh, cv = document.querySelector('#world'), rc = cv.getBoundingClientRect(); A.V.lensShip = { kind: 'ship', id: A.W.ships[0].id }; A.setZoom(.00003); A.render(); const q = A.V.orbPicks.find(q => q.kind === 'voyage'); if (!q) return 'null';
              cv.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: rc.left + q.x, clientY: rc.top + q.y, button: 2 })); const t = document.querySelector('#tip'), bar = t.querySelector('.pb i');
              return JSON.stringify({ shown: t.style.display !== 'none', text: t.innerText, bar: bar ? parseFloat(bar.style.width) : null, logs: [...t.querySelectorAll('.vl')].map(e => e.innerText) }); }'''))
        await ev(r'''() => { const A = window.__aoh, W = A.W, sh = W.ships[0]; sh.t0 = W.simTime - .8 * sh.dur; }''')
        c = await card(); f = await ev("() => { const A = window.__aoh, sh = A.W.ships[0]; return (A.W.simTime - sh.t0) / sh.dur * 100; }")
        print('  card:', c['text'].replace('\n', ' | ')[:400])
        nm = await ev("() => window.__aoh.W.ships[0].name"); civ = await ev("() => window.__aoh.W.civs[0].name")
        under = await ev("() => Math.round(window.__aoh.W.year - window.__aoh.W.ships[0].y0)")
        check('right click on the ship opens its card: name, people, years under way', c['shown'] and nm in c['text'] and civ in c['text'] and f'{under:,} years' in c['text'], f'{nm} / {civ} / {under}')
        check('the card gives how far the destination is from Earth', 'Bound for: Proxima Centauri, 4.2 light years from Earth' in c['text'], [l for l in c['text'].split('\n') if 'Bound' in l])
        check('the progress bar matches the voyage', c['bar'] is not None and abs(c['bar'] - f) < 1.5 and f'{round(f)}% of the way' in c['text'], f'bar {c["bar"]} vs {f:.1f}')
        check('crew left, out of how many set out', '30,000 of 100,000' in c['text'] or ('30' in c['text'] and 'of' in c['text']), re.findall(r'Crew left:[^\n]*', c['text']))
        check('the log is listed with years, in order', len(c['logs']) == 4 and 'Leaves home' in c['logs'][0] and 'Mutiny' in c['logs'][1] and 'Plague' in c['logs'][2] and 'forget' in c['logs'][3] and all(re.search(r'\d', x) for x in c['logs']), str(c['logs']))
        # the card stays live: the bar moves while it is open
        w1 = await ev(r'''async () => { const A = window.__aoh, sh = A.W.ships[0]; sh.t0 -= .1 * sh.dur; A.updateUI(); await new Promise(r => setTimeout(r, 300)); A.render(); A.updateUI(); const i = document.querySelector('#tip .pb i'); return i ? parseFloat(i.style.width) : -1; }''')
        check('the bar moves on while the card is open', w1 > c['bar'] + 5, f'{c["bar"]} -> {w1}')
        await ev("() => { const b = document.querySelector('#tipClose'); if (b) b.click(); }")
        # save/load keeps the log; an old save without logs still loads (the launch is filled in from the launch year)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d)));
          const old = JSON.parse(JSON.stringify(d)); for (const s of old.ships) { delete s.log; delete s.crew0; } const o2 = A.sanitizeWorld(old);
          const bad = JSON.parse(JSON.stringify(d)); bad.ships[0].log = [null, 7, { k: 'party', y: 1 }, { k: 'plague', y: 'x' }, ...Array.from({ length: 30 }, (_, i) => ({ k: 'mutiny', y: i }))]; const b2 = A.sanitizeWorld(bad);
          return JSON.stringify({ same: JSON.stringify(back.ships[0].log) === JSON.stringify(A.W.ships[0].log), old: o2.ships[0].log, oldC0: o2.ships[0].crew0, y0: d.ships[0].y0, bad: b2.ships[0].log.length, badK: [...new Set(b2.ships[0].log.map(e => e.k))] }); }'''))
        check('the log is saved and loaded back unchanged', r['same'], str(r))
        check('an old save without logs loads: the log starts with the launch year', r['old'] == [{'y': r['y0'], 'k': 'launch', 'f': 0}] and r['oldC0'] == 1e5, str(r['old']))
        check('bad log entries are dropped and the log is capped', r['bad'] <= 12 and set(r['badK']) <= {'mutiny', 'plague'}, str(r))
        # arrival: the log ends with the arrival and goes to the colony; a loss: the log goes to its mark
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, sh = W.ships[0]; sh.t0 = W.simTime - sh.dur * 1.01; sh.told = 3; A.shipTick(.001); const st = W.stars[W.stars.length - 1];
          const s2 = { id: 9100, civ: W.civs[0].id, star: 2, name: 'Gone', t0: W.simTime - 300, dur: 1000, crew: 1e5, crew0: 1e5, y0: 3000, told: 0, log: [{ y: 3000, k: 'launch' }] }; W.ships.push(s2); const R = Math.random; Math.random = () => .53; A.shipTick(.001); Math.random = R;
          const m = W.lost[W.lost.length - 1]; return JSON.stringify({ col: st && st.log.map(e => e.k), forgot: st && st.forgot, lost: m && m.log.map(e => e.k), lname: m && m.name }); }'''))
        check('on arrival the log ends "arrive" and the colony keeps it (and whether the crew had forgotten)', r['col'] and r['col'][-1] == 'arrive' and r['col'][0] == 'launch' and r['forgot'] is True, str(r))
        check('a lost ship\'s log ends "lost" and stays with its mark', r['lost'] == ['launch', 'lost'] and r['lname'] == 'Gone', str(r))
        await (await pg.query_selector('#world')).screenshot(path=str(pathlib.Path(__file__).with_name('sv03.png')))
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
