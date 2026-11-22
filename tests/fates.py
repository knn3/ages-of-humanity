import asyncio, json
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
JS = r'''(mode) => {
  const A = window.__aoh, out = [];
  A.newWorld((Math.random() * 1e9) | 0); let t = 0, edge = null;
  if (mode === 'acts') A.W.acts = 120;
  if (mode === 'green') for (const c of A.W.civs) c.policy = 'protect';
  for (let i = 0; i < 26000; i++) {
    A.step(0.1); t += 0.1;
    if (mode === 'ai' && i % 600 === 0 && A.W.civs.some(c => c.alive && c.era >= 11)) { const c = A.W.civs.find(c => c.alive && c.era >= 11); A.applyEvent(A.findEvent('ai'), c.x, {}); }
    if (mode === 'signal' && edge == null && A.W.civs.some(c => c.alive && c.era >= 10) && !A.W.sig) A.applyEvent(A.findEvent('alien'), 0, {});
    if (edge == null && A.W.fates.edgeT != null) edge = Math.round(t);
    if (edge != null && t - edge > 700) break;
  }
  if (!A.W.fates.edgeT && A.W.fates.edgeT !== 0) return mode + ': no edge reached in ' + Math.round(t) + 's';
  const F = A.W.fates, x = A.fateDrives();
  const fl = A.W.chron.filter(e => e.k === 'fate').map(e => e.y + ' ' + e.h.replace(/<[^>]+>/g, '').slice(0, 60)).reverse();
  return `${mode}: ` + A.W.chron.filter(e => e.k === 'fate' && !/falls silent|reined in|calm the panic|slows\.|fades\.|eases\.|superstition|call each other|does not come|left alone|waiting to see|steps back|returns to everyone/.test(e.h)).map(e => e.h.replace(/<b>(.*?)\.<\/b>.*/, '$1')).reverse().join(' → ') + ` || edge at ${edge}s (year ${Math.round(A.W.year)}), ran to ${Math.round(t)}s, poll ${A.W.pollution.toFixed(0)} temp ${A.W.tempShift.toFixed(1)} wars ${A.W.wars.length} acts ${A.W.acts}\n  active ${JSON.stringify(F.active.map(a => a.id))} done ${JSON.stringify(F.done)}\n  drives ${Object.entries(x).map(([k, v]) => k + ':' + v.toFixed(2)).join(' ')}\n  ` + fl.join('\n  ');
}'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width':1200,'height':800})
        errs=[]
        pg.on('pageerror', lambda e: errs.append('PAGEERR '+str(e)))
        pg.on('console', lambda m: errs.append('CONSOLE '+m.type+': '+m.text) if m.type in ('error','warning') and 'ERR_FAILED' not in m.text else None)
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME)
        await pg.wait_for_timeout(800)
        await pg.evaluate("() => { const r = document.querySelector('#randBtn'); }")
        for mode in ['plain'] * 6 + ['signal', 'ai', 'acts', 'green']:
            print(await pg.evaluate(JS, mode)); print()
        # save / load roundtrip keeps fate state
        rt = await pg.evaluate("""() => { const A = window.__aoh; const s1 = JSON.stringify(A.W.fates); const w = A.sanitizeWorld(A.serialize()); return s1 === JSON.stringify(w.fates) ? 'roundtrip ok' : 'ROUNDTRIP DIFF ' + s1.slice(0, 200) + ' vs ' + JSON.stringify(w.fates).slice(0, 200); }""")
        print(rt)
        print('\n'.join(errs) or 'no errors')
        await b.close()
asyncio.run(main())
