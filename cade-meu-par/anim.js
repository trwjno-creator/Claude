// "Cadê Meu Par?" — animação 2D procedural (9:16, 40 s, loop perfeito)
// draw(t) é determinístico: o mesmo t sempre gera o mesmo quadro.
'use strict';
const W = 540, H = 960, DUR = 40;
const cv = document.getElementById('c');
let ctx = cv.getContext('2d');
const OFF = document.createElement('canvas'); OFF.width = cv.width; OFF.height = cv.height;
const OFFCTX = OFF.getContext('2d');
// desenha uma cena num canvas separado e compõe com transparência
function layer(alpha, fn) {
  const main = ctx; ctx = OFFCTX;
  ctx.setTransform(SC, 0, 0, SC, 0, 0); ctx.globalAlpha = 1; ctx.clearRect(0, 0, W, H);
  fn(); ctx = main;
  ctx.save(); ctx.globalAlpha = alpha; ctx.drawImage(OFF, 0, 0, W, H); ctx.restore();
}
const SC = cv.width / W;
const FONT = '"Inter","Liberation Sans",sans-serif';
const OUT = '#2a1b2e';
const PI = Math.PI, TAU = PI * 2;

// ---------- utilidades ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const inv = (a, b, x) => clamp((x - a) / (b - a));
const easeIO = t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
const easeOut = t => 1 - Math.pow(1 - t, 3);
const easeIn = t => t * t * t;
const easeBack = t => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
const spring = (tt, f = 22, d = 7) => tt < 0 ? 0 : Math.exp(-tt * d) * Math.cos(tt * f);
function hash(n) { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function circle(x, y, r) { ctx.beginPath(); ctx.arc(x, y, Math.max(r, 0.01), 0, TAU); }
function ell(x, y, rx, ry, rot = 0) { ctx.beginPath(); ctx.ellipse(x, y, Math.max(rx, .01), Math.max(ry, .01), rot, 0, TAU); }
function fs(f, s = OUT, lw = 3) {
  if (f) { ctx.fillStyle = f; ctx.fill(); }
  if (s) { ctx.strokeStyle = s; ctx.lineWidth = lw; ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.stroke(); }
}
function heartPath(x, y, r) {
  ctx.beginPath(); ctx.moveTo(x, y + r * .9);
  ctx.bezierCurveTo(x - r * 1.6, y - r * .2, x - r * .6, y - r * 1.4, x, y - r * .45);
  ctx.bezierCurveTo(x + r * .6, y - r * 1.4, x + r * 1.6, y - r * .2, x, y + r * .9);
  ctx.closePath();
}
function star(x, y, r, a = 0) {
  ctx.beginPath();
  for (let i = 0; i < 8; i++) {
    const rad = i % 2 ? r * .28 : r, an = a + i * PI / 4;
    ctx[i ? 'lineTo' : 'moveTo'](x + Math.cos(an) * rad, y + Math.sin(an) * rad);
  }
  ctx.closePath();
}
function popScale(dt) { return dt < 0 ? 0 : easeBack(clamp(dt / .28)); }

// Texto estilo legenda de rede social (branco com contorno preto)
function caption(txt, x, y, size, o = {}) {
  const sc = o.scale !== undefined ? o.scale : 1;
  if (sc <= 0.001 || o.alpha === 0) return;
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot || 0); ctx.scale(sc, sc);
  ctx.globalAlpha = o.alpha === undefined ? 1 : o.alpha;
  ctx.font = `${o.weight || 900} ${size}px ${o.font || FONT}`;
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  const lines = String(txt).split('\n'), lh = size * 1.12;
  lines.forEach((l, i) => {
    const yy = (i - (lines.length - 1) / 2) * lh;
    if (o.shadow !== false) { ctx.fillStyle = 'rgba(0,0,0,.35)'; ctx.fillText(l, 3, yy + 5); }
    ctx.lineWidth = o.lw || size * .2; ctx.strokeStyle = o.stroke || '#111';
    ctx.strokeText(l, 0, yy);
    ctx.fillStyle = o.fill || '#fff'; ctx.fillText(l, 0, yy);
  });
  ctx.restore();
}
function sfxText(txt, x, y, size, dt, rot = -.12, fill = '#ffd60a') {
  if (dt < 0 || dt > 1.1) return;
  caption(txt, x, y, size, { scale: popScale(dt) * (1 + dt * .08), rot, fill, stroke: OUT, alpha: clamp((1.1 - dt) / .25) });
}

// ---------- personagem: meia ----------
const SKINS = {
  hero: { base: '#fbf6ee', stripe: '#e63946', cuff: '#e63946', pat: 'stripes' },
  dots: { base: '#3a86ff', stripe: '#ffffff', cuff: '#1d4fbf', pat: 'dots' },
};
function sockPath() {
  ctx.beginPath();
  ctx.moveTo(-25, -60); ctx.lineTo(25, -60); ctx.lineTo(25, 12);
  ctx.quadraticCurveTo(25, 20, 34, 20); ctx.lineTo(52, 20);
  ctx.quadraticCurveTo(76, 20, 76, 40); ctx.quadraticCurveTo(76, 60, 52, 60);
  ctx.lineTo(-4, 60); ctx.quadraticCurveTo(-25, 60, -25, 38); ctx.closePath();
}
// origem = centro da perna; base em y=+60*s; rosto em y=-28*s
function drawSock(x, y, s, o = {}) {
  const st = Object.assign({}, SKINS.hero, o.skin ? SKINS[o.skin] : {}, o.look || {});
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot || 0);
  ctx.scale(s * (o.sx || 1) * (o.flip ? -1 : 1), s * (o.sy || 1));
  sockPath(); ctx.save(); ctx.clip();
  ctx.fillStyle = st.base; ctx.fillRect(-30, -65, 112, 130);
  ctx.fillStyle = st.stripe;
  if (st.pat === 'stripes') { for (let yy = -40; yy < 62; yy += 22) ctx.fillRect(-30, yy, 112, 10); }
  else if (st.pat === 'dots') {
    for (let yy = -40, r = 0; yy < 64; yy += 15, r++) for (let xx = -22 + (r % 2) * 8; xx < 80; xx += 16) { circle(xx, yy, 3.6); ctx.fill(); }
  }
  ctx.fillStyle = st.cuff; ctx.fillRect(-30, -62, 60, 15);
  circle(70, 44, 19); ctx.fill(); circle(-22, 56, 15); ctx.fill();
  ctx.strokeStyle = 'rgba(0,0,0,.18)'; ctx.lineWidth = 1.5;
  for (let xx = -21; xx < 25; xx += 6) { ctx.beginPath(); ctx.moveTo(xx, -60); ctx.lineTo(xx, -48); ctx.stroke(); }
  ctx.fillStyle = 'rgba(255,255,255,.28)'; ctx.fillRect(-19, -46, 6, 92);
  ctx.fillStyle = 'rgba(40,0,40,.10)'; ctx.fillRect(14, -62, 14, 82); ctx.fillRect(-30, 48, 112, 20);
  ctx.restore();
  sockPath(); fs(null, OUT, 4 / Math.pow(Math.max(s, .3), .35));
  drawFace(o, st);
  ctx.restore();
}
function drawFace(o, st) {
  const e = o.eyes || {}, es = e.size || 1, lk = e.look || [0, 0], bl = clamp(e.blink || 0);
  const ey = -27, exs = [-11, 13];
  if (o.blush) { ctx.fillStyle = 'rgba(255,90,120,.45)'; ell(-15, -13, 7, 4); ctx.fill(); ell(17, -13, 7, 4); ctx.fill(); }
  exs.forEach((ex, i) => {
    if (e.mode === 'heart') {
      const r = 9.5 * es * (1 + .12 * Math.sin((e.t || 0) * 14));
      heartPath(ex, ey + 1, r); fs('#ff2e63', OUT, 2.2);
      ctx.fillStyle = 'rgba(255,255,255,.7)'; circle(ex - r * .45, ey - r * .25, r * .2); ctx.fill();
    } else if (e.mode === 'closed') {
      ctx.beginPath(); ctx.arc(ex, ey + 4, 7 * es, PI * 1.1, PI * 1.9); fs(null, OUT, 3);
    } else {
      ell(ex, ey, 8.5 * es, 10.5 * es * (1 - bl * .95)); fs('#fff', OUT, 2.4);
      if (bl < .8) {
        const pr = (e.pupil || 4.3) * Math.min(es, 1.3);
        ctx.save(); ell(ex, ey, 8.5 * es, 10.5 * es * (1 - bl * .95)); ctx.clip();
        circle(ex + lk[0] * 3.6 * es, ey + lk[1] * 4.2 * es, pr); ctx.fillStyle = OUT; ctx.fill();
        ctx.fillStyle = '#fff'; circle(ex + lk[0] * 3.6 * es + pr * .35, ey + lk[1] * 4.2 * es - pr * .4, Math.max(pr * .32, .9)); ctx.fill();
        if (e.lid) { ctx.fillStyle = st.base; ctx.fillRect(ex - 10 * es, ey - 12 * es, 20 * es, 12 * es * e.lid); }
        ctx.restore();
        if (e.lid) { ctx.beginPath(); ctx.moveTo(ex - 8.5 * es, ey - 10.5 * es + 12 * es * e.lid); ctx.lineTo(ex + 8.5 * es, ey - 10.5 * es + 12 * es * e.lid); fs(null, OUT, 2.4); }
      }
    }
    if (o.brow) {
      const d = i === 0 ? 1 : -1, by = ey - 11 * es - 3;
      let yin = by, yout = by;
      if (o.brow === 'angry') { yin = by + 4; yout = by - 4; }
      if (o.brow === 'sad') { yin = by - 5; yout = by + 2; }
      if (o.brow === 'up') { yin = by - 6; yout = by - 6; }
      ctx.beginPath(); ctx.moveTo(ex + 8 * d, yin); ctx.lineTo(ex - 8 * d, yout); fs(null, OUT, 3.2);
    }
  });
  const m = o.mouth;
  if (m === 'scream') { ell(1, -3, 6.5, 9); fs('#5a0f1a', OUT, 2.4); ell(1, 2, 4, 3); ctx.fillStyle = '#ff6b81'; ctx.fill(); }
  else if (m === 'o') { ell(1, -7, 3.5, 4.5); fs('#5a0f1a', OUT, 2); }
  else if (m === 'smile') { ctx.beginPath(); ctx.arc(1, -11, 6.5, .2 * PI, .8 * PI); fs(null, OUT, 2.6); }
  else if (m === 'grin') { ctx.beginPath(); ctx.arc(1, -10, 7, 0, PI); ctx.closePath(); fs('#5a0f1a', OUT, 2.4); }
  else if (m === 'frown') { ctx.beginPath(); ctx.arc(1, -1, 6, 1.2 * PI, 1.8 * PI); fs(null, OUT, 2.6); }
  else if (m === 'teeth') { rr(-7, -12, 16, 8, 3); fs('#fff', OUT, 2.2); ctx.beginPath(); ctx.moveTo(-7, -8); ctx.lineTo(9, -8); fs(null, OUT, 1.5); }
  else if (m === 'wobble') {
    ctx.beginPath();
    for (let k = 0; k <= 12; k++) { const xx = -7 + k * 16 / 12; ctx[k ? 'lineTo' : 'moveTo'](xx, -7 + Math.sin(k * 1.6 + (o.t || 0) * 30) * 1.8); }
    fs(null, OUT, 2.4);
  }
  if (o.tear) {
    ctx.fillStyle = 'rgba(90,180,255,.85)';
    exs.forEach(ex => { rr(ex - 2.5, ey + 7, 5, 46 * o.tear, 2.5); ctx.fill(); });
    for (let k = 0; k < 3; k++) {
      const ph = ((o.t || 0) * 2 + k / 3) % 1;
      exs.forEach((ex, i) => { circle(ex + (i ? 1 : -1) * (10 + ph * 26), ey + 6 + ph * ph * 50, 2.6); ctx.fill(); });
    }
  }
  if (o.sweat) {
    const sp = o.sweat; ctx.save(); ctx.translate(29, -50 + sp * 6); ctx.globalAlpha = clamp(sp * 3);
    ctx.beginPath(); ctx.moveTo(0, -9); ctx.quadraticCurveTo(7, 2, 0, 5); ctx.quadraticCurveTo(-7, 2, 0, -9);
    fs('#8fd3ff', OUT, 1.8); ctx.restore();
  }
}

