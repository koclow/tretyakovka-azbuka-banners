#!/usr/bin/env python3
"""Сборка и проверка отдаваемых файлов по ТТ РБК (TT_RU_v7.08.26.xlsx, лист «HTML»).

1. dist/<name>.zip — плоский архив: index.html и файлы рядом, без подпапок.
2. dist/<name>.html — один самодостаточный файл (картинки data:URI) для витрины.
3. Проверка каждого архива по пунктам ТТ; при нарушении сборка падает.
4. «Отправка РБК/» — папка для отправки: 4 архива + 4 заглушки + README.txt.

    python3 build-standalone.py
"""
import base64, pathlib, re, shutil, sys, zipfile
from PIL import Image

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"; DIST.mkdir(exist_ok=True)
SEND = ROOT / "Отправка РБК"

# имя папки → (имя файла на отправку, заглушка, размер заглушки, лимит заглушки КБ)
BANNERS = {
    "desktop-illustration": ("billboard_1_illustration", (680, 250), 85),
    "desktop-photo":        ("billboard_2_photo",        (680, 250), 85),
    "mobile-woman":         ("mobile_1_woman",           (300, 250), 65),
    "mobile-man":           ("mobile_2_man",             (300, 250), 65),
    "square-plain":         (None,                       (300, 250), 65),   # запасной, не отправляется
}
ZIP_LIMIT_KB = 150            # по письму заказчика (в общих ТТ — 300)
HTML_LIMIT = 65000            # байт
FILE_LIMIT_KB = 300
ALLOWED = {".css", ".js", ".html", ".gif", ".png", ".jpg", ".jpeg", ".mp4"}
NAME_RE = re.compile(r"^[A-Za-z0-9_]+\.[a-z0-9]+$")

def check(folder: pathlib.Path, html: str, archive: pathlib.Path, fb, fb_size, fb_limit):
    errs = []
    files = sorted(p for p in folder.iterdir() if p.name != ".DS_Store")
    if any(p.is_dir() for p in files): errs.append("подпапки в проекте запрещены")
    htmls = [p for p in files if p.suffix == ".html"]
    if len(htmls) != 1: errs.append(f"должен быть ровно один .html, найдено {len(htmls)}")
    if len(files) > 50: errs.append(f"файлов {len(files)} > 50")
    for p in files:
        if p.suffix.lower() not in ALLOWED: errs.append(f"тип не разрешён: {p.name}")
        if not NAME_RE.match(p.name): errs.append(f"имя не по правилу [A-Za-z0-9_]: {p.name}")
        if p.stat().st_size > FILE_LIMIT_KB * 1024: errs.append(f"{p.name} тяжелее {FILE_LIMIT_KB} КБ")
    hb = len(html.encode("utf-8"))
    if hb > HTML_LIMIT: errs.append(f"index.html {hb} байт > {HTML_LIMIT}")
    for m in re.finditer(r'(?:src|href)="([^"]+)"', html):
        u = m.group(1)
        if u.startswith("%"): continue                     # макросы РБК
        if "/" in u or u.startswith("."): errs.append(f"путь с папкой или относительный: {u}")
        elif not (folder / u).exists(): errs.append(f"ссылка на отсутствующий файл: {u}")
    if ".svg" in html or ".json" in html: errs.append("ссылки на svg/json — не поддерживаются")
    if "%banner.reference_mrc_user1%" not in html: errs.append("нет ссылки-клика с макросом %banner.reference_mrc_user1%")
    if not re.search(r"<a [^>]*target=\"%banner.target%\"", html): errs.append("у ссылки нет target=%banner.target%")
    for m in re.finditer(r"function\s+([^\s(]+)|var\s+([A-Za-z_$][\w$]*)", html):
        nm = m.group(1) or m.group(2)
        if not re.match(r"^[A-Za-z_$][\w$]*$", nm): errs.append(f"имя функции/переменной не латиницей: {nm}")
    zk = archive.stat().st_size / 1024
    if zk > ZIP_LIMIT_KB: errs.append(f"архив {zk:.1f} КБ > {ZIP_LIMIT_KB}")
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        if any("/" in n for n in names): errs.append("в архиве есть подпапки")
        if "index.html" not in names: errs.append("в архиве нет index.html в корне")
    if fb is not None:
        if not fb.exists(): errs.append(f"нет заглушки {fb.name}")
        else:
            im = Image.open(fb)
            if im.size != fb_size: errs.append(f"заглушка {fb.name} {im.size}, нужно {fb_size}")
            if fb.stat().st_size > fb_limit * 1024: errs.append(f"заглушка {fb.name} тяжелее {fb_limit} КБ")
            if fb.suffix.lower() not in (".jpg", ".jpeg", ".gif", ".png"): errs.append(f"заглушка не jpg/gif: {fb.name}")
    return errs, zk, hb

if SEND.exists(): shutil.rmtree(SEND)
SEND.mkdir()
failed = False
lines = []
for folder, (send_name, fb_size, fb_limit) in BANNERS.items():
    src = ROOT / "creatives" / folder
    html = (src / "index.html").read_text(encoding="utf-8")

    def inline(m):
        name = m.group(1); data = (src / name).read_bytes()
        mime = "image/jpeg" if name.endswith(".jpg") else "image/png"
        return 'src="data:%s;base64,%s"' % (mime, base64.b64encode(data).decode())
    (DIST / f"{folder}.html").write_text(re.sub(r'src="([^"%]+)"', inline, html), encoding="utf-8")

    archive = DIST / f"{folder}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for a in sorted(src.iterdir()):
            if a.name != ".DS_Store": z.write(a, a.name)

    fb = ROOT / "fallback" / f"{folder}.jpg"
    errs, zk, hb = check(src, html, archive, fb, fb_size, fb_limit)
    status = "ok" if not errs else "ОШИБКИ: " + "; ".join(errs)
    print(f"{folder:22s} архив {zk:6.1f} КБ, html {hb:5d} Б, заглушка {fb.stat().st_size/1024:5.1f} КБ — {status}")
    if errs: failed = True
    if send_name and not errs:
        shutil.copy(archive, SEND / f"{send_name}.zip")
        shutil.copy(fb, SEND / f"{send_name}_{fb_size[0]}x{fb_size[1]}.jpg")
        lines.append(f"{send_name}.zip — {zk:.0f} КБ; заглушка {send_name}_{fb_size[0]}x{fb_size[1]}.jpg — {fb.stat().st_size/1024:.0f} КБ")

(SEND / "README.txt").write_text("""Азбука вкуса × Третьяковская галерея — HTML5-баннеры для РБК

Слоты:
  billboard_1_illustration — Billboard 100%×250, десктоп, первый экран (иллюстрация)
  billboard_2_photo        — Billboard 100%×250, десктоп, второй по доскроллу (фото)
  mobile_1_woman           — Mobile 300×250, первый экран
  mobile_2_man             — Mobile 300×250, второй по доскроллу

К каждому архиву — статичная заглушка (jpg): 680×250 для билбордов, 300×250 для мобильных.

Архивы плоские (index.html и файлы рядом), файлов не больше 11, форматы html/png/jpg.
Клик — по макросу %banner.reference_mrc_user1% с target=%banner.target% (лист «HTML» ТТ).
Билборды тянутся от 680 до 1920+ px, фон #184936 (при неполном растяжении поля заливаются им).
Анимация около 3 с, затем статичный финальный кадр; звука и внешних запросов нет.

""" + "\n".join(lines) + "\n", encoding="utf-8")
print("→", SEND, "(" + str(len(lines)) + " архива)")
sys.exit(1 if failed else 0)
