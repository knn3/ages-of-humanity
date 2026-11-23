# Close-ups of the Sun and the planets. Wide views (page and full screen): the body is huge on the left (it may run off the
# edges), entirely left of the text, and the text stays on screen and clear of the hint bar (at the bottom in full screen),
# the chronicle feed and the altitude box. Narrow views: the body above a card, both on screen and clear of the overlays.
import asyncio, json
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))

PROBE = r'''async (fs) => { const A = window.__aoh; A.newWorld(5); A.UI.random = false; for (const c of A.W.civs) c.era = 12; for (let i = 0; i < 200; i++) A.step(0.1); A.UI.day = false;
  if (fs) A.enterFS(); else A.exitFS(); window.scrollTo(0, 0); A.setZoom(0.004); await new Promise(r => setTimeout(r, 400));
  const cb = document.querySelector('#world').getBoundingClientRect(), out = {};
  const box = k => { const e = document.querySelector(k); if (!e || e.offsetParent === null) return null; const q = e.getBoundingClientRect(); return q.width && q.bottom > cb.top && q.top < cb.bottom ? { l: q.left - cb.left, r: q.right - cb.left, t: q.top - cb.top, b: q.bottom - cb.top } : null; };
  for (const n of ['Sun', 'Jupiter', 'Saturn', 'Mars', 'Moon', 'Venus']) { A.V.focus = null; A.focusBody(n); await new Promise(r => setTimeout(r, 800));
    const F = A.V.focusBox, w = cb.width, h = cb.height, R = F.R;
    const disc = { l: F.cx - R, r: F.cx + R, t: F.cy - R, b: F.cy + R }, hit = q => q && q.l < disc.r && q.r > disc.l && q.t < disc.b && q.b > disc.t;
    const card = { l: F.cardX, r: F.cardX + F.cardW, t: F.cardY, b: F.cardY + F.cardH };
    const ov = (q, o) => !o || !(q.l < o.r && q.r > o.l && q.t < o.b && q.b > o.t);
    out[n] = { side: F.side, R: Math.round(R), h: Math.round(h), w: Math.round(w), minSide: Math.round(Math.min(w, h)), centreIn: F.cx > 0 && F.cx < w && F.cy > 0 && F.cy < h, leftOfText: disc.r < card.l, onScreen: disc.l >= 0 && disc.r <= w && disc.t >= 0 && disc.b <= h, clearCard: !hit(card), clearHint: !hit(box('#hint')), clearFeed: !hit(box('#fschron')), clearAlt: !hit(box('#alt')), cardIn: card.t >= 0 && card.b <= h && card.r <= w && card.l >= 0, textClear: ov(card, box('#hint')) && ov(card, box('#fschron')) && ov(card, box('#alt')) }; }
  A.V.focus = null; if (fs) A.exitFS(); return JSON.stringify(out); }'''

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        for vw, vh in [(1600, 900), (1300, 850), (1000, 1094), (700, 900)]:
            pg = await b.new_page(viewport={'width': vw, 'height': vh}); errs = []
            pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
            await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
            await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
            for fs in [True, False]:
                r = json.loads(await pg.evaluate(PROBE, fs)); tag = f'{"full screen" if fs else "page"} {vw}x{vh}'
                for n, x in r.items(): print(f'  {tag} {n}:', x)
                wide = all(x['side'] for x in r.values())
                if wide:
                    check(f'{tag}: the body is huge (radius over 40% of the height or of 60% of the width on tall screens, rings 32%), centred on screen, wholly left of the text', all(x['R'] > min(x['h'], x['w'] * .6) * (.32 if n == 'Saturn' else .4) and x['centreIn'] and x['leftOfText'] for n, x in r.items()), str({n: x['R'] for n, x in r.items()}))
                else:
                    check(f'{tag}: the body is on screen above the card and clear of the overlays', all(x['R'] >= 30 and x['onScreen'] and x['clearCard'] and x['clearHint'] and x['clearFeed'] and x['clearAlt'] for x in r.values()), str({n: x['R'] for n, x in r.items()}))
                check(f'{tag}: the text is on screen and clear of the hint bar, the chronicle feed and the altitude box', all(x['cardIn'] and x['textClear'] for x in r.values()))
            await pg.close()
            if errs: print('\n'.join(errs))
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
