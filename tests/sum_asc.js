() => { const A = window.__aoh, W = A.W, F = W.fates, H = W.hist || [];
  // ASC-01 real data: did the Great Upload run, who uploaded how far (by character), who refused, minds in the machines, how it ended
  const cnt = re => H.filter(e => re.test(e.h)).length, S = W.asc, back = A.sanitizeWorld(JSON.parse(JSON.stringify(A.serialize())));
  const per = S ? W.civs.filter(c => S.up[c.id] || (S.said[c.id] & 8)).map(c => c.trait.slice(0, 3) + ':' + Math.round((S.up[c.id] || 0) * 100) + (c.alive ? '' : '†')) : [];
  return JSON.stringify({ asc: F.hist.filter(e => e.id === 'ascension').map(e => e.y0 + (e.y1 ? '-' + e.y1 + ':' + e.out : '…')), ended: F.ended, per, minds: S ? +(Object.values(S.minds).reduce((a, b) => a + b, 0) / 1e9).toFixed(2) + 'B' : 0,
    share: +A.ascShare().toFixed(2), begin: cnt(/begin to upload their minds/), half: cnt(/now live in the machines/), last: cnt(/have left their bodies/), refuse: cnt(/refuse the upload/),
    saved: !S ? back.asc === null : !!back.asc && Object.keys(S.up).every(k => Math.abs(back.asc.up[k] - S.up[k]) < 1e-3) }); }
