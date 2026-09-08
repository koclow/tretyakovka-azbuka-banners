#!/usr/bin/env python3
"""Композит «как у РБК»: их ролик (эфир, сжатие в окно, бегущая строка, поля) + наш L-board в L-области.

    python3 rbc_composite.py <ref.mp4> <banner.mov> <out.mp4>

Геометрия снята с ролика РБК от 07.09.2026 (1920×1080, 50 к/с, 12 с):
окно программы 599…1920 × 0…725, бегущая строка 96…1824 × 960…1044, поля: слева 0…96,
сверху 0…54 над колонкой баннера, снизу 1044…1080. Сжатие: кадры 52…70, разжатие: 530…548.
Баннер стартует с начала сжатия (кадр 52), как в их образце.
"""
import subprocess, sys, numpy as np
ref, banner, out = sys.argv[1:4]
W, H, FPS = 1920, 1080, 50
F0, SQ, F1, EX = 52, 18, 530, 18          # старт баннера, длина сжатия, старт разжатия, длина разжатия
WIN_LEFT, WIN_BOTTOM = 599, 725
TICK = (96, 960, 1824, 1044); TOP = 54; BOT = 1044; LEFT = 96
MATTE = np.array([131, 26, 30], np.uint8)
SQUEEZE = [(96, 1080), (96, 1080), (120, 1080), (150, 1080), (180, 1080), (210, 974), (240, 956), (270, 938), (300, 920),
           (330, 902), (360, 885), (390, 867), (420, 849), (450, 831), (480, 814), (510, 796), (539, 778), (570, 760), (599, 742)]
# кадры 52…70: (левый край окна, низ окна); последний элемент подменяется финальным окном 599×725 в steady-state
SQUEEZE[-1] = (599, 725); SQUEEZE[-2] = (570, 742)   # цвет красных полей РБК; в их кадре под полями просвечивал старый баннер

def reader(path):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
def frame(p):
    b = p.stdout.read(W * H * 3)
    return None if len(b) < W * H * 3 else np.frombuffer(b, np.uint8).reshape(H, W, 3)

r, b = reader(ref), reader(banner)
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", ref, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", out], stdin=subprocess.PIPE)
f = 0; used = 0
while True:
    T = frame(r)
    if T is None: break
    outf = T
    if F0 <= f < F1 + EX:
        B = frame(b)
        if B is not None:
            used += 1
            # прямоугольник программы по снятой с их ролика таблице (левый край 30 px/кадр, низ 18 px/кадр),
            # разжатие — зеркало сжатия; в переходах перекрываем ещё 2 px, чтобы не торчал край старого баннера
            if f < F0 + SQ: left, bottom = SQUEEZE[f - F0]; left -= 2; bottom += 2
            elif f >= F1: left, bottom = SQUEEZE[SQ - (f - F1)]; left -= 2; bottom += 2
            else: left, bottom = WIN_LEFT, WIN_BOTTOM
            outf = T.copy()
            # L-область баннера: колонка слева от программы и полоса под ней, до бегущей строки
            if left > LEFT: outf[TOP:TICK[1], LEFT:left] = B[TOP:TICK[1], LEFT:left]
            if bottom < TICK[1]: outf[bottom:TICK[1], left:W] = B[bottom:TICK[1], left:W]
            # поля — сплошным цветом: в их образце значки старого баннера торчали из-под строки и полей
            outf[:, :LEFT] = MATTE
            if left > LEFT: outf[:TOP, LEFT:left] = MATTE
            outf[BOT:, :] = MATTE
            outf[TICK[1]:TICK[3], TICK[2]:] = MATTE
    enc.stdin.write(outf.tobytes()); f += 1
enc.stdin.close(); enc.wait(); r.wait(); b.kill()
print(f"кадров: {f}, из баннера использовано: {used} → {out}")
