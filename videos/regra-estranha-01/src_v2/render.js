// usage: node render.js stills out_dir t1 t2 ...   |   node render.js frames out_dir startFrame endFrame
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [mode, out, ...rest] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'timeline.json'), 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('PAGEERROR', e.message));
  await page.goto('http://127.0.0.1:8766/anim.html');
  await page.evaluate(async d => { setData(d); await window.ready; }, data);
  const shot = async (t, file, q) => {
    const url = await page.evaluate(([t, q]) => { renderFrame(t); return document.getElementById('c').toDataURL(q ? 'image/jpeg' : 'image/png', 0.92); }, [t, q]);
    fs.writeFileSync(file, Buffer.from(url.split(',')[1], 'base64'));
  };
  if (mode === 'stills') {
    for (const t of rest.map(Number)) await shot(t, path.join(out, `t${t.toFixed(2)}.png`), false);
  } else {
    const fps = data.fps, a = +rest[0], b = +rest[1];
    for (let f = a; f < b; f++) await shot(f / fps, path.join(out, `f${String(f).padStart(5, '0')}.jpg`), true);
  }
  await browser.close();
})();
