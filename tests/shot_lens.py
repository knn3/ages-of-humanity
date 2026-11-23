# Close-up screenshot of the neighbourhood lens with 8 ships, 2 colonies and a lost mark (visual check for the Star voyages epic)
import asyncio, pathlib, sys
from playwright.async_api import async_playwright
G = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
OUT = sys.argv[1] if len(sys.argv) > 1 else 'lens.png'
async def m():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1400, 'height': 900}, device_scale_factor=2)
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(G); await pg.wait_for_timeout(600); await pg.keyboard.press('Space')
    await pg.evaluate('''() => { const A = window.__aoh; A.newWorld(777); for (let i = 0; i < 20; i++) A.step(0.1); const W = A.W, cs = W.civs; W.ships = []; W.stars = [{ star: 1, civ: cs[2].id, name: 'C', pop: 1e5, t0: 3000 }, { star: 6, civ: cs[3].id, name: 'D', pop: 1e5, t0: 3000 }];
      for (let i = 0; i < 8; i++) W.ships.push({ id: 700 + i, civ: cs[i % cs.length].id, star: [0, 4, 9, 9, 12, 5, 8, 13][i], name: 'S' + i, t0: W.simTime - 150 * i - 150, dur: 1400, crew: 1e5, y0: 3000, told: 3 });
      W.lost = [{ id: 9, star: 10, civ: cs[0].id, f: .5, t: W.simTime - 50 }]; scrollTo(0, 0); A.setZoom(.00003); A.render(); }''')
    L = await pg.evaluate('() => { const L = window.__aoh.V.lens, r = document.querySelector("#world").getBoundingClientRect(); return [L.x + r.left, L.y + r.top, L.r]; }')
    await pg.screenshot(path=OUT, clip={'x': L[0] - L[2] - 90, 'y': L[1] - L[2] - 30, 'width': 2 * L[2] + 180, 'height': 2 * L[2] + 50})
    await b.close()
asyncio.run(m())
