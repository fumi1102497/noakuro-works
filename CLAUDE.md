# のあくろ工房 ホームページ — 作業メモ

3Dプリント製の工具ホルダーを紹介するサイト。作品を見てもらい、メルカリ・ヤフオクでの購入・受注につなげるのが目的。
GitHub Pages ＋ 独自ドメイン **https://noakuro.com** で公開中。

---

## 1. サイトの基本方針

| 項目 | 内容 |
|---|---|
| 工房名 | のあくろ工房（ロゴ下の英字は仮で `NOAKURO 3D PRINT WORKS`） |
| 目的 | 作品紹介 → メルカリ・ヤフオクの**出品者ページ**へ誘導。カスタム相談は出品ページのコメントで受ける |
| 公開先 | https://noakuro.com （GitHub Pages。静的サイトでサーバー処理なし） |
| 構成 | 素のHTML / CSS / JavaScript（ビルドツールなし。写真とデータの生成だけ Python） |
| デザイン | 工房・工具箱をイメージしたダーク＋オレンジ（`--accent: #ff5a1f`）。見出しは Zen Kaku Gothic New、英数字は JetBrains Mono |

### 工房の情報（サイトに載せている内容）
- プリンタ：**6台**（Creality K1 SE ×3・K1C ×1・K2・K2 Pro）
- 設計：**OpenSCAD / FreeCAD**（パラメトリック設計なので寸法変更が得意）
- 発送：**ネコポス・クリックポスト**（厚み30mm以内）、それを超える場合は宅急便コンパクト
- 素材：PLA / PETG / ABS / TPU を作品ごとに使い分け

### ショップリンク（スマホでアプリを開く）

ページ下部の「ご購入はこちら」は `js/main.js` の末尾で作り替えている。

- **Android**：`intent://…#Intent;package=…;S.browser_fallback_url=…;end` に書き換える。
  アプリが入っていればアプリ、無ければ `browser_fallback_url`（＝元のURL）でブラウザが開く
  （メルカリ `com.kouzoh.mercari` / ヤフオク `jp.co.yahoo.android.yauction`）
- **iOS**：ユニバーサルリンク任せ。ただし別タブで開くとアプリに渡らないことがあるので `target="_blank"` を外している
- **PC**：何もしない（別タブでブラウザが開く）

### 出品URLの方針
**個別の商品ページURLはサイトに載せない。** 売り切れ・再出品でURLが頻繁に変わり、保守が追いつかないため。
作品詳細の「ショップで探す」ボタンは、ページ下部のショップ欄（出品者ページ）へ飛ばしている。

---

## 2. ファイル構成

```
index.html              ページ本体
css/style.css           デザイン（色・フォントは :root の変数で一括変更）
js/works.js             作品データ（WORKS 配列）★自動生成
js/main.js              画面の動き（フィルタ・モーダル・ギャラリー）
images/<作品ID>/        Web用の写真 NN.webp と NN-t.webp（サムネ）★自動生成
images/og.jpg           SNS用のサムネ（1200x630）★自動生成
img(メーカー別)/        写真の原本（1.7GB。公開用リポジトリには入れない）
tools/works-data.json   作品の文章・型番・カテゴリ ← 手で直すのはここ
tools/works-map.json    作品IDと写真の対応 ★自動生成
tools/works-list.md     確認用の作品一覧 ★自動生成
tools/build_images.py   写真の変換（EXIF削除・WebP化）
tools/build_works.py    js/works.js と works-list.md の生成
.claude/launch.json     ローカル確認用サーバーの設定
CNAME                   独自ドメイン名（noakuro.com）。消すと github.io のURLに戻る
README.md               差し替え箇所と GitHub Pages の公開手順
```

**★自動生成のファイルは直接編集しない。** 元データを直してスクリプトを流す。

### ページ構成（上から順）
1. ヒーロー（キャッチコピー・台数／設計ソフト／発送方法）
2. **01 作品一覧**：**メーカー → カテゴリ**の2軸で絞り込み。**10件ずつ表示**し、「あとN件を表示」で追加（件数は js/main.js の PAGE）。カードを押すと詳細をモーダル表示（写真はギャラリー切り替え）。下に互換品の注意書き
3. **02 キャビネット収納イメージ**：工具箱の引き出しの写真を8枚ずつ表示。押すと全枚数のギャラリーをモーダルで開く
4. **03 カスタム製作**
5. **04 ご注文の流れ**（作品を選ぶ → コメントで相談 → 製作 → 発送）
6. **05 工房について**（工房写真・互換品の注意書き）
7. **06 FAQ**
8. **07 ショップ**（メルカリ・ヤフオクの出品者ページへのリンク。スマホではアプリで開く）

