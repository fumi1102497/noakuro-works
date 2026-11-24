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
tools/cabinet-data.json キャビネット収納イメージの説明文 ← 手で直す
tools/site-map.json     サイト用写真の一覧 ★自動生成
tools/works-map.json    作品IDと写真の対応 ★自動生成
tools/works-list.md     確認用の作品一覧 ★自動生成
tools/build_images.py   写真の変換（EXIF削除・WebP化）
tools/build_works.py    js/works.js の生成
CNAME                   独自ドメイン名（noakuro.com）。消すと github.io のURLに戻る
```

`js/works.js` と `images/` は自動生成なので直接編集しない。

## よくある作業

| やりたいこと | 直すファイル | 実行するコマンド |
|---|---|---|
| 作品名・説明・型番を直す | `tools/works-data.json` | `python tools/build_works.py` |
| 写真を足す・差し替える | `img(メーカー別)/` | `python tools/build_images.py` → `python tools/build_works.py` |
| 新しい作品を足す | 上の両方 | 上の両方 |
| サイト用の写真を変える | `img(メーカー別)/HP/` | `python tools/build_images.py` |
| 収納イメージの写真を変える | `img(メーカー別)/cabinet/` | `python tools/build_images.py` → `python tools/build_works.py` |
| 収納イメージの説明文 | `tools/cabinet-data.json` | `python tools/build_works.py` |
| 販売状態を変える | `tools/works-data.json` に `"status": "準備中"` | `python tools/build_works.py` |

個別の商品ページURLは載せない方針（売り切れ・再出品でURLが変わるため）。
作品詳細の「ショップで探す」はページ下部のショップ欄へ飛ぶ。

## 公開先

- リポジトリ: https://github.com/fumi1102497/noakuro-works
- 公開URL: **https://noakuro.com**（`www.` や `fumi1102497.github.io/noakuro-works/` からも転送される）

更新は `git add -A && git commit -m "..." && git push` だけ。1〜2分で反映される。

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

## 独自ドメイン（設定済み）
お名前.com で `noakuro.com` を取得し、下記の通り設定済み。

- DNS（お名前.com）
  - apex `noakuro.com` → A レコード 4つ：
    `185.199.108.153` / `185.199.109.153` / `185.199.110.153` / `185.199.111.153`
  - `www` → CNAME レコード：`fumi1102497.github.io`
- GitHub → Settings → Pages
  - Custom domain: `noakuro.com`（リポジトリ直下の `CNAME` ファイルはこの欄から作られる）
  - Enforce HTTPS: ON
  - Verified domains: 認証済み（乗っ取り対策）

`http://` も `www.` も `fumi1102497.github.io/noakuro-works/` も、すべて `https://noakuro.com/` に転送される。

**`CNAME` ファイルを消すと独自ドメインが外れる。** 自動生成ではないので、ビルドスクリプトで消えることはない。

※ DNS の値は変わることがあるので、設定し直すときは GitHub 公式ドキュメント
「Managing a custom domain for your GitHub Pages site」で最新値を確認すること。
