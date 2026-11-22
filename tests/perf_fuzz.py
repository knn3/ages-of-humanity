import asyncio, random
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width':1400,'height':900}); errs=[]
        pg.on('pageerror', lambda e: errs.append('PAGEERR '+str(e)))
        pg.on('console', lambda m: errs.append('CONSOLE '+m.type+': '+m.text) if m.type in ('error','warning') and 'ERR_FAILED' not in m.text else None)
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(800)
        await pg.evaluate("setInterval(() => { const d = document.querySelector('#dialog'); if (d && d.classList.contains('epi')) d.querySelector('[data-close]').click(); }, 150)")
        await pg.evaluate("() => { const A = window.__aoh; A.newWorld(5142); for (let i = 0; i < 12000 && A.W.fates.edgeT == null; i++) A.step(0.1); const e0 = A.W.simTime; while (A.W.simTime - e0 < 500) A.step(0.1); }")
        print('render ms by zoom (late world):')
        for z in [2.2, 1, .5, .2, .06, .02, .006, .002, .0004, .0001, .00002]:
            ms = await pg.evaluate(f"(() => {{ const A = window.__aoh; A.setZoom({z}); A.render(); A.render(); const t0 = performance.now(); for (let i = 0; i < 12; i++) A.render(); return ((performance.now() - t0) / 12).toFixed(1); }})()")
            print(f'  zoom {z}: {ms} ms')
        # fuzz: random clicks, right clicks, wheel, tools, events, keys while the game runs
        r = await pg.evaluate("(() => { scrollTo(0, 0); const r = document.querySelector('#world').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
        random.seed(3); tools = await pg.evaluate("[...document.querySelectorAll('[data-tool],[data-ev]')].map(b => b.dataset.tool ? '[data-tool=\"' + b.dataset.tool + '\"]' : '[data-ev=\"' + b.dataset.ev + '\"]')")
        acts = 0
        for i in range(260):
            k = random.random(); x = r[0] + random.random() * r[2]; y = r[1] + 10 + random.random() * (min(r[3], 860 - r[1]) - 20)
            try:
                if k < .25: await pg.mouse.click(x, y)
                elif k < .4: await pg.mouse.click(x, y, button='right')
                elif k < .55: await pg.mouse.move(x, y); await pg.mouse.wheel(0, random.choice([-400, -150, 150, 400]))
                elif k < .7:
                    sel = random.choice(tools); await pg.evaluate("(s) => { const b = document.querySelector(s); if (b && !b.disabled) b.click(); scrollTo(0, 0); }", sel)
                elif k < .8: await pg.mouse.move(x, y); await pg.mouse.down(); await pg.mouse.move(x + random.randint(-200, 200), y + random.randint(-120, 120), steps=4); await pg.mouse.up()
                elif k < .9: await pg.keyboard.press(random.choice(['Space', 'Space', 'Escape', 'Home', 'Minus', 'Equal']))
                else: await pg.evaluate("window.__aoh.setZoom([1.6, .7, .03, .001, .00005][Math.floor(Math.random() * 5)])")
                acts += 1
            except Exception as e: errs.append('ACT ' + str(e)[:120])
            if i % 40 == 0: await pg.wait_for_timeout(300)
        await pg.wait_for_timeout(1500)
        print('fuzz actions:', acts, '| world still alive:', await pg.evaluate("window.__aoh.W.civs.some(c => c.alive)"))
        print('\n'.join(errs[:10]) or 'no errors'); await b.close()
asyncio.run(main())
