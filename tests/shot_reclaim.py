# ASC-02 visual check: one uploaded people's town by day as nature reclaims it (green 0, .35, .7, 1), with full forest on its land
import asyncio, pathlib, sys
from playwright.async_api import async_playwright
from PIL import Image
G = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
OUT = sys.argv[1] if len(sys.argv) > 1 else 'reclaim.png'
SETUP = open(pathlib.Path(__file__).with_name('asc01.py')).read().split("SETUP = r'''")[1].split("'''")[0]
async def m():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1400, 'height': 900})
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(G); await pg.wait_for_timeout(600); await pg.keyboard.press('Space'); await pg.evaluate(SETUP)
    await pg.evaluate("() => { const A = window.__aoh; A.ascTick(1); const b = document.querySelector('#banner'); if (b) b.style.display = 'none'; }")
    cv = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
    shots = []
    for i, gr in enumerate([0, .35, .7, 1]):
      await pg.evaluate("""(gr) => { const A = window.__aoh, W = A.W, V = A.V, N = W.nat, c = W.civs.find(c => c.alive && c.trait === 'Curious'); W.asc.up[c.id] = 1; W.asc.green = W.asc.green || {}; W.asc.green[c.id] = gr;
        if (!V.cap) A.render(); for (let i = Math.floor(c.l / 100); i <= Math.floor(c.r / 100); i++) if (!V.seaCell[i]) { N.f[i] = V.cap[i] * (.3 + .7 * gr); N.w[i] = .2 + .8 * gr; }
        V.focus = null; A.setZoom(1.6); V.cam = c.x - V.vw / 2; V.camY = null; V.dayT = .5; V.t = 2; A.render(); A.render(); }""", gr)
      fn = f'{OUT}.{i}.png'; await pg.screenshot(path=fn, clip={'x': cv[0], 'y': cv[1], 'width': cv[2], 'height': cv[3]}); shots.append(fn)
    await b.close()
  ims = [Image.open(s) for s in shots]; w = 700; ims = [im.resize((w, int(w * im.height / im.width))) for im in ims]
  out = Image.new('RGB', (w * 2, ims[0].height * 2))
  for i, im in enumerate(ims): out.paste(im, ((i % 2) * w, (i // 2) * ims[0].height))
  out.save(OUT)
  for s in shots: pathlib.Path(s).unlink()
asyncio.run(m())
