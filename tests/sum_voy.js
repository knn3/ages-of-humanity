() => { const A = window.__aoh, W = A.W, F = W.fates, H = W.hist || [];
  // WE-03 real data: did a voyage happen, how far it got, the Jupiter pass, how it ended; and a save round trip of W.voy
  const cnt = re => H.filter(e => re.test(e.h)).length, back = A.sanitizeWorld(JSON.parse(JSON.stringify(A.serialize())));
  return JSON.stringify({ ended: F.ended, cycle: F.cycle, wand: F.hist.filter(e => e.id === 'wandering').map(e => e.y0 + (e.y1 ? '-' + e.y1 + ':' + e.out : '…')), ready: cnt(/Every planet engine stands complete/),
    voy: W.voy ? { u: +A.voyU().toFixed(2), said: W.voy.said, jup: W.voy.jup, out: W.voy.out, a: +A.voyA().toFixed(2), done: !!W.voy.done, t: +A.temp().toFixed(1) } : null, launch: cnt(/engines fire as one. Slowly/), under: cnt(/move underground/), pull: cnt(/Jupiter’s pull/), clear: cnt(/drag the world clear/), scarred: cnt(/tears free of Jupiter/),
    saved: !W.voy ? back.voy === null : !!back.voy && back.voy.said === W.voy.said && Math.abs(back.voy.t0 - W.voy.t0) < 1e-3 && JSON.stringify(back.voy.jup) === JSON.stringify(W.voy.jup) }); }
