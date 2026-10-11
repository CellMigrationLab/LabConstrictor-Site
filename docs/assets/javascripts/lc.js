// LabConstrictor site: offers each visitor their own system's download, filters the App Centre
// live, and copies pip commands. Everything also works without JavaScript (links go to the
// app page, which lists every download). Re-runs after Zensical/Material instant navigation.

const lcFold = (s) => s.normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase();

/** The system ("windows", "macos", "linux") that a user agent, platform name and touch-point count describe, or null on phones,
 *  tablets, Chromebooks and anything unknown. An iPad reports a Mac, but a Mac has no touch screen. */
function lcSystemFrom(ua, platform, touchPoints) {
  if (/android|iphone|ipad|cros/.test(ua.toLowerCase())) return null;
  const p = platform.toLowerCase();
  if (p.includes("mac")) return touchPoints > 1 ? null : "macos";
  if (p.includes("win")) return "windows";
  if (p.includes("linux") || p.includes("x11")) return "linux";
  return null;
}

/** The visitor's system, read from the browser (see lcSystemFrom). */
function lcSystem() {
  const platform = navigator.userAgentData ? navigator.userAgentData.platform : navigator.platform;
  return lcSystemFrom(navigator.userAgent, platform, navigator.maxTouchPoints);
}

/** "arm", "x86" or null when the browser cannot say (only Chromium-based browsers can, through client hints). */
async function lcArchitecture() {
  if (!navigator.userAgentData) return null;
  try {
    const hints = await navigator.userAgentData.getHighEntropyValues(["architecture"]);
    return hints.architecture === "" ? null : hints.architecture;
  } catch (err) {
    if (err.name === "NotAllowedError") return null;   // the page's permissions policy forbids the question: unknown, not an error
    throw err;
  }
}

/** On a Mac whose chip is known, make the matching button the filled one (in place: nothing moves). */
function lcMarkChip(tile, arch) {
  const mine = tile.querySelector(`[data-arch="${arch === "arm" ? "arm64" : "x86_64"}"]`);
  if (!mine) return;
  tile.querySelectorAll(".lc-btn").forEach((b) => b.classList.add("lc-btn--ghost"));
  mine.classList.remove("lc-btn--ghost");
}

/** Add a second line to a tile saying that this release has no installer for the visitor's ARM processor. */
function lcWarnArm(tile) {
  const offered = tile.dataset.arches.split(" ");
  if (offered.includes("arm64")) return;
  const note = document.createElement("p");
  note.className = "lc-small";
  note.textContent = `This release has ${offered.join(" and ")} installers only; this device looks like ARM.`;
  tile.append(note);
}

/** Mark the visitor's tile ("Your system") in place and, where the browser says which chip, the matching button.
 *  Every tile stays visible and in its place: a wrong guess costs nothing and nothing jumps. */
async function lcInitSystem() {
  const grid = document.querySelector("[data-lc-osgrid]");
  if (!grid) return;
  const system = lcSystem();
  if (!system) { document.querySelectorAll("[data-lc-nosystem]").forEach((el) => { el.hidden = false; }); return; }
  const tile = grid.querySelector(`[data-os="${system}"]`);
  tile.classList.add("is-yours");
  const arch = await lcArchitecture();
  if (system === "macos" && arch) lcMarkChip(tile, arch);
  if (system !== "macos" && arch === "arm") lcWarnArm(tile);
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

/** The phone menu is a checkbox: Space toggles it natively; Enter toggles it too. It says whether it is expanded, and Escape from
 *  anywhere in the menu closes it and returns the focus to the checkbox. */
function lcInitMenu() {
  const box = document.querySelector(".lc-menu-toggle");
  if (!box) return;
  const sync = () => box.setAttribute("aria-expanded", box.checked ? "true" : "false");
  box.addEventListener("change", sync);
  box.addEventListener("keydown", (e) => { if (e.key === "Enter") { box.checked = !box.checked; sync(); e.preventDefault(); } });
  box.closest("nav").addEventListener("keydown", (e) => { if (e.key === "Escape" && box.checked) { box.checked = false; sync(); box.focus(); } });
  sync();
}

function lcInit() { lcInitDownloads(); lcInitFilter(); lcInitCopy(); lcInitDrawer(); lcInitMenu(); }
if (typeof document$ !== "undefined") document$.subscribe(lcInit);
else document.addEventListener("DOMContentLoaded", lcInit);

/** On phones the docs menu starts folded (it is open in the HTML so that it works without scripts). */
function lcInitDrawer() {
  const drawer = document.querySelector(".lc-docs__drawer");
  if (drawer && window.matchMedia("(max-width: 56rem)").matches) drawer.open = false;
}
