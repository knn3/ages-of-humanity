() => { const A = window.__aoh, W = A.W, ch = [...W.chron].reverse(), h = W.fates.hist.find(e => e.id === 'threebody');
  if (!h) return 'no Three-Sun future in this world';
  const ly = (ch.find(e => /sentinels/.test(e.h)) || {}).y, y1 = h.y1 == null ? 1e9 : h.y1;
  const eraUps = ch.filter(e => e.k === 'era' && /enter the/.test(e.h) && ly != null && e.y > ly && e.y < y1).length;
  const pick = re => ch.filter(e => re.test(e.h)).map(e => e.h.replace(/<[^>]+>/g, '').slice(0, 95));
  return JSON.stringify({ began: h.y0, ended: h.y1, out: h.out, stances: pick(/ become (Escapists|Defenders|Worshippers|Defeatists)/).length, lock: ly, eraUpsDuringLock: eraUps, strategist: pick(/given a plan/)[0], probe: pick(/probe/)[0], sabotage: pick(/sabotage/).length, escapes: pick(/escape ship/).length, reveal: pick(/secret is revealed/)[0], active: !!W.tb }); }
