const puppeteer = require('puppeteer-core'); const path = require('path');
(async () => {
  const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const page = await browser.newPage(); const errs = [];
  page.on('pageerror', e => errs.push(e.message)); page.on('requestfailed', r => errs.push('FAIL ' + r.url().slice(-60)));
  for (const [w, h] of [[1440, 700], [375, 700]]) {
    await page.setViewport({ width: w, height: h });
    await page.goto('file://' + path.resolve(__dirname, '../../demo/page.html') + '?w=' + w + '&v=1', { waitUntil: 'load' });
    await new Promise(r => setTimeout(r, 4000));
    await page.screenshot({ path: process.argv[2] + '/demo_' + w + '.png' });
  }
  console.log('errors:', errs.length ? errs : 'none'); await browser.close();
})();
