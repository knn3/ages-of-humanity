# Chronicle lines survive a save exactly: bold titles (bare <b>, e.g. "The Great Upload.") were stripped on load before;
# lines are now cleaned once when written, with the same rules as on load. Unsafe markup is still removed.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        # natural worlds run long enough to reach futures (their lines carry bold titles); save, load, compare every line
        tot = {'lines': 0, 'bold': 0, 'diff': 0, 'boldAfter': 0, 'shown': 0}
        for seed in [11, 5000, 5426]:
            r = json.loads(await ev(r'''(seed) => { const A = window.__aoh; A.newWorld(seed); A.UI.random = true; for (let i = 0; i < 16000; i++) A.step(0.1);
              const s = JSON.parse(JSON.stringify(A.serialize())), before = A.W.hist.map(e => e.h); A.loadWorld(s); const after = A.W.hist.map(e => e.h);
              const bare = h => (h.match(/<b>/g) || []).length; const diff = before.filter((h, i) => h !== after[i]).length;
              A.openHistory(); const shown = [...document.querySelectorAll('#hLog li b')].filter(x => !x.getAttribute('style')).length; document.querySelector('#dialog [data-close]').click();
              return JSON.stringify({ lines: before.length, bold: before.reduce((a, h) => a + bare(h), 0), boldAfter: after.reduce((a, h) => a + bare(h), 0), diff, shown }); }''', seed))
            print(f'  seed {seed}:', r)
            for k in tot: tot[k] += r[k]
        check('every chronicle line reads exactly the same after a save and reload', tot['lines'] > 1000 and tot['diff'] == 0, str(tot))
        check('bold titles survive the reload (and show in See all)', tot['bold'] > 0 and tot['boldAfter'] == tot['bold'] and tot['shown'] > 0, str(tot))
        # the chronicle panel shows the bold title right after a reload
        r = await ev(r'''() => { const A = window.__aoh; A.log('<b>The Test Title.</b> A line with a title.', 'fate'); const s = A.serialize(); A.loadWorld(JSON.parse(JSON.stringify(s))); const li = [...document.querySelectorAll('#log li')].find(li => li.innerText.includes('The Test Title.')); return li ? li.innerHTML : ''; }''')
        check('a bold title in the chronicle panel is still bold after loading', '<b>The Test Title.</b>' in r, r[:120])
        # unsafe or unknown markup is still removed, on load and when written
        r = json.loads(await ev(r'''() => { const A = window.__aoh, S = A.sanitizeHTML;
          const cases = ['<b onclick="alert(1)">x</b>', '<b style="color:red;background:url(x)">x</b>', '<script>alert(1)</script>y', '<img src=x onerror=alert(1)>z', '<b><img src=x onerror=alert(1)></b>', '<span class="delta" onmouseover="x()">d</span>', '<a href="javascript:alert(1)">l</a>', '<b style="color:#12ab9f">ok</b>', '<b>ok</b>', '<span class="delta">+2</span>'];
          const out = cases.map(S); A.log('<b onclick="alert(1)">w</b><img src=x onerror=alert(1)>', 'world'); return JSON.stringify({ out, logged: A.W.chron[0].h }); }'''))
        out = r['out']; bad = [o for o in out[:7] if any(t in o for t in ['onclick', 'onerror', '<script', '<img', 'url(', 'javascript', 'onmouseover', '<a '])]
        check('unsafe markup is stripped (event handlers, scripts, images, links, other styles)', not bad, str(out[:7]))
        check('allowed markup is kept: coloured names, bare bold, the delta span', out[7:] == ['<b style="color:#12ab9f">ok</b>', '<b>ok</b>', '<span class="delta">+2</span>'], str(out[7:]))
        check('a line is cleaned when it is written, not only on load', 'onclick' not in r['logged'] and 'onerror' not in r['logged'] and 'w' in r['logged'], r['logged'])
        print('\n'.join(errs) or 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
