# -*- coding: utf-8 -*-
"""img(メーカー別)/ の写真を Web 用に変換する。

  python tools/build_images.py            変換（既存の新しい出力はスキップ）
  python tools/build_images.py --force    すべて作り直す

やっていること
  0. img(メーカー別)/ を全部見て tools/works-map.json を作り直す
     ・先頭が「#」のフォルダ＝メーカー → その下の末端フォルダが1作品
     ・それ以外のフォルダ（HP など）＝サイト用の写真
  1. EXIF の向き（Orientation）を実際の回転として焼き込む
  2. EXIF / GPS / ICC などのメタデータを全部捨てる（自宅の位置情報が漏れないように）
  3. 長辺 1600px の WebP = 本体、長辺 400px の WebP = サムネイル を出力
  出力先: 作品    images/<作品ID>/01.webp, 01-t.webp, 02.webp, ...
          サイト  images/site/<ファイル名>.webp
"""
import json, os, re, sys, unicodedata
from collections import Counter
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "img(メーカー別)")
DST = os.path.join(ROOT, "images")
MAP = os.path.join(HERE, "works-map.json")

MAIN_EDGE, MAIN_Q = 1600, 80
THUMB_EDGE, THUMB_Q = 400, 72
FORCE = "--force" in sys.argv
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp"}
# 1つのギャラリーとしてまとめるフォルダ（「#」で始まらないもののうち）
ALBUMS = {"cabinet"}

# メーカーフォルダ名 → (表示名, IDの頭)
MAKER = {
    "#ASTRO": ("ASTRO", "astro"),
    "#Blue-Point": ("Blue-Point", "bluepoint"),
    "#HAZET": ("HAZET", "hazet"),
    "#KTC": ("KTC", "ktc"),
    "#Ko-ken": ("Ko-ken", "koken"),
    "#NEPROS": ("NEPROS", "nepros"),
    "#PB SWISS TOOLS": ("PB SWISS TOOLS", "pbswiss"),
    "#SIGNET": ("SIGNET", "signet"),
    "#Snap-on": ("Snap-on", "snapon"),
    "#TONE": ("TONE", "tone"),
    "#VESSEL": ("VESSEL", "vessel"),
    "#ViGOR (ビガー)": ("ViGOR", "vigor"),
    "#その他": ("汎用 / その他", "universal"),
    "#アストロプロダクツ": ("アストロプロダクツ", "astroproducts"),
}

# フォルダ名 → IDの一部。ここにない日本語はローマ字にできないので必ず足すこと
SLUG = {
    "インパクトソケット": "impact-socket", "クリップツール": "clip-tool",
    "ハンディリムーバーセット_ATP2015": "handy-remover-atp2015",
    "細軸ドライバー": "slim-driver", "電動ラチェット＿JTRE330": "power-ratchet-jtre330",
    "電動ラチェット": "power-ratchet", "T型スライドスピンハンドル": "t-slide-spin-handle",
    "エクステンションバー": "extension-bar", "ソケット（エクストラディープ）": "socket-extra-deep",
    "デュアルドライブT型ハンドル": "dual-drive-t-handle", "ナットグリップ": "nut-grip",
    "ナットグリップ（エクストラディープ）": "nut-grip-extra-deep",
    "フリーターンクロスレンチ": "free-turn-cross-wrench", "ブレーカーバー": "breaker-bar",
    "ヘックスビット": "hex-bit", "ラチェットハンドル": "ratchet-handle",
    "クイックスピンナ": "quick-spinner", "スライドヘッドハンドル": "slide-head-handle",
    "プラグレンチ": "plug-wrench", "ラチェットアダプター": "ratchet-adapter",
    "レンチ": "wrench", "コインドライバー": "coin-driver", "ドライバー": "driver",
    "ピックツール": "pick-tool", "ホースリムーバー": "hose-remover", "六角レンチ": "hex-key",
    "ソケットホルダー": "socket-holder", "ピンポンチ": "pin-punch", "やすり": "file",
    "デジタルトルクレンチ": "digital-torque-wrench", "トルクレンチ": "torque-wrench",
    "ネジ山修正ツール": "thread-repair-tool", "ハンドソー": "hand-saw",
    "プライバー": "pry-bar", "ラチェットドライバー": "ratchet-driver",
    "可変プライバー": "adjustable-pry-bar", "スナップオン＿シールリムーバー": "seal-remover",
    "スナップオン＿ソケットホルダー": "socket-holder",
    "V2941 フィンガーラチェット": "finger-ratchet-v2941",
    "$GRIP": "grip", "$プライヤーホルダー": "plier-holder",
    "$モンキーレンチホルダー": "adjustable-wrench-holder",
    # バリエーション
    "一体": "integrated", "別体": "separate", "壁掛け": "wall", "平置き": "flat",
    "幅広": "wide", "幅狭": "narrow", "加工": "mod", "locking": "locking",
    "イエロー": "yellow", "オレンジ": "orange", "グリーン": "green",
    "パープル": "purple", "ブラック": "black", "レッド": "red",
    "6.3sq": "6-3sq", "9.5sq": "9-5sq", "12.7sq": "12-7sq",
    "6.3sqセット": "set-6-3sq", "ショートソケット": "short", "ディープソケット": "deep",
    "セット": "set", "シャロー、セミディープ、ディープ": "shallow-semideep-deep",
    "45deg": "45deg", "high": "high",
    "エクストラロング": "extra-long", "マルチパーパス": "multi-purpose",
    "マルチポジション": "multi-position",
}

