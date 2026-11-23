# AGI-06: the grey spread. Self-copying machines escape and spread through the nature grid; peoples burn it back or flee to space;
# it can be stopped, it can stall, and it can end the world (The Grey Tide)
import asyncio, json
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(os.environ.get('GAME') or pathlib.Path(__file__).resolve().parents[1].joinpath('index.html')).resolve().as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

# a world of space-age peoples during the Waking Machines; the grey escapes from people 0
SETUP = r'''([seed, era]) => { const A = window.__aoh; A.newWorld(seed); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
  const W = A.W; for (const c of W.civs) { c.era = era; c.tech = 30; c.mach = 50; c.pop = 3e8; c.stability = 60; c.military = 40; c.lastReact = 1e12; }
  W.civs[0].mach = 90; W.civs[0].trait = 'Curious'; A.startFate('agi'); W.reactQ.length = 0; return W.civs.length; }'''
# hold every people back from fighting (alarm in the far future), so the grey spreads freely
HOLD = "for (const c of W.civs) W.grey.alarm[c.id] = W.simTime + 1e9;"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1300, 'height': 850}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate

        # 1 the escape
        await ev(SETUP, [601, 11])
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, c = W.civs[0]; W.fates.active = []; W.fates.done = [];
          const ok = A.greyStart(c, 'pressure'); const G = W.grey, i = A.W.grey.g.findIndex(v => v >= .5);
          return JSON.stringify({ ok, live: G.live, src: G.src === c.id, cell: i, inLand: (i + .5) * 100 >= c.l - 100 && (i + .5) * 100 <= c.r + 100, mach: c.mach, agi: W.fates.active.some(a => a.id === 'agi'),
            line: W.chron.some(e => /machines built to build themselves stop listening/.test(e.h)), meta: /grey spread/.test(A.crisisMeta()), react: W.reactQ.length, k: G.k }); }'''))
        check('AGI-06 self-copying machines escape a people: the grey starts in its lands, with a chronicle line, and starts the Waking Machines', r['ok'] and r['live'] and r['src'] and r['inLand'] and r['agi'] and r['line'] and r['meta'] and r['react'] >= 2 and r['mach'] <= 40, str(r))

        # 2 the spread through the nature grid: forests to silicon, animals vanish, soil dies; it stays on land
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, N = W.nat, V = A.V; ''' + HOLD + r'''
          const g0 = W.grey.g.filter(v => v > .1).length, cells = []; W.grey.g.forEach((v, i) => { if (v > .3) cells.push(i); });
          for (const i of W.grey.g.map((v, i) => i).filter(i => !V.seaCell[i])) { N.f[i] = Math.max(N.f[i], .5 * V.cap[i]); N.w[i] = .8; }
          for (let i = 0; i < 600; i++) A.step(0.1);
          const G = W.grey, grey = G.g.map((v, i) => i).filter(i => G.g[i] > .8), sea = G.g.some((v, i) => V.seaCell[i] && v > 0);
          const avg = (a, k) => a.length ? a.reduce((s, i) => s + N[k][i], 0) / a.length : 1;
          return JSON.stringify({ g0, g1: G.g.filter(v => v > .1).length, full: grey.length, f: +avg(grey, 'f').toFixed(3), w: +avg(grey, 'w').toFixed(3), s: +avg(grey, 's').toFixed(3), sea, share: G.share }); }'''))
        print('  spread:', r)
        check('AGI-06 the grey spreads cell by cell along the land (never in the sea)', r['g1'] >= r['g0'] + 8 and not r['sea'], str(r))
        check('AGI-06 under the grey the forests are gone (turned to silicon), the animals vanish and the soil dies', r['full'] >= 5 and r['f'] < .05 and r['w'] < .05 and r['s'] < .45, str(r))

        # 3 regrowth is blocked under the grey (and under the dead crust)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, N = W.nat; const i = W.grey.g.findIndex(v => v > .95); const f0 = N.f[i];
          for (let k = 0; k < 200; k++) A.step(0.1); return JSON.stringify({ i, f0, f1: N.f[i] }); }'''))
        check('AGI-06 nothing grows back where the grey lies', r['i'] >= 0 and r['f1'] <= r['f0'] + .005, str(r))

        # 4 the grey cannot take a whole world without crossing the sea; a thick coastal cell seeds another continent
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, V = A.V, G = W.grey; ''' + HOLD + r'''
          let coast = -1; for (let i = 1; i < V.seaCell.length - 1; i++) if (!V.seaCell[i] && (V.seaCell[i - 1] || V.seaCell[i + 1])) { coast = i; break; }
          G.g[coast] = 1; const li = (x) => A.W.civs.length; const s0 = G.seeds, rnd = Math.random; Math.random = () => 0.0001;
          try { A.greyTick(1); } finally { Math.random = rnd; }
          return JSON.stringify({ coast, s0, s1: G.seeds, line: W.chron.some(e => /wash ashore/.test(e.h)) }); }'''))
        check('AGI-06 now and then the grey crosses the sea and starts a new stain on another continent', r['s1'] > r['s0'] and r['line'], str(r))

        # 5 peoples fight back by character, with their own lines; it costs them
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; const out = {};
          for (const [k, t] of [['War', 'Warlike'], ['Cur', 'Curious'], ['Mer', 'Mercantile'], ['Dev', 'Devout']]) { const c = { era: 12, trait: t, military: 50, stability: 60 }; out[k] = +A.greyPower(c).toFixed(2); }
          out.e11 = +A.greyPower({ era: 11, trait: 'Curious', military: 50, stability: 60 }).toFixed(2); out.e14 = +A.greyPower({ era: 14, trait: 'Curious', military: 50, stability: 60 }).toFixed(2);
          for (const c of W.civs) delete W.grey.alarm[c.id];
          const st = W.civs.map(c => c.stability), sum0 = W.grey.g.reduce((a, v) => a + v, 0);
          for (let i = 0; i < 15; i++) { W.simTime += 1; A.greyTick(1); }
          const live = W.grey.live; for (const c of W.civs) W.grey.alarm[c.id] = W.simTime + 1e9;
          const lines = W.chron.filter(e => /Flamethrowers and firebombs|counter-swarms of their own|anyone with a fire|fire and prayer|turn its machines against each other/.test(e.h)).length;
          return JSON.stringify({ pw: out, live, fought: W.grey.fought.length, lines, burned: W.grey.burned, stabDrop: +Math.max(...W.civs.map((c, i) => W.grey.fought.includes(c.id) ? st[i] - c.stability : 0)).toFixed(2) }); }'''))
        print('  fighting:', r)
        pw = r['pw']
        check('AGI-06 peoples burn the grey back: Warlike and Curious hardest, Devout least, and stronger with age', pw['War'] > pw['Mer'] and pw['Cur'] > pw['Mer'] > pw['Dev'] and pw['e14'] > pw['Cur'] > pw['e11'], str(pw))
        check('AGI-06 each people that meets the grey fights it, with a chronicle line for its character, at a cost in stability', r['live'] and r['fought'] >= 2 and r['lines'] >= r['fought'] and r['burned'] > .3 and r['stabDrop'] > 1, str(r))

        # 6 flight to space: a space people whose land is mostly grey sends ark ships
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, V = A.V, c = W.civs.find(c => c.alive && !W.grey.fled.includes(c.id)); ''' + HOLD + r'''
          c.era = 12; for (let i = 0; i < W.grey.g.length; i++) W.grey.g[i] = Math.min(W.grey.g[i], .1); for (let i = Math.floor(c.l / 100); i <= Math.floor(c.r / 100); i++) if (!V.seaCell[i]) W.grey.g[i] = 1;
          const arks0 = W.fates.arks || 0, pop0 = c.pop; A.greyTick(1); A.updateUI(); const card = (document.querySelector(`#civs .civ[data-id="${c.id}"]`) || {}).innerText || '';
          return JSON.stringify({ fled: W.grey.fled.includes(c.id), arks: (W.fates.arks || 0) - arks0, pop: +(c.pop / pop0).toFixed(2), line: W.chron.some(e => /ark ship/.test(e.h) && e.h.includes(c.name)), chip: /Fled to space/.test(card) && /Grey \d+% of the land/.test(card), food: Math.round(c.food) }); }'''))
        check('AGI-06 a space people that loses its land to the grey flees in ark ships (counted as escaped), with card chips', r['fled'] and r['arks'] >= 1 and r['pop'] < .6 and r['line'] and r['chip'], str(r))

        # 7 the Futures panel shows the grey; the Waking Machines wait for it; no uprising while it spreads
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; if (!W.fates.active.some(a => a.id === 'agi')) A.startFate('agi'); const a = W.fates.active.find(a => a.id === 'agi'); a.t0 = W.simTime - 1e4;
          A.fateTick(1); const still = W.fates.active.some(a => a.id === 'agi'); const clk = A.greyClock(); const up = A.machineRise(W.civs.find(c => c.alive), 'event');
          A.updateUI(); const panel = (document.querySelector('#fates') || document.body).innerText;
          return JSON.stringify({ live: A.greyOn(), still, clk: clk && clk[0], up, panel: /Grey spread · \d+% of the land/.test(document.body.innerText) }); }'''))
        check('AGI-06 the Waking Machines wait for the grey, the Futures panel shows its share, and the machines cannot rise meanwhile', r['still'] and r['clk'] and not r['up'] and r['panel'], str(r))

        # 8 the end of the world: The Grey Tide at half the land, with epilogue rows
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, V = A.V; ''' + HOLD + r'''
          for (let i = 0; i < W.grey.g.length; i++) if (!V.seaCell[i]) W.grey.g[i] = Math.max(W.grey.g[i], .7);
          A.greyTick(1); A.showEpilogue(); const t = document.querySelector('#dialog').innerText; const cl = document.querySelector('#dialog [data-close]'); if (cl) cl.click();
          return JSON.stringify({ ended: W.fates.ended, done: W.grey.done, live: W.grey.live, name: /The Grey Tide/.test(t), rows: /Land it covered/.test(t) && /Fought it/.test(t) && /Fled to space/.test(t), escaped: /fled before the end/.test(t), line: W.chron.some(e => /dead grey crust lies over the world/.test(e.h)) }); }'''))
        check('AGI-06 the grey ends the world when it covers half the land: The Grey Tide, with its own epilogue rows', r['ended'] == 'grey' and r['done'] == 'world' and not r['live'] and r['name'] and r['rows'] and r['escaped'] and r['line'], str(r))

        # 9 a new cycle: the dead crust stays, then weathers away; peoples can live there again
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; A.riseAgain(); const s0 = A.greyShare(); const live = A.greyOn();
          for (let i = 0; i < 1500; i++) A.step(0.1); const s1 = A.greyShare();
          for (let i = 0; i < 1800; i++) A.step(0.1);
          return JSON.stringify({ s0: +s0.toFixed(2), live, s1: +s1.toFixed(2), gone: !W.grey || A.greyShare() < .01, cycle: W.fates.cycle }); }'''))
        check('AGI-06 after the Grey Tide the crust is dead, and it weathers away in the next cycle', r['s0'] > .4 and not r['live'] and r['s1'] < r['s0'] and r['gone'] and r['cycle'] == 2, str(r))

        # 10 a patch caught early by strong peoples is burned out: the grey is stopped
        out = []
        for seed in (611, 612, 613):
            await ev(SETUP, [seed, 14])
            out.append(json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; A.greyStart(W.civs[0], 'pressure');
              for (let i = 0; i < 4000 && W.grey && W.grey.live; i++) A.step(0.1);
              return JSON.stringify({ done: W.grey ? W.grey.done : 'gone', t: Math.round(W.simTime - (W.grey ? W.grey.t0 : 0)), line: W.chron.some(e => /last of the grey is burned away/.test(e.h)), ended: W.fates.ended }); }''')))
        print('  galactic peoples vs the grey:', out)
        check('AGI-06 the grey can be stopped: Galactic Age peoples burn it out', sum(1 for o in out if o['done'] in ('stopped', 'gone') and o['line']) >= 2, str(out))

        # 11 weak peoples cannot: in the Future Age the grey wins, stalls or ends the world more often than not
        out = []
        for seed in (621, 622, 623, 624):
            await ev(SETUP, [seed, 11])
            out.append(json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; A.greyStart(W.civs[0], 'pressure'); let peak = 0;
              for (let i = 0; i < 5200 && W.grey && W.grey.live; i++) { for (const c of W.civs) if (c.era > 11) c.era = 11; A.step(0.1); peak = Math.max(peak, A.greyShare()); }
              return JSON.stringify({ done: W.grey ? W.grey.done : 'gone', peak: +peak.toFixed(2) }); }''')))
        print('  Future Age peoples vs the grey:', out)
        check('AGI-06 Future Age peoples mostly cannot stop it (it spreads far, stalls or ends the world)', sum(1 for o in out if o['done'] in ('world', 'stalled', 'fell')) >= 3 and max(o['peak'] for o in out) > .3, str(out))

        # 12 it stalls after a long while: copying errors
        await ev(SETUP, [631, 11])
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; A.greyStart(W.civs[0], 'pressure'); ''' + HOLD + r''' W.grey.t0 = W.simTime - 1e4;
          for (const k in W.grey.g) W.grey.g[k] = Math.min(W.grey.g[k], .1); A.greyTick(1);
          return JSON.stringify({ done: W.grey.done, live: W.grey.live, line: W.chron.some(e => /Copying errors pile up/.test(e.h)) }); }'''))
        check('AGI-06 after a long while copying errors stop the grey where it is (a dead crust)', r['done'] == 'stalled' and not r['live'] and r['line'], str(r))

        # 13 it rises on its own only during the Waking Machines, from peoples with a meter of 80+, Curious far more than Devout
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; const cnt = {}, run = (fate, trait, mach) => { let n = 0;
            for (let k = 0; k < 1000; k++) { W.grey = null; W.greyCycle = 0; W.mw = null; W.care = null; W.fates.ended = null; W.fates.active = fate ? [{ id: 'agi', t0: W.simTime, y0: 0, why: 'pressure' }] : [];
              for (const c of W.civs) { c.alive = c === W.civs[0]; c.era = 12; c.mach = mach; c.trait = trait; c.merged = false; c.machine = false; }
              A.greyTick(10); if (W.grey && W.grey.live) n++; } return n; };
          cnt.cur = run(true, 'Curious', 95); cnt.dev = run(true, 'Devout', 95); cnt.low = run(true, 'Curious', 70); cnt.nofate = run(false, 'Curious', 95);
          for (const c of W.civs) c.alive = true; W.grey = null; return JSON.stringify(cnt); }'''))
        check('AGI-06 it starts on its own only during the Waking Machines and from a meter of 80+, far likelier from Curious than Devout peoples', r['cur'] >= 40 and r['cur'] > 2.5 * r['dev'] and r['low'] == 0 and r['nofate'] == 0, str(r))

        # 14 the player's events: Grey Spread where you click (refused on the sea), Burn the Grey
        await ev(SETUP, [641, 12])
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, V = A.V; const sea = V.seaCell.findIndex(v => v); const land = W.civs[1].x;
          const e = A.findEvent('grey'), b = A.findEvent('greyburn'); const noBurn = A.applyEvent(b, land, {}); const onSea = A.applyEvent(e, sea * 100 + 50, {}); const ok = A.applyEvent(e, land, {});
          ''' + HOLD + r''' for (let i = 0; i < 300; i++) A.step(0.1); const s0 = W.grey.g.reduce((a, v) => a + v, 0); const burn = A.applyEvent(b, land, {}); const s1 = W.grey.g.reduce((a, v) => a + v, 0);
          const twice = A.applyEvent(e, land + 2000, {});
          return JSON.stringify({ onSea, noBurn, ok, why: W.grey.why, at: Math.abs(W.grey.x - land) < 300, s0: +s0.toFixed(2), s1: +s1.toFixed(2), burn, twice, info: !!document.querySelector('[data-ev="grey"]') }); }'''))
        check('AGI-06 the Grey Spread event starts it where you click (not on the sea, not twice); Burn the Grey burns it away there', r['ok'] and not r['onSea'] and not r['noBurn'] and r['why'] == 'event' and r['at'] and r['burn'] and r['s1'] < r['s0'] * .7 and not r['twice'], str(r))

        # 15 looks: the strip (crust, silicon spires, right click), the strip map and the globe
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, V = A.V; const gi = W.grey.g.map((v, i) => i).filter(i => W.grey.g[i] > .5), wild = gi.filter(i => !W.civs.some(c => c.alive && (i + .5) * 100 > c.l - 150 && (i + .5) * 100 < c.r + 150)); const i = (wild.length ? wild : gi)[0];
          A.setZoom(1.8); V.cam = i * 100 + 50 - V.vw / 2; V.camTarget = null; V.camY = null; A.render(); A.render();
          const qs = V.picks.filter(q => q.kind === 'grey'), q = qs[0]; let tip = null; for (const q of qs) { const [sx, sy] = A.W2S((q.x0 + q.x1) / 2, (q.y0 + q.y1) / 2); const t = A.tipTarget(sx, sy); tip = t && t.p ? t.p.kind + ':' + t.p.d.name : null; if (tip === 'grey:Silicon spire') break; }
          return JSON.stringify({ i, wild: wild.length, pick: !!q, tip }); }'''))
        check('AGI-06 on the strip the grey shows as silicon spires that open info on a right click', r['pick'] and r['tip'] == 'grey:Silicon spire', str(r))
        await pg.evaluate('window.scrollTo(0,0)')
        await pg.screenshot(path=str(pathlib.Path(__file__).with_name('agi06_strip.png')))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, V = A.V; for (const k in W.grey.g) if (!V.seaCell[k]) W.grey.g[k] = Math.max(W.grey.g[k], k < W.grey.g.length / 2 ? .95 : 0);
          A.setZoom(0.004); for (let i = 0; i < 4; i++) { A.step(0.1); A.render(); } return JSON.stringify({ z: V.zoom }); }'''))
        await pg.wait_for_timeout(1700)
        await ev("() => { const A = window.__aoh; A.render(); A.render(); }")
        await pg.screenshot(path=str(pathlib.Path(__file__).with_name('agi06_globe.png')))
        print('  wrote agi06_strip.png and agi06_globe.png')

        # 16 saves: the grey survives save/load; garbage is cleaned; old saves without it load
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.setZoom(1); const s = JSON.parse(JSON.stringify(A.serialize())), g0 = A.W.grey.g.slice(), live0 = A.W.grey.live;
          A.loadWorld(JSON.parse(JSON.stringify(s))); const G = A.W.grey; const same = G && G.live === live0 && G.g.every((v, i) => Math.abs(v - g0[i]) < 1e-3);
          for (let i = 0; i < 20; i++) A.step(0.1);
          const bad = JSON.parse(JSON.stringify(s)); (bad.w || bad).grey = { live: 'yes', g: ['x', -5, 9, null], fled: [1, 'a', -3], fought: 'no', alarm: { a: 1, 2: 'z', 3: 5 }, k: 99, done: 'maybe' };
          let ok2 = true, G2; try { A.loadWorld(bad); G2 = JSON.parse(JSON.stringify(A.W.grey)); for (let i = 0; i < 20; i++) A.step(0.1); A.render(); } catch (e) { ok2 = String(e); }
          const old = JSON.parse(JSON.stringify(s)); const ow = old.w || old; delete ow.grey; delete ow.greyCycle; let ok3 = true; try { A.loadWorld(old); for (let i = 0; i < 20; i++) A.step(0.1); } catch (e) { ok3 = String(e); }
          return JSON.stringify({ same, ok2, clean: G2 && G2.g.length === 120 && G2.g.every(v => v >= 0 && v <= 1) && G2.g[2] === 1 && G2.fled.join() === '1' && G2.fought.length === 0 && G2.k <= 2 && G2.done === null && Object.keys(G2.alarm).join() === '3', ok3, oldGrey: A.W.grey }); }'''))
        check('AGI-06 the grey is saved and loaded; bad grey data is cleaned; old saves without it still load', r['same'] and r['ok2'] is True and r['clean'] and r['ok3'] is True and r['oldGrey'] is None, str(r))

        # 17 a new world starts clean
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(650); return JSON.stringify({ g: A.W.grey, c: A.W.greyCycle }); }'''))
        check('AGI-06 a new world has no grey', r['g'] is None and r['c'] == 0, str(r))

        print('\n'.join(errs[:5]) or 'no errors')
        await b.close()
    print(f'{sum(results)}/{len(results)} passed')
asyncio.run(main())
