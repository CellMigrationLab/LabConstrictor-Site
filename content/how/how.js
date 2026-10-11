/* The /how-it-works/ page: each chapter panel is a small set of choices. A button sets one choice (data-set / data-value); elements with
   data-show appear when the current choices match; lines with data-ran are dimmed when they would not run in the chosen place.
   Nothing is calculated here and nothing leaves the page. */
(function (ns) {
  var d = ns.dom;

  /**
   * Read a panel's starting choices from its data-state attribute ("group:value group2:value2").
   * @param {string} text - the attribute value.
   * @returns {Object<string, string>} the choices by group.
   * @throws {Error} for a part that is not "group:value".
   */
  function parseState(text) {
    var state = {};
    text.split(/\s+/).filter(Boolean).forEach(function (pair) {
      var parts = pair.split(':');
      if (parts.length !== 2 || !parts[0] || !parts[1]) { throw new Error('how: "' + pair + '" is not group:value'); }
      state[parts[0]] = parts[1];
    });
    return state;
  }

  /**
   * Whether any of the "group:value" alternatives of a data-show attribute matches the choices.
   * @param {Object<string, string>} state - the current choices.
   * @param {string} alternatives - space-separated "group:value" tokens.
   * @returns {boolean} true when one of them is the current choice of its group.
   * @throws {Error} when a token names a group the panel does not have.
   */
  function shows(state, alternatives) {
    return alternatives.split(/\s+/).filter(Boolean).some(function (token) {
      var parts = token.split(':');
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
    d.all(panel, '[data-show]').forEach(function (el) { el.hidden = !shows(state, el.dataset.show); });
    d.all(panel, '[data-ran]').forEach(function (el) {
      var where = el.dataset.ran;
      el.classList.toggle('is-skipped', where !== 'both' && where !== state.runtime);
    });
  }

  /**
   * Handle a press on a panel's choice button.
   * @param {Element} panel - the panel root.
   * @param {Object<string, string>} state - the choices (changed in place).
   * @param {Event} e - the click.
   * @returns {void}
   */
  function onClick(panel, state, e) {
    var button = e.target.closest('[data-set]');
    if (!button || !panel.contains(button)) { return; }
    d.lookup(state, button.dataset.set, 'choice group');
    state[button.dataset.set] = button.dataset.value;
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

  d.all(document, '.how__panel').forEach(start);
  d.all(document, '.how__static').forEach(function (list) { list.hidden = true; });
})(window.LCDemo = window.LCDemo || {});
