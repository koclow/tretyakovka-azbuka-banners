// Заглушки: финальный кадр (?static) каждого креатива → JPEG в fallback/.
//   node fallback.js — снимает в 2×, уменьшает Lanczos-ом, качество подбирает под лимит ТТ.
const puppeteer = require('puppeteer-core'); const path = require('path'); const { execFileSync } = require('child_process');
const ROOT = path.resolve(__dirname, '../..');
const SET = { 'desktop-illustration': [680, 250, 85], 'desktop-photo': [680, 250, 85], 'mobile-woman': [300, 250, 65], 'mobile-man': [300, 250, 65] };
(async () => {
  const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true, args: ['--font-render-hinting=none'] });
  const p = await b.newPage();
  for (const [n, [w, h, lim]] of Object.entries(SET)) {
    await p.setViewport({ width: w, height: h, deviceScaleFactor: 2 });
    await p.goto('file://' + path.join(ROOT, 'creatives', n, 'index.html') + '?static', { waitUntil: 'load' });
    await new Promise(r => setTimeout(r, 400));
    const png = `/tmp/fb_${n}.png`; await p.screenshot({ path: png });
    execFileSync('python3', ['-c', `
from PIL import Image; import io
im = Image.open('${png}').convert('RGB').resize((${w}, ${h}), Image.LANCZOS)
for q in range(92, 60, -2):
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=q, optimize=True, subsampling=0)
    if buf.tell() <= ${lim} * 1024: break
open('${path.join(ROOT, 'fallback', n + '.jpg')}', 'wb').write(buf.getvalue()); print('${n}', q, buf.tell())`], { stdio: 'inherit' });
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
