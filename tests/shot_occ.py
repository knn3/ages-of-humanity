# OCC-01 visual check: one Hevari colony by day as it grows (seed tower, outpost, colony, city), the city at night, and the globe
import asyncio, pathlib, sys
from playwright.async_api import async_playwright
from PIL import Image
G = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
OUT = sys.argv[1] if len(sys.argv) > 1 else 'colony.png'
SRC = open(pathlib.Path(__file__).with_name('occ01.py')).read()
SETUP, ARRIVE = [SRC.split(k + " = r'''")[1].split("'''")[0] for k in ('SETUP', 'ARRIVE')]
async def m():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1400, 'height': 900})
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(G); await pg.wait_for_timeout(600); await pg.keyboard.press('Space'); await pg.evaluate(SETUP, 7311); await pg.evaluate(ARRIVE)
    await pg.evaluate("() => { const b = document.querySelector('#banner'); if (b) b.style.display = 'none'; }")
    cv = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
    shots = []
    for i, (gg, day, z) in enumerate([(.1, .5, 1.3), (.4, .5, 1.3), (.7, .5, 1.3), (1, .5, 1.3), (1, .02, 1.3), (1, .5, .12)]):
      await pg.evaluate("""([gg, day, z]) => { const A = window.__aoh, W = A.W, V = A.V, t = W.occ.towers[0]; W.occ.towers.forEach(q => q.g = gg); V.focus = null; A.setZoom(z); V.cam = t.x - V.vw / 2; V.camY = null; V.dayT = day; V.t = 2; A.render(); A.render(); }""", [gg, day, z])
      await pg.wait_for_timeout(300)
      fn = f'{OUT}.{i}.png'; await pg.screenshot(path=fn, clip={'x': cv[0], 'y': cv[1], 'width': cv[2], 'height': cv[3]}); shots.append(fn)
    await b.close()
  ims = [Image.open(s) for s in shots]; w = 700; ims = [im.resize((w, int(w * im.height / im.width))) for im in ims]
  out = Image.new('RGB', (w * 2, ims[0].height * 3))
  for i, im in enumerate(ims): out.paste(im, ((i % 2) * w, (i // 2) * ims[0].height))
  out.save(OUT)
  for s in shots: pathlib.Path(s).unlink()
asyncio.run(m())
