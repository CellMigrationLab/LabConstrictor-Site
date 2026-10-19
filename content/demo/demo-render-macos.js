/* Drawing the Windows | macOS switch and the macOS installer walkthrough (its page, progress and selected icon) from the state. Nothing here changes the state. */
(function (ns) {
  var d = ns.dom;

  /**
   * Show the selected installer (Windows or macOS) and mark its tab; the other installer is hidden.
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderOs(root, state) {
    d.all(root, '[role="tab"][data-os]').forEach(function (t) {
      var on = t.dataset.os === state.os;
      d.setSelected(t, on);
      d.one(root, '#demo-os-' + t.dataset.os).hidden = !on;
    });
  }

  /**
   * The progress page: the bar, the one stage text reached so far (the last whose data-at is not above the progress) and the time-remaining line.
   * @param {Element} panel - the macOS installer panel.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderProgress(panel, state) {
    var bar = d.one(panel, '[data-mac-progress]');
    d.one(bar, 'span').style.width = state.progress + '%';
    bar.setAttribute('aria-valuenow', String(state.progress));
    var stages = d.all(panel, '[data-mac-log] [data-at]'), last = -1;
    stages.forEach(function (s, i) { if (state.progress >= Number(s.dataset.at)) { last = i; } });
    stages.forEach(function (s, i) { s.hidden = i !== last; });
    var late = state.progress >= 85;
    d.one(panel, '[data-mac-eta]').textContent = state.installed ? 'The installation has finished.' : 'Install time remaining: ' + (late ? 'Less than a minute' : 'Calculating...');
    d.one(panel, '[data-needs-install]').disabled = !state.installed;
  }

  /**
   * Draw the macOS installer: the current page, the double-click target that was clicked once, and the progress page.
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderInstaller(root, state) {
    var panel = d.one(root, '[data-os-panel="macos"]');
    d.all(panel, '[data-page]').forEach(function (p) { p.hidden = p.dataset.page !== state.page; });
    d.all(panel, '[data-dbl]').forEach(function (el) { el.classList.toggle('is-selected', state.selectedKey === el.dataset.act + el.dataset.go); });
    renderProgress(panel, state);
  }

  ns.renderMac = { os: renderOs, installer: renderInstaller };
})(window.LCDemo = window.LCDemo || {});
