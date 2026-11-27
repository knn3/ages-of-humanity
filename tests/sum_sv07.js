() => { const A = window.__aoh, W = A.W, V = A.V; scrollTo(0, 0);
  // SV-07 real data: colony-sent ships (in flight, lost, arrived) and how each shows in the lens, the chronicle and the save
  const fly = (W.ships || []).filter(s => s.from != null), lost = (W.lost || []).filter(m => m.from != null), arr = (W.stars || []).filter(st => st.from != null);
  const launches = (W.hist || []).filter(e => /^The settlers of /.test((e.h || '').replace(/<[^>]+>/g, '')) && e.sh != null);
  const out = { colonies: (W.stars || []).length, big: (W.stars || []).filter(st => st.pop >= A.COL_SHIP.COL_SHIP_POP).length, launches: launches.length, fly: fly.length, lost: lost.length, arrived: arr.length, depth: 0, bad: [] };
  // generations: how many hops from Earth each colony is
  const hop = st => { let n = 1, s = st, g = 0; while (s && s.from != null && g++ < 20) { s = (W.stars || []).find(x => x.star === s.from); n++; } return n; };
  for (const st of W.stars || []) out.depth = Math.max(out.depth, hop(st));
  for (const sh of fly) { const k = A.shipFocus(sh.id, true); A.render(); const L = V.lens; if (k !== 'ship' || !L || !L.from || L.from.i !== sh.from) { out.bad.push('lens ' + sh.id); continue; }
    if (Math.hypot(L.ships[0].x - L.x, L.ships[0].y - L.y) > L.r) out.bad.push('out ' + sh.id); if (!(W.stars || []).some(st => st.star === sh.from)) out.bad.push('nofrom ' + sh.id); V.lensShip = null; }
  for (const m of lost) { const k = A.shipFocus(m.id, true); A.render(); if (k !== 'lost' || !V.lens || !V.lens.from) out.bad.push('lost ' + m.id); V.lensShip = null; }
  for (const st of arr) { const k = A.shipFocus(st.sid, true); if (k !== 'world' || !/sent from/.test(A.worldLines(st).join(' '))) out.bad.push('world ' + st.sid); V.focus = null; }
  // nearest-free rule: every colony ship heads for a star that was free; no two ships or colonies share a star
  const stars = (W.ships || []).map(s => s.star).concat((W.stars || []).map(s => s.star)); out.dupStars = stars.length - new Set(stars).size;
  const back = A.sanitizeWorld(JSON.parse(JSON.stringify(A.serialize())));
  out.saved = back.ships.filter(s => s.from != null).length + '/' + fly.length + ' ' + back.stars.filter(s => s.from != null).length + '/' + arr.length;
  out.first = launches.length ? A.W.hist.indexOf(launches[0]) : null;
  return JSON.stringify(out); }
