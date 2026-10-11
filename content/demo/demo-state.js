/* The demo's whole state in one object. Changing the view or pressing Reset starts again from `fresh()`. */
(function (ns) {
  /**
   * @typedef {Object} DemoState
   * @property {string} cat - 'install' or 'use' (the two parts of the demo).
   * @property {string} page - the installer page showing (a data-page value).
   * @property {number} progress - installer progress, 0 to 100.
   * @property {boolean} installed - whether the simulated install has finished.
   * @property {string} selectedKey - the double-click target that was clicked once ('' for none).
   * @property {string} view - 'notebook', 'napari' or 'fiji'.
   * @property {boolean} launched - whether the app icon was opened.
   * @property {boolean} init - whether notebook Step 0 ran.
   * @property {number} step - the last notebook cell run (0 to 3).
   * @property {number} done - the last widget used (0 to 3).
   * @property {string} crop - 'external' or 'random'.
   * @property {string} seg - 'new' or 'existing'.
   * @property {Object<string, boolean>} acc - which accordions are open.
   * @property {boolean} busy - whether a simulated run is in progress.
   * @property {string} selected - the selected napari layer ('' for none).
   * @property {Object<string, boolean>} vis - napari layer visibility.
   * @property {Object<string, number>} opacity - napari layer opacity, 0 to 100.
   */

  /**
   * A new state as it is when the page loads.
   * @returns {DemoState} the initial state.
   */
  function fresh() {
    return {
      cat: 'install', page: 'download', progress: 0, installed: false, selectedKey: '',
      view: 'notebook', launched: false, welcomeRun: false, opened: false, nbTab: 'welcome', code: false,
      init: false, step: 0, done: 0, crop: 'external', seg: 'new', acc: { inst: false, thr: false, adv: false },
      checked: false, scenario: false, updated: false, busy: false, how: 1, fijiDialog: true, selected: '',
      vis: { reference: true, query: false, aligned: true, alignment: true },
      opacity: { reference: 100, query: 100, aligned: 100, alignment: 80 }
    };
  }

  ns.fresh = fresh;
})(window.LCDemo = window.LCDemo || {});
