// LabConstrictor site: offers each visitor their own system's download, filters the App Centre
// live, copies pip commands and runs the phone menu. Everything also works without JavaScript (links go to the
// app page, which lists every download). Re-runs after Zensical/Material instant navigation.
// The same code rules as the demo's scripts apply (tests/test_js_rules.py): every function is documented, short, and has no catch or `|| default`.

const lcFold = (s) => s.normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase();

/**
 * The system ("windows", "macos", "linux") that a user agent, platform name and touch-point count describe. An iPad reports a Mac, but a Mac has no touch screen.
 * @param {string} ua - the user agent text.
 * @param {string} platform - the platform name the browser reports ("" when it reports none).
 * @param {number} touchPoints - navigator.maxTouchPoints.
 * @returns {(string|null)} the system, or null on phones, tablets, Chromebooks and anything unknown.
 */
function lcSystemFrom(ua, platform, touchPoints) {
  if (/android|iphone|ipad|cros/.test(ua.toLowerCase())) return null;
  const p = platform.toLowerCase();
  if (p.includes("mac")) return touchPoints > 1 ? null : "macos";
  if (p.includes("win")) return "windows";
  if (p.includes("linux") || p.includes("x11")) return "linux";
  return null;
}

/**
 * The visitor's system, read from the browser.
 * @returns {(string|null)} see lcSystemFrom.
 */
function lcSystem() {
  const platform = navigator.userAgentData ? navigator.userAgentData.platform : navigator.platform;
  return lcSystemFrom(navigator.userAgent, platform, navigator.maxTouchPoints);
}

/**
 * The processor family, when the browser can say (only Chromium-based browsers can, through client hints).
 * @returns {Promise<(string|null)>} "arm", "x86" or null when it cannot say; a refusal by the page's permissions policy counts as "cannot say".
 */
function lcArchitecture() {
  if (!navigator.userAgentData) return Promise.resolve(null);
  return navigator.userAgentData.getHighEntropyValues(["architecture"]).then(
    (hints) => (hints.architecture === "" ? null : hints.architecture),
    (err) => { if (err.name === "NotAllowedError") return null; throw err; });
}

/**
 * On a Mac whose chip is known, keep only the matching button strong green and the other light (in place: nothing moves).
 * @param {Element} tile - the Mac tile.
 * @param {string} arch - "arm" or "x86".
 * @returns {void}
 */
function lcMarkChip(tile, arch) {
  const mine = tile.querySelector(`[data-arch="${arch === "arm" ? "arm64" : "x86_64"}"]`);
  if (!mine) return;
  tile.querySelectorAll(".lc-btn").forEach((b) => b.classList.add("lc-btn--soft"));
  mine.classList.remove("lc-btn--soft");
}

/**
 * Open the install steps of one system (and close the others), then bring them into view: the reader has just downloaded its installer.
 * @param {string} system - "windows", "macos" or "linux".
 * @returns {void}
 */
function lcShowSteps(system) {
  const steps = document.querySelector(`[data-lc-steps="${system}"]`);
  if (!steps) return;
  document.querySelectorAll("[data-lc-steps]").forEach((d) => { d.open = d === steps; });
  steps.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
}

/**
 * A download button or a "steps" link opens the install steps of its system; the download itself goes ahead as usual.
 * @returns {void}
 */
function lcInitSteps() {
  document.querySelectorAll("[data-lc-download], [data-lc-steps-link]").forEach((el) => {
    el.addEventListener("click", (e) => {
      if (el.dataset.lcStepsLink) e.preventDefault();
      lcShowSteps(el.dataset.lcDownload || el.dataset.lcStepsLink);
    });
  });
}

/**
 * Add a second line to a tile saying that this release has no installer for the visitor's ARM processor (nothing for a tile with no installer at all).
 * @param {Element} tile - the visitor's tile (data-arches lists the processors its installers are for).
 * @returns {void}
 */
function lcWarnArm(tile) {
  if (tile.dataset.arches === "") return;
  const offered = tile.dataset.arches.split(" ");
  if (offered.includes("arm64")) return;
  const note = document.createElement("p");
  note.className = "lc-small";
  note.textContent = `This release has ${offered.join(" and ")} installers only; this device looks like ARM.`;
  tile.append(note);
}

