// node still.js <query> <out.png> — стоп-кадр сцены 1920×1080
const puppeteer = require('puppeteer-core'); const path = require('path');
(async () => {
  const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true, args: ['--force-device-scale-factor=1', '--allow-file-access-from-files', '--font-render-hinting=none'] });
  const page = await browser.newPage(); await page.setViewport({ width: 1920, height: 1080 });
  await page.goto('file://' + path.resolve(__dirname, '../index.html') + '?' + process.argv[2], { waitUntil: 'load' });
  await new Promise(r => setTimeout(r, 300));
  await page.screenshot({ path: process.argv[3] }); await browser.close();
})();
