/* The guide: which control to circle next and, before the app is open, the one line of text that goes with it. */
(function (ns) {
  var d = ns.dom;
  var INSTALL_NEXT = {
    download: '.wi__file', smart: '.wi__sl', smart2: '[data-go="welcome"]', welcome: '[data-go="license"]', license: '[data-go="type"]',
    type: '[data-go="folder"]', folder: '[data-go="options"]', options: '[data-go="installing"]', installing: '[data-needs-install]',
    finish: '[data-go="start"]', start: '.wi__start'
  };
  var STEP_NAMES = { 1: 'Load & Process', 2: 'Load Masks & Extract Features', 3: 'Run adaptive NucleiSky2D' };

  /**
   * The selector of the control to press on an installer page.
   * @param {string} page - an installer page id.
   * @returns {string} a selector for the page's main control.
   * @throws {Error} for an unknown page.
   */
  function installTarget(page) {
    return '[data-page="' + page + '"] ' + d.lookup(INSTALL_NEXT, page, 'installer page');
  }

  /**
   * The hint for the installer: the main control of the current page, and a sentence on the first page only.
   * @param {DemoState} state - the state.
   * @returns {{target: string, text: string}} what to circle and say.
   */
  function installHint(state) {
    var text = '';
    if (state.page === 'download') {
      text = state.selectedKey ? 'Now double-click the file to start the installer (or press Enter).' : 'Double-click the downloaded installer to start it.';
    }
    return { target: installTarget(state.page), text: text };
  }

  /**
   * The hint for the napari and Fiji views.
   * @param {DemoState} state - the state (state.view is 'napari' or 'fiji').
   * @returns {{target: (string|null), text: string}} what to circle (null for nothing) and say.
   */
  function hostHint(state) {
    if (state.view === 'napari') {
      return state.step < 3 ? { target: '#demo-panel-napari .np__run', text: 'Click Run in the dock to run the tool.' }
        : { target: null, text: 'Click a layer name to select it, the eye to hide it, and move the opacity slider. Then try Fiji.' };
    }
    if (state.fijiDialog) { return { target: '[data-dialog] [data-act="run-step"]', text: 'Click OK to run the tool.' }; }
    return state.step < 3 ? { target: '[data-act="fiji-open"]', text: 'Open the tool again from the Plugins menu.' }
      : { target: null, text: 'The result opens in its own window. Switch to another view to start again.' };
  }

  /**
   * The hint while the notebook app is still being opened (icon, Welcome cell, Open the notebook).
   * @param {DemoState} state - the state.
   * @returns {({target: string, text: string}|null)} the hint, or null once the 2D notebook is open.
   */
  function openingHint(state) {
    if (!state.launched) {
      return { target: '[data-act="launch"]', text: state.selectedKey ? 'Now double-click the icon to open the app (or press Enter).' : 'Double-click the NucleiSky icon to open the app.' };
    }
    if (!state.welcomeRun) { return { target: '[data-act="run-welcome"]', text: 'Click the play button to run the Welcome cell. It lists the notebooks of the app.' }; }
    if (!(state.nbTab === 'app' && state.opened)) { return { target: '[data-act="open-app"]', text: 'Click Open the notebook on NucleiSky2DApp to open the 2D notebook.' }; }
    return null;
  }

  /**
   * The hint inside the 2D notebook: Step 0, the next cell, the next widget or the end.
   * @param {DemoState} state - the state (the 2D notebook is open).
   * @returns {{target: (string|null), text: string}} what to circle (null for nothing) and say.
   */
  function notebookHint(state) {
    var n = state.step;
    if (!state.init) { return { target: '#nb-doc-app [data-act="run-init"]', text: 'Click the play button to run Step 0, which initializes the environment.' }; }
    if (n === state.done && n < 3) { return { target: '#nb-doc-app [data-act="run-step"][data-step="' + (n + 1) + '"]', text: 'Click the play button to run the next cell. It shows a widget.' }; }
    if (n === 1 && n > state.done && state.crop !== 'random') { return { target: '[data-act="crop-mode"][data-mode="random"]', text: 'Choose Generate Random Crop: this preview has no crop file to load.' }; }
    if (n === 2 && n > state.done && state.seg !== 'existing') { return { target: '[data-act="seg-mode"][data-mode="existing"]', text: 'Choose Load Existing Masks: the recorded example uses supplied masks.' }; }
    if (n > state.done) { return { target: '[data-act="widget"][data-n="' + n + '"]', text: 'Use the widget: click ' + d.lookup(STEP_NAMES, n, 'step') + '.' }; }
    return { target: null, text: 'This is the whole notebook: scroll down for NucleiSky\'s own output. Try Show/Hide code, then napari or Fiji.' };
  }

  /**
   * What to circle next and say, for the part and view being shown.
   * @param {DemoState} state - the state.
   * @returns {{target: (string|null), text: string}} the hint.
   */
  function hintFor(state) {
    if (state.cat === 'install') { return installHint(state); }
    if (state.view !== 'notebook') { return hostHint(state); }
    return openingHint(state) || notebookHint(state);
  }

  /**
   * Draw the guide: the red loop on the next control (only when it can be used) and the text line (only before the app is open).
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderNext(root, state) {
    d.all(root, '.is-next').forEach(function (el) { el.classList.remove('is-next'); });
    var hint = hintFor(state), target = hint.target ? d.one(root, hint.target) : null;
    if (target && !target.hidden && !target.disabled && !state.busy) { target.classList.add('is-next'); }
    var showText = state.cat === 'install' || (!state.launched && state.view === 'notebook');
    d.one(root, '[data-next]').textContent = showText ? hint.text : '';
  }

  ns.guide = { installTarget: installTarget, render: renderNext };
})(window.LCDemo = window.LCDemo || {});
