# -*- coding: utf-8 -*-
"""img(メーカー別)/ の写真を Web 用に変換する。

  python tools/build_images.py            変換（既存の新しい出力はスキップ）
  python tools/build_images.py --force    すべて作り直す

やっていること
  1. EXIF の向き（Orientation）を実際の回転として焼き込む
  2. EXIF / GPS / ICC などのメタデータを全部捨てる（自宅の位置情報が漏れないように）
  3. 長辺 1600px の WebP = 本体、長辺 400px の WebP = サムネイル を出力
  出力先: images/<作品ID>/01.webp, 01-t.webp, 02.webp, ...
"""
import json, os, sys, unicodedata
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "img(メーカー別)")
DST = os.path.join(ROOT, "images")
MAP = os.path.join(HERE, "works-map.json")

MAIN_EDGE, MAIN_Q = 1600, 80
THUMB_EDGE, THUMB_Q = 400, 72
FORCE = "--force" in sys.argv


def fit(im, edge):
    w, h = im.size
    if max(w, h) <= edge:
        return im.copy()
    s = edge / max(w, h)
    return im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)


def save(im, path, q):
    tmp = path + ".tmp"
    # 生のピクセルから作り直す → EXIF/GPS/ICC/XMP は一切引き継がれない
    out = Image.frombytes(im.mode, im.size, im.tobytes())
    out.save(tmp, "WEBP", quality=q, method=6, exif=b"", icc_profile=None, xmp=b"")
    os.replace(tmp, path)


def main():
    with open(MAP, encoding="utf-8") as f:
        works = json.load(f)

    done = skipped = 0
    rotated = []
    for w in works:
        out_dir = os.path.join(DST, w["id"])
        os.makedirs(out_dir, exist_ok=True)
        for i, name in enumerate(w["files"], 1):
            src = os.path.join(SRC, w["folder"].replace("/", os.sep), name)
            base = "%02d" % i
            main_p = os.path.join(out_dir, base + ".webp")
            thumb_p = os.path.join(out_dir, base + "-t.webp")
            if not FORCE and os.path.exists(main_p) and os.path.exists(thumb_p) \
                    and os.path.getmtime(main_p) >= os.path.getmtime(src):
                skipped += 1
                continue
            with Image.open(src) as im0:
                orient = (im0.getexif() or {}).get(274, 1)
                im = ImageOps.exif_transpose(im0)
                if im.mode not in ("RGB", "L"):
                    im = im.convert("RGB")
                if orient not in (1, 0, None):
                    rotated.append("%s/%s (Orientation=%s)" % (w["folder"], name, orient))
                save(fit(im, MAIN_EDGE), main_p, MAIN_Q)
                save(fit(im, THUMB_EDGE), thumb_p, THUMB_Q)
            done += 1
        # 不要になった出力を掃除
        keep = set()
        for i in range(1, len(w["files"]) + 1):
            keep.add("%02d.webp" % i)
            keep.add("%02d-t.webp" % i)
        for f in os.listdir(out_dir):
            if f not in keep:
                os.remove(os.path.join(out_dir, f))

    total = sum(os.path.getsize(os.path.join(dp, f))
                for dp, _, fs in os.walk(DST) for f in fs)
    print("変換 %d 枚 / スキップ %d 枚" % (done, skipped))
    print("images/ 合計 %.1f MB" % (total / 1024 / 1024))
    if rotated:
        print("\nEXIF の向きを焼き込んだ写真 %d 枚（念のため仕上がりを確認してください）:" % len(rotated))
        for r in rotated[:20]:
            print("  " + r)
        if len(rotated) > 20:
            print("  ... 他 %d 枚" % (len(rotated) - 20))


if __name__ == "__main__":
    main()
