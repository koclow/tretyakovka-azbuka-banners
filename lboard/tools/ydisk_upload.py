#!/usr/bin/env python3
"""Загрузка папки на Яндекс.Диск и публикация ссылки.

    YD_TOKEN=… python3 ydisk_upload.py "<имя папки на Диске>" <локальная папка> [<подпапка на Диске>=<локальная папка> …]

Токен — только из окружения, в файлы и вывод не пишется.
"""
import os, sys, pathlib, urllib.parse, requests

API = "https://cloud-api.yandex.net/v1/disk"
H = {"Authorization": "OAuth " + os.environ["YD_TOKEN"]}

def mkdir(path):
    r = requests.put(f"{API}/resources", headers=H, params={"path": path})
    if r.status_code not in (201, 409): raise SystemExit(f"mkdir {path}: {r.status_code} {r.text[:200]}")

def upload(local: pathlib.Path, remote: str):
    r = requests.get(f"{API}/resources/upload", headers=H, params={"path": remote, "overwrite": "true"}); r.raise_for_status()
    href = r.json()["href"]
    with open(local, "rb") as f:
        u = requests.put(href, data=f)
    if u.status_code not in (201, 202): raise SystemExit(f"upload {local}: {u.status_code}")
    print(f"  ↑ {remote}  {local.stat().st_size/1048576:.1f} МБ")

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
