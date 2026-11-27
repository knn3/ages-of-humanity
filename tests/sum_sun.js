() => { const A = window.__aoh, W = A.W, F = W.fates;
  // WE-01 real data: did the Sun begin to swell (how: pressure, event, the date), how far, its heat, its chronicle lines, and the save
  const h = F.hist.filter(e => e.id === 'wandering'), lines = (W.hist || []).filter(e => e.k === 'nature' && /^The Sun |^A swollen orange Sun/.test(e.h)).length;
  const starts = (W.hist || []).filter(e => /The Dying Sun\./.test(e.h)).map(e => e.y);
  const back = A.sanitizeWorld(JSON.parse(JSON.stringify(A.serialize())));
  return JSON.stringify({ year: Math.round(W.year), wand: h.map(e => e.y0 + (e.y1 ? '-' + e.y1 + ':' + e.out : '')), starts, k: +A.sunK().toFixed(3), heat: +A.sunHeat().toFixed(2), temp: +A.temp().toFixed(2), gh: +A.tempGH().toFixed(2),
    lines, said: W.sun ? W.sun.said : null, ended: F.ended, saved: JSON.stringify(back.sun) === JSON.stringify(W.sun || { k: 0, said: 0 }), hot: !!(W.hot && W.hot.on), sea: +(W.seaRise || 0).toFixed(1) }); }
