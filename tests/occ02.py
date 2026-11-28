# OCC-02 the land turns strange: Hevari ground grows around each growing colony and creeps along the land, as far as its reach;
# forests and animals die back on it; peoples living on it lose food and calm (told once); peoples clear it on their land; the
# player's Clear the Strange Ground event; it fades from empty towers; strip (haze, skin, plants, picks, info), globe, card, panel;
# saved and sanitised; old OCC-01 saves still load.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))
SRC = open(pathlib.Path(__file__).with_name('occ01.py')).read()
SETUP, ARRIVE = [SRC.split(k + " = r'''")[1].split("'''")[0] for k in ('SETUP', 'ARRIVE')]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        await ev(SETUP, 7311); await ev(ARRIVE)
        K = await ev("() => window.__aoh.OCCAL")
        # spread with no one clearing: grows from the towers and stops at the reach
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, S = W.occ, cs = W.civs.filter(c => c.alive); const saved = cs.map(c => [c.l, c.r]); cs.forEach(c => { c.l = c.r = -1e6; });
          window.__f0 = W.nat.f.slice(); window.__w0 = W.nat.w.slice(); const t = S.towers[0], i0 = Math.floor(t.x / 100), at = []; for (let k = 0; k < 160; k++) { A.occTick(1); if (k === 20 || k === 80 || k === 159) at.push(A.occAlShare()); }
          const side = s => { let n = 0; for (let d = 1; d <= 6; d++) if (!A.V.seaCell[(i0 + s * d + 120) % 120]) n++; return n; }, sg = side(1) >= side(-1) ? 1 : -1; const prof = []; for (let d = 0; d <= 3; d++) prof.push(A.V.seaCell[(i0 + sg * d + 120) % 120] ? -1 : S.al[(i0 + sg * d + 120) % 120]); const R = K => K.OCC_AL_R0 + K.OCC_AL_R1 * t.g;
          let beyond = 0; for (let i = 0; i < 120; i++) { const x = (i + .5) * 100; if (S.towers.every(q => { const d = Math.abs(q.x - x) % 12000; return Math.min(d, 12000 - d) > A.OCCAL.OCC_AL_R0 + A.OCCAL.OCC_AL_R1 * q.g + 100; })) beyond = Math.max(beyond, S.al[i]); }
          cs.forEach((c, k) => { c.l = saved[k][0]; c.r = saved[k][1]; }); return JSON.stringify({ at, prof, beyond, g: t.g }); }'''))
        at, prof = r['at'], r['prof']
        check('strange ground grows from the towers over time', at[0] > 0 and at[1] > at[0] and at[2] >= at[1], str(at))
        lp = [v for v in prof if v >= 0]
        check('it is strongest at the tower, spreads to the land beside it and thins with distance', lp[0] > .8 and lp[1] > .2 and all(lp[k] >= lp[k + 1] - 1e-9 for k in range(len(lp) - 1)) and lp[-1] < lp[0], str([round(v, 2) for v in prof]))
        check('it never goes beyond the towers’ reach', r['beyond'] == 0, str(r['beyond']))
        # nature dies back on it
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, S = W.occ, N = W.nat, V = A.V, f0 = window.__f0, w0 = window.__w0; let n = 0, f = 0, w = 0;
          for (let i = 0; i < 120; i++) { if (V.seaCell[i] || S.al[i] < .5 || f0[i] < .05 || w0[i] < .05) continue; n++; f += N.f[i] / f0[i]; w += N.w[i] / w0[i]; } return JSON.stringify({ n, f: f / n, w: w / n }); }'''))
        check('forests and wild animals die back on strange ground (same cells, before and after)', r['n'] > 3 and r['f'] < .4 and r['w'] < .4, str(r))
        # the peoples on it: food and calm, told once; clearing on their land
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, S = W.occ, c = W.civs.find(c => c.alive && S.towers.some(t => t.x >= c.l && t.x <= c.r)) || W.civs.find(c => c.alive);
          for (let i = Math.floor(c.l / 100); i <= Math.floor(c.r / 100); i++) if (!A.V.seaCell[i]) S.al[i] = .6; const f0 = c.food, s0 = c.stability; c.food = 500; c.stability = 80; const sh = A.occAlOf(c); A.occAlTick(1);
          const told = W.hist.filter(e => /Strange violet plants choke the fields of/.test(e.h) && e.h.includes(c.name)).length; A.occAlTick(1); const told2 = W.hist.filter(e => /Strange violet plants choke the fields of/.test(e.h) && e.h.includes(c.name)).length;
          return JSON.stringify({ id: c.id, sh, food: 500 - c.food, stab: 80 - c.stability, told, told2, want: 2 * A.OCCAL.OCC_AL_FOOD * sh }); }'''))
        check('a people on strange ground loses food and calm', r['food'] > .8 * r['want'] and r['stab'] > 0, str(r))
        check('the people is told once when the plants choke its fields', r['told'] == 1 and r['told2'] == 1, str(r))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, S = W.occ, cs = W.civs.filter(c => c.alive); S.towers.forEach(t => t.state = 'empty'); const c = cs[0]; const run = (era, mil) => { for (let i = 0; i < 120; i++) S.al[i] = 0; const i0 = Math.floor(c.x / 100); S.al[i0] = .8; c.era = era; c.military = mil; const fade = A.OCCAL.OCC_AL_FADE; for (let k = 0; k < 10; k++) A.occAlTick(1); return S.al[i0]; };
          const weak = run(6, 10), strong = run(13, 150); S.towers.forEach(t => t.state = 'grow'); return JSON.stringify({ weak, strong }); }'''))
        check('peoples clear it on their own land, the strong and advanced faster', r['strong'] < r['weak'] < .8, str(r))
        # the player's event
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, S = W.occ, t = S.towers[0], i0 = Math.floor(t.x / 100); for (let k = 0; k < 30; k++) A.occTick(1); const ev = A.findEvent('uproot');
          let fi = -1; for (let i = 0; i < 120; i++) { let ok = !A.V.seaCell[i]; for (let d = -7; d <= 7 && ok; d++) if (S.al[(i + d + 120) % 120] > 0) ok = false; if (ok) { fi = i; break; } } const far = (fi + .5) * 100, none = fi >= 0 && A.applyEvent(ev, far), v0 = S.al[i0], ok = A.applyEvent(ev, t.x), v1 = S.al[i0]; A.occTick(1); const v2 = S.al[i0];
          return JSON.stringify({ none, ok, v0, v1, v2, cat: ev.cat, info: A.infoContent('ev:uproot')[1].replace(/<[^>]+>/g, ' ').slice(0, 80) }); }'''))
        check('Clear the Strange Ground burns it out where you click (refused where there is none); a growing tower pushes it back in', r['none'] is False and r['ok'] and r['v0'] > .5 and r['v1'] < .1 and r['v2'] > r['v1'] and r['cat'] == 'Futures' and 'Hevari plants' in r['info'], str(r))
        # empty towers: it fades
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, S = W.occ; for (let k = 0; k < 40; k++) A.occTick(1); const s0 = A.occAlShare(); A.occWithdraw(); for (let k = 0; k < 40; k++) A.occTick(1); const s1 = A.occAlShare(); for (let k = 0; k < 200; k++) A.occTick(1);
          const s2 = A.occAlShare(); S.towers.forEach(t => t.state = 'grow'); for (let k = 0; k < 80; k++) A.occTick(1); return JSON.stringify({ s0, s1, s2, s3: A.occAlShare() }); }'''))
        check('when the towers stand empty the strange ground fades away', r['s0'] > .05 and r['s1'] < r['s0'] and r['s2'] < .2 * r['s0'], str(r))
        # on screen
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, V = A.V, S = W.occ, t = S.towers[0], cv = document.querySelector('#world'), k = cv.width / cv.clientWidth, c2 = cv.getContext('2d'), i0 = Math.floor(t.x / 100);
          let ci = -1; for (const d of [4, -4, 5, -5, 3, -3, 6, -6]) { const i = (i0 + d + 120) % 120; let ok = true; for (let e = -2; e <= 2; e++) if (V.seaCell[(i + e + 120) % 120]) ok = false; if (ok) { ci = i; break; } }
          const X = (ci + .5) * 100; V.focus = null; A.setZoom(1.4); V.cam = X - V.vw / 2; V.camY = null; V.dayT = .5;
          const shot = () => { A.render(); const plants = V.picks.filter(p => p.kind === 'occplant').length; const [sx, sy] = A.W2S(X, A.gy(X)); const d = c2.getImageData(Math.round((sx - 150) * k), Math.round((sy - 90) * k), Math.round(300 * k), Math.round(100 * k)).data; let vi = 0; for (let j = 0; j < d.length; j += 4) if (d[j + 2] > d[j + 1] + 25 && d[j + 2] > 110 && d[j] > d[j + 1]) vi++; return { plants, vi }; };
          for (let i = 0; i < 120; i++) S.al[i] = 0; const off = shot(); for (let i = ci - 3; i <= ci + 3; i++) S.al[(i + 120) % 120] = .9; const on = shot();
          const q = V.picks.find(p => p.kind === 'occplant'), tip = q ? A.tipBody({ p: q }).join(' ').replace(/<[^>]+>/g, ' ') : '';
          return JSON.stringify({ ci, off, on, tip }); }'''))
        check('on the strip: Hevari plants (picks) and a violet haze and skin over strange ground (pixels)', r['off']['plants'] == 0 and r['on']['plants'] > 30 and r['ci'] >= 0 and r['on']['vi'] > max(2 * r['off']['vi'], r['off']['vi'] + 300), str({k: r[k] for k in ('off', 'on')}))
        check('right-clicking a Hevari plant tells how strange the ground is and where it spreads from', 'Hevari plant' in r['tip'] and 'Strange ground here' in r['tip'] and 'Spreading from' in r['tip'], r['tip'][:200])
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, S = W.occ, T = A.TEX, t = S.towers[0]; const ci = Math.floor(t.x / 100); for (let d = -2; d <= 2; d++) S.al[(ci + d + 120) % 120] = .9; A.buildTex(); const c = Math.round(((ci + .5) * 100) / 12000 * T.tw); let idx = -1; for (let r = 0; r < 40; r++) if (T.land[r * T.tw + c]) { idx = r * T.tw + c; break; }
          A.buildTex(); const on = [...T.col.slice(idx * 3, idx * 3 + 3)]; const sv = S.al.slice(); S.al.fill(0); const sT = S.towers; S.towers = []; A.buildTex(); const off = [...T.col.slice(idx * 3, idx * 3 + 3)]; S.al = sv; S.towers = sT; A.buildTex(); return JSON.stringify({ idx, on, off }); }'''))
        check('on the globe strange ground is tinted violet', r['idx'] >= 0 and r['on'][2] > r['on'][1] + 15 and r['on'][2] > r['off'][2] + 20, str(r))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, S = W.occ, t = S.towers[0], c = W.civs.find(c => c.alive && t.x + 300 >= c.l && t.x + 300 <= c.r) || W.civs.find(c => c.alive && A.occAlOf(c) > .01); A.updateUI();
          return JSON.stringify({ card: c ? A.tipBody({ civ: c })[1].replace(/<[^>]+>/g, ' ') : 'none', panel: document.querySelector('#futures').innerText }); }'''))
        check('the people’s card shows its strange ground; the Futures panel shows how much of the land is strange', 'Strange ground' in r['card'] and 'of the land strange' in r['panel'], (r['card'][-90:] + ' || ' + r['panel'].replace('\n', ' | ')[:160]))
        # natural running: through step
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; W.occ.al.fill(0); for (let i = 0; i < 400; i++) { W.wars = []; A.step(.1); } return JSON.stringify({ sh: A.occAlShare(), told: W.hist.filter(e => /the land itself is changing/.test(e.h)).length }); }'''))
        check('it spreads in the running simulation, and the world is told once', r['sh'] > .005 and r['told'] <= 1, str(r))
        # saving
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; const d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d)));
          const bad = JSON.parse(JSON.stringify(d)); bad.occ.al = [9, -3, 'x', .5]; bad.occ.saidC = { 3: 99, q: 1, 4: 'z' }; const b2 = A.sanitizeWorld(bad).occ;
          const old = JSON.parse(JSON.stringify(d)); delete old.occ.al; delete old.occ.saidC; const o2 = A.sanitizeWorld(old).occ; A.loadWorld(old); for (let k = 0; k < 3; k++) A.occTick(1); const grown = A.W.occ.al.length;
          return JSON.stringify({ same: JSON.stringify(back.occ) === JSON.stringify(d.occ), n: d.occ.al.length, bad: [b2.al.length, b2.al.slice(0, 5), b2.saidC], old: [o2.al === undefined, o2.saidC === undefined], grown }); }'''))
        check('strange ground is saved and loaded back exactly', r['same'] and r['n'] == 120, str(r)[:150])
        check('bad values clamped; an OCC-01 save without it loads and starts it', r['bad'][0] == 120 and r['bad'][1] == [1, 0, 0, .5, 0] and r['bad'][2] == {'3': 7} and r['old'] == [True, True] and r['grown'] == 120, str(r['bad']) + str(r['old']))
        print('errors:', errs[:3] if errs else 'no errors'); results.append(not errs)
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
