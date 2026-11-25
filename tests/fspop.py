# Info popovers (the small i buttons) must show in real full screen: only #stage is drawn there, so #pop has to move inside it
import asyncio
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
SEEN = """() => { const p = document.querySelector('#pop'); if (!p.classList.contains('show')) return 'not shown';
  const r = p.getBoundingClientRect(), el = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
  return (el && el.closest('#pop') ? 'VISIBLE' : 'HIDDEN under ' + (el ? el.id || el.className : 'nothing')) + ' parent=' + p.parentNode.id + ' fsEl=' + (document.fullscreenElement ? document.fullscreenElement.id : 'none'); }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width':1400,'height':900}); errs=[]
        pg.on('pageerror', lambda e: errs.append('PAGEERR '+str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(800)
        await pg.evaluate("() => { const A = window.__aoh; for (let i = 0; i < 3000; i++) A.step(0.1); const c = A.W.civs.find(c => c.alive); A.V.cam = c.x - A.V.vw / 2; A.V.camTarget = null; }")
        await pg.evaluate("scrollTo(0,0)"); await pg.click('.js-fs'); await pg.wait_for_timeout(700)
        print('fullscreen element:', await pg.evaluate("document.fullscreenElement && document.fullscreenElement.id"))
        ib = await pg.query_selector('#labInfo .ibtn:not([hidden])')
        await ib.click(); await pg.wait_for_timeout(200)
        print('city i in FS:', await pg.evaluate(SEEN))
        await pg.screenshot(path='fspop.png')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(100)
        # futures panel i buttons
        await pg.evaluate("() => { const A = window.__aoh; const F = A.W.fates; F.edgeT = F.edgeT ?? A.W.simTime; for (const id of Object.keys(A.FATES).slice(0, 3)) F.p[id] = .6; A.updateUI(); }"); await pg.wait_for_timeout(400)
        fb = await pg.query_selector('#futures:not([hidden]) .ibtn[data-info]')
        if fb: await fb.click(); await pg.wait_for_timeout(200); print('futures i in FS:', await pg.evaluate(SEEN))
        else: print('futures panel not shown (skipped)')
        await pg.evaluate("window.__aoh.exitFS()"); await pg.wait_for_timeout(500)
        print('after exit: pop parent =', await pg.evaluate("document.querySelector('#pop').parentNode.tagName"), 'shown =', await pg.evaluate("document.querySelector('#pop').classList.contains('show')"))
        ib = await pg.query_selector('#labInfo .ibtn:not([hidden])')
        if ib: await ib.click(); await pg.wait_for_timeout(200); print('city i windowed:', await pg.evaluate(SEEN))
        print('\n'.join(errs) or 'no errors'); await b.close()
asyncio.run(main())
