# The whole chronicle ("See all"): every line of a natural run is kept, saved, sanitised and shown with filters and search
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

        # real data: natural worlds with random history on, nothing forced, run to the end
        r = json.loads(await ev(r'''() => { const A = window.__aoh, out = [];
          for (const s of [11, 12]) { A.newWorld(s); A.UI.random = true; let n = 0; const c = A.W.chron, u = c.unshift; c.unshift = function () { n++; return u.apply(this, arguments); };
            for (let i = 0; i < 30000; i++) { A.step(0.1); if (A.W.chron !== c) break; }
            const H = A.W.hist; let ordered = true; for (let i = 1; i < H.length; i++) if (H[i].y < H[i - 1].y - 1 && H[i].h.indexOf('rise of humanity') < 0) { ordered = false; break; }
            out.push({ n, hist: H.length, chron: A.W.chron.length, same: H[H.length - 1] === A.W.chron[0], first: H[0].h, ordered }); }
          return JSON.stringify(out); }'''))
        for x in r: print('  run:', {k: v for k, v in x.items() if k != 'first'})
        check('every line of a natural run is kept, far past the 260 of the chronicle', all(x['hist'] == x['n'] + 1 and x['hist'] > 260 and x['chron'] == 260 and x['same'] for x in r), str([(x['n'], x['hist']) for x in r]))
        check('the whole story starts at the first fires (the line before the counter)', all('gather around their fires' in x['first'] for x in r))

        # the window: all lines, newest first; filters, search and order
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.openHistory(); const ul = document.querySelector('#hLog'), vis = () => [...ul.children].filter(li => li.id !== 'hNone' && getComputedStyle(li).display !== 'none');
          const tx = h => { const d = document.createElement('div'); d.innerHTML = h; return d.textContent; }, H = A.W.hist, all = vis().length, firstT = vis()[0].querySelector('p').textContent === tx(H[H.length - 1].h);
          document.querySelector('[data-hf="war"]').click(); const wars = vis().length, warsOk = vis().every(li => li.classList.contains('k-war')), nWar = H.filter(e => e.k === 'war').length;
          document.querySelector('[data-hf="all"]').click(); const nm = A.W.civs[0].name; const s = document.querySelector('#hSearch'); s.value = nm.toLowerCase(); s.dispatchEvent(new Event('input'));
          const found = vis().length, foundOk = vis().every(li => li.textContent.toLowerCase().includes(nm.toLowerCase())), nName = H.filter(e => e.h.replace(/<[^>]+>/g, '').toLowerCase().includes(nm.toLowerCase())).length;
          s.value = 'zzqqxx'; s.dispatchEvent(new Event('input')); const none = !document.querySelector('#hNone').hidden && vis().length === 0;
          s.value = ''; s.dispatchEvent(new Event('input')); document.querySelector('#hOrder').click(); const oldFirst = vis()[0].querySelector('p').textContent === tx(H[0].h);
          const note = document.querySelector('.hist .hnote').textContent;
          document.querySelector('#dialog [data-close]').click(); const closed = !document.querySelector('#modal').classList.contains('open');
          return JSON.stringify({ all, n: H.length, firstT, wars, nWar, warsOk, found, nName, foundOk, none, oldFirst, note, closed }); }'''))
        print('  window:', {k: v for k, v in r.items() if k != 'note'}, r['note'])
        check('See all shows every line, newest first', r['all'] == r['n'] and r['firstT'], str((r['all'], r['n'])))
        check('filters show only their kind', r['wars'] == r['nWar'] and r['warsOk'] and r['wars'] > 0, str((r['wars'], r['nWar'])))
        check('search finds every line naming a people', r['found'] == r['nName'] and r['foundOk'] and r['found'] > 0, str((r['found'], r['nName'])))
        check('nothing matching says so; oldest first works; Close closes', r['none'] and r['oldFirst'] and r['closed'])

        # both buttons open it, in the page and in full screen (inside the full-screen stage)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, m = document.querySelector('#modal'), o = {};
          document.querySelector('#seeAll').click(); o.page = m.classList.contains('open') && m.parentNode === document.body; document.querySelector('#dialog [data-close]').click();
          A.enterFS(); document.querySelector('#fsAll').click(); o.fs = m.classList.contains('open') && m.parentNode.id === 'stage'; o.fsVisible = getComputedStyle(m).display !== 'none';
          A.exitFS(); o.back = m.parentNode === document.body; document.querySelector('#dialog [data-close]').click();
          A.openHistory(); A.showEpilogue && 0; return JSON.stringify(o); }'''))
        check('See all opens from the panel and from the full-screen chronicle', r['page'] and r['fs'] and r['fsVisible'] and r['back'], str(r))
        r = json.loads(await ev(r'''() => { document.querySelector('#dialog [data-close]').click(); const A = window.__aoh; A.newWorld(3); const d = document.querySelector('#dialog'); A.openHistory(); const h = d.classList.contains('hist'); document.querySelector('#dialog [data-close]').click();
          document.querySelector('#dlgSave, [data-act="save"]'); return JSON.stringify({ h }); }'''))
        check('a fresh world starts its whole chronicle again', r['h'])

        # saves: kept and sanitised; old saves (no hist) start from the chronicle; the oldest lines fade past the cap
        r = json.loads(await ev(r'''() => { const A = window.__aoh; A.newWorld(11); A.UI.random = true; for (let i = 0; i < 16000; i++) A.step(0.1);
          const s = JSON.parse(JSON.stringify(A.serialize())), n = s.hist.length; A.loadWorld(s); const kept = A.W.hist.length === n && A.W.hist[n - 1].h === s.hist[n - 1].h;
          const bad = JSON.parse(JSON.stringify(s)); bad.hist[0] = { y: 'x', k: 'nope', h: '<img src=x onerror=alert(1)>hi' }; bad.hist[1] = 5; bad.histLost = -4; const w = A.sanitizeWorld(bad);
          const clean = w.hist.length === n - 1 && w.hist[0].k === 'world' && !/onerror/.test(w.hist[0].h) && w.histLost === 0;
          const old = JSON.parse(JSON.stringify(s)); delete old.hist; delete old.histLost; const wo = A.sanitizeWorld(old); const fromChron = wo.hist.length === Math.min(260, n) && wo.hist[wo.hist.length - 1].h === old.chron[0].h;
          A.loadWorld(old); A.openHistory(); const opens = document.querySelectorAll('#hLog li:not(#hNone)').length === wo.hist.length; document.querySelector('#dialog [data-close]').click();
          const big = JSON.parse(JSON.stringify(s)); big.hist = Array.from({ length: A.HIST_MAX + 900 }, (_, i) => ({ y: i, k: 'world', h: 'line ' + i })); const wb = A.sanitizeWorld(big);
          A.loadWorld(s); for (let i = 0; i < A.HIST_MAX + 400; i++) A.W.hist.push({ y: 0, k: 'world', h: 'pad' }); const before = A.W.hist.length; A.step(0.1); A.applyEvent(A.findEvent('drought') || A.EVENTS[0], A.W.civs[0].x);
          const capped = A.W.hist.length <= A.HIST_MAX + 200 && A.W.histLost > 0;
          return JSON.stringify({ n, kept, clean, fromChron, opens, bigLen: wb.hist.length, bigLast: wb.hist[wb.hist.length - 1].h, capped, lost: A.W.histLost, before }); }'''))
        print('  saves:', r)
        check('the whole chronicle is saved and loaded', r['kept'] and r['n'] > 260, str(r['n']))
        check('bad lines are cleaned or dropped on load', r['clean'])
        check('old saves start the whole chronicle from what the chronicle still holds', r['fromChron'] and r['opens'])
        check('it is capped, keeping the newest lines and counting the faded ones', r['bigLen'] == 5000 and r['bigLast'].endswith(str(5000 + 900 - 1)) and r['capped'], str(r))
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
