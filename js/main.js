/* =========================================================
   画面の動き
   作品データは js/works.js（自動生成）にあります。
     文章・型番・カテゴリを直す → tools/works-data.json → python tools/build_works.py
     写真を足す／減らす         → img(メーカー別)/      → python tools/build_images.py
   ========================================================= */

const grid = document.getElementById("worksGrid");
const filters = document.querySelector(".cat-filters");
const makerFilters = document.querySelector(".maker-filters");
const resultCount = document.getElementById("resultCount");
const moreWrap = document.getElementById("moreWrap");
const moreBtn = document.getElementById("moreBtn");
const modal = document.getElementById("workModal");
const modalBody = document.getElementById("modalBody");

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const catLabel = (key) => (CATEGORIES.find((c) => c.key === key) || {}).label || "";
const statusClass = (s) => (s === "販売中" ? "is-sale" : s === "受注製作" ? "is-order" : "is-soon");
const makersOf = (w) => [...new Set((w.makers || []).map((m) => m.maker))];

// 一度に表示する件数（PCは12件、スマホは10件。860pxはCSSの折り返し位置と同じ）
const PAGE = window.matchMedia("(min-width: 861px)").matches ? 12 : 10;
let curCat = "all";
let curMaker = "all";
let shown = PAGE;

/* ---------- 制作ホルダー一覧 ---------- */

function thumb(work) {
  if (work.thumb || work.image) {
    const src = work.thumb || work.image;
    return `<img src="${esc(src)}" alt="${esc(work.title)}" loading="lazy" decoding="async">`;
  }
  return `<div class="thumb-placeholder"><span class="mono">${esc(work.id.toUpperCase())}</span></div>`;
}

// 2つの条件は AND。件数も「もう片方で絞った結果」を出すので、
// メーカーを選ぶとカテゴリ側の件数が連動して変わる（0件のものは押せなくする）
const matchCat = (w, key) => key === "all" || w.category === key;
const matchMaker = (w, key) => key === "all" || makersOf(w).includes(key);

function chip(attr, key, label, n, selected) {
  return `<button role="tab" data-${attr}="${esc(key)}" aria-selected="${selected}"${n ? "" : " disabled"}>` +
    `${esc(label)}<span class="f-count mono">${n}</span></button>`;
}

function renderFilters() {
  // カテゴリの件数は、いま選んでいるメーカーの中で数える
  filters.innerHTML = CATEGORIES.map((c) =>
    chip("cat", c.key, c.label,
         WORKS.filter((w) => matchCat(w, c.key) && matchMaker(w, curMaker)).length,
         c.key === curCat)
  ).join("");

  // メーカーの件数は、いま選んでいるカテゴリの中で数える
  const used = MAKER_ORDER.filter((m) => WORKS.some((w) => makersOf(w).includes(m)));
  const extra = [...new Set(WORKS.flatMap(makersOf))].filter((m) => !MAKER_ORDER.includes(m));
  makerFilters.innerHTML = [["all", "全メーカー"], ...[...used, ...extra].map((m) => [m, m])]
    .map(([key, label]) =>
      chip("maker", key, label,
           WORKS.filter((w) => matchMaker(w, key) && matchCat(w, curCat)).length,
           key === curMaker)
    )
    .join("");
}

filters.addEventListener("click", (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  curCat = btn.dataset.cat;
  shown = PAGE;
  renderFilters();
  renderWorks();
});

makerFilters.addEventListener("click", (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  curMaker = btn.dataset.maker;
  shown = PAGE;
  renderFilters();
  renderWorks();
});

function cardHtml(w) {
  return `
      <article class="work-card" tabindex="0" data-id="${esc(w.id)}">
        <div class="work-thumb">${thumb(w)}${
    // 「販売中」は全作品に付くのでバッジを出さない。準備中・受注製作のときだけ出す
    w.status === "販売中" ? "" : `<span class="status ${statusClass(w.status)}">${esc(w.status)}</span>`
  }${
    w.images && w.images.length > 1 ? `<span class="shot-count mono">${w.images.length}</span>` : ""
  }</div>
        <div class="work-info">
          <p class="work-cat mono">${esc(catLabel(w.category))}</p>
          <h3>${esc(w.title)}</h3>
          <p class="work-target">${esc(w.target)}</p>
        </div>
      </article>`;
}

function renderWorks() {
  const list = WORKS.filter((w) => matchCat(w, curCat) && matchMaker(w, curMaker));
  const view = list.slice(0, shown);
  const rest = list.length - view.length;

  resultCount.textContent = rest > 0 ? `${list.length} 点中 ${view.length} 点を表示` : `${list.length} 点`;
  grid.innerHTML = list.length
    ? view.map(cardHtml).join("")
    : `<p class="no-result">この条件に合うホルダーはありません。</p>`;

  moreWrap.hidden = rest <= 0;
  if (rest > 0) {
    const next = Math.min(PAGE, rest);
    moreBtn.innerHTML =
      `<span class="more-arrow" aria-hidden="true">↓</span>` +
      `<span>あと${next}件を表示</span>` +
      `<span class="more-rest mono">残り ${rest}</span>`;
  }
}

