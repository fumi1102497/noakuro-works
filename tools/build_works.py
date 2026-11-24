# -*- coding: utf-8 -*-
"""tools/works-data.json（文章）と tools/works-map.json（写真）を合わせて js/works.js を作る。

  python tools/build_works.py

- 作品の文章・型番・カテゴリを直す → tools/works-data.json
- 写真を足した／減らした       → python tools/build_images.py（works-map.json も作り直す）
- js/works.js は自動生成なので直接編集しない
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "js", "works.js")

# 「対応メーカー」欄に出す順番（ここにないメーカーは末尾に追加される）
MAKER_ORDER = [
    "Snap-on", "Ko-ken", "KTC", "NEPROS", "PB SWISS TOOLS", "SIGNET",
    "Blue-Point", "HAZET", "TONE", "VESSEL", "ViGOR",
    "ASTRO", "アストロプロダクツ", "汎用 / その他",
]

CATEGORIES = [
    ("all",       "すべて"),
    ("ratchet",   "ラチェットハンドル"),
    ("extension", "エクステンションバー"),
    ("socket",    "ソケット"),
    ("driver",    "ドライバー"),
    ("wrench",    "レンチ"),
    ("torque",    "トルクレンチ"),
    ("plier",     "プライヤー"),
    ("prybar",    "プライバー"),
    ("grip",      "グリップ"),
    ("hand",      "その他"),    
]

# 全作品に共通の注意書き（モーダル下部に出す）
COMMON_NOTES = [
    "工具は付属しません（ホルダー本体のみ）",
    "カラーは全16色から選べます",
    "サイズ変更・カラー指定は出品ページのコメントからご相談ください",
]


def js_str(s):
    return json.dumps(s, ensure_ascii=False)


def write_list(photos, meta, default_status, order):
    """確認用の一覧 tools/works-list.md を書き出す。"""
    path = os.path.join(HERE, "works-list.md")
    rows = sorted(photos, key=lambda p: (order.get(p["maker"], 99), p["folder"]))
    labels = dict(CATEGORIES)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# 作品一覧（確認用）\n\n")
        f.write("`python tools/build_works.py` が自動生成します。直接編集しないでください。\n")
        f.write("文章・型番を直すのは `tools/works-data.json` です。\n\n")
        f.write("全 %d 作品 / 写真 %d 枚\n" % (len(rows), sum(p["count"] for p in photos)))
        cur = None
        for i, p in enumerate(rows, 1):
            w = meta[p["id"]]
            if p["maker"] != cur:
                cur = p["maker"]
                f.write("\n## %s\n\n| # | 作品名 | 対応 | カテゴリ | 状態 | 枚数 | ID | 原本フォルダ |\n"
                        "|---|---|---|---|---|---|---|---|\n" % cur)
            f.write("| %d | %s | %s | %s | %s | %d | `%s` | `%s` |\n" % (
                i, w["title"], w["target"], labels.get(w["category"], w["category"]),
                w.get("status", default_status), p["count"], p["id"],
                "/".join(p["folder"].split("/")[1:]) or p["folder"]))


def cabinet_js():
    """キャビネット収納イメージ（img(メーカー別)/cabinet/）を JS の配列にする。"""
    site_p = os.path.join(HERE, "site-map.json")
    data_p = os.path.join(HERE, "cabinet-data.json")
    if not (os.path.exists(site_p) and os.path.exists(data_p)):
        return "const CABINET = { lead: \"\", shots: [] };"
    n = json.load(open(site_p, encoding="utf-8")).get("albums", {}).get("cabinet", 0)
    d = json.load(open(data_p, encoding="utf-8"))
    caps = d.get("captions", {})
    shots = [{"image": "images/cabinet/%02d.webp" % i,
              "thumb": "images/cabinet/%02d-t.webp" % i,
              "caption": caps.get("%02d" % i, "")} for i in range(1, n + 1)]
    missing = [s["image"] for s in shots if not s["caption"]]
    if missing:
        print("（説明文のない写真 %d 枚：tools/cabinet-data.json に足してください）" % len(missing))
    return "const CABINET = %s;" % json.dumps({"lead": d.get("lead", ""), "shots": shots},
                                              ensure_ascii=False)


def main():
    data = json.load(open(os.path.join(HERE, "works-data.json"), encoding="utf-8"))
    photos = json.load(open(os.path.join(HERE, "works-map.json"), encoding="utf-8"))
    meta = data["works"]
    default_status = data.get("_default_status", "販売中")

    missing = [p["id"] for p in photos if p["id"] not in meta]
    if missing:
        raise SystemExit("works-data.json に未登録の作品があります:\n  " + "\n  ".join(missing))

    cat_keys = {k for k, _ in CATEGORIES}
    order = {m: i for i, m in enumerate(MAKER_ORDER)}

    entries = []
    for p in sorted(photos, key=lambda p: (order.get(p["maker"], 99), p["folder"])):
        w = meta[p["id"]]
        if w["category"] not in cat_keys:
            raise SystemExit("不明なカテゴリ %r（%s）" % (w["category"], p["id"]))
        images = ["images/%s/%02d.webp" % (p["id"], i) for i in range(1, p["count"] + 1)]
        thumbs = [s.replace(".webp", "-t.webp") for s in images]
        makers = [{"maker": mk, "model": md} for mk, md in w["makers"]]
        entries.append(
            "  {\n"
            "    id: %s,\n"
            "    makers: %s,\n"
            "    title: %s,\n"
            "    category: %s,\n"
            "    status: %s,\n"
            "    target: %s,\n"
            "    summary: %s,\n"
            "    specs: %s,\n"
            "    image: %s,\n"
            "    thumb: %s,\n"
            "    images: %s,\n"
            "    thumbs: %s\n"
            "  }" % (
                js_str(p["id"]),
                json.dumps(makers, ensure_ascii=False),
                js_str(w["title"]),
                js_str(w["category"]),
                js_str(w.get("status", default_status)),
                js_str(w["target"]),
                js_str(w["summary"]),
                json.dumps(w["specs"], ensure_ascii=False),
                js_str(images[0]),
                js_str(thumbs[0]),
                json.dumps(images, ensure_ascii=False),
                json.dumps(thumbs, ensure_ascii=False),
            )
        )

    out = [
        "/* ============================================================",
        "   作品データ — tools/build_works.py が自動生成します。",
        "   直接編集しないでください。",
        "     文章・型番・カテゴリ → tools/works-data.json",
        "     写真               → img(メーカー別)/ ＋ tools/build_images.py",
        "     キャビネットの説明文 → tools/cabinet-data.json",
        "   ============================================================ */",
        "const WORKS = [",
        ",\n".join(entries),
        "];",
        "",
        "const MAKER_ORDER = %s;" % json.dumps(MAKER_ORDER, ensure_ascii=False),
        "",
        "const CATEGORIES = [",
        ",\n".join('  { key: %s, label: %s }' % (js_str(k), js_str(v)) for k, v in CATEGORIES),
        "];",
        "",
        "const COMMON_NOTES = %s;" % json.dumps(COMMON_NOTES, ensure_ascii=False),
        "",
        cabinet_js(),
        "",
    ]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))

    write_list(photos, meta, default_status, order)

    print("js/works.js を書き出しました：%d 作品 / 写真 %d 枚"
          % (len(entries), sum(p["count"] for p in photos)))
    from collections import Counter
    for mk, n in sorted(Counter(p["maker"] for p in photos).items(),
                        key=lambda x: order.get(x[0], 99)):
        print("  %-18s %3d 作品" % (mk, n))


if __name__ == "__main__":
    main()
