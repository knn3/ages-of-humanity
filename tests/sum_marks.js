() => { const A = window.__aoh, W = A.W, V = A.V, cv = document.querySelector('#world'); scrollTo(0, 0);
  const ov = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y, box = (x, y) => ({ x: x - 4, y: y - 4, w: 8, h: 8 });
  const out = { inFlight: (W.ships || []).length, lost: (W.lost || []).length, lenses: 0, marks: 0, missing: 0, offCurve: 0, quarterOff: 0, labelOverlap: 0, offScreen: 0, unlabelled: 0 };
  const ids = [...(W.ships || []).map(s => s.id), ...(W.lost || []).map(m => m.id)];
  for (const id of ids) { V.lensShip = null; A.shipFocus(id, true); A.render(); const L = V.lens; if (!L) continue; out.lenses++;
    const T = A.lensTarget(), log = (T.kind === 'ship' ? T.sh.log : T.m.log) || [], want = log.filter(e => A.VMARK[e.k]);
    out.marks += L.marks.length; out.missing += want.length - L.marks.length;
    // where each event happened: events can only come as the voyage passes a quarter (many quarters pass with nothing)
    for (const e of log) { if (!A.VMARK[e.k]) continue; if (![1, 2, 3].some(k => e.f >= .25 * k - .001 && e.f < .25 * k + .1)) out.quarterOff++; }
    const cvv = A.shipCurve(T.star, T.id); for (const m of L.marks) { const [u, v] = cvv.p(m.f); if (Math.hypot(L.x + u * L.r - m.x, L.y + v * L.r - m.y) > .5) out.offCurve++; }
    const dots = [box(L.x, L.y), box(L.stars[0].x, L.stars[0].y), ...L.ships.map(s => box(s.x, s.y)), ...L.marks.map(m => box(m.x, m.y))];
    for (let i = 0; i < L.labels.length; i++) { const a = L.labels[i]; if (L.labels.some((b, j) => j > i && ov(a, b)) || dots.some(d => ov(a, d))) out.labelOverlap++; if (a.x < 0 || a.y < 0 || a.x + a.w > cv.clientWidth || a.y + a.h > cv.clientHeight) out.offScreen++; }
    out.unlabelled += L.marks.length + 1 + (T.kind === 'lost' ? 1 : 0) - L.labels.length; }
  V.lensShip = null; return JSON.stringify(out); }
