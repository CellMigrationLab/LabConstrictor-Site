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
      if (b.closest('.nb')) { var n = Number(b.dataset.step); b.disabled = state.step < n - 1 || state.step >= n; b.title = state.step >= n ? 'Already run' : b.disabled ? 'Run the cells above first' : ''; }
    });
    all('#demo-panel-napari [data-act="run-step"], #demo-panel-fiji [data-dialog] [data-act="run-step"]').forEach(function (b) { b.disabled = state.step >= 3 && !b.closest('[data-dialog]'); b.title = b.disabled ? 'The example result is already shown; use Reset demo to start again' : ''; });
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
    var inApp = state.nbTab === 'app' && state.opened;
    one('[data-act="run-next"]').disabled = inApp ? state.step >= 3 : state.welcomeRun;
    showUpdates();
  }

  function showUpdates() {
    one('[data-act="scenario"]').checked = state.scenario;
    var out = one('[data-updates-out]'), row = one('[data-nbrow="NucleiSky2DBenchmarking"]');
    var needs = state.checked && state.scenario && !state.updated;
    row.querySelector('[data-status]').textContent = needs ? '❌ Needs Update to 9.9.9' : '✅ Up-to-date';
    row.querySelector('[data-version]').textContent = state.updated ? '9.9.9' : '0.1.0';
    row.querySelector('[data-update]').innerHTML = needs ? '<button type="button" class="nb__btn" data-demo-sim data-act="update">Update</button>' : '-';
    if (!state.checked) { out.textContent = ''; }
    else if (needs) { out.textContent = '⚠️ Some notebooks need to be updated. (Simulated check; the version number is made up.)'; }
    else { out.textContent = state.updated ? '✅ Updated NucleiSky2DBenchmarking to version 9.9.9. (Illustrative example.)' : '✅ All notebooks are up-to-date. (Simulated check; nothing was contacted.)'; }
  }

  function showLayers() {
    all('[data-layer-row]').forEach(function (li) {
      var key = li.dataset.layerRow; li.classList.toggle('is-selected', state.selected === key);
      li.querySelector('.np__eye').setAttribute('aria-pressed', state.vis[key] ? 'true' : 'false');
      li.querySelector('.np__name').setAttribute('aria-pressed', state.selected === key ? 'true' : 'false');
    });
    all('#demo-panel-napari [data-layer], #demo-panel-fiji [data-layer]').forEach(function (img) {
      if (img.tagName !== 'IMG') { return; }
      var key = img.dataset.layer, exists = (key === 'aligned' || key === 'alignment') ? state.step >= 3 : true;
      if (img.closest('#demo-panel-fiji')) { return; }
      img.hidden = !(exists && state.vis[key]); img.style.opacity = state.opacity[key] / 100;
    });
    var slider = one('[data-act="opacity"]'), sel = state.selected;
    slider.disabled = !sel || !state.vis[sel]; slider.value = sel ? state.opacity[sel] : 100;
    slider.setAttribute('aria-valuetext', (slider.value / 100).toFixed(2));
    var shown = Object.keys(state.vis).filter(function (k) { return state.vis[k] && (k === 'reference' || k === 'query' || state.step >= 3); });
    one('.np__canvas').setAttribute('aria-label', 'napari viewer showing the layers: ' + shown.join(', ') + '.');
    one('[data-colormap]').textContent = sel === 'alignment' ? 'magenta' : 'gray';
    one('[data-panel-hint]').hidden = !!sel;
  }

  function showFiji() { one('[data-dialog]').hidden = !state.fijiDialog; }

  function sync() { root.dataset.step = state.step; showViews(); showSteps(); showNotebook(); showLayers(); showFiji(); }

  function runStep(n) { state.step = Math.max(state.step, n); if (n === 3) { state.selected = state.selected || 'aligned'; state.fijiDialog = false; state.opened = true; state.launched = true; } }

  function settle(out) {
    if (!out) { return; }
    if (out[1]) { one('[data-announce]').textContent = out[1]; }
    var target = out[0] ? one(out[0]) : null;
    if (target && !target.hidden && !target.disabled) { target.focus(); }
  }

  var actions = {
    'launch': function () { state.launched = true; return ['#nb-tab-welcome', 'NucleiSky is open in JupyterLab with the Welcome notebook.']; },
    'run-welcome': function () { state.welcomeRun = true; return ['[data-act="test-connection"]', 'Cell ran: the list of notebooks and the update check are shown.']; },
    'open-app': function () { state.launched = true; state.opened = true; state.nbTab = 'app'; },
    'run-step': function (el) { var n = Number(el.dataset.step); runStep(n); return [n === 3 && !el.closest('.nb') ? '[data-act="fiji-open"]' : '', 'Cell ' + n + ' ran; its output is shown below.']; },
    'run-next': function () { if (state.nbTab === 'app' && state.opened) { runStep(Math.min(3, state.step + 1)); } else { state.welcomeRun = true; } },
    'toggle-code': function () { state.code = !state.code; },
    'test-connection': function () { state.checked = true; },
    'scenario': function (el) { state.scenario = el.checked; state.updated = false; },
    'update': function () { state.updated = true; return ['[data-act="test-connection"]', 'Updated.']; },
    'eye': function (el) { var key = el.parentNode.dataset.layerRow; state.vis[key] = !state.vis[key]; },
    'select': function (el) { state.selected = el.dataset.layer; },
    'opacity': function (el) { state.opacity[state.selected] = Number(el.value); },
    'fiji-open': function () { state.fijiDialog = true; return ['[data-dialog] [data-act="run-step"]', '']; },
    'fiji-cancel': function () { state.fijiDialog = false; return ['[data-act="fiji-open"]', '']; }
  };

  root.addEventListener('click', function (e) {
    var el = e.target.closest('[data-act], [data-nb-tab], [data-demo-act]');
    if (!el || !root.contains(el) || el.disabled) { return; }
    if (el.dataset.demoAct === 'view') { state.view = el.dataset.view; sync(); return; }
    if (el.dataset.demoAct === 'reset') { state = JSON.parse(JSON.stringify(FRESH)); sync(); one('#demo-tab-notebook').focus(); return; }
    if (el.dataset.nbTab) { state.nbTab = el.dataset.nbTab; sync(); return; }
    if (el.tagName === 'INPUT' && el.type !== 'checkbox') { return; }
    if (actions[el.dataset.act]) { var out = actions[el.dataset.act](el); sync(); settle(out); }
  });
  root.addEventListener('input', function (e) { if (e.target.dataset.act === 'opacity') { actions.opacity(e.target); sync(); } });
  root.addEventListener('keydown', function (e) {
    var tab = e.target.closest('[role="tab"][data-view]');
    if (!tab || ['ArrowRight', 'ArrowLeft', 'Home', 'End'].indexOf(e.key) < 0) { return; }
    var tabs = all('[role="tab"][data-view]'), i = tabs.indexOf(tab);
    var next = e.key === 'Home' ? tabs[0] : e.key === 'End' ? tabs[tabs.length - 1] : tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
    e.preventDefault();
    state.view = next.dataset.view; sync(); next.focus();
  });

  all('[data-status]').forEach(function (el) { el.dataset.idle = el.textContent; });
  root.classList.add('is-live');
  sync();
})();
