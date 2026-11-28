# GDN-02 visual check: the Garden ending's epilogue over the world, then the garden world itself
import asyncio, pathlib, sys
from playwright.async_api import async_playwright
from PIL import Image
G = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
OUT = sys.argv[1] if len(sys.argv) > 1 else 'gardenend.png'
T = open(pathlib.Path(__file__).with_name('gdn02.py')).read()
SETUP = open(pathlib.Path(__file__).with_name('gdn01.py')).read().split("SETUP = r'''")[1].split("'''")[0]
ALL = T.split("ALL = r'''")[1].split("'''")[0]
async def m():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1400, 'height': 900})
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(G); await pg.wait_for_timeout(600); await pg.keyboard.press('Space'); await pg.evaluate(SETUP); await pg.evaluate(ALL)
    await pg.evaluate("() => { const A = window.__aoh, W = A.W, V = A.V; A.startFate('garden', 'event'); for (let i = 0; i < 31; i++) A.gdnEndTick(1); const c = W.civs.find(c => c.alive); V.focus = null; A.setZoom(1.1); V.cam = c.x - V.vw / 2; V.camY = null; V.dayT = .5; for (const c of W.civs) c._.sig = null; A.render(); }")
    await pg.wait_for_timeout(2800)
    await pg.screenshot(path=f'{OUT}.0.png')
    await pg.evaluate("() => { const b = document.querySelector('#modal [data-close]'); if (b) b.click(); for (const e of document.querySelectorAll('#banner')) e.style.display = 'none'; window.__aoh.render(); }")
    await pg.wait_for_timeout(300)
    await pg.screenshot(path=f'{OUT}.1.png')
    await b.close()
  ims = [Image.open(f'{OUT}.{i}.png') for i in range(2)]; w = 900; ims = [im.resize((w, int(w * im.height / im.width))) for im in ims]
  out = Image.new('RGB', (w * 2, ims[0].height)); out.paste(ims[0], (0, 0)); out.paste(ims[1], (w, 0)); out.save(OUT)
  for i in range(2): pathlib.Path(f'{OUT}.{i}.png').unlink()
asyncio.run(m())
