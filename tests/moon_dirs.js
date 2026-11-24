() => { const A = window.__aoh; A.UI.paused = true;
  const snap = (day, t) => { A.V.dayT = day; A.W.simTime = t; A.setZoom(.0004); A.render(); return { sun: [...A.V.sunXY], e: [A.V.cx, A.V.cy], b: JSON.parse(JSON.stringify(A.V.bodyPos)), rot: A.V.sysRot || 0 }; };
  const ang = (p, c) => Math.atan2(p[1] - c[1], p[0] - c[0]), wrap = a => (a + 3 * Math.PI) % (2 * Math.PI) - Math.PI, sg = v => v > 0 ? 'cw' : 'ccw';
  const inert = (s, p) => ang(p, s.sun) - s.rot, a = snap(.3, 5000), b = snap(.3 + 1 / 48, 5001), out = {};
  for (const n of ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']) out[n] = sg(wrap(inert(b, b.b[n]) - inert(a, a.b[n])));
  out.Earth = sg(wrap(inert(b, b.e) - inert(a, a.e)));
  out.spin = sg(-wrap(ang(b.sun, b.e) - ang(a.sun, a.e)));
  A.V.moonD = 5; A.setZoom(.03); A.V.dayT = .3; A.render(); const p = [...A.V.bodyPos.Moon]; A.V.moonD = 5.5; A.render(); const q = [...A.V.bodyPos.Moon];
  out.Moon = sg(wrap(ang(q, [A.V.cx, A.V.cy]) - ang(p, [A.V.cx, A.V.cy])));
  const y0 = snap(.3, 5000), y1 = snap(.3, 5006); out.earthLaps = +(wrap(inert(y1, y1.e) - inert(y0, y0.e)) / (2 * Math.PI) * 10).toFixed(3);
  return out; }
