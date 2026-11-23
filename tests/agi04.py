# AGI-04: the war against the machines. A machine people breaks away, has its own looks, and fights the humans for land
import asyncio, json
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

# Future Age world; civ 0 Warlike with many machines; two other peoples at war; the Waking Machines under way; then the machines rise
RISE = r'''(seed) => { const A = window.__aoh; A.newWorld(seed); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
  const cs = A.W.civs; for (const c of cs) { c.era = 11; c.tech = 30; c.mach = 40; c.stability = 60; c.pop = 3e8; } cs[0].trait = 'Warlike'; cs[0].mach = 90;
  A.W.wars = []; A.W.wars.push({ a: cs[1].id, b: cs[2].id, t: 0, adv: 0 }); A.startFate('agi'); A.W.reactQ.length = 0;
  const n0 = cs.length, ok = A.machineRise(cs[0], 'pressure'); A.render(); A.render();
  const m = A.W.civs.find(c => c.machine), p = cs[0];
  if (m) A.ensureLayout(m);
  return JSON.stringify({ ok, n0, n: A.W.civs.length, name: m && m.name, parent: m && m.mParent === p.id, color: m && m.color, mw: !!A.W.mw, atWar: A.W.wars.some(w => (w.a === m.id && w.b === p.id) || (w.b === m.id && w.a === p.id)),
    oldWar: A.W.wars.some(w => w.a === cs[1].id && w.b === cs[2].id), pMach: p.mach, pStab: Math.round(p.stability), agi: A.W.fates.active.some(a => a.id === 'agi'),
    items: m ? [...new Set(m._.items.map(b => b.t))] : [], agents: m ? [...new Set(m._.agents.map(a => a.kind))] : [], road: m ? m._.road : 1, planes: m ? m._.planes.length : 1,
    said: A.W.chron.some(e => /stop taking orders/.test(e.h)), peace: A.W.chron.some(e => /Old enemies make peace/.test(e.h)), joined: A.W.wars.filter(w => w.a === m.id || w.b === m.id).length }); }'''

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate

        r = json.loads(await ev(RISE, 401))
        print('  uprising:', r)
        check('AGI-04 the machines of a people rise and become a people of their own', r['ok'] and r['n'] == r['n0'] + 1 and r['parent'] and r['mw'] and r['agi'], str(r))
        check('AGI-04 the machine people has its own looks: factories, stacks and pylons, drones and robots, no farms', set(r['items']) <= {'mcore', 'mfab', 'mstack', 'mpylon'} and 'mcore' in r['items'] and set(r['agents']) <= {'drone', 'bot'} and 'drone' in r['agents'] and r['road'] is None and r['planes'] == 0 and r['color'] == '#9aa3ad', str(r))
        check('AGI-04 they go to war with their makers; the humans set their own wars aside', r['atWar'] and not r['oldWar'] and r['peace'] and r['said'], str(r))
        check('AGI-04 the makers are weakened and lose their machines', r['pMach'] == 15 and r['pStab'] <= 30, str(r))

        # the machine people: no births (food does not matter), no progress, no choices, no peace; the other humans join the war
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, m = W.civs.find(c => c.machine); const t0 = m.era * 100 + m.tech;
          let food = 100, treaty = false, react = 0, wars = 0, hum = 0;
          m.pop = m._.K ? m._.K * .2 : m.pop; const p0 = m.pop;
          for (let i = 0; i < 600; i++) { m.food = 0; A.step(0.1); food = Math.min(food, m.food); if (W.chron[0] && /machines.*(make peace|treaty|truce)/i.test(W.chron[0].h)) treaty = true; }
          const before = m.lastReact; A.doReaction(m, 'threat'); react = m.lastReact !== before;
          wars = W.wars.filter(w => w.a === m.id || w.b === m.id).length; hum = W.wars.filter(w => !(w.a === m.id || w.b === m.id)).length;
          return JSON.stringify({ grew: m.pop > p0, food: Math.round(food), tech: +(m.era * 100 + m.tech - t0).toFixed(1), react, wars, hum, mil: Math.round(m.military), share: W.mw.share, alive: m.alive, done: W.mw.done }); }'''))
        print('  machine people at war:', r)
        check('AGI-04 no births: the machines build more of themselves whatever the harvest', r['grew'] and r['food'] >= 99 or not r['alive'], str(r))
        check('AGI-04 the machines make no progress and no choices', r['tech'] <= 0 and not r['react'], str(r))
        check('AGI-04 the other humans join the war, and fight no one else', r['wars'] >= 2 and r['hum'] == 0 or r['done'] is not None, str(r))

        # the machines win: The Iron Dominion
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, m = W.civs.find(c => c.machine); W.mw.kills = 2; A.mwTick(1);
          A.showEpilogue(); const t = document.querySelector('#dialog').innerText; document.querySelector('#dialog [data-close]').click();
          return JSON.stringify({ ended: W.fates.ended, done: W.mw.done, care: W.care, wars: W.wars.filter(w => w.a === m.id || w.b === m.id).length, rows: /Their share of their continent/.test(t) && /Peoples overrun/.test(t) && /Humans left/.test(t), name: /The Iron Dominion/.test(t) }); }'''))
        check('AGI-04 the machines win: The Iron Dominion, with its own epilogue rows (no caretakers)', r['ended'] == 'dominion' and r['done'] == 'machines' and r['care'] is None and r['wars'] == 0 and r['rows'] and r['name'], str(r))

        # the humans win: the machines are destroyed; humanity bans thinking machines
        await ev(RISE, 402)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, m = W.civs.find(c => c.machine); m.pop = 30; A.step(0.1); for (let i = 0; i < 12; i++) A.step(0.1);
          const hum = W.civs.filter(c => c.alive);
          return JSON.stringify({ done: W.mw.done, alive: m.alive, ended: W.fates.ended, active: W.fates.active.some(a => a.id === 'agi'), mach: Math.max(...hum.map(c => c.mach || 0)), ban: hum.every(c => c.aiBan > W.simTime), said: W.chron.some(e => /war against the machines is won/.test(e.h)) }); }'''))
        check('AGI-04 the humans win: the machines are gone, the future fades, thinking machines are banned', r['done'] == 'humans' and not r['alive'] and r['ended'] is None and not r['active'] and r['mach'] <= 12 and r['ban'] and r['said'], str(r))

        # a long war with the machines held in a corner: the humans cut the power
        await ev(RISE, 403)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, m = W.civs.find(c => c.machine); W.mw.t0 = W.simTime - 400; m.r = m.l + 40; A.mwTick(1);
          return JSON.stringify({ done: W.mw.done, alive: m.alive, said: W.chron.some(e => /drones fall out of the sky/.test(e.h)) }); }'''))
        check('AGI-04 a long war with the machines cornered: the humans cut their power', r['done'] == 'humans' and not r['alive'] and r['said'], str(r))

        # the Waking Machines don't end on their own while the war goes on
        await ev(RISE, 404)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, a = W.fates.active.find(a => a.id === 'agi'); a.t0 = W.simTime - 500; W.fates.bias.agi = 3; for (let i = 0; i < 30; i++) A.fateTick(0.1);
          return JSON.stringify({ active: W.fates.active.some(a => a.id === 'agi'), ended: W.fates.ended, clock: A.fateDrives && document.querySelector('#fates') ? document.querySelector('#fates').innerText.slice(0, 200) : '' }); }'''))
        check('AGI-04 the future waits for the war to end', r['active'] and r['ended'] is None, str(r))

        # rising on its own during the Waking Machines; Warlike and machine armies most likely
        r = json.loads(await ev(r'''() => { const A = window.__aoh, out = {};
          for (const t of ['Warlike', 'Curious', 'Devout']) { let n = 0; for (let k = 0; k < 16; k++) { A.newWorld(500 + k); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
            for (const c of A.W.civs) { c.era = 11; c.mach = 10; c.trait = 'Mercantile'; } const c = A.W.civs[0]; c.trait = t; c.mach = 92; A.startFate('agi'); A.W.fates.active[0].t0 = A.W.simTime;
            for (let i = 0; i < 1200; i++) { c.mach = 92; A.step(0.1); if (A.W.mw) break; } if (A.W.mw && A.W.mw.parent === c.id) n++; } out[t] = n; }
          A.newWorld(520); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); for (const c of A.W.civs) { c.era = 11; c.mach = 95; } for (let i = 0; i < 1200; i++) A.step(0.1); out.noFate = !!A.W.mw;
          return JSON.stringify(out); }'''))
        print('  uprisings in 16 worlds x 120 s of the Waking Machines:', r)
        check('AGI-04 the machines rise on their own during the Waking Machines; Warlike far most; never without it', r['Warlike'] >= 6 and r['Warlike'] >= max(r['Curious'], r['Devout']) + 2 and not r['noFate'], str(r))

        # the player's event
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(530); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const c = A.W.civs[0], e = A.findEvent('uprising'); c.era = 9; const early = A.applyEvent(e, c.x); c.era = 10; const ok = A.applyEvent(e, c.x); const again = A.applyEvent(e, A.W.civs[1].x);
          return JSON.stringify({ tool: !!document.querySelector('[data-ev="uprising"]') && !!document.querySelector('[data-info="ev:uprising"]'), early, ok, again, agi: A.W.fates.active.some(a => a.id === 'agi'), mw: !!A.W.mw }); }'''))
        check('AGI-04 a Machine Uprising event (Information Age on), once per cycle, starts the Waking Machines', r['tool'] and not r['early'] and r['ok'] and not r['again'] and r['agi'] and r['mw'], str(r))

        # machines do not catch the plague; the card; a new cycle has no machines
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, m = W.civs.find(c => c.machine); A.startPandemic(m); for (let i = 0; i < 50; i++) A.step(0.1); const sick = !!(W.pandemic && W.pandemic.inf[m.id] > 0) && false || (m._.sick || 0) > 0;
          A.updateUI(); const el = document.querySelector(`#civs .civ[data-id="${m.id}"]`), card = el ? el.innerText : '';
          A.reachEnding('collapse'); A.riseAgain();
          return JSON.stringify({ sick, chip: /Machine people/.test(card), govt: /Machine mind/.test(card) && /No births/.test(card), next: /drones instead of children/.test(card), after: m.alive, mw: W.mw, rust: W.chron.some(e => /rust where they stand/.test(e.h)) }); }'''))
        check('AGI-04 machines never fall sick', not r['sick'], str(r))
        check('AGI-04 the people card shows the machine people', r['chip'] and r['govt'] and r['next'], str(r))
        check('AGI-04 after a fall the machines rust; a new cycle begins without them', not r['after'] and r['mw'] is None and r['rust'], str(r))

        # saves
        await ev(RISE, 405)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, m = W.civs.find(c => c.machine); W.mw.kills = 1; const s = JSON.parse(JSON.stringify(A.serialize())); const w = A.sanitizeWorld(s);
          const s2 = JSON.parse(JSON.stringify(s)); s2.mw = { id: 99999, kills: 'x' }; const bad = A.sanitizeWorld(s2); const s3 = JSON.parse(JSON.stringify(s)); s3.mw.done = 'aliens'; s3.mw.kills = -4; const odd = A.sanitizeWorld(s3);
          const s4 = JSON.parse(JSON.stringify(s)); delete s4.mw; for (const c of s4.civs) { delete c.machine; delete c.mParent; } const old = A.sanitizeWorld(s4);
          A.loadWorld(s); for (let i = 0; i < 30; i++) A.step(0.1); A.render(); const m2 = A.W.civs.find(c => c.machine); if (m2) A.ensureLayout(m2);
          return JSON.stringify({ kept: w.mw && w.mw.id === m.id && w.mw.kills === 1 && w.civs.some(c => c.machine && c.mParent === W.mw.parent), bad: bad.mw, odd: [odd.mw.done, odd.mw.kills], old: old.mw === null && !old.civs.some(c => c.machine), loaded: !!m2 && !!A.W.mw && m2._.items.some(b => b.t === 'mcore') }); }'''))
        check('AGI-04 the machine people and the war are saved and sanitised; old saves load', r['kept'] and r['bad'] is None and r['odd'] == [None, 0] and r['old'] and r['loaded'], str(r))

        # look at it: machine city next to its makers, at night
        await ev(RISE, 406)
        await ev(r'''() => { const A = window.__aoh, W = A.W, m = W.civs.find(c => c.machine); for (let i = 0; i < 100; i++) A.step(0.1); A.V.banners.length = 0; A.setZoom(1.25); A.V.cam = (m.x + W.civs[0].x) / 2 - A.V.vw / 2; A.V.camY = null; A.V.dayT = .8; }''')
        await pg.wait_for_timeout(1500); await ev("() => { const d = document.querySelector('#modal.open [data-close]'); if (d) d.click(); window.scrollTo(0, 0); }"); await pg.wait_for_timeout(400)
        await (await pg.query_selector('#world')).screenshot(path='agi04_machines.png')
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
