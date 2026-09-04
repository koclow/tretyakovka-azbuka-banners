// node svg2png.js <svg> <out.png> <widthPx>  — рендер SVG в PNG с альфой через Chrome
const puppeteer = require('puppeteer-core');
const fs = require('fs'), path = require('path');
const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')); // [{svg,out,w}]
(async () => {
  const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true, args: ['--force-device-scale-factor=1'] });
  const page = await browser.newPage();
  for (const j of jobs) {
    const svg = fs.readFileSync(j.svg, 'utf8');
    const m = /viewBox="([\d.\s-]+)"/.exec(svg); const vb = m[1].trim().split(/\s+/).map(Number);
    const h = Math.round(j.w * vb[3] / vb[2]);
    await page.setViewport({ width: j.w, height: h, deviceScaleFactor: 1 });
    await page.setContent(`<!doctype html><style>html,body{margin:0;background:transparent}img{display:block;width:${j.w}px;height:${h}px}</style><img src="data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}">`);
    await page.evaluate(() => new Promise(r => { const i = document.querySelector('img'); i.complete ? r() : i.onload = r; }));
    await page.screenshot({ path: j.out, type: 'png', omitBackground: true, clip: { x: 0, y: 0, width: j.w, height: h } });
    console.log(`${j.out} ${j.w}x${h} ${fs.statSync(j.out).size} B`);
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
