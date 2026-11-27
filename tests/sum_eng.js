() => { const A = window.__aoh, W = A.W, F = W.fates, H = W.hist || [];
  // WE-02 real data: was the Dying Sun reached, who built engines, how far they got, how often war stalled them, and how it ended
  const cnt = re => H.filter(e => re.test(e.h)).length, wand = F.hist.filter(e => e.id === 'wandering').map(e => e.y0 + (e.y1 ? '-' + e.y1 + ':' + e.out : '…'));
  const back = A.sanitizeWorld(JSON.parse(JSON.stringify(A.serialize())));
  return JSON.stringify({ wand, ended: F.ended, cycle: F.cycle, begun: cnt(/begin a planet engine/), finished: cnt(/planet engine of .* is finished/), stalls: cnt(/Work on the planet engines stops/), resumed: cnt(/work on the planet engines begins again/),
    truces: cnt(/With the engines waiting/), half: cnt(/Half of the planet engines/), ready: cnt(/Every planet engine stands complete/), voyage: cnt(/The Long Voyage/), eng: W.eng ? { n: Object.keys(W.eng.by).length, P: +A.engProgress().toFixed(2), done: W.eng.done } : null,
    saved: !W.eng ? back.eng === null : !!back.eng && back.eng.said === W.eng.said && back.eng.stall === !!W.eng.stall && back.eng.done === !!W.eng.done && Object.keys(W.eng.by).every(k => Math.abs(back.eng.by[k] - W.eng.by[k]) < 1e-3) && Object.keys(back.eng.by).length === Object.keys(W.eng.by).length }); }
