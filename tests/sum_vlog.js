() => { const A = window.__aoh, W = A.W, V = A.V, now = Math.round(W.year); scrollTo(0, 0);
  const all = [...(W.ships || []).map(s => ['ship', s]), ...(W.stars || []).map(s => ['star', s]), ...(W.lost || []).map(s => ['lost', s])];
  let bad = [];
  for (const [t, s] of all) { const L = s.log || [], ks = L.map(e => e.k), ys = L.map(e => e.y);
    if (!L.length || ks[0] !== 'launch') bad.push(t + ':nolaunch'); if (ys.some((y, i) => i && y < ys[i - 1])) bad.push(t + ':order'); if (ys.some(y => y > now + 1)) bad.push(t + ':future');
    if (t === 'star' && ks[ks.length - 1] !== 'arrive') bad.push('star:noarrive'); if (t === 'lost' && ks[ks.length - 1] !== 'lost') bad.push('lost:nolost'); if (t === 'ship' && (ks.includes('arrive') || ks.includes('lost'))) bad.push('ship:ended');
    if (t === 'ship' && !!s.forgot !== ks.includes('forgot')) bad.push('ship:forgot'); }
  const cnt = k => all.reduce((n, [, s]) => n + (s.log || []).filter(e => e.k === k).length, 0), hist = re => (W.hist || []).filter(e => re.test(e.h)).length;
  // open each ship's card in the lens and compare its bar with its progress
  A.setZoom(.00003); A.render(); const cv = document.querySelector('#world'), rc = cv.getBoundingClientRect(); let cards = 0, barOff = 0, logOff = 0;
  for (const q of V.orbPicks.filter(q => q.kind === 'voyage')) { cv.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: rc.left + q.x, clientY: rc.top + q.y, button: 2 }));
    const t = document.querySelector('#tip'), i = t.querySelector('.pb i'); if (t.style.display === 'none' || !i) continue; cards++; const f = (W.simTime - q.d.t0) / q.d.dur * 100;
    if (Math.abs(parseFloat(i.style.width) - Math.min(100, f)) > 1.5) barOff++; if (t.querySelectorAll('.vl').length !== q.d.log.length) logOff++; const b = document.querySelector('#tipClose'); if (b) b.click(); }
  return JSON.stringify({ ships: (W.ships || []).length, stars: (W.stars || []).length, lostMarks: (W.lost || []).length, bad: [...new Set(bad)], mutiny: cnt('mutiny') + '/' + hist(/Mutiny aboard/), plague: cnt('plague') + '/' + hist(/Plague aboard/), forgot: cnt('forgot') + '/' + hist(/forgotten they are on a ship/), arrive: cnt('arrive') + '/' + hist(/ reaches [A-Z]/), cards, barOff, logOff }); }
