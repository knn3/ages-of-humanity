() => { const A = window.__aoh, W = A.W, F = W.fates, H = W.hist || [], S = W.sil;
  // SIL-01 real data: did the Great Silence run, were the ruins found (how many, by whom, kinds), chronicle lines, saved
  const cnt = re => H.filter(e => re.test(e.h)).length, back = A.sanitizeWorld(JSON.parse(JSON.stringify(A.serialize())));
  return JSON.stringify({ silence: F.hist.filter(e => e.id === 'silence').map(e => e.y0 + (e.y1 ? '-' + e.y1 + ':' + e.out : '…')), ended: F.ended,
    sites: S ? S.sites.map(t => t.kind + ':' + t.dead) : null, by: S ? S.byName : null, found: cnt(/The ruins among the stars/), perSite: S ? S.sites.filter(t => H.some(e => e.h.toLowerCase().includes(t.name.toLowerCase() + ':'))).length : 0,
    saved: !S ? back.sil === null : !!back.sil && back.sil.sites.length === S.sites.length }); }
