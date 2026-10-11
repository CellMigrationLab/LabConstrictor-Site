/* The /demo/ page: a small state machine that switches between stored views of one precomputed result.
   Nothing is calculated here and nothing leaves the page. */
(function () {
  var root = document.querySelector('[data-demo]');
  if (!root) { return; }
  var FRESH = { view: 'notebook', launched: false, step: 0, welcomeRun: false, opened: false, nbTab: 'welcome', code: false, checked: false, scenario: false, updated: false,
                fijiDialog: true, selected: '', vis: { reference: true, query: false, aligned: true, alignment: true },
                opacity: { reference: 100, query: 100, aligned: 100, alignment: 80 } };
  var state = JSON.parse(JSON.stringify(FRESH));
  var all = function (sel) { return Array.prototype.slice.call(root.querySelectorAll(sel)); };
  var one = function (sel) { return root.querySelector(sel); };

  function showViews() {
    all('[role="tab"][data-view]').forEach(function (t) {
      var on = t.dataset.view === state.view;
      t.setAttribute('aria-selected', on ? 'true' : 'false'); t.tabIndex = on ? 0 : -1;
      one('#demo-panel-' + t.dataset.view).hidden = !on;
    });
    one('[data-demo-experimental]').hidden = state.view === 'notebook';
  }

  function showSteps() {
    all('[data-from]').forEach(function (el) { el.hidden = state.step < Number(el.dataset.from); });
    all('[data-from-welcome]').forEach(function (el) { el.hidden = !state.welcomeRun; });
    all('[data-from-nb]').forEach(function (el) { el.hidden = !state.opened; });
    all('[data-act="run-step"]').forEach(function (b) {
      if (b.closest('.nb')) { b.disabled = state.step < Number(b.dataset.step) - 1; b.title = b.disabled ? 'Run the cells above first' : ''; }
    });
    all('[data-status]').forEach(function (el) { if (el.dataset.done) { el.textContent = state.step >= 3 ? el.dataset.done : el.dataset.idle; } });
  }

  function showNotebook() {
    one('[data-launch]').hidden = state.launched; one('[data-shell]').hidden = !state.launched;
    var app = state.nbTab === 'app' && state.opened;
    one('#nb-doc-welcome').hidden = app; one('#nb-doc-app').hidden = !app;
    all('[data-nb-tab]').forEach(function (t) { var on = (t.dataset.nbTab === 'app') === app; t.setAttribute('aria-selected', on ? 'true' : 'false'); });
    all('.nb__code').forEach(function (c) { c.hidden = !state.code; });
    all('.nb__collapsed').forEach(function (c) { c.hidden = state.code; });
    one('[data-act="toggle-code"]').setAttribute('aria-pressed', state.code ? 'true' : 'false');
    one('[data-act="run-welcome"]').disabled = state.welcomeRun;
    showUpdates();
  }

  function showUpdates() {
    var out = one('[data-updates-out]'), row = one('[data-nbrow="NucleiSky2DBenchmarking"]');
    var needs = state.checked && state.scenario && !state.updated;
    row.querySelector('[data-status]').textContent = needs ? '❌ Needs Update to 0.1.1' : '✅ Up-to-date';
    row.querySelector('[data-version]').textContent = state.updated ? '0.1.1' : '0.1.0';
    row.querySelector('[data-update]').innerHTML = needs ? '<button type="button" class="nb__btn" data-demo-sim data-act="update">Update</button>' : '-';
    if (!state.checked) { out.textContent = ''; }
    else if (needs) { out.textContent = '⚠️ Some notebooks need to be updated. (Simulated check; the newer version is an illustrative example.)'; }
    else { out.textContent = state.updated ? '✅ Updated NucleiSky2DBenchmarking to version 0.1.1. (Illustrative example.)' : '✅ All notebooks are up-to-date. (Simulated check; nothing was contacted.)'; }
  }

  function showLayers() {
    all('[data-layer-row]').forEach(function (li) {
      var key = li.dataset.layerRow; li.classList.toggle('is-selected', state.selected === key);
      li.querySelector('.np__eye').setAttribute('aria-pressed', state.vis[key] ? 'true' : 'false');
    });
    all('#demo-panel-napari [data-layer], #demo-panel-fiji [data-layer]').forEach(function (img) {
      if (img.tagName !== 'IMG') { return; }
      var key = img.dataset.layer, exists = (key === 'aligned' || key === 'alignment') ? state.step >= 3 : true;
      if (img.closest('#demo-panel-fiji')) { return; }
      img.hidden = !(exists && state.vis[key]); img.style.opacity = state.opacity[key] / 100;
    });
    var slider = one('[data-act="opacity"]'), sel = state.selected;
    slider.disabled = !sel; slider.value = sel ? state.opacity[sel] : 100;
    slider.setAttribute('aria-valuetext', (slider.value / 100).toFixed(2));
    one('[data-colormap]').textContent = sel === 'alignment' ? 'magenta' : 'gray';
    one('[data-panel-hint]').hidden = !!sel;
  }

  function showFiji() { one('[data-dialog]').hidden = !state.fijiDialog; }

  function sync() { root.dataset.step = state.step; showViews(); showSteps(); showNotebook(); showLayers(); showFiji(); }

  function runStep(n) { state.step = Math.max(state.step, n); if (n === 3) { state.selected = state.selected || 'aligned'; state.fijiDialog = false; state.opened = true; state.launched = true; } }

  var actions = {
    'launch': function () { state.launched = true; },
    'run-welcome': function () { state.welcomeRun = true; },
    'open-app': function () { state.launched = true; state.opened = true; state.nbTab = 'app'; },
    'run-step': function (el) { runStep(Number(el.dataset.step)); },
    'run-next': function () { if (state.nbTab === 'app' && state.opened) { runStep(Math.min(3, state.step + 1)); } else { state.welcomeRun = true; } },
    'toggle-code': function () { state.code = !state.code; },
    'test-connection': function () { state.checked = true; },
    'scenario': function (el) { state.scenario = el.checked; state.updated = false; },
    'update': function () { state.updated = true; },
    'eye': function (el) { var key = el.parentNode.dataset.layerRow; state.vis[key] = !state.vis[key]; },
    'select': function (el) { state.selected = el.dataset.layer; },
    'opacity': function (el) { state.opacity[state.selected] = Number(el.value); },
    'fiji-open': function () { state.fijiDialog = true; },
    'fiji-cancel': function () { state.fijiDialog = false; }
  };

  root.addEventListener('click', function (e) {
    var el = e.target.closest('[data-act], [data-nb-tab], [data-demo-act]');
    if (!el || !root.contains(el) || el.disabled) { return; }
    if (el.dataset.demoAct === 'view') { state.view = el.dataset.view; sync(); return; }
    if (el.dataset.demoAct === 'reset') { state = JSON.parse(JSON.stringify(FRESH)); sync(); one('#demo-tab-notebook').focus(); return; }
    if (el.dataset.nbTab) { state.nbTab = el.dataset.nbTab; sync(); return; }
    if (el.tagName === 'INPUT' && el.type !== 'checkbox') { return; }
    if (actions[el.dataset.act]) { actions[el.dataset.act](el); sync(); }
  });
  root.addEventListener('input', function (e) { if (e.target.dataset.act === 'opacity') { actions.opacity(e.target); sync(); } });
  root.addEventListener('keydown', function (e) {
    var tab = e.target.closest('[role="tab"][data-view]');
    if (!tab || (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft')) { return; }
    var tabs = all('[role="tab"][data-view]'), i = tabs.indexOf(tab), next = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
    state.view = next.dataset.view; sync(); next.focus();
  });

  all('[data-status]').forEach(function (el) { el.dataset.idle = el.textContent; });
  root.classList.add('is-live');
  sync();
})();
