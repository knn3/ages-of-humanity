# AGI-01: a machine autonomy meter for each people, shown on its card, pushing the Waking Machines
import asyncio, json
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

# run four peoples of each character at an age for a while; return their meters
RISE = r'''([era, secs]) => { const A = window.__aoh; A.newWorld(91); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
  const cs = A.W.civs.slice(0, 4), tr = ['Curious', 'Mercantile', 'Warlike', 'Devout'];
  cs.forEach((c, i) => { c.trait = tr[i]; c.era = era; c.tech = 20; c.mach = 0; c.machSaid = 0; });
  A.W.wars = []; for (let i = 0; i < secs * 10; i++) { for (const c of cs) { c.era = era; c.tech = Math.min(c.tech, 60); } A.step(0.1); }
  return JSON.stringify(cs.map(c => +c.mach.toFixed(1))); }'''

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate

        m9 = json.loads(await ev(RISE, [9, 60]))
        m10 = json.loads(await ev(RISE, [10, 60]))
        m11 = json.loads(await ev(RISE, [11, 60]))
        print('  meters after 60 s (Curious, Mercantile, Warlike, Devout): Industrial', m9, 'Information', m10, 'Future', m11)
        check('AGI-01 no machine autonomy before the Information Age', max(m9) == 0, str(m9))
        check('AGI-01 the meter rises in the Information Age', min(m10) > 0, str(m10))
        check('AGI-01 it rises faster in the Future Age', all(b > a for a, b in zip(m10, m11)), f'{m10} {m11}')
        check('AGI-01 Curious fastest, Devout slowest', m11[0] == max(m11) and m11[3] == min(m11) and m11[0] > 2 * m11[3], str(m11))

        # an AI Awakening gives a jump at once and speeds the rise while it lasts
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(92); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const [a, b] = A.W.civs; for (const c of [a, b]) { c.era = 11; c.tech = 30; c.trait = 'Warlike'; c.mach = 10; c.machSaid = 0; }
          A.applyEvent(A.findEvent('ai'), a.x); const jump = a.mach;
          // mute reactions (a random ban would knock the meter back) so only the speed-up is measured
          for (let i = 0; i < 200; i++) { for (const c of [a, b]) { c.era = 11; c.tech = Math.min(c.tech, 60); c.lastReact = 1e12; } A.step(0.1); }
          return JSON.stringify({ jump: +jump.toFixed(1), a: +a.mach.toFixed(1), b: +b.mach.toFixed(1), ai: A.W.fates.ai }); }'''))
        check('AGI-01 an AI Awakening hands the machines a big step', r['jump'] >= 25, str(r))
        check('AGI-01 and the meter climbs faster while it lasts', r['a'] - r['jump'] > 2 * (r['b'] - 10), str(r))

        # chronicle milestones; the card shows the row only from the Information Age; the chip when machines are in charge
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(93); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const [a, b] = A.W.civs; a.era = 11; b.era = 3; b.mach = 0; a.mach = 0; a.machSaid = 0; A.machAdd(a, 95); A.updateUI();
          const card = id => document.querySelector(`#civs .civ[data-id="${id}"]`);
          const row = el => { const d = el.querySelector('dt.mrow'); return d && d.style.display !== 'none'; };
          const said = A.W.chron.filter(e => /thinking machines|write most of their laws|decide almost everything/.test(e.h)).length;
          return JSON.stringify({ said, saidN: a.machSaid, rowA: row(card(a.id)), rowB: row(card(b.id)), val: card(a.id).querySelector('[data-f="mach"]').textContent, chip: /Machines in charge/.test(card(a.id).innerText) }); }'''))
        check('AGI-01 chronicle lines as the machines take over (30, 60, 90)', r['said'] == 3 and r['saidN'] == 3, str(r))
        check('AGI-01 the meter shows on the people card from the Information Age', r['rowA'] and not r['rowB'] and r['val'] == '95', str(r))
        check('AGI-01 "Machines in charge" chip', r['chip'])

        # the meter pushes the fate
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(94); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          for (const c of A.W.civs) { c.trait = 'Warlike'; c.mach = 0; } A.W.fates.ai = 0; const lo = A.fateDrives().agi;
          A.W.civs[0].mach = 90; const one = A.fateDrives().agi; for (const c of A.W.civs) c.mach = 90; const all = A.fateDrives().agi;
          return JSON.stringify({ lo: +lo.toFixed(3), one: +one.toFixed(3), all: +all.toFixed(3) }); }'''))
        check('AGI-01 the meter pushes the Waking Machines', r['one'] > r['lo'] + .3 and r['all'] > r['one'], str(r))

        # saves keep it, old saves load with zero; a new cycle starts with none
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(95); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const c = A.W.civs[0]; c.era = 11; A.machAdd(c, 44); const s = JSON.parse(JSON.stringify(A.serialize()));
          const w = A.sanitizeWorld(s); for (const k of s.civs) { delete k.mach; delete k.machSaid; } const old = A.sanitizeWorld(s);
          s.civs[0].mach = 'junk'; s.civs[0].machSaid = 99; const bad = A.sanitizeWorld(s);
          A.reachEnding('collapse'); A.riseAgain();
          return JSON.stringify({ saved: Math.round(w.civs[0].mach), said: w.civs[0].machSaid, old: old.civs[0].mach, bad: bad.civs[0].mach, badSaid: bad.civs[0].machSaid, after: c.mach }); }'''))
        check('AGI-01 the meter is saved and sanitised (old saves load with 0)', r['saved'] == 44 and r['said'] == 1 and r['old'] == 0 and r['bad'] == 0 and r['badSaid'] == 3, str(r))
        check('AGI-01 a new cycle begins without thinking machines', r['after'] == 0, str(r))

        cid = await ev(r'''() => { const A = window.__aoh; A.newWorld(96); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); const c = A.W.civs[0]; c.era = 11; A.machAdd(c, 82); A.updateUI(); window.scrollTo(0, 0); return c.id; }''')
        await pg.wait_for_timeout(300)
        card = await pg.query_selector(f'#civs .civ[data-id="{cid}"]')
        if card: await card.screenshot(path='agi01_card.png')
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
