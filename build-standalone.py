#!/usr/bin/env python3
"""Собирает баннеры в одиночные HTML-файлы: картинки уходят внутрь как data:URI.
Такой файл можно отдать в рекламную систему одним куском.

    python3 build-standalone.py   →  dist/banner-680x250.html, dist/banner-300x250.html
"""
import base64, pathlib, re

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

for size in ("680x250", "300x250"):
    src = ROOT / "banners" / size / "index.html"
    html = src.read_text(encoding="utf-8")

    def inline(m):
        name = m.group(1)
        data = (src.parent / "assets" / name).read_bytes()
        return 'src="data:image/png;base64,%s"' % base64.b64encode(data).decode()

    html = re.sub(r'src="assets/([^"]+)"', inline, html)
    out = DIST / f"banner-{size}.html"
    out.write_text(html, encoding="utf-8")
    print(f"{out.relative_to(ROOT)} — {out.stat().st_size/1024:.0f} КБ")
