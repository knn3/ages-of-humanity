() => { const A = window.__aoh, W = A.W, V = A.V; scrollTo(0, 0);
  const lines = (W.hist || []).filter(e => e.sh != null), ids = [...new Set(lines.map(e => e.sh))], out = { lines: lines.length, ships: ids.length, ship: 0, lost: 0, world: 0, none: 0, bad: [] };
  // every ship line in the chronicle panel is a link
  const lis = [...document.querySelectorAll('#log li')], linked = lis.filter(li => li.classList.contains('shiplink')).length, shipish = lis.filter(li => /generation ship|Mutiny aboard|Plague aboard|forgotten they are on a ship|falls silent|reaches [A-Z]/.test(li.innerText) && !/A mission launched/.test(li.innerText)).length;
  out.panel = linked + '/' + shipish;
  for (const id of ids) {
    const k = A.shipFocus(id, true); A.render();
    if (!k) { out.none++; continue; } out[k]++;
    if (k === 'world') { if (!V.focus || V.focus.body !== 'world' || V.focus.st.sid !== id || !V.focus.st.world) out.bad.push('world ' + id); V.focus = null; }
    else { const L = V.lens; if (!L || L.id !== id || L.ships.length !== 1 || L.stars.length !== 1 || L.labels.length < 1 + (L.from ? 1 : 0)) out.bad.push(k + ' ' + id); else { const s = L.ships[0], d = L.stars[0]; if (Math.hypot(s.x - L.x, s.y - L.y) > L.r || Math.hypot(d.x - L.x, d.y - L.y) > L.r) out.bad.push('outside ' + id); } V.lensShip = null; }
  }
  // arrivals in this cycle all lead to their world
  const arr = (W.stars || []).filter(st => st.sid != null), named = arr.filter(st => st.world && lines.some(e => e.sh === st.sid && /They call their new world/.test(e.h))).length;
  out.worldsNamed = named + '/' + arr.length;
  return JSON.stringify(out); }
