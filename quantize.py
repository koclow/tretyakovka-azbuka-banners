"""Палитровое сжатие слоёв баннера.

Иллюстрация плоская, цветов в ней немного — 255-цветная палитра почти не врёт,
а вес падает вдвое-втрое. Альфа у слоёв двоичная (0 или 255), поэтому она
уезжает в один прозрачный индекс палитры, а не в отдельный канал.
"""
from PIL import Image
import numpy as np, os, sys, glob

def quantize(path, out=None, colors=255):
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    alpha = a[:, :, 3]
    rgb = Image.fromarray(a[:, :, :3], "RGB")
    pal = rgb.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE)
    idx = np.array(pal)
    if (alpha == 0).any():
        idx = idx.copy()
        idx[alpha == 0] = colors                      # последний индекс — прозрачный
        p = pal.getpalette()[: colors * 3] + [0, 0, 0]
        q = Image.fromarray(idx, "P")
        q.putpalette(p)
        q.info["transparency"] = colors
        out_img, kw = q, {"transparency": colors}
    else:
        out_img, kw = pal, {}
    out = out or path
    out_img.save(out, optimize=True, **kw)
    # контроль: сравниваем только видимые пиксели
    b = np.array(Image.open(out).convert("RGBA")).astype(int)
    m = alpha > 0
    d = np.abs(a.astype(int) - b)[:, :, :3][m]
    da = int(np.abs(a[:, :, 3].astype(int) - b[:, :, 3]).max())
    return d.max(), d.mean(), da

if __name__ == "__main__":
    tot_b = tot_a = 0
    for f in sorted(sys.argv[1:]):
        before = os.path.getsize(f)
        mx, mean, da = quantize(f)
        after = os.path.getsize(f)
        tot_b += before; tot_a += after
        print(f"{f.split('/')[-3]}/{os.path.basename(f):11s} {before/1024:6.1f}K → {after/1024:6.1f}K  maxRGB={mx:3d} mean={mean:.2f} alphaDiff={da}")
    print(f"итого {tot_b/1024:.0f}K → {tot_a/1024:.0f}K")