// ---------- mão gigante ----------
// dedos apontam para -x, braço sai para +x. pinch: ponto de pinça em (-70,-14)
function drawHand(x, y, s, rot, pose) {
  const skin = '#f2c29b', lw = 3.5;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  rr(110, -62, 700, 124, 18); fs('#4361ee', OUT, lw);
  rr(98, -68, 34, 136, 12); fs('#3a0ca3', OUT, lw);
  if (pose === 'open') {
    [[-41, 72], [-18, 86], [5, 80], [28, 64]].forEach(([fy, len]) => { rr(-len + 8, fy, len + 20, 22, 11); fs(skin, OUT, lw); });
    rr(-12, -50, 126, 100, 40); fs(skin, OUT, lw);
    ctx.save(); ctx.translate(46, -40); ctx.rotate(-.9); rr(-13, -56, 27, 66, 13); fs(skin, OUT, lw); ctx.restore();
  } else if (pose === 'pinch') {
    [-8, 14, 34].forEach(fy => { rr(-26, fy - 4, 44, 22, 11); fs(skin, OUT, lw); });
    rr(-12, -50, 126, 100, 40); fs(skin, OUT, lw);
    rr(-78, -40, 100, 23, 11.5); fs(skin, OUT, lw);
    ctx.save(); ctx.translate(18, 6); ctx.rotate(.08); rr(-92, -20, 104, 23, 11.5); fs(skin, OUT, lw); ctx.restore();
    ctx.fillStyle = '#ffd9be'; ell(-66, -33, 7, 4); ctx.fill();
  } else { // fist
    [-44, -21, 2, 25].forEach(fy => { rr(-34, fy, 50, 22, 11); fs(skin, OUT, lw); });
    rr(-12, -50, 126, 100, 40); fs(skin, OUT, lw);
    ctx.save(); ctx.translate(20, -26); ctx.rotate(.15); rr(-52, -12, 74, 24, 12); fs(skin, OUT, lw); ctx.restore();
  }
  ctx.restore();
}

// ---------- cenários ----------
function laundryBg() {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#ffe8d4'); g.addColorStop(1, '#ffcfae');
  ctx.fillStyle = g; ctx.fillRect(-600, -600, W + 1200, H + 1200);
  ctx.fillStyle = 'rgba(255,255,255,.28)';
  for (let x = -600; x < W + 600; x += 64) ctx.fillRect(x, -600, 26, 1385);
  // janela + luz
  rr(36, 96, 150, 190, 10); fs('#bde0fe', OUT, 4);
  ctx.beginPath(); ctx.moveTo(111, 96); ctx.lineTo(111, 286); ctx.moveTo(36, 191); ctx.lineTo(186, 191); fs(null, OUT, 4);
  ctx.fillStyle = 'rgba(255,255,255,.55)'; ctx.beginPath(); ctx.moveTo(50, 110); ctx.lineTo(80, 110); ctx.lineTo(50, 160); ctx.fill();
  const lg = ctx.createLinearGradient(110, 190, 360, 780); lg.addColorStop(0, 'rgba(255,250,210,.38)'); lg.addColorStop(1, 'rgba(255,250,210,0)');
  ctx.fillStyle = lg; ctx.beginPath(); ctx.moveTo(36, 286); ctx.lineTo(186, 286); ctx.lineTo(520, 785); ctx.lineTo(240, 785); ctx.fill();
  // prateleira
  rr(330, 196, 190, 12, 3); fs('#b5835a', OUT, 3);
  rr(345, 120, 44, 76, 12); fs('#ff70a6', OUT, 3); rr(357, 104, 20, 18, 4); fs('#fff', OUT, 3); rr(352, 145, 30, 26, 4); fs('#fff', null);
  rr(400, 136, 40, 60, 9); fs('#70d6ff', OUT, 3); rr(410, 124, 18, 14, 3); fs('#ffd670', OUT, 3);
  rr(452, 150, 52, 46, 8); fs('#ffd670', OUT, 3); ctx.fillStyle = OUT; ctx.font = `900 13px ${FONT}`; ctx.textAlign = 'center'; ctx.fillText('SABÃO', 478, 178);
  // chão
  ctx.fillStyle = '#d6a77a'; ctx.fillRect(-600, 785, W + 1200, 800);
  ctx.strokeStyle = 'rgba(80,40,10,.18)'; ctx.lineWidth = 2;
  for (let x = -600; x < W + 600; x += 70) { ctx.beginPath(); ctx.moveTo(x, 785); ctx.lineTo(x - 40, 1600); ctx.stroke(); }
  for (let y = 840; y < 1600; y += 80) { ctx.beginPath(); ctx.moveTo(-600, y); ctx.lineTo(W + 600, y); ctx.stroke(); }
  ctx.fillStyle = '#fff6ec'; ctx.fillRect(-600, 772, W + 1200, 14);
  ctx.beginPath(); ctx.moveTo(-600, 786); ctx.lineTo(W + 600, 786); fs(null, OUT, 3);
}

const CLOTH = ['#ffb703', '#219ebc', '#8ecae6', '#fb8500', '#90be6d', '#e5989b'];
function clothBlob(x, y, r, a, c) { ell(x, y, r, r * .62, a); fs(c, OUT, 2.5); ctx.beginPath(); ctx.ellipse(x, y, r * .6, r * .3, a, .3, 2.2); fs(null, 'rgba(0,0,0,.2)', 2); }

// máquina de lavar: centro (0,0), porta em (0,40)
function drawMachine(st) {
  const dc = 40;
  ell(0, 252, 215, 16); ctx.fillStyle = 'rgba(0,0,0,.16)'; ctx.fill();
  rr(-175, 226, 42, 22, 5); fs('#59606b', OUT, 3); rr(133, 226, 42, 22, 5); fs('#59606b', OUT, 3);
  rr(-200, -235, 400, 470, 28); fs('#f7f4ef', OUT, 4);
  ctx.save(); rr(-200, -235, 400, 470, 28); ctx.clip();
  ctx.fillStyle = 'rgba(0,0,0,.06)'; ctx.fillRect(150, -240, 60, 480);
  ctx.fillStyle = 'rgba(255,255,255,.6)'; ctx.fillRect(-188, -140, 12, 360);
  ctx.fillStyle = '#e6dfd4'; ctx.fillRect(-200, -235, 400, 88);
  ctx.restore();
  ctx.beginPath(); ctx.moveTo(-200, -147); ctx.lineTo(200, -147); fs(null, OUT, 3);
  rr(-200, -235, 400, 470, 28); fs(null, OUT, 4);
  circle(-135, -191, 27); fs('#d5dae1', OUT, 3);
  const da = st.dial || -1;
  ctx.beginPath(); ctx.moveTo(-135, -191); ctx.lineTo(-135 + Math.cos(da) * 20, -191 + Math.sin(da) * 20); fs(null, OUT, 4);
  rr(-45, -212, 120, 42, 8); fs('#16212b', OUT, 3);
  ctx.fillStyle = '#6dffb0'; ctx.font = '800 24px "JetBrains Mono",monospace'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  if (st.display) ctx.fillText(st.display, 15, -190);
  circle(115, -191, 11); fs(st.led ? '#ff3b3b' : '#ff9b9b', OUT, 2.5);
  circle(150, -191, 11); fs('#ffd166', OUT, 2.5);
  circle(0, dc, 156); fs('#dfe2e7', OUT, 3.5);
  circle(0, dc, 132); fs('#1d2128', null);
  ctx.save(); circle(0, dc, 127); ctx.clip();
  ctx.fillStyle = '#4a5260'; ctx.fillRect(-140, dc - 140, 280, 280);
  ctx.fillStyle = '#353b46';
  for (let r = 30; r <= 120; r += 30) { const n = Math.round(r / 6); for (let k = 0; k < n; k++) { const a = (st.drum || 0) + k * TAU / n; circle(Math.cos(a) * r, dc + Math.sin(a) * r, 4); ctx.fill(); } }
  if (st.contents) st.contents();
  if (st.water) {
    ctx.beginPath(); ctx.moveTo(-140, 200);
    for (let x = -140; x <= 140; x += 8) ctx.lineTo(x, dc + 60 - st.water * 10 + Math.sin(x * .05 + (st.t || 0) * 9) * 9 * st.water + x * .15 * Math.sin((st.t || 0) * 4));
    ctx.lineTo(140, 200); ctx.closePath(); ctx.fillStyle = `rgba(80,170,230,${.5 * clamp(st.water)})`; ctx.fill();
  }
  ctx.restore();
  circle(0, dc, 129); fs(null, '#2b3038', 10);
  const op = st.open || 0;
  if (op < .01) drawDoor(0, dc, false);
  else {
    const th = op * PI * .82, k = Math.cos(th);
    ctx.save(); ctx.translate(-152, dc); ctx.scale(k, 1); drawDoor(152, 0, k < 0); ctx.restore();
  }
}
function drawDoor(x, y, back) {
  const g = ctx.createLinearGradient(x - 150, y - 150, x + 150, y + 150);
  g.addColorStop(0, '#ffffff'); g.addColorStop(.5, '#c4cad3'); g.addColorStop(1, '#8d96a2');
  ctx.beginPath(); ctx.arc(x, y, 150, 0, TAU); ctx.arc(x, y, 118, 0, TAU, true); ctx.fillStyle = g; ctx.fill('evenodd');
  circle(x, y, 150); fs(null, OUT, 3.5);
  circle(x, y, 118);
  if (back) fs('#a4acb7', OUT, 3);
  else {
    fs('rgba(150,205,245,.25)', OUT, 3);
    ctx.save(); circle(x, y, 118); ctx.clip();
    ctx.strokeStyle = 'rgba(255,255,255,.55)'; ctx.lineWidth = 16; ctx.beginPath(); ctx.arc(x, y, 92, 3.55, 4.6); ctx.stroke();
    ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(x, y, 70, 3.7, 4.3); ctx.stroke();
    ctx.restore();
  }
  rr(x + 126, y - 30, 26, 60, 9); fs('#b7bfca', OUT, 3);
}

