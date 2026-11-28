# ASC-01 visual check: one people's town at night as it uploads (none, half, all), and by day with its data centre
import asyncio, pathlib, sys
from playwright.async_api import async_playwright
from PIL import Image
G = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
OUT = sys.argv[1] if len(sys.argv) > 1 else 'upload.png'
SETUP = open(pathlib.Path(__file__).with_name('asc01.py')).read().split("SETUP = r'''")[1].split("'''")[0]
async def m():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1400, 'height': 900})
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(G); await pg.wait_for_timeout(600); await pg.keyboard.press('Space'); await pg.evaluate(SETUP)
    await pg.evaluate("() => { const A = window.__aoh; A.ascTick(1); const b = document.querySelector('#banner'); if (b) b.style.display = 'none'; }")
    cv = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
    shots = []
    for i, (u, day) in enumerate([(0, .02), (.5, .02), (1, .02), (.7, .5)]):
      await pg.evaluate("""([u, day]) => { const A = window.__aoh, W = A.W, V = A.V, c = W.civs.find(c => c.alive && c.trait === 'Curious'); W.asc.up[c.id] = u; V.focus = null; A.setZoom(1.0); V.cam = c.x - V.vw / 2; V.camY = null; V.dayT = day; V.t = 2; A.render(); A.render(); }""", [u, day])
      fn = f'{OUT}.{i}.png'; await pg.screenshot(path=fn, clip={'x': cv[0], 'y': cv[1], 'width': cv[2], 'height': cv[3]}); shots.append(fn)
    await b.close()
  ims = [Image.open(s) for s in shots]; w = 700; ims = [im.resize((w, int(w * im.height / im.width))) for im in ims]
  out = Image.new('RGB', (w * 2, ims[0].height * 2))
  for i, im in enumerate(ims): out.paste(im, ((i % 2) * w, (i // 2) * ims[0].height))
  out.save(OUT)
  for s in shots: pathlib.Path(s).unlink()
asyncio.run(m())
