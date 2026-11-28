# ASC-03 visual check: the holdouts break away beside an uploaded people's dark town; by night (their lights against the dark) and by day
import asyncio, pathlib, sys
from playwright.async_api import async_playwright
from PIL import Image
G = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
OUT = sys.argv[1] if len(sys.argv) > 1 else 'holdouts.png'
SETUP = open(pathlib.Path(__file__).with_name('asc01.py')).read().split("SETUP = r'''")[1].split("'''")[0]
async def m():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1400, 'height': 900})
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(G); await pg.wait_for_timeout(600); await pg.keyboard.press('Space'); await pg.evaluate(SETUP)
    await pg.evaluate("""() => { const A = window.__aoh, W = A.W, c = W.civs.find(c => c.alive && c.trait === 'Curious'); W.wars = []; A.ascTick(1); W.asc.up[c.id] = .599; A.ascTick(1); A.ascTick(1); W.asc.up[c.id] = 1; W.asc.green[c.id] = .5;
      for (let i = 0; i < 40; i++) { W.wars = []; A.step(.25); } const b = document.querySelector('#banner'); if (b) b.style.display = 'none'; window.__c = c.id; }""")
    cv = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
    shots = []
    for i, day in enumerate([.02, .5]):
      await pg.evaluate("""(day) => { const A = window.__aoh, W = A.W, V = A.V, c = W.civs.find(c => c.id === window.__c), h = W.civs[W.civs.length - 1]; W.asc.up[c.id] = 1; V.focus = null; A.setZoom(.8); V.cam = (c.x + h.x) / 2 - V.vw / 2; V.camY = null; V.dayT = day; V.t = 2; A.render(); A.render(); }""", day)
      fn = f'{OUT}.{i}.png'; await pg.screenshot(path=fn, clip={'x': cv[0], 'y': cv[1], 'width': cv[2], 'height': cv[3]}); shots.append(fn)
    await b.close()
  ims = [Image.open(s) for s in shots]; w = 1000; ims = [im.resize((w, int(w * im.height / im.width))) for im in ims]
  out = Image.new('RGB', (w, ims[0].height * 2))
  for i, im in enumerate(ims): out.paste(im, (0, i * ims[0].height))
  out.save(OUT)
  for s in shots: pathlib.Path(s).unlink()
asyncio.run(m())
