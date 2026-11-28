() => { const A = window.__aoh, W = A.W, h = W.fates.hist.find(e => e.id === 'threebody'), O = W.occ;
  const pick = re => W.hist.filter(e => re.test(e.h)).length;
  if (!h && !O) return 'no Three-Sun future and no Hevari colonies';
  const bad = O ? O.towers.filter(t => !A.isLand(t.x) || !(t.g >= 0 && t.g <= 1)).length : 0;
  const al = O && O.al ? O.al : [], strange = A.occAlShare ? A.occAlShare() : 0, peak = O ? O.peakAl : undefined;
  const hit = W.civs.filter(c => c.alive && A.occAlOf && A.occAlOf(c) > .1).map(c => `${c.name}:${Math.round(A.occAlOf(c) * 100)}%`).join(' ');
  return JSON.stringify({ tb: h ? { y0: h.y0, y1: h.y1, out: h.out } : null, ended: W.fates.ended, arrived: pick(/Hevari fleet arrives/), landed: pick(/plant \d+ seed towers/), towers: O ? O.towers.map(t => `${t.name}:${t.state}:${Math.round(t.g * 100)}%`).join(' ') : '', cities: pick(/grown into a colony city/), empty: pick(/leave their colonies behind/), badTowers: bad, strange: +strange.toFixed(3), choked: pick(/Strange violet plants choke/), changing: pick(/the land itself is changing/), hit, alive: W.civs.filter(c => c.alive).length }); }
