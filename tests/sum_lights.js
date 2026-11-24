async () => { const A = window.__aoh, W = A.W, V = A.V; scrollTo(0, 0); const out = { colonies: 0, drawnOk: 0, minN: 1e9, maxN: 0, notMonotone: 0, byPop: {} };
  const c2 = document.querySelector('#world').getContext('2d'), arc = c2.arc, fill = c2.fill, bp = c2.beginPath;
  A.setZoom(A.LENS_Z); A.render(); const rows = (W.stars || []).map(st => [st.pop, A.worldLightCount(st) / A.worldLights(st).length]).sort((a, b) => a[0] - b[0]); out.minSpots = Math.min(...(W.stars || []).map(st => A.worldLights(st).length), 1e9);
  // on the same world, more people never means fewer lights (each world's own spots; one with little land on its night side has fewer)
  for (const st of W.stars || []) { const p0 = st.pop; let last = -1; for (const m of [.1, .3, 1, 3, 10, 30, 100]) { st.pop = p0 * m; const n = A.worldLightCount(st); if (n < last) out.notMonotone++; last = n; } st.pop = p0; }
  for (const st of (W.stars || []).slice(0, 12)) { out.colonies++; const want = A.worldLightCount(st); out.minN = Math.min(out.minN, want); out.maxN = Math.max(out.maxN, want);
    const b = Math.floor(Math.log10(Math.max(1, st.pop))); out.byPop['1e' + b] = (out.byPop['1e' + b] || []).concat(want);
    V.focus = null; A.focusWorld(st); V.focus.t0 = performance.now() - 2000; let cur = [], n = -1;
    c2.beginPath = function () { cur = []; return bp.call(this); }; c2.arc = function (x, y, r, ...q) { cur.push(1); return arc.call(this, x, y, r, ...q); };
    c2.fill = function (...q) { if (n < 0 && /rgba\(255,\s*226,\s*160/.test(this.fillStyle)) n = cur.length; return fill.apply(this, q); };
    A.render(); c2.arc = arc; c2.fill = fill; c2.beginPath = bp; if (n === want) out.drawnOk++; }
  V.focus = null; for (const k in out.byPop) out.byPop[k] = Math.min(...out.byPop[k]) + '-' + Math.max(...out.byPop[k]); return JSON.stringify(out); }
