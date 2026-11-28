() => { const A = window.__aoh, W = A.W, F = W.fates, H = W.hist || [], G = W.gdn;
  // GDN-01 real data: did the Garden future run, who took the Garden path (character, how far, population against the land's capacity,
  // forests), who left and why, chronicle lines, saved
  const cnt = re => H.filter(e => re.test(e.h)).length, back = A.sanitizeWorld(JSON.parse(JSON.stringify(A.serialize())));
  const per = G ? W.civs.filter(c => G.k[c.id] || G.on[c.id]).map(c => c.trait.slice(0, 3) + ':' + Math.round((G.k[c.id] || 0) * 100) + (G.on[c.id] ? '' : '-') + (c.alive ? ' fr' + Math.round((c._.nat ? c._.nat.fr : 0) * 100) + ' e' + c.era : '†')) : [];
  return JSON.stringify({ garden: F.hist.filter(e => e.id === 'garden').map(e => e.y0 + (e.y1 ? '-' + e.y1 + ':' + e.out : '…')), ended: F.ended, per,
    chose: cnt(/choose the Garden path/), towns: cnt(/shrunk to towns and villages/), gardeners: cnt(/live as gardeners/), leftWar: cnt(/leave the Garden path/), leftLand: cnt(/give up the Garden path/),
    errs: (window.__errs || []).length, saved: !G ? back.gdn === null : !!back.gdn && Object.keys(G.k).every(k => Math.abs(back.gdn.k[k] - G.k[k]) < 1e-3) }); }
