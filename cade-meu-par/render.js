// Renderiza index.html quadro a quadro (JPEG) com Playwright.
// uso: node render.js <pasta_saida> [fps] [workers] [t_inicial t_final]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const out = process.argv[2] || 'frames', FPS = +(process.argv[3] || 30), WORKERS = +(process.argv[4] || 4);
const T0 = process.argv[5] !== undefined ? +process.argv[5] : 0, T1 = process.argv[6] !== undefined ? +process.argv[6] : 40;
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const url = 'file://' + path.resolve(__dirname, 'index.html') + '?render';
  const first = Math.round(T0 * FPS), last = Math.round(T1 * FPS);
  let next = first, done = 0;
  await Promise.all([...Array(WORKERS)].map(async () => {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
    await page.goto(url); await page.evaluate(() => document.fonts.ready);
    await page.evaluate(() => { draw(0); return new Promise(r => setTimeout(r, 300)); });
    while (true) {
      const i = next++; if (i >= last) break;
      const b64 = await page.evaluate(t => { draw(t); return document.getElementById('c').toDataURL('image/jpeg', .94).split(',')[1]; }, i / FPS);
      fs.writeFileSync(path.join(out, `f${String(i).padStart(5, '0')}.jpg`), Buffer.from(b64, 'base64'));
      if (++done % 100 === 0) console.log(done, 'quadros');
    }
  }));
  await browser.close();
})();
