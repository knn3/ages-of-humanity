() => { const A = window.__aoh, W = A.W, V = A.V; scrollTo(0, 0); A.setZoom(.00003); A.render(); const L = V.lens; if (!L) return JSON.stringify({ lens: false, ships: (W.ships || []).length, stars: (W.stars || []).length });
  const s0 = L.ships.map(s => ({ ...s })), ids = new Set((W.ships || []).map(s => s.id)), inb = [...new Set((W.ships || []).map(s => s.star))].sort((a, b) => a - b);
  let md = 1e9; for (let i = 0; i < s0.length; i++) for (let j = i + 1; j < s0.length; j++) md = Math.min(md, Math.hypot(s0[i].x - s0[j].x, s0[i].y - s0[j].y));
  const out = s0.filter(s => Math.hypot(s.x - L.x, s.y - L.y) > L.r).length;
  // progress check: step 20 sim seconds and see every surviving ship moved on toward its star (not backward)
  const dStar = s => { const sh = W.ships.find(x => x.id === s.id), st = L.stars.find(q => q.i === sh.star); return st ? Math.hypot(s.x - st.x, s.y - st.y) : 0; };
  const before = Object.fromEntries(s0.filter(s => W.ships.some(x => x.id === s.id)).map(s => [s.id, dStar(s)]));
  for (let i = 0; i < 200; i++) A.step(.1); A.setZoom(.00003); A.render();
  const L2 = V.lens, back = L2 ? L2.ships.filter(s => before[s.id] != null && W.ships.some(x => x.id === s.id) && (() => { const sh = W.ships.find(x => x.id === s.id), st = L2.stars.find(q => q.i === sh.star); return st && Math.hypot(s.x - st.x, s.y - st.y) > before[s.id] + .5; })()).length : 0;
  const silent = (W.hist || []).filter(e => /falls silent/.test(e.h)).length;
  return JSON.stringify({ ships: s0.length, drawn: s0.length === ids.size, minGap: s0.length > 1 ? +md.toFixed(1) : null, outside: out, pulsing: JSON.stringify(L.pulsing.slice().sort((a, b) => a - b)) === JSON.stringify(inb), movedBack: back, lostEver: silent, lostMarks: A.lostMarks().length, stars: (W.stars || []).length }); }
