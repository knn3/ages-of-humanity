# AGI-02: each character answers AI pressure in its own way (reaction system), with chronicle lines
import asyncio, json
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
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

        # which answer each character picks under AI pressure (300 draws each)
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(201); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const c = A.W.civs[0], out = {}; c.era = 11;
          for (const t of ['Curious', 'Devout', 'Warlike', 'Mercantile']) { c.trait = t; const n = {}; for (let i = 0; i < 300; i++) { const k = A.chooseResponse(c, 'ai'); n[k] = (n[k] || 0) + 1; } out[t] = n; }
          return JSON.stringify(out); }'''))
        print('  answers to AI pressure:', r)
        own = {'Curious': 'raceai', 'Devout': 'banai', 'Warlike': 'machinearmy', 'Mercantile': 'sellai'}
        check('AGI-02 each character mostly gives its own answer', all(r[t].get(k, 0) >= 220 for t, k in own.items()), str({t: r[t].get(k, 0) for t, k in own.items()}))

        # run each answer and look at what it does
        r = json.loads(await ev(r'''() => { const A = window.__aoh, out = {};
          for (const [t, k] of [['Curious', 'raceai'], ['Devout', 'banai'], ['Warlike', 'machinearmy'], ['Mercantile', 'sellai']]) for (let tries = 0; tries < 12; tries++) {
            A.newWorld(210 + tries); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
            const cs = A.W.civs; for (const o of cs) { o.era = 11; o.mach = 40; o.machSaid = 1; o.lastReact = -99; }
            const c = cs[0]; c.trait = t; const o = cs.find(o => o !== c && A.W.rel && true && o.alive) ; for (const x of cs) if (x !== c) { x.l = Math.min(x.l, c.r + 5); }
            A.W.reactQ.length = 0; c.mods = [];
            const before = { mach: c.mach, tech: c.tech + c.era * 100, mil: c.military, stab: c.stability, other: o.mach }, n0 = A.W.chron.length;
            A.doReaction(c, 'ai'); if (!c._.did || !c._.did[k]) continue;
            const line = A.W.chron[0] ? A.W.chron[0].h : '';
            out[t] = { mach: +(c.mach - before.mach).toFixed(1), tech: +(c.tech + c.era * 100 - before.tech).toFixed(1), mil: +(c.military - before.mil).toFixed(1), stab: +(c.stability - before.stab).toFixed(1), other: +(o.mach - before.other).toFixed(1), threat: A.W.reactQ.filter(q => q.s === 'threat').length, mods: c.mods.map(m => m.name), ban: (c.aiBan || 0) > A.W.simTime, line: line.replace(/<[^>]+>/g, '').slice(0, 80) };
            break;
          }
          return JSON.stringify(out); }'''))
        for t in r: print(f'  {t}:', r[t])
        cu, de, wa, me = r['Curious'], r['Devout'], r['Warlike'], r['Mercantile']
        check('AGI-02 Curious race ahead: progress and machines up', 'smarter machines' in cu['line'] and cu['tech'] >= 10 and cu['mach'] >= 8, str(cu))
        check('AGI-02 Devout ban the machines: meter down, slower rise, slower progress', 'ban thinking machines' in de['line'] and de['mach'] <= -14 and de['ban'] and 'Machines banned' in de['mods'] and de['stab'] > 0, str(de))
        check('AGI-02 Warlike build machine armies; neighbours feel threatened', 'drones' in wa['line'] and wa['mil'] >= 15 and wa['threat'] >= 1 and 'Machine army' in wa['mods'], str(wa))
        check('AGI-02 Mercantile sell the machines to everyone', 'sell their thinking machines' in me['line'] and me['other'] >= 5, str(me))

        # a ban slows the meter's rise
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(220); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const c = A.W.civs[0]; c.era = 11; c.trait = 'Devout'; c.mach = 10; c.aiBan = 0; const free = A.machRate(c); c.aiBan = A.W.simTime + 50; const banned = A.machRate(c); return JSON.stringify({ free, banned }); }'''))
        check('AGI-02 a ban cuts the rise of the machines', r['banned'] < r['free'] * .2, str(r))

        # AI pressure arrives on its own: milestones, now and then, an AI Awakening, the Waking Machines
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(230); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const c = A.W.civs[0]; c.era = 10; c.mach = 0; c.machSaid = 0; A.W.reactQ.length = 0; A.machAdd(c, 31); const mile = A.W.reactQ.some(q => q.cid === c.id && q.s === 'ai');
          A.W.reactQ.length = 0; let later = 0; for (let i = 0; i < 1500; i++) { c.era = 10; c.tech = Math.min(c.tech, 50); A.step(0.1); } later = A.W.chron.filter(e => /smarter machines|ban thinking|drones and robot|sell their thinking|race on|renew the ban|swarms of drones|new generation of machines/.test(e.h)).length;
          A.W.reactQ.length = 0; c.era = 11; A.applyEvent(A.findEvent('ai'), c.x); const awake = A.W.reactQ.some(q => q.cid === c.id && q.s === 'ai');
          A.W.reactQ.length = 0; A.startFate('agi'); const fate = A.W.reactQ.filter(q => q.s === 'ai').length;
          return JSON.stringify({ mile, later, awake, fate, n: A.W.civs.filter(c => c.alive).length }); }'''))
        check('AGI-02 AI pressure at a milestone, now and then, after an AI Awakening and when the machines wake', r['mile'] and r['later'] >= 1 and r['awake'] and r['fate'] == r['n'], str(r))

        # saves keep the ban; bad values sanitised
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(240); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const c = A.W.civs[0]; c.aiBan = A.W.simTime + 77; const s = JSON.parse(JSON.stringify(A.serialize())); const w = A.sanitizeWorld(s); s.civs[0].aiBan = 'x'; const bad = A.sanitizeWorld(s); delete s.civs[0].aiBan; const old = A.sanitizeWorld(s);
          return JSON.stringify({ ok: Math.round(w.civs[0].aiBan - A.W.simTime), bad: bad.civs[0].aiBan, old: old.civs[0].aiBan }); }'''))
        check('AGI-02 the ban is saved and sanitised', r['ok'] == 77 and r['bad'] == 0 and r['old'] == 0, str(r))
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
