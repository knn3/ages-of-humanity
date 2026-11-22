import asyncio, json, base64
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
CHECK = r'''() => { const A = window.__aoh, F = A.W.fates; return JSON.stringify({ year: Math.round(A.W.year), cycle: F.cycle, edge: F.edgeT != null, active: F.active.map(a => a.id), done: F.done, hist: F.hist.map(e => e.id + '@' + e.era + (e.y1 == null ? '' : '/end')), ended: F.ended, p: Object.keys(F.p).filter(k => F.p[k] > .01).sort(), acts: A.W.acts, wars: A.W.warCount, sig: !!A.W.sig, eras: A.W.civs.map(c => c.era), fateLog: A.W.chron.filter(e => e.k === 'fate').length }); }'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        ctx = await b.new_context(viewport={'width':1300,'height':850}); await ctx.grant_permissions(['clipboard-read', 'clipboard-write'])
        pg = await ctx.new_page(); errs=[]; res = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR '+str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(800)
        def ok(name, cond, extra=''): res.append(('PASS ' if cond else 'FAIL ') + name + (' ' + extra if extra else ''))
        # 1. a world in the middle of futures
        await pg.evaluate("""() => { const A = window.__aoh; A.newWorld(31337); for (let i = 0; i < 9000 && A.W.fates.edgeT == null; i++) A.step(0.1);
          A.applyEvent(A.findEvent('alien'), 0, {}); A.startFate('agi', 'event'); for (let i = 0; i < 400; i++) A.step(0.1); A.startFate('garden', 'event'); A.W.fates.p.contact = .5; for (let i = 0; i < 50; i++) A.step(0.1); }""")
        await pg.keyboard.press('Space'); before = await pg.evaluate(CHECK)
        # save button -> local storage, reload page (autosave also) -> load
        await pg.click('#saveBtn'); await pg.wait_for_timeout(200); await pg.click('#dialog [data-close]')
        await pg.reload(); await pg.wait_for_timeout(900); await pg.keyboard.press('Space')
        await pg.click('#loadBtn'); await pg.click('#dlgLocal'); await pg.wait_for_timeout(300)
        after = await pg.evaluate(CHECK)
        ok('save button + reload + load keeps futures', json.loads(before) == json.loads(after), '' if before == after else before + ' vs ' + after)
        ok('panel shows after load', 'unfolding' in (await pg.evaluate("document.querySelector('#futures').innerText")).lower())
        # 2. world code export / import
        code = await pg.evaluate("() => { const A = window.__aoh; return btoa(unescape(encodeURIComponent(JSON.stringify({ world: A.serialize(), custom: {} })))); }")
        await pg.evaluate("() => window.__aoh.newWorld(5)")
        await pg.click('#loadBtn'); await pg.click('#dlgPaste'); await pg.fill('#dialog textarea', code); await pg.click('#dialog .primary'); await pg.wait_for_timeout(300)
        ok('world code roundtrip', json.loads(await pg.evaluate(CHECK)) == json.loads(before))
        # 3. old save from before the futures existed: era 11 done, no fates fields
        old = await pg.evaluate("""() => { const A = window.__aoh; const s = A.serialize(); for (const k of ['fates', 'acts', 'sig', 'nukeT', 'lastWarT', 'warCount']) delete s[k]; s.chron = s.chron.filter(e => e.k !== 'fate');
          s.civs.forEach((c, i) => { c.era = i ? 10 : 11; c.tech = i ? 50 : 100; c.threshold = !i; for (const k of Object.keys(c.reached)) if (+k > c.era) delete c.reached[k]; }); A.loadWorld(s); for (let i = 0; i < 20; i++) A.step(0.1); A.render(); return 0; }""")
        st = json.loads(await pg.evaluate(CHECK))
        ok('old save loads and moves past the old edge', st['eras'][0] == 12 and st['edge'] and st['active'] == [], json.dumps(st))
        # 4. garbage in the fates is cleaned
        g = await pg.evaluate("""() => { const A = window.__aoh; const s = A.serialize(); s.fates = { edgeT: 'x', p: { agi: 1e9, bogus: 3 }, bias: { agi: -5 }, active: [{ id: 'agi', t0: 'NaN' }, { id: '<img>' }, null], done: ['nope', 'garden'], hist: [{ id: 'x' }, { id: 'agi', era: 99, y0: 1e12 }], ended: 'evil', cycle: -4 }; s.warCount = -1; s.acts = 'lots';
          const w = A.sanitizeWorld(s); return JSON.stringify({ p: w.fates.p, bias: w.fates.bias.agi, active: w.fates.active, done: w.fates.done, hist: w.fates.hist, ended: w.fates.ended, cycle: w.fates.cycle, wc: w.warCount, acts: w.acts }); }""")
        gj = json.loads(g)
        ok('bad fate data is cleaned', gj['p'] == {'agi': 5} and gj['bias'] == 0.3 and [a['id'] for a in gj['active']] == ['agi'] and gj['done'] == ['garden'] and gj['ended'] is None and gj['cycle'] == 1 and gj['wc'] == 0 and gj['acts'] == 0 and gj['hist'][0]['era'] == 14, g)
        # 5. an ended world and a second cycle survive saving
        await pg.evaluate("() => { const A = window.__aoh; A.newWorld(77); for (let i = 0; i < 9000 && A.W.fates.edgeT == null; i++) A.step(0.1); A.startFate('collapse', 'event'); A.endFate('collapse', 'ending'); }")
        await pg.wait_for_timeout(2600)
        ok('ending opens the epilogue', await pg.evaluate("document.querySelector('#modal').classList.contains('open') && /The Fall/.test(document.querySelector('#dialog').innerText)"))
        s1 = await pg.evaluate("() => { const A = window.__aoh; A.loadWorld(A.serialize()); return A.W.fates.ended; }")
        await pg.wait_for_timeout(500)
        ok('ended state saved; map keeps its final scene', s1 == 'collapse' and 'grayscale' in await pg.evaluate("document.querySelector('#world').style.filter"))
        await pg.click('#epiRise'); await pg.wait_for_timeout(300)
        s2 = await pg.evaluate("() => { const A = window.__aoh; A.loadWorld(A.serialize()); return JSON.stringify([A.W.fates.cycle, A.W.fates.ended, A.W.fates.hist.length, A.W.civs.filter(c => c.alive).map(c => c.era)]); }")
        ok('second cycle saved', json.loads(s2)[0] == 2 and json.loads(s2)[1] is None and json.loads(s2)[2] >= 1, s2)
        # 6. hot snapshot path (page reload restores autosave)
        await pg.evaluate("() => { const A = window.__aoh; A.startFate('agi','event'); }"); await pg.wait_for_timeout(200)
        await pg.evaluate("() => { localStorage.setItem('aoh.world.v2', JSON.stringify(window.__aoh.serialize())); }")
        await pg.reload(); await pg.wait_for_timeout(900)
        ok('autosave restores after reload', json.loads(await pg.evaluate(CHECK))['active'] == ['agi'])
        print('\n'.join(res)); print('\n'.join(errs) or 'no page errors'); await b.close()
asyncio.run(main())
