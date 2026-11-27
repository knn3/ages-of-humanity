# WE-02 visual check: planet engines on the strip (being built with test burns, all firing) and as blue jets on the globe
import asyncio, pathlib, sys
from playwright.async_api import async_playwright
from PIL import Image
G = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
OUT = sys.argv[1] if len(sys.argv) > 1 else 'engines.png'
SETUP = open(pathlib.Path(__file__).with_name('we02.py')).read().split("SETUP = r'''")[1].split("'''")[0]
async def m():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1400, 'height': 900})
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(G); await pg.wait_for_timeout(600); await pg.keyboard.press('Space'); await pg.evaluate(SETUP)
    await pg.evaluate("() => { const b = document.querySelector('#banner'); if (b) b.style.display = 'none'; }")
    cv = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
    shots = []
    for i, (z, P, done, sk) in enumerate([(.55, .5, False, .5), (.55, 1, True, 1), (.06, 1, True, 1)]):
      await pg.evaluate("""([z, P, done, sk]) => { const A = window.__aoh, W = A.W, V = A.V; W.wars = []; W.eng = { by: {}, said: 0, stall: false, done }; for (const c of A.engBuilders()) W.eng.by[c.id] = P; W.sun = { k: sk, said: 0 };
        const c = A.engBuilders()[0]; V.focus = null; A.setZoom(z); V.cam = A.engX(c) - V.vw / 2; V.camY = null; V.dayT = .62; V.t = 3.1; A.render(); A.render(); }""", [z, P, done, sk])
      fn = f'{OUT}.{i}.png'; await pg.screenshot(path=fn, clip={'x': cv[0], 'y': cv[1], 'width': cv[2], 'height': cv[3]}); shots.append(fn)
    await b.close()
  ims = [Image.open(s) for s in shots]; w = 700; ims = [im.resize((w, int(w * im.height / im.width))) for im in ims]
  out = Image.new('RGB', (w * len(ims), ims[0].height))
  for i, im in enumerate(ims): out.paste(im, (i * w, 0))
  out.save(OUT)
  for s in shots: pathlib.Path(s).unlink()
asyncio.run(m())
