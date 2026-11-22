() => { const A = window.__aoh, W = A.W;
  const s1 = A.serialize(), w = A.sanitizeWorld(JSON.parse(JSON.stringify(s1)));
  const keys = ['bases', 'spaceRes', 'colonies', 'ships', 'stars', 'megas', 'dyson', 'debris', 'fates', 'warCount'];
  const lost = keys.filter(k => JSON.stringify(s1[k]) !== JSON.stringify(w[k]) && !(k === 'dyson' || k === 'fates' || k === 'debris')).join(',');
  A.loadWorld(s1); for (let i = 0; i < 30; i++) A.step(0.1); A.render();
  return JSON.stringify({ top: Math.max(...W.civs.filter(c => c.alive).map(c => c.era)), ended: A.W.fates.ended, futures: A.W.fates.hist.length, bases: A.W.bases.length, colonies: (A.W.colonies || []).length, ships: (A.W.ships || []).length, stars: (A.W.stars || []).length, swarm: Math.round((A.W.dyson || {}).total / 10) + '%', cyl: (A.W.megas || []).length, maxK: Math.max(...A.W.civs.filter(c => c.alive).map(c => A.energyOf(c))).toFixed(2), lostOnSave: lost || 'none' }); }