JA = {  # 作品名に使うときの言い換え
    "スナップオン＿シールリムーバー": "シールリムーバー",
    "スナップオン＿ソケットホルダー": "ソケットホルダー",
    "電動ラチェット＿JTRE330": "電動ラチェット JTRE330",
    "ハンディリムーバーセット_ATP2015": "ハンディリムーバーセット ATP2015",
    "$GRIP": "カスタムグリップ", "$プライヤーホルダー": "プライヤー",
    "V2941 フィンガーラチェット": "フィンガーラチェット V2941",
    "$モンキーレンチホルダー": "モンキーレンチ",
    "ソケット（エクストラディープ）": "ソケット エクストラディープ",
    "ナットグリップ（エクストラディープ）": "ナットグリップ エクストラディープ",
    "シャロー、セミディープ、ディープ": "シャロー/セミディープ/ディープ",
}

IS_MODEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _.＋+\-]*$")


def slug(s):
    if s in SLUG:
        return SLUG[s]
    t = unicodedata.normalize("NFKC", s).lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t or "item"


def sortkey(name):
    """全角数字も半角として並べ替える（０.jpg が先頭に来るように）。"""
    n = unicodedata.normalize("NFKC", name).lower()
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", n)]


def scan():
    """img(メーカー別)/ を見て (作品のリスト, サイト用写真のリスト) を返す。"""
    works, site = [], []
    for dirpath, dirnames, filenames in os.walk(SRC):
        dirnames.sort()
        imgs = sorted([f for f in filenames if os.path.splitext(f)[1].lower() in IMG_EXT],
                      key=sortkey)
        if not imgs:
            continue
        rel = os.path.relpath(dirpath, SRC).replace("\\", "/")
        parts = rel.split("/")

        # 先頭が「#」でないフォルダはサイト用の写真（作品ではない）
        if not parts[0].startswith("#"):
            if parts[0] in ALBUMS:
                # まとめて1つのギャラリーにする（images/<フォルダ名>/01.webp ...）
                for i, f in enumerate(imgs, 1):
                    site.append({"folder": rel, "file": f, "album": parts[0],
                                 "out": "%s/%02d.webp" % (parts[0], i),
                                 "thumb": "%s/%02d-t.webp" % (parts[0], i)})
            else:
                for f in imgs:
                    site.append({"folder": rel, "file": f, "album": "",
                                 "out": "site/%s.webp" % slug(os.path.splitext(f)[0]),
                                 "thumb": ""})
            continue

        maker_name, maker_slug = MAKER.get(parts[0], (parts[0].lstrip("#"), slug(parts[0].lstrip("#"))))
        tail = parts[1:]
        tool = JA.get(tail[0], tail[0]) if tail else ""
        variant = " / ".join(JA.get(p, p) for p in tail[1:])
        title = tool if (tool.endswith("ホルダー") or tool.endswith("グリップ")) else tool + "ホルダー"
        if variant:
            title += " " + variant
        model = " / ".join(p for p in tail
                           if IS_MODEL.match(p) and not re.match(r"^\d+(\.\d+)?sq$", p))
        notes = []
        skipped = [f for f in filenames if f not in imgs]
        if skipped:
            notes.append("非画像除外: " + ", ".join(skipped))
        if any(unicodedata.normalize("NFKC", f) != f for f in imgs):
            notes.append("全角数字あり")
        if len(imgs) == 1:
            notes.append("写真1枚のみ")
        works.append(dict(folder=rel, maker=maker_name,
                          id="-".join([maker_slug] + [slug(p) for p in tail]),
                          title=title, model=model, count=len(imgs),
                          main=imgs[0], files=imgs, note=" / ".join(notes)))

    order = [v[0] for v in MAKER.values()]
    works.sort(key=lambda r: (order.index(r["maker"]) if r["maker"] in order else 99, r["folder"]))

    dup = [k for k, v in Counter(r["id"] for r in works).items() if v > 1]
    if dup:
        raise SystemExit("作品IDが重複しています（SLUG に日本語フォルダ名を足してください）:\n  "
                         + "\n  ".join(dup))
    return works, site


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


