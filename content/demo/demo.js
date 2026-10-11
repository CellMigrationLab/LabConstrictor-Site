/* The /demo/ page: a small state machine that switches between stored views of one precomputed result.
   Nothing is calculated here and nothing leaves the page. This file wires the events; the other demo-*.js files hold the parts. */
(function (ns) {
  var d = ns.dom;
  var KEYS = ['ArrowRight', 'ArrowLeft', 'Home', 'End'];
  var INSTALL_STEP_MS = 100, INSTALL_STEP_PERCENT = 2;

  /**
   * Draw everything from the state.
   * @param {DemoContext} ctx - the controller context ({root, state, pending, installTimer}).
   * @returns {void}
   */
  function sync(ctx) {
    var root = ctx.root, state = ctx.state;
    root.dataset.step = state.step;
    ns.renderHost.cat(root, state);
    ns.renderHost.installer(root, state);
    ns.renderHost.views(root, state);
    ns.renderNotebook.steps(root, state);
    ns.renderNotebook.notebook(root, state);
    ns.renderHost.layers(root, state);
    ns.renderHost.fiji(root, state);
    ns.renderHost.how(root, state);
    ns.guide.render(root, state);
  }

  /**
   * Stop the processing delay of a simulated run and clear its busy look.
   * @param {DemoContext} ctx - the controller context ({root, state, pending, installTimer}).
   * @returns {void}
   */
  function clearBusy(ctx) {
    clearTimeout(ctx.pending);
    ctx.pending = null;
    ctx.state.busy = false;
    delete ctx.root.dataset.busy;
    d.all(ctx.root, '.is-busy').forEach(function (el) { el.classList.remove('is-busy'); el.removeAttribute('aria-busy'); });
  }

  /**
   * Stop the simulated install's progress timer.
   * @param {DemoContext} ctx - the controller context.
   * @returns {void}
   */
  function stopInstall(ctx) {
    clearInterval(ctx.installTimer);
    ctx.installTimer = null;
  }

  /**
   * Announce a text to screen readers.
   * @param {DemoContext} ctx - the controller context.
   * @param {string} text - what to say.
   * @returns {void}
   */
  function say(ctx, text) {
    d.one(ctx.root, '[data-announce]').textContent = text;
  }

  /**
   * After an action: announce its text and move the focus to the control it names, when that control can take it.
   * @param {DemoContext} ctx - the controller context.
   * @param {{focus: string, say: string}} result - the action's reply.
   * @returns {void}
   */
  function settle(ctx, result) {
    if (result.say) { say(ctx, result.say); }
    if (!result.focus) { return; }
    var target = d.one(ctx.root, result.focus);
    if (!target.hidden && !target.disabled) { target.focus(); }
  }

  /**
   * Start the simulated install: progress grows until it reaches 100, then Next is enabled and focused.
   * @param {DemoContext} ctx - the controller context.
   * @returns {void}
   */
  function startInstall(ctx) {
    ctx.state.progress = 0;
    ctx.state.installed = false;
    ctx.installTimer = setInterval(function () {
      ctx.state.progress = Math.min(100, ctx.state.progress + INSTALL_STEP_PERCENT);
      ctx.state.installed = ctx.state.progress === 100;
      if (ctx.state.installed) { stopInstall(ctx); say(ctx, 'Installation complete. Click Next.'); }
      sync(ctx);
      if (ctx.state.installed) { d.one(ctx.root, '[data-page="installing"] [data-needs-install]').focus(); }
    }, INSTALL_STEP_MS);
  }

  /**
   * Run the action of a control now: change the state, redraw, announce, and start the install when the action asks.
   * @param {DemoContext} ctx - the controller context.
   * @param {HTMLElement} el - the control.
   * @returns {void}
   */
  function perform(ctx, el) {
    var result = ns.actions.actionFor(el.dataset.act)(ctx.state, el);
    sync(ctx);
    settle(ctx, result);
    if (result.startInstall) { startInstall(ctx); }
  }

  /**
   * Run the action of a control after a short delay that mimics the processing, with the control shown as busy meanwhile.
   * @param {DemoContext} ctx - the controller context.
   * @param {HTMLElement} el - the control.
   * @param {number} ms - the delay in milliseconds.
   * @returns {void}
   */
  function performLater(ctx, el, ms) {
    ctx.state.busy = true;
    ctx.root.dataset.busy = 'true';
    el.classList.add('is-busy');
    el.setAttribute('aria-busy', 'true');
    say(ctx, 'Running…');
    sync(ctx);
    ctx.pending = setTimeout(function () { clearBusy(ctx); perform(ctx, el); }, ms);
  }

  /**
   * Start again from the first state, with every field back to its written value.
   * @param {DemoContext} ctx - the controller context.
   * @returns {void}
   */
  function restart(ctx) {
    clearBusy(ctx);
    stopInstall(ctx);
    ctx.state = ns.fresh();
    d.resetControls(ctx.root);
  }

  /**
   * Show another view; changing the view always restarts the demo.
   * @param {DemoContext} ctx - the controller context.
   * @param {string} view - 'notebook', 'napari' or 'fiji'.
   * @returns {void}
   */
  function switchView(ctx, view) {
    if (view !== ctx.state.view) { restart(ctx); ctx.state.cat = 'use'; ctx.state.view = view; }
    sync(ctx);
  }

  /**
   * Handle a press on one of the demo's own controls (category tabs, view tabs).
   * @param {DemoContext} ctx - the controller context.
   * @param {HTMLElement} el - the control (it has data-demo-act).
   * @returns {void}
   * @throws {Error} for an unknown data-demo-act value.
   */
  function onDemoControl(ctx, el) {
    var kind = el.dataset.demoAct;
    if (kind === 'view') { switchView(ctx, el.dataset.view); return; }
    if (kind === 'cat') { ctx.state.cat = el.dataset.cat; sync(ctx); return; }
    throw new Error('demo: unknown data-demo-act "' + kind + '"');
  }

  /**
   * Handle a press on a control inside a window: a notebook tab, a first click on a double-click target, or an action.
   * @param {DemoContext} ctx - the controller context.
   * @param {HTMLElement} el - the control.
   * @param {number} clicks - the click count of the event (1 for a single click, 0 for the keyboard).
   * @returns {void}
   */
  function onWindowControl(ctx, el, clicks) {
    if (el.dataset.nbTab) { ctx.state.nbTab = el.dataset.nbTab; sync(ctx); return; }
    if (el.hasAttribute('data-dbl') && clicks === 1) {
      ctx.state.selectedKey = el.dataset.act + el.dataset.go;
      el.classList.add('is-selected');
      sync(ctx);
      return;
    }
    if ((el.tagName === 'INPUT' && el.type !== 'checkbox') || el.tagName === 'SELECT') { return; }
    var ms = ns.actions.delayFor(el);
    if (ms) { performLater(ctx, el, ms); } else { perform(ctx, el); }
  }

  /**
   * The click handler of the demo root.
   * @param {DemoContext} ctx - the controller context.
   * @param {MouseEvent} e - the click.
   * @returns {void}
   */
  function onClick(ctx, e) {
    var el = e.target.closest('[data-act], [data-nb-tab], [data-demo-act]');
    if (!el || !ctx.root.contains(el) || el.disabled) { return; }
    if (el.dataset.demoAct) { onDemoControl(ctx, el); return; }
    if (!ctx.state.busy) { onWindowControl(ctx, el, e.detail); }
  }

  /**
   * The tab that an arrow, Home or End key moves to, among the tabs of one tab list.
   * @param {HTMLElement[]} tabs - the tabs of the list, in order.
   * @param {HTMLElement} tab - the tab that has the focus.
   * @param {string} key - 'ArrowRight', 'ArrowLeft', 'Home' or 'End'.
   * @returns {HTMLElement} the tab to select.
   */
  function tabAfterKey(tabs, tab, key) {
    if (key === 'Home') { return tabs[0]; }
    if (key === 'End') { return tabs[tabs.length - 1]; }
    var i = tabs.indexOf(tab);
    return tabs[(i + (key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
  }

  /**
   * The key handler of the demo root: arrow keys move between the tabs of a tab list.
   * @param {DemoContext} ctx - the controller context.
   * @param {KeyboardEvent} e - the key event.
   * @returns {void}
   */
  function onKey(ctx, e) {
    var tab = e.target.closest('[role="tab"][data-view], [role="tab"][data-cat]');
    if (!tab || KEYS.indexOf(e.key) < 0) { return; }
    var tabs = d.all(ctx.root, '[role="tab"]').filter(function (t) { return t.parentNode === tab.parentNode; });
    var next = tabAfterKey(tabs, tab, e.key);
    e.preventDefault();
    if (next.dataset.view) { switchView(ctx, next.dataset.view); } else { ctx.state.cat = next.dataset.cat; sync(ctx); }
    next.focus();
  }

  /**
   * Remember each status text as its idle wording, so it can be restored after a run.
   * @param {Element} root - the demo root.
   * @returns {void}
   */
  function rememberIdle(root) {
    d.all(root, '[data-status][data-done]').forEach(function (el) { el.dataset.idle = el.textContent; });
  }

  /**
   * Start the demo on the page: wire the events and draw the first state.
   * @param {Element} root - the element with data-demo.
   * @returns {void}
   */
  function start(root) {
    var ctx = { root: root, state: ns.fresh(), pending: null, installTimer: null };
    rememberIdle(root);
    root.addEventListener('click', function (e) { onClick(ctx, e); });
    root.addEventListener('change', function (e) { if (e.target.dataset.ctl || e.target.type === 'range') { sync(ctx); } });
    root.addEventListener('input', function (e) {
      if (e.target.dataset.act === 'opacity') { ns.actions.actionFor('opacity')(ctx.state, e.target); }
      if (e.target.type === 'range') { sync(ctx); }
    });
    root.addEventListener('keydown', function (e) { onKey(ctx, e); });
    root.classList.add('is-live');
    sync(ctx);
  }

  var root = document.querySelector('[data-demo]');
  if (root) { start(root); }
})(window.LCDemo = window.LCDemo || {});
