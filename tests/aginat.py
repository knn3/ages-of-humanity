# "Real data" runs for the AGI takeover epic: natural worlds (nothing forced) run for SECONDS of sim time,
# tracking machine autonomy per people, when it crosses 30/60/90, and whether the Waking Machines start and end the world.
# AGI-04: records each machine uprising (when, whose machines, outcome, how long, peoples overrun, largest share of land).
# AGI-03: after the takeover the world runs on for CARE seconds (env CARE, default 400) to see the caretakers at work.
# usage: python aginat.py [N=12] [SECONDS=3000]   (GAME=/path/to/index.html to run another build)
import asyncio, json, sys
from playwright.async_api import async_playwright
import os, pathlib
GAME = pathlib.Path(os.environ.get('GAME') or pathlib.Path(__file__).resolve().parents[1].joinpath('index.html')).resolve().as_uri()
_CH = os.environ.get('CHROME')
LAUNCH = {'args': ['--no-sandbox'], **({'executable_path': _CH} if _CH else {})}
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
SEC = float(sys.argv[2]) if len(sys.argv) > 2 else 3000
CARE = float(os.environ.get('CARE', 400))
RUN = r'''([seed, sec, care]) => { const A = window.__aoh; A.newWorld(seed); const W = () => A.W, has = !!A.machAdd;
  const o = { maxMach: 0, avgAtEdge: null, cross: {}, aiEvents: 0, fates: [], endings: [], cycles: 1, byTrait: {}, saidLines: 0, answers: {}, wars: 0, endMach: {} };
  let ended = null, nh = 0, top = null, nw = 0, mwRec = null; o.mw = [];
  const ANS = [['race', /smarter machines|race on, giving/], ['ban', /ban thinking machines|renew the ban/], ['army', /drones and robot soldiers|swarms of drones/], ['sell', /sell their thinking machines|new generation of machines/]];
  for (let i = 0; i < sec * 10; i++) { A.step(0.1); const w = W();
    for (const e of w.chron) { if (e === top) break; for (const [k, re] of ANS) if (re.test(e.h)) { let c = null, bi = 1e9; for (const x of w.civs) { const j = e.h.indexOf(x.name); if (j >= 0 && j < bi) { bi = j; c = x; } } const key = k + ':' + (c ? c.trait.slice(0, 3) : '?'); o.answers[key] = (o.answers[key] || 0) + 1; } } top = w.chron[0];
    if (w.wars.length > nw) o.wars += w.wars.length - nw; nw = w.wars.length;
    if (w.mw && !mwRec) { const p = w.civs.find(c => c.id === w.mw.parent); mwRec = { t: Math.round(w.simTime), trait: p ? p.trait.slice(0, 3) : '?', era: p ? p.era : null, why: w.mw.why, maxShare: 0, out: null }; o.mw.push(mwRec); }
    if (mwRec && w.mw) { mwRec.maxShare = Math.max(mwRec.maxShare, w.mw.share || 0); if (w.mw.done && !mwRec.out) { mwRec.out = w.mw.done; mwRec.dur = Math.round(w.simTime - w.mw.t0); mwRec.kills = w.mw.kills || 0; } }
    if (mwRec && !w.mw) { if (!mwRec.out) mwRec.out = 'fell with the world'; mwRec = null; }
    if (has && i % 10 === 0) for (const c of w.civs) if (c.alive) { o.maxMach = Math.max(o.maxMach, c.mach || 0);
      for (const t of [30, 60, 90]) if ((c.mach || 0) >= t && o.cross[t] == null) o.cross[t] = { t: Math.round(w.simTime), era: c.era, trait: c.trait };
      o.byTrait[c.trait] = Math.max(o.byTrait[c.trait] || 0, Math.round(c.mach || 0)); }
    if (w.fates.edgeT != null && o.avgAtEdge == null && has) { const cs = w.civs.filter(c => c.alive); o.avgAtEdge = Math.round(cs.reduce((a, c) => a + (c.mach || 0), 0) / cs.length); }
    while (nh < w.fates.hist.length) { const h = w.fates.hist[nh++]; o.fates.push(h.id + '@' + Math.round(w.simTime)); }
    if (w.fates.ended && w.fates.ended !== ended) o.endings.push(w.fates.ended + '@c' + w.fates.cycle); ended = w.fates.ended;
    if (w.fates.cycle < o.cycles) nh = 0; o.cycles = w.fates.cycle; if (w.fates.hist.length < nh) nh = w.fates.hist.length;
    if (!w.civs.some(c => c.alive)) break;
    if (ended && !w.fates.riseAt && !['doom'].includes(A.ENDINGS[ended].kind)) break; }
  if (ended === 'agi' && W().care && A.careOf) { const w = W(), K = w.care, kept = () => w.civs.filter(A.careOf), cut = () => { let a = 0, n = 0; for (const c of kept()) if (c._.nat) { a += c._.nat.fr; n++; } return n ? +(a / n).toFixed(2) : null; };
    const k0 = kept(), t0 = new Map(k0.map(c => [c.id, c.era * 100 + c.tech])), q = { kept0: k0.length, free0: K.free.length, freeTraits: w.civs.filter(c => c.alive && !A.careOf(c)).map(c => c.trait.slice(0, 3) + Math.round(c.mach || 0)), stab0: Math.round(k0.reduce((a, c) => a + c.stability, 0) / k0.length), fr0: cut(), poll0: Math.round(w.pollution), warN: w.warCount || 0 };
    let keptWars = 0; for (let i = 0; i < care * 10; i++) { A.step(0.1); if (i % 10 === 0) keptWars += w.wars.filter(x => A.careOf(A.W.civs.find(c => c.id === x.a)) || A.careOf(A.W.civs.find(c => c.id === x.b))).length; }
    const k1 = kept(); q.kept1 = k1.length; q.joined = w.chron.filter(e => /give in at last/.test(e.h)).length; q.stab1 = k1.length ? Math.round(k1.reduce((a, c) => a + c.stability, 0) / k1.length) : null; q.fr1 = cut(); q.poll1 = Math.round(w.pollution);
    q.techGain = Math.max(0, ...k1.filter(c => t0.has(c.id)).map(c => Math.round(c.era * 100 + c.tech - t0.get(c.id)))); q.keptWars = keptWars; q.allWars = (w.warCount || 0) - q.warN; q.lines = w.chron.filter(e => /caretakers|history lessons end|no decision of any weight|Nothing new has been invented|armies of .* are quietly/.test(e.h)).length; q.alive = w.civs.filter(c => c.alive).length; o.care = q; }
  for (const c of W().civs) if (c.alive && c.era >= 10) { const t = c.trait.slice(0, 3); (o.endMach[t] = o.endMach[t] || []).push(Math.round(c.mach || 0)); }
  o.aiEvents = W().fates.ai || 0; o.saidLines = W().chron.filter(e => /to thinking machines\.|write most of their laws|decide almost everything/.test(e.h)).length;
  o.maxMach = Math.round(o.maxMach); o.t = Math.round(W().simTime);
  const s1 = A.serialize(); let saveOk = true; try { A.loadWorld(JSON.parse(JSON.stringify(s1))); for (let i = 0; i < 20; i++) A.step(0.1); A.render(); } catch (e) { saveOk = String(e); } o.saveOk = saveOk;
  return JSON.stringify(o); }'''
