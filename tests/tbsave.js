() => { const A = window.__aoh, out = []; if (!A.W.tb) { A.startFate('threebody', 'event'); }
  for (const stage of ['deter', 'strike']) {
    for (let i = 0; i < 6000 && A.W.tb && !(stage === 'deter' ? A.W.tb.deter : A.W.tb.strikeT); i++) { if (stage === 'strike' && A.W.tb.deter && i === 10) A.tbBroadcast(null); A.step(0.1); }
    if (!A.W.tb) { out.push(stage + ': story ended first'); continue; }
    const a = JSON.stringify(A.W.tb, (k, v) => typeof v === 'number' ? Math.round(v) : v); A.loadWorld(A.serialize()); const b = JSON.stringify(A.W.tb, (k, v) => typeof v === 'number' ? Math.round(v) : v);
    out.push(stage + ': ' + (a === b ? 'saved exactly' : 'DIFF ' + [...a].findIndex((ch, i) => ch !== b[i]) + ' ' + a.slice(0, 400) + ' VS ' + b.slice(0, 400))); }
  return out.join(' | '); }
