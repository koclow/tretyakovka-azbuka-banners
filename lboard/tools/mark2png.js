// Строка маркировки в PNG с альфой шрифтом AzbukaVkusa (установлен на аймаке):
//   node mark2png.js jobs.json   — [{out, lines:[…], size(px CSS), lh(px CSS), scale, color}]
// Печатает размер картинки в CSS-пикселях — его и ставить в width/height креатива.
const puppeteer = require('puppeteer-core'); const fs = require('fs');
const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
(async () => {
  const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true, args: ['--font-render-hinting=none'] });
  const p = await b.newPage();
  for (const j of jobs) {
    const sc = j.scale || 3, lh = j.lh || Math.round(j.size * 1.2);
    await p.setViewport({ width: 1200, height: 200, deviceScaleFactor: sc });
    await p.setContent(`<style>html,body{margin:0;background:transparent}
      #t{display:inline-block;white-space:nowrap;font:${j.size}px/${lh}px AzbukaVkusa,Inter,sans-serif;color:${j.color||'#fff'};padding:0 1px}</style>
      <div id="t">${j.lines.join('<br>')}</div>`);
    await p.evaluate(() => document.fonts.ready);
    const r = await p.evaluate(() => { const b = document.getElementById('t').getBoundingClientRect(); return { w: Math.ceil(b.width), h: Math.ceil(b.height) }; });
    await p.screenshot({ path: j.out, type: 'png', omitBackground: true, clip: { x: 0, y: 0, width: r.w, height: r.h } });
    console.log(`${j.out}: ${r.w}x${r.h} css (${r.w*sc}x${r.h*sc} px), ${fs.statSync(j.out).size} B`);
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