// ---------- CENA 1: close-up na janela da máquina (u pode ser negativo: aproximação) ----------
function sceneWindow(u) {
  ctx.fillStyle = '#efe9e1'; ctx.fillRect(0, 0, W, H);
  const cx = 270, cy = 500, R = 360;
  const g = ctx.createLinearGradient(0, 100, W, 900); g.addColorStop(0, '#ffffff'); g.addColorStop(.5, '#c4cad3'); g.addColorStop(1, '#7e8794');
  circle(cx, cy, R + 52); fs(g, OUT, 5);
  ctx.save(); circle(cx, cy, R); ctx.clip();
  ctx.fillStyle = '#2f3642'; ctx.fillRect(0, 0, W, H);
  const ang = u * 7;
  ctx.fillStyle = '#242a34';
  for (let ring = 1; ring <= 6; ring++) { const r = ring * 62, n = ring * 8; for (let k = 0; k < n; k++) { const a = ang * .6 + k * TAU / n; circle(cx + Math.cos(a) * r, cy + Math.sin(a) * r, 7); ctx.fill(); } }
  for (let i = 0; i < 6; i++) for (let k = 5; k >= 0; k--) {
    const a = ang + i * 1.05 - k * .07; ctx.globalAlpha = k ? .45 - k * .07 : 1;
    const x = cx + Math.cos(a) * 270, y = cy + Math.sin(a) * 270;
    if (k) { ell(x, y, 110, 66, a + 1.2); ctx.fillStyle = CLOTH[i]; ctx.fill(); } else clothBlob(x, y, 110, a + 1.2, CLOTH[i]);
  }
  ctx.globalAlpha = 1;
  ctx.beginPath(); ctx.moveTo(0, H);
  for (let x = 0; x <= W; x += 10) ctx.lineTo(x, cy + 175 + Math.sin(x * .018 + u * 9) * 22 + (x - cx) * .25 * Math.sin(u * 3));
  ctx.lineTo(W, H); ctx.closePath(); ctx.fillStyle = 'rgba(80,170,230,.55)'; ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,.65)'; ctx.lineWidth = 2.5;
  for (let i = 0; i < 28; i++) { const a = ang * .8 + i * .9, r = 70 + (i * 37) % 280; circle(cx + Math.cos(a) * r, cy + Math.sin(a) * r, 4 + (i % 4) * 3); ctx.stroke(); }
  // a meia
  const p = u >= 0 ? 1 : easeIn(inv(-1, 0, u));
  const s = lerp(.7, 2.75, p);
  const press = u >= 0 ? 1 : inv(-.06, 0, u);
  const jig = Math.sin(u * 22) * .04 * press;
  const sx = 1 + .22 * press + jig, sy = 1 - .12 * press - jig;
  const px = cx + Math.sin(u * 3.1) * 24 * p + (1 - p) * Math.cos(u * 7) * 140;
  const py = cy - 10 + Math.cos(u * 2.7) * 18 * p + (1 - p) * Math.sin(u * 7) * 140;
  const rot = Math.sin(u * 3.7) * .16 + (1 - p) * u * 9;
  drawSock(px, py + 28 * s * sy, s, { sx, sy, rot, eyes: { size: 1.45, pupil: 2.3, look: [Math.sin(u * 31) * .35, Math.cos(u * 27) * .35] }, brow: 'up', mouth: 'scream' });
  if (press > 0) { // marca de "esmagado no vidro"
    ctx.globalAlpha = .18 * press; ell(px + 8, py + 20, 150, 175, rot); ctx.fillStyle = '#fff'; ctx.fill(); ctx.globalAlpha = 1;
  }
  ctx.strokeStyle = 'rgba(255,255,255,.4)'; ctx.lineWidth = 46; ctx.beginPath(); ctx.arc(cx, cy, R - 62, 3.55, 4.55); ctx.stroke();
  ctx.lineWidth = 15; ctx.beginPath(); ctx.arc(cx, cy, R - 120, 3.7, 4.25); ctx.stroke();
  ctx.fillStyle = 'rgba(255,255,255,.08)'; ctx.beginPath(); ctx.moveTo(380, 120); ctx.lineTo(470, 120); ctx.lineTo(120, 900); ctx.lineTo(30, 900); ctx.fill();
  ctx.restore();
  circle(cx, cy, R + 9); fs(null, '#2b3038', 16);
  circle(cx, cy, R); fs(null, OUT, 4);
}

// ---------- CENA 2: máquina para, mão tira as roupas, meia cai na fresta ----------
const MX = 270, MY = 520, MS = 1.05; // posição da máquina no plano aberto
function machineCam(p, ty) { // p=0 plano aberto, p=1 close na janela
  const k = lerp(1, 2.857, p), dy = MY + 40 * MS;
  ctx.translate(270, lerp(dy, ty, p)); ctx.scale(k, k); ctx.translate(-270, -dy);
}
function scene2(t) {
  ctx.save();
  let zp = 1 - easeOut(inv(2.0, 2.4, t));
  if (t > 4.6) zp = 0;
  machineCam(zp, 500);
  if (t > 4.6) { // aproxima na borracha da porta
    const z = 1 + .9 * easeOut(inv(4.62, 4.95, t)), fy = MY + (40 + 110) * MS;
    ctx.translate(270, fy); ctx.scale(z, z); ctx.translate(-270, -fy);
  }
  laundryBg();
  const drum = 7 * easeOut(inv(1.6, 2.6, t)) + t * .2;
  const open = easeOut(inv(2.55, 3.0, t)) * (1 - easeIn(inv(4.25, 4.6, t)));
  const handIn = easeIO(inv(3.0, 3.5, t)), handOut = easeIn(inv(3.65, 4.2, t));
  const grabbed = t > 3.5;
  ctx.save(); ctx.translate(MX, MY); ctx.scale(MS, MS);
  drawMachine({
    drum, open, display: t < 2.55 ? (Math.floor(t * 4) % 2 ? 'FIM' : '') : 'FIM', led: t < 2.55, t, water: 1 - inv(2, 2.6, t),
    contents: () => {
      if (!grabbed) for (let i = 0; i < 5; i++) { const a = drum + i * 1.25; clothBlob(Math.cos(a) * 62, 40 + Math.sin(a) * 62 + 20 * inv(2.4, 2.8, t), 42, a, CLOTH[i]); }
      // meia: escorrega do vidro até a borracha
      const fall = easeIn(inv(2.25, 2.6, t));
      let hy = lerp(30, 134, fall), hs = .62 - .14 * fall, look = [0, -.6], mouth = 'o', brow = null, eyes = 1.2;
      let rot = (1 - fall) * Math.sin(t * 6) * .3;
      if (t > 3.55 && t < 4.6) { // "ei! esqueceu de mim!"
        const j = Math.abs(Math.sin((t - 3.55) * 12)) * 14 * (1 - inv(4.2, 4.5, t));
        hy -= j; look = [.9, -.6]; mouth = 'scream'; brow = 'up'; rot = Math.sin(t * 20) * .15;
      }
      if (t > 4.6) { hy += easeIn(inv(4.7, 5.15, t)) * 90; look = [0, -1]; mouth = 'scream'; eyes = 1.5; brow = 'up'; }
      if (t > 4.6) { // esmagada pela porta
        const sq = spring(t - 4.6) * .3;
        drawSock(0, hy, hs, { sx: 1 + sq, sy: 1 - sq, rot, eyes: { size: eyes, look }, brow, mouth });
      } else drawSock(0, hy, hs, { rot, eyes: { size: eyes, look }, brow, mouth });
    }
  });
  ctx.restore();
  // mão
  if (t > 3.0 && t < 4.25) {
    const tx = 270 + (1 - handIn) * 420 + handOut * 520, ty = MY + 40 * MS + handOut * -40;
    if (grabbed) { // trouxa de roupa
      for (let i = 0; i < 5; i++) clothBlob(tx - 40 + Math.cos(i * 2.1) * 30, ty + Math.sin(i * 2.1) * 26, 36, i, CLOTH[i]);
    }
    drawHand(tx + 20 * .9, ty, .9, 0, grabbed ? 'fist' : 'open');
  }
  ctx.restore();
  if (t > 3.55 && t < 4.3) caption('!', 270 - 50, 640, 60, { scale: popScale(t - 3.55), fill: '#ffd60a', stroke: OUT });
  sfxText('BAM!', 330, 300, 78, t - 4.6, .1);
  if (t > 4.6 && t < 5.15) shakeAdd(spring(t - 4.6, 30, 6) * 10);
}

