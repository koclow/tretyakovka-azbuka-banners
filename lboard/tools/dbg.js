const puppeteer = require('puppeteer-core'); const path = require('path');
(async () => {
  const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const page = await browser.newPage(); page.on('pageerror', e => console.log('PAGEERROR', e.message)); page.on('console', m => console.log('CONSOLE', m.text()));
  await page.setViewport({ width: 1440, height: 250 });
  const url = 'file://' + path.resolve(__dirname, '../../creatives/desktop-illustration/index.html');
  await page.goto(url + '?at=1600', { waitUntil: 'load' });
  const r = await page.evaluate(() => {
    const c = document.getElementById('cr');
    const anims = document.getAnimations().map(a => ({ n: a.animationName, t: a.currentTime, ps: a.playState, el: a.effect.target.className && String(a.effect.target.className).slice(0, 20) }));
    const op = s => getComputedStyle(document.querySelector(s)).opacity;
    return { cls: c.className, anims, horse: op('.horse'), w1: op('.wide .w1'), badge: op('.badge'), lnk: op('.lnk') };
  });
  console.log(JSON.stringify(r, null, 1));
  await browser.close();
})();
