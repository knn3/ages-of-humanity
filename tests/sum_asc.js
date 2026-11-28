() => { const A = window.__aoh, W = A.W, F = W.fates, H = W.hist || [];
  // ASC-01 real data: did the Great Upload run, who uploaded how far (by character), who refused, minds in the machines, how it ended
  const cnt = re => H.filter(e => re.test(e.h)).length, S = W.asc, back = A.sanitizeWorld(JSON.parse(JSON.stringify(A.serialize())));
  const per = S ? W.civs.filter(c => S.up[c.id] || (S.said[c.id] & 8)).map(c => c.trait.slice(0, 3) + ':' + Math.round((S.up[c.id] || 0) * 100) + (c.alive ? '' : '†')) : [];
  return JSON.stringify({ asc: F.hist.filter(e => e.id === 'ascension').map(e => e.y0 + (e.y1 ? '-' + e.y1 + ':' + e.out : '…')), ended: F.ended, per, minds: S ? +(Object.values(S.minds).reduce((a, b) => a + b, 0) / 1e9).toFixed(2) + 'B' : 0,
    share: +A.ascShare().toFixed(2), begin: cnt(/begin to upload their minds/), half: cnt(/now live in the machines/), last: cnt(/have left their bodies/), refuse: cnt(/refuse the upload/),
    // ASC-02: forests and animals on uploaded land (peoples ≥ 50% uploaded) against everyone else's, and how far it has grown over
    green: S && S.green ? Object.entries(S.green).filter(([k, v]) => v > .05).map(([k, v]) => k + ':' + Math.round(v * 100)) : [], reclaim: (() => { const up = [], rest = []; for (const c of W.civs) { if (!c.alive || !c._.nat) continue; ((S && S.up[c.id] >= .5) ? up : rest).push(c._.nat); } const av = (a, k) => a.length ? +(a.reduce((s, n) => s + n[k], 0) / a.length).toFixed(2) : null; return { up: [av(up, 'fr'), av(up, 'w')], rest: [av(rest, 'fr'), av(rest, 'w')] }; })(),
    saplings: cnt(/Saplings push up through the empty streets/), sinking: cnt(/are sinking under forest/),
    // ASC-03: holdout peoples (split from whom, or Devout from the start), tension, how it ended; lines
    hold: S && S.hold ? Object.entries(S.hold).map(([k, H]) => { const h = W.civs.find(c => c.id === +k); return (h ? h.name.slice(0, 6) : k) + (H.from != null ? '<' + H.from : '') + ':' + (H.out || Math.round(H.ten * 100) + '%') + (H.end ? '/' + H.end : '') + (h && !h.alive ? '†' : ''); }) : [],
    split: cnt(/break away and call themselves/), tomb: cnt(/data centres of .* tombs/), sab: cnt(/Saboteurs from/), uneasy: cnt(/sign an uneasy peace/), march: cnt(/march on the data centres/), plugs: cnt(/pull the plugs/), drones: cnt(/Drones flown by the uploaded/),
    saved: !S ? back.asc === null : !!back.asc && Object.keys(S.up).every(k => Math.abs(back.asc.up[k] - S.up[k]) < 1e-3) }); }