// queda no escuro
function sceneFall(t) {
  const u = t - 5.15;
  ctx.fillStyle = '#07040d'; ctx.fillRect(0, 0, W, H);
  for (let i = 0; i < 9; i++) {
    const ph = ((u * 1.6 + i / 9) % 1), r = Math.pow(ph, 2.2) * 700;
    circle(270, 480, r); ctx.strokeStyle = `rgba(140,90,220,${.5 * (1 - ph) * ph * 3})`; ctx.lineWidth = 3 + ph * 18; ctx.stroke();
  }
  const s = lerp(1.6, .15, easeIn(clamp(u / .85)));
  drawSock(270, 480, s, { rot: u * 9, eyes: { size: 1.5, pupil: 2.4 }, brow: 'up', mouth: 'scream' });
  caption('BLOP', 270, 200, 70, { scale: popScale(u), fill: '#ffd60a', stroke: OUT, alpha: clamp(1 - (u - .3) / .3) });
  caption('blop...', 270, 290, 44, { scale: popScale(u - .3), fill: '#e0c3fc', stroke: OUT, alpha: .8 * clamp(1 - (u - .55) / .2) });
  caption('blop...', 270, 360, 30, { scale: popScale(u - .55), fill: '#b388eb', stroke: OUT, alpha: .55 * clamp(1 - (u - .8) / .1) });
}

// ---------- CENA 3: O Reino das Meias Perdidas ----------
const COLS = ['#ffbe0b', '#8338ec', '#06d6a0', '#ff006e', '#3a86ff', '#fb5607', '#adb5bd', '#90be6d', '#f15bb5'];
const LOST = [30, 110, 205, 345, 480, 575, 700, 860, 990, 1140, 1300, 1430].map((x, i) => {
  const pat = ['stripes', 'dots', 'plain'][i % 3];
  return { x, s: .5 + hash(i) * .2, look: { base: pat === 'plain' ? COLS[i % 9] : (i % 2 ? '#fff' : COLS[(i + 3) % 9]), stripe: COLS[i % 9], cuff: COLS[(i + 5) % 9], pat }, ph: hash(i + 9) * 6, flip: hash(i + 3) > .6 };
});
const HK = .95;
const bridgeY = x => (x > 600 && x < 800) ? 800 - 55 * Math.sin(PI * (x - 600) / 200) : 800;
function heroKingdom(t) {
  const walk = easeIO(inv(8.2, 12.6, t));
  const x = t < 8.2 ? 270 : lerp(270, 1010, walk);
  return { x, y: bridgeY(x) - 60 * HK, walking: t > 8.2 && t < 12.6 };
}
function kingdomWorld(t, opt = {}) {
  // teto (fundo da máquina) com a fresta de luz
  ctx.fillStyle = '#120b20'; ctx.fillRect(-300, -200, 2200, 290);
  ctx.fillStyle = '#2a1d40'; for (let x = -280; x < 1900; x += 120) { circle(x, 70, 7); ctx.fill(); }
  ctx.fillStyle = '#ffe9a8'; ctx.fillRect(256, 84, 28, 6);
  const lg = ctx.createLinearGradient(0, 90, 0, 800); lg.addColorStop(0, 'rgba(255,236,170,.35)'); lg.addColorStop(1, 'rgba(255,236,170,0)');
  ctx.fillStyle = lg; ctx.beginPath(); ctx.moveTo(256, 90); ctx.lineTo(284, 90); ctx.lineTo(400, 800); ctx.lineTo(140, 800); ctx.fill();
  // rio do ralo
  ctx.fillStyle = '#16314f'; ctx.fillRect(600, 790, 200, 400);
  ctx.strokeStyle = 'rgba(120,190,255,.45)'; ctx.lineWidth = 3;
  for (let k = 0; k < 4; k++) { ctx.beginPath(); for (let x = 600; x <= 800; x += 10) ctx.lineTo(x, 830 + k * 30 + Math.sin(x * .06 + t * 4 + k) * 4); ctx.stroke(); }
  // chão
  ctx.fillStyle = '#3a2a55'; ctx.fillRect(-300, 800, 900, 400); ctx.fillRect(800, 800, 1100, 400);
  ctx.fillStyle = '#56407a'; ctx.fillRect(-300, 800, 900, 10); ctx.fillRect(800, 800, 1100, 10);
  ctx.fillStyle = 'rgba(200,190,220,.35)';
  for (let i = 0; i < 30; i++) { const x = -250 + i * 70 + hash(i) * 30; if (x > 590 && x < 810) continue; ell(x, 860 + hash(i + 4) * 80, 12, 4); ctx.fill(); }
  // casas com telhado de tampa de pote
  [[150, 120, 110, '#ffd6a5', 'rgba(110,190,255,.85)'], [420, 100, 92, '#caffbf', 'rgba(255,120,180,.85)'], [920, 130, 120, '#bdb2ff', 'rgba(130,240,170,.85)']].forEach(([x, w, h, wall, lid], i) => {
    rr(x - w / 2, 800 - h, w, h, 6); fs(wall, OUT, 3);
    rr(x - 13, 800 - 46, 26, 46, [13, 13, 0, 0]); fs('#8d5a3b', OUT, 3);
    rr(x + w / 2 - 38, 800 - h + 22, 24, 22, 4); fs(`rgba(255,220,120,${.75 + .25 * Math.sin(t * 3 + i)})`, OUT, 2.5);
    ctx.beginPath(); ctx.moveTo(x - w / 2 - 18, 800 - h + 4); ctx.bezierCurveTo(x - w / 2 - 6, 800 - h - 62, x + w / 2 + 6, 800 - h - 62, x + w / 2 + 18, 800 - h + 4); ctx.closePath(); fs(lid, OUT, 3);
    rr(x - w / 2 - 22, 800 - h - 2, w + 44, 12, 6); fs(lid, OUT, 3);
    ctx.fillStyle = 'rgba(255,255,255,.4)'; ell(x - w * .2, 800 - h - 28, w * .18, 6, -.2); ctx.fill();
  });
  // cartaz de procurado (fone sem fio)
  ctx.save(); ctx.translate(920, 735); ctx.rotate(-.06);
  rr(-40, -48, 80, 96, 3); fs('#f3e3c3', OUT, 2.5);
  ctx.fillStyle = OUT; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.font = `900 11px ${FONT}`; ctx.fillText('PROCURADO', 0, -36);
  rr(-9, -24, 18, 20, 9); fs('#fff', OUT, 2); rr(-1, -8, 8, 26, 4); fs('#fff', OUT, 2);
  ctx.font = `800 9px ${FONT}`; ctx.fillText('desde 2023', 0, 32);
  ctx.restore();
  // postes de caneta
  [60, 520, 1400].forEach((x, i) => {
    const gl = ctx.createRadialGradient(x, 588, 2, x, 588, 90); gl.addColorStop(0, `rgba(255,230,140,${.55 + .1 * Math.sin(t * 5 + i)})`); gl.addColorStop(1, 'rgba(255,230,140,0)');
    ctx.fillStyle = gl; circle(x, 588, 90); ctx.fill();
    rr(x - 7, 600, 14, 200, 5); fs('#3a86ff', OUT, 3); rr(x - 7, 600, 14, 40, 5); fs('#1d4fbf', OUT, 3);
    rr(x + 5, 606, 6, 30, 3); fs('#1d4fbf', OUT, 2);
    circle(x, 588, 14); fs('#ffe58a', OUT, 3);
    ctx.beginPath(); ctx.moveTo(x - 20, 584); ctx.quadraticCurveTo(x, 556, x + 20, 584); ctx.closePath(); fs('#e63946', OUT, 3);
  });
  // placa
  ctx.save(); ctx.translate(1220, 0);
  rr(-104, 650, 14, 150, 3); fs('#7f4f24', OUT, 3); rr(90, 650, 14, 150, 3); fs('#7f4f24', OUT, 3);
  ctx.save(); ctx.translate(0, 640); ctx.rotate(-.03);
  rr(-132, -56, 264, 108, 8); fs('#b07a46', OUT, 4);
  ctx.strokeStyle = 'rgba(70,30,0,.3)'; ctx.lineWidth = 2;
  for (let y = -40; y < 54; y += 18) { ctx.beginPath(); ctx.moveTo(-126, y); ctx.lineTo(126, y + 2); ctx.stroke(); }
  ctx.fillStyle = '#2a1405'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.font = `900 25px ${FONT}`;
  ctx.fillText('BEM-VINDO.', 0, -20); ctx.fillStyle = '#7a0010'; ctx.fillText('NINGUÉM VOLTA.', 0, 20);
  ctx.restore(); ctx.restore();
  // ponte de elásticos de cabelo
  const tieC = ['#ff70a6', '#70d6ff', '#ffd670', '#e9ff70', '#ff9770', '#c77dff'];
  for (let i = 0; i <= 10; i++) {
    const x = 600 + i * 20, y = bridgeY(x) + 6;
    ell(x, y, 13, 8, Math.cos(PI * i / 10) * -.7); fs(null, OUT, 9); ell(x, y, 13, 8, Math.cos(PI * i / 10) * -.7); fs(null, tieC[i % 6], 5);
  }
  // meias perdidas
  const hero = heroKingdom(t);
  LOST.forEach((m, i) => {
    const gy = bridgeY(m.x), surprise = (t > 6.5 && t < 7.4 && i < 6) ? Math.abs(Math.sin((t - 6.5) * 9)) * 16 * (1 - inv(6.5, 7.4, t)) : 0;
    const bob = Math.abs(Math.sin(t * 3 + m.ph)) * 5 + surprise;
    const lk = [clamp((hero.x - m.x) / 90, -1, 1) * (m.flip ? -1 : 1), -.2];
    drawSock(m.x, gy - 60 * m.s - bob, m.s, { look: m.look, flip: m.flip, rot: Math.sin(t * 2 + m.ph) * .06, eyes: { look: lk, blink: (Math.sin(t * 1.3 + m.ph * 3) > .985) ? 1 : 0, size: surprise > 2 ? 1.25 : 1 }, mouth: i % 4 === 0 ? 'smile' : (surprise > 2 ? 'o' : null) });
    if (surprise > 2 && i % 2 === 0) caption('!', m.x, gy - 140 * m.s - 30, 30, { fill: '#ffd60a', stroke: OUT, lw: 6 });
  });
  // a heroína
  if (!opt.noHero) {
    let { x, y } = hero, rot = 0, sx = 1, sy = 1, eyes = { look: [0, 0], size: 1 }, mouth = null, brow = null, sweat = 0;
    if (t < 6.5) { const p = easeIn(inv(5.95, 6.5, t)); y = lerp(-120, y, p); rot = (1 - p) * 6; eyes = { size: 1.5, pupil: 2.4 }; mouth = 'scream'; }
    else if (t < 8.2) {
      const sq = spring(t - 6.5, 24, 6) * .35; sx = 1 + sq; sy = 1 - sq;
      if (t < 7.0) { eyes = { mode: 'closed' }; mouth = 'frown'; }
      else { eyes = { size: 1.25, look: [Math.sin((t - 7) * 5), -.3] }; mouth = 'o'; brow = 'up'; }
    } else if (t < 12.6) {
      y -= Math.abs(Math.sin(t * 10)) * 12; rot = Math.sin(t * 10) * .08; eyes = { look: [Math.sin(t * 1.7) * .8, -.2], size: 1.15 }; mouth = 'smile';
    } else {
      eyes = { look: [.8, -.8], size: 1.3 + .1 * spring(t - 13.25, 30, 5) }; mouth = 'wobble'; brow = 'sad'; sweat = inv(12.9, 13.4, t);
      sy = 1 - .08 * Math.max(0, spring(t - 13.3, 18, 5));
    }
    const sg = ctx.createRadialGradient(x, y, 10, x, y, 120); sg.addColorStop(0, 'rgba(255,230,160,.35)'); sg.addColorStop(1, 'rgba(255,230,160,0)');
    ctx.fillStyle = sg; circle(x, y, 120); ctx.fill();
    drawSock(x, y, HK, { rot, sx, sy, eyes, mouth, brow, sweat, t });
    if (t > 6.5 && t < 7.2) { // poeira
      const d = inv(6.5, 7.2, t); ctx.fillStyle = `rgba(200,190,230,${.6 * (1 - d)})`;
      for (let k = -3; k <= 3; k++) { circle(x + k * (14 + d * 26), 800 - 6 - Math.abs(k) * 3 * d, 9 * (1 - d) + 3); ctx.fill(); }
    }
  }
}
function kingdomBg(camX) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#1b1035'); g.addColorStop(.55, '#3c1e5a'); g.addColorStop(1, '#1f4f5c');
  ctx.fillStyle = g; ctx.fillRect(-300, -300, W + 600, H + 600);
  ctx.save(); ctx.translate(-camX * .35, 0);
  ctx.fillStyle = '#2e1d4d';
  [[-60, 260, 70, 600], [140, 330, 50, 500], [300, 210, 90, 640], [520, 300, 60, 520], [700, 240, 80, 600], [900, 320, 55, 520]].forEach(([x, y, w, h]) => { rr(x, y, w, h, 20); ctx.fill(); rr(x - 10, y + 60, w + 20, 18, 6); ctx.fill(); });
  ctx.fillStyle = '#4a2f73';
  for (let i = 0; i < 9; i++) { const x = -100 + i * 140, h = 90 + hash(i) * 80; rr(x, 800 - h, 70, h, 10); ctx.fill(); ell(x + 35, 800 - h, 48, 22); ctx.fill(); }
  ctx.restore();
}
function motes(t, col = '255,220,150') {
  for (let i = 0; i < 46; i++) {
    const x = ((hash(i) * W + t * 14 * (hash(i + 1) - .5) * 4) % W + W) % W;
    const y = ((hash(i + 2) * H - t * 18 * (.3 + hash(i + 3))) % H + H) % H;
    const a = .35 + .35 * Math.sin(t * 3 + i);
    ctx.fillStyle = `rgba(${col},${a})`; circle(x, y, 1.4 + hash(i + 5) * 2.4); ctx.fill();
  }
}
function sceneKingdom(t) {
  const camX = lerp(0, 905, easeIO(inv(8, 12.6, t)));
  const z = 1 + .05 * easeIO(inv(12.6, 13.6, t));
  ctx.save(); ctx.translate(270, 640); ctx.scale(z, z); ctx.translate(-270, -640);
  ctx.translate(270, 830); ctx.scale(1.32, 1.32); ctx.translate(-270, -830);
  kingdomBg(camX);
  ctx.save(); ctx.translate(-camX, 0); kingdomWorld(t); ctx.restore();
  ctx.restore();
  motes(t);
  if (t > 7.0 && t < 11.2) {
    const a = clamp((11.2 - t) / .3);
    caption('O REINO DAS\nMEIAS PERDIDAS', 270, 200, 46, { scale: popScale(t - 7.0), fill: '#ffd60a', stroke: '#2a0f45', alpha: a });
    for (let k = 0; k < 5; k++) { ctx.globalAlpha = a * (.5 + .5 * Math.sin(t * 6 + k * 2)); star(70 + k * 100, 120 + (k % 2) * 160, 10 + (k % 3) * 4, t); fs('#fff6c2', null); }
    ctx.globalAlpha = 1;
  }
}

