# WE-01 visual check: the dying Sun from the ground (as ever, half swollen, fully swollen), from the solar system (as ever, swollen)
# and its close-up; one composite image
import asyncio, pathlib, sys
from playwright.async_api import async_playwright
from PIL import Image
G = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
OUT = sys.argv[1] if len(sys.argv) > 1 else 'sun.png'
async def m():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1400, 'height': 900})
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(G); await pg.wait_for_timeout(600); await pg.keyboard.press('Space')
    await pg.evaluate("() => { const A = window.__aoh; A.newWorld(4242); A.UI.random = false; for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1); scrollTo(0, 0); document.querySelector('#banner') && (document.querySelector('#banner').style.display = 'none'); }")
    cv = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
    shots = []
    for i, (z, k, foc) in enumerate([(1.2, 0, 0), (1.2, .5, 0), (1.2, 1, 0), (.0016, 0, 0), (.0016, 1, 0), (.0016, 1, 1)]):
      await pg.evaluate("([z, k, foc]) => { const A = window.__aoh, V = A.V; A.W.sun = { k, said: 0 }; V.focus = null; A.setZoom(z); V.dayT = .66; if (foc) A.focusBody('Sun'); A.render(); }", [z, k, foc])
      await pg.wait_for_timeout(1200 if foc else 150); await pg.evaluate("() => window.__aoh.render()")
      fn = f'{OUT}.{i}.png'; await pg.screenshot(path=fn, clip={'x': cv[0], 'y': cv[1], 'width': cv[2], 'height': cv[3]}); shots.append(fn)
    await b.close()
  ims = [Image.open(s).resize((700, int(700 * Image.open(s).height / Image.open(s).width))) for s in shots]; W, H = 700 * 3, ims[0].height * 2; out = Image.new('RGB', (W, H))
  for i, im in enumerate(ims): out.paste(im, ((i % 3) * 700, (i // 3) * ims[0].height))
  out.save(OUT)
  for s in shots: pathlib.Path(s).unlink()
asyncio.run(m())
