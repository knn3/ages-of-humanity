() => { const A = window.__aoh, W = A.W, ch = [...W.chron].reverse(), h = W.fates.hist.find(e => e.id === 'threebody');
  if (!h) return 'no Three-Sun future';
  const has = re => ch.filter(e => re.test(e.h)).length;
  return JSON.stringify({ out: h.out || (W.tb ? 'still running' : '?'), ended: W.fates.ended, deterrence: has(/take the switch/), tests: has(/do not blink/), succession: has(/switch passes/), failed: has(/hesitate a moment/), broadcast: has(/goes out to the whole galaxy/), arrived: has(/fleet arrives/), resistanceWin: has(/resistance wins/), reveal: (ch.find(e => /secret is revealed/.test(e.h)) || {}).h, arks: W.fates.arks || 0 }).replace(/<[^>]+>/g, ''); }
