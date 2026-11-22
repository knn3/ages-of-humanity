import asyncio
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
JS = r'''() => {
  const A = window.__aoh, out = [], q = s => document.querySelector(s);
  const snap = tag => out.push(tag + ' year=' + Math.round(A.W.year) + ' ' + A.W.civs.map(c => `${c.name}:${c.alive?'':'X'}e${c.era} t${c.tech.toFixed(0)} p${Math.round(c.pop)} f${c.food.toFixed(0)} s${c.stability.toFixed(0)} k${c.keyState}`).join(' | ') + ` wars=${A.W.wars.length} poll=${A.W.pollution.toFixed(1)} temp=${A.W.tempShift.toFixed(2)}`);
  let t = 0, eraT = {};
  out.push("lands " + JSON.stringify(A.V.lands.map(L=>[Math.round(L.l),Math.round(L.r)]))); let maxW = 0; for (let i = 0; i < 9500; i++) { A.step(0.1); maxW = Math.max(maxW, A.W.wars.length); t += 0.1; for (const c of A.W.civs) { const k = c.name + c.era; if (!(k in eraT)) eraT[k] = Math.round(t); } if (i % 400 === 0) A.render(); if (i % 1200 === 0) snap('t=' + Math.round(t)); }
  out.push("max wars " + maxW + " ww " + A.W.wwCount); out.push(JSON.stringify(eraT));
  out.push(A.W.chron.filter(e => e.k === 'era' || e.k === 'war').map(e => e.y + ' ' + e.h.replace(/<[^>]+>/g, '')).reverse().join('\n'));
  // every event, local at each capital
  const xs = A.W.civs.filter(c => c.alive).map(c => c.x);
  let ok = 0;
  for (const ev of A.EVENTS) { try { A.applyEvent(ev, xs[0], { confirmed: true }); ok++; for (let i = 0; i < 30; i++) A.step(0.1); A.render(); } catch (e) { out.push('ERR ' + ev.id + ' ' + e.stack); } }
  out.push('events ok ' + ok);
  for (let i = 0; i < 300; i++) { A.step(0.1); if (i % 50 === 0) A.render(); }
  snap('after events');
  return out.join('\n');
}'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width':1400,'height':1000})
        errs=[]
        pg.on('pageerror', lambda e: errs.append('PAGEERR '+str(e)))
        pg.on('console', lambda m: errs.append('CONSOLE '+m.type+': '+m.text) if m.type in ('error','warning') and 'ERR_FAILED' not in m.text else None)
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME)
        await pg.wait_for_timeout(1200)
        await pg.evaluate("setInterval(() => { const d = document.querySelector('#dialog'); if (d && d.classList.contains('epi')) d.querySelector('[data-close]').click(); }, 150)")
        print(await pg.evaluate(JS))
        # UI: workshop event creation, rule, element, save/load
        await pg.wait_for_timeout(2600)
        if await pg.evaluate("document.querySelector('#modal').classList.contains('open')"): print('epilogue shown:', (await pg.evaluate("document.querySelector('#dialog h3').textContent"))); await pg.click('#dialog [data-close]')
        await pg.click('#t-workshop')
        await pg.click('#ce-save')
        await pg.click('[data-ws="el"]')
        await pg.click('#cx-save')
        await pg.click('#t-rules')
        await pg.select_option('#rc', 'year'); await pg.fill('#rvNum', '2100')
        await pg.click('#ruleForm button[type=submit]')
        await pg.click('#t-events')
        n = await pg.evaluate("document.querySelectorAll('#tab-events [data-ev]').length")
        await pg.click('#tab-events [data-ev^="c_"]')
        box = await pg.query_selector('#world'); bb = await box.bounding_box()
        await pg.mouse.click(bb['x']+bb['width']/2, bb['y']+bb['height']*0.7)
        await pg.click('#t-elements')
        await pg.click('#tab-elements [data-tool^="el:c:"]')
        await pg.mouse.click(bb['x']+bb['width']*0.4, bb['y']+bb['height']*0.7)
        await pg.click('#tab-elements [data-tool="el:people"]')
        await pg.mouse.click(bb['x']+bb['width']*0.9, bb['y']+bb['height']*0.7)
        await pg.click('#tab-elements [data-tool="erase"]')
        await pg.mouse.click(bb['x']+bb['width']*0.4, bb['y']+bb['height']*0.7)
        await pg.keyboard.press('Escape')
        await pg.wait_for_timeout(500)
        code = await pg.evaluate("btoa(unescape(encodeURIComponent(JSON.stringify({world: __aoh.serialize(), custom: JSON.parse(localStorage.getItem('aoh.custom.v1'))}))))")
        await pg.click('#loadBtn'); await pg.click('#dlgPaste'); await pg.fill('#dlgCode', code); await pg.click('#dlgGo')
        await pg.wait_for_timeout(800)
        print('event buttons', n, 'log', await pg.evaluate("document.querySelectorAll('#log li').length"), 'toast:', await pg.inner_text('#toast'))
        print(await pg.evaluate("[...document.querySelectorAll('#log li')].slice(0,8).map(l=>l.innerText.replace(/\\n/g,' ')).join('\\n')"))
        print('\n'.join(errs[:30]) or 'no errors')
        await b.close()
asyncio.run(main())
