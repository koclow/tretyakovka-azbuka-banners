// Рендер HTML-анимации в кадры → ffmpeg → ProRes 4444 MOV.
// node render.js <file.html> <seconds> <out.mov|out.mp4> [fps=50] [alpha=0] [query, напр. v=B&overlay]
const puppeteer = require('puppeteer-core');
const { spawn } = require('child_process');
const path = require('path');
const [,, html, secArg, out, fpsArg = '50', alphaArg = '0', query = ''] = process.argv;
const sec = +secArg, fps = +fpsArg, alpha = alphaArg === '1';
const W = 1920, H = 1080, N = Math.round(sec * fps);
(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true, args: ['--hide-scrollbars', '--force-device-scale-factor=1', '--disable-gpu-vsync', '--font-render-hinting=none', '--allow-file-access-from-files']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(html) + '?render' + (query ? '&' + query : ''), { waitUntil: 'load' });
  await page.evaluate(async () => { if (document.fonts) await document.fonts.ready; });
  await page.evaluate(() => window.lbStart && window.lbStart());
  const mp4 = /\.mp4$/i.test(out);
  const codec = mp4
    ? ['-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart']
    : ['-c:v', 'prores_ks', '-profile:v', '4', '-pix_fmt', alpha ? 'yuva444p10le' : 'yuv444p10le', '-vendor', 'apl0'];
  const ff = spawn('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    ...codec, '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-r', String(fps), out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let i = 0; i < N; i++) {
    const t = i * 1000 / fps;
    await page.evaluate(t => { document.getAnimations().forEach(a => { a.pause(); a.currentTime = t; }); }, t);
    const buf = await page.screenshot({ type: 'png', omitBackground: alpha, clip: { x: 0, y: 0, width: W, height: H } });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 100 === 0) process.stderr.write(`frame ${i}/${N} ${((Date.now() - t0) / 1000).toFixed(1)}s\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log(`done ${N} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s → ${out}`);
})().catch(e => { console.error(e); process.exit(1); });