かつてあった「02 対応メーカー」（メーカーごとに型番を並べる欄）は、
掲載内容の手入れが大変なので削除した。メーカー別の絞り込みは作品一覧のフィルタで足りる。

---

## 3. 作品データ

現在 **102作品 / 写真556枚**。データは2つのファイルを `tools/build_works.py` が合体させて `js/works.js` を作る。

| ファイル | 中身 | 誰が作るか |
|---|---|---|
| `tools/works-data.json` | 作品名・説明・型番・カテゴリ・状態 | **手で書く** |
| `tools/works-map.json` | 作品IDごとの写真の枚数と並び | `build_images.py` が自動生成 |

### works-data.json の書き方

```json
"snapon-pry-bar-wall": {
  "title": "プライバーホルダー 壁掛けタイプ",
  "category": "hand",
  "target": "Snap-on SPBS8A / SPBS12A / SPBS18A / SPBS24A",
  "makers": [["Snap-on", "SPBS8A"], ["Snap-on", "SPBS12A"]],
  "summary": "説明文",
  "specs": ["仕様1", "仕様2"]
}
```

- キーは**作品ID**。`tools/works-map.json` の `id` と1対1で対応する（片方にしかないとビルドが止まる）
- `makers` の各行が「02 対応メーカー」欄の1行になる。並び順は `build_works.py` の `MAKER_ORDER`
- `status` は省略すると `_default_status`（＝「販売中」）。**今は全作品が販売中**なので誰にも書いていない。
  準備中・受注製作のものが出たら `"status": "準備中"` を足す
- 全作品に共通の注意書き（工具は付属しない／全16色 など）は `build_works.py` の `COMMON_NOTES`

### カテゴリ（`build_works.py` の `CATEGORIES`）

| key | 表示名 | 件数 |
|---|---|---|
| socket | ソケット・ビット | 21 |
| ratchet | ラチェット・ハンドル | 31 |
| extension | エクステンションバー | 14 |
| driver | ドライバー・六角 | 9 |
| wrench | レンチ・トルクレンチ | 8 |
| hand | ハンドツール | 18 |
| grip | グリップ | 1 |

**分類の軸は「工具の種類」**。壁掛け・直置きといった取り付け方で分けると軸が混ざるので、それは `specs` に書く。

### メーカー（`MAKER_ORDER` の順）

Snap-on 49 / Ko-ken 14 / NEPROS 8 / PB SWISS TOOLS 6 / SIGNET 6 / KTC 5 / 汎用・その他 4 /
Blue-Point 2 / VESSEL 2 / アストロプロダクツ 2 / HAZET 1 / TONE 1 / ViGOR 1 / ASTRO 1

※ **ASTRO と アストロプロダクツは別メーカー**なので統合しない。

**掲載しないもの**：取引先向けの受託品（LUMO ブランド向けのラチェットホルダーなど）は、独占販売の約束があるため載せない。

---

## 4. メーカー名の扱い（商標まわりの方針）

※一般的な考え方で、法的な助言ではない。

- メーカー名は「どの工具に合うか」を示すためだけに使う（2014年改正の商標法26条1項6号の考え方）
- **ロゴ画像・ブランドカラー・専用フォントは使わない**。普通のテキストで書く
- 見出しは「取扱メーカー」ではなく **「対応メーカー」「対応工具」**
- 「〇〇風」より **「〇〇対応」** と書く（「スナップオン風」は形状模倣の論点にも近づく）
- 「純正品ではない互換品で、各メーカーとは関係ない」旨の注意書きを、**作品一覧の下**と「工房について」に置いている（メーカー名はフィルタと各作品の「対応」欄に出るので、この2か所は必ず残すこと）
- 工房名・ドメインにメーカー名を入れない

---

## 5. 写真の扱い

### 原本のフォルダ構成（`img(メーカー別)/`）

```
img(メーカー別)/
  #Snap-on/
    エクステンションバー/
      9.5sq/
        パープル/        ← 一番下の階層 = 1作品
          0.jpg          ← 最初のファイル = メイン写真（一覧に出る）
          1.jpg          ← 2枚目以降は詳細モーダルのギャラリー
  #ASTRO/
    インパクトソケット/   ← 2階層で終わる作品もある
  HP/                  ← 「#」で始まらないフォルダ = サイト用の写真（作品ではない）
    top_pic.jpg        → images/site/top-pic.webp
    og.jpg             → images/og.jpg（SNS用。これだけ特別扱い）
  cabinet/             ← ギャラリーにまとめるフォルダ（build_images.py の ALBUMS）
    IMG...113311.jpg   → images/cabinet/01.webp ＋ 01-t.webp（ファイル名順に連番）
```

