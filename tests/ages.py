import asyncio
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
JS = r'''() => {
  const A = window.__aoh, out = []; A.newWorld((Math.random() * 1e9) | 0); let t = 0; const first = {};
  for (let i = 0; i < 26000; i++) { A.step(0.1); t += 0.1; for (const c of A.W.civs) if (c.alive && !(c.era in first)) first[c.era] = [Math.round(t), Math.round(A.W.year)]; if (i % 500 === 0) A.render(); if (A.W.civs.some(c => c.threshold) && !first.done) first.done = [Math.round(t), Math.round(A.W.year)]; if (first.done && t > first.done[0] + 60) break; }
  out.push('first reached (sim s, year): ' + JSON.stringify(first));
  out.push(A.W.civs.map(c => `${c.name}:${c.alive ? '' : 'X'}e${c.era} t${c.tech.toFixed(0)} p${(c.pop/1e6).toFixed(0)}M`).join(' | ') + ` poll=${A.W.pollution.toFixed(1)}`);
  out.push(A.W.chron.filter(e => e.k === 'era' && /Planetary|Stellar|Galactic|edge/.test(e.h)).slice(-8).reverse().map(e => e.y + ' ' + e.h.replace(/<[^>]+>/g, '')).join('\n'));
  out.push('fates: ' + A.W.chron.filter(e => e.k === 'fate').map(e => e.h.replace(/<b>(.*?)\.<\/b>.*/, '$1')).reverse().join(' / '));
  out.push('space reactions: ' + A.W.chron.filter(e => e.k === 'react' && /orbit|asteroid|colon|space|Moon|stars|cargo|printed|moons/i.test(e.h)).slice(0, 6).map(e => e.h.replace(/<[^>]+>/g, '')).join(' | '));
  return out.join('\n');
}'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width':1300,'height':850}); errs=[]
        pg.on('pageerror', lambda e: errs.append('PAGEERR '+str(e)))
        pg.on('console', lambda m: errs.append('CONSOLE '+m.type+': '+m.text) if m.type in ('error','warning') and 'ERR_FAILED' not in m.text else None)
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(800)
        for k in range(2): print(await pg.evaluate(JS)); print()
        # old save: a people at the old edge (era 11, done) loads and moves on
        print(await pg.evaluate("""() => { const A = window.__aoh; const s = A.serialize(); s.civs.forEach(c => { c.era = 11; c.tech = 100; c.threshold = true; }); s.fates = undefined; s.year = 2350; const w = A.sanitizeWorld(s);
          A.loadWorld(s); for (let i = 0; i < 30; i++) A.step(0.1); A.render(); return 'old save -> eras ' + A.W.civs.filter(c => c.alive).map(c => c.era).join(',') + ' threshold ' + A.W.civs.some(c => c.threshold) + ' edgeT ' + (A.W.fates.edgeT != null); }"""))
        print('ribbon items', await pg.evaluate("document.querySelectorAll('#ages li').length"))
        print('\n'.join(errs) or 'no errors'); await b.close()
asyncio.run(main())
