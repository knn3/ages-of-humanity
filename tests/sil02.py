# SIL-02 fear or urgency: once the ruins are found every people takes a stance by character (hide, arm, race), told once each; the
# fear fades over SIL_FEAR; while it lasts each stance acts on its people (research, calm, armies, colony ships) and the shares of the
# stances shift the other futures' pressure; a mostly hidden world can keep the Silence; card, panel; saved and sanitised.
import asyncio, json, os, pathlib
from playwright.async_api import async_playwright
GAME = pathlib.Path(__file__).resolve().parents[1].joinpath('index.html').as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
results = []
def check(name, ok, info=''):
    results.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''))
SETUP = open(pathlib.Path(__file__).with_name('sil01.py')).read().split("SETUP = r'''")[1].split("'''")[0]
ALL = r'''(k) => { const A = window.__aoh, W = A.W; for (const c of W.civs.filter(c => c.alive)) W.sil.stance[c.id] = k; return true; }'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH)
        pg = await b.new_page(viewport={'width': 1400, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto(GAME); await pg.wait_for_timeout(700); await pg.keyboard.press('Space')
        ev = pg.evaluate
        await ev(SETUP)
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; A.startFate('silence', 'event'); A.silTick(1); A.silTick(1); const cs = W.civs.filter(c => c.alive);
          const re = /go quiet\. They switch off|will not find them unready|warning to hurry/; return JSON.stringify({ n: cs.length, st: cs.map(c => A.silStance(c)), lines: W.hist.filter(e => re.test(e.h)).length }); }'''))
        check('once the ruins are found every people takes a stance, told once each', all(x in ('hide', 'arm', 'race') for x in r['st']) and r['lines'] == r['n'], str(r))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, o = {}; for (const t of ['Devout', 'Warlike', 'Curious', 'Mercantile']) { const n = { hide: 0, arm: 0, race: 0 }; for (let i = 0; i < 3000; i++) n[A.silPick({ trait: t })]++; o[t] = Object.fromEntries(Object.entries(n).map(([k, v]) => [k, +(v / 3000).toFixed(2)])); } return JSON.stringify(o); }'''))
        check('stances follow character: the Devout hide, the Warlike arm, the Curious race outward', r['Devout']['hide'] > .6 and r['Warlike']['arm'] > .6 and r['Curious']['race'] > .55 and r['Mercantile']['race'] > r['Mercantile']['arm'], str(r))
        T = await ev("() => window.__aoh.SIL_FEAR")
        r = json.loads(await ev(r'''(T) => { const A = window.__aoh, W = A.W, t0 = W.sil.t0, f = x => { W.sil.t0 = W.simTime - x; return +A.silFear().toFixed(3); }; const o = [f(0), f(T / 2), f(T + 5)];
          W.sil.t0 = W.simTime - T * .6; A.silTick(1); A.silTick(1); const l = W.hist.filter(e => /first terror of the ruins eases/.test(e.h)).length; W.sil.t0 = t0; return JSON.stringify({ o, l }); }''', T))
        check('the fear starts full and fades away; its easing is told once', r['o'] == [1, .5, 0] and r['l'] == 1, str(r))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, c = W.civs.find(c => c.alive), o = {};
          const run = k => { W.sil.stance[c.id] = k; c.mods = c.mods.filter(m => !/Gone quiet|Arming|Racing/.test(m.name)); const m0 = c.military; A.silTick(1); A.silTick(1); const m = c.mods.filter(m => /Gone quiet|Arming|Racing/.test(m.name)); return { n: m.length, tech: m[0] && m[0].techMul, stab: m[0] && m[0].stab, dm: c.military - m0, ships: A.silShips(c) }; };
          c.military = 30; o.hide = run('hide'); o.arm = run('arm'); o.race = run('race'); const t0 = W.sil.t0; W.sil.t0 = W.simTime - 1e4; o.after = A.silShips(c); W.sil.t0 = t0; return JSON.stringify(o); }'''))
        check('hiding slows research, steadies a people and cuts its colony ships', r['hide']['n'] == 1 and r['hide']['tech'] < 1 and r['hide']['stab'] > 0 and r['hide']['ships'] < .5, str(r['hide']))
        check('arming builds armies and costs calm', r['arm']['n'] == 1 and r['arm']['dm'] > 1 and r['arm']['stab'] < 0, str(r['arm']))
        check('racing speeds research and doubles the colony ships; once the fear fades, ships are back to normal', r['race']['n'] == 1 and r['race']['tech'] > 1 and abs(r['race']['ships'] - 2) < .05 and r['after'] == 1, str(r))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, S0 = W.sil, base = (() => { W.sil = null; const d = A.fateDrives(); W.sil = S0; return d; })(), o = {};
          for (const k of ['hide', 'arm', 'race']) { for (const c of W.civs.filter(c => c.alive)) W.sil.stance[c.id] = k; const d = A.fateDrives(); o[k] = Object.fromEntries(Object.keys(d).map(id => [id, +(d[id] - base[id]).toFixed(3)])); }
          const t0 = W.sil.t0; W.sil.t0 = W.simTime - A.SIL_FEAR / 2; for (const c of W.civs.filter(c => c.alive)) W.sil.stance[c.id] = 'hide'; const half = +(A.fateDrives().silence - base.silence).toFixed(3); W.sil.t0 = t0;
          return JSON.stringify({ o, half, base: { contact: base.contact, threebody: base.threebody } }); }'''))
        o = r['o']
        check('a world gone quiet presses toward the Silence and the Garden, away from contact and the Three-Sun Signal', o['hide']['silence'] > .85 and o['hide']['garden'] > .25 and o['hide']['contact'] <= 0 and o['hide']['threebody'] <= 0 and o['hide']['contact'] < 0 or (r['base']['contact'] == 0 and o['hide']['contact'] == 0), str(o['hide']))
        check('an armed world presses toward collapse, the waking machines and the Long Night, away from the Garden', o['arm']['collapse'] > .25 and o['arm']['agi'] > .25 and o['arm']['longnight'] > .2 and o['arm']['garden'] <= 0, str(o['arm']))
        check('a racing world presses toward the Branching, contact and the Signal', o['race']['speciation'] > .35 and o['race']['contact'] > .25 and o['race']['threebody'] > .15, str(o['race']))
        check('the pressure fades with the fear', abs(r['half'] - .45) < .03, str(r['half']))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; A.updateUI(); const clock = document.querySelector('#futures').innerText; const card = A.tipBody({ civ: W.civs.find(c => c.alive) })[1].replace(/<[^>]+>/g, ' ');
          return JSON.stringify({ clock, card }); }'''))
        check('the Great Silence panel counts the stances; the card shows a people’s stance', 'gone quiet' in r['clock'] and 'arming' in r['clock'] and 'racing outward' in r['clock'] and 'After the ruins' in r['card'], r['clock'].replace('\n', ' | ')[:160] + ' || ' + r['card'][-80:])
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W, F = W.fates; for (const c of W.civs.filter(c => c.alive)) W.sil.stance[c.id] = 'hide'; const a = F.active.find(a => a.id === 'silence'); a.t0 = W.simTime - A.FATES.silence.span - 2; W.sil.t0 = W.simTime;
          A.fateTick(1); return JSON.stringify({ ended: F.ended, d: +A.fateDrives().silence.toFixed(2) }); }'''))
        check('a world that has gone quiet can keep the Silence: the Silence Kept ending', r['ended'] == 'silence', str(r))
        r = json.loads(await ev(r'''() => { const A = window.__aoh, W = A.W; const d = A.serialize(), back = A.sanitizeWorld(JSON.parse(JSON.stringify(d))); const bad = JSON.parse(JSON.stringify(d)); bad.sil.stance = { 5: 'hide', 6: 'boom', x: 'arm', 7: 3 };
          const old = JSON.parse(JSON.stringify(d)); delete old.sil.stance; return JSON.stringify({ same: JSON.stringify(back.sil.stance) === JSON.stringify(W.sil.stance), bad: A.sanitizeWorld(bad).sil.stance, old: A.sanitizeWorld(old).sil.stance }); }'''))
        check('stances are saved and loaded back; bad values dropped; old saves have none', r['same'] and r['bad'] == {'5': 'hide'} and r['old'] == {}, str(r))
        print('errors:', errs[:3] if errs else 'no errors')
        print(f'{sum(results)}/{len(results)} passed')
        await b.close()
asyncio.run(main())
