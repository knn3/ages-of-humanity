import asyncio
from playwright.async_api import async_playwright
from PIL import Image
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
        print('hidden before edge:', await pg.evaluate("document.querySelector('#futures').hidden"))
        await pg.evaluate("""() => { const A = window.__aoh; A.newWorld(12345); for (let i = 0; i < 9000 && A.W.fates.edgeT == null; i++) A.step(0.1);
          A.W.fates.p.agi = .7; A.W.fates.p.garden = .4; A.W.fates.p.silence = .2; A.startFate('threebody', 'event'); for (let i = 0; i < 300; i++) A.step(0.1); A.startFate('collapse', 'event'); for (let i = 0; i < 50; i++) A.step(0.1); }""")
        await pg.keyboard.press('Space'); await pg.wait_for_timeout(600)
        print('panel text:', (await pg.evaluate("document.querySelector('#futures').innerText")).replace('\n', ' | '))
        print('ribbon markers:', await pg.evaluate("[...document.querySelectorAll('#ages .fmk i')].map(i => i.title + (i.className ? '*' : '')).join(', ')"))
        print('hint bottom / panel top:', await pg.evaluate("[document.querySelector('#hint').getBoundingClientRect().bottom, document.querySelector('#futures').getBoundingClientRect().top]"))
        ib = await pg.query_selector('#futures .ibtn[data-info="fate:threebody"]')
        await ib.hover(); await pg.wait_for_timeout(700)
        print('pop:', await pg.evaluate("document.querySelector('#pop').classList.contains('show') ? document.querySelector('#pop').innerText.replace(/\\n+/g, ' | ') : 'NOT SHOWN'"))
        r = await pg.evaluate("(() => { const r = document.querySelector('#stage').getBoundingClientRect(); return [r.left, r.top]; })()")
        await pg.screenshot(path='fp1.png', clip={'x': r[0], 'y': r[1], 'width': 720, 'height': 330})
        await pg.mouse.move(900, 300); await pg.wait_for_timeout(400)
        # live update
        t1 = await pg.evaluate("document.querySelector('#futures .fc').textContent")
        await pg.evaluate("() => { const A = window.__aoh; for (let i = 0; i < 200; i++) A.step(0.1); }"); await pg.wait_for_timeout(500)
        t2 = await pg.evaluate("document.querySelector('#futures .fc').textContent")
        print('countdown live:', t1, '->', t2)
        # collapse toggle
        await pg.click('#futToggle'); await pg.wait_for_timeout(300)
        print('collapsed:', (await pg.evaluate("document.querySelector('#futures').innerText")).replace('\n', ' | '))
        await pg.click('#futToggle'); await pg.wait_for_timeout(300)
        # full screen
        await pg.evaluate("window.__aoh.enterFS()"); await pg.wait_for_timeout(500)
        print('fs panel rect:', await pg.evaluate("(() => { const r = document.querySelector('#futures').getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; })()"), 'fsbar bottom', await pg.evaluate("Math.round(document.querySelector('.fsbar').getBoundingClientRect().bottom)"))
        await pg.screenshot(path='fp2.png', clip={'x': 0, 'y': 0, 'width': 720, 'height': 330})
        await pg.evaluate("window.__aoh.exitFS()")
        # save roundtrip of history
        print(await pg.evaluate("""() => { const A = window.__aoh; const w = A.sanitizeWorld(A.serialize()); return 'hist ' + JSON.stringify(w.fates.hist.map(e => [e.id, e.era, e.y1 == null])); }"""))
        print('\n'.join(errs) or 'no errors'); await b.close()
    ims=[Image.open('fp1.png'), Image.open('fp2.png')]
    out=Image.new('RGB',(720, ims[0].height+ims[1].height+10),(30,30,30)); out.paste(ims[0],(0,0)); out.paste(ims[1],(0,ims[0].height+10)); out.save('fpcomp.png')
asyncio.run(main())
