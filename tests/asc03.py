# ASC-03 the holdouts: past ASC_SPLIT those who refuse break away as a people of their own on one edge of the land; Devout refusers
# are holdouts from the start; tension with the uploaded grows (by character, border), with lines and sabotage, and ends in war or an
# uneasy peace; in war the uploaded fly drones; holdouts who win pull the plugs (minds lost); card, data centre info, panel; saved.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))
SETUP = open(pathlib.Path(__file__).with_name('asc01.py')).read().split("SETUP = r'''")[1].split("'''")[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        ids = {t: i for i, t in json.loads(await ev(SETUP))}
        cu, dv, me = ids['Curious'], ids['Devout'], ids['Mercantile']
        r = json.loads(await ev(r'''(d) => { const A = window.__aoh, W = A.W; A.ascTick(1); return JSON.stringify({ h: W.asc.hold[d], n: Object.keys(W.asc.hold).length }); }''', dv))
        check('a Devout people that refuses is a holdout people from the start', r['h'] and r['h']['from'] is None and r['n'] == 1, str(r))
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, p = W.civs.find(c => c.id === a); W.wars = []; W.asc.up[a] = A.ASC.ASC_SPLIT - .002; const n0 = W.civs.length, pop0 = p.pop, l0 = p.l, r0 = p.r;
          A.ascTick(1); A.ascTick(1); A.ascTick(1); const h = W.civs[W.civs.length - 1], H = W.asc.hold[h.id], share = h.pop / (h.pop + p.pop);
          for (let i = 0; i < 20; i++) A.ascTick(1);
          return JSON.stringify({ n: W.civs.length - n0, name: h.name, named: A.HOLD_NAMES.includes(h.name), from: H && H.from, era: h.era === p.era, inside: h.l >= l0 - 1 && h.r <= r0 + 1, apart: h.l > p.r || h.r < p.l, share, hup: A.ascOf(h), lines: W.hist.filter(e => /break away and call themselves/.test(e.h)).length, trait: h.trait }); }''', cu))
        check('past the split point those who refuse break away as a people of their own, once', r['n'] == 1 and r['named'] and r['from'] == cu and r['era'] and r['lines'] == 1, str(r))
        check('they take one edge of the old land, apart from the uploaded, with most of the bodies left', r['inside'] and r['apart'] and .5 < r['share'] < .7, str(r))
        check('the holdouts never upload', r['hup'] == 0 and r['trait'] in ('Devout', 'Warlike'), str(r))
        T = (await ev("() => window.__aoh.ASC"))['ASC_TEN']
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, p = W.civs.find(c => c.id === a), h = W.civs[W.civs.length - 1], H = W.asc.hold[h.id]; W.wars = [];
          const run = (tr, n) => { h.trait = tr; H.ten = 0; H.said = 0; H.out = null; for (let i = 0; i < n; i++) A.ascHoldTick(1); return H.ten; };
          const foe = A.ascFoe(h) === p, b = A.W.civs && true; const tw = run('Warlike', 15), td = run('Devout', 15); h.trait = 'Devout';
          W.asc.minds[a] = 1e9; H.ten = 0; H.said = 0; for (let i = 0; i < 400 && H.ten < .99 && !H.out; i++) { W.wars = []; A.ascHoldTick(.5); }
          const cnt = re => W.hist.filter(e => re.test(e.h) && e.h.includes(h.name)).length;
          return JSON.stringify({ foe, tw, td, tomb: cnt(/data centres of .* tombs/), sab: cnt(/Saboteurs from/), minds: W.asc.minds[a], ten: H.ten }); }''', cu))
        check('the holdouts face the people they broke from; tension grows faster for the Warlike', r['foe'] and r['tw'] > r['td'] * 1.2 and r['td'] > 0, str(r))
        check('the chronicle tells of the quarrel, then of sabotage that costs the uploaded some minds', r['tomb'] == 1 and r['sab'] == 1 and r['minds'] < 1e9, str(r))
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, p = W.civs.find(c => c.id === a), h = W.civs[W.civs.length - 1], H = W.asc.hold[h.id];
          W.wars = []; H.out = null; A.ascResolve(h, p, H, 'peace'); const peace = { out: H.out, war: W.wars.length, rel: A.W.rel && true };
          H.out = null; A.ascResolve(h, p, H, 'war'); const war = { out: H.out, atWar: W.wars.some(w => (w.a === h.id && w.b === p.id) || (w.b === h.id && w.a === p.id)) };
          const cnt = re => W.hist.filter(e => re.test(e.h) && e.h.includes(h.name)).length;
          h.trait = 'Warlike'; p.trait = 'Curious'; const cw = A.ascWarChance(h, p); h.trait = 'Devout'; p.trait = 'Mercantile'; const cm = A.ascWarChance(h, p); p.trait = 'Curious';
          return JSON.stringify({ peace, war, lp: cnt(/sign an uneasy peace/), lw: cnt(/march on the data centres/), cw, cm }); }''', cu))
        check('full tension ends in an uneasy peace or a war between the two', r['peace']['out'] == 'peace' and r['peace']['war'] == 0 and r['war']['out'] == 'war' and r['war']['atWar'] and r['lp'] == 1 and r['lw'] == 1, str(r))
        check('war is likelier with Warlike holdouts, peace likelier with Mercantile neighbours', r['cw'] > .6 and r['cm'] < .35, str(r))
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, p = W.civs.find(c => c.id === a), h = W.civs[W.civs.length - 1], o = W.civs.find(c => c.alive && c.trait === 'Warlike' && c.id !== h.id);
          const own = A.ascHoldWar(h, p), other = o ? A.ascHoldWar(h, o) : false; return JSON.stringify({ own, other }); }''', cu))
        check('the holdouts’ own war is known as such (and slow to end in a treaty)', r['own'] and not r['other'], str(r))
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, p = W.civs.find(c => c.id === a); const u = W.asc.up[a]; W.asc.up[a] = 0; const s0 = A.strength(p); W.asc.up[a] = 1; const s1 = A.strength(p); W.asc.up[a] = u; return JSON.stringify({ k: s1 / s0 }); }''', cu))
        check('the uploaded fight with drones: stronger the more have uploaded', abs(r['k'] - 1.2) < .01, str(r))
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, p = W.civs.find(c => c.id === a), h = W.civs[W.civs.length - 1], H = W.asc.hold[h.id]; const cnt = re => W.hist.filter(e => re.test(e.h) && e.h.includes(h.name)).length;
          W.asc.minds[a] = 1e9; let w = W.wars.find(w => w.a === h.id || w.b === h.id); A.endWar(w, 'victory', h, p); const won = { m: W.asc.minds[a], end: H.end, l: cnt(/pull the plugs on whole halls/) };
          H.end = null; A.startWar(h, p); w = W.wars.find(w => w.a === h.id || w.b === h.id); A.endWar(w, 'victory', p, h); const lost = { end: H.end, l: cnt(/Drones flown by the uploaded minds/) };
          H.end = null; A.startWar(h, p); w = W.wars.find(w => w.a === h.id || w.b === h.id); A.endWar(w, 'treaty'); const tr = H.end;
          A.startWar(h, p); w = W.wars.find(w => w.a === h.id || w.b === h.id); A.endWar(w, 'victory', p, h); const again = { end: H.end, l: cnt(/Drones flown by the uploaded minds/) };
          H.end = null; H.out = 'peace'; A.startWar(h, p); w = W.wars.find(w => w.a === h.id || w.b === h.id); A.endWar(w, 'victory', h, p); const ord = { end: H.end, m: W.asc.minds[a] }; H.out = 'war';
          return JSON.stringify({ won, lost, tr, again, ord }); }''', cu))
        check('holdouts who win storm the data centres and pull the plugs: minds are lost', r['won']['m'] == 6e8 and r['won']['end'] == 'won' and r['won']['l'] == 1, str(r))
        check('if the uploaded win, their drones drive the holdouts back; a treaty is noted too', r['lost']['end'] == 'lost' and r['lost']['l'] == 1 and r['tr'] == 'treaty', str(r))
        check('only the holdouts’ own war ends that way, once; later ordinary wars between them are ordinary', r['again']['end'] == 'treaty' and r['again']['l'] == 1 and r['ord']['end'] is None and r['ord']['m'] == 6e8, str(r))
        r = json.loads(await ev(r'''(a) => { const A = window.__aoh, W = A.W, p = W.civs.find(c => c.id === a), h = W.civs[W.civs.length - 1], H = W.asc.hold[h.id]; H.end = null; H.out = null; H.ten = .42; A.updateUI();
          const card = A.tipBody({ civ: h })[1].replace(/<[^>]+>/g, ' '), clock = document.querySelector('#futures').innerText;
          A.render(); const dc = A.tipBody({ p: { kind: 'datacentre', d: { c: p } } })[1].replace(/<[^>]+>/g, ' ');
          return JSON.stringify({ card, clock, dc }); }''', cu))
        check('the holdouts’ card says whom they broke from and the tension', 'broke away from the' in r['card'] and 'tension 42%' in r['card'], r['card'][-140:])
        check('the data centre info names the holdouts nearby, and the panel counts them', 'Holdouts' in r['dc'] and 'holdout peoples' in r['clock'], r['dc'][-120:] + ' || ' + r['clock'].replace('\n', ' ')[:120])
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; W.asc.hold = { 7: { from: 3, ten: .5, out: 'war', said: 3, foe: 3, end: 'won' }, 9: { from: null, ten: .1, out: null, said: 0, foe: null, end: null } };
          const d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d))); const bad = JSON.parse(JSON.stringify(d)); bad.asc.hold = { 7: { from: 'x', ten: 9, out: 'boom', said: 99, end: 'meh' }, x: {}, 8: 5 };
          const b2 = A.sanitizeWorld(bad); const old = JSON.parse(JSON.stringify(d)); delete old.asc.hold; return JSON.stringify({ back: back.asc.hold, bad: b2.asc.hold, old: A.sanitizeWorld(old).asc.hold }); }'''))
        check('holdouts are saved and loaded back; bad values are dropped or clamped; old saves have none',
              r['back'] == {'7': {'from': 3, 'ten': .5, 'out': 'war', 'said': 3, 'foe': 3, 'end': 'won'}, '9': {'from': None, 'ten': .1, 'out': None, 'said': 0, 'foe': None, 'end': None}}
              and r['bad'] == {'7': {'from': None, 'ten': 1, 'out': None, 'said': 3, 'foe': None, 'end': None}} and r['old'] == {}, str(r))
        print('errors:', errs[:3] if errs else 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
