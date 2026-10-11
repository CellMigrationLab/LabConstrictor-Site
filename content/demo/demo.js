/* The /demo/ page: a small state machine that switches between stored views of one precomputed result.
   Nothing is calculated here and nothing leaves the page. */
(function () {
  var root = document.querySelector('[data-demo]');
  if (!root) { return; }
  var FRESH = { cat: 'install', page: 'download', progress: 0, installed: false, selectedKey: '', view: 'notebook', launched: false, done: 0, how: 1, busy: false, step: 0, welcomeRun: false, opened: false, nbTab: 'welcome', code: false, checked: false, scenario: false, updated: false,
                fijiDialog: true, selected: '', vis: { reference: true, query: false, aligned: true, alignment: true },
                opacity: { reference: 100, query: 100, aligned: 100, alignment: 80 } };
  var state = JSON.parse(JSON.stringify(FRESH));
  var all = function (sel) { return Array.prototype.slice.call(root.querySelectorAll(sel)); };
  var one = function (sel) { return root.querySelector(sel); };

  var INSTALL_NEXT = { download: '.wi__file', smart: '.wi__sl', smart2: '[data-go="welcome"]', welcome: '[data-go="license"]', license: '[data-go="type"]', type: '[data-go="folder"]',
                       folder: '[data-go="options"]', options: '[data-go="installing"]', installing: '[data-needs-install]', finish: '[data-go="start"]', start: '.wi__start' };
  var installTimer = null;

  function showCat() {
    all('[role="tab"][data-cat]').forEach(function (t) {
      var on = t.dataset.cat === state.cat;
      t.setAttribute('aria-selected', on ? 'true' : 'false'); t.tabIndex = on ? 0 : -1;
      one('#demo-cat-' + t.dataset.cat).hidden = !on;
    });
  }

  function showInstaller() {
    all('[data-page]').forEach(function (p) { p.hidden = p.dataset.page !== state.page; });
    one('[data-progress] span').style.width = state.progress + '%';
    one('[data-progress]').setAttribute('aria-valuenow', String(state.progress));
    all('[data-log] [data-at]').forEach(function (l) { l.hidden = state.progress < Number(l.dataset.at); });
    one('[data-cmd]').hidden = state.progress < 85;
    one('[data-needs-install]').disabled = !state.installed;
    var head = one('[data-page="installing"] .wi__head div');
    if (!head.dataset.wait) { head.dataset.wait = head.lastElementChild.textContent; }
    head.firstElementChild.textContent = state.installed ? 'Installation Complete' : 'Installing';
    head.lastElementChild.textContent = state.installed ? 'Setup was completed successfully.' : head.dataset.wait;
  }

  function startInstall() {
    state.progress = 0; state.installed = false;
    installTimer = setInterval(function () {
      state.progress = Math.min(100, state.progress + 2);
      if (state.progress === 100) { clearInterval(installTimer); installTimer = null; state.installed = true; one('[data-announce]').textContent = 'Installation complete. Click Next.'; }
      sync();
      if (state.installed) { var t = one('[data-page="installing"] [data-needs-install]'); t.focus(); }
    }, 100);
  }

  function showViews() {
    all('[role="tab"][data-view]').forEach(function (t) {
      var on = t.dataset.view === state.view;
      t.setAttribute('aria-selected', on ? 'true' : 'false'); t.tabIndex = on ? 0 : -1;
      one('#demo-panel-' + t.dataset.view).hidden = !on;
    });
    one('[data-demo-experimental]').hidden = state.view === 'notebook';
    one('[data-how]').hidden = state.view === 'notebook';
  }

  function showSteps() {
    all('[data-from]').forEach(function (el) { el.hidden = state.step < Number(el.dataset.from); });
    all('[data-done]:not([data-status])').forEach(function (el) { el.hidden = state.done < Number(el.dataset.done); });
    all('[data-after]').forEach(function (el) { el.hidden = state.done < Number(el.dataset.after); });
    all('[data-from-welcome]').forEach(function (el) { el.hidden = !state.welcomeRun; });
    all('[data-from-nb]').forEach(function (el) { el.hidden = !state.opened; });
    all('[data-act="run-step"]').forEach(function (b) {
      if (b.closest('.nb')) { var n = Number(b.dataset.step); b.disabled = state.done < n - 1 || state.step >= n; b.title = state.step >= n ? 'Already run' : b.disabled ? 'Finish the step above first' : ''; }
    });
    all('#demo-panel-napari [data-act="run-step"], #demo-panel-fiji [data-dialog] [data-act="run-step"]').forEach(function (b) { b.disabled = state.step >= 3 && !b.closest('[data-dialog]'); b.title = b.disabled ? 'The example result is already shown; use Reset demo to start again' : ''; });
    all('[data-status]').forEach(function (el) { if (el.dataset.done) { el.textContent = state.busy ? 'running\u2026' : state.step >= 3 ? el.dataset.done : el.dataset.idle; } });
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
    one('[data-act="run-next"]').disabled = inApp ? (state.step >= 3 || state.step !== state.done) : state.welcomeRun;
    all('[data-act="widget"]').forEach(function (b) { b.disabled = state.done >= Number(b.dataset.n); });
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

  function next() {
    var app = state.nbTab === 'app' && state.opened, n = state.step;
    if (state.cat === 'install') { return ['[data-page="' + state.page + '"] ' + INSTALL_NEXT[state.page], state.page === 'download' ? (state.selectedKey ? 'Now double-click the file to start the installer (or press Enter).' : 'Double-click the downloaded installer to start it.') : '']; }
    if (state.view === 'napari') { return state.step < 3 ? ['#demo-panel-napari .np__run', 'Click Run in the dock to run the tool.'] : [null, 'Click a layer name to select it, the eye to hide it, and move the opacity slider. Then try Fiji.']; }
    if (state.view === 'fiji') { return state.fijiDialog ? ['[data-dialog] [data-act="run-step"]', 'Click OK to run the tool.'] : state.step < 3 ? ['[data-act="fiji-open"]', 'Open the tool again from the Plugins menu.'] : [null, 'The result opens in its own window. Use Reset demo to start again.']; }
    if (!state.launched) { return ['[data-act="launch"]', state.selectedKey ? 'Now double-click the icon to open the app (or press Enter).' : 'Double-click the NucleiSky icon to open the app.']; }
    if (!state.welcomeRun) { return ['[data-act="run-welcome"]', 'Click the play button to run the Welcome cell. It lists the notebooks of the app.']; }
    if (!app) { return ['[data-act="open-app"]', 'Click Open the notebook on NucleiSky2DApp to open the 2D notebook.']; }
    var names = ['', 'Load & Process', 'Load Masks & Extract Features', 'Run adaptive NucleiSky2D'];
    if (n === state.done && n < 3) { return ['#nb-doc-app [data-act="run-step"][data-step="' + (n + 1) + '"]', 'Click the play button to run the next cell. It shows a widget.']; }
    if (n > state.done) { return ['[data-act="widget"][data-n="' + n + '"]', 'Use the widget: click ' + names[n] + '.']; }
    return [null, 'That is the whole notebook: scroll down for NucleiSky\'s own output. Try Show/Hide code, then napari or Fiji.'];
  }

  function showNext() {
    all('.is-next').forEach(function (el) { el.classList.remove('is-next'); });
    var hint = next(), target = hint[0] ? one(hint[0]) : null;
    if (target && !target.hidden && !target.disabled && !state.busy) { target.classList.add('is-next'); }
    one('[data-next]').textContent = (state.cat === 'install' || (!state.launched && state.view === 'notebook')) ? hint[1] : '';
  }

  var BOXES = { 1: [0], 2: [0], 3: [1], 4: [2], 5: [0, 1], 6: [2] };
  var WHERE = { 4: ['#demo-panel-napari .np__form', '#demo-panel-fiji [data-dialog]'], 6: ['#demo-panel-napari .np__canvas', '#demo-panel-fiji .fj__win:nth-child(3)'] };
  function showHow() {
    all('.is-explain').forEach(function (el) { el.classList.remove('is-explain'); });
    all('.lc-how__step').forEach(function (b) { b.setAttribute('aria-pressed', Number(b.dataset.i) === state.how ? 'true' : 'false'); });
    all('.lc-how__box').forEach(function (b, i) { b.classList.toggle('is-active', BOXES[state.how].indexOf(i) >= 0); });
    var where = WHERE[state.how];
    if (where && state.view !== 'notebook') { var el = one(where[state.view === 'napari' ? 0 : 1]); if (el && !el.hidden) { el.classList.add('is-explain'); } }
  }

  function showFiji() { one('[data-dialog]').hidden = !state.fijiDialog; }

  function sync() { root.dataset.step = state.step; showCat(); showInstaller(); showViews(); showSteps(); showNotebook(); showLayers(); showFiji(); showHow(); showNext(); }

  function runStep(n, fromHost) { state.step = Math.max(state.step, n); if (fromHost) { state.done = 3; } if (n === 3 && fromHost) { state.selected = state.selected || 'aligned'; state.fijiDialog = false; state.opened = true; state.launched = true; } }

  var pending = null;
  function switchView(view) {
    if (view !== state.view) { clearBusy(); state = JSON.parse(JSON.stringify(FRESH)); state.cat = 'use'; state.view = view; }
    sync();
  }
  function delayFor(el) {
    var a = el.dataset.act;
    if (a === 'run-step') { return el.closest('.nb') ? 600 : 1500; }
    if (a === 'widget') { return [0, 900, 900, 2200][Number(el.dataset.n)]; }
    return { 'run-welcome': 700, 'test-connection': 900, 'update': 700 }[a] || 0;
  }
  function clearBusy() {
    if (pending) { clearTimeout(pending); pending = null; }
    if (installTimer) { clearInterval(installTimer); installTimer = null; }
    state.busy = false; delete root.dataset.busy;
    all('.is-busy').forEach(function (el) { el.classList.remove('is-busy'); el.removeAttribute('aria-busy'); });
  }
  function runLater(el, ms) {
    state.busy = true; root.dataset.busy = 'true'; el.classList.add('is-busy'); el.setAttribute('aria-busy', 'true');
    one('[data-announce]').textContent = 'Running\u2026'; sync();
    pending = setTimeout(function () { clearBusy(); var out = actions[el.dataset.act](el); sync(); settle(out); }, ms);
  }

  function settle(out) {
    if (!out) { return; }
    if (out[1]) { one('[data-announce]').textContent = out[1]; }
    var target = out[0] ? one(out[0]) : null;
    if (target && !target.hidden && !target.disabled) { target.focus(); }
  }

  var actions = {
    'inst': function (el) { state.page = el.dataset.go; state.selectedKey = ''; if (state.page === 'installing') { startInstall(); } return ['[data-page="' + state.page + '"] ' + INSTALL_NEXT[state.page], 'Installer page: ' + state.page + '.']; },
    'open-start': function () { state.cat = 'use'; state.view = 'notebook'; state.launched = true; return ['#nb-tab-welcome', 'NucleiSky is open in JupyterLab with the Welcome notebook.']; },
    'how': function (el) { state.how = Number(el.dataset.i); },
    'launch': function () { state.launched = true; return ['#nb-tab-welcome', 'NucleiSky is open in JupyterLab with the Welcome notebook.']; },
    'run-welcome': function () { state.welcomeRun = true; return ['[data-act="test-connection"]', 'Cell ran: the list of notebooks and the update check are shown.']; },
    'open-app': function () { state.launched = true; state.opened = true; state.nbTab = 'app'; },
    'run-step': function (el) { var n = Number(el.dataset.step), host = !el.closest('.nb'); runStep(n, host); return [host && n === 3 ? '[data-act="fiji-open"]' : '', host ? 'Example result shown.' : 'Cell ' + n + ' ran; its widget is shown below.']; },
    'widget': function (el) { state.done = Math.max(state.done, Number(el.dataset.n)); return ['', 'Done: the result is shown below.']; },
    'run-next': function () { if (state.nbTab === 'app' && state.opened) { runStep(Math.min(3, state.step + 1), false); } else { state.welcomeRun = true; } },
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
    if (el.dataset.demoAct === 'cat') { state.cat = el.dataset.cat; sync(); return; }
    if (el.dataset.demoAct === 'view') { switchView(el.dataset.view); return; }
    if (state.busy && el.dataset.demoAct !== 'reset') { return; }
    if (el.dataset.demoAct === 'reset') { clearBusy(); state = JSON.parse(JSON.stringify(FRESH)); sync(); one('#demo-cat-tab-install').focus(); return; }
    if (el.dataset.nbTab) { state.nbTab = el.dataset.nbTab; sync(); return; }
    if (el.hasAttribute('data-dbl') && e.detail === 1) { state.selectedKey = el.dataset.act + el.dataset.go; el.classList.add('is-selected'); sync(); return; }
    if (el.tagName === 'INPUT' && el.type !== 'checkbox') { return; }
    if (!actions[el.dataset.act]) { return; }
    var ms = delayFor(el);
    if (ms) { runLater(el, ms); return; }
    var out = actions[el.dataset.act](el); sync(); settle(out);
  });
  root.addEventListener('input', function (e) { if (e.target.dataset.act === 'opacity') { actions.opacity(e.target); sync(); } });
  root.addEventListener('keydown', function (e) {
    var tab = e.target.closest('[role="tab"]');
    if (!tab || ['ArrowRight', 'ArrowLeft', 'Home', 'End'].indexOf(e.key) < 0) { return; }
    var tabs = all('[role="tab"]').filter(function (t) { return t.parentNode === tab.parentNode; }), i = tabs.indexOf(tab);
    var next = e.key === 'Home' ? tabs[0] : e.key === 'End' ? tabs[tabs.length - 1] : tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
    e.preventDefault();
    if (next.dataset.view) { switchView(next.dataset.view); } else { state.cat = next.dataset.cat; sync(); } next.focus();
  });

  all('[data-status]').forEach(function (el) { el.dataset.idle = el.textContent; });
  root.classList.add('is-live');
  sync();
})();