/**
 * Mark the visitor's tile ("Your system") in place and, where the browser says which chip, the matching button. Every tile stays visible and in
 * its place: a wrong guess costs nothing and nothing jumps.
 * @returns {Promise<void>} resolves when the processor question is answered.
 */
function lcInitSystem() {
  const grid = document.querySelector("[data-lc-osgrid]");
  if (!grid) return Promise.resolve();
  const system = lcSystem();
  if (!system) {
    document.querySelectorAll("[data-lc-nosystem]").forEach((el) => { el.hidden = false; });
    return Promise.resolve();
  }
  const tile = grid.querySelector(`[data-os="${system}"]`);
  tile.classList.add("is-yours");
  tile.querySelectorAll(".lc-btn").forEach((b) => b.classList.remove("lc-btn--soft"));
  return lcArchitecture().then((arch) => {
    if (system === "macos" && arch) lcMarkChip(tile, arch);
    if (system !== "macos" && arch === "arm") lcWarnArm(tile);
  });
}

/**
 * True when a card passes the drop-downs and contains every word of the search text (so "nuclei segmentation" needs both words).
 * @param {HTMLElement} card - an app card.
 * @param {{kind: string, route: string, host: string, words: string[]}} state - the filter values.
 * @returns {boolean} whether the card stays visible.
 */
function lcMatches(card, state) {
  const has = (attr, want) => !want || card.dataset[attr].split(" ").includes(want);
  const folded = lcFold(card.dataset.search);
  return (!state.kind || card.dataset.kind === state.kind) && has("routes", state.route) && has("hosts", state.host)
    && state.words.every((w) => folded.includes(w));
}

/**
 * "1 app" or "4 apps".
 * @param {number} n - the count.
 * @returns {string} the count with its noun.
 */
function lcApps(n) {
  return `${n} app${n === 1 ? "" : "s"}`;
}

/**
 * The sentence under the filter: the apps shown of the apps in the main list, plus a note when the testing list has matches.
 * @param {number} shown - main-list cards shown.
 * @param {number} total - main-list cards.
 * @param {number} testingShown - testing cards shown.
 * @returns {string} the sentence.
 */
function lcCountText(shown, total, testingShown) {
  const more = testingShown ? `, and ${testingShown} more for testing and maintenance` : "";
  return `Showing ${shown} of ${lcApps(total)}${more}`;
}

/**
 * The empty-state sentence, naming what is active ("No app matches "tracking" with these filters.").
 * @param {string} query - the search text.
 * @param {boolean} filtered - whether a drop-down is set.
 * @param {number} testingShown - testing cards shown (they are listed below the main list).
 * @returns {string} the sentence.
 */
function lcEmptyText(query, filtered, testingShown) {
  const base = `No app matches${query ? ` "${query}"` : ""}${filtered ? " with these filters" : ""}.`;
  return testingShown ? `${base} The apps for testing and maintenance below match.` : base;
}

/**
 * The filter's fields that exist on this page (a drop-down is left out when no app offers a choice).
 * @param {Element} form - the filter form.
 * @returns {Array<[string, HTMLInputElement]>} pairs of the field's name and its element.
 */
function lcFilterFields(form) {
  const names = { q: "[data-lc-search]", kind: "[data-lc-kind]", route: "[data-lc-route]", host: "[data-lc-host]" };
  return Object.entries(names).map(([key, sel]) => [key, form.querySelector(sel)]).filter(([, el]) => el);
}

/**
 * Put the address's parameters into the fields; a drop-down value that is not one of its options is cleared instead of leaving the box blank.
 * @param {Array<[string, HTMLInputElement]>} fields - the fields.
 * @param {URLSearchParams} params - the address's parameters.
 * @returns {void}
 */
function lcReadParams(fields, params) {
  fields.forEach(([key, el]) => {
    el.value = params.has(key) ? params.get(key) : "";
    if (el.tagName === "SELECT" && el.value !== params.get(key) && params.has(key)) el.value = "";
  });
}

/**
 * Show and hide the cards for the current fields and write the count, the empty state and the address.
 * @param {Element} form - the filter form.
 * @param {Array<[string, HTMLInputElement]>} fields - the fields.
 * @param {{main: HTMLElement[], testing: HTMLElement[]}} cards - the cards of the main and the testing list.
 * @returns {void}
 */
