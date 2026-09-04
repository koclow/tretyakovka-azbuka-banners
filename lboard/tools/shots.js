// Раскадровки креативов: node shots.js <outDir>
const puppeteer = require('puppeteer-core'); const path = require('path'); const fs = require('fs');
const ROOT = path.resolve(__dirname, '../../creatives'); const OUT = process.argv[2]; fs.mkdirSync(OUT, { recursive: true });
const ONLY = process.argv[3];
const SET = [
  ['desktop-illustration', [1440, 680, 1920]], ['desktop-photo', [1440, 680, 1920]],
  ['mobile-woman', [300, 375]], ['mobile-man', [300, 375]],
].filter(s => !ONLY || s[0] === ONLY);
const TIMES = [0, 300, 700, 1100, 1600, 2400, 3600];
(async () => {
  const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true, args: ['--force-device-scale-factor=1'] });
  const page = await browser.newPage();
  for (const [name, widths] of SET) for (const w of widths) {
    await page.setViewport({ width: w, height: 250, deviceScaleFactor: 1 });
    const url = 'file://' + path.join(ROOT, name, 'index.html');
    // обёртка: iframe точной ширины, чтобы вьюпорт не был шире экрана
    for (const t of [...TIMES, 'static']) {
      const q = t === 'static' ? '?static' : '?at=' + t;
      await page.goto(url + q, { waitUntil: 'load' });
      await new Promise(r => setTimeout(r, 400));
      if (t !== 'static') await page.evaluate(t => document.getAnimations().forEach(a => { a.pause(); a.currentTime = t; }), t);
      await new Promise(r => setTimeout(r, 100));
      await page.screenshot({ path: `${OUT}/${name}_${w}_${t}.png` });
    }
    console.log(name, w, 'ok');
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
