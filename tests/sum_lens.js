() => { const A = window.__aoh, W = A.W, V = A.V; scrollTo(0, 0); A.setZoom(.00003); A.render(); const L = V.lens;
  const picks = V.orbPicks.filter(q => q.kind === 'voyage' || q.kind === 'starcol'), sun = V.sunXY;
  const ov = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  const labs = L ? L.labels : [], lo = labs.filter((a, i) => labs.some((b, j) => j > i && ov(a, b))).length;
  const inL = L ? picks.every(q => Math.hypot(q.x - L.x, q.y - L.y) <= L.r) : true, nearSun = picks.filter(q => Math.hypot(q.x - sun[0], q.y - sun[1]) < 20).length;
  A.setZoom(.0004); A.render(); const solar = !!V.lens;
  return JSON.stringify({ ships: (W.ships || []).length, stars: (W.stars || []).length, lens: !!L, want: (W.ships || []).length + (W.stars || []).length > 0, labels: labs.length, overlap: lo, picksInLens: inL, picks: picks.length, nearSun, solarLens: solar }); }