async def worker(b, seeds, out, errs):
    pg = await b.new_page(viewport={'width': 1300, 'height': 850})
    pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
    await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
    await pg.goto(GAME); await pg.wait_for_timeout(600); await pg.keyboard.press('Space')
    for s in seeds: out.append((s, json.loads(await pg.evaluate(RUN, [s, SEC, CARE]))))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(**LAUNCH); out = []; errs = []
        seeds = [7000 + 53 * i for i in range(N)]
        await asyncio.gather(*[worker(b, seeds[k::6], out, errs) for k in range(min(6, N))])
        await b.close()
    out.sort()
    for s, o in out: print(f'seed {s}:', json.dumps(o))
    fs = [f.split('@')[0] for _, o in out for f in o['fates']]
    ends = {}
    for _, o in out:
        for e in o['endings']: k = e.split('@')[0]; ends[k] = ends.get(k, 0) + 1
    agiW = sum(1 for _, o in out if any(f.startswith('agi@') for f in o['fates']))
    print(f"\nworlds {len(out)} | max machine autonomy per world {[o['maxMach'] for _, o in out]} | world average when the first people finished the Future Age {[o['avgAtEdge'] for _, o in out]}")
    for t in ('30', '60', '90'):
        cr = [o['cross'][t] for _, o in out if t in o['cross']]
        print(f"  crossed {t}: {len(cr)} worlds | ages {sorted(c['era'] for c in cr)} | first traits {[c['trait'][:3] for c in cr]}")
    print(f"chronicle lines {sum(o['saidLines'] for _, o in out)} | AI Awakenings {sum(o['aiEvents'] for _, o in out)} | worlds where the Waking Machines began {agiW} | futures begun {len(fs)}: {dict((k, fs.count(k)) for k in sorted(set(fs)))}")
    ans = {}
    for _, o in out:
        for k, v in o['answers'].items(): ans[k] = ans.get(k, 0) + v
    em = {}
    for _, o in out:
        for t, v in o['endMach'].items(): em.setdefault(t, []).extend(v)
    print('answers to AI pressure (answer:character):', dict(sorted(ans.items(), key=lambda x: -x[1])), '| wars begun', sum(o['wars'] for _, o in out))
    print('average meter at the end by character:', {t: round(sum(v) / len(v)) for t, v in em.items() if v})
    print('endings:', ends, '| save ok', sum(1 for _, o in out if o['saveOk'] is True))
    cw = [(s, o['care']) for s, o in out if o.get('care')]
    for s, q in cw: print(f'  caretakers seed {s}:', json.dumps(q))
    ups = [(s, u) for s, o in out for u in o.get('mw', [])]
    for s, u in ups: print(f'  uprising seed {s}:', json.dumps(u))
    if ups:
        outs = {}
        for _, u in ups: outs[str(u['out'])] = outs.get(str(u['out']), 0) + 1
        print(f"machine uprisings {len(ups)} in {len(set(s for s, _ in ups))} worlds | whose machines {sorted(u['trait'] for _, u in ups)} | outcomes {outs} | war lengths {sorted(u.get('dur', -1) for _, u in ups)} | peoples overrun {sum(u.get('kills', 0) for _, u in ups)} | largest machine share {sorted(round(u['maxShare'], 2) for _, u in ups)}")
    if cw: print(f"caretaker worlds {len(cw)} | holdouts at the start {sum(q['free0'] for _, q in cw)} (joined later {sum(q['joined'] for _, q in cw)}) | wars touching peoples in care {sum(q['keptWars'] for _, q in cw)} | tech gained in care (max) {max(q['techGain'] for _, q in cw)} | stability {[(q['stab0'], q['stab1']) for _, q in cw]} | forest share in care {[(q['fr0'], q['fr1']) for _, q in cw]} | pollution {[(q['poll0'], q['poll1']) for _, q in cw]}")
    print('\n'.join(errs[:5]) or 'no errors')
asyncio.run(main())
