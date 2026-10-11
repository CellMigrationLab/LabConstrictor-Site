/* Drawing the installer, the part and view tabs, and the napari and Fiji windows from the state. Nothing here changes the state. */
(function (ns) {
  var d = ns.dom;
  var BOXES = { 1: [0], 2: [0], 3: [1], 4: [2], 5: [0, 1], 6: [2] };
  var WHERE = { 4: ['#demo-panel-napari .np__form', '#demo-panel-fiji [data-dialog]'], 6: ['#demo-panel-napari .np__canvas', '#demo-panel-fiji .fj__win:nth-child(3)'] };
  var INSTALL_DONE_LINE = 'Setup was completed successfully.';

  /**
   * Show the selected part of the demo (Install or Use) and hide the other.
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderCat(root, state) {
    d.all(root, '[role="tab"][data-cat]').forEach(function (t) {
      var on = t.dataset.cat === state.cat;
      d.setSelected(t, on);
      d.one(root, '#demo-cat-' + t.dataset.cat).hidden = !on;
    });
  }

  /**
   * Set the title and sentence of the "Installing" page to the waiting or the finished wording.
   * @param {Element} root - the demo root.
   * @param {boolean} installed - whether the install has finished.
   * @returns {void}
   */
  function setInstallHead(root, installed) {
    var head = d.one(root, '[data-page="installing"] .wi__head div');
    if (!head.dataset.wait) { head.dataset.wait = head.lastElementChild.textContent; }
    head.firstElementChild.textContent = installed ? 'Installation Complete' : 'Installing';
    head.lastElementChild.textContent = installed ? INSTALL_DONE_LINE : head.dataset.wait;
  }

  /**
   * Draw the installer: the current page, the progress bar, the log lines reached and the Next button.
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderInstaller(root, state) {
    d.all(root, '[data-page]').forEach(function (p) { p.hidden = p.dataset.page !== state.page; });
    d.one(root, '[data-progress] span').style.width = state.progress + '%';
    d.one(root, '[data-progress]').setAttribute('aria-valuenow', String(state.progress));
    d.all(root, '[data-log] [data-at]').forEach(function (l) { l.hidden = state.progress < Number(l.dataset.at); });
    d.one(root, '[data-cmd]').hidden = state.progress < 85;
    d.one(root, '[data-needs-install]').disabled = !state.installed;
    setInstallHead(root, state.installed);
  }

  /**
   * Show the selected view (Notebook, napari or Fiji) and the notices that belong to the host views.
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderViews(root, state) {
    d.all(root, '[role="tab"][data-view]').forEach(function (t) {
      var on = t.dataset.view === state.view;
      d.setSelected(t, on);
      d.one(root, '#demo-panel-' + t.dataset.view).hidden = !on;
    });
    d.one(root, '[data-demo-experimental]').hidden = state.view === 'notebook';
    d.one(root, '[data-how]').hidden = state.view === 'notebook';
  }

  /**
   * Draw the napari layer list: selected row, eye and name toggles.
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderLayerList(root, state) {
    d.all(root, '[data-layer-row]').forEach(function (li) {
      var key = li.dataset.layerRow;
      li.classList.toggle('is-selected', state.selected === key);
      d.setPressed(d.one(li, '.np__eye'), state.vis[key]);
      d.setPressed(d.one(li, '.np__name'), state.selected === key);
    });
  }

  /**
   * Whether a napari layer exists yet (the two result layers appear after the tool has run).
   * @param {string} key - the layer key.
   * @param {DemoState} state - the state.
   * @returns {boolean} true when the layer is in the list.
   */
  function layerExists(key, state) {
    return (key === 'aligned' || key === 'alignment') ? state.step >= 3 : true;
  }

  /**
   * Draw the napari viewer: which layers show, their opacity, the slider, the viewer's text description and the side panel hint.
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderLayers(root, state) {
    renderLayerList(root, state);
    d.all(root, '#demo-panel-napari img[data-layer]').forEach(function (img) {
      var key = img.dataset.layer;
      img.hidden = !(layerExists(key, state) && state.vis[key]);
      img.style.opacity = state.opacity[key] / 100;
    });
    var slider = d.one(root, '[data-act="opacity"]'), sel = state.selected;
    slider.disabled = !sel || !state.vis[sel];
    slider.value = sel ? state.opacity[sel] : 100;
    slider.setAttribute('aria-valuetext', (slider.value / 100).toFixed(2));
    var shown = Object.keys(state.vis).filter(function (k) { return layerExists(k, state) && state.vis[k]; });
    d.one(root, '.np__canvas').setAttribute('aria-label', 'napari viewer showing the layers: ' + shown.join(', ') + '.');
    d.one(root, '[data-colormap]').textContent = sel === 'alignment' ? 'magenta' : 'gray';
    d.one(root, '[data-panel-hint]').hidden = !!sel;
  }

  /**
   * Show or hide the Fiji tool dialog.
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderFiji(root, state) {
    d.one(root, '[data-dialog]').hidden = !state.fijiDialog;
  }

  /**
   * Draw "How the connection works": the pressed step, the highlighted boxes and, in the host views, the outlined part of the window.
   * @param {Element} root - the demo root.
   * @param {DemoState} state - the state to draw.
   * @returns {void}
   */
  function renderHow(root, state) {
    d.all(root, '.is-explain').forEach(function (el) { el.classList.remove('is-explain'); });
    d.all(root, '.lc-how__step').forEach(function (b) { d.setPressed(b, Number(b.dataset.i) === state.how); });
    var boxes = d.lookup(BOXES, state.how, 'how step');
    d.all(root, '.lc-how__box').forEach(function (b, i) { b.classList.toggle('is-active', boxes.indexOf(i) >= 0); });
    if (state.view === 'notebook' || !Object.prototype.hasOwnProperty.call(WHERE, state.how)) { return; }
    var el = d.one(root, WHERE[state.how][state.view === 'napari' ? 0 : 1]);
    if (!el.hidden) { el.classList.add('is-explain'); }
  }

  ns.renderHost = { cat: renderCat, installer: renderInstaller, views: renderViews, layers: renderLayers, fiji: renderFiji, how: renderHow };
})(window.LCDemo = window.LCDemo || {});