// ---------- CENA 4: a fuga (montagem) ----------
function m1Map(u) { // plano de fuga num papel de bala
  ctx.save(); ctx.filter = 'blur(7px)'; ctx.translate(-200, -120); ctx.scale(1.25, 1.25); kingdomBg(150); ctx.save(); ctx.translate(-150, 0); kingdomWorld(9, { noHero: true }); ctx.restore(); ctx.restore();
  ctx.filter = 'none'; ctx.fillStyle = 'rgba(20,8,40,.35)'; ctx.fillRect(0, 0, W, H);
  const lookUp = u > 1.15;
  drawSock(270, 470, 3.1, { eyes: { look: lookUp ? [0, 0] : [.2, 1], size: 1.1, lid: lookUp ? .35 : 0 }, brow: 'angry', mouth: lookUp ? 'grin' : 'frown' });
  ctx.save(); ctx.translate(270, 720 + Math.sin(u * 3) * 4); ctx.rotate(-.04);
  const g = ctx.createLinearGradient(-200, -130, 200, 130); g.addColorStop(0, '#ff8fab'); g.addColorStop(.45, '#ffd6e0'); g.addColorStop(.55, '#ffc8dd'); g.addColorStop(1, '#ffb703');
  ctx.beginPath(); ctx.moveTo(-170, -120);
  for (let k = 0; k <= 8; k++) ctx.lineTo(-170 + (k % 2 ? -24 : 0), -120 + k * 30);
  ctx.lineTo(170, 120);
  for (let k = 8; k >= 0; k--) ctx.lineTo(170 + (k % 2 ? 24 : 0), -120 + k * 30);
  ctx.closePath(); fs(g, OUT, 4);
  ctx.strokeStyle = 'rgba(255,255,255,.55)'; ctx.lineWidth = 3;
  for (let k = 0; k < 5; k++) { ctx.beginPath(); ctx.moveTo(-150 + k * 70, -110); ctx.lineTo(-120 + k * 70, 110); ctx.stroke(); }
  // desenhos do mapa
  ctx.strokeStyle = OUT; ctx.lineWidth = 3;
  rr(-140, 40, 50, 60, 6); ctx.stroke(); circle(-115, 75, 15); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(-60, 80); ctx.lineTo(-10, -40); ctx.lineTo(10, -40); ctx.lineTo(-40, 80); ctx.stroke();
  for (let k = 0; k < 14; k++) { const a = k / 14 * TAU; ctx.beginPath(); ctx.moveTo(60 + Math.cos(a) * 18, 40 + Math.sin(a) * 18); ctx.lineTo(60 + Math.cos(a) * 26, 40 + Math.sin(a) * 26); ctx.stroke(); }
  circle(60, 40, 18); fs('#bbb', OUT, 3);
  const prog = easeIO(inv(.15, 1.1, u));
  const path = [[-115, 100], [-60, 110], [-25, 20], [0, -50], [60, 0], [100, -40], [120, -75]];
  ctx.setLineDash([9, 8]); ctx.strokeStyle = '#d00000'; ctx.lineWidth = 5; ctx.beginPath();
  const n = (path.length - 1) * prog;
  for (let k = 0; k <= Math.floor(n); k++) ctx[k ? 'lineTo' : 'moveTo'](...path[k]);
  if (n < path.length - 1) { const k = Math.floor(n), f = n - k; ctx.lineTo(lerp(path[k][0], path[k + 1][0], f), lerp(path[k][1], path[k + 1][1], f)); }
  ctx.stroke(); ctx.setLineDash([]);
  if (prog > .97) {
    ctx.strokeStyle = '#d00000'; ctx.lineWidth = 7; const s = popScale(u - 1.1) * 16;
    ctx.beginPath(); ctx.moveTo(120 - s, -75 - s); ctx.lineTo(120 + s, -75 + s); ctx.moveTo(120 + s, -75 - s); ctx.lineTo(120 - s, -75 + s); ctx.stroke();
    ctx.fillStyle = '#d00000'; ctx.font = `900 22px ${FONT}`; ctx.textAlign = 'center'; ctx.fillText('SAÍDA', 120, -102);
  }
  ctx.restore();
  caption('PLANO DE FUGA', 270, 150, 50, { scale: popScale(u - .05), fill: '#fff' });
}
function m2Hose(u) { // escalando a mangueira
  ctx.fillStyle = '#1d1730'; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = '#2a2045'; for (let i = 0; i < 5; i++) { rr(20 + i * 120, -50, 40, 1100, 20); ctx.fill(); }
  motes(u + 30, '170,150,255');
  const camY = u * 40;
  ctx.save(); ctx.translate(0, camY);
  const ax = 40, ay = 1080, bx = 520, by = -140, ang = Math.atan2(by - ay, bx - ax), len = Math.hypot(bx - ax, by - ay);
  ctx.save(); ctx.translate(ax, ay); ctx.rotate(ang);
  const g = ctx.createLinearGradient(0, -70, 0, 70); g.addColorStop(0, '#d9dde3'); g.addColorStop(.5, '#9aa3ad'); g.addColorStop(1, '#5c6470');
  rr(0, -70, len, 140, 40); fs(g, OUT, 4);
  ctx.strokeStyle = 'rgba(40,40,60,.45)'; ctx.lineWidth = 4;
  for (let x = 10; x < len; x += 22) { ctx.beginPath(); ctx.moveTo(x, -66); ctx.quadraticCurveTo(x + 8, 0, x, 66); ctx.stroke(); }
  ctx.restore();
  // avanço tipo minhoca
  const step = Math.floor(u * 3), f = easeIO((u * 3) % 1);
  const prog = .32 + (step + f) * .055;
  const hx = lerp(ax, bx, prog), hy = lerp(ay, by, prog);
  const stretch = Math.sin(f * PI) * .18;
  drawSock(hx - 26, hy - 30, 1.5, { rot: ang + PI / 2, sx: 1 - stretch * .5, sy: 1 + stretch, eyes: { look: [.6, -.9], size: 1.1 }, brow: 'angry', mouth: 'teeth', sweat: (u * 2) % 1 });
  ctx.fillStyle = '#8fd3ff';
  for (let k = 0; k < 4; k++) { const ph = (u * 1.7 + k / 4) % 1; circle(hx - 70 - ph * 60 * (k % 2 ? 1 : -.4), hy - 120 + ph * ph * 160, 5); ctx.fill(); }
  ctx.restore();
  caption('ESCALAR A MANGUEIRA', 270, 150, 38, { scale: popScale(u - .05) });
}
function m3Lint(u) { // fugindo do monstro de fiapos
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#120a22'); g.addColorStop(1, '#3a2a55');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.strokeStyle = 'rgba(255,255,255,.12)'; ctx.lineWidth = 3;
  for (let i = 0; i < 16; i++) { const y = 80 + hash(i) * 640, x = ((-u * 1600 - hash(i + 3) * 900) % 700 + 700) % 700 - 80; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 90 + hash(i) * 120, y); ctx.stroke(); }
  ctx.fillStyle = '#3a2a55'; ctx.fillRect(0, 780, W, 200); ctx.fillStyle = '#56407a'; ctx.fillRect(0, 780, W, 10);
  ctx.fillStyle = 'rgba(200,190,220,.35)';
  for (let i = 0; i < 10; i++) { const x = ((i * 90 - u * 1400) % 900 + 900) % 900 - 100; ell(x, 840 + (i % 3) * 30, 14, 4); ctx.fill(); }
  // monstro
  const mx = 140 + Math.sin(u * 7) * 14 + u * 20, my = 600 - Math.abs(Math.sin(u * 8)) * 30, R = 150;
  for (let k = 0; k < 140; k++) {
    const a = k / 140 * TAU + Math.sin(u * 20 + k) * .05, r1 = R * (.75 + hash(k) * .15), r2 = R * (1.02 + hash(k + 7) * .22 + .04 * Math.sin(u * 30 + k));
    ctx.beginPath(); ctx.moveTo(mx + Math.cos(a) * r1, my + Math.sin(a) * r1); ctx.lineTo(mx + Math.cos(a + .05) * r2, my + Math.sin(a + .05) * r2);
    ctx.strokeStyle = k % 3 ? '#9c97a6' : '#c4bfcc'; ctx.lineWidth = 6; ctx.stroke();
  }
  circle(mx, my, R * .92); fs('#8d8796', null);
  for (let k = 0; k < 20; k++) { ell(mx + (hash(k) - .5) * R * 1.3, my + (hash(k + 2) - .5) * R * 1.3, 14, 5, hash(k) * 3); fs(null, 'rgba(60,55,70,.4)', 2); }
  [[-45, -30], [45, -30]].forEach(([ex, ey], i) => {
    const gl = ctx.createRadialGradient(mx + ex, my + ey, 2, mx + ex, my + ey, 50); gl.addColorStop(0, 'rgba(255,40,40,.8)'); gl.addColorStop(1, 'rgba(255,40,40,0)');
    ctx.fillStyle = gl; circle(mx + ex, my + ey, 50); ctx.fill();
    ell(mx + ex, my + ey, 22, 16, i ? -.3 : .3); fs('#ff2b2b', OUT, 3); circle(mx + ex + 6, my + ey, 6); ctx.fillStyle = '#300'; ctx.fill();
    ctx.beginPath(); ctx.moveTo(mx + ex - 26 * (i ? -1 : 1), my + ey - 34); ctx.lineTo(mx + ex + 22 * (i ? -1 : 1), my + ey - 14); fs(null, OUT, 7);
  });
  const mo = .5 + .5 * Math.abs(Math.sin(u * 9));
  ctx.beginPath(); ctx.moveTo(mx - 70, my + 30);
  for (let k = 0; k <= 8; k++) ctx.lineTo(mx - 70 + k * 17.5, my + 30 + (k % 2 ? -12 : 0));
  ctx.lineTo(mx + 70, my + 30 + 50 * mo); ctx.quadraticCurveTo(mx, my + 30 + 80 * mo, mx - 70, my + 30 + 50 * mo); ctx.closePath(); fs('#2b0b14', OUT, 3);
  ctx.fillStyle = '#fff'; for (let k = 0; k < 8; k++) { ctx.beginPath(); ctx.moveTo(mx - 66 + k * 17.5, my + 30 + (k % 2 ? -12 : 0) - 1); ctx.lineTo(mx - 58 + k * 17.5, my + 50); ctx.lineTo(mx - 50 + k * 17.5, my + 30); ctx.fill(); }
  // heroína correndo
  const hop = Math.abs(Math.sin(u * 16)) * 40;
  drawSock(400, 780 - 60 * 1.2 - hop, 1.2, { rot: .18 + Math.sin(u * 16) * .1, eyes: { look: [-1, -.2], size: 1.45, pupil: 2.6 }, brow: 'up', mouth: 'scream', sweat: (u * 3) % 1 });
  ctx.strokeStyle = 'rgba(255,255,255,.5)'; ctx.lineWidth = 4;
  for (let k = 0; k < 3; k++) { ctx.beginPath(); ctx.moveTo(320 - k * 6, 640 + k * 40 - hop); ctx.lineTo(280 - k * 10, 640 + k * 40 - hop); ctx.stroke(); }
  caption('GRRRR!', 150, 360, 52, { scale: popScale(u - .2) * (1 + .05 * Math.sin(u * 40)), fill: '#ff4d6d', stroke: OUT, rot: -.15 });
  caption('O MONSTRO DE FIAPOS', 270, 150, 38, { scale: popScale(u - .05) });
}
function m4Sling(u) { // estilingue de elástico
  ctx.fillStyle = '#1d1730'; ctx.fillRect(0, 0, W, H);
  const gl = ctx.createRadialGradient(270, 500, 20, 270, 500, 500); gl.addColorStop(0, 'rgba(130,80,200,.45)'); gl.addColorStop(1, 'rgba(130,80,200,0)');
  ctx.fillStyle = gl; ctx.fillRect(0, 0, W, H);
  motes(u + 50, '170,150,255');
  ctx.fillStyle = '#3a2a55'; ctx.fillRect(0, 800, W, 200); ctx.fillStyle = '#56407a'; ctx.fillRect(0, 800, W, 10);
  // grampos
  [180, 360].forEach(x => {
    ctx.beginPath(); ctx.moveTo(x - 8, 805); ctx.lineTo(x - 8, 560);
    for (let y = 560; y < 800; y += 20) ctx.lineTo(x + 8 + (Math.floor(y / 20) % 2 ? 4 : -4), y + 10);
    fs(null, '#000', 9); ctx.stroke(); fs(null, '#444b5a', 5);
    circle(x - 8, 556, 7); fs('#444b5a', '#000', 3);
  });
  const rel = 1.15, pull = easeOut(inv(.1, 1.0, u)), shake = u < rel ? Math.sin(u * 70) * 3 * pull : 0;
  let hx = lerp(270, 245, pull) + shake, hy = lerp(600, 720, pull);
  const fly = inv(rel, rel + .3, u);
  if (u > rel) { hx = lerp(245, 640, easeIn(fly)); hy = lerp(720, -260, easeIn(fly)); }
  const L = [172, 575], R = [352, 575];
  let mid = [hx, hy + 40];
  if (u > rel) mid = [266, 575 + spring(u - rel, 40, 5) * 90];
  ctx.beginPath(); ctx.moveTo(...L); ctx.quadraticCurveTo(mid[0], mid[1] + 10, ...R); fs(null, OUT, 13); ctx.stroke(); fs(null, '#ff70a6', 8);
  if (u <= rel) drawSock(hx, hy, 1.15, { eyes: { look: [.5, -.8], size: 1, lid: .3 }, brow: 'angry', mouth: 'teeth', sy: 1 - pull * .12, sx: 1 + pull * .08 });
  else if (fly < 1) {
    const a = Math.atan2(-980, 395);
    drawSock(hx, hy, 1.15, { rot: a + PI / 2, sy: 1.35, sx: .8, eyes: { size: 1.5, pupil: 2.4 }, brow: 'up', mouth: 'scream' });
    ctx.strokeStyle = 'rgba(255,255,255,.5)'; ctx.lineWidth = 5;
    for (let k = 0; k < 4; k++) { ctx.beginPath(); ctx.moveTo(hx - 30 + k * 18, hy + 90); ctx.lineTo(hx - 70 + k * 18, hy + 200); ctx.stroke(); }
  }
  sfxText('TWANG!', 300, 330, 70, u - rel, -.1);
  caption('ESTILINGUE!', 270, 150, 44, { scale: popScale(u - .05) });
}
function m5Fly(u) { // voo em câmera lenta
  ctx.save(); ctx.translate(270, 480); ctx.scale(1.15, 1.15); ctx.translate(-270, -480); laundryBg(); ctx.restore();
  const p = u / 2;
  const hx = lerp(-80, 620, p), hy = lerp(760, 230, p) - Math.sin(p * PI) * 120, rot = lerp(.5, 1.2, p);
  for (let k = 1; k < 12; k++) {
    const q = p - k * .025; if (q < 0) continue;
    const sx_ = lerp(-80, 620, q), sy_ = lerp(760, 230, q) - Math.sin(q * PI) * 120;
    ctx.globalAlpha = (1 - k / 12) * .9; star(sx_ - 30 + hash(k) * 20, sy_ + 30 + hash(k + 2) * 30, 10 - k * .5, u * 2 + k); fs('#fff6a5', null); ctx.globalAlpha = 1;
  }
  const flap = Math.sin(u * 10) * .05;
  drawSock(hx, hy, 1.7, { rot: rot + flap, sx: 1.08, sy: .95, eyes: { mode: 'closed' }, mouth: 'grin', blush: true });
  const vg = ctx.createRadialGradient(270, 480, 200, 270, 480, 700); vg.addColorStop(0, 'rgba(255,255,255,0)'); vg.addColorStop(1, 'rgba(255,230,180,.55)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  caption('LIBERDADE!!!', 270, 150, 52, { scale: popScale(u - .1), fill: '#ffd60a', stroke: OUT });
}

// ---------- CENA 5: o reencontro... só que não ----------
function basket(front) {
  const top = 640;
  if (!front) {
    ell(270, top, 240, 34); fs('#7a4a24', OUT, 4);
    rr(70, top - 80, 170, 70, 10); fs('#8ecae6', OUT, 3); ctx.fillStyle = 'rgba(255,255,255,.4)'; ctx.fillRect(80, top - 60, 150, 6);
    rr(250, top - 70, 220, 60, 10); fs('#ffd6a5', OUT, 3); ctx.fillStyle = 'rgba(0,0,0,.08)'; ctx.fillRect(260, top - 40, 200, 8);
    rr(110, top - 40, 300, 50, 10); fs('#cdb4db', OUT, 3);
    return;
  }
  ctx.beginPath(); ctx.moveTo(30, top); ctx.lineTo(510, top); ctx.lineTo(475, 990); ctx.lineTo(65, 990); ctx.closePath();
  ctx.save(); ctx.clip(); ctx.fillStyle = '#c68b59'; ctx.fillRect(0, top, W, 400);
  for (let r = 0, y = top + 26; y < 1000; y += 30, r++) for (let x = 20 + (r % 2) * 22; x < 540; x += 44) { ell(x, y, 20, 12); fs('#d9a066', 'rgba(90,50,20,.55)', 2.5); }
  ctx.restore();
  ctx.beginPath(); ctx.moveTo(30, top); ctx.lineTo(510, top); ctx.lineTo(475, 990); ctx.lineTo(65, 990); ctx.closePath(); fs(null, OUT, 4);
  rr(18, top - 16, 504, 32, 16); fs('#a86b3c', OUT, 4);
  ctx.strokeStyle = 'rgba(60,30,10,.35)'; ctx.lineWidth = 3;
  for (let x = 40; x < 510; x += 26) { ctx.beginPath(); ctx.moveTo(x, top - 14); ctx.lineTo(x + 14, top + 14); ctx.stroke(); }
}
const HS = 1.1, SEAT = 600; // escala e "chão" das meias no cesto
function couple(t, reveal) { // par + meia de bolinhas
  const r = easeBack(inv(27.45, 27.75, t)) * reveal;
  const px = lerp(400, 385, r), dx = lerp(400, 458, r);
  const pairEyes = t < 25.3 ? { look: [-.3, 0] } : (t < 26.6 ? { look: [-1, -.2], size: 1.2 } : { look: [1, -.4], size: 1 });
  if (reveal > 0) drawSock(dx, SEAT - 60 * HS * .95 - (t > 27.4 ? Math.max(0, spring(t - 27.45, 20, 6)) * 10 : 0), HS * .95, { skin: 'dots', flip: true, eyes: { look: [-1, 0], lid: .45, size: 1 }, mouth: 'smile', rot: -.06 * r });
  drawSock(px, SEAT - 60 * HS, HS, { flip: true, eyes: pairEyes, mouth: t > 26.6 ? 'teeth' : (t > 25.3 ? 'o' : null), sweat: t > 26.6 ? ((t * 1.2) % 1) : 0, brow: t > 26.6 ? 'sad' : null, rot: .06 * r });
  if (reveal > 0 && r > .05) { // os dois enrolados juntos
    ctx.save(); ctx.translate((px + dx) / 2 - 2, SEAT - 116 * HS); ctx.rotate(.02);
    rr(-62 * r, -11, 124 * r, 26, 12);
    ctx.save(); ctx.clip(); ctx.fillStyle = '#3a86ff'; ctx.fillRect(-80, -20, 160, 50); ctx.fillStyle = '#fff';
    for (let x = -70; x < 80; x += 14) { circle(x, -2, 3.2); ctx.fill(); circle(x + 7, 9, 3.2); ctx.fill(); }
    ctx.restore(); rr(-62 * r, -11, 124 * r, 26, 12); fs(null, OUT, 3.5);
    ctx.restore();
  }
}
function heroBasket(t) {
  let x = 150, y = SEAT - 60 * HS, o = { eyes: { look: [1, 0] }, t };
  if (t < 24.6) { const p = easeIn(inv(24.0, 24.6, t)); y = lerp(-150, y, p); o.rot = (1 - p) * -2; o.eyes = { size: 1.3 }; o.mouth = 'grin'; }
  else if (t < 25.2) { const sq = spring(t - 24.6, 24, 6) * .35; o.sx = 1 + sq; o.sy = 1 - sq; o.eyes = { look: [Math.sin((t - 24.6) * 9), -.2] }; o.mouth = 'smile'; }
  else if (t < 27.45) {
    const p = inv(25.45, 27.45, t);
    x = lerp(150, 222, p); y -= Math.abs(Math.sin(p * PI * 3)) * 26;
    o.eyes = { mode: 'heart', size: 1.25 + .15 * popScale(t - 25.2), t }; o.mouth = 'grin'; o.blush = true; o.rot = Math.sin(p * PI * 3) * .08;
  } else {
    x = 222 - spring(t - 27.45, 25, 8) * 8; o.rot = -.1 * Math.max(0, spring(t - 27.45, 16, 6));
    o.eyes = { size: 1.5, pupil: 2.3, look: [1, -.2] }; o.mouth = 'o'; o.brow = 'up';
    if (t > 28.6) { o.eyes = { size: 1.35, pupil: 2.6, look: [.9, 0] }; o.mouth = 'wobble'; o.brow = 'sad'; }
  }
  return { x, y, o };
}
function scene5(t) {
  const zoom = easeOut(inv(30.0, 30.35, t)), dark = inv(30.0, 30.3, t);
  const hb = heroBasket(t);
  const fx = hb.x, fy = hb.y - 28 * HS;
  ctx.save();
  const k = lerp(1, 3.3, zoom);
  ctx.translate(lerp(270, 270, zoom), lerp(480, 520, zoom)); ctx.scale(k, k); ctx.translate(-lerp(270, fx, zoom), -lerp(480, fy, zoom));
  laundryBg(); basket(false);
  couple(t, t > 27.45 ? 1 : 0);
  if (dark > 0) {
    ctx.fillStyle = `rgba(30,10,60,${.85 * dark})`; ctx.fillRect(-300, -300, 1200, 1600);
    if (t > 30.3) { // raio
      ctx.save(); ctx.translate(fx + 40, fy - 120); ctx.scale(.45, .45);
      ctx.beginPath(); ctx.moveTo(-10, -260); ctx.lineTo(60, -260); ctx.lineTo(10, -60); ctx.lineTo(70, -60); ctx.lineTo(-50, 200); ctx.lineTo(-10, 0); ctx.lineTo(-60, 0); ctx.closePath();
      ctx.shadowColor = '#fff6a5'; ctx.shadowBlur = 40; fs('#ffd60a', '#fff', 6); ctx.restore();
    }
    ctx.fillStyle = `rgba(150,190,255,${.6 * dark})`;
    for (let i = 0; i < 40; i++) { const rx = fx - 100 + hash(i) * 200, ry = fy - 150 + ((hash(i + 1) * 300 + t * 260) % 300); rr(rx, ry, 1.2, 9, .6); ctx.fill(); }
  }
  hb.o.t = t;
  if (t > 30.0) { hb.o.tear = easeOut(inv(30.2, 30.9, t)); hb.o.eyes = { size: 1.35, pupil: 3.4, look: [0, -.3] }; hb.o.mouth = 'wobble'; hb.o.brow = 'sad'; }
  drawSock(hb.x, hb.y, HS, hb.o);
  if (zoom < .99) basket(true);
  ctx.restore();
  // corações flutuando (câmera lenta romântica)
  if (t > 25.3 && t < 27.45) {
    const a = clamp((t - 25.3) / .3);
    const vg = ctx.createRadialGradient(270, 480, 150, 270, 480, 650); vg.addColorStop(0, 'rgba(255,150,200,0)'); vg.addColorStop(1, `rgba(255,120,180,${.5 * a})`);
    ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
    for (let i = 0; i < 14; i++) { const hx = 40 + hash(i) * 460, hy = 900 - ((t - 25.3) * (60 + hash(i + 2) * 80) + hash(i + 5) * 500) % 900; heartPath(hx, hy, 10 + hash(i + 1) * 12); ctx.globalAlpha = .75 * a; fs('#ff4d8d', null); ctx.globalAlpha = 1; }
  }
  if (t > 27.45 && t < 27.6) { ctx.fillStyle = `rgba(255,255,255,${.8 * (1 - inv(27.45, 27.6, t))})`; ctx.fillRect(0, 0, W, H); }
  // balão "faz 3 semanas..."
  if (t > 28.0 && t < 30.0) {
    const s = popScale(t - 28.0); ctx.save(); ctx.translate(392, 395); ctx.scale(s, s);
    rr(-118, -42, 236, 76, 30); fs('#fff', OUT, 4);
    ctx.beginPath(); ctx.moveTo(-10, 32); ctx.lineTo(10, 70); ctx.lineTo(25, 32); fs('#fff', null); ctx.beginPath(); ctx.moveTo(-10, 34); ctx.lineTo(10, 70); ctx.lineTo(25, 34); fs(null, OUT, 4);
    ctx.fillStyle = OUT; ctx.font = `italic 800 28px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const full = 'faz 3 semanas…', n = Math.floor(clamp((t - 28.1) / .7) * full.length);
    ctx.fillText(full.slice(0, n), 0, -4); ctx.restore();
  }
  if (t > 30.3 && t < 30.42) { ctx.fillStyle = 'rgba(255,255,255,.9)'; ctx.fillRect(0, 0, W, H); }
  if (t > 27.45 && t < 28.1) sfxText('*SCRATCH*', 270, 200, 46, t - 27.45, -.06, '#fff');
}

// ---------- CENA 6: de volta pra máquina (loop) ----------
function scene6a(t) { // mão pega a meia no cesto
  laundryBg(); basket(false); couple(t, 1);
  const lift = easeIn(inv(33.25, 34.0, t)) * 820;
  const hx = 150, hy = SEAT - 60 * HS - lift;
  const sw = t > 33.15 ? Math.sin((t - 33.15) * 9) * .25 * (1 - inv(33.2, 34, t) * .5) : 0;
  const o = { eyes: { look: [0, -.8], size: 1.1 }, brow: 'sad', mouth: 'frown', sy: 1 - Math.sin(t * 2.2) * .03, t, rot: sw };
  if (t > 33.1) { o.eyes = { size: 1.5, pupil: 2.4, look: [0, -1] }; o.mouth = 'o'; o.brow = 'up'; }
  if (t < 33.1) drawSock(hx, hy, HS, o);
  basket(true);
  if (t >= 33.1) { ctx.save(); ctx.translate(hx, hy - 62 * HS); ctx.rotate(sw); ctx.translate(-hx, -(hy - 62 * HS)); drawSock(hx, hy, HS, o); ctx.restore(); }
  const reach = easeOut(inv(32.3, 33.1, t));
  const tx = hx, ty = lerp(-300, hy - 64 * HS, reach) - (t > 33.25 ? 0 : 0);
  drawHand(tx + 14 * 1.05, ty - 70 * 1.05, 1.05, -PI / 2, t > 33.1 ? 'pinch' : 'open');
  if (t > 32.0 && t < 32.3) { ctx.fillStyle = `rgba(0,0,0,${1 - inv(32.0, 32.3, t)})`; ctx.fillRect(0, 0, W, H); }
}
function scene6b(t) { // a mão olha a meia... e dá de ombros
  ctx.save(); ctx.filter = 'blur(6px)'; ctx.translate(270, 480); ctx.scale(1.7, 1.7); ctx.translate(-330, -380); laundryBg(); ctx.restore(); ctx.filter = 'none';
  const shrug = t > 35.0 && t < 35.7 ? Math.abs(Math.sin((t - 35.0) * PI / .35)) * -26 : 0;
  const turn = Math.sin((t - 34) * 2.6) * .3 * (1 - inv(34.9, 35.1, t));
  const s = 2.0, px = 270, py = 330 + shrug;
  const o = { eyes: { size: 1.5, pupil: 3.6, look: [0, -.4] }, brow: 'up', mouth: 'smile', blush: true, t };
  if (t > 35.25) { o.eyes = { size: 1.4, pupil: 2.6, look: [0, -.8] }; o.mouth = 'o'; o.brow = 'sad'; o.blush = false; o.sweat = inv(35.3, 35.6, t); }
  ctx.save(); ctx.translate(px, py); ctx.rotate(turn); ctx.translate(-px, -py);
  drawSock(px, py + 62 * s, s, o);
  ctx.restore();
  drawHand(px + 14 * 1.6, py - 70 * 1.6, 1.6, -PI / 2, 'pinch');
  // brilho "olhos pidões"
  if (t < 35.2) for (let k = 0; k < 4; k++) { ctx.globalAlpha = .5 + .5 * Math.sin(t * 8 + k); star(170 + k * 66, 520 + (k % 2) * 60, 9, t * 2); fs('#fff6a5', null); ctx.globalAlpha = 1; }
  caption('?', 420, 260, 110, { scale: popScale(t - 34.35) * (t < 35.0 ? 1 : 0), fill: '#fff' });
  if (t > 35.0) caption('🤷', 420, 250, 110, { scale: popScale(t - 35.0), shadow: false, lw: 1, stroke: 'rgba(0,0,0,0)' });
}
function scene6c(t) { // jogada de volta na máquina, liga e zoom
  const zp = easeIn(inv(38.5, 39.35, t));
  ctx.save(); machineCam(zp, 500);
  laundryBg();
  const open = 1 - easeIn(inv(36.85, 37.2, t));
  const spinStart = 37.6, sp = Math.max(0, t - spinStart);
  const drum = .5 * 9 * sp * sp + t * .1;
  const tossP = inv(35.8, 36.55, t);
  ctx.save(); ctx.translate(MX, MY); ctx.scale(MS, MS);
  drawMachine({
    drum, open, display: t > 37.45 ? (t > spinStart ? 'ON' : '...') : '', led: t > 37.45, t, water: inv(37.8, 38.6, t), dial: t > 37.45 ? .6 : -1,
    contents: () => {
      if (tossP < 1) return;
      const a = PI / 2 + drum, r = 75;
      const land = spring(t - 36.55, 20, 6) * .3;
      let o = { eyes: { size: 1.4, pupil: 2.4, look: [0, -.6] }, brow: 'up', mouth: 'scream', t };
      if (t > 37.2 && t < 37.6) { o.eyes = { size: 1.5, pupil: 2.4, look: [0, 0] }; o.mouth = 'o'; }
      drawSock(Math.cos(a) * r * (sp > 0 ? 1 : 0), 40 + (sp > 0 ? Math.sin(a) * r : 75) - 60 * .55, .55, Object.assign(o, { rot: sp > 0 ? drum : 0, sx: 1 + land, sy: 1 - land }));
    }
  });
  ctx.restore();
  if (tossP > 0 && tossP < 1) { // arco da jogada
    const p = easeIn(tossP), x = lerp(640, 270, p), y = lerp(-100, MY + 75 * MS, p) - Math.sin(p * PI) * 160, s = lerp(1.3, .6, p);
    drawSock(x, y, s, { rot: p * 12, eyes: { size: 1.5, pupil: 2.4 }, brow: 'up', mouth: 'scream' });
  }
  ctx.restore();
  sfxText('BAM!', 340, 260, 78, t - 37.2, .1);
  if (t > 37.2 && t < 37.6) shakeAdd(spring(t - 37.2, 30, 6) * 10);
  if (sp > 0) shakeAdd(Math.min(sp, 1.4) * 4 * Math.sin(t * 60) * (1 - inv(39.0, 39.4, t)));
  if (t > 35.8 && t < 36.1) { ctx.fillStyle = `rgba(255,255,255,${1 - inv(35.8, 36.1, t)})`; ctx.fillRect(0, 0, W, H); }
  // entra o close da cena 1 (u negativo) -> loop perfeito em t=40
  if (t > 39.0) {
    layer(easeIO(inv(39.0, 39.35, t)), () => sceneWindow(t - 40));
  }
}

// ---------- montagem ----------
let SHAKE = 0;
function shakeAdd(v) { SHAKE += v; }
function drawScene(t) {
  if (t < 2) sceneWindow(t);
  else if (t < 5.15) scene2(t);
  else if (t < 6.0) sceneFall(t);
  else if (t < 14) sceneKingdom(t);
  else if (t < 16) m1Map(t - 14);
  else if (t < 18) m2Hose(t - 16);
  else if (t < 20) m3Lint(t - 18);
  else if (t < 22) m4Sling(t - 20);
  else if (t < 24) m5Fly(t - 22);
  else if (t < 32) scene5(t);
  else if (t < 34) scene6a(t);
  else if (t < 35.8) scene6b(t);
  else scene6c(t);
}
function shakeFor(t) {
  let s = 0;
  if (t < 2) s += 3.5;
  if (t > 39.7) s += 3.5 * inv(39.7, 40, t);
  if (t > 30.3 && t < 30.8) s += 10 * (1 - inv(30.3, 30.8, t));
  if (t > 6.5 && t < 6.8) s += 8 * (1 - inv(6.5, 6.8, t));
  if (t > 24.6 && t < 24.85) s += 6 * (1 - inv(24.6, 24.85, t));
  return s;
}
function draw(t) {
  t = ((t % DUR) + DUR) % DUR;
  ctx.setTransform(SC, 0, 0, SC, 0, 0);
  ctx.globalAlpha = 1; ctx.filter = 'none';
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  // 1ª passada para medir o tremor pedido pela cena
  SHAKE = 0;
  const base = shakeFor(t);
  ctx.save();
  const sx = (Math.sin(t * 91) + Math.sin(t * 57)) * .5 * base, sy = (Math.cos(t * 83) + Math.sin(t * 47)) * .5 * base;
  ctx.translate(sx, sy);
  ctx.save(); ctx.translate(-12, -12); ctx.scale(1 + 24 / W, 1 + 24 / H); // sobra de margem para o tremor
  drawScene(t);
  ctx.restore(); ctx.restore();
  if (SHAKE) { // tremores adicionais (impactos) aplicados à imagem já desenhada
    OFFCTX.setTransform(1, 0, 0, 1, 0, 0); OFFCTX.drawImage(cv, 0, 0);
    const a = Math.abs(SHAKE), m = 1 + 2 * (a + 1) / W * 1.8;
    ctx.save(); ctx.translate(W / 2 + SHAKE * Math.sin(t * 77), H / 2 + SHAKE * Math.cos(t * 69)); ctx.scale(m, m);
    ctx.drawImage(OFF, -W / 2, -H / 2, W, H); ctx.restore();
  }
  // legenda do gancho (início e fim, para o loop)
  if (t < 2) caption('POV: você é a\nmeia que sumiu', 270, 150, 48, { alpha: clamp((2 - t) / .15) });
  else if (t > 39.6) caption('POV: você é a\nmeia que sumiu', 270, 150, 48, { scale: easeBack(inv(39.6, 39.85, t)) });
  // vinheta
  const vg = ctx.createRadialGradient(270, 480, 300, 270, 480, 640); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,.28)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
}
window.draw = draw;
window.DUR = DUR;

// pré-visualização em tempo real (abrir index.html no navegador)
if (!/render/.test(location.search)) {
  const t0 = performance.now();
  const loop = () => { draw(((performance.now() - t0) / 1000) % DUR); requestAnimationFrame(loop); };
  document.fonts.ready.then(() => requestAnimationFrame(loop));
} else document.body.classList.add('render');
