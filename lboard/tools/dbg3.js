const puppeteer = require('puppeteer-core'); const path = require('path');
const url = 'file://' + path.resolve(__dirname, '../../creatives/desktop-illustration/index.html');
async function run(label, args, useRaf, S) {
  const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true, args });
  const page = await browser.newPage(); await page.setViewport({ width: 1440, height: 250, deviceScaleFactor: 1 });
  for (const t of [0, 1600, 3600]) {
    await page.goto(url + '?at=' + t, { waitUntil: 'load' });
    await new Promise(r => setTimeout(r, 300));
    if (useRaf) await page.evaluate(() => new Promise(r => { document.body.style.outline = '1px solid transparent'; requestAnimationFrame(() => requestAnimationFrame(r)); }));
    await page.screenshot({ path: `${S}/v_${label}_${t}.png`, clip: { x: 0, y: 0, width: 1440, height: 250 } });
  }
  await browser.close();
}
(async () => {
  const S = process.argv[2];
  await run('A_flag', ['--force-device-scale-factor=1'], false, S);
  await run('B_noflag', [], false, S);
  await run('C_raf', ['--force-device-scale-factor=1'], true, S);
})();
