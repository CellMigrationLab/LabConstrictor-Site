/* The /how-it-works/ page: each chapter panel is a small set of choices. A button sets one choice (data-set / data-value); elements with
   data-show appear when the current choices match; lines with data-ran are dimmed when they would not run in the chosen place.
   Nothing is calculated here and nothing leaves the page. */
(function (ns) {
  var d = ns.dom;

  /**
   * Read a panel's starting choices from its data-state attribute ("group:value group2:value2").
   * @param {string} text - the attribute value.
   * @returns {Object<string, string>} the choices by group.
   * @throws {Error} for a part that is not "group:value" or a group declared twice.
   */
  function parseState(text) {
    var state = {};
    text.split(/\s+/).filter(Boolean).forEach(function (pair) {
      var parts = pair.split(':');
      if (parts.length !== 2 || !parts[0] || !parts[1]) { throw new Error('how: "' + pair + '" is not group:value'); }
      if (Object.prototype.hasOwnProperty.call(state, parts[0])) { throw new Error('how: the choice group "' + parts[0] + '" is declared twice in "' + text + '"'); }
      state[parts[0]] = parts[1];
    });
    return state;
  }

  /**
   * Whether any of the "group:value" alternatives of a data-show attribute matches the choices.
   * @param {Object<string, string>} state - the current choices.
   * @param {string} alternatives - space-separated "group:value" tokens.
   * @returns {boolean} true when one of them is the current choice of its group.
   * @throws {Error} when a token is not "group:value" or names a group the panel does not have.
   */
  function shows(state, alternatives) {
    return alternatives.split(/\s+/).filter(Boolean).some(function (token) {
      var parts = token.split(':');
      if (parts.length !== 2 || !parts[0] || !parts[1]) { throw new Error('how: "' + token + '" in data-show="' + alternatives + '" is not group:value'); }
      return d.lookup(state, parts[0], 'choice group') === parts[1];
    });
  }

  /**
   * Draw a panel from its choices: pressed buttons, shown elements, dimmed lines.
   * @param {Element} panel - the panel root.
   * @param {Object<string, string>} state - the current choices.
   * @returns {void}
   */
  function render(panel, state) {
    d.all(panel, '[data-set]').forEach(function (b) { d.setPressed(b, d.lookup(state, b.dataset.set, 'choice group') === b.dataset.value); });
    d.all(panel, '[data-toggle]').forEach(function (b) { d.setPressed(b, d.lookup(state, b.dataset.toggle, 'choice group') === 'on'); });
    d.all(panel, '[data-show]').forEach(function (el) { el.hidden = !shows(state, el.dataset.show); });
    d.all(panel, '[data-ran]').forEach(function (el) {
      var where = el.dataset.ran;
      el.classList.toggle('is-skipped', where !== 'both' && where !== state.runtime);
    });
  }

  /**
   * Flip an on/off choice; a panel whose data-min-on lists some choices keeps at least one of them on.
   * @param {Element} panel - the panel root.
   * @param {Object<string, string>} state - the choices (changed in place).
   * @param {string} group - the on/off group to flip.
   * @returns {void}
   */
  function toggle(panel, state, group) {
    var next = d.lookup(state, group, 'choice group') === 'on' ? 'off' : 'on';
    var kept = panel.dataset.minOn ? panel.dataset.minOn.split(/\s+/) : [];
    var others = kept.filter(function (g) { return g !== group && state[g] === 'on'; });
    if (next === 'off' && kept.indexOf(group) >= 0 && others.length === 0) { return; }
    state[group] = next;
  }

  /**
   * Handle a press on a panel's choice button (data-set picks a value, data-toggle flips on and off).
   * @param {Element} panel - the panel root.
   * @param {Object<string, string>} state - the choices (changed in place).
   * @param {Event} e - the click.
   * @returns {void}
   */
  function onClick(panel, state, e) {
    var button = e.target.closest('[data-set], [data-toggle]');
    if (!button || !panel.contains(button)) { return; }
    if (button.dataset.toggle) {
      toggle(panel, state, button.dataset.toggle);
    } else {
      d.lookup(state, button.dataset.set, 'choice group');
      state[button.dataset.set] = button.dataset.value;
    }
    render(panel, state);
  }

  /**
   * Make one panel live.
   * @param {Element} panel - the panel root (it has data-state).
   * @returns {void}
   */
  function start(panel) {
    var state = parseState(panel.dataset.state);
    panel.addEventListener('click', function (e) { onClick(panel, state, e); });
    render(panel, state);
  }

  /**
   * Open the "Go further" disclosure that holds the element the address points to (a chapter keeps its address, whether it is shown or folded).
   * An address that names no element is an ordinary browser case and is left to the browser.
   * @returns {void}
   */
  function openTarget() {
    var target = document.getElementById(location.hash.slice(1));
    var folded = target ? target.closest('details') : null;
    if (!folded) { return; }
    folded.open = true;
    target.scrollIntoView();
  }

  document.documentElement.classList.add('how-live');
  d.all(document, '.how__panel').forEach(start);
  openTarget();
  window.addEventListener('hashchange', openTarget);
  d.all(document, '.how__static').forEach(function (list) { list.hidden = true; });
})(window.LCDemo = window.LCDemo || {});