moreBtn.addEventListener("click", () => {
  const before = grid.querySelectorAll(".work-card").length;
  shown += PAGE;
  renderWorks();
  // 追加された先頭のカードへフォーカスを移す（キーボード・読み上げ用）
  const cards = grid.querySelectorAll(".work-card");
  if (cards[before]) cards[before].focus({ preventScroll: true });
});

/* ---------- ホルダー詳細（ギャラリー付き） ---------- */

function galleryMarkup(shots, tiles, alt, start) {
  const nav =
    shots.length > 1
      ? `<button class="gallery-nav prev" data-step="-1" aria-label="前の写真">‹</button>
           <button class="gallery-nav next" data-step="1" aria-label="次の写真">›</button>
           <span class="gallery-count mono"><span id="galleryIndex">${start + 1}</span> / ${shots.length}</span>`
      : "";
  const strip =
    shots.length > 1
      ? `<div class="gallery-strip" role="tablist" aria-label="写真">${tiles
          .map(
            (t, i) =>
              `<button role="tab" data-i="${i}" aria-selected="${i === start}"><img src="${esc(t)}" alt="${esc(
                alt
              )} 写真${i + 1}" loading="lazy" decoding="async"></button>`
          )
          .join("")}</div>`
      : "";
  return `<div class="gallery">
         <div class="gallery-main">
           <img id="galleryMain" src="${esc(shots[start])}" alt="${esc(alt)}">
           ${nav}
         </div>
         ${strip}
       </div>`;
}

function openWork(id) {
  const w = WORKS.find((x) => x.id === id);
  if (!w) return;
  gallery = null;

  const shots = w.images && w.images.length ? w.images : w.image ? [w.image] : [];
  const tiles = w.thumbs && w.thumbs.length ? w.thumbs : shots;

  // 商品ページのURLは変わりやすいので持たせない。ショップ（出品者ページ）へ誘導する。
  const buttons = [`<a class="btn btn-primary" href="#shop" data-close>ショップで探す</a>`];

  const galleryHtml = shots.length
    ? galleryMarkup(shots, tiles, w.title, 0)
    : `<div class="modal-thumb"><div class="thumb-placeholder"><span class="mono">${esc(w.id.toUpperCase())}</span></div></div>`;

  modalBody.innerHTML = `
    ${galleryHtml}
    <div class="modal-text">
      <p class="work-cat mono">${esc(catLabel(w.category))} ・ <span class="status-inline ${statusClass(w.status)}">${esc(w.status)}</span></p>
      <h3>${esc(w.title)}</h3>
      <p class="work-target">対応：${esc(w.target)}</p>
      <p>${esc(w.summary)}</p>
      <ul class="modal-specs">${w.specs.map((s) => `<li>${esc(s)}</li>`).join("")}</ul>
      <div class="modal-actions">${buttons.join("")}</div>
      <ul class="modal-notes note">${(typeof COMMON_NOTES !== "undefined" ? COMMON_NOTES : [])
        .map((n) => `<li>${esc(n)}</li>`)
        .join("")}</ul>
    </div>`;

  if (shots.length > 1) setupGallery(shots);
  if (!modal.open) modal.showModal();
}

/* ---------- キャビネット収納イメージ ---------- */

const cabinetSection = document.getElementById("cabinet");
const cabinetGrid = document.getElementById("cabinetGrid");
const cabinetMoreWrap = document.getElementById("cabinetMoreWrap");
const cabinetMoreBtn = document.getElementById("cabinetMoreBtn");
const CAB_PAGE = 8; // 一度に表示する枚数
let cabShown = CAB_PAGE;

const cabShots = () => (typeof CABINET !== "undefined" && CABINET.shots) || [];

function renderCabinet() {
  const all = cabShots();
  if (!all.length) {
    cabinetSection.hidden = true;
    return;
  }
  document.getElementById("cabinetLead").textContent = CABINET.lead || "";
  const view = all.slice(0, cabShown);
  cabinetGrid.innerHTML = view
    .map(
      (s, i) => `
      <button type="button" class="shot" data-i="${i}">
        <img src="${esc(s.thumb)}" alt="${esc(s.caption)}" loading="lazy" decoding="async">
        <span class="shot-cap">${esc(s.caption)}</span>
      </button>`
    )
    .join("");

  const rest = all.length - view.length;
  cabinetMoreWrap.hidden = rest <= 0;
  if (rest > 0) {
    cabinetMoreBtn.innerHTML =
      `<span class="more-arrow" aria-hidden="true">↓</span>` +
      `<span>あと${Math.min(CAB_PAGE, rest)}枚を表示</span>` +
      `<span class="more-rest mono">残り ${rest}</span>`;
  }
}

cabinetMoreBtn.addEventListener("click", () => {
  const before = cabinetGrid.querySelectorAll(".shot").length;
  cabShown += CAB_PAGE;
  renderCabinet();
  const shots = cabinetGrid.querySelectorAll(".shot");
  if (shots[before]) shots[before].focus({ preventScroll: true });
});

cabinetGrid.addEventListener("click", (e) => {
  const b = e.target.closest(".shot");
  if (b) openCabinet(Number(b.dataset.i));
});

function openCabinet(start) {
  const all = cabShots();
  if (!all.length) return;
  gallery = null;

  const shots = all.map((s) => s.image);
  const tiles = all.map((s) => s.thumb);
  const caps = all.map((s) => s.caption);

  modalBody.innerHTML = `
    ${galleryMarkup(shots, tiles, "キャビネット収納イメージ", start)}
    <div class="modal-text">
      <p class="work-cat mono">キャビネット収納イメージ</p>
      <h3 id="galleryCaption">${esc(caps[start])}</h3>
      <p>手持ちの工具を実測して設計したホルダーで、引き出しを1段ずつ埋めています。</p>
      <div class="modal-actions"><a class="btn btn-primary" href="#shop" data-close>ショップで探す</a></div>
      <ul class="modal-notes note">${(typeof COMMON_NOTES !== "undefined" ? COMMON_NOTES : [])
        .map((n) => `<li>${esc(n)}</li>`)
        .join("")}</ul>
    </div>`;

  setupGallery(shots, start, caps);
  if (!modal.open) modal.showModal();
}

let gallery = null; // { shots, i, show } — 開いているホルダーのギャラリー

function setupGallery(shots, start = 0, captions = null) {
  const main = modalBody.querySelector("#galleryMain");
  const idx = modalBody.querySelector("#galleryIndex");
  const strip = modalBody.querySelector(".gallery-strip");
  const cap = modalBody.querySelector("#galleryCaption");

  const show = (n) => {
    gallery.i = (n + shots.length) % shots.length;
    main.src = shots[gallery.i];
    idx.textContent = gallery.i + 1;
    if (cap && captions) cap.textContent = captions[gallery.i];
    strip.querySelectorAll("button").forEach((b, k) => b.setAttribute("aria-selected", k === gallery.i));
    const active = strip.children[gallery.i];
    if (active) active.scrollIntoView({ block: "nearest", inline: "nearest" });
  };
  gallery = { shots, i: start, show };

  strip.addEventListener("click", (e) => {
    const b = e.target.closest("button[data-i]");
    if (b) show(Number(b.dataset.i));
  });
  modalBody.querySelectorAll(".gallery-nav").forEach((b) =>
    b.addEventListener("click", () => show(gallery.i + Number(b.dataset.step)))
  );
}

modal.addEventListener("keydown", (e) => {
  if (!gallery) return;
  if (e.key === "ArrowRight") { e.preventDefault(); gallery.show(gallery.i + 1); }
  if (e.key === "ArrowLeft") { e.preventDefault(); gallery.show(gallery.i - 1); }
});
modal.addEventListener("close", () => { gallery = null; });

/* ---------- イベント ---------- */

grid.addEventListener("click", (e) => {
  const card = e.target.closest(".work-card");
  if (card) openWork(card.dataset.id);
});
grid.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && e.target.classList.contains("work-card")) openWork(e.target.dataset.id);
});

modal.addEventListener("click", (e) => {
  if (e.target === modal || e.target.closest(".modal-close") || e.target.closest("[data-close]")) modal.close();
});

/* モバイルメニュー */
const toggle = document.querySelector(".nav-toggle");
const nav = document.querySelector(".site-nav");
toggle.addEventListener("click", () => {
  const open = nav.classList.toggle("is-open");
  toggle.setAttribute("aria-expanded", open);
});
nav.addEventListener("click", (e) => {
  if (e.target.tagName === "A") {
    nav.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", false);
  }
});

/* ショップリンク — スマホでは同じタブで開く
   別タブ（target="_blank"）だと、OSがアプリに渡してくれないことがあるため。
   Android の intent:// による起動は試したが、メルカリ・ヤフオクとも
   「出品者ページ」はアプリの対象外でブラウザに戻されるだけだったので入れていない
   （アプリ内ブラウザで intent:// がエラーになる副作用のほうが大きい）。 */
const isPhone =
  /Android|iPhone|iPad|iPod/.test(navigator.userAgent) ||
  (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);

if (isPhone) {
  document.querySelectorAll(".shop-card").forEach((a) => {
    a.removeAttribute("target");
    a.removeAttribute("rel");
  });
}

document.getElementById("year").textContent = new Date().getFullYear();

renderFilters();
renderWorks();
renderCabinet();
