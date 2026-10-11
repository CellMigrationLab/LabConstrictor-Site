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

function lcInitDownloads() { lcInitSystem(); }

/** True when a card passes the drop-downs and contains every word of the search text (so "nuclei segmentation" needs both words). */
function lcMatches(card, state) {
  const has = (attr, want) => !want || card.dataset[attr].split(" ").includes(want);
  const folded = lcFold(card.dataset.search);
  return (!state.kind || card.dataset.kind === state.kind) && has("routes", state.route) && has("hosts", state.host)
    && state.words.every((w) => folded.includes(w));
}

/** The sentence under the filter: the apps shown of the apps in the main list, plus a note when the testing list has matches. */
function lcCountText(shown, total, testingShown) {
  const more = testingShown ? `, and ${testingShown} more for testing and maintenance` : "";
  return `Showing ${shown} of ${total} apps${more}`;
}

/** The empty-state sentence, naming what is active ("No app matches "tracking" with these filters."). */
function lcEmptyText(query, filtered) {
  return `No app matches${query ? ` "${query}"` : ""}${filtered ? " with these filters" : ""}.`;
}

function lcInitFilter() {
  const form = document.querySelector("[data-lc-filter]");
  if (!form || form.dataset.ready) return;
  form.dataset.ready = "1";
  const mainCards = [...document.querySelectorAll("[data-lc-group]:not(.lc-testing) .lc-card")];
  const testingCards = [...document.querySelectorAll(".lc-testing .lc-card")];
  const fields = { q: form.querySelector("[data-lc-search]"), kind: form.querySelector("[data-lc-kind]"),
                   route: form.querySelector("[data-lc-route]"), host: form.querySelector("[data-lc-host]") };
  const present = Object.entries(fields).filter(([, el]) => el);
  const params = new URLSearchParams(location.search);
  present.forEach(([key, el]) => { el.value = params.get(key) || ""; });
  const apply = () => {
    const state = Object.fromEntries(present.map(([k, el]) => [k, el.value.trim()]));
    state.words = lcFold(state.q).split(/\s+/).filter(Boolean);
    const count = (list) => list.reduce((n, c) => { const ok = lcMatches(c, state); c.hidden = !ok; return n + ok; }, 0);
    const shown = count(mainCards), testingShown = count(testingCards);
    form.querySelector("[data-lc-count]").textContent = lcCountText(shown, mainCards.length, testingShown);
    document.querySelector("[data-lc-empty]").hidden = shown + testingShown > 0;
    document.querySelector("[data-lc-empty-text]").textContent = lcEmptyText(state.q, present.some(([k]) => k !== "q" && state[k]));
    document.querySelectorAll("[data-lc-group]").forEach((g) => { g.hidden = !g.querySelector(".lc-card:not([hidden])"); });
    const next = new URLSearchParams(present.map(([k]) => [k, state[k]]).filter(([, v]) => v));
    history.replaceState(null, "", next.toString() ? `?${next}` : location.pathname);
  };
  present.forEach(([, el]) => el.addEventListener("input", apply));
  form.querySelector("[data-lc-reset]").addEventListener("click", () => { present.forEach(([, el]) => { el.value = ""; }); apply(); });
  form.hidden = false;
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

/** The phone menu is a checkbox: Space toggles it natively; Enter toggles it too and Escape closes it. */
function lcInitMenu() {
  const box = document.querySelector(".lc-menu-toggle");
  if (!box) return;
  box.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { box.checked = !box.checked; e.preventDefault(); }
    if (e.key === "Escape") box.checked = false;
  });
}

function lcInit() { lcInitDownloads(); lcInitFilter(); lcInitCopy(); lcInitDrawer(); lcInitMenu(); }
if (typeof document$ !== "undefined") document$.subscribe(lcInit);
else document.addEventListener("DOMContentLoaded", lcInit);

/** On phones the docs menu starts folded (it is open in the HTML so that it works without scripts). */
function lcInitDrawer() {
  const drawer = document.querySelector(".lc-docs__drawer");
  if (drawer && window.matchMedia("(max-width: 56rem)").matches) drawer.open = false;
}
