#!/usr/bin/env python3
"""Сборка отдаваемых файлов.

1. dist/*.html — по одному самодостаточному файлу на баннер: картинки уходят
   внутрь как data:URI, внешних запросов не остаётся.
2. dist/*.zip — архивы «html + assets», как их просит РБК (лимит 150 КБ).

    python3 build-standalone.py
"""
import base64, pathlib, re, zipfile

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

BANNERS = {
    "billboard-100x250": "billboard-100x250",
    "300x250": "banner-300x250",
    "680x250": "banner-680x250",
}
LIMIT_KB = 150

for folder, name in BANNERS.items():
    src = ROOT / "banners" / folder / "index.html"
    html = src.read_text(encoding="utf-8")

    def inline(m):
        data = (src.parent / "assets" / m.group(1)).read_bytes()
        return 'src="data:image/png;base64,%s"' % base64.b64encode(data).decode()

    single = DIST / f"{name}.html"
    single.write_text(re.sub(r'src="assets/([^"]+)"', inline, html), encoding="utf-8")

    archive = DIST / f"{name}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.write(src, "index.html")
        for a in sorted((src.parent / "assets").iterdir()):
            z.write(a, f"assets/{a.name}")

    kb = archive.stat().st_size / 1024
    mark = "ok" if kb <= LIMIT_KB else f"ПЕРЕВЕС, лимит {LIMIT_KB} КБ"
    print(f"{name}: архив {kb:5.1f} КБ ({mark}), одним файлом {single.stat().st_size/1024:5.1f} КБ")
