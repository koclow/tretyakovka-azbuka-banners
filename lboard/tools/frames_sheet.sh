#!/bin/zsh
# frames_sheet.sh <video> <out.png> [times...] — контактный лист кадров из видео
v=$1; out=$2; shift 2; S=$(mktemp -d); i=0
for t in "$@"; do ffmpeg -y -hide_banner -loglevel error -ss $t -i "$v" -frames:v 1 -vf scale=640:-1 "$S/f_$i.png"; i=$((i+1)); done
python3 - "$S" "$out" "$@" <<'PY'
from PIL import Image, ImageDraw; import sys, os
S,out=sys.argv[1],sys.argv[2]; T=sys.argv[3:]
ims=[Image.open(f"{S}/f_{i}.png") for i in range(len(T))]
cols=2; rows=(len(ims)+1)//2; w=ims[0].width; h=ims[0].height
sheet=Image.new("RGB",(cols*(w+10),rows*(h+22)),(40,40,40)); d=ImageDraw.Draw(sheet)
for i,(im,t) in enumerate(zip(ims,T)):
    x=(i%cols)*(w+10); y=(i//cols)*(h+22); d.text((x+4,y+3),f"{t} с",fill=(230,230,230)); sheet.paste(im,(x,y+18))
sheet.save(out); print(out, sheet.size)
PY
