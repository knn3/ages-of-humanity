# SIL-01 visual check: the galaxy view with the ruins among the stars marked, and one ruin's right-click info open
import asyncio, pathlib, sys
from playwright.async_api import async_playwright
G = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
OUT = sys.argv[1] if len(sys.argv) > 1 else 'silence.png'
SETUP = open(pathlib.Path(__file__).with_name('sil01.py')).read().split("SETUP = r'''")[1].split("'''")[0]
async def m():
  async with async_playwright() as p:
    b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1400, 'height': 900})
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(G); await pg.wait_for_timeout(600); await pg.keyboard.press('Space'); await pg.evaluate(SETUP)
    await pg.evaluate("() => { const A = window.__aoh; A.startFate('silence', 'event'); A.V.focus = null; A.setZoom(.00002); A.render(); }")
    await pg.wait_for_timeout(3500)
    await pg.evaluate("""() => { const A = window.__aoh, V = A.V; A.render(); const q = V.orbPicks.find(q => q.kind === 'deadciv'), cv = document.querySelector('#world'), rc = cv.getBoundingClientRect();
      cv.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: rc.left + q.x, clientY: rc.top + q.y, button: 2 })); }""")
    await pg.wait_for_timeout(300)
    r = await pg.evaluate("(() => { const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
    await pg.screenshot(path=OUT, clip={'x': r[0], 'y': r[1], 'width': r[2], 'height': r[3]})
    await b.close()
asyncio.run(m())
