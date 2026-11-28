() => { const A = window.__aoh, W = A.W, F = W.fates, H = W.hist || [], S = W.sil;
  // SIL-01 real data: did the Great Silence run, were the ruins found (how many, by whom, kinds), chronicle lines, saved
  const cnt = re => H.filter(e => re.test(e.h)).length, back = A.sanitizeWorld(JSON.parse(JSON.stringify(A.serialize())));
  return JSON.stringify({ silence: F.hist.filter(e => e.id === 'silence').map(e => e.y0 + (e.y1 ? '-' + e.y1 + ':' + e.out : '…')), ended: F.ended,
    sites: S ? S.sites.map(t => t.kind + ':' + t.dead) : null, by: S ? S.byName : null, found: cnt(/The ruins among the stars/), perSite: S ? S.sites.filter(t => H.some(e => e.h.toLowerCase().includes(t.name.toLowerCase() + ':'))).length : 0,
    // SIL-02: stances taken (by character), lines, and the futures that started after the find
    stances: S && S.stance ? W.civs.filter(c => S.stance[c.id]).map(c => c.trait.slice(0, 3) + ':' + S.stance[c.id]) : [], told: cnt(/go quiet\. They switch off|will not find them unready|warning to hurry/), eased: cnt(/first terror of the ruins eases/),
    after: S ? F.hist.filter(e => e.y0 > S.y).map(e => e.id) : [],
    saved: !S ? back.sil === null : !!back.sil && back.sil.sites.length === S.sites.length }); }
