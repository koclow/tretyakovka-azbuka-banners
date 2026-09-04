// node still2x.js <query> <out.png> <dpr> — стоп-кадр с deviceScaleFactor (суперсэмплинг)
const puppeteer = require('puppeteer-core'); const path = require('path');
(async () => {
  const dpr = +process.argv[4] || 2;
  const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true, args: ['--allow-file-access-from-files', '--font-render-hinting=none'] });
  const page = await browser.newPage(); await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: dpr });
  await page.goto('file://' + path.resolve(__dirname, '../index.html') + '?' + process.argv[2], { waitUntil: 'load' });
  await new Promise(r => setTimeout(r, 300));
  await page.screenshot({ path: process.argv[3] }); await browser.close();
})();