- **先頭が「#」のフォルダ＝メーカー**。その下の**一番下の階層が1作品**で、そのフォルダの写真は全部ギャラリーに載せる
- **「#」で始まらないフォルダはサイト用の写真**。作品一覧には出ない
  - `HP/` → `images/site/<ファイル名>.webp`。工房について欄の写真がこれ（`index.html` の `#about` から直接ファイル名で参照）
  - `cabinet/` → `images/cabinet/NN.webp`（連番のギャラリー）。説明文は `tools/cabinet-data.json` に番号で書く。
    **写真を入れ替えると番号がずれる**ので、増減させたら説明文を付け直すこと（説明文のない写真があると `build_works.py` が警告を出す）
  - ギャラリーにまとめるフォルダは `build_images.py` の `ALBUMS` で指定する
  - `HP/og.jpg` だけは特別扱い。**SNSやLINEにURLを貼ったときに出るサムネ**として、
    1200x630 に切り抜いた **JPEG** を `images/og.jpg` に出す（WebPだと表示されないサービスがあるため）。
    どんな比率の写真でも中央で切り抜く。縦のどこを残すかは `build_images.py` の `OG_FOCUS`
    （0=上端 / 0.5=中央 / 1=下端。今は 0.33）
- **メイン写真はフォルダ内の最初のファイル**。全角数字（`０.jpg`）も半角に直して並べ替えるので `０` が先頭に来る
- メイン写真の多くは**出品用バナー**で、作品名・対応型番・「※工具は付属しません」「※カラー変更可能(全16色)」が画像に焼き込まれている。
  `tools/works-data.json` の型番はこのバナーから読み取った

### build_images.py がやること

```
python tools/build_images.py          # 新しい・更新された写真だけ変換
python tools/build_images.py --force  # 全部作り直す
```

1. **EXIF・GPS・ICC・XMP をすべて削除する**（自宅の場所が漏れないようにするため。生のピクセルから作り直しているので、メタデータは一切引き継がれない）
2. EXIF の回転情報は、実際に画像を回してから焼き込む
3. 長辺1600px / quality 80 の WebP → `images/<作品ID>/NN.webp`（平均137KB）
4. 長辺400px / quality 72 のサムネ → `images/<作品ID>/NN-t.webp`（平均14KB）
5. `img(メーカー別)/` を全部見て `tools/works-map.json`（作品IDと写真の対応）を作り直す
6. 原本から消えた写真・フォルダの出力ファイルも消す

作品IDはフォルダ名から作る。日本語のフォルダ名はローマ字にできないので、
新しい工具名のフォルダを足したら `build_images.py` の `SLUG` に対訳を書き足すこと
（書かないとIDが重複してエラーで止まる）。

### 写真を足す・差し替えるとき

1. `img(メーカー別)/` の該当フォルダに写真を置く（新作ならフォルダを作る）
2. `python tools/build_images.py`
3. 新作なら `tools/works-data.json` に作品IDのブロックを足す（IDは `tools/works-map.json` を見る）
4. `python tools/build_works.py`
5. `tools/works-list.md` で作品名・型番・枚数を確認

---

## 6. 公開までの残り作業

- [x] 作品写真の反映 — 102作品 / 556枚（EXIF削除済み）
- [x] 詳細モーダルのギャラリー表示
- [x] メーカー＋カテゴリの2軸フィルタ
- [x] ショップ欄の出品者ページURL（メルカリ・ヤフオクとも設定済み）
- [x] 個別の商品URLは載せない方針に決定
- [x] `.gitignore` で `img(メーカー別)/`（原本1.7GB）を除外。push しているのは `images/` の85MBだけ
- [x] 工房について欄の写真（`img(メーカー別)/HP/top_pic.jpg` → `images/site/top-pic.webp`）
- [x] GitHub リポジトリ作成 → push → Pages 公開（https://github.com/fumi1102497/noakuro-works ）
- [x] ドメイン取得（お名前.com）→ `CNAME` に `noakuro.com`（GitHub の Custom domain 欄から作られたファイル）
- [x] DNS 設定（apex は A レコード4つ、www は CNAME → `fumi1102497.github.io`）→ Enforce HTTPS 済み
- [x] Settings › Pages の Verified domains でドメイン認証（乗っ取り対策）済み
- [ ] スマホ実機で表示確認（ここまではPCとブラウザの375px表示でのみ確認済み）

### ローカルで確認

```
python -m http.server 8765
```
→ http://localhost:8765
