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

const PAGE = 10; // 一度に表示する件数
let curCat = "all";
let curMaker = "all";
let shown = PAGE;

/* ---------- 作品一覧 ---------- */

function thumb(work) {
  if (work.thumb || work.image) {
    const src = work.thumb || work.image;
    return `<img src="${esc(src)}" alt="${esc(work.title)}" loading="lazy" decoding="async">`;
  }
  return `<div class="thumb-placeholder"><span class="mono">${esc(work.id.toUpperCase())}</span></div>`;
}

function renderFilters() {
  filters.innerHTML = CATEGORIES.map((c) => {
    const n = c.key === "all" ? WORKS.length : WORKS.filter((w) => w.category === c.key).length;
    return `<button role="tab" data-cat="${c.key}" aria-selected="${c.key === curCat}">${esc(c.label)}<span class="f-count mono">${n}</span></button>`;
  }).join("");

  const used = MAKER_ORDER.filter((m) => WORKS.some((w) => makersOf(w).includes(m)));
  const extra = [...new Set(WORKS.flatMap(makersOf))].filter((m) => !MAKER_ORDER.includes(m));
  makerFilters.innerHTML = [["all", "全メーカー"], ...[...used, ...extra].map((m) => [m, m])]
    .map(([key, label]) => {
      const n = key === "all" ? WORKS.length : WORKS.filter((w) => makersOf(w).includes(key)).length;
      return `<button role="tab" data-maker="${esc(key)}" aria-selected="${key === curMaker}">${esc(label)}<span class="f-count mono">${n}</span></button>`;
    })
    .join("");
}

filters.addEventListener("click", (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  curCat = btn.dataset.cat;
  shown = PAGE;
  filters.querySelectorAll("button").forEach((b) => b.setAttribute("aria-selected", b === btn));
  renderWorks();
});

makerFilters.addEventListener("click", (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  curMaker = btn.dataset.maker;
  shown = PAGE;
  makerFilters.querySelectorAll("button").forEach((b) => b.setAttribute("aria-selected", b === btn));
  renderWorks();
});

function cardHtml(w) {
  return `
      <article class="work-card" tabindex="0" data-id="${esc(w.id)}">
        <div class="work-thumb">${thumb(w)}<span class="status ${statusClass(w.status)}">${esc(w.status)}</span>${
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
  const list = WORKS.filter(
    (w) => (curCat === "all" || w.category === curCat) && (curMaker === "all" || makersOf(w).includes(curMaker))
  );
  const view = list.slice(0, shown);
  const rest = list.length - view.length;

  resultCount.textContent = rest > 0 ? `${list.length} 作品中 ${view.length} 作品を表示` : `${list.length} 作品`;
  grid.innerHTML = list.length
    ? view.map(cardHtml).join("")
    : `<p class="no-result">この条件に合う作品はありません。</p>`;

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

/* ---------- 作品詳細（ギャラリー付き） ---------- */

function openWork(id) {
  const w = WORKS.find((x) => x.id === id);
  if (!w) return;
  gallery = null;

  const shots = w.images && w.images.length ? w.images : w.image ? [w.image] : [];
  const tiles = w.thumbs && w.thumbs.length ? w.thumbs : shots;

  // 商品ページのURLは変わりやすいので持たせない。ショップ（出品者ページ）へ誘導する。
  const buttons = [`<a class="btn btn-primary" href="#shop" data-close>ショップで探す</a>`];

  const galleryHtml = shots.length
    ? `<div class="gallery">
         <div class="gallery-main">
           <img id="galleryMain" src="${esc(shots[0])}" alt="${esc(w.title)}">
           ${shots.length > 1 ? `<button class="gallery-nav prev" data-step="-1" aria-label="前の写真">‹</button>
           <button class="gallery-nav next" data-step="1" aria-label="次の写真">›</button>
           <span class="gallery-count mono"><span id="galleryIndex">1</span> / ${shots.length}</span>` : ""}
         </div>
         ${
           shots.length > 1
             ? `<div class="gallery-strip" role="tablist" aria-label="写真">${tiles
                 .map(
                   (t, i) =>
                     `<button role="tab" data-i="${i}" aria-selected="${i === 0}"><img src="${esc(t)}" alt="${esc(
                       w.title
                     )} 写真${i + 1}" loading="lazy" decoding="async"></button>`
                 )
                 .join("")}</div>`
             : ""
         }
       </div>`
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

let gallery = null; // { shots, i, show } — 開いている作品のギャラリー

function setupGallery(shots) {
  const main = modalBody.querySelector("#galleryMain");
  const idx = modalBody.querySelector("#galleryIndex");
  const strip = modalBody.querySelector(".gallery-strip");

  const show = (n) => {
    gallery.i = (n + shots.length) % shots.length;
    main.src = shots[gallery.i];
    idx.textContent = gallery.i + 1;
    strip.querySelectorAll("button").forEach((b, k) => b.setAttribute("aria-selected", k === gallery.i));
    const active = strip.children[gallery.i];
    if (active) active.scrollIntoView({ block: "nearest", inline: "nearest" });
  };
  gallery = { shots, i: 0, show };

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

/* ショップリンク — スマホではアプリで開く（アプリが無ければブラウザ） */
const APP_PACKAGE = {
  "jp.mercari.com": "com.kouzoh.mercari",
  "auctions.yahoo.co.jp": "jp.co.yahoo.android.yauction"
};
const isAndroid = /Android/.test(navigator.userAgent);
const isIOS =
  /iPhone|iPad|iPod/.test(navigator.userAgent) ||
  (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);

if (isAndroid || isIOS) {
  document.querySelectorAll(".shop-card").forEach((a) => {
    const web = a.href;
    // iOS はユニバーサルリンク任せ。別タブで開くとアプリに渡らないことがあるので同じタブにする
    a.removeAttribute("target");
    a.removeAttribute("rel");
    if (!isAndroid) return;
    const u = new URL(web);
    const pkg = APP_PACKAGE[u.hostname];
    if (!pkg) return;
    // アプリが無ければ browser_fallback_url（＝元のURL）に飛ぶ
    a.href =
      "intent://" + u.host + u.pathname + u.search +
      "#Intent;scheme=https;package=" + pkg +
      ";S.browser_fallback_url=" + encodeURIComponent(web) + ";end";
  });
}

document.getElementById("year").textContent = new Date().getFullYear();

renderFilters();
renderWorks();
