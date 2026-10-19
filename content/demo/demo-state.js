/* The demo's whole state in one object. Changing the view starts again from `fresh()`. */
(function (ns) {
  /**
   * @typedef {Object} DemoState
   * @property {string} cat - 'install' (how installation works, shown first) or 'use' (the installed app).
   * @property {string} os - the installer shown in the installation part: 'windows' (the default) or 'macos'.
   * @property {string} page - the installer page showing (a data-page value: the macOS pages start with 'mac-').
   * @property {number} progress - installer progress, 0 to 100.
   * @property {boolean} installed - whether the simulated install has finished.
   * @property {string} selectedKey - the double-click target that was clicked once ('' for none).
   * @property {string} view - 'notebook', 'napari' or 'fiji'.
   * @property {boolean} launched - whether the app icon was opened.
   * @property {boolean} welcomeRun - whether the Welcome notebook's first cell ran.
   * @property {boolean} opened - whether the example notebook was opened from the Welcome table.
   * @property {string} nbTab - the notebook tab showing: 'welcome' or 'app'.
   * @property {boolean} code - whether the code cells are shown.
   * @property {boolean} init - whether notebook Step 0 ran.
   * @property {number} step - the last notebook cell run (0 to 3).
   * @property {number} done - the last widget used (0 to 3).
   * @property {string} crop - 'external' or 'random'.
   * @property {string} seg - 'new' or 'existing'.
   * @property {boolean} optA - whether the Option A cell ran (its widget is shown).
   * @property {string} aTab - the matcher settings tab of Option A that is open.
   * @property {Object<string, boolean>} acc - which accordions are open.
   * @property {boolean} checked - whether the update check was run in the Welcome notebook.
   * @property {boolean} scenario - whether the illustrative outdated-notebook scenario is on.
   * @property {boolean} updated - whether the example notebook was updated in that scenario.
   * @property {number} how - the step of "How the connection works" that is pressed (1 to 6).
   * @property {boolean} fijiDialog - whether the Fiji tool dialog is open.
   * @property {boolean} busy - whether a simulated run is in progress.
   * @property {string} selected - the selected napari layer ('' for none).
   * @property {Object<string, boolean>} vis - napari layer visibility.
   * @property {Object<string, number>} opacity - napari layer opacity, 0 to 100.
   */

  /**
   * @typedef {Object} DemoContext
   * @property {Element} root - the element with data-demo.
   * @property {DemoState} state - the state being drawn.
   * @property {?number} pending - the timer of a simulated run that is waiting, or null.
   * @property {?number} installTimer - the timer of the simulated install, or null.
   */

  /**
   * @typedef {Object} ActionReply
   * @property {string} focus - selector of the control to focus ('' to leave the focus where it is).
   * @property {string} say - text for screen readers ('' for nothing).
   * @property {boolean} startInstall - whether the simulated install should start.
   */

  /**
   * A new state as it is when the page loads.
   * @returns {DemoState} the initial state.
   */
  function fresh() {
    return {
      cat: 'install', os: 'windows', page: 'download', progress: 0, installed: false, selectedKey: '',
      view: 'notebook', launched: false, welcomeRun: false, opened: false, nbTab: 'welcome', code: false,
      init: false, optA: false, aTab: '_common', step: 0, done: 0, crop: 'external', seg: 'new', acc: { inst: false, thr: false, adv: false },
      checked: false, scenario: false, updated: false, busy: false, how: 1, fijiDialog: true, selected: '',
      vis: { reference: true, query: false, aligned: true, alignment: true },
      opacity: { reference: 100, query: 100, aligned: 100, alignment: 80 }
    };
  }

  ns.fresh = fresh;
})(window.LCDemo = window.LCDemo || {});