function lcApplyFilter(form, fields, cards) {
  const state = Object.fromEntries(fields.map(([k, el]) => [k, el.value.trim()]));
  state.words = lcFold(state.q).split(/\s+/).filter(Boolean);
  const count = (list) => list.reduce((n, c) => { const ok = lcMatches(c, state); c.hidden = !ok; return n + ok; }, 0);
  const shown = count(cards.main), testingShown = count(cards.testing);
  form.querySelector("[data-lc-count]").textContent = lcCountText(shown, cards.main.length, testingShown);
  document.querySelector("[data-lc-empty]").hidden = shown > 0;
  document.querySelector("[data-lc-empty-text]").textContent = lcEmptyText(state.q, fields.some(([k]) => k !== "q" && state[k]), testingShown);
  document.querySelectorAll("[data-lc-group]").forEach((g) => { g.hidden = !g.querySelector(".lc-card:not([hidden])"); });
  const next = new URLSearchParams(fields.map(([k]) => [k, state[k]]).filter(([, v]) => v));
  history.replaceState(null, "", `${location.pathname}${next.toString() ? `?${next}` : ""}${location.hash}`);
}

/**
 * Make the App Centre filter live (once per page).
 * @returns {void}
 */
function lcInitFilter() {
  const form = document.querySelector("[data-lc-filter]");
  if (!form || form.dataset.ready) return;
  form.dataset.ready = "1";
  const cards = { main: [...document.querySelectorAll("[data-lc-group]:not(.lc-testing) .lc-card")], testing: [...document.querySelectorAll(".lc-testing .lc-card")] };
  const fields = lcFilterFields(form);
  lcReadParams(fields, new URLSearchParams(location.search));
  const apply = () => lcApplyFilter(form, fields, cards);
  fields.forEach(([, el]) => el.addEventListener("input", apply));
  form.querySelector("[data-lc-reset]").addEventListener("click", () => { fields.forEach(([, el]) => { el.value = ""; }); apply(); });
  form.hidden = false;
  apply();
}

/**
 * Make the Copy buttons of the pip commands work; when the browser refuses to write to the clipboard, the button says so.
 * @returns {void}
 */
function lcInitCopy() {
  document.querySelectorAll(".lc-code [data-copy]").forEach((btn) => {
    if (btn.dataset.ready) return;
    btn.dataset.ready = "1";
    const say = (text) => { btn.textContent = text; setTimeout(() => { btn.textContent = "Copy"; }, 1500); };
    btn.addEventListener("click", () => {
      navigator.clipboard.writeText(btn.parentElement.querySelector("code").textContent).then(() => say("Copied"), () => say("Select and copy"));
    });
  });
}

/**
 * The phone menu is a checkbox: Space toggles it natively; Enter toggles it too. It says whether it is expanded, and Escape from
 * anywhere in the menu closes it and returns the focus to the checkbox. Runs once per page.
 * @returns {void}
 */
function lcInitMenu() {
  const box = document.querySelector(".lc-menu-toggle");
  if (!box || box.dataset.ready) return;
  box.dataset.ready = "1";
  const sync = () => box.setAttribute("aria-expanded", box.checked ? "true" : "false");
  box.addEventListener("change", sync);
  box.addEventListener("keydown", (e) => { if (e.key === "Enter") { box.checked = !box.checked; sync(); e.preventDefault(); } });
  box.closest("nav").addEventListener("keydown", (e) => { if (e.key === "Escape" && box.checked) { box.checked = false; sync(); box.focus(); } });
  sync();
}

/**
 * On phones the docs menu starts folded (it is open in the HTML so that it works without scripts).
 * @returns {void}
 */
function lcInitDrawer() {
  const drawer = document.querySelector(".lc-docs__drawer");
  if (drawer && window.matchMedia("(max-width: 56rem)").matches) drawer.open = false;
}

/**
 * Start everything the page needs.
 * @returns {void}
 */
function lcInit() {
  lcInitSystem();
  lcInitSteps();
  lcInitFilter();
  lcInitCopy();
  lcInitDrawer();
  lcInitMenu();
}

if (typeof document$ !== "undefined") document$.subscribe(lcInit);
else document.addEventListener("DOMContentLoaded", lcInit);
