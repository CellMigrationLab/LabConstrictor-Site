/* Drawing the notebook window (cells, outputs, NucleiSky widgets, update check) from the state. Nothing here changes the state. */
(function (ns) {
  var d = ns.dom;
  var UPDATE_BUTTON = '<button type="button" class="nb__btn" data-demo-sim data-act="update">Update</button>';
  var CTL_PAIRS = [['seed', 'seed-val'], ['override', 'override-val'], ['time', 'time-val']];

  /**
   * The reason a notebook cell's play button is off, or '' when it can be pressed.
   * @param {number} n - the cell's step number (1 to 3).
   * @param {DemoState} state - the state.
   * @returns {string} the tooltip text.
   */
  function stepTitle(n, state) {
    if (state.step >= n) { return 'Already run'; }
    if (n === 1 && !state.init) { return 'Run the Step 0 cell first'; }
    return state.done < n - 1 ? 'Finish the step above first' : '';
  }

  /**
   * Show each output and cell once its step is reached, and set the play buttons of the three windows.
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderSteps(root, state) {
    d.all(root, '[data-from]').forEach(function (el) { el.hidden = state.step < Number(el.dataset.from); });
    d.all(root, '[data-done]:not([data-status])').forEach(function (el) { el.hidden = state.done < Number(el.dataset.done); });
    d.all(root, '[data-after]').forEach(function (el) { el.hidden = state.done < Number(el.dataset.after); });
    d.all(root, '[data-opta]').forEach(function (el) { el.hidden = !state.optA; });
    d.all(root, '[data-from-init]').forEach(function (el) { el.hidden = !state.init; });
    d.all(root, '[data-from-welcome]').forEach(function (el) { el.hidden = !state.welcomeRun; });
    d.all(root, '[data-from-nb]').forEach(function (el) { el.hidden = !state.opened; });
    d.all(root, '.nb [data-act="run-step"]').forEach(function (b) {
      b.title = stepTitle(Number(b.dataset.step), state);
      b.disabled = b.title !== '';
    });
    renderHostRuns(root, state);
  }

  /**
   * Set the Run buttons of the napari dock and the Fiji dialog, and the napari status line.
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderHostRuns(root, state) {
    d.all(root, '#demo-panel-napari [data-act="run-step"], #demo-panel-fiji [data-dialog] [data-act="run-step"]').forEach(function (b) {
      b.disabled = state.step >= 3 && !b.closest('[data-dialog]');
      b.title = b.disabled ? 'The example result is already shown; use Reset demo to start again' : '';
    });
    d.all(root, '[data-status][data-done]').forEach(function (el) {
      el.textContent = state.busy ? 'running…' : state.step >= 3 ? el.dataset.done : el.dataset.idle;
    });
  }

  /**
   * Draw the widgets of NucleiSky that can be explored: the two toggles, the method panels, the dependent fields and the accordions.
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderWidgets(root, state) {
    ['crop', 'seg'].forEach(function (key) {
      d.all(root, '[data-act="' + key + '-mode"]').forEach(function (b) {
        var on = b.dataset.mode === state[key];
        b.classList.toggle('is-on', on);
        d.setPressed(b, on);
      });
      d.all(root, '[data-' + key + ']').forEach(function (el) { el.hidden = el.dataset[key] !== state[key]; });
    });
    var method = d.one(root, '[data-ctl="method"]').value;
    d.all(root, '[data-method]').forEach(function (el) { el.hidden = el.dataset.method !== method; });
    d.all(root, '[data-method-desc]').forEach(function (el) { el.hidden = el.dataset.methodDesc !== method; });
    CTL_PAIRS.forEach(function (p) { d.one(root, '[data-ctl="' + p[1] + '"]').disabled = !d.one(root, '[data-ctl="' + p[0] + '"]').checked; });
    d.all(root, '[data-act="acc"]').forEach(function (b) {
      var on = state.acc[b.dataset.acc];
      b.setAttribute('aria-expanded', on ? 'true' : 'false');
      d.one(root, '#' + b.getAttribute('aria-controls')).hidden = !on;
    });
    d.all(root, 'input[type="range"] + output').forEach(function (o) { o.textContent = o.previousElementSibling.value; });
  }

  /**
   * Draw Option A's settings: the matcher tabs show only when Use default settings is unticked, and the open tab's pill and panel.
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderOptionA(root, state) {
    d.one(root, '[data-a-custom]').hidden = d.one(root, '[data-ctl="a-default"]').checked;
    d.all(root, '[data-act="a-tab"]').forEach(function (b) {
      var on = b.dataset.tab === state.aTab;
      b.classList.toggle('is-on', on);
      d.setPressed(b, on);
    });
    d.all(root, '[data-a-panel]').forEach(function (p) { p.hidden = p.dataset.aPanel !== state.aTab; });
  }

  /**
   * The sentence the update check shows under its button.
   * @param {DemoState} state - the state.
   * @param {boolean} needs - whether a notebook is shown as outdated.
   * @returns {string} the sentence ('' before the check was run).
   */
  function updateMessage(state, needs) {
    if (!state.checked) { return ''; }
    if (needs) { return '⚠️ Some notebooks need to be updated. (Simulated check; the version number is made up.)'; }
    return state.updated ? '✅ Updated NucleiSky2DBenchmarking to version 9.9.9. (Illustrative example.)' : '✅ All notebooks are up-to-date. (Simulated check; nothing was contacted.)';
  }

  /**
   * Draw the Welcome notebook's update check: the example row, its Update button and the message.
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderUpdates(root, state) {
    var row = d.one(root, '[data-nbrow="NucleiSky2DBenchmarking"]'), needs = state.checked && state.scenario && !state.updated;
    d.one(root, '[data-act="scenario"]').checked = state.scenario;
    d.one(row, '[data-status]').textContent = needs ? '❌ Needs Update to 9.9.9' : '✅ Up-to-date';
    d.one(row, '[data-version]').textContent = state.updated ? '9.9.9' : '0.1.0';
    d.one(row, '[data-update]').innerHTML = needs ? UPDATE_BUTTON : '-';
    d.one(root, '[data-updates-out]').textContent = updateMessage(state, needs);
  }

  /**
   * Draw the notebook window: start screen or shell, the open tab, code shown or hidden, the toolbar and the widgets.
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderNotebook(root, state) {
    var inApp = state.nbTab === 'app' && state.opened;
    d.one(root, '[data-launch]').hidden = state.launched;
    d.one(root, '[data-shell]').hidden = !state.launched;
    d.one(root, '#nb-doc-welcome').hidden = inApp;
    d.one(root, '#nb-doc-app').hidden = !inApp;
    d.all(root, '[data-nb-tab]').forEach(function (t) { t.setAttribute('aria-selected', (t.dataset.nbTab === 'app') === inApp ? 'true' : 'false'); });
    d.all(root, '.nb__code').forEach(function (c) { c.hidden = !state.code; });
    d.all(root, '.nb__collapsed').forEach(function (c) { c.hidden = state.code; });
    d.setPressed(d.one(root, '[data-act="toggle-code"]'), state.code);
    d.one(root, '[data-act="run-welcome"]').disabled = state.welcomeRun;
    d.one(root, '[data-act="run-next"]').disabled = inApp ? (state.init && (state.step >= 3 || state.step !== state.done)) : state.welcomeRun;
    d.one(root, '[data-act="run-init"]').disabled = state.init;
    d.all(root, '[data-act="widget"]').forEach(function (b) { b.disabled = state.done >= Number(b.dataset.n) || (b.dataset.n === '1' && state.crop !== 'random'); });
    renderWidgets(root, state);
    renderOptionA(root, state);
    renderUpdates(root, state);
  }

  ns.renderNotebook = { steps: renderSteps, notebook: renderNotebook };
})(window.LCDemo = window.LCDemo || {});
