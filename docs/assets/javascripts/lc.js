// LabConstrictor site: offers each visitor their own system's download, filters the App Centre
// live, and copies pip commands. Everything also works without JavaScript (links go to the
// app page, which lists every download). Re-runs after Zensical/Material instant navigation.

const lcFold = (s) => s.normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase();

/** The visitor's system ("windows", "macos", "linux"), or null on phones, Chromebooks and anything unknown. */
function lcSystem() {
  const ua = navigator.userAgent.toLowerCase();
  if (/android|iphone|ipad|cros/.test(ua)) return null;
  const p = (navigator.userAgentData?.platform || navigator.platform || ua).toLowerCase();
  if (p.includes("win")) return "windows";
  if (p.includes("mac")) return "macos";
  if (p.includes("linux") || p.includes("x11")) return "linux";
  return null;
}

/** "arm", "x86" or null. Only Chromium-based browsers can say (client hints); Safari and Firefox cannot. */
async function lcArchitecture() {
  try {
    const hints = await navigator.userAgentData?.getHighEntropyValues(["architecture"]);
    return hints?.architecture || null;
  } catch (err) {
    return null;
  }
}

/** Mark the visitor's tile ("Your system") and, on a Mac where the browser says which chip, the matching button.
 *  Every tile stays visible: a wrong guess costs nothing. */
async function lcInitSystem() {
  const grid = document.querySelector("[data-lc-osgrid]");
  const system = lcSystem();
  if (!grid || !system) return;
  const tile = grid.querySelector(`[data-os="${system}"]`);
  tile.classList.add("is-yours");
  grid.prepend(tile);
  const arch = await lcArchitecture();
  if (system === "macos" && arch) {
    const mine = tile.querySelector(`[data-arch="${arch === "arm" ? "arm64" : "x86_64"}"]`);
    if (mine) {
      tile.querySelectorAll(".lc-btn").forEach((b) => b.classList.add("lc-btn--ghost"));
      mine.classList.remove("lc-btn--ghost");
      tile.querySelector("h3").after(mine);
    }
  }
  if (system !== "macos" && arch === "arm") tile.querySelector(".lc-small:last-child").textContent = "Only 64-bit Intel/AMD (x86_64) installers exist; this device looks like ARM.";
}

function lcInitDownloads() { lcInitSystem(); document.querySelectorAll(".lc-os").forEach((el) => { el.open = el.dataset.os === lcSystem(); }); }

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
