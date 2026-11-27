# WE-03 visual check: the voyage from the ground (leaving, frozen with the cities under the ice, Jupiter's pass) and from the solar system
import asyncio, pathlib, sys
from playwright.async_api import async_playwright
from PIL import Image
G = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
OUT = sys.argv[1] if len(sys.argv) > 1 else 'voyage.png'
SETUP = open(pathlib.Path(__file__).with_name('we03.py')).read().split("SETUP = r'''")[1].split("'''")[0]
async def m():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1400, 'height': 900})
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(G); await pg.wait_for_timeout(600); await pg.keyboard.press('Space'); await pg.evaluate(SETUP)
    await pg.evaluate("() => { const A = window.__aoh; A.voyBegin(); const b = document.querySelector('#banner'); if (b) b.style.display = 'none'; }")
    cv = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
    shots = []
    for i, (u, z) in enumerate([(.08, .55), (.3, 1.4), (.5, .55), (.5, .0016)]):
      await pg.evaluate("""([u, z]) => { const A = window.__aoh, W = A.W, V = A.V; W.voy.t0 = W.simTime - u * A.VOY.VOY_SPAN; const c = W.civs.find(c => c.alive); V.focus = null; A.setZoom(z); V.cam = c.x - V.vw / 2; V.camY = null; V.dayT = .6; V.t = 2; A.render(); A.render(); }""", [u, z])
      fn = f'{OUT}.{i}.png'; await pg.screenshot(path=fn, clip={'x': cv[0], 'y': cv[1], 'width': cv[2], 'height': cv[3]}); shots.append(fn)
    await b.close()
  ims = [Image.open(s) for s in shots]; w = 700; ims = [im.resize((w, int(w * im.height / im.width))) for im in ims]
  out = Image.new('RGB', (w * 2, ims[0].height * 2))
  for i, im in enumerate(ims): out.paste(im, ((i % 2) * w, (i // 2) * ims[0].height))
  out.save(OUT)
  for s in shots: pathlib.Path(s).unlink()
asyncio.run(m())
