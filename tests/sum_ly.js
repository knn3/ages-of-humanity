() => { const A = window.__aoh, W = A.W, V = A.V, out = { worlds: 0, withLy: 0, right: 0, ships: 0, cardLy: 0 };
  const want = i => { const d = A.STAR_LY[A.XSTARS[i][0]]; return (d < 20 ? d.toFixed(1).replace(/\.0$/, '') : Math.round(d).toLocaleString('en-US')) + ' light years from Earth'; };
  for (const st of W.stars || []) { out.worlds++; const L = A.worldLines(st).join(' '); if (/light years from Earth/.test(L)) out.withLy++; if (L.includes(A.XSTARS[st.star][0] + ', ' + want(st.star))) out.right++; }
  for (const sh of W.ships || []) { out.ships++; const b = A.orbitTipBody({ kind: 'voyage', d: sh, c: null })[1]; if (b.includes(want(sh.star))) out.cardLy++; }
  return JSON.stringify(out); }
