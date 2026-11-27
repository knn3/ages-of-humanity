# WE-04 visual check: arriving at a new star (slowing in, the thaw, out from under the ice) and a lost world, from the ground
import asyncio, pathlib, sys
from playwright.async_api import async_playwright
from PIL import Image
G = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
OUT = sys.argv[1] if len(sys.argv) > 1 else 'arrival.png'
SETUP = open(pathlib.Path(__file__).with_name('we03.py')).read().split("SETUP = r'''")[1].split("'''")[0]
async def m():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1400, 'height': 900})
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(G); await pg.wait_for_timeout(600); await pg.keyboard.press('Space')
    cv = None; shots = []
    for i, (out, a) in enumerate([('arrive', .2), ('arrive', .5), ('arrive', .95), ('lost', 0)]):
      await pg.evaluate(SETUP)
      await pg.evaluate("""([out, a]) => { const A = window.__aoh, W = A.W, V = A.V; A.voyBegin(); W.voy.said = 511; W.voy.t0 = W.simTime - A.VOY.VOY_SPAN - 1; W.voy.out = out; W.voy.dest = 2; W.voy.t1 = W.simTime - a * A.VOY.VOY_ARRIVE; W.sun = { k: 0, said: 0 };
        const b = document.querySelector('#banner'); if (b) b.style.display = 'none'; document.querySelector('#modal').classList.remove('open'); const c = W.civs.find(c => c.alive); V.focus = null; A.setZoom(.55); V.cam = c.x - V.vw / 2; V.camY = null; V.dayT = .6; V.t = 2; A.render(); A.render(); }""", [out, a])
      cv = cv or await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
      fn = f'{OUT}.{i}.png'; await pg.screenshot(path=fn, clip={'x': cv[0], 'y': cv[1], 'width': cv[2], 'height': cv[3]}); shots.append(fn)
    await b.close()
  ims = [Image.open(s) for s in shots]; w = 700; ims = [im.resize((w, int(w * im.height / im.width))) for im in ims]
  outi = Image.new('RGB', (w * 2, ims[0].height * 2))
  for i, im in enumerate(ims): outi.paste(im, ((i % 2) * w, (i // 2) * ims[0].height))
  outi.save(OUT)
  for s in shots: pathlib.Path(s).unlink()
asyncio.run(m())
