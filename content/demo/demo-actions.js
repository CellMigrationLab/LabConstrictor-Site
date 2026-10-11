/* What each control does to the state. An action changes the state and returns a reply (where to put the focus, what to announce);
   it never touches the page and never calculates anything. */
(function (ns) {
  var d = ns.dom;
  var WELCOME_OPEN = 'NucleiSky is open in JupyterLab with the Welcome notebook.';
  var DELAYS_MS = { 'run-init': 700, 'run-welcome': 700, 'test-connection': 900, 'update': 700 };
  var WIDGET_DELAYS_MS = { 1: 900, 2: 900, 3: 2200 };

  /**
   * A reply to the controller after an action.
   * @param {string} focus - selector of the control to focus ('' to leave the focus where it is).
   * @param {string} say - text for screen readers ('' for nothing).
   * @param {boolean} startInstall - whether the simulated install should start.
   * @returns {{focus: string, say: string, startInstall: boolean}} the reply.
   */
  function reply(focus, say, startInstall) {
    return { focus: focus, say: say, startInstall: startInstall };
  }

  /**
   * Record that notebook cell `n` ran; a run from napari or Fiji also completes the example and opens the notebook state behind it.
   * @param {DemoState} state - the state to change.
   * @param {number} n - the cell number (1 to 3).
   * @param {boolean} fromHost - true for the Run button of napari or Fiji.
   * @returns {void}
   */
  function applyRun(state, n, fromHost) {
    state.step = Math.max(state.step, n);
    if (!fromHost) { return; }
    state.done = 3;
    if (n !== 3) { return; }
    Object.assign(state, { init: true, crop: 'random', seg: 'existing', fijiDialog: false, opened: true, launched: true });
    if (!state.selected) { state.selected = 'aligned'; }
  }

  /**
   * Go to an installer page; the "Installing" page starts the simulated install.
   * @param {DemoState} state - the state to change.
   * @param {HTMLElement} el - the pressed button (data-go names the page).
   * @returns {Object} the reply.
   */
  function inst(state, el) {
    state.page = el.dataset.go;
    state.selectedKey = '';
    return reply(ns.guide.installTarget(state.page), 'Installer page: ' + state.page + '.', state.page === 'installing');
  }

  /**
   * Open the installed app from the Start menu: the Use part, Welcome notebook.
   * @param {DemoState} state - the state to change.
   * @returns {Object} the reply.
   */
  function openStart(state) {
    Object.assign(state, { cat: 'use', view: 'notebook', launched: true });
    return reply('#nb-tab-welcome', WELCOME_OPEN, false);
  }

  /**
   * Run notebook Step 0, or a cell of the napari or Fiji dialog.
   * @param {DemoState} state - the state to change.
   * @param {HTMLElement} el - the play, Run or OK button.
   * @returns {Object} the reply.
   */
  function runStep(state, el) {
    var n = Number(el.dataset.step), host = !el.closest('.nb');
    applyRun(state, n, host);
    return reply(host && n === 3 ? '[data-act="fiji-open"]' : '', host ? 'Example result shown.' : 'Cell ' + n + ' ran; its widget is shown below.', false);
  }

  /**
   * The Run button of the toolbar: Step 0, the next cell, or the Welcome cell, whichever is next.
   * @param {DemoState} state - the state to change.
   * @returns {Object} the reply.
   */
  function runNext(state) {
    if (!(state.nbTab === 'app' && state.opened)) { state.welcomeRun = true; } else if (!state.init) { state.init = true; } else { applyRun(state, Math.min(3, state.step + 1), false); }
    return reply('', '', false);
  }

  /**
   * Toggle the napari layer's visibility (its row is the eye button's parent).
   * @param {DemoState} state - the state to change.
   * @param {HTMLElement} el - the eye button.
   * @returns {Object} the reply.
   */
  function eye(state, el) {
    var key = el.parentNode.dataset.layerRow;
    state.vis[key] = !state.vis[key];
    return reply('', '', false);
  }

  /**
   * Set the selected napari layer's opacity from the slider.
   * @param {DemoState} state - the state to change.
   * @param {HTMLInputElement} el - the opacity slider.
   * @returns {Object} the reply.
   * @throws {Error} when no layer is selected (the slider is disabled then).
   */
  function opacity(state, el) {
    if (!state.selected) { throw new Error('demo: the opacity slider moved with no layer selected'); }
    state.opacity[state.selected] = Number(el.value);
    return reply('', '', false);
  }

  /**
   * A simple change of one state field, as a ready-made action.
   * @param {string} field - the state field to set.
   * @param {function(HTMLElement): *} value - how to read the new value from the pressed element.
   * @param {string} focus - selector to focus afterwards ('' for none).
   * @param {string} say - text to announce ('' for none).
   * @returns {function(DemoState, HTMLElement): Object} the action.
   */
  function setter(field, value, focus, say) {
    return function (state, el) {
      state[field] = value(el);
      return reply(focus, say, false);
    };
  }

  var ACTIONS = {
    'inst': inst,
    'open-start': openStart,
    'run-step': runStep,
    'run-next': runNext,
    'eye': eye,
    'opacity': opacity,
    'run-init': setter('init', function () { return true; }, '', 'Cell ran: the environment is ready.'),
    'crop-mode': setter('crop', function (el) { return el.dataset.mode; }, '', ''),
    'seg-mode': setter('seg', function (el) { return el.dataset.mode; }, '', ''),
    'how': setter('how', function (el) { return Number(el.dataset.i); }, '', ''),
    'launch': setter('launched', function () { return true; }, '#nb-tab-welcome', WELCOME_OPEN),
    'run-welcome': setter('welcomeRun', function () { return true; }, '[data-act="test-connection"]', 'Cell ran: the list of notebooks and the update check are shown.'),
    'toggle-code': function (state) { state.code = !state.code; return reply('', '', false); },
    'test-connection': setter('checked', function () { return true; }, '', ''),
    'scenario': function (state, el) { state.scenario = el.checked; state.updated = false; return reply('', '', false); },
    'update': setter('updated', function () { return true; }, '[data-act="test-connection"]', 'Updated.'),
    'select': setter('selected', function (el) { return el.dataset.layer; }, '', ''),
    'fiji-open': setter('fijiDialog', function () { return true; }, '[data-dialog] [data-act="run-step"]', ''),
    'fiji-cancel': setter('fijiDialog', function () { return false; }, '[data-act="fiji-open"]', ''),
    'open-app': function (state) { Object.assign(state, { launched: true, opened: true, nbTab: 'app' }); return reply('', '', false); },
    'widget': function (state, el) { state.done = Math.max(state.done, Number(el.dataset.n)); return reply('', 'Done: the result is shown below.', false); },
    'acc': function (state, el) { state.acc[el.dataset.acc] = !state.acc[el.dataset.acc]; return reply('', '', false); }
  };

  /**
   * The action for a control's data-act value.
   * @param {string} name - the data-act value.
   * @returns {function(DemoState, HTMLElement): Object} the action.
   * @throws {Error} when no action has that name.
   */
  function actionFor(name) {
    return d.lookup(ACTIONS, name, 'action');
  }

  /**
   * How long a control's result is delayed, to mimic the processing (0 for none).
   * @param {HTMLElement} el - the pressed control.
   * @returns {number} milliseconds.
   */
  function delayFor(el) {
    var name = el.dataset.act;
    if (name === 'run-step') { return el.closest('.nb') ? 600 : 1500; }
    if (name === 'widget') { return d.lookup(WIDGET_DELAYS_MS, el.dataset.n, 'widget number'); }
    return Object.prototype.hasOwnProperty.call(DELAYS_MS, name) ? DELAYS_MS[name] : 0;
  }

  ns.actions = { actionFor: actionFor, delayFor: delayFor, names: Object.keys(ACTIONS) };
})(window.LCDemo = window.LCDemo || {});
