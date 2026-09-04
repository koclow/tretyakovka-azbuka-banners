#!/usr/bin/env python3
"""Загрузка папки на Яндекс.Диск и публикация ссылки.

    YD_TOKEN=… python3 ydisk_upload.py "<имя папки на Диске>" <локальная папка> [<подпапка на Диске>=<локальная папка> …]

Токен — только из окружения, в файлы и вывод не пишется.
"""
import os, sys, time, pathlib, subprocess, requests

API = "https://cloud-api.yandex.net/v1/disk"
H = {"Authorization": "OAuth " + os.environ["YD_TOKEN"]}

def mkdir(path):
    r = requests.put(f"{API}/resources", headers=H, params={"path": path})
    if r.status_code not in (201, 409): raise SystemExit(f"mkdir {path}: {r.status_code} {r.text[:200]}")

def upload(local: pathlib.Path, remote: str, tries=8):
    """Большие файлы шлём curl-ом: если скорость падает ниже 50 КБ/с на минуту — обрыв и новая попытка с новым href."""
    for attempt in range(1, tries + 1):
        r = requests.get(f"{API}/resources/upload", headers=H, params={"path": remote, "overwrite": "true"}, timeout=60); r.raise_for_status()
        href = r.json()["href"]
        t0 = time.time()
        res = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "-X", "PUT", "-T", str(local),
                              "--speed-limit", "51200", "--speed-time", "60", "--max-time", "3600", href], capture_output=True, text=True)
        code = res.stdout.strip()
        if res.returncode == 0 and code in ("201", "202"):
            mb = local.stat().st_size / 1048576; dt = max(time.time() - t0, 1)
            print(f"  ↑ {remote}  {mb:.1f} МБ за {dt:.0f} с ({mb/dt*1024:.0f} КБ/с)" + (f", попытка {attempt}" if attempt > 1 else ""), flush=True); return
        print(f"  ! {remote}: curl rc={res.returncode} http={code} {res.stderr.strip()[:80]} — попытка {attempt}", flush=True)
        time.sleep(15)
    raise SystemExit(f"upload {local}: не удалось за {tries} попыток")

root = "disk:/" + sys.argv[1]
mkdir(root)
for spec in sys.argv[2:]:
    sub, local = spec.split("=", 1)
    rpath = root + "/" + sub
    mkdir(rpath)
    for p in sorted(pathlib.Path(local).iterdir()):
        if p.name.startswith(".") or p.is_dir(): continue
        upload(p, rpath + "/" + p.name)
r = requests.put(f"{API}/resources/publish", headers=H, params={"path": root}); r.raise_for_status()
r = requests.get(f"{API}/resources", headers=H, params={"path": root, "fields": "public_url,name"}); r.raise_for_status()
print("ССЫЛКА:", r.json().get("public_url"))
