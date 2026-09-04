const puppeteer = require('puppeteer-core'); const path = require('path');
(async () => {
  const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const page = await browser.newPage(); await page.setViewport({ width: 1440, height: 250 });
  const url = 'file://' + path.resolve(__dirname, '../../creatives/desktop-illustration/index.html');
  await page.goto(url + '?at=1600', { waitUntil: 'load' });
  await page.screenshot({ path: process.argv[2] + '/dbg_a.png' });
  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({ path: process.argv[2] + '/dbg_b.png' });
  // без ?at — живой прогон, кадр через 1.6 с
  await page.goto(url, { waitUntil: 'load' }); await new Promise(r => setTimeout(r, 1600));
  await page.screenshot({ path: process.argv[2] + '/dbg_live1600.png' });
  await new Promise(r => setTimeout(r, 2500));
  await page.screenshot({ path: process.argv[2] + '/dbg_live4100.png' });
  await browser.close();
})();
