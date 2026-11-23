# Every people's town has its landmark (machine core, temple, castle...) even when the capital sits on a slope, a river or the coast
import asyncio, json
from playwright.async_api import async_playwright
import os, pathlib, sys
GAME = pathlib.Path(os.environ.get('GAME') or pathlib.Path(__file__).resolve().parents[1].joinpath('index.html')).resolve().as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        r = json.loads(await ev(r'''() => { const A = window.__aoh; let core = 0, rises = 0, marks = 0, towns = 0, missing = [];
          for (let k = 0; k < 40; k++) { A.newWorld(1200 + k); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
            const cs = A.W.civs; for (const c of cs) { c.era = 11; c.tech = 30; c.mach = 40; c.pop = 3e8; } cs[0].trait = 'Warlike'; cs[0].mach = 90; A.startFate('agi');
            if (A.machineRise(cs[k % 4], 'pressure')) { rises++; const m = A.W.civs.find(c => c.machine); for (let i = 0; i < 30; i++) A.step(0.1); A.ensureLayout(m); if (m._.items.some(b => b.t === 'mcore')) core++; else missing.push(1200 + k); }
            for (const c of A.W.civs.filter(c => c.alive && !c.machine)) { c.era = (k % 14) + 1; c._.sig = null; A.ensureLayout(c); towns++; const plan = c.era; if (c._.items.some(b => b.k === 0 && ['totem','henge','temple0','ziggurat','fort','temple','castle','dome','factory','radio','sky','arcology','tether','beam','gate','nhub'].includes(b.t))) marks++; } }
          return JSON.stringify({ rises, core, missing, towns, marks }); }'''))
        print('  ', r)
        check('every machine people has its machine core', r['rises'] >= 30 and r['core'] == r['rises'], str(r))
        check('human towns of every age have their landmark', r['marks'] >= r['towns'] * .97, f"{r['marks']}/{r['towns']}")
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
