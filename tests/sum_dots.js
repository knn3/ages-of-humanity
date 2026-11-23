() => { const A = window.__aoh, W = A.W, V = A.V, cv = document.querySelector('#world'); scrollTo(0, 0); const out = { colonies: (W.stars || []).length };
  for (const z of [.00011, .00005]) { A.V.focus = null; A.V.lensShip = null; A.setZoom(z); A.render(); const r = cv.getBoundingClientRect();
    const dots = V.orbPicks.filter(q => q.kind === 'starcol' && q.x > 5 && q.y > 5 && q.x < cv.clientWidth - 5 && q.y < cv.clientHeight - 5); let ok = 0, wrong = 0;
    for (const q of dots) { A.V.focus = null; A.render(); const p = A.V.orbPicks.find(o => o.kind === 'starcol' && o.d === q.d); if (!p) continue;
      const o = { bubbles: true, cancelable: true, clientX: r.left + p.x, clientY: r.top + p.y, pointerId: 1, pointerType: 'mouse', isPrimary: true, button: 0 };
      cv.dispatchEvent(new PointerEvent('pointerdown', o)); cv.dispatchEvent(new PointerEvent('pointerup', o));
      if (V.focus && V.focus.body === 'world') { if (V.focus.st === q.d || (V.focus.st.star === q.d.star)) ok++; else wrong++; } else wrong++; }
    out['z' + z] = ok + '/' + dots.length + (wrong ? ' wrong ' + wrong : ''); }
  A.V.focus = null; return JSON.stringify(out); }
