# AGI-05: the merge. A people joins minds with its machines: its character and its looks change
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

        # who chooses to merge under AI pressure, and when
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(501); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const c = A.W.civs[0], out = {}; c.era = 11; A.startFate('agi');
          for (const t of ['Curious', 'Mercantile', 'Warlike', 'Devout']) { c.trait = t; c.merged = false; let n = 0, lo = 0; for (let i = 0; i < 1000; i++) { c.mach = 95; if (A.chooseResponse(c, 'ai') === 'mergeai') n++; c.mach = 60; if (A.chooseResponse(c, 'ai') === 'mergeai') lo++; } out[t] = [n, lo]; }
          c.trait = 'Curious'; c.mach = 95; c.era = 10; let early = 0; for (let i = 0; i < 300; i++) if (A.chooseResponse(c, 'ai') === 'mergeai') early++; out.early = early;
          c.era = 11; c.aiBan = A.W.simTime + 50; let ban = 0; for (let i = 0; i < 300; i++) if (A.chooseResponse(c, 'ai') === 'mergeai') ban++; out.ban = ban; c.aiBan = 0; A.W.fates.active = []; let nofate = 0; for (let i = 0; i < 300; i++) if (A.chooseResponse(c, 'ai') === 'mergeai') nofate++; out.nofate = nofate;
          return JSON.stringify(out); }'''))
        print('  merge chosen (meter 95, meter 60) of 1000:', r)
        check('AGI-05 merging is an answer to AI pressure during the Waking Machines, once the machines run almost everything', r['Curious'][0] > 250 and all(v[1] == 0 for k, v in r.items() if isinstance(v, list)) and r['early'] == 0 and r['ban'] == 0 and r['nofate'] == 0, str(r))
        check('AGI-05 Curious merge most, Devout never', r['Curious'][0] > r['Mercantile'][0] > r['Warlike'][0] and r['Devout'][0] == 0, str(r))

        # merge: character changes
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(502); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const cs = A.W.civs; for (const c of cs) { c.era = 11; c.tech = 20; c.trait = 'Curious'; c.mach = 95; c.lastReact = -99; }
          const c = cs[0], o = cs[1]; A.startFate('agi'); A.W.reactQ.length = 0; 
          let tries = 0; while (!c.merged && tries++ < 60) { c.lastReact = -99; c.aiBan = 0; c.mach = 95; c.trait = c.merged ? c.trait : 'Curious'; A.doReaction(c, 'ai'); }
          const lines = A.W.chron.slice(0, 4).map(e => e.h.replace(/<[^>]+>/g, ''));
          return JSON.stringify({ merged: !!c.merged, trait: c.trait, old: c.oldTrait, tries, said: lines.some(l => /wire their minds/.test(l)) && lines.some(l => /one mind with their machines/.test(l)), mach: c.mach }); }'''))
        check('AGI-05 a people merges by its own choice, and its character becomes Merged', r['merged'] and r['trait'] == 'Merged' and r['old'] == 'Curious' and r['said'] and r['mach'] == 100, str(r))

        # what merging does: faster progress, fewer births, calm, no more AI pressure, no uprising
        r = json.loads(await ev(r'''() => { const A = window.__aoh, out = {};
          for (const mg of [false, true]) { A.newWorld(503); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
            const c = A.W.civs[0]; for (const o of A.W.civs) { o.era = 11; o.tech = 10; o.mach = 95; o.trait = 'Curious'; } A.W.wars = []; c.pop = 1e7; c.food = 80; c.stability = 50;
            if (mg) A.mergeCiv(c, 'event'); const t0 = c.era * 100 + c.tech, p0 = c.pop; let ai = 0;
            for (let i = 0; i < 300; i++) { c.era = 11; c.tech = Math.min(c.tech, 50); A.step(0.1); ai += A.W.reactQ.filter(q => q.cid === c.id && q.s === 'ai').length; }
            out[mg ? 'merged' : 'human'] = { tech: +c._.mult.toFixed(3), pop: +(c.pop / p0).toFixed(2), stab: Math.round(c.stability), ai, rise: A.mwTick && (() => { A.startFate('agi'); for (let i = 0; i < 2000; i++) A.mwTick(1); return !!A.W.mw && A.W.mw.parent === c.id; })() }; }
          return JSON.stringify(out); }'''))
        print('  30 s, human vs merged:', r)
        h, m = r['human'], r['merged']
        check('AGI-05 merged: faster progress, fewer births, calmer', m['tech'] > h['tech'] * 1.15 and m['pop'] < h['pop'] and m['stab'] > h['stab'], str(r))
        check('AGI-05 merged: no more AI pressure, and their machines never rise', m['ai'] == 0 and not m['rise'], str(r))

        # looks: neural city, people with implants; card
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(504); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const c = A.W.civs[0]; c.era = 11; c.pop = 3e8; A.ensureLayout(c); const before = [...new Set(c._.items.map(b => b.t))]; A.mergeCiv(c, 'event'); A.ensureLayout(c);
          const after = [...new Set(c._.items.map(b => b.t))]; A.updateUI(); const el = document.querySelector(`#civs .civ[data-id="${c.id}"]`), card = el ? el.innerText : '', sel = document.querySelector(`#ct-${c.id}`);
          return JSON.stringify({ before, after, chip: /Merged \(once/.test(card), govt: /Neural Commonwealth/.test(card), sel: sel && sel.value }); }'''))
        check('AGI-05 a neural city: neural towers and hubs, no fields', 'nnode' in r['after'] and 'nhub' in r['after'] and 'field' not in r['after'] and 'nnode' not in r['before'], str(r))
        check('AGI-05 the card shows the merged people', r['chip'] and r['govt'] and r['sel'] == 'Merged', str(r))

        # the player's event; new peoples are never born merged; a new cycle wakes them
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(505); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const c = A.W.civs[0], e = A.findEvent('merge'); c.era = 10; const early = A.applyEvent(e, c.x); c.era = 11; const ok = A.applyEvent(e, c.x); const again = A.applyEvent(e, c.x);
          const up = A.applyEvent(A.findEvent('uprising'), c.x);
          let born = 0; for (let k = 0; k < 20; k++) { A.newWorld(600 + k); born += A.W.civs.filter(c => c.trait === 'Merged').length; }
          A.newWorld(506); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1); const d = A.W.civs[0]; d.era = 11; d.trait = 'Warlike'; A.mergeCiv(d, 'event'); A.reachEnding('collapse'); A.riseAgain();
          return JSON.stringify({ tool: !!document.querySelector('[data-ev="merge"]') && !!document.querySelector('[data-info="ev:merge"]'), early, ok, again, up, born, back: d.trait, merged: d.merged, woke: A.W.chron.some(e => /wake up alone/.test(e.h)) }); }'''))
        check('AGI-05 a Merge event (Future Age on); merged machines cannot rise', r['tool'] and not r['early'] and r['ok'] and not r['again'] and not r['up'], str(r))
        check('AGI-05 no people is born merged; a new cycle returns them to their old character', r['born'] == 0 and r['back'] == 'Warlike' and not r['merged'] and r['woke'], str(r))

        # saves
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(507); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const c = A.W.civs[0]; c.era = 11; c.trait = 'Mercantile'; A.mergeCiv(c, 'event'); const s = JSON.parse(JSON.stringify(A.serialize())); const w = A.sanitizeWorld(s);
          const s2 = JSON.parse(JSON.stringify(s)); s2.civs[0].oldTrait = 'Alien'; s2.civs[1].merged = true; const bad = A.sanitizeWorld(s2);
          const s3 = JSON.parse(JSON.stringify(s)); for (const k of s3.civs) { delete k.merged; delete k.oldTrait; } s3.civs[0].trait = 'Curious'; const old = A.sanitizeWorld(s3);
          A.loadWorld(s); for (let i = 0; i < 20; i++) A.step(0.1); A.render(); const c2 = A.W.civs[0]; A.ensureLayout(c2);
          return JSON.stringify({ kept: w.civs[0].merged && w.civs[0].trait === 'Merged' && w.civs[0].oldTrait === 'Mercantile', badOld: bad.civs[0].oldTrait, badMerged: bad.civs[1].merged, old: !old.civs.some(k => k.merged), loaded: c2.merged && c2._.items.some(b => b.t === 'nnode' || b.t === 'nhub') }); }'''))
        check('AGI-05 merging is saved and sanitised; old saves load', r['kept'] and r['badOld'] is None and not r['badMerged'] and r['old'] and r['loaded'], str(r))

        # look at it: a merged city next to a human one, at night
        await ev(r'''() => { const A = window.__aoh; A.newWorld(508); A.UI.random = false; for (let i = 0; i < 20; i++) A.step(0.1);
          const c = A.W.civs[0]; for (const o of A.W.civs) { o.era = 11; o.pop = 5e8; } A.mergeCiv(c, 'event'); for (let i = 0; i < 60; i++) A.step(0.1); A.V.banners.length = 0; A.setZoom(1.6); A.V.cam = c.x - A.V.vw / 2; A.V.camY = null; A.V.dayT = .85; }''')
        await pg.wait_for_timeout(1200); await ev("() => { const d = document.querySelector('#modal.open [data-close]'); if (d) d.click(); window.scrollTo(0, 0); }"); await pg.wait_for_timeout(300)
        await (await pg.query_selector('#world')).screenshot(path='agi05_merged.png')
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
