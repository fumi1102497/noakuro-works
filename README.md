# のあくろ工房 サイト

## 構成
```
index.html              ページ本体
css/style.css           デザイン（色は :root の変数で一括変更）
js/works.js             作品データ（WORKS 配列）★自動生成
js/main.js              画面の動き（フィルタ・モーダル・ギャラリー）
images/<作品ID>/        Web用の写真（WebP）★自動生成
img(メーカー別)/        写真の原本（1.7GB・push しない）
tools/works-data.json   作品の文章・型番 ← 手で直すのはここ
tools/works-map.json    作品IDと写真の対応 ★自動生成
tools/works-list.md     確認用の作品一覧 ★自動生成
tools/build_images.py   写真の変換（EXIF削除・WebP化）
tools/build_works.py    js/works.js の生成
CNAME.example           独自ドメイン名のひな形。ドメインが決まったら CNAME にリネームする
```

`js/works.js` と `images/` は自動生成なので直接編集しない。

## よくある作業

| やりたいこと | 直すファイル | 実行するコマンド |
|---|---|---|
| 作品名・説明・型番を直す | `tools/works-data.json` | `python tools/build_works.py` |
| 写真を足す・差し替える | `img(メーカー別)/` | `python tools/build_images.py` → `python tools/build_works.py` |
| 新しい作品を足す | 上の両方 | 上の両方 |
| 販売状態を変える | `tools/works-data.json` に `"status": "準備中"` | `python tools/build_works.py` |

個別の商品ページURLは載せない方針（売り切れ・再出品でURLが変わるため）。
作品詳細の「ショップで探す」はページ下部のショップ欄へ飛ぶ。

## まだ差し替えが必要なところ
1. **`.gitignore`**：`img(メーカー別)/`（写真の原本・1.7GB）を除外する。push するのは `images/` の85MBだけ
2. **工房写真**：`index.html` の `#about` 内、`WORKSHOP PHOTO` の枠
3. **CNAME**：ドメインを決めたら `CNAME.example` を `CNAME` にリネームして中身を書き換える（仮の `example.com` のまま置くと Pages がそれを独自ドメインとして扱ってしまうので、今は外してある）

## ローカルで確認
```
python -m http.server 8765
```
→ http://localhost:8765

## GitHub Pages で公開
1. GitHub で新しいリポジトリを作成（Public）
2. このフォルダの中身を push（`img(メーカー別)/` は `.gitignore` で除外する）
3. Settings → Pages → Source:「Deploy from a branch」→ `main` / `/(root)` を選んで Save
4. `https://ユーザー名.github.io/リポジトリ名/` で表示を確認

## 独自ドメイン
1. ドメインを取得（お名前.com、Cloudflare、Squarespace など）
2. DNS 設定
   - `www.example.com` で使う → CNAME レコード：`www` → `ユーザー名.github.io`
   - `example.com`（apex）で使う → A レコード 4つ：
     `185.199.108.153` / `185.199.109.153` / `185.199.110.153` / `185.199.111.153`
3. Settings → Pages → Custom domain にドメインを入力 → DNS 反映後「Enforce HTTPS」にチェック
4. 事前に Settings → Pages の「Verified domains」でドメイン認証しておくと乗っ取り対策になる

※ DNS の値は変わることがあるので、設定時は GitHub 公式ドキュメント
「Managing a custom domain for your GitHub Pages site」で最新値を確認してください。
