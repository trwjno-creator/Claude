// ---------- scenes (v2, phrase-driven) ----------
function P(phrase, which = 's') {
  const toks = phrase.toLowerCase().split(' ').map(s => s.replace(/[.,?!:]/g, ''));
  for (const l of D.lines) {
    const ws = l.words.map(w => w.w.toLowerCase().replace(/[.,?!:]/g, ''));
    for (let i = 0; i + toks.length <= ws.length; i++) {
      let ok = true; for (let k = 0; k < toks.length; k++) if (ws[i + k] !== toks[k]) { ok = false; break; }
      if (ok) return which === 's' ? l.words[i].s : l.words[i + toks.length - 1].e;
    }
  }
  console.warn('phrase not found', phrase); return 0;
}
function LN(id) { return D.lines.find(l => l.id === id); }
function stamp(t, t0, label, col = '#ff5d5d') {
  const k = prog(t, t0, t0 + 0.25); if (k <= 0) return;
  ctx.save(); ctx.translate(W / 2, 520); ctx.rotate(-0.08); const s = lerp(1.8, 1, easeOut(k)); ctx.scale(s, s); ctx.globalAlpha = k;
  rr(-330, -80, 660, 160, 24); ctx.fillStyle = 'rgba(25,15,35,.85)'; ctx.fill(); ctx.lineWidth = 8; ctx.strokeStyle = col; ctx.stroke();
  txt(label, 0, 6, 92, col, 'center', 'Baloo', 0); ctx.restore();
}
function thought(x, y, r, a, inner) {
  if (a <= 0) return; ctx.save(); ctx.globalAlpha = a;
  circ(x - r * 0.9, y + r * 1.25, r * 0.12); fillStroke('#fff', 5); circ(x - r * 0.6, y + r * 0.95, r * 0.2); fillStroke('#fff', 5);
  ctx.beginPath(); ctx.ellipse(x, y, r * 1.25, r * 0.85, 0, 0, 7); fillStroke('#fff', 6);
  inner && inner(); ctx.restore();
}
function heart(x, y, s, col = '#ff4d6d') { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.beginPath(); ctx.moveTo(0, 30); ctx.bezierCurveTo(-60, -10, -30, -60, 0, -28); ctx.bezierCurveTo(30, -60, 60, -10, 0, 30); fillStroke(col, 5); ctx.restore(); }
function flames(x, y, a, t) {
  if (a <= 0) return; ctx.save();
  for (let i = 0; i < 7; i++) {
    const ph = (t * 2.2 + i * 0.17) % 1, xx = x + (i - 3) * 26 + Math.sin(t * 9 + i) * 6, h = (90 + rand(i) * 60) * (1 - ph * 0.4) * a;
    ctx.beginPath(); ctx.moveTo(xx - 22, y); ctx.quadraticCurveTo(xx - 26, y - h * 0.6, xx, y - h); ctx.quadraticCurveTo(xx + 26, y - h * 0.6, xx + 22, y); ctx.closePath();
    ctx.fillStyle = i % 2 ? '#ffb03a' : '#ff5a1f'; ctx.globalAlpha = 0.9 * a; ctx.fill();
  }
  ctx.restore();
}
const S = {};
S.HOOK = (t, a, b) => {
  const lt = t - a; const tMinha = P('E a minha'), tAte = P('Até a terça-feira');
  const zk = ease(prog(t, tMinha - 0.4, tMinha + 0.8));
  ctx.save();
  camera(lerp(1, 1.75, zk) * (1 + lt * 0.006), W / 2, lerp(H / 2, 1080, zk));
  bgStreet(t, 0, lt * 60);
  for (let i = 0; i < 7; i++) { const x = ((i * 190 + lt * (i % 2 ? 70 : -60)) % 1500 + 1500) % 1500 - 200; drawPerson(Object.assign(extra(i), { x, y: 1330, s: 0.62, walk: true, flip: i % 2 === 0, glow: 0.8 + 0.2 * Math.sin(t * 3 + i) }), t); }
  for (let i = 7; i < 12; i++) { if (i === 9) continue; const x = ((i * 260 + lt * (i % 2 ? 110 : -90)) % 1600 + 1600) % 1600 - 250; drawPerson(Object.assign(extra(i), { x, y: 1450, s: 0.8, walk: true, flip: i % 2 === 0, glow: 0.9 }), t); }
  const hp = prog(t, tMinha - 0.3, tMinha + 0.3);
  drawPerson(Object.assign({}, HERO, { x: W / 2, y: 1640, s: 1.05, pose: 'neck', posePrev: 'down', armP: ease(hp), emo: t > tAte ? 'shock' : hp > 0.5 ? 'sad' : 'neutral', lookY: hp > 0.5 && t < tAte ? 0.5 : 0 }), t);
  ctx.restore();
  if (t > tAte) { ctx.fillStyle = `rgba(20,30,70,${0.35 * prog(t, tAte, tAte + 0.3)})`; ctx.fillRect(0, 0, W, H); }
  vignette(0.5);
  hookText(t, 1 - prog(t, tMinha - 0.2, tMinha + 0.2));
  stamp(t, tAte, 'TERÇA-FEIRA...', '#8fd3ff');
};
S.WORLD = (t, a, b) => {
  const lt = t - a; const tCrush = P('Quando o crush'), tFogo = P('pega fogo'), tMae = P('sua mãe');
  ctx.save();
  if (t < tCrush) {
    // top: mom at office thinking; bottom: kid at school, nape warming
    camera(1 + lt * 0.01, W / 2, H / 2);
    ctx.fillStyle = vgrad(0, 960, ['#cfe3f0', '#b6d3e6']); ctx.fillRect(0, 0, W, 960);
    rr(80, 160, 360, 260, 14); fillStroke('#9fd3ff', 10, '#5b6b7a');
    rr(560, 560, 420, 40, 10); fillStroke('#c8874f', 6); rr(640, 420, 220, 150, 12); fillStroke('#2b3440', 6); rr(655, 435, 190, 120, 6); ctx.fillStyle = '#7fd0ff'; ctx.fill();
    drawPerson(Object.assign(extra(3), { x: 360, y: 960, s: 0.95, hair: 'long', hairColor: '#4a2a1a', shirt: '#e86a5a', emo: 'smile', look: 0.6, lookY: -0.4, noLegs: true }), t);
    const tb = prog(t, tMae, tMae + 0.4);
    thought(640, 240, 120, easeBack(tb), () => { ctx.save(); ctx.translate(640, 300); ctx.scale(0.42, 0.42); drawPerson(Object.assign({}, HERO, { x: 0, y: 200, s: 1, noLegs: true, emo: 'happy' }), t); ctx.restore(); });
    txt('MÃE NO TRABALHO', W / 2, 880, 54, '#fff', 'center', 'Baloo', 10);
    ctx.fillStyle = INK; ctx.fillRect(0, 955, W, 10);
    ctx.save(); ctx.beginPath(); ctx.rect(0, 965, W, 955); ctx.clip();
    ctx.translate(0, 0);
    ctx.fillStyle = vgrad(965, H, ['#f5e6c8', '#e2c79a']); ctx.fillRect(0, 965, W, 955);
    const g = 0.15 + 0.55 * prog(t, tMae + 0.5, tMae + 1.4);
    drawPerson(Object.assign(extra(6), { x: W / 2, y: 1950, s: 1.25, glow: g, emo: g > 0.5 ? 'happy' : 'neutral', noLegs: true, pose: 'neck' }), t);
    txt('morninha', W / 2 + 230, 1180, 60, '#ffb84d', 'center', 'Baloo', 10);
    ctx.restore();
  } else {
    camera(1.05 + (t - tCrush) * 0.02, W / 2, H / 2);
    bgClass(t);
    const k = prog(t, tCrush + 0.2, tCrush + 0.6);
    drawPerson(Object.assign(extra(1), { x: 260, y: 1600, s: 1.0, hair: 'long', hairColor: '#24160f', shirt: '#b48cff', emo: 'happy', look: 1, noLegs: true, blush: 1 }), t);
    thought(330, 760, 110, easeBack(k), () => { heart(330, 760, 1.2 + Math.sin(t * 8) * 0.1); });
    const f = prog(t, tFogo - 0.15, tFogo + 0.3);
    drawPerson(Object.assign(extra(4), { x: 790, y: 1600, s: 1.0, glow: f, emo: f > 0.4 ? 'shock' : 'neutral', look: -0.6, noLegs: true, blush: f * 2, flip: true }), t);
    flames(790, 1600 - 290, f, t);
    if (f > 0.4) { for (let i = 0; i < 3; i++) { const ph = (t * 1.5 + i / 3) % 1; circ(790 + (i - 1) * 60, 1200 - ph * 260, 20 + ph * 30); ctx.fillStyle = `rgba(120,120,130,${0.4 * (1 - ph)})`; ctx.fill(); } }
  }
  ctx.restore();
  vignette(0.45);
};
S.SCHOOL = (t, a, b) => {
  const lt = t - a;
  const tJ = P('A Júlia') - 0.2, tP = P('O Pedro') - 0.1, tOlhar = P('olhar');
  const focus = t < tJ ? 0 : t < tP ? 1 : 2;
  const cx = [W / 2, 330, 760][focus], cy = [1150, 1180, 1180][focus], z = [1, 1.35, 1.35][focus];
  const k = ease(prog(t, focus === 1 ? tJ : tP, (focus === 1 ? tJ : tP) + 0.45));
  const prevC = focus === 2 ? [330, 1180, 1.35] : [W / 2, 1150, 1];
  ctx.save();
  camera(focus === 0 ? 1 + lt * 0.01 : lerp(prevC[2], z, k), focus === 0 ? W / 2 : lerp(prevC[0], cx, k), focus === 0 ? 1150 : lerp(prevC[1], cy, k));
  bgClass(t);
  drawPerson(Object.assign({}, HERO, { x: 560, y: 1150, s: 0.62, emo: 'sad', lookY: 0.6, noLegs: true }), t); desk(560, 1080, 0.7);
  drawPerson(Object.assign({}, JULIA, { x: 300, y: 1500, s: 0.95, glow: 0.75 + 0.25 * Math.sin(t * 5), emo: 'happy', noLegs: true, pose: t > tJ + 0.3 ? 'wave' : 'down', posePrev: 'down', armP: ease(prog(t, tJ + 0.3, tJ + 0.7)) }), t);
  desk(300, 1390, 1);
  const looks = t > tOlhar - 0.35;
  drawPerson(Object.assign(extra(5), { x: 1010, y: 1530, s: 0.9, flip: !looks, glow: 0.5, emo: 'smile', noLegs: true, look: looks ? -1 : 0 }), t);
  const flare = clamp((t - tOlhar + 0.15) * 2.5);
  drawPerson(Object.assign({}, PEDRO, { x: 760, y: 1500, s: 0.95, glow: 0.35 + flare * 0.9, blush: flare * 2, emo: flare > 0.3 ? 'grin' : 'smile', noLegs: true, look: flare > 0.3 ? 0.6 : 0 }), t);
  desk(760, 1390, 1);
  // crossed-out note at start
  const nk = 1 - prog(t, tJ - 0.3, tJ);
  if (nk > 0 && focus === 0) { ctx.save(); ctx.globalAlpha = nk; ctx.translate(W / 2, 760); ctx.rotate(-0.1); rr(-150, -90, 300, 180, 10); fillStroke('#fffbe6', 6); txt('bilhetinho', 0, -10, 46, INK, 'center', 'Nunito', 0, 900); ctx.strokeStyle = '#ff4d4d'; ctx.lineWidth = 14; ctx.beginPath(); ctx.moveTo(-140, -80); ctx.lineTo(140, 80); ctx.moveTo(140, -80); ctx.lineTo(-140, 80); ctx.stroke(); ctx.restore(); }
  ctx.restore();
  vignette(0.45);
};
S.CAIO = (t, a, b) => {
  const lt = t - a; const P1 = LN('P1'); const tMao = P('Todo dia eu');
  const pin = easeOut(prog(t, P1.start - 0.7, P1.start - 0.15));
  const pat = ease(prog(t, P1.speechEnd - 0.9, P1.speechEnd - 0.5));
  ctx.save();
  camera(1 + lt * 0.01, W / 2, H / 2);
  bgClass(t);
  ctx.fillStyle = 'rgba(40,20,50,.18)'; ctx.fillRect(0, 0, W, H);
  const hx = lerp(W / 2, 300, ease(prog(t, P1.start - 0.8, P1.start - 0.2)));
  const neck = t > tMao;
  drawPerson(Object.assign({}, HERO, { x: hx, y: 2080, s: 1.75, emo: neck ? 'sad' : 'neutral', pose: neck ? 'neck' : 'down', posePrev: 'down', armP: ease(prog(t, tMao, tMao + 0.4)), lookY: pin > 0.5 ? 0 : neck ? 0.5 : 0, look: pin > 0.5 ? 0.9 : 0, noLegs: true }), t);
  const pm = talking('pedro', t);
  if (pin > 0) drawPerson(Object.assign({}, PEDRO, { x: lerp(1500, 790, pin), y: 2080, s: 1.75, flip: true, glow: 0.55, emo: 'smile', mouth: pm || 'X', pose: 'pat', posePrev: 'down', armP: pat, noLegs: true, look: 0.4 }), t);
  ctx.restore();
  // name tag
  const nt = prog(t, a + 0.1, a + 0.4) * (1 - prog(t, P1.start - 1.2, P1.start - 0.8));
  if (nt > 0) { ctx.save(); ctx.globalAlpha = nt; ctx.translate(W / 2, 560); ctx.scale(easeBack(nt), easeBack(nt)); rr(-260, -90, 520, 180, 30); ctx.fillStyle = 'rgba(25,15,35,.85)'; ctx.fill(); txt('CAIO, 16', 0, -18, 84, '#fff', 'center', 'Baloo', 0); txt('o garoto da nuca fria', 0, 50, 44, '#8fd3ff', 'center', 'Baloo', 0); ctx.restore(); }
  vignette(0.6);
};
S.MONT = (t, a, b) => {
  const t2 = P('Me formei') - 0.1, t3 = P('Cresci') - 0.1;
  const part = t < t2 ? 0 : t < t3 ? 1 : 2; const ps = [a, t2, t3][part]; const lt = t - ps;
  ctx.save();
  camera(1.04 + lt * 0.03, W / 2, H / 2);
  if (part === 0) {
    ctx.fillStyle = vgrad(0, H, ['#7b5cd6', '#c58bf2']); ctx.fillRect(-200, -200, W + 400, H + 400);
    for (let i = 0; i < 30; i++) { ctx.fillStyle = SHIRTS[i % 7]; ctx.save(); ctx.translate(rand(i) * W, (rand(i + 3) * H + lt * 300) % H); ctx.rotate(t * 3 + i); ctx.fillRect(-10, -5, 20, 10); ctx.restore(); }
    drawPerson(Object.assign(extra(1), { x: 200, y: 1500, s: 0.8, glow: 0.9, emo: 'happy', hat: 'party' }), t);
    drawPerson(Object.assign(extra(2), { x: 880, y: 1500, s: 0.8, glow: 0.9, emo: 'happy', hat: 'party', flip: true }), t);
    drawPerson(Object.assign({}, HERO, { x: W / 2, y: 1560, s: 0.85, emo: 'neutral', hat: 'party', lookY: 0.4 }), t);
    rr(370, 1260, 340, 150, 30); fillStroke('#fff1f5', 6); rr(370, 1260, 340, 40, 20); fillStroke('#ff7aa8', 6);
    for (let i = 0; i < 3; i++) { rr(430 + i * 90, 1190, 18, 70, 6); fillStroke('#7b8cff', 4); ctx.save(); ctx.translate(439 + i * 90, 1175); ctx.scale(1, 1 + Math.sin(t * 20 + i) * 0.15); ctx.beginPath(); ctx.ellipse(0, 0, 12, 20, 0, 0, 7); ctx.fillStyle = '#ffb84d'; ctx.fill(); ctx.restore(); }
    txt('ANIVERSÁRIO', W / 2, 420, 100, '#fff');
  } else if (part === 1) {
    ctx.fillStyle = vgrad(0, H, ['#2c5f8a', '#5aa0c8']); ctx.fillRect(-200, -200, W + 400, H + 400);
    drawPerson(Object.assign(extra(3), { x: 190, y: 1520, s: 0.9, glow: 1, emo: 'happy', hat: 'grad', shirt: '#23232f' }), t);
    drawPerson(Object.assign(extra(4), { x: 890, y: 1520, s: 0.9, glow: 1, emo: 'happy', hat: 'grad', shirt: '#23232f', flip: true }), t);
    drawPerson(Object.assign({}, HERO, { x: W / 2, y: 1600, s: 1.0, emo: 'sad', hat: 'grad', shirt: '#23232f', hoodie: false, lookY: 0.5 }), t);
    txt('FORMATURA', W / 2, 420, 100, '#fff');
  } else {
    ctx.fillStyle = vgrad(0, H, ['#151a33', '#2c3360']); ctx.fillRect(-200, -200, W + 400, H + 400);
    rr(180, 360, 720, 760, 20); fillStroke('#3a4a7a', 14, '#0d1024');
    ctx.strokeStyle = 'rgba(180,200,255,.6)'; ctx.lineWidth = 3; for (let i = 0; i < 40; i++) { const x = 190 + rand(i) * 700, y = 370 + ((t * 700 + rand(i + 9) * 760) % 740); ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 6, y + 30); ctx.stroke(); }
    ctx.beginPath(); ctx.moveTo(540, 360); ctx.lineTo(540, 1120); ctx.moveTo(180, 740); ctx.lineTo(900, 740); fillStroke(null, 12, '#0d1024');
    drawPerson(Object.assign({}, HERO, { x: W / 2, y: 1900, s: 1.6, emo: 'sad', pose: 'neck', noLegs: true, lookY: 0.4, shirt: '#3d7f8c' }), t);
  }
  ctx.restore();
  const since = t - ps; const wk = since < 0.16 && part > 0 ? 1 - since / 0.16 : 0;
  if (wk > 0) { ctx.fillStyle = `rgba(255,255,255,${wk * 0.8})`; ctx.fillRect(0, 0, W, H); }
  if (part < 2) { ctx.save(); ctx.translate(W - 140, 260); circ(0, 0, 70); fillStroke('#fff', 8); ctx.rotate(t * 9); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, -52); fillStroke(null, 8); ctx.rotate(-t * 8.2); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(36, 0); fillStroke(null, 8); ctx.restore(); }
  if (part < 2) stamp(t, ps + 0.35, 'NADA.', '#8fd3ff');
  vignette(0.5);
};
S.VO = (t, a, b) => {
  const V1 = LN('V1');
  const walk = ease(prog(t, P('Toda tarde') - 0.2, P('enrolava')));
  const wrap = ease(prog(t, P('enrolava'), P('pescoço', 'e')));
  const zoom = ease(prog(t, V1.start - 0.3, V1.start + 0.3));
  ctx.save();
  camera(lerp(1.0, 1.7, zoom), lerp(W / 2, 560, zoom), lerp(H / 2, 1180, zoom));
  bgHome(t);
  rr(560, 1080, 380, 300, 60); fillStroke('#a63d40', 8); rr(520, 1180, 80, 220, 30); fillStroke('#8e3033', 8); rr(900, 1180, 80, 220, 30); fillStroke('#8e3033', 8);
  drawPerson(Object.assign({}, HERO, { x: 750, y: 1430, s: 0.95, emo: wrap > 0.6 ? 'smile' : 'neutral', look: -0.8, scarf: wrap }), t);
  const vm = talking('vo', t);
  drawPerson(Object.assign({}, VO, { x: lerp(180, 470, walk), y: 1460, s: 0.92, walk: walk > 0 && walk < 1, emo: 'smile', mouth: vm || 'X', pose: wrap > 0 && wrap < 1 ? 'wrap' : 'down', posePrev: 'down', armP: wrap > 0 && wrap < 1 ? 1 : 0, look: 0.8, blink: vm ? false : undefined }), t);
  rr(90, 1270, 150, 100, 40); fillStroke('#fff', 6); ctx.save(); for (let i = 0; i < 3; i++) { const ph = (t * 0.6 + i / 3) % 1; circ(160 + Math.sin(ph * 8) * 14, 1250 - ph * 160, 14 + ph * 16); ctx.fillStyle = `rgba(255,255,255,${0.5 * (1 - ph)})`; ctx.fill(); } ctx.restore();
  ctx.restore();
  if (t < V1.start - 0.2) { const k = prog(t, P('Cida') - 0.1, P('Cida') + 0.2); if (k > 0) { ctx.save(); ctx.globalAlpha = k * (1 - prog(t, P('Toda tarde') + 0.6, P('Toda tarde') + 0.9)); ctx.translate(W / 2, 520); ctx.scale(easeBack(k), easeBack(k)); rr(-220, -70, 440, 140, 30); ctx.fillStyle = 'rgba(25,15,35,.85)'; ctx.fill(); txt('VÓ CIDA', 0, 4, 80, '#d8b4ff', 'center', 'Baloo', 0); ctx.restore(); } }
  vignette(0.45);
};
S.SUMMER = (t, a, b) => {
  const tDorm = P('Nem pra dormir') - 0.1; const lt = t - a;
  ctx.save();
  if (t < tDorm) {
    camera(1.05 + lt * 0.03, W / 2, H / 2);
    ctx.fillStyle = vgrad(0, H, ['#ffd25a', '#ff9a3c', '#ff7a2c']); ctx.fillRect(-200, -200, W + 400, H + 400);
    ctx.save(); ctx.translate(800, 380); ctx.rotate(t * 0.6); for (let i = 0; i < 12; i++) { ctx.rotate(Math.PI / 6); rr(140, -12, 90, 24, 12); ctx.fillStyle = '#fff3a8'; ctx.fill(); } ctx.restore();
    circ(800, 380, 130); fillStroke('#fff3a8', 8);
    // heat waves
    ctx.strokeStyle = 'rgba(255,255,255,.35)'; ctx.lineWidth = 6; for (let r = 0; r < 4; r++) { ctx.beginPath(); for (let x = 0; x <= W; x += 20) ctx.lineTo(x, 1250 + r * 70 + Math.sin(x * 0.03 + t * 5 + r) * 10); ctx.stroke(); }
    ctx.fillStyle = '#e5b06a'; ctx.fillRect(-200, 1400, W + 400, 800);
    drawPerson(Object.assign({}, HERO, { x: W / 2, y: 1720, s: 1.15, emo: 'sad', scarf: 1, blush: 1.5 }), t);
    for (let i = 0; i < 4; i++) { const ph = (t * 1.2 + i / 4) % 1; const x = W / 2 + (i % 2 ? 1 : -1) * (80 + i * 10) * 1.15, y = 1720 - 470 * 1.15 + ph * 180; ctx.beginPath(); ctx.moveTo(x, y - 18); ctx.quadraticCurveTo(x + 14, y + 6, x, y + 10); ctx.quadraticCurveTo(x - 14, y + 6, x, y - 18); ctx.globalAlpha = 1 - ph; fillStroke('#9fd8ff', 4); ctx.globalAlpha = 1; }
    // thermometer
    const th = easeOut(prog(t, P('quarenta') - 0.2, P('quarenta') + 0.5));
    rr(120, 300, 70, 420, 35); fillStroke('#fff', 7); circ(155, 760, 62); fillStroke('#ff3b3b', 7); rr(140, 720 - 360 * th, 30, 360 * th + 20, 15); ctx.fillStyle = '#ff3b3b'; ctx.fill();
    if (th > 0.2) txt('40°', 330, 360, 120, '#fff', 'center', 'Baloo', 14);
  } else {
    camera(1.1 + (t - tDorm) * 0.03, W / 2, 1200);
    ctx.fillStyle = vgrad(0, H, ['#1c2448', '#2e3a6b']); ctx.fillRect(-200, -200, W + 400, H + 400);
    rr(640, 260, 300, 360, 14); fillStroke('#0f1530', 10, '#59628a'); circ(840, 360, 40); ctx.fillStyle = '#f4f1d0'; ctx.fill();
    rr(140, 1230, 820, 200, 40); fillStroke('#6b5aa8', 8); rr(150, 1150, 230, 120, 50); fillStroke('#fff', 7);
    ctx.save(); ctx.translate(430, 1215); ctx.rotate(-Math.PI / 2); drawPerson(Object.assign({}, HERO, { x: 0, y: 0, s: 0.62, emo: 'closed', noLegs: true, scarf: 1 }), t); ctx.restore();
    rr(470, 1170, 480, 130, 50); fillStroke('#8a7ad0', 8);
    for (let i = 0; i < 3; i++) { const ph = (t * 0.5 + i / 3) % 1; txt('z', 330 + ph * 80 + i * 20, 1000 - ph * 200, 50 + ph * 30, '#fff', 'center', 'Baloo', 8); }
  }
  ctx.restore();
  vignette(0.5);
};
S.HOSP = (t, a, b) => {
  const lt = t - a;
  ctx.save(); camera(1.02 + lt * 0.02, W / 2, H / 2);
  bgHospital(t);
  rr(300, 1240, 700, 150, 30); fillStroke('#ffffff', 8); rr(320, 1380, 36, 220, 10); fillStroke('#9aa', 5); rr(944, 1380, 36, 220, 10); fillStroke('#9aa', 5);
  rr(320, 1150, 190, 110, 40); fillStroke('#ffffff', 7);
  ctx.save(); ctx.translate(640, 1205); ctx.rotate(-Math.PI / 2); drawPerson(Object.assign({}, VO, { x: 0, y: 0, s: 0.55, emo: 'closed', noLegs: true }), t); ctx.restore();
  rr(450, 1170, 540, 120, 40); fillStroke('#cfe6ff', 8);
  drawPerson(Object.assign({}, HERO, { x: 870, y: 1900, s: 1.15, emo: 'sad', flip: true, look: 0.8, lookY: 0.3, noLegs: true, scarf: 1, pose: 'hold' }), t);
  ctx.restore();
  stamp(t, P('Aí veio') + 0.1, 'TERÇA-FEIRA', '#8fd3ff');
  vignette(0.6);
};
S.CLASS = (t, a, b) => {
  const k = t - a;
  ctx.save(); camera(1.25 + k * 0.03, 780, 900);
  bgClass(t, 1);
  ctx.fillStyle = 'rgba(40,50,80,.25)'; ctx.fillRect(-400, -400, W + 800, H + 800);
  drawPerson(Object.assign({}, HERO, { x: 640, y: 1500, s: 1.0, emo: 'neutral', look: 1, lookY: -0.4, noLegs: true, scarf: 1 }), t);
  desk(640, 1400, 1.05);
  ctx.restore();
  vignette(0.65);
};
S.COLD = (t, a, b) => {
  const lt = t - a; const tF = P('frio'), tUm = P('Um frio');
  const fr = ease(prog(t, a + 0.05, tF + 0.6));
  ctx.fillStyle = '#0d1428'; ctx.fillRect(0, 0, W, H);
  if (t < tUm) {
    ctx.save(); camera(1 + lt * 0.05, W / 2, H / 2);
    const sk = '#f2c7a0';
    rr(360, 1000, 360, 600, 80); fillStroke(sk, 10);
    ctx.beginPath(); ctx.ellipse(540, 760, 380, 420, 0, 0, Math.PI * 2); fillStroke('#3b2a20', 10);
    for (let i = 0; i < 14; i++) { ctx.beginPath(); ctx.moveTo(220 + i * 47, 1050); ctx.lineTo(240 + i * 47, 1120 + (i % 3) * 14); ctx.lineTo(262 + i * 47, 1050); ctx.fillStyle = '#3b2a20'; ctx.fill(); }
    rr(160, 1500, 760, 600, 140); fillStroke('#2fa3a0', 10);
    rr(250, 1460, 580, 120, 50); fillStroke('#d7263d', 10);
    drawGlow(540, 1280, 420, fr * 0.9, COLD, 0);
    ctx.save(); ctx.strokeStyle = `rgba(230,248,255,${fr})`; ctx.lineWidth = 6; ctx.lineCap = 'round';
    for (let i = 0; i < 16; i++) {
      const cx = 400 + rand(i) * 280, cy = 1150 + rand(i + 7) * 320, r = (24 + rand(i + 3) * 40) * clamp(fr * 1.6 - rand(i) * 0.6);
      if (r <= 2) continue;
      for (let k = 0; k < 6; k++) { const ang = k * Math.PI / 3 + i; ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + Math.cos(ang) * r, cy + Math.sin(ang) * r); ctx.stroke(); ctx.beginPath(); ctx.moveTo(cx + Math.cos(ang) * r * 0.55, cy + Math.sin(ang) * r * 0.55); ctx.lineTo(cx + Math.cos(ang + 0.5) * r * 0.8, cy + Math.sin(ang + 0.5) * r * 0.8); ctx.stroke(); }
    }
    ctx.restore(); ctx.restore();
  } else {
    const k = t - tUm;
    ctx.save(); camera(2.4 + k * 0.08, W / 2, 1260 + k * 30);
    ctx.fillStyle = '#1a2440'; ctx.fillRect(-400, -400, W + 800, H + 800);
    drawPerson(Object.assign({}, HERO, { x: W / 2, y: 1640, s: 1, emo: 'shock', noLegs: true, scarf: 1, glow: 0.7, glowCol: COLD }), t);
    // frost line running down the spine
    ctx.strokeStyle = 'rgba(200,240,255,.9)'; ctx.lineWidth = 10; ctx.beginPath(); ctx.moveTo(W / 2, 1640 - 280); ctx.lineTo(W / 2 + Math.sin(k * 20) * 6, 1640 - 280 + 260 * clamp(k / 1.2)); ctx.stroke();
    for (let i = 0; i < 3; i++) { const ph = (k * 0.8 + i / 3) % 1; circ(560 + ph * 60, 1340 - ph * 50, 12 + ph * 24); ctx.fillStyle = `rgba(220,240,255,${0.5 * (1 - ph)})`; ctx.fill(); }
    ctx.restore();
  }
  vignette(0.7);
};
function corridor(t, scroll) {
  ctx.fillStyle = vgrad(0, H, ['#cfe9e4', '#a9d0ca']); ctx.fillRect(-400, -400, W + 800, H + 800);
  ctx.fillStyle = '#e8efe9'; ctx.fillRect(-400, 1300, W + 800, 1000);
  for (let i = -2; i < 8; i++) {
    const x = i * 420 - (scroll % 420);
    rr(x, 700, 220, 600, 10); fillStroke('#7fa8c9', 8); circ(x + 190, 1010, 12); fillStroke('#ffd84d', 4);
    rr(x + 40, 760, 140, 120, 8); fillStroke('#dff3ff', 6);
    ctx.fillStyle = 'rgba(255,255,255,.6)'; ctx.fillRect(x + 260, 260, 120, 40);
  }
  ctx.strokeStyle = 'rgba(0,0,0,.08)'; ctx.lineWidth = 4; for (let i = -2; i < 14; i++) { const x = i * 140 - (scroll * 1.3) % 140; ctx.beginPath(); ctx.moveTo(x, 1300); ctx.lineTo(x - 120, 1920); ctx.stroke(); }
}
S.RUN = (t, a, b) => {
  const tCheg = P('Quando eu cheguei') - 0.1; const lt = t - a;
  ctx.save();
  if (t < tCheg) {
    camera(1.05, W / 2, H / 2);
    corridor(t, lt * 900);
    for (let i = 0; i < 6; i++) { ctx.strokeStyle = 'rgba(255,255,255,.7)'; ctx.lineWidth = 6; const y = 900 + i * 120; ctx.beginPath(); ctx.moveTo(80 + ((lt * 1500 + i * 200) % 400), y); ctx.lineTo(220 + ((lt * 1500 + i * 200) % 400), y); ctx.stroke(); }
    ctx.save(); ctx.translate(560, 1720); ctx.rotate(0.12); drawPerson(Object.assign({}, HERO, { x: 0, y: 0, s: 1.05, emo: 'cry', scarf: 1, walk: true, phase: t * 1.8, tear: t * 1.4 }), t * 1.9); ctx.restore();
  } else {
    const k = t - tCheg;
    camera(1.1 + k * 0.04, W / 2, H / 2);
    corridor(t, 0);
    // door closing at center
    const close = ease(prog(t, tCheg + 0.3, P('dela', 'e') + 0.1));
    rr(330, 600, 420, 760, 12); ctx.fillStyle = '#26303a'; ctx.fill();
    rr(330 + 420 * close * 0, 600, 420 * close + 1, 760, 10); fillStroke('#7fa8c9', 8);
    if (close < 0.9) { ctx.save(); ctx.beginPath(); ctx.rect(330 + 420 * close, 600, 420 * (1 - close), 760); ctx.clip(); drawPerson(Object.assign(extra(6), { x: 620, y: 1360, s: 1.05, shirt: '#e8f4ff', hair: 'long', hairColor: '#2b1c14', emo: 'sad', look: -0.5 }), t); ctx.restore(); }
    ctx.fillStyle = 'rgba(255,255,255,.7)'; ctx.fillRect(470, 520, 140, 50); txt('QUARTO 12', 540, 548, 30, INK, 'center', 'Nunito', 0, 900);
    drawPerson(Object.assign({}, HERO, { x: 540, y: 1960, s: 1.25, emo: 'shock', scarf: 1, noLegs: true, lookY: -0.3 }), t);
  }
  ctx.restore();
  vignette(0.6);
};
S.REVEAL = (t, a, b) => {
  const lt = t - a; const tPorque = P('porque');
  const rev = ease(prog(t, tPorque, tPorque + 0.8));
  ctx.save(); camera(1.9 + lt * 0.03, W / 2, 1250);
  ctx.fillStyle = vgrad(0, H, ['#1a2440', rev > 0.5 ? '#6b3b2a' : '#2b2440']); ctx.fillRect(-400, -400, W + 800, H + 800);
  for (let i = 0; i < 26; i++) { const ang = i * 0.7 + t * (0.6 + rand(i) * 0.5), r = 300 + rand(i + 2) * 260; circ(W / 2 + Math.cos(ang) * r, 1250 + Math.sin(ang) * r * 0.7, 6 + rand(i) * 10); ctx.fillStyle = rgba(GLOW, 0.25 + 0.6 * rev); ctx.fill(); }
  drawPerson(Object.assign({}, HERO, { x: W / 2, y: 1640, s: 1, emo: rev > 0.3 ? 'cry' : 'sad', noLegs: true, scarf: 1, pose: 'neck', tear: rev > 0.3 ? t * 0.7 : 0, glow: rev * 0.5 }), t);
  ctx.restore();
  vignette(0.65);
};
S.BABY = (t, a, b) => {
  const tAlg = P('alguém pensava') - 0.1, tTodo = P('todo santo') - 0.1;
  const sepia = fn => { ctx.save(); ctx.filter = 'sepia(0.85) saturate(0.9) brightness(1.02)'; fn(); ctx.restore(); };
  ctx.save();
  if (t < tAlg) {
    const lt = t - a; camera(1.1 + lt * 0.05, W / 2, 1100);
    sepia(() => { bgHome(t); drawPerson(Object.assign({}, VO, { x: 540, y: 1600, s: 1.1, emo: 'happy', pose: 'hold', hairColor: '#8a8a8a' }), t); });
    drawGlow(540, 1320, 160, 1, GLOW, t);
    sepia(() => { ctx.beginPath(); ctx.ellipse(540, 1380, 120, 70, 0, 0, 7); fillStroke('#fff4e0', 6); circ(540, 1335, 48); fillStroke('#f2c7a0', 6); ctx.beginPath(); ctx.moveTo(522, 1330); ctx.lineTo(530, 1330); ctx.moveTo(550, 1330); ctx.lineTo(558, 1330); ctx.moveTo(530, 1352); ctx.quadraticCurveTo(540, 1360, 550, 1352); fillStroke(null, 5); });
    txt('DIA 1', W / 2, 360, 110, '#ffd84d');
  } else if (t < tTodo) {
    const lt = t - tAlg; camera(1.05 + lt * 0.05, W / 2, H / 2);
    sepia(() => { bgStreet(t, 1, lt * 40); rr(60, 900, 40, 500, 8); fillStroke('#6b5a4a', 6); rr(980, 900, 40, 500, 8); fillStroke('#6b5a4a', 6); rr(60, 880, 960, 60, 10); fillStroke('#8a6b4a', 6); txt('ESCOLA', W / 2, 912, 50, '#fff', 'center', 'Baloo', 8); });
    sepia(() => drawPerson(Object.assign({}, VO, { x: 260, y: 1640, s: 0.95, emo: 'happy', pose: 'wave' }), t));
    sepia(() => drawPerson(Object.assign({}, HERO, { x: 760, y: 1640, s: 0.75, emo: 'happy', walk: true, flip: true, scarf: 1, look: -0.6 }), t));
    drawGlow(760, 1640 - 278 * 0.75, 120, 1, GLOW, t);
  } else {
    const lt = t - tTodo; camera(1.2 + lt * 0.06, W / 2, 1150);
    sepia(() => { bgHome(t); drawPerson(Object.assign({}, VO, { x: 540, y: 1700, s: 1.2, emo: 'happy', pose: 'hold' }), t); rr(440, 1380, 200, 150, 10); fillStroke('#fff1d6', 8, '#6e3f25'); circ(540, 1450, 40); fillStroke('#f2c7a0', 4); });
    drawGlow(540, 1455, 120 + lt * 260, 1, GLOW, t);
  }
  ctx.restore();
  vignette(0.55);
};
S.SCARF = (t, a, b) => {
  const lt = t - a; const tCach = P('era o cachecol') - 0.1;
  const sepia = fn => { ctx.save(); ctx.filter = 'sepia(0.85) saturate(0.9) brightness(1.02)'; fn(); ctx.restore(); };
  ctx.save(); camera(1.5 + lt * 0.05, W / 2, 1150);
  sepia(() => { bgHome(t); });
  // grandma wrapping scarf (memory) - the warmth glows from under the scarf
  const lift = ease(prog(t, tCach, tCach + 0.6));
  drawGlow(640, 1430 - 278 * 0.95, 200 + 40 * Math.sin(t * 4), 0.6 + 0.4 * lift, GLOW, t);
  sepia(() => drawPerson(Object.assign({}, VO, { x: 380, y: 1460, s: 0.92, emo: 'happy', pose: 'wrap', look: 0.8 }), t));
  sepia(() => drawPerson(Object.assign({}, HERO, { x: 640, y: 1430, s: 0.95, emo: 'happy', look: -0.8, scarf: 1, kid: true }), t));
  // the scarf itself in color (only colored element)
  ctx.save(); ctx.translate(640, 1430); ctx.scale(0.95, 0.95); drawScarf(1, t); ctx.restore();
  ctx.restore();
  if (t > tCach) { ctx.fillStyle = rgba([255, 190, 110], 0.25 * lift); ctx.fillRect(0, 0, W, H); }
  vignette(0.55);
};
S.END = (t, a, b) => {
  const lt = t - a; const last = D.lines[D.lines.length - 1];
  const tEsq = P('ele esquenta') + 0.25;
  const handK = ease(prog(t, P('cachecol dela') - 0.2, P('cachecol dela') + 0.4));
  const g = ease(prog(t, tEsq, tEsq + 0.6));
  const out = ease(prog(t, last.speechEnd + 0.3, b - 0.3));
  ctx.save();
  camera(lerp(1.6, 1.0, out), W / 2, lerp(1120, H / 2, out));
  bgStreet(t, 1, lt * 40);
  for (let i = 0; i < 26; i++) { ctx.save(); ctx.translate((rand(i) * W + lt * 60 * (0.5 + rand(i + 1))) % W, (rand(i + 4) * H + lt * 140) % H); ctx.rotate(t * 2 + i); ctx.beginPath(); ctx.ellipse(0, 0, 14, 7, 0, 0, 7); ctx.fillStyle = ['#e8743b', '#d9a32b', '#c4452c'][i % 3]; ctx.fill(); ctx.restore(); }
  for (let i = 0; i < 6; i++) { const x = ((i * 230 + lt * (i % 2 ? 80 : -70)) % 1500 + 1500) % 1500 - 200; drawPerson(Object.assign(extra(i + 3), { x, y: 1360, s: 0.6, walk: true, flip: i % 2 === 0, glow: 0.8 }), t); }
  drawPerson(Object.assign({}, HERO, { x: W / 2, y: 1700, s: 1.15, hoodie: false, shirt: '#4a5a8a', hair: 'man', scarf: 1, emo: g > 0.3 ? 'smile' : 'neutral', pose: 'neck', posePrev: 'down', armP: handK, glow: g * 0.75, lookY: g > 0.3 ? 0 : 0.3 }), t);
  ctx.restore();
  vignette(0.45);
  const ca = prog(t, last.speechEnd + 0.5, last.speechEnd + 0.9);
  if (ca > 0) { ctx.save(); ctx.globalAlpha = ca; const p = easeBack(ca); ctx.translate(W / 2, 360); ctx.scale(p, p); rr(-450, -110, 900, 220, 40); ctx.fillStyle = 'rgba(25,15,35,.8)'; ctx.fill(); txt('QUEM JÁ FEZ SUA', 0, -40, 72, '#fff', 'center', 'Baloo', 0); txt('NUCA ESQUENTAR? 👇', 0, 46, 80, '#ffa53a', 'center', 'Baloo', 0); ctx.restore(); }
};
const HARD_CUT = new Set(['COLD', 'CLASS']);
