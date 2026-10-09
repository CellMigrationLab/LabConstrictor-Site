// LabConstrictor site: offers each visitor their own system's download, filters the App Centre
// live, and copies pip commands. Everything also works without JavaScript (links go to the
// app page, which lists every download). Re-runs after Zensical/Material instant navigation.

const lcFold = (s) => s.normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase();

/** The visitor's system ("windows", "macos", "linux"), or null on phones and anything unknown. */
function lcSystem() {
  const ua = navigator.userAgent.toLowerCase();
  if (/android|iphone|ipad/.test(ua)) return null;
  const p = (navigator.userAgentData?.platform || navigator.platform || ua).toLowerCase();
  if (p.includes("win")) return "windows";
  if (p.includes("mac")) return "macos";
  if (p.includes("linux") || p.includes("x11") || p.includes("cros")) return "linux";
  return null;
}

const lcSize = (bytes) => `${Math.round(bytes / 2 ** 20)} MB`;

/** Downloads for the visitor's system, from an element's data-downloads JSON ([] when none). */
function lcOptions(el, system) {
  return system ? (JSON.parse(el.dataset.downloads)[system] || []) : [];
}

/** Replace the "See all downloads" button by one button per download for this system. */
function lcFillGet(el, system) {
  const options = lcOptions(el, system);
  if (!options.length) return;
  const primary = options.map((o, i) =>
    `<a class="lc-btn${i ? " lc-btn--ghost" : ""}" href="${o.url}">Download for ${o.label}<small>${lcSize(o.size)} · .${o.ext}</small></a>`);
  const hint = system === "macos" ? '<p class="lc-small">Not sure which Mac you have? Apple menu, About This Mac: "Intel" means Intel, "M1" or later means Apple Silicon.</p>' : "";
  el.innerHTML = primary.join("") + '<a class="lc-btn lc-btn--ghost" href="#downloads">All downloads</a>' + hint;
}

/** Make a card's "Get" link a direct download when the system has exactly one choice. */
function lcFillCard(el, system) {
  const options = lcOptions(el, system);
  if (options.length === 1) { el.href = options[0].url; el.textContent = "Download"; }
}

function lcInitDownloads() {
  const system = lcSystem();
  document.querySelectorAll(".lc-get[data-downloads]").forEach((el) => lcFillGet(el, system));
  document.querySelectorAll(".lc-card__get[data-downloads]").forEach((el) => lcFillCard(el, system));
  document.querySelectorAll(".lc-os").forEach((el) => { el.open = el.dataset.os === system; });
}

/** True when a card passes the current search text and the three drop-downs. */
function lcMatches(card, state) {
  const has = (attr, want) => !want || card.dataset[attr].split(" ").includes(want);
  return (!state.kind || card.dataset.kind === state.kind) && has("routes", state.route) && has("hosts", state.host)
    && (!state.q || lcFold(card.dataset.search).includes(state.q));
}

function lcInitFilter() {
  const form = document.querySelector("[data-lc-filter]");
  if (!form || form.dataset.ready) return;
  form.dataset.ready = "1";
  const cards = [...document.querySelectorAll("[data-lc-grid] .lc-card")];
  const fields = { q: form.querySelector("[data-lc-search]"), kind: form.querySelector("[data-lc-kind]"),
                   route: form.querySelector("[data-lc-route]"), host: form.querySelector("[data-lc-host]") };
  const params = new URLSearchParams(location.search);
  Object.entries(fields).forEach(([key, el]) => { el.value = params.get(key) || ""; });
  const apply = () => {
    const state = Object.fromEntries(Object.entries(fields).map(([k, el]) => [k, k === "q" ? lcFold(el.value.trim()) : el.value]));
    let shown = 0;
    cards.forEach((c) => { const ok = lcMatches(c, state); c.hidden = !ok; shown += ok; });
    form.querySelector("[data-lc-count]").textContent = `${shown} of ${cards.length} apps`;
    document.querySelector("[data-lc-empty]").hidden = shown > 0;
    const next = new URLSearchParams(Object.entries(fields).map(([k, el]) => [k, el.value.trim()]).filter(([, v]) => v));
    history.replaceState(null, "", next.toString() ? `?${next}` : location.pathname);
  };
  Object.values(fields).forEach((el) => el.addEventListener("input", apply));
  apply();
}

function lcInitCopy() {
  document.querySelectorAll(".lc-code [data-copy]").forEach((btn) => {
    if (btn.dataset.ready) return;
    btn.dataset.ready = "1";
    btn.addEventListener("click", async () => {
      await navigator.clipboard.writeText(btn.parentElement.querySelector("code").textContent);
      btn.textContent = "Copied";
      setTimeout(() => { btn.textContent = "Copy"; }, 1500);
    });
  });
}

function lcInit() { lcInitDownloads(); lcInitFilter(); lcInitCopy(); }
if (typeof document$ !== "undefined") document$.subscribe(lcInit);
else document.addEventListener("DOMContentLoaded", lcInit);