def convert(src, outs, state):
    """outs = [(出力パス, 長辺, 品質), ...]。更新が要るときだけ変換する。"""
    if not FORCE and all(os.path.exists(p) and os.path.getmtime(p) >= os.path.getmtime(src)
                         for p, _, _ in outs):
        state["skipped"] += 1
        return
    with Image.open(src) as im0:
        orient = (im0.getexif() or {}).get(274, 1)
        im = ImageOps.exif_transpose(im0)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        if orient not in (1, 0, None):
            state["rotated"].append("%s (Orientation=%s)" % (os.path.relpath(src, SRC), orient))
        for path, edge, q in outs:
            save(fit(im, edge), path, q)
    state["done"] += 1


def main():
    works, site = scan()
    with open(MAP, "w", encoding="utf-8", newline="\n") as f:
        json.dump(works, f, ensure_ascii=False, indent=1)

    state = {"done": 0, "skipped": 0, "rotated": []}

    # --- 作品の写真 ---
    for w in works:
        out_dir = os.path.join(DST, w["id"])
        os.makedirs(out_dir, exist_ok=True)
        for i, name in enumerate(w["files"], 1):
            src = os.path.join(SRC, w["folder"].replace("/", os.sep), name)
            base = os.path.join(out_dir, "%02d" % i)
            convert(src, [(base + ".webp", MAIN_EDGE, MAIN_Q),
                          (base + "-t.webp", THUMB_EDGE, THUMB_Q)], state)
        keep = set()
        for i in range(1, len(w["files"]) + 1):
            keep.add("%02d.webp" % i)
            keep.add("%02d-t.webp" % i)
        for f in os.listdir(out_dir):
            if f not in keep:
                os.remove(os.path.join(out_dir, f))

    # --- サイト用の写真（工房写真・キャビネットのギャラリー） ---
    albums = {}
    for sp in site:
        d = os.path.dirname(sp["out"])
        os.makedirs(os.path.join(DST, d), exist_ok=True)
        src = os.path.join(SRC, sp["folder"].replace("/", os.sep), sp["file"])
        outs = [(os.path.join(DST, sp["out"].replace("/", os.sep)), MAIN_EDGE, MAIN_Q)]
        if sp["thumb"]:
            outs.append((os.path.join(DST, sp["thumb"].replace("/", os.sep)), THUMB_EDGE, THUMB_Q))
        convert(src, outs, state)
        if sp["album"]:
            albums[sp["album"]] = albums.get(sp["album"], 0) + 1
    # そのフォルダから消えた写真の出力を掃除
    for d in {os.path.dirname(sp["out"]) for sp in site}:
        keep = {os.path.basename(sp["out"]) for sp in site if os.path.dirname(sp["out"]) == d}
        keep |= {os.path.basename(sp["thumb"]) for sp in site
                 if sp["thumb"] and os.path.dirname(sp["thumb"]) == d}
        for f in os.listdir(os.path.join(DST, d)):
            if f not in keep:
                os.remove(os.path.join(DST, d, f))

    with open(os.path.join(HERE, "site-map.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"albums": albums,
                   "single": sorted(sp["out"] for sp in site if not sp["album"])},
                  f, ensure_ascii=False, indent=1)

    # 作品フォルダごと消えた場合の掃除
    ids = {w["id"] for w in works} | {"site"} | set(albums)
    for d in os.listdir(DST):
        p = os.path.join(DST, d)
        if os.path.isdir(p) and d not in ids:
            for f in os.listdir(p):
                os.remove(os.path.join(p, f))
            os.rmdir(p)

    total = sum(os.path.getsize(os.path.join(dp, f))
                for dp, _, fs in os.walk(DST) for f in fs)
    print("作品 %d 件 / 写真 %d 枚" % (len(works), sum(w["count"] for w in works)))
    if site:
        print("サイト用の写真 %d 枚: %s" % (len(site), ", ".join("images/" + s["out"] for s in site)))
    print("変換 %d 枚 / スキップ %d 枚" % (state["done"], state["skipped"]))
    print("images/ 合計 %.1f MB" % (total / 1024 / 1024))
    if state["rotated"]:
        print("\nEXIF の向きを焼き込んだ写真 %d 枚（仕上がりを確認してください）:" % len(state["rotated"]))
        for r in state["rotated"][:20]:
            print("  " + r)


if __name__ == "__main__":
    main()
