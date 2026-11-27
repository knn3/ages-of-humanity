# Close-ups of the lens for ships sent by star colonies (SV-07 visual check): near pair, a far colony, a lost one; one composite image
import asyncio, pathlib, sys
from playwright.async_api import async_playwright
from PIL import Image
G = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
OUT = sys.argv[1] if len(sys.argv) > 1 else 'sv07_lens.png'
CASES = [(0, 1, .45, 'ship'), (9, 12, .6, 'ship'), (4, 11, .5, 'lost')]
async def m():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1400, 'height': 900}, device_scale_factor=2)
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(G); await pg.wait_for_timeout(600); await pg.keyboard.press('Space')
    shots = []
    for i, (fr, to, f, kind) in enumerate(CASES):
      await pg.evaluate('''([fr, to, f, kind]) => { const A = window.__aoh; A.newWorld(777); for (let i = 0; i < 20; i++) A.step(0.1); const W = A.W, c = W.civs[1]; W.ships = []; W.lost = []; A.V.focus = null;
        W.stars = [{ star: fr, civ: c.id, name: 'C', pop: 1e8, t0: 3000, world: 'Halcyon', log: [] }];
        const sh = { id: 800, civ: c.id, star: to, name: 'Patience', t0: W.simTime - f * 600, dur: 600, crew: 1e5, crew0: 1e5, y0: 3600, told: 2, from: fr, fromW: 'Halcyon', log: [{ y: 3600, k: 'launch', f: 0 }, { y: 3700, k: 'mutiny', f: .25 }] };
        if (kind === 'lost') W.lost.push({ id: 800, star: to, civ: c.id, f, t: W.simTime, name: 'Patience', from: fr, log: sh.log.concat([{ y: 3800, k: 'lost', f }]) }); else W.ships.push(sh);
        scrollTo(0, 0); A.shipFocus(800, true); A.render(); }''', [fr, to, f, kind])
      L = await pg.evaluate('() => { const L = window.__aoh.V.lens, r = document.querySelector("#world").getBoundingClientRect(); return [L.x + r.left, L.y + r.top, L.r]; }')
      fn = f'{OUT}.{i}.png'; await pg.screenshot(path=fn, clip={'x': L[0] - L[2] - 90, 'y': L[1] - L[2] - 30, 'width': 2 * L[2] + 180, 'height': 2 * L[2] + 50}); shots.append(fn)
    await b.close()
  ims = [Image.open(s) for s in shots]; W = sum(i.width for i in ims); H = max(i.height for i in ims); out = Image.new('RGB', (W, H))
  x = 0
  for im in ims: out.paste(im, (x, 0)); x += im.width
  out.save(OUT)
  for s in shots: pathlib.Path(s).unlink()
asyncio.run(m())
