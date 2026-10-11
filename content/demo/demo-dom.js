/* Strict DOM helpers for the /demo/ page. A missing element or an unknown key is an error that names it, never a silent skip. */
(function (ns) {
  /**
   * Every element under `root` that matches `sel`.
   * @param {Element} root - where to look.
   * @param {string} sel - CSS selector.
   * @returns {Element[]} the matches (an empty array when there are none; use `one` when one must exist).
   */
  function all(root, sel) {
    return Array.prototype.slice.call(root.querySelectorAll(sel));
  }

  /**
   * The one element under `root` that matches `sel`.
   * @param {Element} root - where to look.
   * @param {string} sel - CSS selector.
   * @returns {Element} the first match.
   * @throws {Error} when nothing matches, naming the selector.
   */
  function one(root, sel) {
    var el = root.querySelector(sel);
    if (!el) { throw new Error('demo: no element matches ' + sel); }
    return el;
  }

  /**
   * The value stored under `key` in a table of this page's own constants.
   * @param {Object} table - the table.
   * @param {string} key - the key to read.
   * @param {string} what - what the table holds, for the error message.
   * @returns {*} the value.
   * @throws {Error} when the key is not in the table.
   */
  function lookup(table, key, what) {
    if (!Object.prototype.hasOwnProperty.call(table, key)) { throw new Error('demo: unknown ' + what + ' "' + key + '"'); }
    return table[key];
  }

  /**
   * Mark a toggle button as pressed or not, for assistive technology.
   * @param {Element} el - the button.
   * @param {boolean} on - whether it is pressed.
   * @returns {void}
   */
  function setPressed(el, on) {
    el.setAttribute('aria-pressed', on ? 'true' : 'false');
  }

  /**
   * Mark a tab as selected (the only tab in the order of the page's tab keys) or not.
   * @param {HTMLElement} tab - the tab button.
   * @param {boolean} on - whether it is the selected tab.
   * @returns {void}
   */
  function setSelected(tab, on) {
    tab.setAttribute('aria-selected', on ? 'true' : 'false');
    tab.tabIndex = on ? 0 : -1;
  }

  /**
   * Put every field of the demo back to the value written in the page.
   * @param {Element} root - the demo root.
   * @returns {void}
   */
  function resetControls(root) {
    all(root, 'input, select').forEach(function (c) {
      if (c.tagName === 'SELECT') {
        Array.prototype.forEach.call(c.options, function (o) { o.selected = o.defaultSelected; });
      } else {
        c.value = c.defaultValue;
        c.checked = c.defaultChecked;
      }
    });
  }

  ns.dom = { all: all, one: one, lookup: lookup, setPressed: setPressed, setSelected: setSelected, resetControls: resetControls };
})(window.LCDemo = window.LCDemo || {});
